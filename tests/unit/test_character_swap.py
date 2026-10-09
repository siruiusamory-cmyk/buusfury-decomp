"""The invocable front end: spec parsing, and the two rules it must own exactly once.

No ROM is needed. The spec tests are pure, and the guard tests use a trivial transform because
the rules under test are about files and identities rather than about pixels.
"""

from __future__ import annotations

import json
import os

import pytest

from tools.webfoot import character_swap as cs
from tools.webfoot import sprite_swap
from tools.webfoot.sprite_swap import SpriteSwapError


def test_a_sprite_spec_becomes_a_sprite_operation():
    sprites, portraits, rewrites = cs.parse_spec({"operations": [
        {"kind": "sprite", "sprite_id": 41,
         "slots": [{"slot": 0, "sheet": "stand.png", "frames": 2}]}]})
    assert len(sprites) == 1 and not portraits and not rewrites
    assert sprites[0].sprite_id == 41
    assert sprites[0].character_index == 31
    assert (sprites[0].slots[0].slot, sprites[0].slots[0].sheet,
            sprites[0].slots[0].frames_per_facing) == (0, "stand.png", 2)


def test_the_geometry_defaults_to_the_measured_donor():
    sprites, _, _ = cs.parse_spec({"operations": [
        {"kind": "sprite", "sprite_id": 12,
         "slots": [{"slot": 0, "sheet": "a.png", "frames": 1}]}]})
    assert sprites[0].geometry == cs.DONOR_GEOMETRY


def test_a_portrait_spec_becomes_a_portrait_operation():
    _, portraits, _ = cs.parse_spec({"operations": [
        {"kind": "portrait", "slot": 17, "png": "portrait.png", "side": 64}]})
    assert portraits[0].slot == 17 and portraits[0].side == 64


def test_a_dialogue_spec_keeps_the_record_optional_and_the_speaker_a_claim():
    _, _, rewrites = cs.parse_spec({"operations": [
        {"kind": "dialogue", "selector": 2,
         "lines": [{"speaker": "tulma", "old": "x", "new": "y"},
                   {"speaker": "bulma", "old": "p", "new": "q", "record": [10, 4]}]}]})
    first, second = rewrites[0].lines
    assert (first.decoded_start, first.decoded_length) == (None, None)
    assert (second.decoded_start, second.decoded_length) == (10, 4)
    assert second.speaker == "bulma"


def test_an_empty_spec_is_refused():
    with pytest.raises(cs.SwapSpecError, match="non-empty 'operations'"):
        cs.parse_spec({"operations": []})


def test_an_unknown_operation_kind_is_refused():
    with pytest.raises(cs.SwapSpecError, match="unknown kind"):
        cs.parse_spec({"operations": [{"kind": "shrink", "sprite_id": 1}]})


def test_a_sprite_without_slots_is_refused():
    with pytest.raises(cs.SwapSpecError, match="non-empty 'slots'"):
        cs.parse_spec({"operations": [{"kind": "sprite", "sprite_id": 1, "slots": []}]})


def test_a_dialogue_edit_without_lines_is_refused():
    with pytest.raises(cs.SwapSpecError, match="needs 'lines'"):
        cs.parse_spec({"operations": [{"kind": "dialogue", "selector": 2, "lines": []}]})


def test_a_record_that_is_not_a_pair_is_refused():
    with pytest.raises(cs.SwapSpecError, match="decoded start"):
        cs.parse_spec({"operations": [
            {"kind": "dialogue", "selector": 2,
             "lines": [{"old": "x", "new": "y", "record": [1, 2, 3]}]}]})


def _transform(image: bytes) -> tuple[bytes, dict]:
    return image + b"!", {"note": "appended one byte"}


def test_guarded_apply_writes_the_output_and_the_report(tmp_path):
    image = tmp_path / "image.bin"
    image.write_bytes(b"base")
    report = cs.guarded_apply(image, cs.sha256(b"base"), tmp_path / "out.bin",
                              tmp_path / "report.json", _transform)
    assert (tmp_path / "out.bin").read_bytes() == b"base!"
    assert report["image"]["output_size"] == 5
    assert json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))["note"]


def test_guarded_apply_refuses_to_write_over_its_own_input(tmp_path):
    image = tmp_path / "image.bin"
    image.write_bytes(b"base")
    with pytest.raises(cs.WriteError, match="same file"):
        cs.guarded_apply(image, cs.sha256(b"base"), image, None, _transform)


def test_guarded_apply_refuses_a_hard_link_of_its_own_input(tmp_path):
    image = tmp_path / "image.bin"
    image.write_bytes(b"base")
    alias = tmp_path / "alias.bin"
    os.link(image, alias)
    with pytest.raises(cs.WriteError, match="same file"):
        cs.guarded_apply(image, cs.sha256(b"base"), alias, None, _transform)
    assert image.read_bytes() == b"base"


def test_guarded_apply_refuses_a_report_that_is_its_own_input(tmp_path):
    image = tmp_path / "image.bin"
    image.write_bytes(b"base")
    with pytest.raises(cs.WriteError, match="same file"):
        cs.guarded_apply(image, cs.sha256(b"base"), tmp_path / "out.bin", image, _transform)
    assert image.read_bytes() == b"base"


def test_guarded_apply_refuses_an_image_that_is_not_the_expected_one(tmp_path):
    image = tmp_path / "image.bin"
    image.write_bytes(b"base")
    with pytest.raises(cs.SwapSpecError, match="not the image this swap was proven"):
        cs.guarded_apply(image, "00" * 32, tmp_path / "out.bin", None, _transform)
    assert not (tmp_path / "out.bin").exists(), "a refusal must not leave an output behind"


def test_guarded_apply_leaves_no_partial_files_behind_after_a_refusal(tmp_path):
    image = tmp_path / "image.bin"
    image.write_bytes(b"base")
    with pytest.raises(cs.WriteError):
        cs.guarded_apply(image, cs.sha256(b"base"), image, None, _transform)
    assert [p.name for p in tmp_path.iterdir()] == ["image.bin"]


def test_the_engine_refuses_a_pass_with_nothing_to_do(tmp_path):
    with pytest.raises(SpriteSwapError, match="no operation was given"):
        sprite_swap.swap(b"", tmp_path)
