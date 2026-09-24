"""CQA-12: the Workbench Build tab inherits the default provenance publication.

The allocation-critical slice of CQA-12 is a *default*, and a default is only
worth having if every normal authoring surface gets it without asking. The
Workbench Build tab is the primary authoring surface, and it used to supply no
manifest path at all - so its derivatives carried provenance only in memory.

This pins the mechanism rather than the wording: the panel must call
`build_project` with NO `manifest_path` argument, which is what makes it inherit
whatever the SDK default is. A test that asserted the panel passed
`MANIFEST_BESIDE_OUTPUT` explicitly would pass while the panel was still coupled
to one spelling of the default.

build_panel imports PySide6 at module scope and the SDK CI job installs only the
base package, so this skips before importing it - the portable half of this
slice lives in `tests/unit/test_build_manifest_default.py`.
"""

from pathlib import Path
from types import SimpleNamespace

import pytest

pytest.importorskip("PySide6")

from tools.webfoot.workbench import build_panel as bp  # noqa: E402
from tools.webfoot.workbench.build_panel import BuildPanelTab, output_file_for  # noqa: E402
from tools.webfoot.workbench.session import Session  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402


@pytest.fixture(scope="module")
def _app():
    return QApplication.instance() or QApplication([])


def _make_panel(tmp_path, _app):
    rom = tmp_path / "src" / "buus_fury.gba"
    rom.parent.mkdir()
    rom.write_bytes(b"\x00")
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    session = Session(
        rom_path=rom,
        profile=SimpleNamespace(id="buus_fury_usa_rev0"),
        project_dir=tmp_path / "proj",
        output_dir=out_dir,
    )
    session.record_validation(True)
    return BuildPanelTab(session, catalog=None), session, out_dir


def test_the_build_tab_lets_the_sdk_default_decide_provenance(tmp_path, monkeypatch, _app):
    panel, session, out_dir = _make_panel(tmp_path, _app)
    seen = {}

    def fake_build(project_dir, rom_path, out, catalog, **kwargs):
        seen["kwargs"] = kwargs
        seen["out"] = Path(out)
        return SimpleNamespace(output_path=out, manifest_path=None)

    monkeypatch.setattr(bp.build_sdk, "build_project", fake_build)

    panel._run_build(output_file_for(out_dir, session.profile.id))

    assert "manifest_path" not in seen["kwargs"], (
        "the Build tab must not name a manifest path; it inherits the SDK default")
    assert session.last_build is not None
