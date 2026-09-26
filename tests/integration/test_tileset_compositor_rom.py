"""TILESET-COMPOSITOR-001 ROM-gated integration proof.

Reads the canonical local ROM and nothing else. No ROM-derived fixture is
committed: the assertions here are properties and digests computed from the
image at run time, and the module skips cleanly without one.

The load-bearing assertion is :func:`test_observed_view_is_the_production_renderer`
- the compositor's reference view must stay byte-identical to the accepted
renderer's own output on real chunks, because a second opinion about what a
32x32 screen-entry plane looks like is exactly what the ticket forbids.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from tools.webfoot import map_render as mr
from tools.webfoot import map_view
from tools.webfoot import tileset_compositor as tc
from tools.webfoot.formats import map_graphics as mg


ROM = Path(os.environ.get(
    "WEBFOOT_BUU_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba"
))

#: The identity this module is allowed to describe, read from the profile that
#: owns it rather than restated here.
SUPPORTED_ROM_SHA256 = mr.canonical_profile().sha256

#: The supplied "jigsaw" example: the compiled resource library's Tileset 1 is
#: bank 0 (`containerAddress 0x080945c0`), and it is the bank whose raw sheet
#: reads most obviously as scattered art.
JIGSAW_BANK = 0

#: A bank the LZ literal-base correction measurably changed (BUU_MAP_GRAPHICS
#: _DIAG section 3.7: `shipping == engine` is False for bank 141 and True under
#: the corrected rule). It is in the evidence set precisely because its decode
#: is not the one the pre-correction library shows.
CORRECTED_BANK = 141

pytestmark = pytest.mark.skipif(not ROM.exists(), reason="canonical Buu ROM not configured")


@pytest.fixture(scope="module")
def reader() -> mg.MapGraphicsReader:
    data = ROM.read_bytes()
    assert hashlib.sha256(data).hexdigest() == SUPPORTED_ROM_SHA256
    return mg.MapGraphicsReader(data, mr.canonical_profile())


@pytest.fixture(scope="module")
def census(reader: mg.MapGraphicsReader) -> tc.Census:
    """One census of the whole corpus, shared by every test in the module."""
    return tc.census_image(reader)


def test_every_map_and_layer_in_the_corpus_censuses_without_a_failure(
    census: tc.Census,
) -> None:
    """A census that silently skipped a map would understate every relationship."""
    assert census.maps_censused == census.map_count == 452
    assert census.failures == ()
    assert len(census.banks) == 187
    assert census.bank_table_address == 0x08179764
    # The corpus is large enough for the relationships to mean something.
    assert census.cells_censused > 4_000_000
    assert census.skipped["ordinal_past_selector_stream"] > 0


def test_every_bank_container_matches_the_supplied_librarys_identity(
    reader: mg.MapGraphicsReader,
) -> None:
    """Tileset N is bank N-1, and the census reads the banks in that order.

    The supplied resource library names the identical container address per
    tileset, which is what fixes the correspondence the atlas labels use.
    """
    table, containers = tc.read_bank_table(reader)
    assert table == 0x08179764
    assert len(containers) == 187
    assert containers[JIGSAW_BANK] == 0x080945C0      # Tileset 1
    assert containers[CORRECTED_BANK] == 0x0813CB6C    # Tileset 142
    assert containers[186] == 0x08177AB8               # Tileset 187, the short bank


def test_the_short_bank_declares_241_tiles_and_is_not_truncated(
    reader: mg.MapGraphicsReader,
) -> None:
    table, containers = tc.read_bank_table(reader)
    banks = mg.read_banks(reader, table)
    assert banks[186].declared_size == 0x3C40
    assert banks[186].tile_count == 241
    assert all(bank.tile_count == 256 for bank in banks[:186])


def test_every_inferred_atlas_cell_resolves_to_a_real_declared_tile(
    reader: mg.MapGraphicsReader, census: tc.Census
) -> None:
    """No invented pixel: each cell is a tile the bank actually declares."""
    table, _containers = tc.read_bank_table(reader)
    for bank in (JIGSAW_BANK, CORRECTED_BANK, 178, 41):
        atlas = tc.infer_bank(census, bank)
        declared = census.bank_usage(bank).tile_count
        assert atlas.cells
        assert all(0 <= cell.tile.tile < declared for cell in atlas.cells)
        assert all(cell.tile.bank == bank for cell in atlas.cells)
        # ...and every declared tile is presented at least once.
        assert {cell.tile.tile for cell in atlas.cells} == set(range(declared))


def test_observed_view_is_the_production_renderer(
    reader: mg.MapGraphicsReader, census: tc.Census
) -> None:
    """The reference view must be the accepted renderer's own output.

    The compositor lays the sheet out; it does not own the tile path. This
    renders real observed chunks through both this module and the SDK's chunk
    renderer and requires byte-identical pixels.
    """
    planes, total = tc.observed_chunk_planes(
        reader, census, JIGSAW_BANK, limit=4
    )
    assert total > 0
    assert planes
    for reference, char_data, words in planes:
        accepted = map_view.render_chunk_entries(char_data, words)
        mine = tc.render_observed_view(
            [(reference, char_data, words)], columns=1, gutter=0
        )
        assert mine.pixels == accepted.pixels
        assert (mine.width, mine.height) == (accepted.width, accepted.height)

    sheet = tc.render_observed_view(planes, columns=2, gutter=1)
    assert sheet.width == 2 * (mg.CHUNK_PIXELS + 8) - 8
    assert sheet.detail["chunks"] == len(planes)


def test_the_raw_sheet_is_the_banks_own_storage_order(
    reader: mg.MapGraphicsReader,
) -> None:
    """The before picture is the container, unmodified."""
    table, containers = tc.read_bank_table(reader)
    payload = reader.container(containers[JIGSAW_BANK]).data
    view = tc.render_raw_bank(payload)
    assert (view.width, view.height) == (128, 128)
    assert view.empty_cell_count == 0
    assert view.detail["tiles"] == 256


def test_the_inferred_atlas_is_measurably_more_grouped_than_storage_order(
    reader: mg.MapGraphicsReader, census: tc.Census
) -> None:
    """The whole point: related tiles end up adjacent, unlike the raw sheet.

    The measure is the fraction of horizontally adjacent cells in the sheet
    whose two tiles were ever observed next to each other in a decoded map.
    Storage order has no reason to score well; an inferred sheet that scored the
    same would be a failure no matter how it looked.
    """
    table, containers = tc.read_bank_table(reader)

    def adjacency_rate(width_tiles: int, rows: int, ids: dict) -> float:
        observed = set()
        for (source, _direction), bucket in census.adjacency.items():
            for target in bucket:
                if target >= 0:
                    observed.add((source, target))
        related = total = 0
        for row in range(rows):
            for column in range(width_tiles - 1):
                left = ids.get((column, row))
                right = ids.get((column + 1, row))
                if left is None or right is None:
                    continue
                total += 1
                if (left, right) in observed or (right, left) in observed:
                    related += 1
        return related / total if total else 0.0

    payload = reader.container(containers[JIGSAW_BANK]).data

    raw_ids = {
        (index % tc.RAW_COLUMNS, index // tc.RAW_COLUMNS): (JIGSAW_BANK << 8) | index
        for index in range(256)
    }
    raw_rate = adjacency_rate(
        tc.RAW_COLUMNS, 16, raw_ids
    )

    atlas = tc.infer_bank(census, JIGSAW_BANK)
    inferred_ids = {
        (cell.column, cell.row): (JIGSAW_BANK << 8) | cell.tile.tile
        for cell in atlas.cells
    }
    inferred_rate = adjacency_rate(
        atlas.canvas.columns,
        atlas.canvas.rows,
        inferred_ids,
    )
    assert inferred_rate > raw_rate, (
        f"the inferred sheet is no more grouped than storage order "
        f"({inferred_rate:.3f} vs {raw_rate:.3f})"
    )


def test_census_and_atlas_are_deterministic_over_the_real_corpus(
    reader: mg.MapGraphicsReader,
) -> None:
    """Same bytes in, byte-identical manifest and pixel-identical images out."""
    import json

    def build():
        result = tc.census_image(reader, maps=range(24))
        atlas = tc.infer_bank(result, JIGSAW_BANK)
        payload = reader.container(
            tc.read_bank_table(reader)[1][JIGSAW_BANK]
        ).data
        view = tc.render_inferred_atlas(atlas, payload)
        return (
            json.dumps(tc.atlas_document(result, atlas), sort_keys=True),
            view.pixels,
        )

    assert build() == build()


def test_the_bundle_writes_under_build_output_and_reproduces_byte_identically(
    reader: mg.MapGraphicsReader, tmp_path: Path
) -> None:
    """A run is a fresh directory whose every artifact is reproducible."""
    census = tc.census_image(reader, maps=range(24))
    first = tmp_path / "first"
    second = tmp_path / "second"
    one = tc.write_bundle(reader, census, [JIGSAW_BANK], first, write_observed=False)
    two = tc.write_bundle(reader, census, [JIGSAW_BANK], second, write_observed=False)
    assert [
        (a["path"], a["sha256"]) for a in one["artifacts"]
    ] == [(a["path"], a["sha256"]) for a in two["artifacts"]]
    assert (first / "bank-000" / "raw.png").read_bytes() == (
        second / "bank-000" / "raw.png"
    ).read_bytes()
    assert (first / "manifest.json").read_bytes() == (
        second / "manifest.json"
    ).read_bytes()
