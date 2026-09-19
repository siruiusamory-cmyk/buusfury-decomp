"""Portable tests for ASSET-EXPORT-001 metadata, the no-prose rule and the PNG
encoder. Nothing here needs the private ROM.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.export import metadata as meta
from tools.export import png

# --- the no-prose rule -------------------------------------------------------

@pytest.mark.parametrize(
    "key",
    [
        "description", "notes", "meaning", "interpretation", "caption",
        "summary", "comment", "commentary", "explanation", "purpose",
        "rationale", "semantic", "title", "label", "about",
    ],
)
def test_prose_keys_are_rejected(key):
    with pytest.raises(meta.MetadataError):
        meta.dumps({"maps": [{"map_index": 0, key: "explained"}]})


@pytest.mark.parametrize("key", ["DESCRIPTION", "Notes", "SuMMaRy"])
def test_prose_detection_is_case_insensitive(key):
    with pytest.raises(meta.MetadataError):
        meta.check_structural({key: "x"})


def test_prose_keys_are_rejected_at_any_depth():
    document = {"a": [{"b": {"c": [{"notes": "deep"}]}}]}
    with pytest.raises(meta.MetadataError) as excinfo:
        meta.check_structural(document)
    assert "notes" in str(excinfo.value)
    assert "$.a[0].b.c[0].notes" in str(excinfo.value)


def test_structural_fields_are_accepted():
    document = {
        "sprite_id": 24,
        "animation_index": 3,
        "frame_index": 2,
        "direction_index": 1,
        "width": 32,
        "height": 48,
        "source_address": "0x08123456",
        "sha256": "ab" * 32,
        "references": ["0x08000000"],
        "null": None,
        "flag": True,
    }
    text = meta.dumps(document)
    assert json.loads(text) == document


def test_serialization_is_deterministic_and_sorted():
    first = meta.dumps({"b": 1, "a": {"d": 2, "c": 3}})
    second = meta.dumps({"a": {"c": 3, "d": 2}, "b": 1})
    assert first == second
    assert first.index('"a"') < first.index('"b"')
    assert first.endswith("\n")


def test_json_uses_lf_endings_and_ascii():
    text = meta.dumps({"rom_text": "Grand Kai's Planet"})
    assert "\r" not in text
    assert "\u2019" not in text or "\\u" in text
    assert meta.dumps({"x": "\u00e9"}).isascii()


def test_csv_rows_quote_only_what_needs_it():
    text = meta.csv_rows(("a", "b"), [("plain", "with,comma"), ('quo"te', 3)])
    lines = text.splitlines()
    assert lines[0] == "a,b"
    assert lines[1] == 'plain,"with,comma"'
    assert lines[2] == '"quo""te",3'
    assert text.endswith("\n")


def test_scan_finds_prose_files(tmp_path: Path):
    (tmp_path / "maps").mkdir()
    (tmp_path / "maps" / "README.md").write_text("notes", encoding="utf-8")
    (tmp_path / "maps" / "notes.txt").write_text("notes", encoding="utf-8")
    (tmp_path / "maps" / "layer_0.png").write_bytes(b"\x89PNG")
    found = {path.name for path in meta.scan_for_prose_files(tmp_path)}
    assert found == {"README.md", "notes.txt"}


def test_scan_finds_prose_metadata_keys(tmp_path: Path):
    (tmp_path / "metadata").mkdir()
    (tmp_path / "metadata" / "good.json").write_text(
        json.dumps({"sprite_id": 1}), encoding="utf-8"
    )
    (tmp_path / "metadata" / "bad.json").write_text(
        json.dumps({"sprite_id": 1, "notes": "hi"}), encoding="utf-8"
    )
    found = meta.scan_for_prose_keys(tmp_path)
    assert len(found) == 1
    assert found[0][0].name == "bad.json"


# --- the PNG encoder ---------------------------------------------------------

def _rgba(width: int, height: int) -> bytes:
    out = bytearray()
    for y in range(height):
        for x in range(width):
            out += bytes(((x * 7) % 256, (y * 11) % 256, 255 - x % 256, 0 if x == 0 else 255))
    return bytes(out)


def test_png_round_trips_exactly():
    pixels = _rgba(9, 5)
    image = png.encode_rgba(9, 5, pixels)
    assert image.startswith(png.PNG_SIGNATURE)
    width, height, decoded = png.decode_rgba(image)
    assert (width, height) == (9, 5)
    assert decoded == pixels


def test_png_is_byte_reproducible():
    pixels = _rgba(16, 16)
    assert png.encode_rgba(16, 16, pixels) == png.encode_rgba(16, 16, pixels)


def test_png_carries_no_timestamp_or_text_chunk():
    image = png.encode_rgba(4, 4, _rgba(4, 4))
    for forbidden in (b"tIME", b"tEXt", b"iTXt", b"zTXt", b"pHYs"):
        assert forbidden not in image


def test_png_uses_colour_type_6_at_depth_8():
    image = png.encode_rgba(4, 4, _rgba(4, 4))
    assert png.read_ihdr(image) == (4, 4, 8, 6)


def test_png_rejects_wrong_buffer_size():
    with pytest.raises(png.PngError):
        png.encode_rgba(4, 4, b"\x00" * 10)


def test_png_rejects_non_positive_dimensions():
    with pytest.raises(png.PngError):
        png.encode_rgba(0, 4, b"")


def test_truncated_png_is_refused():
    image = png.encode_rgba(4, 4, _rgba(4, 4))
    with pytest.raises(png.PngError):
        png.decode_rgba(image[:20])
