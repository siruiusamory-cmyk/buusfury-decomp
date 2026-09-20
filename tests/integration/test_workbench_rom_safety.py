"""WORKBENCH-001 T2B.3 - the Workbench build NEVER mutates the source ROM.

This proves the ticket's #1 safety invariant end to end: hashing the canonical
source ROM before and after a full extract -> validate -> build_project run and
asserting the source is byte-identical afterwards. It drives the SAME output-path
composition and Qt-free guard the GUI uses (`build_panel.output_file_for` +
`is_safe_output_path`), not a bespoke copy, so a regression in either the guard
or the path convention shows up here.

ROM-gated the way its siblings are: `open_rom` also needs the assembled atlas
artifact, so both fixtures are required and the test skips cleanly without them.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

# `tools.webfoot.workbench.build_panel` imports PySide6 at module scope, so
# without the workbench extra this module must skip the way its unit siblings
# do. A bare ImportError here aborts collection of the whole
# `tests/integration` directory, which hides every other integration test.
pytest.importorskip("PySide6")

from tools.webfoot import build as build_sdk
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.workbench.build_panel import (is_safe_output_path,
                                                 output_file_for)
from tools.webfoot.workbench.session import Session

LOCAL_ROM = Path("roms/Dragon Ball Z - Buu's Fury (U).gba")
CATALOG = "config/roms.yaml"
CANONICAL_SHA = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"

pytestmark = pytest.mark.skipif(
    not LOCAL_ROM.exists(),
    reason="canonical Buu's Fury image not present",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_workbench_build_never_mutates_source_rom(tmp_path):
    if _sha256(LOCAL_ROM) != CANONICAL_SHA:
        pytest.skip("ROM present but not the canonical Buu's Fury image")

    catalog = RomProfileCatalog.load(CATALOG)
    session = Session()
    session.output_dir = tmp_path
    try:
        session.open_rom(LOCAL_ROM, catalog)
    except build_sdk.BuildError:  # pragma: no cover - env guard
        raise
    except Exception as exc:  # SessionError when the atlas artifact is absent
        pytest.skip(f"workbench cannot open ROM headless: {exc}")

    # SC1: source hash BEFORE the build.
    before = _sha256(session.rom_path)

    project_dir = tmp_path / "project"
    build_sdk.extract_project(session.rom_path, project_dir, catalog, graphics=False)
    assert build_sdk.validate_project(project_dir, session.rom_path, catalog).passed

    # SC2: compose the output path and check it exactly as build_panel does.
    output_path = output_file_for(session.output_dir, session.profile.id)
    assert is_safe_output_path(output_path, session.rom_path)

    result = build_sdk.build_project(
        project_dir, session.rom_path, output_path, catalog)

    # SC1: source hash AFTER - the safety property.
    after = _sha256(session.rom_path)
    assert after == before, (
        f"source ROM was mutated by the build: {before} -> {after}"
    )

    # SC4: the build wrote a real, distinct output under tmp_path.
    assert result.output_path.exists()
    assert result.output_path.resolve() != session.rom_path.resolve()
