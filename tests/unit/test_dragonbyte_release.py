"""DRAGONBYTE-Z-SHIP-V1-001 - the release surface: the frozen build, its identity
and the patch a user is handed.

Three claims, each proved where it can actually fail:

* **the frozen build is *this* product.** The spec names the product's own entry
  shim and not the beta workbench's, and this repository has already paid for the
  distinction: the earlier shim froze the beta.
* **the visible version is the recorded identity, twice.** The ``--version``
  string, the window title and the Windows version resource are four spellings of
  one identity, and a drift between them is how a release ends up named one
  version and reporting another.
* **a packaged build opens a project.** The interpreter case runs here over a real
  project directory. The frozen case cannot run in CI at all - PyInstaller does not
  cross-compile to win64 - so the executable itself is driven by
  ``scripts/smoke-dragonbyte-z-packaged.ps1``, which asserts the same report fields
  this file asserts.
"""

from __future__ import annotations

import ast
import json
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path  # noqa: E402
import re  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402

import pytest  # noqa: E402

from tools.webfoot.release_identity import (  # noqa: E402
    PRODUCT_NAME,
    PRODUCT_VERSION,
    VERSION_TUPLE,
    release_identity,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SPEC = REPOSITORY_ROOT / "DragonByte Z.spec.in"
VERSION_RESOURCE = REPOSITORY_ROOT / "DragonByte Z.version.txt"
PRODUCT_PACKAGE = REPOSITORY_ROOT / "tools" / "dragonbyte"
BETA_PACKAGE = "tools/webfoot/workbench"

#: The project a smoke run opens: the smallest document the project reader accepts,
#: which is the product's own reader and not a fixture of this test's invention.
PROJECT_TOML = """\
[project]
format_version = 1
name = "smoke"

[base]
profile_id = "buus_fury_usa_rev0_01c1707f"
game = "Dragon Ball Z: Buu's Fury"
sha256 = "{sha256}"
size = {size}
"""


def _version_tuple_literal() -> str:
    """The four-field tuple as PyInstaller's resource syntax spells it."""
    return "(" + ", ".join(str(field) for field in VERSION_TUPLE) + ")"


def _version_quad() -> str:
    return ".".join(str(field) for field in VERSION_TUPLE)


def _run_module(arguments: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "tools.dragonbyte", *arguments],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )


def _write_project(directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "project.toml").write_text(
        PROJECT_TOML.format(sha256="0" * 64, size=8388608),
        encoding="utf-8",
        newline="\n",
    )
    return directory


# --- the packaging definition ------------------------------------------------


def test_the_spec_freezes_the_product_and_not_the_beta():
    """The entry shim is the product's, and it is the shim the spec names.

    The beta's own shim still exists and still works; what would be the defect is
    a shipped executable that runs it, because the beta is the engineering surface
    and not the product.
    """
    spec = SPEC.read_text(encoding="utf-8")

    assert "'tools/dragonbyte/_pyinstaller_entry.py'" in spec
    # Read as PyInstaller reads it: the argument list of Analysis. The beta's own
    # shim is what the product's build must not freeze, and the spec names it in
    # prose on purpose, so the check is on the frozen script list only.
    frozen = re.search(r"Analysis\(\s*\[([^\]]*)\]", spec)
    assert frozen is not None
    assert "'tools/dragonbyte/_pyinstaller_entry.py'" in frozen.group(1)
    assert "workbench" not in frozen.group(1)

    shim = (PRODUCT_PACKAGE / "_pyinstaller_entry.py").read_text(encoding="utf-8")
    assert "from tools.dragonbyte.app import main" in shim
    # The rule the beta import would break, asked of the compiler's own resolver
    # rather than of the file's prose.
    from tools.quality import architecture

    imported = architecture._imported_modules(
        "tools/dragonbyte/_pyinstaller_entry.py", ast.parse(shim)
    )
    assert [name for name, _line in imported if "workbench" in name] == []


