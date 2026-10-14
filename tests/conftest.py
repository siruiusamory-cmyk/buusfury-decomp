"""Shared pytest configuration: focused gates, a usable temporary root, a loud
failure when a required GUI module collapses, and a session-end census of what
the run skipped.

Four things live here, all test-infrastructure only - no shipped behaviour is
configured from this file.

**Focused gates.** Every collected test is tagged with the gates defined in
``tests/gates.py`` (``fast``, ``workbench``, ``writer``, ``map``,
``research``, ``rom``), so a ticket can run ``pytest -m writer`` instead of
reconstructing a path list. The tagging is additive and does not change what
an unqualified ``pytest`` run collects. ``docs/testing.md`` documents the
gates; ``tests/unit/test_test_gates.py`` checks the registry.

**The required GUI surface (CQA-08).** Every module named in
``REQUIRED_GUI_MODULES`` in ``tests/gates.py`` is a shipping Workbench test file
that a module-level ``pytest.importorskip`` guard lets collapse to a single
``SKIPPED`` line. That guard is deliberate and stays: a developer without
PySide6 must still be able to run the portable suite. What must not happen is
CI reporting a green job over it, which is precisely how CQA-08 hid - the CI job
installed only ``.[dev]``, so fourteen PySide6 modules and three capstone
modules each collapsed to one ``SKIPPED`` line and the job exited 0. So this
module records which test files pytest *attempted* and which actually
contributed a test, and at session end any required module that was attempted
but contributed nothing is reported by name, with its skip reason, and:

- under CI (``GITLAB_CI`` or ``CI`` in the environment) it FAILS the session -
  the affected job must be red, not green-with-skips;
- with ``WEBFOOT_REQUIRE_GUI_TESTS=1`` it FAILS the session anywhere, so the
  guard can be mutation-tested without pretending to be CI;
- otherwise it WARNs only. ``docs/testing.md`` promises that PySide6-less local
  runs skip the GUI modules cleanly; the defect was CI hiding a surface, not a
  developer choosing a smaller environment.

A required module that is not attempted in a run is never reported, so a
targeted subset (``python -m pytest tests/unit/test_map_render.py``) is
unaffected.

**What the session skipped (CQA-21).** A green run says what it did not run.
Every test the session reported as skipped is collected by
:func:`pytest_runtest_logreport` - the same hook the terminal reporter builds its
own skip summary from - and listed at session end with pytest's own reason. A
member declared in ``ARTEFACT_DEPENDENT_TESTS`` (``tests/gates.py``) is marked as
such, so the dependency is stated by the gate rather than recovered from a reason
string. That list is reported and never enforced: no CI job builds the site for
the ``fast`` gate, so a member skipping over a missing ``dist/`` is the designed
arrangement rather than a hidden surface. A session that skipped nothing prints
nothing.

**A usable temporary root.** ``tmp_path`` must not resolve inside the
repository, and must not resolve into a temp root the process cannot read or
write. A ``tmp_path`` under the work tree makes the generated-output guards
refuse paths they are right to refuse (the tests that expect an accepted
output fail by design), and an unusable default root makes every ``tmp_path``
test error out before it runs. This module therefore states the requirement
once, up front, instead of leaving it to whoever reads the thirtieth
``PermissionError``.

**Sharding (RETRO-CI-GITHUB-001 part 4).** ``WEBFOOT_SHARD_COUNT`` and
``WEBFOOT_SHARD_INDEX`` name one slice of the portable suite; the GitHub workflow
runs ten of them as parallel jobs. With both unset - every local run, and the
local full-CI record - the hook below does nothing at all, so that record is
unchanged. With them set it DESELECTS the other shards' nodes rather than
skipping them, so this shard's junit report and skip census describe only the
tests it ran and its counts stay comparable with the record's.
"""

from __future__ import annotations

import faulthandler
import getpass
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

import pytest

from tests.gates import (
    ARTEFACT_DEPENDENT_TESTS,
    GATE_DESCRIPTIONS,
    REPOSITORY_ROOT,
    REQUIRED_GUI_MODULES,
    TESTS_DIRECTORY,
    gates_for,
    relative_test_path,
)
from tests.rom_support import (
    CANONICAL_ROM_SHA256 as _CANONICAL_ROM_SHA256,
    ROM_DEFAULT as _ROM_DEFAULT,
    ROM_ENVIRONMENT_VARIABLES as _ROM_ENVIRONMENT_VARIABLES,
    mutable_rom_copy,
)
from tests.shards import node_identifier, selection_from_environment, shard_of

#: Set by :func:`pytest_configure` when pytest's own temporary root is unusable
#: and this module redirected the process temp root to an isolated one.
_REDIRECTED_TEMPROOT: tuple[Path, str] | None = None

#: Status the shard hook sets once it has sharded a run, so a pytest a test
#: starts inside that run - which inherits the shard variables - keeps the whole
#: collection the test asked for instead of being sharded a second time.
_NESTED_RUN_VARIABLE = "WEBFOOT_PYTEST_IN_PROGRESS"

#: Set this to force the required-GUI-surface guard to fail a session outside
#: CI, so the guard can be mutation-tested on a developer machine.
_REQUIRE_GUI_TESTS_VARIABLE = "WEBFOOT_REQUIRE_GUI_TESTS"

#: Environment variables that mean "this run is CI, so a collapsed required GUI
#: module is a pipeline defect rather than a local environment choice".
_CI_ENVIRONMENT_VARIABLES = ("GITLAB_CI", "CI")

#: Option destination that means "this run's result is read from a machine-readable
#: report", which is what both CI and the local full-CI record gate do and what no
#: local developer run does. The record gate cannot set ``CI`` itself: it is
#: master's reviewed ``scripts/local-ci.ps1`` and it runs the suite as an ordinary
#: local process. This option is why the exit path below takes the clean exit under
#: the gate as well as under CI.
#:
#: The name is ``xmlpath``, not ``junitxml``: ``_pytest/junitxml.py`` registers
#: ``--junitxml`` with ``dest="xmlpath"``. Read the destination through
#: ``config.option``; the attribute does not exist under the flag's own spelling, and
#: a key that never matches is a mitigation that never fires. Measured 2026-10-13: an
#: xdist ``-n 2`` run of one Qt module with ``--junitxml`` set ``xmlpath`` in the
#: controller AND in both workers, and reading a missing ``junitxml`` left every one
#: of the three on the interpreter's own exit path.
_RECORDED_REPORT_OPTION = "xmlpath"

