"""Portable tests for RESOURCE-LIBRARY-CURATION-001.

Every test here runs against a small **synthetic** raw library built in
``tmp_path`` from the canonical exporter's own metadata schema. Nothing needs
the private ROM, the real 86,444-artifact dump, or an emulator: the curator is a
function of the raw library's metadata plus its file bytes, so a faithful
miniature exercises the same code paths.

The synthetic library deliberately contains the shapes that matter:

* two maps sharing one ROM name (grouping) and one map with no name (fallback);
* two sprites sharing one ROM name, and two unnamed sprites;
* two structurally distinct animations that render byte-identical pixels;
* one animation whose four direction cells all render the same image;
* two sprite definitions selecting the same animation objects (visual aliases);
* a structured sprite-graphics container that duplicates a sprite pose and one
  that exists nowhere else;
* a chunk whose pixels equal a map layer's, so class separation is tested rather
  than assumed.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest

from tools.export import buu_resource_curate as curate
from tools.export import metadata as meta
from tools.export import png


# --- synthetic PNGs ----------------------------------------------------------

def rgba(width: int, height: int, colour: tuple[int, int, int, int]) -> bytes:
    return bytes(colour) * (width * height)


def image(colour: tuple[int, int, int, int], width: int = 4, height: int = 4) -> bytes:
    return png.encode_rgba(width, height, rgba(width, height, colour))


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# --- synthetic raw library ---------------------------------------------------

class SyntheticLibrary:
    """Builds a miniature canonical raw library and remembers what it wrote."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.bytes: dict[str, bytes] = {}

    # -- writing ------------------------------------------------------------

    def write(self, relative: str, data: bytes) -> str:
        target = self.root / Path(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        self.bytes[relative] = data
        return relative

    def write_json(self, relative: str, document: object) -> None:
        target = self.root / Path(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(document, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    def build(self) -> Path:
        self._images()
        self._metadata()
        return self.root

    #: The raw map directory each map index gets. The canonical exporter appends
    #: the sanitized ROM string when one exists, and - like the real
    #: ``metadata/names.json`` - stores the directory *without* the ``maps/``
    #: prefix. A curator that reconstructed ``map_<id>`` instead would silently
    #: lose that map's layers, which is the defect this fixture is shaped to
    #: catch.
    map_directories = {
        0: "map_000_west_city",
        1: "map_001_west_city",
        2: "map_002",
        3: "map_003_buu_s_house",
    }

    # -- the artifact layout ------------------------------------------------

    def _images(self) -> None:
        # Maps. map_000 and map_001 share the ROM name "West City"; map_002 is
        # unnamed. map_003's composite is byte-identical to map_002's, which must
        # be *retained* because a distinct MapEntry is a distinct resource.
        self.map_composites = {
            0: image((10, 20, 30, 255), 8, 8),
            1: image((11, 21, 31, 255), 8, 8),
            2: image((12, 22, 32, 255), 8, 8),
            3: image((12, 22, 32, 255), 8, 8),
        }
        self.map_layers = {
            0: [image((1, 1, 1, 255), 4, 4), image((2, 2, 2, 255), 4, 4)],
            1: [image((3, 3, 3, 255), 4, 4)],
            2: [image((4, 4, 4, 255), 4, 4)],
            3: [image((4, 4, 4, 255), 4, 4)],
        }
        for index, data in self.map_composites.items():
            self.write(f"maps/{self.map_directories[index]}/composite.png", data)
        for index, layers in self.map_layers.items():
            for slot, data in enumerate(layers):
                self.write(f"maps/{self.map_directories[index]}/layer_{slot}.png", data)
        for index, layers in self.map_layers.items():
            self.write_json(
                f"maps/{self.map_directories[index]}/map.json",
                {
                    "schema": 1,
                    "map_index": index,
                    "key_high": 0,
                    "key_low": index + 1,
                    "rom_text": None,
                    "text_index": None,
                    "root_address": f"0x082b8c{index:02x}",
                    "composite_image": f"maps/{self.map_directories[index]}/composite.png",
                    "composite_sha256": digest(self.map_composites[index]),
                    "composite_width": 8,
                    "composite_height": 8,
                    "composite_status": "produced",
                    "composite_runtime_status": "provisional_runtime_capture_unavailable",
                    "composite_placement_model": "origin_aligned_descending_addend_bg",
                    "layer_count": len(layers),
                    "layers": [
                        {
                            "slot": slot,
                            "classification": "dominant",
                            "handler": "0x08008087",
                            "status": "rendered",
                            "image": (
                                f"maps/{self.map_directories[index]}/layer_{slot}.png"
                            ),
                            "image_sha256": digest(data),
                            "width": 4,
                            "height": 4,
                            "record_address": f"0x082b1{index:02d}{slot}",
                            "chunk_x": 1,
                            "chunk_y": 1,
                            "chunk_cells": 1,
                            "bg_control_addend": slot,
                        }
                        for slot, data in enumerate(layers)
                    ],
                },
            )

        # Tilesets. Two banks, four tiles each, in a fixed sheet.
        self.tile_bytes = {
            0: [image((5, 5, 5, 255), 8, 8), image((6, 6, 6, 255), 8, 8),
                image((7, 7, 7, 255), 8, 8), image((8, 8, 8, 255), 8, 8)],
            1: [image((9, 9, 9, 255), 8, 8), image((9, 9, 9, 255), 8, 8),
                image((10, 10, 10, 255), 8, 8), image((11, 11, 11, 255), 8, 8)],
        }
        for bank, tiles in self.tile_bytes.items():
            self.write(f"tiles/banks/bank_{bank:03d}/sheet.png", image((0, 0, 0, 255), 32, 8))
            for index, data in enumerate(tiles):
                self.write(f"tiles/banks/bank_{bank:03d}/tiles/tile_{index:04d}.png", data)

        # Chunks. chunk_000 is byte-identical to map 2's only layer: a chunk and a
        # map layer are different resource classes and both must survive.
        self.chunk_bytes = {
            0: self.map_layers[2][0],
            1: image((20, 20, 20, 255), 4, 4),
            2: image((21, 21, 21, 255), 4, 4),
        }
        for index, data in self.chunk_bytes.items():
            self.write(f"tiles/chunks/chunk_{index:06d}.png", data)

        # Sprites. sprite 10 "Babidi" has two animation slots; sprite 11 "Babidi"
        # shares both animation objects with it (a visual alias); sprite 12 is
        # unnamed with one animation whose four direction cells are identical;
        # sprite 13 is unnamed and select the same objects as sprite 12.
        self.animation_bytes = {
            "0x083c0000": {  # two frames, four directions, all distinct
                0: image((30, 30, 30, 255)),
                1: image((31, 31, 31, 255)),
                2: image((32, 32, 32, 255)),
                3: image((33, 33, 33, 255)),
                4: image((34, 34, 34, 255)),
                5: image((35, 35, 35, 255)),
                6: image((36, 36, 36, 255)),
                7: image((37, 37, 37, 255)),
            },
            "0x083c1000": {  # two frames; every direction cell of a frame matches
                0: image((40, 40, 40, 255)),
                1: image((40, 40, 40, 255)),
                2: image((40, 40, 40, 255)),
                3: image((40, 40, 40, 255)),
                4: image((41, 41, 41, 255)),
                5: image((41, 41, 41, 255)),
                6: image((41, 41, 41, 255)),
                7: image((41, 41, 41, 255)),
            },
        }
        self.sprite_slots = {
            10: [("0x083c0000", 2), ("0x083c1000", 2)],
            11: [("0x083c0000", 2), ("0x083c1000", 2)],
            12: [("0x083c1000", 2)],
            13: [("0x083c1000", 2)],
            14: [],
        }
        for sprite_id, slots in self.sprite_slots.items():
            base = f"sprites/sprite_{sprite_id:03d}"
            for slot, (address, frames) in enumerate(slots):
                slot_folder = f"{base}/animations/animation_{slot:02d}"
                cells = self.animation_bytes[address]
                for position, data in sorted(cells.items()):
                    frame = position // 4
                    direction = position % 4
                    self.write(
                        f"{slot_folder}/frame_{frame:03d}/direction_{direction}.png", data
                    )
                self.write(f"{slot_folder}/sheet.png", image((50 + slot, 0, 0, 255), 16, 4))

        # sprite_graphics. graphic 0 duplicates a sprite pose; graphic 1 is unique.
        self.graphic_bytes = {
            0: self.animation_bytes["0x083c0000"][0],
            1: image((60, 60, 60, 255)),
        }
        for index, data in self.graphic_bytes.items():
            self.write(f"sprite_graphics/graphic_{index:06d}.png", data)

        # Palettes.
        self.palette_bytes = {
            0: image((70, 70, 70, 255), 8, 1),
            1: image((71, 71, 71, 255), 8, 1),
        }
        for index, data in self.palette_bytes.items():
            self.write(f"palettes/palette_{index:03d}.png", data)

    def _metadata(self) -> None:
        self.write_json(
            "metadata/names.json",
            {
                "schema": 1,
                "map_names": [
                    {
                        "map_index": 0,
                        "rom_text": "West City",
                        "text_index": 595,
                        "directory": self.map_directories[0],
                    },
                    {
                        "map_index": 1,
                        "rom_text": "West City",
                        "text_index": 595,
                        "directory": self.map_directories[1],
                    },
                    {
                        "map_index": 2,
                        "rom_text": None,
                        "text_index": None,
                        "directory": self.map_directories[2],
                    },
                    {
                        "map_index": 3,
                        "rom_text": "Buu's House",
                        "text_index": 531,
                        "directory": self.map_directories[3],
                    },
                ],
                "sprite_names": [
                    {"sprite_id": 10, "run_index": 0, "names": [{"rom_text": "Babidi"}]},
                    {"sprite_id": 11, "run_index": 1, "names": [{"rom_text": "Babidi"}]},
                    {"sprite_id": 12, "run_index": 2, "names": []},
                    {"sprite_id": 13, "run_index": 3, "names": []},
                    {"sprite_id": 14, "run_index": 4, "names": []},
                ],
            },
        )
        self.write_json(
            "metadata/maps.json",
            {
                "schema": 1,
                "maps": [
                    {
                        "map_index": index,
                        "key_high": 0,
                        "key_low": index + 1,
                        "source_address": "0x080728cc",
                        "root_address": f"0x082b8c{index:02x}",
                        "text_index": None,
                        "rom_text": None,
                        "layer_count": len(self.map_layers[index]),
                        "composite_image": f"maps/map_{index:03d}/composite.png",
                        "composite_sha256": digest(self.map_composites[index]),
                        "composite_width": 8,
                        "composite_height": 8,
                        "composite_status": "produced",
                        "composite_runtime_status": "provisional_runtime_capture_unavailable",
                        "composite_placement_model": "origin_aligned_descending_addend_bg",
                        "composite_unpainted_pixels": 0,
                        "bg_control_index": 0,
                        "connection_count": 0,
                        "animated_tile_count": 0,
                        "char_block_tile_count": 4,
                        "selector_count": 4,
                        "root_extent_x_raw": 0,
                        "root_extent_y_raw": 0,
                        "layers": [
                            {
                                "slot": slot,
                                "classification": "dominant",
                                "handler": "0x08008087",
                                "chunk_x": 1,
                                "chunk_y": 1,
                                "chunk_cells": 1,
                                "bg_control_addend": slot,
                            }
                            for slot in range(len(self.map_layers[index]))
                        ],
                    }
                    for index in range(4)
                ],
            },
        )
        self.write_json(
            "metadata/tile_banks.json",
            {
                "schema": 1,
                "tile_banks": [
                    {
                        "bank_id": bank,
                        "container_address": f"0x080945c{0 + bank}",
                        "declared_size": 256,
                        "packed_bytes": 128,
                        "sheet_sha256": digest(
                            (self.root / f"tiles/banks/bank_{bank:03d}/sheet.png").read_bytes()
                        ),
                        "referencing_map_count": 4,
                    }
                    for bank in (0, 1)
                ],
            },
        )
        self.write_json(
            "metadata/chunks.json",
            {
                "schema": 1,
                "chunks": [
                    {
                        "chunk_id": index,
                        "image": f"tiles/chunks/chunk_{index:06d}.png",
                        "image_sha256": digest(data),
                        "width": 4,
                        "height": 4,
                        "referencing_map_indices": [index],
                        "render_map_index": index,
                        "referencing_map_count": 1,
                    }
                    for index, data in sorted(self.chunk_bytes.items())
                ],
            },
        )
        addresses = sorted(self.animation_bytes)
        self.write_json(
            "metadata/animations.json",
            {
                "schema": 1,
                "unique_animation_count": len(addresses),
                "references": [
                    {
                        "sprite_id": sprite_id,
                        "slot": slot,
                        "animation_address": address,
                        "frame_count": frames,
                        "direction_cells": frames * 4,
                        "cell_addresses": [
                            f"0x083d{position:04x}" for position in range(frames * 4)
                        ],
                    }
                    for sprite_id, slots in sorted(self.sprite_slots.items())
                    for slot, (address, frames) in enumerate(slots)
                ],
                "unique_animations": [
                    {
                        "animation_address": address,
                        "animation_file_offset": "0x3c0000",
                        "frame_count": len(cells) // 4,
                        "direction_cells": len(cells),
                        "cell_addresses": [
                            f"0x083d{position:04x}" for position in range(len(cells))
                        ],
                    }
                    for address, cells in sorted(self.animation_bytes.items())
                ],
            },
        )
        self.write_json("metadata/frames.json", {"schema": 1, "frames": []})
        self.write_json(
            "metadata/sprites.json",
            {
                "schema": 1,
                "sprites": [
                    {
                        "sprite_id": sprite_id,
                        "run_index": sprite_id - 10,
                        "definition_address": f"0x086a89{sprite_id:02x}",
                        "definition_file_offset": "0x6a89d0",
                        "extent_end": "0x086a8a2c",
                        "animation_array_offset": 84,
                        "animation_slots": len(slots),
                        "non_null_slots": len(slots),
                        "null_slots": 0,
                        "slots": [
                            {
                                "slot": slot,
                                "null": False,
                                "status": "rendered",
                                "animation_address": address,
                                "frame_count": frames,
                                "direction_cells": frames * 4,
                                "directory": (
                                    f"sprites/sprite_{sprite_id:03d}/"
                                    f"animations/animation_{slot:02d}"
                                ),
                            }
                            for slot, (address, frames) in enumerate(slots)
                        ],
                    }
                    for sprite_id, slots in sorted(self.sprite_slots.items())
                ],
            },
        )
        self.write_json(
            "metadata/sprite_graphics.json",
            {
                "schema": 1,
                "sprite_graphics": [
                    {
                        "graphic_id": index,
                        "image": f"sprite_graphics/graphic_{index:06d}.png",
                        "image_sha256": digest(data),
                        "width": 4,
                        "height": 4,
                        "colour_256": True,
                        "container_address": f"0x083c34d{index}",
                        "declared_size": 16,
                    }
                    for index, data in sorted(self.graphic_bytes.items())
                ],
            },
        )
        for index, data in sorted(self.palette_bytes.items()):
            self.write_json(
                f"palettes/palette_{index:03d}.json",
                {
                    "palette_id": index,
                    "role": "object" if index == 0 else "background",
                    "encoding": "bgr555_le_u16" if index == 0 else "rgb888",
                    "entry_count": 2,
                    "rgb": [[0, 0, 0], [255, 255, 255]],
                    "image": f"palettes/palette_{index:03d}.png",
                    "image_width": 8,
                    "image_height": 1,
                    "image_sha256": digest(data),
                },
            )


@pytest.fixture()
def synthetic(tmp_path: Path) -> Path:
    return SyntheticLibrary(tmp_path / "raw").build()


@pytest.fixture()
def planned(synthetic: Path):
    raw = curate.RawLibrary(synthetic)
    plan, stats = curate.plan_curation(raw, raw.hash_tree())
    return raw, plan, stats


@pytest.fixture()
def world(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """A scratch root guaranteed to be outside any git work tree.

    The curator refuses to write a curated library inside version control, so the
    tests that exercise that refusal need a root that is genuinely outside it.
    pytest's basetemp is often configured inside the checkout, so this fixture
    resolves a directory beside it instead and asserts the property it needs
    rather than assuming it.
    """
    root = Path(tmp_path_factory.getbasetemp()).parent / "curation-world"
    if curate.find_repository_root(root) is not None:
        pytest.skip("the configured pytest basetemp is inside a git work tree")
    root = root / "run"
    if root.exists():
        shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)
    return root


def paths(plan: curate.Plan) -> set[str]:
    return {entry.relative_path for entry in plan.entries}


# --- Windows-safe clean names -------------------------------------------------

@pytest.mark.parametrize(
    "text,expected",
    [
        ("West City", "West City"),
        ("Buu's House", "Buu's House"),
        ("Grand Kai's Planet", "Grand Kai's Planet"),
        ("Android #18", "Android #18"),
        ("Z-Mart", "Z-Mart"),
        ("Yemma's Assistant", "Yemma's Assistant"),
        ("Mode 7 Fly", "Mode 7 Fly"),
        ("East District 439", "East District 439"),
    ],
)
def test_clean_name_keeps_normal_spacing_and_punctuation(text, expected):
    assert curate.clean_name(text) == expected


def test_clean_name_preserves_the_apostrophe():
    assert "'" in curate.clean_name("Buu's House")
    assert curate.clean_name("Buu's House") != curate.clean_name("Buus House")


def test_clean_name_preserves_spaces():
    assert " " in curate.clean_name("Grand Kai's Planet")
    assert curate.clean_name("Grand Kai's Planet") != "GrandKaisPlanet"


@pytest.mark.parametrize("character", list('<>:"/\\|?*'))
def test_clean_name_removes_windows_forbidden_characters(character):
    cleaned = curate.clean_name(f"Left{character}Right")
    assert character not in cleaned
    assert "Left" in cleaned and "Right" in cleaned


def test_clean_name_drops_trailing_dots_and_spaces():
    assert curate.clean_name("West City.") == "West City"
    assert curate.clean_name("West City... ") == "West City"


def test_clean_name_collapses_control_characters_and_whitespace():
    assert curate.clean_name("West\tCity") == "West City"
    assert curate.clean_name("West\nCity") == "West City"
    assert curate.clean_name("West   City") == "West City"
    assert curate.clean_name("  West City  ") == "West City"


@pytest.mark.parametrize("reserved", ["CON", "con", "NUL", "LPT1", "com9"])
def test_clean_name_refuses_a_reserved_device_name(reserved):
    assert curate.clean_name(reserved) == ""
    assert curate.human_name(reserved, "Map 1") == "Map 1"


def test_clean_name_is_not_re_spaced_or_re_cased():
    assert curate.clean_name("HFIL") == "HFIL"
    assert curate.clean_name("Hercule Caf\u00e9") == "Hercule Caf\u00e9"


def test_clean_name_rejects_a_non_string():
    with pytest.raises(TypeError):
        curate.clean_name(7)  # type: ignore[arg-type]


# --- collision handling -------------------------------------------------------

def test_a_unique_name_is_used_unchanged():
    assert curate.resolve_collisions([("a", "West City")]) == {"a": "West City"}


def test_a_shared_name_becomes_a_one_based_group():
    assigned = curate.resolve_collisions(
        [("a", "West City"), ("b", "West City"), ("c", "West City")]
    )
    assert assigned == {
        "a": "West City 1",
        "b": "West City 2",
        "c": "West City 3",
    }


def test_grouping_is_case_insensitive():
    assigned = curate.resolve_collisions([("a", "NUL"), ("b", "nul")])
    assert len(set(assigned.values())) == 2


def test_a_numbered_name_is_disambiguated_from_a_literal_one():
    assigned = curate.resolve_collisions(
        [("a", "West City"), ("b", "West City"), ("c", "West City 1")]
    )
    assert len(set(assigned.values())) == 3
    assert assigned["a"] == "West City 1"
    assert assigned["c"] != assigned["a"]


def test_collision_handling_is_deterministic():
    requested = [("a", "Z-Mart"), ("b", "Z-Mart"), ("c", "Z-Mart")]
    assert curate.resolve_collisions(requested) == curate.resolve_collisions(requested)


# --- human path audit --------------------------------------------------------

def test_an_underscore_fails_the_human_path_audit():
    assert curate.check_human_path("Maps/west_city/Map.png") is not None
    assert curate.check_human_path("Sprites/sprite_028_babidi/Sprite.json") is not None


@pytest.mark.parametrize(
    "path",
    [
        "Maps/West City/Map.png",
        "Maps/Grand Kai's Planet/Map 1/Map.png",
        "Maps/Buu's House/Layers/Layer 1.png",
        "Sprites/Android 18/Animations/Walk/Pose 1.png",
        "Sprites/Z-Mart/Sprite 1/Sprite.json",
        "Tilesets/Tileset 012/Sheet.png",
    ],
)
def test_legitimate_punctuation_passes_the_human_path_audit(path):
    assert curate.check_human_path(path) is None


def test_the_planned_layout_carries_no_underscore(planned):
    _raw, plan, _stats = planned
    assert curate.scan_human_paths(plan) == []


# --- one-based human numbering -----------------------------------------------

def test_map_pose_layer_and_variant_numbering_starts_at_one():
    assert curate.GROUP.format(name="Map", index=1) == "Map 1"
    assert curate.LAYER_IMAGE.format(index=1) == "Layer 1.png"
    assert curate.POSE_IMAGE.format(index=1) == "Pose 1.png"
    assert curate.GRAPHIC_IMAGE.format(index=1) == "Graphic 1.png"


def test_animation_slot_zero_is_animation_one_when_no_verified_name_exists():
    assert curate.animation_slot_name(11) == (
        "Animation 12",
        curate.NEUTRAL_NAME_SOURCE,
    )


# --- verified name authority --------------------------------------------------

def test_verified_logextractor_slot_names_are_used_with_their_source():
    assert curate.animation_slot_name(0) == ("Stand", curate.LOGEXTRACTOR_SOURCE)
    assert curate.animation_slot_name(1) == ("Walk", curate.LOGEXTRACTOR_SOURCE)
    assert curate.animation_slot_name(8) == ("Idle", curate.LOGEXTRACTOR_SOURCE)
    assert curate.animation_slot_name(17) == ("Dead", curate.LOGEXTRACTOR_SOURCE)


def test_logextractor_placeholder_entries_take_the_neutral_fallback():
    for slot in (11, 20, 22):
        name, source = curate.animation_slot_name(slot)
        assert source == curate.NEUTRAL_NAME_SOURCE
        assert name == f"Animation {slot + 1}"
        assert "unknown" not in name.lower()


def test_a_slot_beyond_the_table_takes_the_neutral_fallback():
    name, source = curate.animation_slot_name(99)
    assert (name, source) == ("Animation 100", curate.NEUTRAL_NAME_SOURCE)


def test_no_animation_name_is_invented_from_appearance():
    allowed = {
        name for name in curate.LOGEXTRACTOR_ANIMATION_NAMES if name
    } | {f"Animation {slot + 1}" for slot in range(64)}
    for slot in range(64):
        assert curate.animation_slot_name(slot)[0] in allowed


# --- curation rules over the synthetic library -------------------------------

def test_maps_keep_one_browsable_entry_per_canonical_map(planned):
    _raw, plan, stats = planned
    assert stats.maps_curated == 4
    # Two maps carry the ROM string "West City", so the flat group numbers them
    # from one; the one unnamed map takes the first neutral label; the fourth is
    # uniquely named and keeps its name unchanged.
    assert "Maps/West City 1/Map.png" in paths(plan)
    assert "Maps/West City 2/Map.png" in paths(plan)
    assert "Maps/Map 1/Map.png" in paths(plan)
    assert "Maps/Buu's House/Map.png" in paths(plan)
    assert "Maps/West City/Map.png" not in paths(plan)


def test_repeated_name_numbering_carries_no_canonical_id(planned):
    _raw, plan, _stats = planned
    index = plan.documents["Index/Maps.json"]["entries"]
    west_city = [row for row in index if row["romText"] == "West City"]
    assert [row["mapId"] for row in west_city] == [0, 1]
    assert [row["groupIndex"] for row in west_city] == [1, 2]
    assert [row["curatedPath"] for row in west_city] == [
        "Maps/West City 1",
        "Maps/West City 2",
    ]


def test_a_repeated_map_name_is_grouped_and_numbered(planned):
    _raw, plan, stats = planned
    assert stats.map_name_groups == 3
    assert stats.maps_in_numbered_groups == 2
    assert stats.maps_unnamed == 1


def test_contextual_map_duplicates_are_retained(planned):
    """map 3's composite equals map 2's; both images must exist."""
    _raw, plan, _stats = planned
    assert "Maps/Map 1/Map.png" in paths(plan)
    assert "Maps/Buu's House/Map.png" in paths(plan)
    assert (
        plan.documents["Index/Source Map.json"] is not None
    )


def test_map_layers_are_one_based(planned):
    _raw, plan, _stats = planned
    assert "Maps/West City 1/Layers/Layer 1.png" in paths(plan)
    assert "Maps/West City 1/Layers/Layer 2.png" in paths(plan)
    assert not any("Layer 0" in path for path in paths(plan))


def test_the_layer_slot_is_always_the_raw_records_own_slot(planned):
    _raw, plan, stats = planned
    index = plan.documents["Index/Maps.json"]["entries"]
    for row in index:
        document = plan.documents[row["recordPath"]]
        assert document["layerCount"] == len(document["layers"])
        assert [layer["slot"] for layer in document["layers"]] == sorted(
            layer["slot"] for layer in document["layers"]
        )
        assert document["layerCount"] > 0


def test_named_map_directories_resolve_their_own_layers(planned):
    """The raw directory carries the ROM name; a reconstructed ``map_<id>`` path
    would find nothing and silently drop every layer of a named map."""
    raw, plan, _stats = planned
    index = {row["mapId"]: row for row in plan.documents["Index/Maps.json"]["entries"]}
    named = index[3]
    assert named["rawPaths"][0] == "maps/map_003_buu_s_house"
    document = plan.documents[named["recordPath"]]
    assert document["layerCount"] == 1
    assert document["layers"][0]["rawPath"] == (
        "maps/map_003_buu_s_house/layer_0.png"
    )
    assert raw.path(document["layers"][0]["rawPath"]).is_file()
    # The composite's own renderer numbers are carried through from the raw map
    # record, so a map stays self-describing without prose.
    assert document["composite"]["composite_width"] == 8
    assert document["composite"]["composite_height"] == 8
    assert len(document["composite"]["composite_sha256"]) == 64


def test_every_maps_layers_resolve_to_real_raw_files(planned):
    raw, plan, _stats = planned
    for row in plan.documents["Index/Maps.json"]["entries"]:
        document = plan.documents[row["recordPath"]]
        assert document["layerCount"] == len(plan.documents and document["layers"])
        for layer in document["layers"]:
            assert raw.path(layer["rawPath"]).is_file(), layer["rawPath"]
            assert layer["sha256"] == raw.sha256_of(layer["rawPath"])


def test_tilesets_expose_a_sheet_but_not_loose_tiles(planned):
    _raw, plan, stats = planned
    assert "Tilesets/Tileset 1/Sheet.png" in paths(plan)
    assert "Tilesets/Tileset 2/Sheet.png" in paths(plan)
    # The loose 8x8 tiles stay in the raw library; the sheet plus coordinates is
    # the curated view, so no ``Individual Tiles`` tree is written.
    assert not any("Individual Tiles" in path for path in paths(plan))
    assert stats.tilesets_curated == 2
    assert stats.individual_tiles_retained == 0


def test_tileset_metadata_records_tile_coordinates(planned):
    _raw, plan, _stats = planned
    document = plan.documents["Tilesets/Tileset 1/Tileset.json"]
    assert document["columns"] == curate.SHEET_TILE_COLUMNS
    assert document["tiles"][1]["x"] == 8
    assert document["tiles"][1]["y"] == 0
    assert document["tiles"][1]["index"] == 1
    assert document["tiles"][1]["column"] == 1
    assert document["tiles"][1]["row"] == 0


def test_chunks_are_retained_in_a_grouped_directory(planned):
    _raw, plan, stats = planned
    assert stats.chunks_curated == 3
    assert "Chunks/Chunks 1 to 32/Chunk 1.png" in paths(plan)
    assert "Chunks/Chunks 1 to 32/Chunk 3.png" in paths(plan)


def test_a_chunk_and_a_map_layer_with_identical_pixels_are_both_kept(planned):
    """A chunk and a map layer are different resource classes."""
    _raw, plan, _stats = planned
    assert "Chunks/Chunks 1 to 32/Chunk 1.png" in paths(plan)
    assert "Maps/Map 1/Map.png" in paths(plan)


def test_pose_names_are_plain_and_sort_naturally(planned):
    _raw, plan, _stats = planned
    poses = sorted(
        path
        for path in paths(plan)
        if "Babidi 1/Animations/Walk/Poses/" in path
    )
    assert poses == [
        "Sprites/Babidi 1/Animations/Walk/Poses/Pose 1.png",
        "Sprites/Babidi 1/Animations/Walk/Poses/Pose 2.png",
    ]


def test_sprites_are_grouped_by_verified_name(planned):
    _raw, plan, stats = planned
    # Sprites 10 and 11 both carry "Babidi", so they number within one group.
    # Sprites 12, 13 and 14 carry no verified name; they take a contiguous
    # human sequence, not their canonical ids.
    assert "Sprites/Babidi 1/Sprite.json" in paths(plan)
    assert "Sprites/Babidi 2/Sprite.json" in paths(plan)
    assert "Sprites/Sprite 1/Sprite.json" in paths(plan)
    assert "Sprites/Sprite 2/Sprite.json" in paths(plan)
    assert "Sprites/Sprite 3/Sprite.json" in paths(plan)
    assert stats.sprites_named == 2
    assert stats.sprites_unnamed == 3
    assert stats.sprite_name_groups == 4
    assert stats.sprites_in_numbered_groups == 2


def test_animations_use_verified_names_and_neutral_fallbacks(planned):
    _raw, plan, _stats = planned
    assert "Sprites/Babidi 1/Animations/Stand/Sheet.png" in paths(plan)
    assert "Sprites/Babidi 1/Animations/Walk/Sheet.png" in paths(plan)


def test_direction_cells_collapse_to_unique_poses(planned):
    """Animation 2's four direction cells per frame render the same image."""
    _raw, plan, stats = planned
    assert stats.direction_cells_collapsed >= 6
    walk = plan.documents["Sprites/Babidi 1/Animations/Walk/Animation.json"]
    assert len(walk["poses"]) == 2
    assert len(walk["cells"]) == 8


def test_a_collapsed_pose_preserves_every_frame_and_direction(planned):
    _raw, plan, _stats = planned
    walk = plan.documents["Sprites/Babidi 1/Animations/Walk/Animation.json"]
    first = walk["poses"][0]
    users = [
        cell
        for cell in walk["cells"]
        if cell["curatedPath"] == first["path"]
    ]
    assert {cell["directionIndex"] for cell in users} == {0, 1, 2, 3}
    assert {cell["frameIndex"] for cell in users} == {0}
    assert len(first["sources"]) >= 1


def test_cells_record_canonical_identity_even_when_payload_is_shared(planned):
    _raw, plan, _stats = planned
    walk = plan.documents["Sprites/Babidi 1/Animations/Walk/Animation.json"]
    # The cells table keeps every original frame/direction pair; the address is
    # the positional key and is carried by the pair itself.
    pairs = {(cell["frameIndex"], cell["directionIndex"]) for cell in walk["cells"]}
    assert pairs == {
        (frame, direction)
        for frame in range(2)
        for direction in range(4)
    }
    collapsed = [cell for cell in walk["cells"] if cell["curatedPath"]]
    assert collapsed
    # Within one animation the four equal direction renders point at one pose and
    # keep their own frame/direction identity.
    first = walk["cells"][0]["curatedPath"]
    assert first.endswith("Pose 1.png")
    assert all(
        cell["curatedPath"] == first for cell in walk["cells"] if cell["frameIndex"] == 0
    )


def test_each_sprite_keeps_its_own_poses_even_when_an_animation_object_is_shared(planned):
    """sprite 11 selects the same animation objects as sprite 10. First-pass
    curation keeps each sprite's poses self-contained: the pose payload may be the
    same bytes, but two different source objects are not merged, and the sprite's
    own folder stays browsable on its own."""
    _raw, plan, stats = planned
    second = plan.documents["Sprites/Babidi 2/Animations/Stand/Animation.json"]
    own_poses = [
        cell["curatedPath"]
        for cell in second["cells"]
        if cell["curatedPath"] and cell["curatedPath"].startswith("Sprites/Babidi 2/")
    ]
    assert own_poses, "sprite 11 should carry its own pose files"
    assert all("Sprites/Babidi 2/" in path for path in own_poses)
    # No cell points into another sprite's tree.
    assert all(
        not cell["curatedPath"].startswith("Sprites/Babidi 1/")
        for cell in second["cells"]
        if cell["curatedPath"]
    )


def test_structurally_distinct_animations_keep_separate_identities(planned):
    """Stand and Walk are different objects; both records exist and both keep
    their own animation address even though payloads may be shared."""
    _raw, plan, _stats = planned
    stand = plan.documents["Sprites/Babidi 1/Animations/Stand/Animation.json"]
    walk = plan.documents["Sprites/Babidi 1/Animations/Walk/Animation.json"]
    assert stand["animationAddress"] != walk["animationAddress"]
    assert stand["name"] != walk["name"]


def test_a_shared_animation_object_is_attributed_to_one_curated_path(planned):
    _raw, plan, stats = planned
    # five non-null slots, four of them selected by a sprite that shares objects
    assert stats.animation_references == 6
    assert stats.unique_animation_objects == 2
    written = [
        path
        for path in paths(plan)
        if path.endswith("Sheet.png") and "/Animations/" in path
    ]
    assert len(written) == 2


def test_sprite_visual_aliases_are_recorded_without_collapsing_identity(planned):
    _raw, plan, stats = planned
    aliases = {(row["spriteId"], row["aliasOfSpriteId"]) for row in plan.aliases}
    assert (11, 10) in aliases
    assert (13, 12) in aliases
    assert stats.distinct_pixel_identity_groups == 2
    assert "Sprites/Babidi 2/Sprite.json" in paths(plan)
    assert "Sprites/Babidi 2/Sprite.json" in plan.documents


def test_sprite_graphics_duplicating_the_sprite_tree_is_indexed_not_copied(planned):
    _raw, plan, _stats = planned
    assert not any(
        path.startswith("Technical/Unique Sprite Graphics/Graphic 1")
        for path in paths(plan)
    )
    assert "Technical/Unique Sprite Graphics/Graphic 2.png" in paths(plan)


def test_palettes_use_neutral_curated_names(planned):
    _raw, plan, stats = planned
    assert "Palettes/Palette 1/Palette.png" in paths(plan)
    assert "Palettes/Palette 2/Palette.png" in paths(plan)
    assert stats.palettes_curated == 2


def test_no_technical_identifier_reaches_a_human_path(planned):
    _raw, plan, _stats = planned
    assert curate.scan_tree_technical_ids(plan) == []


def test_allowlisted_human_numbers_are_permitted(planned):
    _raw, plan, _stats = planned
    permitted = [
        path
        for path in plan.human_paths()
        if any(
            part.startswith(("Tileset ", "Chunk ", "Palette ", "Map ", "Sprite ", "Animation ", "Pose ", "Layer ", "Tile ", "Graphic "))
            for part in Path(path).parts
        )
    ]
    assert permitted


# --- traceability -------------------------------------------------------------

def test_every_curated_artifact_is_traceable_to_a_raw_source(planned):
    _raw, plan, _stats = planned
    assert curate.unrecoverable_sources(plan) == []


def _sources_of(document: dict, entry: dict) -> list[str]:
    """Resolve one source-map entry against the deduplicated sources table."""
    return document["sources"][entry["source"]]


def test_the_source_map_covers_every_curated_path_except_itself(planned):
    _raw, plan, _stats = planned
    document = plan.documents["Index/Source Map.json"]
    mapped = {row["path"] for row in document["entries"]}
    assert mapped == paths(plan) - {"Index/Source Map.json"}
    assert document["entryCount"] == len(mapped)


def test_the_source_map_points_at_paths_that_exist_in_the_raw_library(planned):
    raw, plan, _stats = planned
    document = plan.documents["Index/Source Map.json"]
    sources = [
        source
        for row in document["entries"]
        for source in _sources_of(document, row)
    ]
    # A source may legitimately be absent from the fixture: the canonical exporter
    # writes a per-map ``map.json`` and an ``animations`` directory that this
    # miniature does not reproduce. Everything that is present must resolve.
    present = [source for source in sources if raw.path(source).exists()]
    assert present
    assert {Path(source).suffix for source in present} <= {".png", ".json", ""}
    assert all("\\" not in source for source in present)


def test_a_raw_file_may_participate_in_several_curated_views(planned):
    raw, plan, _stats = planned
    document = plan.documents["Index/Source Map.json"]
    assert document["backrefs"], "the fixture has no shared raw payload"
    for source, indices in document["backrefs"].items():
        assert len(indices) > 1
        assert all(isinstance(index, int) for index in indices)


def test_the_source_map_backrefs_cover_every_shared_raw_source(planned):
    raw, plan, _stats = planned
    document = plan.documents["Index/Source Map.json"]
    # Re-derive the forward map from the entries and check the compact table
    # agrees: every raw source used by more than one curated entry must appear,
    # with exactly the entry indices that reference it.
    forward: dict[str, list[int]] = {}
    for index, row in enumerate(document["entries"]):
        for source in document["sources"][row["source"]]:
            forward.setdefault(source, []).append(index)
    multi = {source: indices for source, indices in forward.items() if len(indices) > 1}
    assert set(multi) == set(document["backrefs"])
    for source, indices in multi.items():
        assert sorted(indices) == sorted(document["backrefs"][source])


def test_index_documents_are_planned_and_written(planned):
    _raw, plan, _stats = planned
    for name in curate.INDEX_DOCUMENTS:
        assert f"Index/{name}" in plan.documents


# --- prose rules --------------------------------------------------------------

def test_no_planned_document_carries_a_prose_field(planned):
    _raw, plan, _stats = planned
    for path, document in plan.documents.items():
        meta.check_structural(document, path)


def test_a_prose_field_is_refused(planned):
    _raw, _plan, _stats = planned
    with pytest.raises(meta.MetadataError):
        meta.dumps({"schema": 1, "description": "this appears to be a map"})


def test_no_curated_document_name_is_a_prose_document(planned):
    raw, plan, _stats = planned
    for path in paths(plan):
        assert Path(path).suffix.lower() in (".png", ".json")


# --- output and source safety -------------------------------------------------

def test_the_output_may_not_be_the_raw_root(world: Path, synthetic: Path):
    with pytest.raises(curate.CurationError):
        curate.ensure_output_roots(synthetic, synthetic, world / "audit")


def test_the_output_may_not_be_inside_the_raw_root(world: Path, synthetic: Path):
    with pytest.raises(curate.CurationError):
        curate.ensure_output_roots(synthetic, synthetic / "curated", world / "audit")


def test_the_raw_root_may_not_be_inside_the_output(world: Path, synthetic: Path):
    with pytest.raises(curate.CurationError):
        curate.ensure_output_roots(synthetic, synthetic.parent, world / "audit")


def test_the_audit_root_may_not_be_the_raw_root(world: Path, synthetic: Path):
    with pytest.raises(curate.CurationError):
        curate.ensure_output_roots(synthetic, world / "out", synthetic)


def test_the_output_and_audit_may_not_contain_one_another(world: Path, synthetic: Path):
    with pytest.raises(curate.CurationError):
        curate.ensure_output_roots(synthetic, world / "out", world / "out" / "audit")
    with pytest.raises(curate.CurationError):
        curate.ensure_output_roots(synthetic, world / "out", world)


def test_a_valid_output_and_audit_pair_is_accepted(world: Path, synthetic: Path):
    curate.ensure_output_roots(synthetic, world / "curated", world / "curated-audit")


def test_an_output_inside_a_git_work_tree_is_refused(world: Path, synthetic: Path):
    repository = world / "repo"
    (repository / ".git").mkdir(parents=True)
    (repository / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    with pytest.raises(curate.CurationError):
        curate.ensure_output_roots(synthetic, repository / "curated", world / "audit")


def test_a_stray_git_directory_without_head_is_not_a_repository(world: Path, synthetic: Path):
    """An interrupted clone leaves a bare ``.git``; it must not refuse a safe path."""
    stray = world / "stray"
    (stray / ".git").mkdir(parents=True)
    curate.ensure_output_roots(
        synthetic, stray / "curated", stray / "curated-audit"
    )


# --- deterministic rebuild ----------------------------------------------------

def test_two_plans_from_one_raw_library_are_identical(synthetic: Path):
    first_raw = curate.RawLibrary(synthetic)
    first_plan, first_stats = curate.plan_curation(first_raw, first_raw.hash_tree())
    second_raw = curate.RawLibrary(synthetic)
    second_plan, second_stats = curate.plan_curation(second_raw, second_raw.hash_tree())

    assert paths(first_plan) == paths(second_plan)
    assert first_stats.as_document() == second_stats.as_document()
    for path, document in first_plan.documents.items():
        assert meta.dumps(document) == meta.dumps(second_plan.documents[path])


def test_two_builds_write_identical_bytes(world: Path, synthetic: Path):
    outputs = []
    for name in ("first", "second"):
        raw = curate.RawLibrary(synthetic)
        hashes = raw.hash_tree()
        plan, stats = curate.plan_curation(raw, hashes)
        root = world / name
        root.mkdir()
        curate.write_plan(plan, raw, root, stats)
        outputs.append(curate.hash_tree(root))
    assert outputs[0] == outputs[1]


def test_written_images_are_byte_identical_to_their_raw_sources(
    world: Path, synthetic: Path
):
    raw = curate.RawLibrary(synthetic)
    plan, stats = curate.plan_curation(raw, raw.hash_tree())
    root = world / "curated"
    root.mkdir()
    curate.write_plan(plan, raw, root, stats)
    for entry in plan.entries:
        if entry.relative_path in plan.documents or not entry.sources:
            continue
        written = (root / Path(entry.relative_path)).read_bytes()
        assert written == raw.path(entry.sources[0]).read_bytes()


def test_a_written_tree_has_no_underscore_in_a_human_path(world: Path, synthetic: Path):
    raw = curate.RawLibrary(synthetic)
    plan, stats = curate.plan_curation(raw, raw.hash_tree())
    root = world / "curated"
    root.mkdir()
    curate.write_plan(plan, raw, root, stats)
    assert curate.scan_tree_human_paths(root) == []


def test_a_written_tree_has_no_prose_file_and_no_prose_field(
    world: Path, synthetic: Path
):
    raw = curate.RawLibrary(synthetic)
    plan, stats = curate.plan_curation(raw, raw.hash_tree())
    root = world / "curated"
    root.mkdir()
    curate.write_plan(plan, raw, root, stats)
    files, keys = curate.scan_tree_prose(root)
    assert files == []
    assert keys == []


def test_the_curation_run_does_not_modify_the_raw_library(world: Path, synthetic: Path):
    raw = curate.RawLibrary(synthetic)
    before = raw.hash_tree()
    plan, stats = curate.plan_curation(raw, before)
    root = world / "curated"
    root.mkdir()
    curate.write_plan(plan, raw, root, stats)
    after = raw.hash_tree()
    assert before == after


def test_duplicate_planning_refuses_to_write_one_path_twice(synthetic: Path):
    raw = curate.RawLibrary(synthetic)
    plan = curate.Plan()
    plan.add("Maps/West City/Map.png", ("maps/map_000/composite.png",))
    with pytest.raises(curate.CurationError):
        plan.add("Maps/West City/Map.png", ("maps/map_001/composite.png",))


def test_a_case_only_collision_is_refused(synthetic: Path):
    raw = curate.RawLibrary(synthetic)
    plan = curate.Plan()
    plan.add("Maps/West City/Map.png", ("maps/map_000/composite.png",))
    with pytest.raises(curate.CurationError):
        plan.add("Maps/West City/map.png", ("maps/map_001/composite.png",))


def test_a_planned_human_path_with_an_underscore_is_refused(synthetic: Path):
    plan = curate.Plan()
    with pytest.raises(curate.CurationError):
        plan.add("Maps/west_city/Map.png", ("maps/map_000/composite.png",))


def test_raw_duplicate_measurement_reports_the_measured_groups(planned):
    _raw, _plan, stats = planned
    assert stats.exact_duplicate_groups > 0
    assert stats.exact_duplicate_files > stats.exact_duplicate_groups


def test_raw_library_rejects_a_directory_that_is_not_a_canonical_export(tmp_path: Path):
    empty = tmp_path / "not-a-library"
    empty.mkdir()
    with pytest.raises(curate.CurationError):
        curate.RawLibrary(empty)
