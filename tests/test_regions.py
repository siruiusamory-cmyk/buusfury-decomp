"""The region map: structural validation and a regression lock on the numbers.

The totals asserted here are the measured baseline. If a later ticket changes
the map, these tests fail - which is the point: the coverage inventory must not
drift silently while the documentation keeps claiming the old figures.
"""

from __future__ import annotations

import pytest

from buusfury import assets, build, regions

# Measured 2026-09-28 against the canonical ROM. See docs/VALIDATION_REPORT.md.
EXPECTED_TOTALS = {"incbin": 8_268_480, "asset": 26_112, "ads": 94_016}
EXPECTED_COUNTS = {"incbin": 13, "asset": 10, "ads": 5}
ROM_SIZE = 8_388_608


@pytest.fixture(scope="module")
def region_list():
    return regions.load_regions()


# --------------------------------------------------------------------------
# the map is well formed and tiles the ROM exactly
# --------------------------------------------------------------------------
def test_map_loads(region_list):
    assert len(region_list) == 28


def test_map_tiles_the_rom_exactly(region_list):
    regions.validate_tiling(region_list, ROM_SIZE)


def test_regions_are_sorted_and_disjoint(region_list):
    cursor = 0
    for region in region_list:
        assert region.start == cursor, f"{region.id} does not start at 0x{cursor:X}"
        cursor = region.end
    assert cursor == ROM_SIZE


def test_every_region_has_a_class_and_a_reference_source(region_list):
    for region in region_list:
        assert region.cls in regions.VALID_CLASSES
        assert region.reference_source, f"{region.id} has no reference_source"
        assert region.note, f"{region.id} has no note"


def test_every_region_has_a_distinct_id(region_list):
    ids = [r.id for r in region_list]
    assert len(ids) == len(set(ids))


# --------------------------------------------------------------------------
# coverage: the inventory must not drift
# --------------------------------------------------------------------------
def test_class_totals_match_the_documented_baseline(region_list):
    assert regions.class_totals(region_list) == EXPECTED_TOTALS


def test_class_counts_match_the_documented_baseline(region_list):
    counts = {
        cls: len(regions.regions_by_class(region_list, cls))
        for cls in regions.VALID_CLASSES
    }
    assert counts == EXPECTED_COUNTS


def test_totals_sum_to_the_rom_size(region_list):
    totals = regions.class_totals(region_list)
    assert sum(totals.values()) == ROM_SIZE


def test_opaque_coverage_is_the_vast_majority(region_list):
    """The headline finding: the reference project is ~98.6% opaque."""
    totals = regions.class_totals(region_list)
    assert totals["incbin"] / ROM_SIZE > 0.98


def test_ads_blocked_share_is_about_one_percent(region_list):
    totals = regions.class_totals(region_list)
    assert 0.011 < totals["ads"] / ROM_SIZE < 0.012


# --------------------------------------------------------------------------
# named regions carry the lengths measured from the binary
# --------------------------------------------------------------------------
@pytest.mark.parametrize(
    "region_id,expected_length",
    [
        ("rom_header", 0xC0),
        ("crt0", 0x98),
        ("gbaram_text", 0xE8),
        ("gbaram_data", 0x10),
        ("afterlibs_thunk", 0x0C),
        ("asset_intro", 2980),
        ("bmp_corner_top_left", 64),
        ("bmp_corner_top_right", 64),
        ("bmp_corner_bottom_left", 64),
        ("bmp_corner_bottom_right", 64),
        ("palette_bg", 512),
        ("palette_sprite", 512),
        ("color_transforms", 4608),
        ("strings", 89_012),
        ("asset_dialogbox", 788),
        ("asset_dialogbox_small", 548),
        ("asset_splash", 20_516),
        ("opaque_10", 292_440),
    ],
)
def test_named_region_lengths(region_list, region_id, expected_length):
    region = next(r for r in region_list if r.id == region_id)
    assert region.length == expected_length


def test_the_two_corner_and_palette_blocks_are_adjacent_and_exact(region_list):
    """4x64 corner bytes then 2x512 palette bytes, ending flush at 0x05672C."""
    by_id = {r.id: r for r in region_list}
    cursor = by_id["bmp_corner_top_left"].start
    for rid in (
        "bmp_corner_top_left",
        "bmp_corner_top_right",
        "bmp_corner_bottom_left",
        "bmp_corner_bottom_right",
        "palette_bg",
        "palette_sprite",
    ):
        assert by_id[rid].start == cursor, rid
        cursor = by_id[rid].end
    assert cursor == by_id["color_transforms"].start == 0x05672C


