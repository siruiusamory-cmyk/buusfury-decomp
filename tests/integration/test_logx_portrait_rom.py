"""Read-only ROM-gated evidence for the GRAPHICS-COVERAGE-001 portrait population.

Asserts the measured portrait container population and its disjointness from the
accepted sprite / tileset / map graphs. Every expected value is a count, an
address or a size - no decoded payload is committed. The suite skips cleanly when
the private canonical image is not configured.

Run with ``LOGX_CANONICAL_ROM`` pointing at the image, or place it at the default
``roms/Dragon Ball Z - Buu's Fury (U).gba``.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from tools.research import logx_gfxscan_probe as scan
from tools.research import logx_portrait_probe as pp


@pytest.fixture(scope="module")
def canonical_bytes() -> bytes:
    path = Path(
        os.environ.get("LOGX_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba")
    )
    if not path.is_file():
        pytest.skip("canonical Buu ROM not configured locally")
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == pp.CANONICAL_SHA256
    return data


def test_portrait_array_base_is_engine_derived(canonical_bytes: bytes) -> None:
    # The base is read from the accessor's own pool word (LOGX-CHAR-001 s11.2).
    assert pp.portrait_array_base(canonical_bytes) == 0x086F393C


def test_portrait_population(canonical_bytes: bytes) -> None:
    report = pp.enumerate_portraits(canonical_bytes)
    assert report["portrait_count"] == 155
    assert report["pointers_strictly_ascending"] is True
    assert report["container_kinds"] == {1: 155}
    assert report["declared_sizes"] == [4096]
    assert report["decoded_sizes"] == [4096]
    assert report["decode_failures"] == 0
    assert report["packed_extent_overlaps"] == 0
    assert report["first_pointer"] == "0x086B880C"
    assert report["last_pointer"] == "0x086F3360"


def test_portraits_disjoint_from_accepted_graphics_corpus(
    canonical_bytes: bytes,
) -> None:
    """No portrait container is reached by the accepted sprite/tileset/map graphs."""
    corpus = scan.build_known_corpus(canonical_bytes)
    known = set(corpus.resources.keys())
    portraits = set(pp.portrait_pointers(canonical_bytes))
    assert portraits & known == set()
