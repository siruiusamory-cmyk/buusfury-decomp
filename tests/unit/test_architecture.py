"""The repository purity gate, and the boundaries of each of its rules.

A rule that cannot be shown to fire is not a check, and a rule that fires on
everything is noise. Each rule below therefore gets a positive control (the
shape it exists to catch) and a negative control (a near-miss it must accept).
The rules are exercised as functions over a synthetic file list, so a control
proves the rule itself rather than the current tree.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

from tools.quality import architecture as arch

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


# --- roots -------------------------------------------------------------------


def test_a_file_outside_every_declared_root_is_a_violation():
    findings = arch._rule_top_level_roots(["whatever/file.py"])

    assert [item["path"] for item in findings] == ["whatever/file.py"]


def test_files_inside_a_declared_root_are_accepted():
    files = ["tools/webfoot/cli.py", "docs/DEVELOPMENT.md", "README.md"]

    assert arch._rule_top_level_roots(files) == []


# --- the shipping package ----------------------------------------------------


def test_a_non_python_file_in_the_shipping_package_is_a_violation():
    findings = arch._rule_python_package_source(["tools/webfoot/notes.md"])

    assert [item["rule"] for item in findings] == ["shipping-language"]


def test_packaged_data_and_modules_in_the_shipping_package_are_accepted():
    files = [
        "tools/webfoot/cli.py",
        "tools/webfoot/data/roms.yaml",
        "tools/webfoot/data/__init__.py",
    ]

    assert arch._rule_python_package_source(files) == []


def test_a_test_module_inside_the_shipping_package_is_a_violation():
    findings = arch._rule_no_tests_in_production(["tools/webfoot/test_rom.py"])

    assert [item["rule"] for item in findings] == ["no-tests-in-production"]


def test_a_module_named_like_a_test_elsewhere_is_accepted():
    files = ["tools/webfoot/rom.py", "tools/runtime/rom009_probe.py"]

    assert arch._rule_no_tests_in_production(files) == []


def test_a_research_probe_inside_the_shipping_package_is_a_violation():
    findings = arch._rule_no_probes_in_production(
        ["tools/webfoot/p004_capture.py", "tools/webfoot/atlas_probe.py"]
    )

    assert len(findings) == 2
    assert {item["rule"] for item in findings} == {"no-probes-in-production"}


def test_a_shipping_module_with_a_substantive_name_is_accepted():
    files = ["tools/webfoot/map_transitions.py", "tools/webfoot/build.py"]

    assert arch._rule_no_probes_in_production(files) == []


# --- tracked content ---------------------------------------------------------


def test_a_proprietary_suffix_is_a_violation_but_a_normal_file_is_not():
    assert arch._rule_no_proprietary_artifacts(["roms/game.gba"])
    assert arch._rule_no_proprietary_artifacts(["docs/project-format.md"]) == []


def test_an_upstream_checkout_under_extern_is_a_violation():
    findings = arch._rule_no_proprietary_artifacts(["extern/tool/README.md"])

    assert [item["rule"] for item in findings] == ["no-upstream-checkout"]


def test_local_state_is_a_violation_but_a_policy_document_is_not():
    assert arch._rule_no_local_state_tracked(["handoffs/notes.md"])
    assert arch._rule_no_local_state_tracked(["docs/DEVELOPMENT.md"]) == []


def test_a_tracked_file_the_ignore_rules_match_is_reported(monkeypatch):
    """The generated-output rule is the one rule that asks git, so it is
    controlled by giving it git's answer rather than by committing a fixture."""
    monkeypatch.setattr(arch, "_git", lambda *arguments: "build/generated.py\0")

    findings = arch._rule_nothing_generated_is_tracked([])

    assert [item["rule"] for item in findings] == ["nothing-generated-tracked"]
    assert findings[0]["path"] == "build/generated.py"


def test_a_tree_with_nothing_ignored_tracked_is_accepted(monkeypatch):
    monkeypatch.setattr(arch, "_git", lambda *arguments: "")

    assert arch._rule_nothing_generated_is_tracked([]) == []


def test_site_source_and_sdk_source_may_not_cross():
    assert arch._rule_site_and_sdk_are_separate(["src/tool.py"])
    assert arch._rule_site_and_sdk_are_separate(["tools/webfoot/theme.py"]) == []
    assert arch._rule_site_and_sdk_are_separate(["src/data/project.ts"]) == []


def test_a_test_only_import_in_shipping_source_is_a_violation(tmp_path, monkeypatch):
    package = tmp_path / "tools" / "webfoot"
    package.mkdir(parents=True)
    (package / "helper.py").write_text("import pytest\n", encoding="utf-8")
    monkeypatch.setattr(arch, "REPOSITORY_ROOT", tmp_path)

    findings = arch._rule_no_test_imports_in_production(["tools/webfoot/helper.py"])

    assert [item["rule"] for item in findings] == ["no-test-imports-in-production"]


def test_an_ordinary_import_in_shipping_source_is_accepted(tmp_path, monkeypatch):
    package = tmp_path / "tools" / "webfoot"
    package.mkdir(parents=True)
    (package / "helper.py").write_text("import yaml\n", encoding="utf-8")
    monkeypatch.setattr(arch, "REPOSITORY_ROOT", tmp_path)

    assert arch._rule_no_test_imports_in_production(["tools/webfoot/helper.py"]) == []


# --- the real tree -----------------------------------------------------------


def test_the_repository_passes_its_own_purity_check():
    report = arch.check()

    assert report["files"] > 500, "the rule set did not see the whole tree"
    assert report["violations"] == [], json.dumps(report["violations"], indent=2)


def test_observations_never_fail_the_run(tmp_path):
    """A size measurement is a reading list; it must not affect the verdict."""
    report = arch.check()

    assert isinstance(report["observations"], list)
    assert arch.main(["--no-fail", "--json", str(tmp_path / "purity.json")]) == 0


def test_the_report_is_deterministic(tmp_path):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    arch.main(["--no-fail", "--json", str(first)])
    arch.main(["--no-fail", "--json", str(second)])

    assert first.read_bytes() == second.read_bytes()


def test_the_removed_engine_prototype_stays_out_of_the_product_repository():
    """The repository is not a standalone remake, and must not carry one."""
    tracked = subprocess.run(
        ["git", "ls-files", "--", "remake/**", "remake"],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert tracked.stdout == ""
    assert not (REPOSITORY_ROOT / "remake").exists()
    readme = (REPOSITORY_ROOT / "README.md").read_text(encoding="utf-8")
    assert "not a standalone remake" in readme