# --------------------------------------------------------------------------
# cross-checks against the other config and code
# --------------------------------------------------------------------------
def test_every_asset_region_has_exactly_one_rebuild_spec(region_list):
    asset_ids = {r.id for r in regions.regions_by_class(region_list, regions.CLASS_ASSET)}
    spec_ids = {s.region_id for s in assets.ASSET_SPECS}
    assert asset_ids == spec_ids


def test_every_ads_region_has_a_recorded_reference_command(region_list):
    ads_ids = {r.id for r in regions.regions_by_class(region_list, regions.CLASS_ADS)}
    assert ads_ids == set(build.ADS_COMMANDS)


def test_asset_spec_source_paths_are_reference_relative(region_list):
    for spec in assets.ASSET_SPECS:
        assert not spec.source.startswith("/")
        assert ".." not in spec.source
        assert spec.kind in ("grit", "grit+jcalg1", "copy")


def test_only_the_two_compressed_assets_have_small_uncompressed_sources():
    """A guard against silently swapping a compressed asset for a copy."""
    for spec in assets.ASSET_SPECS:
        if spec.kind == "copy":
            assert spec.source.endswith(".pal")


# --------------------------------------------------------------------------
# tiling validation actually catches the two failure modes
# --------------------------------------------------------------------------
def _region(rid, start, end, cls="incbin"):
    return regions.Region(id=rid, start=start, end=end, cls=cls)


def test_validate_tiling_rejects_a_gap():
    with pytest.raises(regions.RegionMapError) as excinfo:
        regions.validate_tiling([_region("a", 0, 4), _region("b", 8, 16)], 16)
    assert "gap" in str(excinfo.value)


def test_validate_tiling_rejects_an_overlap():
    with pytest.raises(regions.RegionMapError) as excinfo:
        regions.validate_tiling([_region("a", 0, 8), _region("b", 4, 16)], 16)
    assert "overlap" in str(excinfo.value)


def test_validate_tiling_rejects_a_short_map():
    with pytest.raises(regions.RegionMapError) as excinfo:
        regions.validate_tiling([_region("a", 0, 8)], 16)
    assert "ends at" in str(excinfo.value)


def test_validate_tiling_accepts_a_perfect_tiling():
    regions.validate_tiling([_region("a", 0, 8), _region("b", 8, 16)], 16)


def test_load_regions_rejects_an_unknown_class(tmp_path):
    import json

    payload = {
        "rom_size": "0x10",
        "regions": [{"id": "a", "start": "0x0", "end": "0x10", "class": "mystery"}],
    }
    path = tmp_path / "regions.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(regions.RegionMapError):
        regions.load_regions(path)


def test_load_regions_rejects_duplicate_ids(tmp_path):
    import json

    payload = {
        "rom_size": "0x10",
        "regions": [
            {"id": "a", "start": "0x0", "end": "0x8", "class": "incbin"},
            {"id": "a", "start": "0x8", "end": "0x10", "class": "incbin"},
        ],
    }
    path = tmp_path / "regions.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(regions.RegionMapError):
        regions.load_regions(path)


# --------------------------------------------------------------------------
# markdown rendering
# --------------------------------------------------------------------------
def test_markdown_reports_every_class_and_the_total(region_list):
    text = regions.render_markdown(region_list, ROM_SIZE)
    for cls in regions.VALID_CLASSES:
        assert f"`{cls}`" in text
    assert f"{ROM_SIZE:,}" in text
    assert "98.568%" in text
    assert "0.311%" in text
    assert "1.121%" in text


def test_markdown_lists_every_region(region_list):
    text = regions.render_markdown(region_list, ROM_SIZE)
    for region in region_list:
        assert region.id in text


def test_markdown_escapes_pipes_in_reference_sources(tmp_path):
    region = regions.Region(
        id="a", start=0, end=4, cls="incbin", reference_source="a|b", note="n"
    )
    text = regions.render_markdown([region], 4)
    assert "a\\|b" in text


def test_generated_markdown_uses_lf_only(region_list):
    """Generated documents must be byte-stable across platforms.

    Python's text mode translates "\\n" to os.linesep on Windows. If that ever
    leaks into the committed map, every regeneration shows a spurious diff, so
    the guarantee is asserted here rather than trusted.
    """
    text = regions.render_markdown(region_list, ROM_SIZE)
    assert "\r" not in text


def test_committed_map_matches_a_fresh_render(region_list):
    """docs/BUILD_REGIONS.md must be exactly what the generator produces today.

    The build-region document was called ROM_MAP.md before DECOMP-ROM-MAP-001;
    that name now belongs to the independent structural ROM map produced by
    tools/buusfury/mapbuild.py, so the build model lives here instead.
    """
    committed = (regions._identity.REPO_ROOT / "docs" / "BUILD_REGIONS.md").read_text(
        encoding="utf-8"
    )
    assert committed == regions.render_markdown(region_list, ROM_SIZE)