def test_the_console_script_runs_the_product_and_not_the_beta():
    """The installed command must reach the product.

    ``dragonbyte-z`` is what a user types after an install, and it named the beta
    workbench. The spec template and this entry point are two ways the same
    mistake can be made, so both are checked.
    """
    import tomllib

    document = tomllib.loads(
        (REPOSITORY_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )

    assert document["project"]["scripts"]["dragonbyte-z"] == "tools.dragonbyte.app:main"


def test_the_spec_carries_the_identity_the_icon_and_the_profile_catalog():
    spec = SPEC.read_text(encoding="utf-8")

    assert f"version='{VERSION_RESOURCE.name}'" in spec
    assert "icon='scripts/randomizer.ico'" in spec
    assert "('tools/webfoot/data/roms.yaml', 'tools/webfoot/data')" in spec
    # The frozen build is a directory: an editor's artefact is not the single
    # executable a randomizer's release is, and the shape is declared, not implied.
    assert "exclude_binaries=True" in spec
    assert "COLLECT(" in spec


def test_the_version_resource_matches_the_identity_authority():
    """The resource is a second spelling of one identity, and this fails when the
    two disagree - which is the whole reason ``release_identity.py`` is the only
    place a version literal is allowed to live."""
    text = VERSION_RESOURCE.read_text(encoding="utf-8")
    fields = dict(
        re.findall(r'StringStruct\("(\w+)",\s*"((?:[^"\\]|\\.)*)"\)', text)
    )
    fixed = dict(re.findall(r"\b(filevers|prodvers)=\(([^)]*)\)", text))

    assert fields["ProductName"] == PRODUCT_NAME
    assert fields["InternalName"] == PRODUCT_NAME
    assert fields["OriginalFilename"] == f"{PRODUCT_NAME}.exe"
    assert fields["FileVersion"] == _version_quad()
    assert fields["ProductVersion"] == _version_quad()
    assert set(fixed) == {"filevers", "prodvers"}
    for value in fixed.values():
        assert value.replace(" ", "") == _version_tuple_literal().strip("()").replace(
            " ", ""
        )


def test_no_file_in_the_product_package_restates_the_version():
    for path in sorted(PRODUCT_PACKAGE.rglob("*.py")):
        assert PRODUCT_VERSION not in path.read_text(encoding="utf-8"), path


def test_the_application_runs_from_the_shim_the_spec_freezes(tmp_path):
    """The shim is exercised the way PyInstaller supplies it: from the repository
    root, with the packages importable. Run as a bare script it would have only its
    own directory on ``sys.path``, which is not how the frozen build runs it."""
    environment = dict(os.environ, PYTHONPATH=str(REPOSITORY_ROOT))
    result = subprocess.run(
        [sys.executable, str(PRODUCT_PACKAGE / "_pyinstaller_entry.py"), "--version"],
        cwd=REPOSITORY_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == release_identity().display


# --- the visible version, headless -------------------------------------------


def test_the_version_flag_prints_the_recorded_identity():
    result = _run_module(["--version"])

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == f"{PRODUCT_NAME} {PRODUCT_VERSION}"


def test_the_smoke_run_opens_a_project_and_reports_the_identity(tmp_path):
    """The interpreter half of "a packaged build opens a project".

    The packaged half is the same report, read by
    ``scripts/smoke-dragonbyte-z-packaged.ps1`` from the frozen executable's own
    output. Both assert ``project.opened`` and the identity, so a build that
    stopped being able to open a project cannot pass by answering the version
    question alone.
    """
    project = _write_project(tmp_path / "project")
    report = tmp_path / "smoke.json"

    result = _run_module(
        ["--smoke", str(project), "--smoke-report", str(report)]
    )

    assert result.returncode == 0, result.stderr
    document = json.loads(report.read_text(encoding="utf-8"))
    assert document["schema_version"] == 1
    assert document["error"] is None
    assert document["project"]["opened"] is True
    assert document["project"]["name"] == "smoke"
    assert document["identity"]["product"] == {
        "name": PRODUCT_NAME,
        "version": PRODUCT_VERSION,
        "version_tuple": list(VERSION_TUPLE),
    }
    # No image was named, so none was opened: the report says what happened rather
    # than what was hoped for.
    assert document["rom"] == {"path": None, "opened": False}


def test_a_smoke_run_that_cannot_open_its_project_says_so(tmp_path):
    """A refusal is reported, not swallowed, and the exit code is not 0."""
    report = tmp_path / "smoke.json"

    result = _run_module(
        ["--smoke", str(tmp_path / "absent"), "--smoke-report", str(report)]
    )

    assert result.returncode == 1
    document = json.loads(report.read_text(encoding="utf-8"))
    assert document["project"]["opened"] is False
    assert "does not exist" in document["error"]


def test_a_smoke_run_without_a_report_path_is_refused_before_any_startup():
    result = _run_module(["--smoke", "some-project"])

    assert result.returncode == 2
    assert "--smoke-report" in result.stderr


def test_the_window_title_is_the_same_string_the_flag_prints():
    """One identity, two surfaces. The title case needs a window, so it is skipped
    rather than failed when PySide6 is absent; the flag case above is not."""
    pytest.importorskip("PySide6.QtWidgets")
    from PySide6.QtWidgets import QApplication

    from tools.dragonbyte.shell import Shell
    from tools.dragonbyte.session import Session

    app = QApplication.instance() or QApplication([])
    shell = Shell(Session(), Path(os.environ.get("TEMP", ".")) / "dbz-smoke-config")

    assert shell.windowTitle() == _run_module(["--version"]).stdout.strip()
    shell.close()
