"""The invocable front end: spec parsing, and the two rules it must own exactly once.

No ROM is needed. The spec tests are pure, and the guard tests use a trivial transform because
the rules under test are about files and identities rather than about pixels.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from tools.webfoot import character_swap as cs
from tools.webfoot import destination as destination_sdk
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


def test_a_typo_in_a_key_is_refused_rather_than_ignored():
    """A misspelled key would otherwise silently write with the donor's value for it."""
    with pytest.raises(cs.SwapSpecError, match="does not define"):
        cs.parse_spec({"operations": [
            {"kind": "sprite", "sprite_id": 41, "cropx": 8,
             "slots": [{"slot": 0, "sheet": "a.png", "frames": 1}]}]})


def test_a_misspelled_record_key_is_refused_rather_than_dropping_the_span_check():
    with pytest.raises(cs.SwapSpecError, match="does not define"):
        cs.parse_spec({"operations": [
            {"kind": "dialogue", "selector": 2,
             "lines": [{"old": "x", "new": "y", "records": [1, 2]}]}]})


def test_a_float_where_an_integer_belongs_is_refused_rather_than_truncated():
    with pytest.raises(cs.SwapSpecError, match="must be an integer"):
        cs.parse_spec({"operations": [
            {"kind": "portrait", "slot": 17.9, "png": "p.png"}]})


def test_a_missing_key_is_refused_with_the_key_named():
    with pytest.raises(cs.SwapSpecError, match="missing 'sprite_id'"):
        cs.parse_spec({"operations": [
            {"kind": "sprite", "slots": [{"slot": 0, "sheet": "a.png", "frames": 1}]}]})


def test_an_operation_that_is_not_an_object_is_refused():
    with pytest.raises(cs.SwapSpecError, match="unknown kind"):
        cs.parse_spec({"operations": ["sprite"]})


def test_a_crop_window_outside_the_cell_is_refused():
    with pytest.raises(cs.SwapSpecError, match="outside a 32-pixel cell"):
        cs.parse_spec({"operations": [
            {"kind": "sprite", "sprite_id": 41, "crop_x": 24, "frame": [16, 32],
             "slots": [{"slot": 0, "sheet": "a.png", "frames": 1}]}]})


# --- text fields are required strings, never coerced ------------------------------------------


def _line(**overrides) -> dict:
    line = {"speaker": "tulma", "old": "the old wording", "new": "the new wording"}
    line.update(overrides)
    return line


def _dialogue(*lines: dict) -> dict:
    return {"operations": [{"kind": "dialogue", "selector": 2, "lines": list(lines)}]}


def test_a_null_new_text_is_refused_rather_than_written_as_the_word_none():
    """The defect this closes: str(None) became the literal line "None" and passed read-back."""
    with pytest.raises(cs.SwapSpecError, match="must be a string"):
        cs.parse_spec(_dialogue(_line(new=None)))


def test_a_null_old_text_is_refused():
    with pytest.raises(cs.SwapSpecError, match="must be a string"):
        cs.parse_spec(_dialogue(_line(old=None)))


def test_a_number_where_a_line_belongs_is_refused():
    with pytest.raises(cs.SwapSpecError, match="must be a string"):
        cs.parse_spec(_dialogue(_line(new=42)))


def test_a_null_speaker_is_refused_rather_than_becoming_the_word_none():
    with pytest.raises(cs.SwapSpecError, match="must be a string"):
        cs.parse_spec(_dialogue(_line(speaker=None)))


def test_an_omitted_speaker_is_still_allowed_and_stays_a_claim():
    _, _, rewrites = cs.parse_spec(_dialogue({"old": "the old wording",
                                             "new": "the new wording"}))
    assert rewrites[0].lines[0].speaker == "unstated"


def test_a_null_sheet_name_is_refused():
    with pytest.raises(cs.SwapSpecError, match="must be a string"):
        cs.parse_spec({"operations": [
            {"kind": "sprite", "sprite_id": 41,
             "slots": [{"slot": 0, "sheet": None, "frames": 1}]}]})


def test_a_null_portrait_name_is_refused():
    with pytest.raises(cs.SwapSpecError, match="must be a string"):
        cs.parse_spec({"operations": [{"kind": "portrait", "slot": 17, "png": None}]})


def test_the_diagnostic_names_the_field_that_is_wrong():
    with pytest.raises(cs.SwapSpecError, match="operation 0 line 1: new"):
        cs.parse_spec(_dialogue(_line(), _line(new=None)))


