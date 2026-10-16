"""The Cell port: extraction, build and independent verification, gated on both retail images.

The port is a translation between two titles that share an engine, so the tests that matter are the ones
that would catch a silent mistake: the source walk must find exactly the records the measurements describe,
the built image must announce the animations it claims, and the verifier must compare the ported payloads
against the source's rather than trusting the builder.

Both ROMs are read only through the same gate the rest of the suite uses, so the tests skip where they are
absent instead of reaching for a private path.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tests.rom_support import (  # noqa: E402
    CANONICAL_ROM_SHA256, canonical_rom_bytes, canonical_rom_path)

LOG2_SHA256 = "6E6C370C339EC9171CB1956ADF837A0D342A197F78964882EF46C3086656FF75"
LOG2_DEFAULT = Path("roms") / "Dragon Ball Z - The Legacy of Goku II (USA).gba"
#: The release configuration: Perfect Cell replaces SPOPOVICH, whose id is 252 and whose definition
#: announces 20 animation slots. Testing any other id would not exercise what ships.
PORT_ID = 252
PORT_SLOTS = "20"


#: The second retail title this port reads. Named by an environment variable first, so a worktree that
#: does not carry it can still exercise the test without a private path being tracked here.
LOG2_ENVIRONMENT_VARIABLES = ("WEBFOOT_LOG2_ROM", "LOGX_LOG2_ROM")


def log2_path() -> Path | None:
    import os
    candidates = [Path(os.environ[name]) for name in LOG2_ENVIRONMENT_VARIABLES if os.environ.get(name)]
    candidates.append(ROOT / LOG2_DEFAULT)
    for candidate in candidates:
        if candidate.is_file() and \
                hashlib.sha256(candidate.read_bytes()).hexdigest().upper() == LOG2_SHA256:
            return candidate
    return None


@pytest.fixture(scope="module")
def built(tmp_path_factory) -> dict:
    """Build the port from the two retail images, or skip."""
    if canonical_rom_path() is None:
        pytest.skip("canonical Buu's Fury ROM not present locally")
    if hashlib.sha256(canonical_rom_bytes()).hexdigest() != CANONICAL_ROM_SHA256:
        pytest.skip("local Buu's Fury image is not the canonical profile")
    log2 = log2_path()
    if log2 is None:
        pytest.skip("The Legacy of Goku II is not present locally")
    directory = tmp_path_factory.mktemp("v4b")
    out = directory / "v4b-cell.gba"
    manifest = directory / "manifest.txt"
    result = subprocess.run(
        [sys.executable, "-m", "tools.research.build_friend_v4b_cell",
         "--log2", str(log2), "--image", str(canonical_rom_path()),
         "--expect-sha256", CANONICAL_ROM_SHA256, "--id", str(PORT_ID), "--slots", PORT_SLOTS,
         "--out", str(out), "--manifest", str(manifest)],
        cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    return {"out": out, "log2": log2, "stdout": result.stdout}


def test_the_source_walk_finds_the_measured_records(built) -> None:
    from tools.research.build_friend_v4b_cell import read_log2_cell
    slots, payloads = read_log2_cell(built["log2"].read_bytes())
    assert len(slots) == 8, "Cell has 2 animations x 4 directions"
    assert sum(len(records) for records in slots) == 24
    assert len(payloads) == 17
    assert all(record[2] == 64 and record[3] == 64 for records in slots for record in records), (
        "every Cell piece is 64x64, which is why no piece has to be composed for the target engine")


def test_the_build_repoints_the_named_id_and_appends(built) -> None:
    manifest = (built["out"].parent / "manifest.txt").read_text(encoding="utf-8")
    assert f"id: {PORT_ID}" in manifest
    assert "animations: 2" in manifest
    assert "payloads: 17" in manifest
    base = canonical_rom_bytes()
    port = built["out"].read_bytes()
    assert len(port) > len(base), "the port appends; it must not shrink the image"
    import struct
    word = struct.unpack_from("<I", port, 0x6B6BB4 + 4 * PORT_ID)[0]
    assert word >= 0x08000000 + len(base), "the id must point into the appended region"
    definition = word - 0x08000000
    assert port[definition] & 0xFF == int(PORT_SLOTS), (
        "the definition must announce the slot count the release fills")


def test_the_independent_verifier_passes(built) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "tools.research.verify_friend_v4b_cell",
         "--log2", str(built["log2"]), "--image", str(built["out"]),
         "--id", str(PORT_ID), "--base-image", str(canonical_rom_path()), "--base-id", str(PORT_ID),
             "--palette", "0x0805652C", "--source-palette", "0x081DA6C8"],
        cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "verdict: PASS" in result.stdout
    assert "header: identical to the base definition" in result.stdout, (
        "the crash-class fix: every header field the constructor reads must match the definition replaced")
    assert "allocator size 4096" in result.stdout, (
        "0x1000 is the value Spopovich's definition carries for one 64x64 8bpp frame")
    assert "every source payload present: True" in result.stdout
    assert "block(s) concatenated in slot order" in result.stdout, (
        "the verifier must state that the order was checked, not only the membership")
    assert "entries whose colour differs from the source title" in result.stdout, (
        "the palette difference must be reported: the port renders, but not in the source colors")


def test_the_builder_requires_the_source_titles_digest(tmp_path) -> None:
    """No filename may excuse skipping the source identity check."""
    from tools.research.build_friend_v4b_cell import LOG2_SHA256, CellPortError, sha256_of
    text = (ROOT / "tools/research/build_friend_v4b_cell.py").read_text(encoding="utf-8")
    assert "and not Path(args.image).name.startswith(\"log2\")" not in text, (
        "the digest check must not be skippable by naming the output after the source title")
    assert LOG2_SHA256 in text
    fake = tmp_path / "log2-not-really.gba"
    fake.write_bytes(b"\x00" * 64)
    assert sha256_of(fake) != LOG2_SHA256


def test_the_builder_refuses_to_write_over_an_input(tmp_path) -> None:
    """ROM_SAFETY: an output may never BE an input, and the write must be staged."""
    path = ROOT / "tools/research/build_friend_v4b_cell.py"
    text = path.read_text(encoding="utf-8")
    assert "names an input this build reads" in text, "no refusal for an output equal to an input"
    assert "protected input directory" in text, "no refusal for writing inside roms/ or dumps/"
    assert ".staging" in text, "the write must go through a staged file that is renamed into place"


def test_the_verifier_checks_frame_order_not_just_membership() -> None:
    text = (ROOT / "tools/research/verify_friend_v4b_cell.py").read_text(encoding="utf-8")
    assert "not the source's blocks in order" in text, (
        "a reordered port would pass a set comparison, so the order must be checked")


#: The release base: the image the 4B port is built on. It is a build artifact, not a repository file, so a
#: test that needs it finds it by identity and skips with a reason rather than assuming a path.
RELEASE_BASE_SHA256 = "a21c1e27f7b4f04cbe6952d70eb102b350adac04e6eaba106fa10e2b90a55021"
RELEASE_BASE_ENVIRONMENT = ("WEBFOOT_V4A_IMAGE", "LOG1_V4A_IMAGE")


def release_base() -> Path | None:
    import hashlib
    import os
    candidates = [Path(os.environ[name]) for name in RELEASE_BASE_ENVIRONMENT
                  if os.environ.get(name)]
    candidates += [ROOT / "build" / "fv4" / "v4a-broly.gba",
                   ROOT / "build" / "fv4" / "v4a-broly" / "v4a-broly.gba"]
    for candidate in candidates:
        if candidate.is_file():
            if hashlib.sha256(candidate.read_bytes()).hexdigest().upper() == RELEASE_BASE_SHA256.upper():
                return candidate
    return None


def test_the_name_is_written_on_the_release_base(tmp_path) -> None:
    """The release configuration is id 252 on the 4A image, so the name write is exercised there."""
    base = release_base()
    if base is None:
        pytest.skip("the release-4A image is not present (name it with WEBFOOT_V4A_IMAGE)")
    log2 = log2_path()
    if log2 is None:
        pytest.skip("The Legacy of Goku II is not present locally")
    out = tmp_path / "named.gba"
    manifest = tmp_path / "named.txt"
    result = subprocess.run(
        [sys.executable, "-m", "tools.research.build_friend_v4b_cell",
         "--log2", str(log2), "--image", str(base), "--expect-sha256", RELEASE_BASE_SHA256,
         "--id", str(PORT_ID), "--slots", PORT_SLOTS, "--name", "Cell",
         "--out", str(out), "--manifest", str(manifest)],
        cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "name_slot: 1018" in manifest.read_text(encoding="utf-8")
    import struct
    port = out.read_bytes()
    name_pointer = struct.unpack_from("<I", port, 0x6BCE8 + 4 * 1018)[0]
    payload = port[name_pointer - 0x08000000:name_pointer - 0x08000000 + 10]
    assert payload.decode("utf-16-le").rstrip("\x00") == "Cell", "the name slot must read Cell"

    # A name longer than the slot holds must be refused rather than overlapping the next slot.
    too_long = tmp_path / "too-long.gba"
    refused = subprocess.run(
        [sys.executable, "-m", "tools.research.build_friend_v4b_cell",
         "--log2", str(log2), "--image", str(base), "--expect-sha256", RELEASE_BASE_SHA256,
         "--id", str(PORT_ID), "--slots", PORT_SLOTS, "--name", "Spopovich the Great",
         "--out", str(too_long), "--manifest", str(tmp_path / "too-long.txt")],
        cwd=ROOT, capture_output=True, text=True)
    assert refused.returncode != 0, "a name that does not fit must be refused"
    assert "would overlap the next slot" in (refused.stdout + refused.stderr)


def test_the_verifier_refuses_to_run_without_the_base_image() -> None:
    """Without the base it cannot check the constructor-read fields, so it must not print a verdict."""
    parser = (ROOT / "tools/research/verify_friend_v4b_cell.py").read_text(encoding="utf-8")
    assert '"--base-image", required=True' in parser, (
        "an optional --base-image let a run without it claim PASS without checking the header")
