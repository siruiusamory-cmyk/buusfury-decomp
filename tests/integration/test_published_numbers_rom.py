"""The published map figures are what the canonical image measures.

The registry's 452 / 440 / 12 map triple and its 1,516 of 1,808 layer-slot pair
are recomputed here from the canonical image through the same production reader
the Maps editor's Layout mode drives, and then re-checked against every artifact
that quotes them. The ROM-free half holds the artifacts to the registry; this
half holds the registry to the image, which is the only thing that can catch a
rule change that updated the registry and the census together but not the code.

The module reads nothing but the image and re-hashes it at the end. It skips
cleanly when the private image is not configured, so CI reports it as a skip
rather than a pass.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from tests import published_numbers as published
from tools.webfoot.map_layout_edit import MapLayoutEditor

#: The accepted canonical Buu's Fury USA rev0 image.
CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"


def _rom_path() -> Path:
    return Path(
        os.environ.get(
            "LOGX_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba"
        )
    )


@pytest.fixture(scope="module")
def image() -> bytes:
    path = _rom_path()
    if not path.is_file():
        pytest.skip("canonical Buu ROM not configured locally")
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == CANONICAL_SHA256
    return data


@pytest.fixture(scope="module")
def measured(image: bytes) -> dict[str, int]:
    """One walk of the canonical image, through the production reader."""
    editor = MapLayoutEditor(image)
    maps = editor.map_entry_count
    editable = 0
    slots = 0
    dominant = 0
    for index in range(maps):
        target = editor.target(index)
        editable += 1 if target.editable else 0
        slots += len(target.slots)
        dominant += sum(1 for slot in target.slots if slot.classification == "dominant")
    return {
        "maps": maps,
        "editable": editable,
        "read_only": maps - editable,
        "layer_slots": slots,
        "dominant_slots": dominant,
    }


def test_the_registry_figures_are_what_the_image_measures(
    measured: dict[str, int],
) -> None:
    assert measured == published.registry_figures(), (
        "the registry's published figures are not what the canonical image "
        "measures. The registry is the authority and the site and the census "
        "quote it, so the measuring rule and the publications have to move "
        "together"
    )


def test_every_published_figure_is_the_measured_one(measured: dict[str, int]) -> None:
    missing = published.missing_quotes(measured)
    assert not missing, (
        "a published figure is not the one the canonical image measures:\n  "
        + "\n  ".join(missing)
    )


def test_the_canonical_image_is_unchanged_by_the_walk(image: bytes) -> None:
    path = _rom_path()
    assert path.is_file(), "the image disappeared during the run"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == CANONICAL_SHA256, (
        "the canonical image changed while it was being measured")
