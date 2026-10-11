"""Shared setup for the seven DragonByte acceptance and page modules.

TEST-SPEED-002. A shell built over an open image decodes every destination's
surface in that destination's own constructor, and each of these seven modules
builds one shell per test. Measured with `--durations=30`, that decode is the
whole of the per-test setup: the `setup` phase carries almost all of these
modules' slowest entries and the `call` phase is a few seconds. Measured
directly, one shell over the canonical image costs about 30 s, of which the
actor-sprite corpus alone is 23 s. The decode is a pure function of the
already-identified image, so it is done once per module here and handed back
through the module-level loader seam these modules already replace for the
range index.

Nothing here weakens a test: a page still installs a real surface built from the
canonical image, still renders it and still states a real reason when a read
fails, and every test still builds its own session, project copy, shell and
page. The replacement is for one image: a module whose tests open a second one
must not reuse this.

This module also carries the four helpers these modules used to import from
`tests/unit/test_dragonbyte_state.py`, because a test module importing another
test module is what the support module exists to remove.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from tools.dragonbyte import datasurface as ds
from tools.dragonbyte import entitysurface as es
from tools.dragonbyte import graphicsurface as gs
from tools.dragonbyte import mapsurface as ms
from tools.dragonbyte import textsurface as ts
from tools.dragonbyte.session import Session
from tools.webfoot.catalog import RomProfileCatalog
from tools.webfoot.rom import identify_rom

#: The sibling primary checkout, derived from this file's own location rather
#: than written down. Its roms/ directory is where a canonical image lives.
SIBLING_CHECKOUT = Path(__file__).resolve().parents[2].parent / "log1-remake"

CANONICAL_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)


def _close(shell, session) -> None:
    """Close without reaching a modal question.

    A dirty journal makes `closeEvent` ask, and a modal QMessageBox cannot be
    answered offscreen, so a test that leaves edits pending would block forever
    instead of failing - including a test that fails BEFORE reaching its cleanup.
    Rebinding the journal is the reset that makes the window clean whatever the
    assertions already did, and it touches no state the tests assert on.
    """
    session.journal.bind(session.journal.authority or "")
    shell.close()


def wait_for_text_surface(shell, timeout_ms: int = 120_000) -> None:
    """Let the Scripts & Text read land, so every destination has answered.

    That read runs off the UI thread by design, so a test that needs every
    destination read before it asserts on the ROM surface spins the event loop,
    exactly as a user's window does. A destination still loading states that on
    the ROM surface, which would otherwise be measured as part of the test.
    """
    from PySide6.QtCore import QDeadlineTimer, QEventLoop

    page = shell._text_page
    deadline = QDeadlineTimer(timeout_ms)
    while page._surface_loading and not deadline.hasExpired():
        QEventLoop().processEvents()
    assert not page._surface_loading, "the text surface never finished loading"
    assert page._surface is not None, page._problem


def canonical_image(catalog: RomProfileCatalog) -> Path | None:
    """The canonical image in the sibling checkout, or None when it is absent.

    The same search the modules' own `canonical_rom` fixture makes, without the
    skip: a module whose tests do not all need the image must still run the ones
    that do not.
    """
    roms = SIBLING_CHECKOUT / "roms"
    for candidate in sorted(roms.glob("*.gba")) if roms.is_dir() else []:
        try:
            identification = identify_rom(candidate, catalog)
        except Exception:  # noqa: BLE001 - any unreadable file is simply not it
            continue
        if identification.hashes.sha256 == CANONICAL_SHA256:
            return candidate
    return None


@dataclass(frozen=True)
class DecodedSurfaces:
    """One image's five destination reads, decoded once for a module."""

    data: object
    maps: object
    entities: object
    graphics: object
    text: object


def decode_surfaces(canonical_rom, catalog) -> DecodedSurfaces:
    """Read all five destinations once, as a shell over this image would."""
    session = Session()
    session.open_rom(canonical_rom)
    identification = session.identification
    profile = session.profile
    image = session.base_image

    text = ts.load_text_surface(canonical_rom, catalog, identification, profile, image)
    # The text page's own worker warms both mode lists inside its one read.
    text.dialogue_rows()
    text.event_rows()

    return DecodedSurfaces(
        data=ds.load_data_surface(canonical_rom, catalog, identification, profile, image),
        maps=ms.load_map_surface(canonical_rom, catalog, identification, profile, image),
        entities=es.load_entity_surface(canonical_rom, catalog, identification, profile, image),
        graphics=gs.load_graphics_surface(identification, profile, image),
        text=text,
    )


def reuse_surfaces(monkeypatch, surfaces: DecodedSurfaces) -> None:
    """Answer each destination's own read with this module's one decode.

    A page asks its loader by module attribute, which is the same seam these
    modules already replace for the range index. The replacement answers every
    call with the one decode, so it is for one image only.
    """
    monkeypatch.setattr(ds, "load_data_surface", lambda *args, **kwargs: surfaces.data)
    monkeypatch.setattr(ms, "load_map_surface", lambda *args, **kwargs: surfaces.maps)
    monkeypatch.setattr(es, "load_entity_surface", lambda *args, **kwargs: surfaces.entities)
    monkeypatch.setattr(gs, "load_graphics_surface", lambda *args, **kwargs: surfaces.graphics)
    monkeypatch.setattr(ts, "load_text_surface", lambda *args, **kwargs: surfaces.text)


@pytest.fixture(scope="module")
def surfaces(catalog):
    """This module's one decode of the five destinations, or None without it.

    None when this machine has no canonical image, so a test that does not need
    the image neither decodes nor skips.
    """
    rom = canonical_image(catalog)
    return None if rom is None else decode_surfaces(rom, catalog)


@pytest.fixture(autouse=True)
def one_decode(surfaces, monkeypatch):
    """Let every shell this module builds install the module's one decode."""
    if surfaces is not None:
        reuse_surfaces(monkeypatch, surfaces)
