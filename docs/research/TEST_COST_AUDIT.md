# Test cost audit, measured from CI

What the portable suite costs and where the cost sits, measured from the CI
artifacts of two runs rather than from a local suite run: the last green master
`test-sdk` job and the red head `test-sdk` job. Every table names its pipeline
and job id.

## The two runs

| run | pipeline | iid | commit | job | result | wall clock |
|---|---|---|---|---|---|---|
| last green master | [2939754480](https://gitlab.com/siruiusamory/log1-remake/-/pipelines/2939754480) | 1015 | `d634213d` | `test-sdk` 17120802626 | success | 206.18 s |
| red head master | [2957986023](https://gitlab.com/siruiusamory/log1-remake/-/pipelines/2957986023) | 1167 | `c9a09e33` | `test-sdk` 17252635042 | job timeout at 30m0s | 1800 s |

The green job ran on the shared Linux runner (`k8s.saas-linux-small-amd64`,
`python:3.12-slim` container, `pip` as root). The red job ran on the owner's
self-hosted Windows runner. They are not the same environment; the green run is
used here only for the shape and cost of the collected suite, and the red run for
what the Windows job actually did.

### The JUnit artifact is not downloadable

`GET /projects/86252118/jobs/<id>/artifacts` returned HTTP 404 for **both**
jobs, and so did the single-file path
`/jobs/17120802626/artifacts/junit.xml.gz`:

```
glab api projects/siruiusamory%2Flog1-remake/jobs/17120802626/artifacts
glab: 404 Not Found (HTTP 404)
```

The job API still lists `junit.xml.gz` (112,261 bytes) in the job's `artifacts`,
so this is an artifact-retrieval fact, not evidence that the report was never
uploaded. The fallback is two other CI sources, quoted where used:

- the pipeline test report, `GET /projects/86252118/pipelines/2939754480/test_report`,
  which is GitLab's own parse of the uploaded JUnit report: 5,487 cases,
  `total_time` 150.679 s. Every per-test and per-module table below comes from it;
- the red job's trace, `GET /projects/86252118/jobs/17252635042/trace`.

The green job's own pytest summary line, from that trace:

```
5182 passed, 305 skipped in 150.88s (0:02:30)
```

## Cost by module, top 25

Pipeline 2939754480, job 17120802626, from the report's `classname` and
`execution_time`. `execution_time` is the case's own call time; a module's
per-module fixture setup is not in it, which is why a module's slot in a
`--dist loadfile` run is at least this figure.

| seconds | tests | module |
|---|---|---|
| 38.516 | 27 | `tests.unit.test_public_surface` |
| 28.256 | 76 | `tests.unit.test_readability` |
| 18.669 | 38 | `tests.unit.test_atlas_build` |
| 12.461 | 22 | `tests.unit.test_ui_graphics_probe` |
| 12.227 | 26 | `tests.unit.test_logx_synthesis_audit` |
| 10.069 | 27 | `tests.unit.test_architecture` |
| 9.679 | 81 | `tests.unit.test_workbench_resize_and_layers` |
| 8.425 | 38 | `tests.unit.test_decoded_text_index` |
| 8.198 | 34 | `tests.unit.test_dragonbyte_foundation` |
| 7.440 | 15 | `tests.unit.test_mgba_launch_coverage` |
| 6.765 | 85 | `tests.unit.test_dragonbyte_romsurface` |
| 5.759 | 10 | `tests.unit.test_friend_v3_playtest_boost` |
| 4.948 | 10 | `tests.unit.test_frozen_containers` |
| 4.779 | 9 | `tests.unit.test_graphics_override_sdk` |
| 4.165 | 46 | `tests.unit.test_workbench_chunk_authoring` |
| 4.064 | 53 | `tests.unit.test_workbench_map_browser` |
| 3.688 | 50 | `tests.unit.test_warp_randomizer_gui` |
| 3.574 | 12 | `tests.unit.test_dragonbyte_release` |
| 3.499 | 10 | `tests.unit.test_write_invariants_property` |
| 2.860 | 15 | `tests.unit.test_randomizer_release` |
| 2.727 | 10 | `tests.unit.test_project_safety` |
| 2.530 | 9 | `tests.unit.test_workbench_run_config_rom_picker` |
| 2.512 | 39 | `tests.unit.test_workbench_state_and_errors` |
| 2.208 | 15 | `tests.unit.test_workbench_graphics_undo` |
| 2.173 | 81 | `tests.unit.test_workbench_warp_creation` |

252 modules contributed cases. The largest by count are
`test_resource_library_curation` (101 cases, 1.593 s), `test_script_vm` (93,
0.580 s) and `test_dragonbyte_romsurface` (85, 6.765 s): many cheap cases, not
slow ones.

## The 25 slowest tests

Pipeline 2939754480, job 17120802626.

| seconds | test |
|---|---|
| 25.974 | `tests.unit.test_public_surface::test_the_report_is_deterministic` |
| 12.342 | `tests.unit.test_public_surface::test_the_public_surface_is_clean` |
| 11.007 | `tests.unit.test_readability::test_two_runs_write_byte_identical_json` |
| 7.416 | `tests.unit.test_mgba_launch_coverage::test_the_current_tree_has_no_unregistered_launch_site` |
| 5.961 | `tests.unit.test_readability::test_the_summary_says_advisories_never_change_the_exit_code` |
| 5.585 | `tests.unit.test_readability::test_the_json_document_has_a_stable_schema` |
| 5.567 | `tests.unit.test_readability::test_the_enemy_behaviour_sense_is_covered_by_a_written_exception` |
| 4.761 | `tests.unit.test_graphics_override_sdk::test_pack_gba_colour_is_the_exact_inverse_of_the_word_decode` |
| 3.462 | `tests.unit.test_ui_graphics_probe::test_report_records_the_pre_filter_corpus_hits` |
| 3.397 | `tests.unit.test_architecture::test_the_report_is_deterministic` |
| 3.368 | `tests.unit.test_dragonbyte_foundation::test_the_real_tree_passes_the_gate_and_the_package_never_imports_the_beta` |
| 3.153 | `tests.unit.test_warp_randomizer_gui::test_the_application_is_configured_with_the_shared_dragonbyte_z_theme` |
| 3.145 | `tests.unit.test_architecture::test_observations_never_fail_the_run` |
| 3.039 | `tests.unit.test_logx_synthesis_audit::test_the_audit_is_deterministic` |
| 3.009 | `tests.unit.test_dragonbyte_foundation::test_the_application_starts_and_stays_alive_offscreen` |
| 2.793 | `tests.unit.test_write_invariants_property::test_normalized_changes_do_not_depend_on_input_order` |
| 2.703 | `tests.unit.test_dragonbyte_romsurface::test_a_byte_edit_is_one_undo_entry_and_one_overlay_offset` |
| 2.626 | `tests.unit.test_project_safety::test_built_wheel_uses_packaged_profile_catalog` |
| 2.479 | `tests.unit.test_frozen_containers::test_no_frozen_dataclass_in_tools_hands_out_a_mutable_container` |
| 2.458 | `tests.unit.test_frozen_containers::test_every_allowlisted_field_is_still_a_hit` |
| 1.937 | `tests.unit.test_ui_graphics_probe::test_report_states_its_own_scan_gap` |
| 1.934 | `tests.unit.test_ui_graphics_probe::test_shared_resources_reports_a_container_named_twice` |
| 1.763 | `tests.unit.test_architecture::test_the_real_tree_respects_the_import_direction` |
| 1.759 | `tests.unit.test_thumb_caller_census::test_validity_of_the_second_halfword_is_decided_as_the_architecture_does` |
| 1.729 | `tests.unit.test_ui_graphics_probe::test_enumeration_removes_containers_the_known_corpus_reaches` |

## Job wall clock, and the loadfile floor

Green job 17120802626: 206.18 s end to end (job API `duration`, started
18:12:45.946Z, finished 18:16:12.126Z). Inside it, from the trace: `pip install`
of `.[dev,workbench,research]` 18:13:09.7 to 18:13:26.2, the suite 150.88 s to
18:15:57.7, then the four quality-gate steps.

Red job 17252635042: 1800 s, which is the job's 30-minute cap, not the suite's
length. The suite was at 98% five minutes in and then wedged, and the trace
records why in this order:

```
2026-10-17T06:17:44.617784Z 01O ........................................................................ [ 98%]
2026-10-17T06:17:46.361616Z 01O ......sss............ss.....................................[gw3] node down: Not properly terminated
2026-10-17T06:30:18.792884Z 01E Windows fatal exception: access violation
2026-10-17T06:30:18.794400Z 01E   File "...\tests\conftest.py", line 845 in pytest_unconfigure
2026-10-17T06:35:28.571285Z 01O FEntering debug mode. Use h or ? for help.
2026-10-17T06:42:33.003355Z 00O ERROR: Job failed: execution took longer than 30m0s seconds
```

So the red job is a worker crash plus a controller that never returned, not an
assertion failure: 5,182-odd cases had already executed. No test is failing in
that job; the process dies after `gw3` goes down.

**The loadfile floor module.** Under `--dist loadfile` the job cannot finish
before the slowest single module, so that module's own time floors the run. The
CI report cannot name it directly: it carries call-phase seconds, not a module's
slot, and the JUnit artifact that might have carried more is the one that 404s.
Measured from the report, the largest per-module call time is
`tests.unit.test_public_surface` at 38.5 s over 27 cases. In the Windows
environment the floor is `tests/unit/test_text_tool_shell.py`: 32 cases,
153.56 s in a single serial process, measured in this worktree
([LOCAL-VERIFIED], 2026-10-17, shared venv 3.12.10, `QT_QPA_PLATFORM=offscreen`),
against a whole `-n 4` suite the lead measured at 307-368 s. That local number
is the one measurement here that is not from CI, and it is labelled because the
CI artifacts do not carry the module slot that would replace it.

## Table-drive candidates

Method: every module-level `test_*` function in `tests/` was parsed with `ast`;
decorated functions were excluded, docstrings dropped, and every literal
constant normalised, so a group is a set of functions with the same statement
shape that differ only in their literals. Groups of four or more are listed.

| tests in the group | module | shape |
|---|---|---|
| 9 | `tests/unit/test_site_consistency.py` | copy the clean status document, mutate one field through a helper, assert one expected sentence appears in `structure_findings` |
| 5 | `tests/unit/test_readability.py` | a text literal plus a filename suffix, then `assert "<signal>" not in signals(...)`; four of the five are the same signal (`commented_out_code`), the fifth (`test_a_provisional_marker_retires_the_wording`) shares the shape but asserts a different signal and is not a case of the same rule |
| 4 | `tests/unit/test_map_chunk_authoring.py` | one `edits` tuple plus one expected `pytest.raises(match=...)` string |
| 4 | `tests/unit/test_dev_tools.py` | one citation document plus one expected orphan/report sentence |
| 4 | `tests/unit/test_raw_byte_document.py` | one TOML text plus one expected refusal |
| 4 | `tests/unit/test_token_splice_verifier.py` | one splice request plus one expected output |

`test_map_chunk_authoring.py` carries a fifth function of the same shape that is
already parametrised over `prior,entry`, so its literal-only group is the four
above.

## Restate-the-implementation candidates

Tests that replace a function or a private attribute of the module under test.
Found by resolving every `monkeypatch.setattr(<module alias>, "<name>", ...)` to
the module it names and keeping the calls whose name is private (`_name`) or is
defined by that module's own source. 85 patching calls land on the module under
test; 26 of them are on a private name, across 19 distinct seams:

| patched seam | test module |
|---|---|
| `tools.buufury_text.session.Session._output_keys` | `tests/unit/test_buufury_text.py` |
| `tools.buufury_text.theme._ICON_FILES` | `tests/unit/test_text_tool_theme.py` |
| `tools.quality.architecture._git` | `tests/unit/test_architecture.py` |
| `tools.runtime.evidence_bundle._git` | `tests/unit/test_runtime_evidence_bundle.py` |
| `tools.runtime.rom012_live_containment._registers` | `tests/unit/test_rom012_runtime.py` |
| `tools.save_catalogue.walk._index_one` | `tests/unit/test_save_catalogue.py` |
| `tools.webfoot.atlas_producers.scan._text_rows`, `._pointer_rows`, `._pointer_table_rows`, `._entropy_rows`, `._compression_rows`, `._code_shape_rows` | `tests/unit/test_atlas_producers.py` |
| `tools.webfoot.build._load_for_project` | `tests/unit/test_authored_placements.py` |
| `tools.webfoot.capability._packaged_catalog` | `tests/unit/test_placement_types.py` |
| `tools.webfoot.formats.webfoot_lz._emit_raw` | `tests/integration/test_webfoot_lz_strict_rom.py` |
| `tools.webfoot.formats.webfoot_lz._gamma` | `tests/unit/test_webfoot_lz.py` |
| `tools.webfoot.release_identity._git` | `tests/unit/test_release_identity.py` |
| `tools.webfoot.scene._placement_types` | `tests/unit/test_workbench_scene.py` |
| `tools.webfoot.workbench.launcher._detect_mgba` | `tests/unit/test_workbench_launcher_settings.py` |

These are candidates, not findings: patching a private seam is sometimes the
only way to make a failure reachable (the two `_git` seams drive a subprocess
that is not installed in CI). Each one is a place to ask whether the public
surface already offers the same observation.

## Dead code: vulture over `tools/`

`vulture 2.16`, installed in a throwaway venv (`C:\temp\lean-test-001\vulture-venv`),
never added to the project's dependencies, run from this worktree as
`vulture --min-confidence 80 tools/` (exit 3: findings present). Findings as
printed, no edits made:

- `tools/qa/buu_sprite_palette.py:148: unused variable 'counts_hint' (100% confidence)`
- `tools/qa/cqa03_atlas_identity_probe.py:56: unused variable 'cat' (100% confidence)`
- `tools/research/apply_tulma_graphics.py:34: unused import 'ANIMATION_ARRAY_OFFSET' (90% confidence)`
- `tools/research/apply_tulma_graphics.py:34: unused import 'PORTRAIT_ARRAY_ADDRESS' (90% confidence)`
- `tools/research/apply_tulma_graphics.py:34: unused import 'REGISTRY_TABLE_ADDRESS' (90% confidence)`
- `tools/research/logx_gfxscan_probe.py:1756: unused variable 'reference_hits' (100% confidence)`
- `tools/webfoot/cli.py:77: unused import '_recover_handle' (90% confidence)`
- `tools/webfoot/cli.py:77: unused import '_unpack_handle' (90% confidence)`