#: The status the CI exit path below carries. It starts at pytest's INTERNAL_ERROR
#: rather than at 0, because ``pytest_sessionfinish`` is what overwrites it and that
#: hook does not run when the session dies before it: a raising ``pytest_sessionstart``
#: or an earlier ``sessionfinish`` hook doing the same. Seeded with 0, the CI exit path
#: would then report SUCCESS for a run that errored, which is worse than the crash it
#: exists to avoid. Measured: a sessionstart that raises exits 3 without CI, 0 with
#: CI=1, and 3 again with ``WEBFOOT_KEEP_INTERPRETER_EXIT=1``.
_SESSION_EXIT_STATUS = int(pytest.ExitCode.INTERNAL_ERROR)

#: Rule S (ticket SPEED-GATE-001) budgets one test at 5 s, or 30 s for the
#: integration directory, which is the rom gate. Each entry is (measured seconds, the
#: run and SHA it was measured on, why it is slow, owning ticket), and its allowance is
#: max(measured * `_SPEED_EXCEPTION_SLACK`, budget): the budget is the floor, so slack is
#: proportional and only a node measured over the budget gets more than the budget.
_SPEED_BUDGET_SECONDS = 5.0
_SPEED_ROM_BUDGET_SECONDS = 30.0
_SPEED_EXCEPTION_SLACK = 1.5
_SPEED_RERUN_VARIABLE = "WEBFOOT_SPEED_RERUN"
_BUDGET_EXCEPTIONS: dict[str, tuple[float, str, str, str]] = {
    "tests/unit/test_architecture.py::test_observations_never_fail_the_run":
        (6.853, "38610899807 89fb181b", "duplicates the gates job: tools.quality.architecture", "SPEED-GATE-001"),
    "tests/unit/test_architecture.py::test_the_real_tree_respects_the_import_direction":
        (3.243, "38610899807 89fb181b", "duplicates the gates job: tools.quality.architecture (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_architecture.py::test_the_report_is_deterministic":
        (6.504, "38610899807 89fb181b", "duplicates the gates job: tools.quality.architecture", "SPEED-GATE-001"),
    "tests/unit/test_architecture.py::test_the_repository_passes_its_own_purity_check":
        (3.541, "38610899807 89fb181b", "duplicates the gates job: tools.quality.architecture (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_dev_tools.py::test_the_writer_refuses_an_empty_message":
        (3.614, "38610899807 89fb181b", "drives the commit message probe over a throwaway repository (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_dragonbyte_foundation.py::test_the_application_starts_and_stays_alive_offscreen":
        (3.013, "38610899807 89fb181b", "duplicates the gates job: tools.quality.architecture, plus an AST parse (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_dragonbyte_foundation.py::test_the_real_tree_passes_the_gate_and_the_package_never_imports_the_beta":
        (6.296, "38600996718 f55e32d8", "duplicates the gates job: tools.quality.architecture, plus an AST parse", "SPEED-GATE-001"),
    "tests/unit/test_frozen_containers.py::test_no_frozen_dataclass_in_tools_hands_out_a_mutable_container":
        (4.406, "38610899807 89fb181b", "walks every frozen dataclass in tools/ (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_graphics_override_sdk.py::test_pack_gba_colour_is_the_exact_inverse_of_the_word_decode":
        (8.376, "38600996718 f55e32d8", "an exhaustive 32768 colour round trip", "SPEED-GATE-001"),
    "tests/unit/test_local_ci_script.py::test_a_cleanup_failure_reaches_the_record":
        (36.700, "local 2026-10-14 venv 3.12.10", "drives scripts/local-ci.ps1 in a throwaway worktree", "SPEED-GATE-001"),
    "tests/unit/test_local_ci_script.py::test_a_failed_step_keeps_its_captured_output":
        (40.480, "local 2026-10-14 venv 3.12.10", "drives scripts/local-ci.ps1 in a throwaway worktree", "SPEED-GATE-001"),
    "tests/unit/test_local_ci_script.py::test_a_green_run_passes_so_the_red_guard_is_not_vacuous":
        (37.450, "local 2026-10-14 venv 3.12.10", "drives scripts/local-ci.ps1 in a throwaway worktree", "SPEED-GATE-001"),
    "tests/unit/test_local_ci_script.py::test_a_green_run_passes_when_the_pinned_files_are_present":
        (36.980, "local 2026-10-14 venv 3.12.10", "drives scripts/local-ci.ps1 in a throwaway worktree", "SPEED-GATE-001"),
    "tests/unit/test_local_ci_script.py::test_a_later_run_keeps_the_earlier_runs_artifacts_and_names_do_not_collide":
        (69.550, "local 2026-10-14 venv 3.12.10", "drives scripts/local-ci.ps1 in a throwaway worktree", "SPEED-GATE-001"),
    "tests/unit/test_local_ci_script.py::test_a_red_quality_step_fails_the_record":
        (40.060, "local 2026-10-14 venv 3.12.10", "drives scripts/local-ci.ps1 in a throwaway worktree", "SPEED-GATE-001"),
    "tests/unit/test_local_ci_script.py::test_an_early_failure_leaves_no_clone_or_worktree":
        (54.220, "local 2026-10-14 venv 3.12.10", "drives scripts/local-ci.ps1 in a throwaway worktree", "SPEED-GATE-001"),
    "tests/unit/test_local_ci_script.py::test_the_gate_refuses_when_the_record_directory_cannot_be_computed":
        (38.680, "local 2026-10-14 venv 3.12.10", "drives scripts/local-ci.ps1 in a throwaway worktree", "SPEED-GATE-001"),
    "tests/unit/test_logx_synthesis_audit.py::test_live_code_carries_no_superseded_assumption_of_an_unrecorded_kind":
        (3.156, "38610899807 89fb181b", "reads and compares the recorded synthesis reports (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_logx_synthesis_audit.py::test_recorded_production_defects_are_exactly_the_ones_the_synthesis_names":
        (3.057, "38610899807 89fb181b", "reads and compares the recorded synthesis reports (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_logx_synthesis_audit.py::test_the_audit_is_deterministic":
        (6.179, "38610899807 89fb181b", "reads and compares the recorded synthesis reports", "SPEED-GATE-001"),
    "tests/unit/test_logx_synthesis_audit.py::test_the_corrected_files_no_longer_carry_a_superseded_assumption":
        (3.175, "38600996718 f55e32d8", "reads and compares the recorded synthesis reports (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_logx_synthesis_audit.py::test_the_recorded_stale_text_set_is_exactly_what_remains":
        (3.350, "38610899807 89fb181b", "reads and compares the recorded synthesis reports (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_mgba_launch_coverage.py::test_every_registered_site_uses_the_gate_its_proof_names":
        (7.575, "38600996718 f55e32d8", "the scan of every test module for launch sites", "SPEED-GATE-001"),
    "tests/unit/test_mgba_launch_coverage.py::test_no_exemption_names_a_registered_launch_site":
        (11.600, "38610899807 89fb181b", "the scan of every test module for launch sites", "SPEED-GATE-001"),
    "tests/unit/test_mgba_launch_coverage.py::test_the_current_tree_has_no_unregistered_launch_site":
        (10.129, "38610899807 89fb181b", "the scan of every test module for launch sites", "SPEED-GATE-001"),
    "tests/unit/test_pre_merge_check.py::test_a_master_commit_on_a_disjoint_path_passes":
        (5.357, "38610899807 89fb181b", "drives the pre-merge gate over throwaway repositories", "SPEED-GATE-001"),
    "tests/unit/test_pre_merge_check.py::test_a_supplied_merged_tree_digest_that_does_not_match_fails":
        (4.055, "38610899807 89fb181b", "drives the pre-merge gate over throwaway repositories (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_pre_merge_check.py::test_an_unchanged_master_is_a_pass":
        (3.123, "38610899807 89fb181b", "drives the pre-merge gate over throwaway repositories (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_pre_merge_check.py::test_the_focused_run_refuses_a_missing_or_empty_inventory":
        (5.010, "local 2026-10-14 venv 3.12.10", "drives the pre-merge gate over throwaway repositories", "SPEED-GATE-001"),
    "tests/unit/test_pre_merge_check.py::test_the_primary_a_subdirectory_of_it_and_a_linked_worktree":
        (4.269, "38600996718 f55e32d8", "drives the pre-merge gate over throwaway repositories (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_pre_merge_check.py::test_the_primary_checkout_is_refused_and_a_linked_worktree_is_not":
        (6.887, "38610899807 89fb181b", "drives the pre-merge gate over throwaway repositories", "SPEED-GATE-001"),
    "tests/unit/test_project_safety.py::test_built_wheel_uses_packaged_profile_catalog":
        (6.192, "38610899807 89fb181b", "builds a wheel with pip", "SPEED-GATE-001"),
    "tests/unit/test_public_surface.py::test_the_public_surface_is_clean":
        (22.902, "38610899807 89fb181b", "duplicates the gates job: tools.quality.public_surface --all", "SPEED-GATE-001"),
    "tests/unit/test_public_surface.py::test_the_report_is_deterministic":
        (36.608, "38610899807 89fb181b", "duplicates the gates job: tools.quality.public_surface --all", "SPEED-GATE-001"),
    "tests/unit/test_readability.py::test_a_load_bearing_exception_suppresses_exactly_its_own_hits":
        (10.004, "38610899807 89fb181b", "duplicates the gates job: tools.quality.readability --all", "SPEED-GATE-001"),
    "tests/unit/test_readability.py::test_findings_are_ordered_by_path_line_signal":
        (9.858, "38610899807 89fb181b", "duplicates the gates job: tools.quality.readability --all", "SPEED-GATE-001"),
    "tests/unit/test_readability.py::test_the_enemy_behaviour_sense_is_covered_by_a_written_exception":
        (9.858, "38600996718 f55e32d8", "duplicates the gates job: tools.quality.readability --all", "SPEED-GATE-001"),
    "tests/unit/test_readability.py::test_the_json_document_has_a_stable_schema":
        (9.972, "38610899807 89fb181b", "duplicates the gates job: tools.quality.readability --all", "SPEED-GATE-001"),
    "tests/unit/test_readability.py::test_the_real_tree_reports_nothing_in_the_shipping_toolkit":
        (10.264, "38600996718 f55e32d8", "duplicates the gates job: tools.quality.readability --all", "SPEED-GATE-001"),
    "tests/unit/test_readability.py::test_the_summary_says_advisories_never_change_the_exit_code":
        (7.126, "38600996718 f55e32d8", "duplicates the gates job: tools.quality.readability --all", "SPEED-GATE-001"),
    "tests/unit/test_readability.py::test_two_runs_write_byte_identical_json":
        (18.255, "38600996718 f55e32d8", "duplicates the gates job: tools.quality.readability --all", "SPEED-GATE-001"),
    "tests/unit/test_text_tool_list.py::test_a_badge_is_as_wide_as_its_own_word_and_not_the_whole_cell":
        (4.552, "38610899807 89fb181b", "builds and themes a real Qt list view (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_text_tool_list.py::test_a_map_heading_carries_the_inference_its_link_rests_on":
        (5.151, "38610899807 89fb181b", "builds and themes a real Qt list view", "SPEED-GATE-001"),
    "tests/unit/test_text_tool_list.py::test_the_empty_speaker_state_says_drawn_and_never_claims_a_stored_speaker":
        (3.987, "38610899807 89fb181b", "builds and themes a real Qt list view (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_text_tool_list.py::test_the_export_window_shows_the_facts_the_digest_and_one_close_action":
        (7.990, "38600996718 f55e32d8", "builds and themes a real Qt list view", "SPEED-GATE-001"),
    "tests/unit/test_text_tool_list.py::test_the_row_is_drawn_with_one_divider_the_selection_and_the_state_badge":
        (3.028, "38600996718 f55e32d8", "builds and themes a real Qt list view (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_text_tool_list.py::test_the_state_chips_narrow_the_list_and_the_clear_action_restores_it":
        (8.397, "38600996718 f55e32d8", "builds and themes a real Qt list view", "SPEED-GATE-001"),
    "tests/unit/test_text_tool_list.py::test_the_status_cell_paints_no_fill_of_its_own_and_the_divider_runs_its_width":
        (5.659, "38600996718 f55e32d8", "builds and themes a real Qt list view", "SPEED-GATE-001"),
    "tests/unit/test_text_tool_shell.py::test_a_closed_window_does_not_leave_its_export_summary_shown":
        (3.983, "38610899807 89fb181b", "builds and themes the shell window (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_text_tool_shell.py::test_a_corrupt_settings_file_answers_the_defaults":
        (4.832, "38610899807 89fb181b", "builds and themes the shell window (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_text_tool_shell.py::test_a_saved_project_edit_survives_editing_and_undoing_in_the_window":
        (4.352, "38610899807 89fb181b", "builds and themes the shell window (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_text_tool_shell.py::test_a_status_message_hands_the_row_identity_back_on_the_next_selection":
        (4.796, "38610899807 89fb181b", "builds and themes the shell window (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_text_tool_shell.py::test_an_export_clears_the_unsaved_marker_and_reports_its_digest":
        (9.314, "38610899807 89fb181b", "builds and themes the shell window", "SPEED-GATE-001"),
    "tests/unit/test_text_tool_shell.py::test_smoke_exits_zero":
        (4.906, "38600996718 f55e32d8", "builds and themes the shell window (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_text_tool_shell.py::test_smoke_exits_zero_over_the_synthetic_image":
        (6.756, "38610899807 89fb181b", "builds and themes the shell window", "SPEED-GATE-001"),
    "tests/unit/test_text_tool_shell.py::test_the_window_without_an_image_shows_what_to_do":
        (4.732, "38610899807 89fb181b", "builds and themes the shell window (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_text_tool_shell.py::test_undo_of_a_rename_beside_a_line_edit_restores_and_does_not_wedge":
        (6.341, "38610899807 89fb181b", "builds and themes the shell window", "SPEED-GATE-001"),
    "tests/unit/test_text_tool_theme.py::test_every_control_class_is_painted_in_the_theme_ink":
        (3.716, "38600996718 f55e32d8", "paints every control class in the theme ink (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_text_tool_theme.py::test_the_extra_control_classes_are_painted_in_the_theme_ink":
        (5.139, "38610899807 89fb181b", "paints every control class in the theme ink", "SPEED-GATE-001"),
    "tests/unit/test_text_tool_theme_handback.py::test_taking_the_theme_back_restores_an_untouched_control":
        (3.573, "38610899807 89fb181b", "applies the theme and hands it back around a control (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_ui_graphics_probe.py::test_enumeration_reports_the_literal_container_and_its_owner":
        (3.017, "38600996718 f55e32d8", "runs the graphics probe report over its corpus (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_ui_graphics_probe.py::test_report_records_the_pre_filter_corpus_hits":
        (4.602, "38610899807 89fb181b", "runs the graphics probe report over its corpus (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_warp_randomizer_gui.py::test_the_application_is_configured_with_the_shared_dragonbyte_z_theme":
        (8.210, "38615873476 a762e52", "applies the shared DragonByte Z theme in a cold process", "SPEED-GATE-001"),
    "tests/unit/test_write_invariants_property.py::test_a_no_op_plan_reproduces_the_base":
        (3.852, "38610899807 89fb181b", "a hypothesis search over generated span pairs (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_write_invariants_property.py::test_applying_a_plan_changes_exactly_the_declared_bytes":
        (5.340, "38615873476 a762e52", "a hypothesis search over generated span pairs", "SPEED-GATE-001"),
    "tests/unit/test_write_invariants_property.py::test_identical_physical_writes_collapse_deterministically":
        (3.608, "38610899807 89fb181b", "a hypothesis search over generated span pairs (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_write_invariants_property.py::test_normalized_changes_do_not_depend_on_input_order":
        (3.757, "38600996718 f55e32d8", "a hypothesis search over generated span pairs (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_write_invariants_property.py::test_overlapping_spans_fail_closed_in_the_planner":
        (4.736, "38610899807 89fb181b", "a hypothesis search over generated span pairs (headroom below the budget)", "SPEED-GATE-001"),
    "tests/unit/test_write_invariants_property.py::test_writes_that_disagree_about_one_span_fail_closed":
        (6.471, "38600996718 f55e32d8", "a hypothesis search over generated span pairs", "SPEED-GATE-001"),
}


# --- a mutable ROM fixture that cannot share a file with a protected input -----
#
# OWNER R3, 2026-10-09, after the incident. A test that mutates ROM bytes must
# never do it at the canonical path - that path is a hard link shared with other
# worktrees, so one in-place write changed every tree at once. Every helper below
# lives in `tests/rom_support.py` so a test module can import it without depending
# on conftest import order; this module keeps only the fixture that hands the
# suite's mutable ROM copy over.


@pytest.fixture
def mutable_rom(tmp_path):
    """A mutable copy of the canonical image, sharing no file with a protected input.

    The safety this fixture exists for is in `rom_support.mutable_rom_copy`: the
    copy is created in pytest's temporary root and its file identity is proved
    distinct from every protected repository input before it is returned.
    """
    return mutable_rom_copy(tmp_path)


@pytest.fixture(autouse=True)
def _isolate_destination_policy_cache():
    """Keep one test's protected-input index out of another's.

    `tools.webfoot.destination` caches the protected-input index per checkout root,
    which is what keeps the check cheap on every emitted image. A test that points
    the policy at a temporary root must not leave that root's index behind for a
    later test to read, so the cache is cleared around every test.
    """
    from tools.webfoot import destination

    destination._PROTECTED_CACHE.clear()
    yield
    destination._PROTECTED_CACHE.clear()

#: Every candidate test file pytest offered to this session's collection, as
#: :func:`_path_key` strings. Populated by :func:`pytest_collect_file`.
_CANDIDATE_TEST_FILES: set[str] = set()

#: Every test file pytest actually descended into in this run, whether it
#: produced items, skipped as a whole, or failed to import. Populated by
#: :func:`pytest_collectreport`. This - not the candidate set - is what makes a
#: required module "part of this run".
_ATTEMPTED_TEST_FILES: set[str] = set()

#: Every test file that contributed at least one collected item, in the same
#: key form. Populated by :func:`pytest_collection_modifyitems` before any
#: ``-m``/``-k`` deselection, because a deselected file was still collected.
_COLLECTED_TEST_FILES: set[str] = set()

#: Why a file collapsed, for the files pytest reported a whole-file collection
#: skip for. Populated by :func:`pytest_collectreport`.
_COLLAPSED_REASONS: dict[str, str] = {}

#: Every test this session reported as skipped, as ``{node id: reason}``.
#: Populated by :func:`pytest_runtest_logreport` and reported once by
#: :func:`pytest_sessionfinish`.
_SKIPPED_TEST_REASONS: dict[str, str] = {}

#: Every test's call-phase wall time in this session, as ``{node id: seconds}``.
#: On the controller under xdist this holds the whole session.
_TEST_SECONDS: dict[str, float] = {}

#: pytest's rootdir, captured by :func:`pytest_configure`. Collection reports
#: identify a file by a node id, which is relative to this root.
_ROOTDIR: Path | None = None


def hand_back_application(application, state) -> None:
    """Hand the Qt application back as it was, given a state captured earlier.

    The editor's theme is applied to the whole QApplication, so a module that installs it also
    changes what every other product's window measures in the same process. Measured with one
    ordinary button: applying it takes the size hint from 20 to 26, which is the application
    stylesheet, and the editor's proxy style moves it further.

    The stylesheet is cleared first because that is what moves the metrics, then the palette is
    restored, then the style is put back BY NAME. The old style object is never kept and never
    handed back: installing a theme lets Qt delete the style the application owned, so passing
    that wrapper to `setStyle` raises "Internal C++ object already deleted" instead of
    restoring anything. A wrapper that is already invalid is the case the bare exception below
    covers, and it is a refusal to touch the application rather than a silent half restore.
    """
    from PySide6.QtWidgets import QStyleFactory

    palette, sheet, was = state
    try:
        application.setStyleSheet(sheet)
        application.setPalette(palette)
        current = application.style().metaObject().className()
    except RuntimeError:
        return
    if current == was:
        return
    for key in QStyleFactory.keys():
        if QStyleFactory.create(key).metaObject().className() == was:
            application.setStyle(key)
            return


def capture_application(application):
    """The part of an application's appearance this suite has to hand back.

    `was` is the style's CLASS NAME rather than the object, because the object does not survive
    the theme it is replaced by.
    """
    return (application.palette(), application.styleSheet(),
            application.style().metaObject().className())


def pytest_configure(config: pytest.Config) -> None:
    """Enable the fault handler, so a crash in a native call names the Python frame.

    The crash it was added for, and what the handler did and did not answer, are recorded in
    ``docs/research/RETRO_QT_SHUTDOWN_001.md``. The handler is stdlib and prints the frame
    that was executing when a fatal signal arrives. It writes to the interpreter's own
    stderr, which pytest's capture does not own, because the crash happens after the last
    test when capture is being torn down itself.
    """
    faulthandler.enable(file=sys.__stderr__)

    """Make the temp root one ``tmp_path`` can actually live in.

    pytest derives its basetemp from ``tempfile.gettempdir()``, so redirecting
    that root - rather than pinning ``--basetemp`` - keeps every other property
    of the default path: a numbered ``pytest-N`` subdirectory, the
    ``tmp_path_retention_count`` pruning of old failed runs, removal of the
    whole root after a green run, and safety between two runs that happen to
    share a worktree (a pinned ``--basetemp`` is deleted at startup, so
    concurrent runs would destroy each other's directories mid-run).

    ``tempfile.tempdir`` is read lazily, on the first basetemp request, so this
    does not depend on hook ordering relative to ``_pytest.tmpdir``. Nothing in
    this repository reads the process temp root itself; only pytest's own
    temporary directories move.

    It also captures pytest's rootdir, because a collection report identifies a
    file by a node id relative to that root.
    """
    global _REDIRECTED_TEMPROOT, _ROOTDIR

    _ROOTDIR = Path(config.rootpath)

    if config.option.basetemp is not None:
        # An explicit --basetemp is the caller's choice and wins outright.
        return

    temproot = Path(tempfile.gettempdir()).resolve()
    default_root = temproot / f"pytest-of-{_user_name()}"
    problem = _temp_root_problem(default_root)
    if problem is None:
        return

    isolated_root = temproot / f"webfoot-pytest-temproot-{_user_name()}"
    if _temp_root_problem(isolated_root) is not None:
        # Nothing better to offer: let pytest report its own failure rather
        # than redirecting to a root that is just as unusable.
        return
    tempfile.tempdir = str(isolated_root)
    _REDIRECTED_TEMPROOT = (isolated_root, problem)


def pytest_report_header(config: pytest.Config) -> list[str]:
    """State the gates, the temporary root and the ROM situation, once."""
    lines = [
        "test gates: " + " | ".join(f"-m {gate}" for gate in GATE_DESCRIPTIONS),
        "gate docs: docs/testing.md",
    ]

    if _REDIRECTED_TEMPROOT is not None:
        root, problem = _REDIRECTED_TEMPROOT
        lines.append(
            f"temp root: {root} (pytest's own {problem}; the process temp root "
            "was redirected, and --basetemp overrides it)"
        )
    else:
        basetemp = config.option.basetemp
        root = Path(basetemp) if basetemp else Path(tempfile.gettempdir())
        lines.append(f"temp root: {root}")
        if basetemp and Path(basetemp).resolve().is_relative_to(REPOSITORY_ROOT):
            lines.append(
                "temp root WARNING: --basetemp is inside the repository, so the "
                "generated-output guards will refuse those paths and the "
                "output-safety tests that expect an accepted output will fail by "
                "design (test_asset_export_output_safety, and the mGBA capture "
                "build-tree check when the root is under build/); choose a "
                "directory outside the work tree"
            )

    lines.append(_rom_status())
    if Path.cwd().resolve() != REPOSITORY_ROOT:
        lines.append(
            f"working directory WARNING: {Path.cwd()} is not {REPOSITORY_ROOT}; "
            "tests that read config/, upstreams.lock or roms/ relatively will fail"
        )
    return lines


def pytest_collect_file(file_path: Path, parent: pytest.Collector):
    """Record every candidate test file pytest offers the collection.

    Returning ``None`` leaves the normal Python collector to build the module.
    What this hook does *not* mean is "pytest tried to collect this file": when
    an argument names one file, pytest still walks the whole sibling directory
    to match that argument, so the hook fires for every file beside it
    (measured: 119 candidates for a single-file run). "Pytest descended into
    it" is recorded by :func:`pytest_collectreport` instead, and that is the
    distinction a targeted subset depends on.
    """
    path = Path(file_path)
    if _is_test_file(path):
        _CANDIDATE_TEST_FILES.add(_path_key(path))
    return None


def pytest_collectreport(report: pytest.CollectReport) -> None:
    """Record a file pytest really collected, and why it collapsed if it did.

    pytest reports every collector it descends into, so this fires once per test
    file in the run - and produces no report at all for a file a targeted subset
    never went into. A module-level ``pytest.importorskip`` or ``pytest.skip``
    arrives here as a skipped report of the file itself, whose ``longrepr``
    already carries the message a reader needs ("could not import
    'PySide6.QtWidgets'").
    """
    path = _reported_test_path(report)
    if path is None:
        return
    key = _path_key(path)
    _ATTEMPTED_TEST_FILES.add(key)
    if report.skipped:
        _COLLAPSED_REASONS[key] = _collapsed_reason(report)


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Tag every collected test with the gates its file belongs to.

    Also records which files actually contributed a test. ``tryfirst`` puts the
    tagging before the ``-m``/``-k`` deselection hooks (which are ``trylast``),
    so the markers exist when those filters run and the recorded files describe
    collection rather than the final selection: a module filtered out by ``-m``
    was collected and executed nothing, which is not the collapse this guard is
    about.
    """
    for item in items:
        for gate in gates_for(item.path):
            item.add_marker(getattr(pytest.mark, gate))
        if _is_test_file(item.path):
            _COLLECTED_TEST_FILES.add(_path_key(item.path))


@pytest.hookimpl(trylast=True, specname="pytest_collection_modifyitems")
def pytest_deselect_other_shards(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Keep only this shard's nodes, when the shard variables name one.

    The other shards' nodes are DESELECTED, never marked skipped: the junit
    report and the skip census must describe the tests this shard ran, so its
    counts stay comparable with the single-process record. Untouched when the
    variables are unset, which is every local run and the local full-CI record.

    ``specname`` is load-bearing. The tagging hook above already owns the name
    ``pytest_collection_modifyitems``, and a module defines one function per
    name, so pluggy is told which hook to register this one against. It is
    ``trylast``, so the tagging still sees the whole collection and pytest's own
    ``-m``/``-k`` filter has already run; either order leaves the same nodes.
    """
    if os.environ.get(_NESTED_RUN_VARIABLE):
        return
    selection = selection_from_environment()
    if selection is None:
        return
    os.environ[_NESTED_RUN_VARIABLE] = "1"
    count, index = selection
    keep: list[pytest.Item] = []
    deselected: list[pytest.Item] = []
    for item in items:
        path, _, name = item.nodeid.partition("::")
        destination = keep if shard_of(node_identifier(path, name), count) == index else deselected
        destination.append(item)
    if not deselected:
        return
    config.hook.pytest_deselected(items=deselected)
    items[:] = keep


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """Record every skipped test and pytest's reason, for the session census.

    This is the hook the terminal reporter builds its own skip summary from, so
    the census sees the same skips it does; under ``-n auto`` the controller runs
    it for each report a worker sends, which is what keeps the census complete
    there rather than silently empty.
    """
    if report.when == "call":
        _TEST_SECONDS[report.nodeid] = max(_TEST_SECONDS.get(report.nodeid, 0.0),
                                           report.duration)
    if report.skipped:
        _SKIPPED_TEST_REASONS[report.nodeid] = _skip_reason(report)


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Report what the session skipped, and fail it on a collapsed GUI module.

    The checks are at session end because only then is the whole picture known:
    which files were attempted, which contributed a test, why the rest stopped,
    and which tests reported a skip. See the module docstring for the
    CI/local/opt-in scope of the GUI guard and the scope of the census.

    The hook runs LAST, and the status the exit path carries is read at the very end of it,
    because the guard below raises the status and the exit path must carry what the guard
    decided. Measured: reading it first carried 0 over a collapsed shipping surface, so a CI
    job reported success while failing, which is the CQA-22 class.
    """
    collapsed = _collapsed_required_modules()
    collapsed += [entry for entry in _collapsed_gui_modules() if entry not in collapsed]
    if collapsed:
        enforced = _required_gui_surface_is_enforced()
        _report_collapsed_modules(session.config, collapsed, enforced)
        if enforced:
            # pytest has already computed its own status ("no tests ran" is 5 when
            # the only collected module collapsed); a collapsed shipping surface is
            # a test failure, and the summary below says which one.
            session.exitstatus = pytest.ExitCode.TESTS_FAILED
    if _report_speed_breaches(session):
        session.exitstatus = pytest.ExitCode.TESTS_FAILED
    _report_skipped_tests(session.config)
    global _SESSION_EXIT_STATUS
    _SESSION_EXIT_STATUS = int(session.exitstatus if session.exitstatus is not None
                               else exitstatus)


def _is_test_file(path: Path | str) -> bool:
    """True for a ``tests/``-tree file pytest would collect as a test module."""
    name = Path(path).name
    return (
        name.startswith("test_")
        and name.endswith(".py")
        and relative_test_path(path) is not None
    )


def _path_key(path: Path | str) -> str:
    """A comparable key for a test file, case-correct on every platform.

    The hooks below see the same file through two different pytest objects, and
    Windows paths are case-insensitive: normalising here keeps the attempted and
    collected sets comparable without touching the filesystem.
    """
    return os.path.normcase(os.path.abspath(str(path)))


def _reported_test_path(report: pytest.CollectReport) -> Path | None:
    """The test file a collect report is about, or None for a directory/session.

    A collection report names its collector by node id, which is relative to
    pytest's rootdir while the file sits under it - so it is resolved against
    the rootdir captured in :func:`pytest_configure`, never against the process
    working directory.
    """
    nodeid = getattr(report, "nodeid", "")
    if not nodeid:
        return None
    path = Path(nodeid.split("::", 1)[0])
    if not path.is_absolute() and _ROOTDIR is not None:
        path = _ROOTDIR / path
    return path if _is_test_file(path) else None


def _collapsed_reason(report: pytest.CollectReport) -> str:
    """The one-line reason pytest gave for a whole-file collection skip.

    A skipped collection report carries ``(path, lineno, message)`` as its
    ``longrepr``; a failed one carries a formatted exception. Both are reduced
    to the sentence a reader needs, without the surrounding structure.
    """
    longrepr = report.longrepr
    if longrepr is None:
        return "no reason reported by pytest"
    if isinstance(longrepr, (tuple, list)) and len(longrepr) == 3:
        path, lineno, message = longrepr
        # The message of a skipped collection report is prefixed with the
        # outcome ("Skipped: ..."), which pytest's own summary line drops; drop
        # it here too so the reason reads as the reason.
        message = str(message).removeprefix("Skipped: ")
        return f"{message} (reported at {path}:{lineno})"
    lines = [line.strip() for line in str(longrepr).splitlines() if line.strip()]
    return lines[-1] if lines else "no reason reported by pytest"


def _skip_reason(report: pytest.TestReport) -> str:
    """The one-line reason a skipped test reported, without its location.

    The node id the census prints already names the test, so only the message is
    repeated here; a location matters for a whole-file collapse, which is why
    :func:`_collapsed_reason` keeps it.
    """
    longrepr = report.longrepr
    if isinstance(longrepr, (tuple, list)) and len(longrepr) == 3:
        return str(longrepr[2]).removeprefix("Skipped: ")
    return _collapsed_reason(report)


def _relative_node_id(node_id: str) -> str:
    """A node id in the ``unit/test_x.py::test_y`` form the gate lists use."""
    path, _, test = node_id.partition("::")
    relative = relative_test_path(path) or path
    return f"{relative}::{test}" if test else relative


def _is_artefact_dependent(relative_node_id: str) -> bool:
    """Whether a declaration in ``ARTEFACT_DEPENDENT_TESTS`` covers this test.

    A parametrised member is declared by its function, so a reported
    ``::test_x[param]`` matches the ``::test_x`` entry.
    """
    return any(
        relative_node_id == declared or relative_node_id.startswith(f"{declared}[")
        for declared in ARTEFACT_DEPENDENT_TESTS
    )


#: How a declaration in ``ARTEFACT_DEPENDENT_TESTS`` is marked in the census.
_DECLARED_ARTEFACT_MARK = "declared artefact dependency (see tests/gates.py)"


def _report_skipped_tests(config: pytest.Config) -> None:
    """Print every test this session skipped, with pytest's own reason.

    Nothing is printed when nothing skipped, so a healthy run stays quiet, and
    nothing here can fail the session: the census states what did not execute
    rather than enforcing it (``ARTEFACT_DEPENDENT_TESTS`` in ``tests/gates.py``
    says why an artefact skip must not fail CI).
    """
    entries = []
    for node_id in sorted(_SKIPPED_TEST_REASONS):
        relative = _relative_node_id(node_id)
        entries.append(
            (relative, _SKIPPED_TEST_REASONS[node_id], _is_artefact_dependent(relative))
        )
    if not entries:
        return
    # One line per skipped test, so a `-m rom` run with no canonical image prints
    # one per test where pytest's own summary groups them. Cap the list here if
    # that log becomes the problem rather than the report.
    lines = [
        f"skipped: {relative} - {reason}"
        + (f" [{_DECLARED_ARTEFACT_MARK}]" if declared else "")
        for relative, reason, declared in entries
    ]
    declared = sum(1 for _, _, is_declared in entries if is_declared)
    lines.append(
        f"{len(entries)} skipped test(s), {declared} of them declared artefact "
        "dependencies; reported, never failed."
    )

    terminal = config.pluginmanager.get_plugin("terminalreporter")
    if terminal is None:  # pragma: no cover - only in an embedded/plugin run
        for line in lines:
            print(line)
        return
    terminal.write_sep("=", f"tests skipped ({len(entries)})")
    for line in lines:
        terminal.write_line(line)


def _speed_budget(nodeid: str, rom: bool) -> tuple[float, float, str]:
    """The budget, the allowance and the owning ticket for one node."""
    budget = _SPEED_ROM_BUDGET_SECONDS if rom else _SPEED_BUDGET_SECONDS
    entry = _BUDGET_EXCEPTIONS.get(nodeid)
    if entry is None:
        return budget, budget, "SPEED-GATE-001"
    measured, _source, _why, ticket = entry
    return budget, max(measured * _SPEED_EXCEPTION_SLACK, budget), ticket


def _junit_seconds(report: Path, nodeid: str) -> float | None:
    if not report.is_file():
        return None
    try:
        root = ET.parse(report).getroot()
    except ET.ParseError:
        return None
    for case in root.iter("testcase"):
        name = f"{case.get('classname', '').replace('.', '/')}.py::{case.get('name', '')}"
        if name == nodeid:
            return float(case.get("time") or 0.0)
    return None


def _remeasure(nodeid: str) -> float | None:
    """One single-node re-run, measured the same way, so a breach needs two timings.

    The child run is a measurement only: it carries `_SPEED_RERUN_VARIABLE`, which
    makes this guard stand down inside it.
    """
    with tempfile.TemporaryDirectory() as directory:
        report = Path(directory) / "rerun.xml"
        environment = dict(os.environ)
        environment[_SPEED_RERUN_VARIABLE] = "1"
        try:
            subprocess.run(
                [sys.executable, "-m", "pytest", nodeid, "-q", "-p", "no:cacheprovider",
                 f"--junitxml={report}"],
                cwd=str(REPOSITORY_ROOT), env=environment, capture_output=True, timeout=900,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        return _junit_seconds(report, nodeid)


def _report_speed_breaches(session: pytest.Session) -> bool:
    """Name every test over its rule-S allowance, and fail the session when one is."""
    if getattr(session.config, "workerinput", None):
        return False
    if os.environ.get(_SPEED_RERUN_VARIABLE):
        return False
    breaches = []
    for nodeid, seconds in sorted(_TEST_SECONDS.items()):
        # The rom gate is the integration directory (tests/gates.py:54), which is
        # what the controller can see of a worker's node: the marked items are not
        # collected here under xdist.
        budget, allowance, ticket = _speed_budget(nodeid, nodeid.startswith("tests/integration/"))
        if seconds <= allowance:
            continue
        again = _remeasure(nodeid)
        if again is not None and again <= allowance:
            continue
        signal = "unmeasured" if again is None else f"{again:.2f}s"
        breaches.append(
            f"{nodeid} took {seconds:.2f}s, re-run {signal}, over its {budget:.1f}s budget "
            f"and {allowance:.1f}s allowance, owned by {ticket}"
        )
    if not breaches:
        return False
    terminal = session.config.pluginmanager.get_plugin("terminalreporter")
    if terminal is None:  # pragma: no cover - only in an embedded/plugin run
        for line in breaches:
            print(line)
        return True
    terminal.write_sep("=", f"tests over the rule-S budget ({len(breaches)})", red=True)
    for line in breaches:
        terminal.write_line(line)
    return True


def _required_gui_surface_is_enforced() -> bool:
    """Whether a collapsed required GUI module must fail this session.

    CI is the case the guard exists for. ``WEBFOOT_REQUIRE_GUI_TESTS=1`` forces
    the same failure locally so the guard can be mutation-tested; every other
    local run only warns, because a developer without PySide6 is allowed to run
    the portable suite (``docs/testing.md``).
    """
    if os.environ.get(_REQUIRE_GUI_TESTS_VARIABLE) == "1":
        return True
    return any(os.environ.get(name) for name in _CI_ENVIRONMENT_VARIABLES)


def pytest_unconfigure(config: pytest.Config) -> None:
    """In CI, or under the local full-CI record gate, leave before CPython tears the loaded
    Qt extensions down.

    The crash this path exists for, the pipelines that carry it and the instrument that can
    name it are recorded in ``docs/research/RETRO_QT_SHUTDOWN_001.md``: one definition of
    that fact rather than a second telling here.

    This is a mitigation, not a fix. It runs under CI, and under a run whose result is read
    from a machine-readable report - the local record gate passes ``--junitxml`` and cannot
    set ``CI``, because that gate is master's reviewed script and runs the suite as an
    ordinary local process. Measured 2026-10-13: the record gate's own suite step for this
    ticket reported exit 0 while its captured stderr carried ``Fatal Python error: Aborted``,
    so that record could not be called crash-free; the two crash-free runs on this line are
    the CI ones, where this path already ran. A local run keeps the interpreter's own exit
    path. ``os._exit`` is deliberate where ``sys.exit`` would not do: the point is to skip the
    finalizers. Streams are flushed first, because ``os._exit`` does not flush them.
    ``WEBFOOT_KEEP_INTERPRETER_EXIT=1`` keeps the ordinary exit so the crash can still be
    observed from CI by whoever works on it.
    """
    if os.environ.get("WEBFOOT_KEEP_INTERPRETER_EXIT") == "1":
        return
    if not _run_result_is_recorded(config):
        return
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(_SESSION_EXIT_STATUS)


def _run_result_is_recorded(config: pytest.Config) -> bool:
    """Whether this run is CI or one whose result is read from a machine-readable report.

    CI is the environment. The local full-CI record gate is the report: it runs
    ``scripts/local-ci.ps1``, which passes ``--junitxml`` and sets no CI variable. A local
    developer run passes neither. The report option is read defensively because a caller may
    hand this hook a stub config, which is how the exit-path cases drive it, and it is read
    under its destination name - ``xmlpath`` - because that is the attribute pytest actually
    sets; see :data:`_RECORDED_REPORT_OPTION`.
    """
    if any(os.environ.get(name) for name in _CI_ENVIRONMENT_VARIABLES):
        return True
    option = getattr(config, "option", None)
    return bool(getattr(option, _RECORDED_REPORT_OPTION, None))


def _collapsed_required_modules() -> list[tuple[str, str]]:
    """Required GUI modules that this run collected but that produced no test.

    Three conditions, in this order, and the order is what keeps a targeted run
    quiet:

    1. the file exists here (a module another contributor has not landed yet is
       not this session's failure);
    2. pytest offered it as a candidate *and* descended into it
       (``_CANDIDATE_TEST_FILES`` is a superset of ``_ATTEMPTED_TEST_FILES``;
       requiring both means the guard can only fire for a file this run really
       opened, so ``pytest tests/unit/test_map_render.py`` stays quiet);
    3. it contributed no collected item (which is the collapse).
    """
    collapsed: list[tuple[str, str]] = []
    for relative in REQUIRED_GUI_MODULES:
        path = REPOSITORY_ROOT / TESTS_DIRECTORY / relative
        if not path.is_file():
            continue
        key = _path_key(path)
        if key not in _CANDIDATE_TEST_FILES or key not in _ATTEMPTED_TEST_FILES:
            continue
        if key in _COLLECTED_TEST_FILES:
            continue
        collapsed.append(
            (relative, _COLLAPSED_REASONS.get(key, "contributed no collected test"))
        )
    return collapsed


def _collapsed_gui_modules() -> list[tuple[str, str]]:
    """Every opened test module that collapsed on a PySide6 import.

    ``REQUIRED_GUI_MODULES`` is the explicit shipping-surface regression set. This
    generalisation covers the rest: a Workbench module that carries its own
    module-level ``pytest.importorskip`` and was never registered collapses to one
    ``SKIPPED`` line, which leaves the job green while the surface it tests never
    ran. The reason is pytest's own collection report, so this is evidence of what
    happened rather than a guess made from the source text.

    The rule is keyed on the reason naming PySide6, because that is what the
    shipping GUI surface imports. A module that collapsed because some other
    optional dependency was missing is not this guard's business; every Qt-guarded
    unit module in the tree spells its guard ``importorskip("PySide6...")``, so all
    of them are covered.
    """
    collapsed: list[tuple[str, str]] = []
    for key in sorted(_CANDIDATE_TEST_FILES & _ATTEMPTED_TEST_FILES):
        if key in _COLLECTED_TEST_FILES:
            continue
        reason = _COLLAPSED_REASONS.get(key, "")
        if "PySide6" not in reason:
            continue
        collapsed.append((relative_test_path(key) or key, reason))
    return collapsed


def _report_collapsed_modules(
    config: pytest.Config,
    collapsed: list[tuple[str, str]],
    enforced: bool,
) -> None:
    """Print the collapsed modules where a reader of the job log will see them."""
    verdict = "FAILING THE SESSION" if enforced else "WARNING ONLY (not CI)"
    lines = [
        f"required GUI module COLLAPSED: {relative} - collected by this run, "
        f"contributed no test ({reason})"
        for relative, reason in collapsed
    ]
    lines.append(
        "A required GUI module is a shipping Workbench test file named in "
        "REQUIRED_GUI_MODULES (tests/gates.py) and it must execute, not skip as "
        "a whole: that is audit finding CQA-08. CI installs "
        '`-e ".[dev,workbench,research]"` and sets QT_QPA_PLATFORM=offscreen '
        "for exactly these modules (.gitlab-ci.yml)."
    )
    if enforced:
        lines.append(
            "Scope: CI (GITLAB_CI/CI) or "
            f"{_REQUIRE_GUI_TESTS_VARIABLE}=1, so the exit status is a failure. "
            "Set the variable to 0 and install .[dev,workbench,research] if this "
            "is a deliberate local environment without Qt."
        )
    else:
        lines.append(
            "Scope: this is not a CI run, so it is reported and not failed - a "
            "developer without PySide6 may run the portable suite. Set "
            f"{_REQUIRE_GUI_TESTS_VARIABLE}=1 (or run under CI) to make it fail."
        )

    terminal = config.pluginmanager.get_plugin("terminalreporter")
    if terminal is None:  # pragma: no cover - only in an embedded/plugin run
        for line in lines:
            print(line)
        return
    terminal.write_sep(
        "=",
        f"required GUI surface collapsed ({verdict})",
        red=enforced,
        yellow=not enforced,
    )
    for line in lines:
        terminal.write_line(line)


def _user_name() -> str:
    try:
        return getpass.getuser()
    except Exception:  # pragma: no cover - platform user lookup failure
        return "unknown"


def _temp_root_problem(root: Path) -> str | None:
    """Why ``root`` cannot serve as pytest's temporary root, or None if it can.

    Mirrors what ``_pytest.tmpdir.TempPathFactory.getbasetemp`` needs: create
    the directory if absent, enumerate it to pick a free run number, and write
    inside it. A fence that denies any of those turns *every* ``tmp_path`` test
    into an error, which is worth detecting before the run rather than after
    it. The reason names which of the three failed, and the probe file is
    removed again immediately.
    """
    probe = root / f".webfoot-writable-{os.getpid()}"
    try:
        root.mkdir(mode=0o700, exist_ok=True)
    except OSError as exc:
        return f"{root.name} cannot be created here ({_os_error_detail(exc)})"
    try:
        with os.scandir(root):
            pass
    except OSError as exc:
        return f"{root.name} cannot be read here ({_os_error_detail(exc)})"
    try:
        probe.write_bytes(b"")
        probe.unlink()
    except OSError as exc:
        return f"{root.name} cannot be written here ({_os_error_detail(exc)})"
    return None


def _os_error_detail(exc: OSError) -> str:
    return exc.strerror or type(exc).__name__


def _rom_status() -> str:
    """A one-line statement of which ROM, if any, the ROM gate will use."""
    for variable in _ROM_ENVIRONMENT_VARIABLES:
        configured = os.environ.get(variable)
        if configured and Path(configured).is_file():
            return f"rom gate: {variable}={configured}"
    if _ROM_DEFAULT.is_file():
        return f"rom gate: {_ROM_DEFAULT} ({_CANONICAL_ROM_SHA256[:12]}...)"
    return (
        "rom gate: no canonical image found, `-m rom` will skip; set "
        + " or ".join(_ROM_ENVIRONMENT_VARIABLES)
        + f", or place {_ROM_DEFAULT}"
    )