def test_a_refused_text_field_publishes_no_output(tmp_path):
    """The refusal must happen before anything is written, so no file appears."""
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps(_dialogue(_line(new=None))), encoding="utf-8")
    with pytest.raises(cs.SwapSpecError):
        cs.apply_spec(b"image", spec)
    assert [p.name for p in tmp_path.iterdir()] == ["spec.json"]


def test_a_spec_that_is_not_json_is_refused_with_a_message(tmp_path):
    spec = tmp_path / "spec.json"
    spec.write_text("{not json", encoding="utf-8")
    with pytest.raises(cs.SwapSpecError, match="not readable JSON text"):
        cs.apply_spec(b"image", spec)


def test_a_spec_that_is_not_utf8_is_refused_with_a_message(tmp_path):
    spec = tmp_path / "spec.json"
    spec.write_bytes(b'{"operations": [\xff\xfe]}')
    with pytest.raises(cs.SwapSpecError, match="not readable JSON text"):
        cs.apply_spec(b"image", spec)


def test_a_bool_where_a_line_belongs_is_refused():
    with pytest.raises(cs.SwapSpecError, match="must be a string"):
        cs.parse_spec(_dialogue(_line(new=True)))


def test_a_missing_image_is_reported_as_a_refusal(tmp_path):
    with pytest.raises(cs.SwapSpecError, match="could not be read"):
        cs.guarded_apply(tmp_path / "absent.gba", "00" * 32, tmp_path / "out.bin", None,
                         lambda image: (image, {}))


def test_a_missing_file_is_reported_as_a_refusal_not_a_traceback(tmp_path):
    """A missing sheet or portrait arrives as an OSError, which the guard translates."""
    image = tmp_path / "image.bin"
    image.write_bytes(b"base")

    def transform(_image: bytes) -> tuple[bytes, dict]:
        raise FileNotFoundError(2, "No such file or directory", "stand.png")

    with pytest.raises(cs.SwapSpecError, match="could not be read"):
        cs.guarded_apply(image, cs.sha256(b"base"), tmp_path / "out.bin", None, transform)
    assert not (tmp_path / "out.bin").exists()



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


# --- the shared R3 destination policy, on the production publish path --------------------------
#
# The destination rule is `tools.webfoot.destination`, reused as it is. These tests drive it
# through the production path - `guarded_apply`, `write_staged` and the module's own `main` - and
# prove that a refusal leaves the source, the protected inputs, an existing destination and the
# protected directory itself exactly as they were, with no `.partial` file created.
#
# The checkout under test is private to this module: the policy is read from a `.gitignore` this
# file writes into a temporary root, so nothing here reads or writes the real repository's ROM
# inputs.

ROM_NAME = "Dragon Ball Z - Buu's Fury (U).gba"
ROM_BYTES = b"protected canonical rom bytes" * 4


@pytest.fixture(autouse=True)
def _isolate_protected_input_index():
    """One root's protected-input index must not be read by another test's run."""
    destination_sdk._PROTECTED_CACHE.clear()
    yield
    destination_sdk._PROTECTED_CACHE.clear()


