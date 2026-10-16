"""AUTHORED-WORK-SAFETY-001 N-03: extraction never overwrites an occupied destination.

`write_project` keeps its deliberate re-save contract: a writer called by a
caller that wants convergence converges. The boundary that may not converge is
the extractor. Both the CLI and the Workbench reach `extract_project`, and it
refuses a destination that already holds anything, before the image is opened.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from tests.helpers import make_synthetic_rom, write_catalog
from tools.webfoot.build import BuildError, extract_project
from tools.webfoot.cli import main
from tools.webfoot.rom import RomReadError


def _tree(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*")
        if path.is_file()
    }


def _authored_project(root: Path) -> Path:
    """The files an authored project holds: identity, records, maps, text, art."""
    for relative in (
        "project.toml",
        "enemies/enemies.toml",
        "characters/characters.toml",
        "text/strings.toml",
        "maps/maps.toml",
        "maps/transitions.toml",
        "graphics/assets/graphic_0000.png",
    ):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(f"authored {relative}\n".encode("utf-8"))
    return root


def test_extract_refuses_an_occupied_directory(tmp_path: Path):
    destination = _authored_project(tmp_path / "project")

    # The guard runs before the image is opened, which is why no catalog is
    # needed and the ROM path may not even exist.
    with pytest.raises(BuildError, match="is not empty"):
        extract_project(tmp_path / "absent.gba", destination, None)


def test_a_refusal_leaves_every_authored_byte_and_the_image_alone(tmp_path: Path):
    destination = _authored_project(tmp_path / "project")
    before = _tree(destination)
    image = tmp_path / "canonical.gba"
    image.write_bytes(make_synthetic_rom())
    image_before = hashlib.sha256(image.read_bytes()).hexdigest()

    with pytest.raises(BuildError):
        extract_project(image, destination, None)

    assert _tree(destination) == before
    assert hashlib.sha256(image.read_bytes()).hexdigest() == image_before


def test_an_empty_destination_is_not_refused(tmp_path: Path):
    """The directory picker only returns directories that already exist, so an
    existing empty one is the Workbench's normal path and must never refuse."""
    destination = tmp_path / "empty"
    destination.mkdir()

    with pytest.raises(RomReadError):
        extract_project(tmp_path / "absent.gba", destination, None)


def test_extract_refuses_unrelated_content(tmp_path: Path):
    destination = tmp_path / "notes"
    destination.mkdir()
    (destination / "notes.txt").write_bytes(b"not a project\n")

    with pytest.raises(BuildError, match="is not empty"):
        extract_project(tmp_path / "absent.gba", destination, None)

    assert (destination / "notes.txt").read_bytes() == b"not a project\n"


def test_extract_refuses_a_destination_that_is_a_file(tmp_path: Path):
    destination = tmp_path / "already-a-file"
    destination.write_bytes(b"z")

    with pytest.raises(BuildError, match="is not empty"):
        extract_project(tmp_path / "absent.gba", destination, None)

    assert destination.read_bytes() == b"z"


def test_cli_extract_refuses_a_non_empty_destination(tmp_path: Path, capsys):
    destination = _authored_project(tmp_path / "project")
    config = tmp_path / "roms.yaml"
    write_catalog(config, [])

    exit_code = main([
        "--profiles", str(config), "extract",
        str(tmp_path / "absent.gba"), str(destination),
    ])
    error = capsys.readouterr().err

    assert exit_code == 2
    assert "is not empty" in error


def test_workbench_extract_reports_the_refusal_and_adopts_nothing(
    tmp_path: Path, monkeypatch
):
    pytest.importorskip("PySide6")
    from types import SimpleNamespace

    from PySide6.QtWidgets import QApplication, QMessageBox

    from tools.webfoot.workbench import build_panel as bp
    from tools.webfoot.workbench.build_panel import BuildPanelTab
    from tools.webfoot.workbench.session import Session

    QApplication.instance() or QApplication([])
    destination = _authored_project(tmp_path / "project")
    before = _tree(destination)
    image = tmp_path / "src.gba"
    image.write_bytes(make_synthetic_rom())
    session = Session(
        rom_path=image,
        profile=SimpleNamespace(id="synthetic_exact"),
        project_dir=None,
    )
    panel = BuildPanelTab(session, catalog=None)
    reported: list[str] = []
    monkeypatch.setattr(
        bp.QFileDialog, "getExistingDirectory",
        staticmethod(lambda *args, **kwargs: str(destination)),
    )
    monkeypatch.setattr(
        QMessageBox, "critical",
        staticmethod(lambda parent, title, text: reported.append(text)),
    )

    panel.extract_project_dialog()

    assert reported and "is not empty" in reported[0]
    assert session.project_dir is None
    assert _tree(destination) == before
