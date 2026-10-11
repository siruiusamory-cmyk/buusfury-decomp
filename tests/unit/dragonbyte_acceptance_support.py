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
must not reuse this, and the replacement loader refuses a call that names any
other image instead of answering it with the wrong surfaces.

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
    #: The image these five reads were decoded from. The replacement loaders
    #: check every call against it, so a read of a second image is refused
    #: instead of answered with this one's surfaces.
    image: bytes


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
        image=image,
    )


#: The module attribute each destination's page asks for its own read, the
#: DecodedSurfaces field its answer lives in, and the position the image holds
#: in that loader's arguments. A page calls its loader by module attribute,
#: which is the seam these modules already replace for the range index.
LOADER_SITES = (
    (ds, "load_data_surface", "data", 4),
    (ms, "load_map_surface", "maps", 4),
    (es, "load_entity_surface", "entities", 4),
    (gs, "load_graphics_surface", "graphics", 2),
    (ts, "load_text_surface", "text", 4),
)


def check_image(surfaces: DecodedSurfaces, called_with) -> None:
    """Refuse to answer a read of an image these surfaces were not decoded from.

    The five loaders have different arities, so the caller passes the image the
    call actually names: the graphics loader's 3rd argument, the other four
    loaders' 5th. A read of a second image would otherwise silently receive the
    first one's surfaces, which is the silent-wrong-answer case F3 of the
    TEST-SPEED-002 review flagged.
    """
    assert called_with == surfaces.image, (
        "the decode is for a different image than this read names, so answering "
        "it would report another image's surfaces; decode the named image "
        "instead of reusing this one"
    )


def replacement_loader(surfaces: DecodedSurfaces, position: str, image_argument: int):
    """The loader that stands in for one destination's own read.

    It checks the image that call actually names against the one the surfaces
    were decoded from, then answers with those surfaces, or refuses. The index
    of the image argument is per loader because their arities differ.
    """
    surface = getattr(surfaces, position)

    def loader(*args, **kwargs):
        called_with = args[image_argument] if len(args) > image_argument else None
        check_image(surfaces, called_with)
        return surface

    return loader


def reuse_surfaces(monkeypatch, surfaces: DecodedSurfaces) -> None:
    """Answer each destination's own read with this module's one decode.

    The replacement answers every call with the one decode, for the one image it
    was decoded from; a call that names any other image is refused rather than
    answered.
    """
    for module, attribute, position, image_argument in LOADER_SITES:
        monkeypatch.setattr(
            module,
            attribute,
            replacement_loader(surfaces, position, image_argument),
        )


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