@pytest.fixture
def protected_checkout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A private checkout whose `roms/` directory holds one protected ROM."""
    root = tmp_path / "checkout"
    (root / "roms").mkdir(parents=True)
    (root / ".gitignore").write_text("roms/\nroms\n", encoding="utf-8")
    (root / "roms" / ROM_NAME).write_bytes(ROM_BYTES)
    monkeypatch.setattr(destination_sdk, "repository_root", lambda: root)
    return root


def _source(tmp_path: Path) -> Path:
    source = tmp_path / "source.bin"
    source.write_bytes(b"base")
    return source


def _protected_names(checkout: Path) -> list[str]:
    return sorted(p.name for p in (checkout / "roms").iterdir())


def test_guarded_apply_refuses_a_new_name_in_a_protected_directory(
        protected_checkout: Path, tmp_path: Path):
    """The hole this closes: the guard used to run only against the source itself."""
    source = _source(tmp_path)
    destination = protected_checkout / "roms" / "derivative.gba"
    before = (protected_checkout / "roms" / ROM_NAME).read_bytes()

    with pytest.raises(cs.WriteError, match="protected ROM input directory"):
        cs.guarded_apply(source, cs.sha256(b"base"), destination, None, _transform)

    assert not destination.exists()
    assert not list((protected_checkout / "roms").glob("*.partial"))
    assert _protected_names(protected_checkout) == [ROM_NAME]
    assert (protected_checkout / "roms" / ROM_NAME).read_bytes() == before
    assert source.read_bytes() == b"base"


def test_guarded_apply_refuses_a_report_in_a_protected_directory(
        protected_checkout: Path, tmp_path: Path):
    """The policy is about the path, so it covers the report destination too."""
    source = _source(tmp_path)
    destination = protected_checkout / "roms" / "report.json"

    with pytest.raises(cs.WriteError, match="protected ROM input directory"):
        cs.guarded_apply(source, cs.sha256(b"base"), tmp_path / "out.bin", destination,
                         _transform)

    assert not destination.exists()
    assert not (tmp_path / "out.bin").exists(), "the report refusal must precede the publish"
    assert _protected_names(protected_checkout) == [ROM_NAME]


def test_guarded_apply_refuses_a_hardlink_of_a_protected_rom(
        protected_checkout: Path, tmp_path: Path):
    """A different name and a different directory, one file: identity is what refuses this."""
    source = _source(tmp_path)
    protected = protected_checkout / "roms" / ROM_NAME
    alias = tmp_path / "alias.gba"
    os.link(protected, alias)

    with pytest.raises(cs.WriteError, match="same file under a different name"):
        cs.guarded_apply(source, cs.sha256(b"base"), alias, None, _transform)

    assert protected.read_bytes() == ROM_BYTES
    assert alias.read_bytes() == ROM_BYTES
    assert not list(tmp_path.glob("*.partial"))


def test_guarded_apply_refuses_a_junction_route_into_a_protected_directory(
        protected_checkout: Path, tmp_path: Path):
    """A directory alias is not a way around the rule; the destination path is resolved."""
    route = tmp_path / "route-to-roms"
    try:
        os.symlink(protected_checkout / "roms", route, target_is_directory=True)
    except (OSError, NotImplementedError) as exc:  # pragma: no cover - host policy
        pytest.skip(f"this host cannot create a directory link: {exc}")
    if not route.is_dir():  # pragma: no cover - defensive
        pytest.skip("the host accepted the call but created no directory link")

    with pytest.raises(cs.WriteError, match="protected ROM input directory"):
        cs.guarded_apply(_source(tmp_path), cs.sha256(b"base"), route / "anything.gba", None,
                         _transform)

    assert _protected_names(protected_checkout) == [ROM_NAME]


def test_write_staged_refuses_before_creating_anything_in_a_protected_directory(
        protected_checkout: Path, tmp_path: Path):
    """The publish boundary itself refuses: no directory and no `.partial` file is created.

    `write_staged` is the function that calls `mkdir` and creates the temporary file, so this is
    the call a guard placed only beside the source-alias checks would have left reachable.
    """
    destination = protected_checkout / "roms" / "made-up" / "out.gba"

    with pytest.raises(cs.WriteError, match="protected ROM input directory"):
        cs.write_staged(destination, b"x", _source(tmp_path))

    assert not (protected_checkout / "roms" / "made-up").exists()
    assert _protected_names(protected_checkout) == [ROM_NAME]


def test_the_cli_refuses_a_protected_destination_and_never_reaches_the_spec(
        protected_checkout: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    """Direct CLI invocation: exit 2, the rule named, and no file or directory created."""
    source = _source(tmp_path)
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps(_dialogue(_line())), encoding="utf-8")
    destination = protected_checkout / "roms" / "cli-output.gba"

    code = cs.main(["--image", str(source), "--expect-sha256", cs.sha256(b"base"),
                    "--spec", str(spec), "--out", str(destination)])

    assert code == 2
    captured = capsys.readouterr()
    assert "refused:" in captured.err
    assert "protected ROM input directory" in captured.err
    assert not destination.exists()
    assert _protected_names(protected_checkout) == [ROM_NAME]


def test_the_cli_still_writes_a_legitimate_derivative(tmp_path: Path,
                                                      monkeypatch: pytest.MonkeyPatch,
                                                      capsys: pytest.CaptureFixture[str]):
    """Requirement 5: a safe output location is still written, directory and all.

    Only the pixel and dialogue engines are stubbed here; the guard, the staged write, the exit
    code and the report are the production ones.
    """
    source = _source(tmp_path)
    spec = tmp_path / "spec.json"
    spec.write_text("{}", encoding="utf-8")
    destination = tmp_path / "output" / "derivative.gba"
    report = tmp_path / "output" / "derivative.json"
    monkeypatch.setattr(cs, "apply_spec",
                        lambda image, path: (image + b"!", {"note": "n", "passes": []}))

    code = cs.main(["--image", str(source), "--expect-sha256", cs.sha256(b"base"),
                    "--spec", str(spec), "--out", str(destination), "--report", str(report)])

    assert code == 0
    assert destination.read_bytes() == b"base!"
    assert json.loads(report.read_text(encoding="utf-8"))["note"] == "n"
    assert cs.sha256(destination.read_bytes()) in capsys.readouterr().out
