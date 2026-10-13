"""The save catalogue's own bar: kinds by content, provenance by evidence, writes refused.

Every check here is synthetic except the geometry, and the geometry is built the
way the corpus is: an 8-byte-block-reversed medium, a real `zlib.adler32` over
the de-swizzled payload, and the checksum the image actually holds. A check that
would pass on a save the tool mis-reads is worth nothing, so the tests exercise
the read path the CLI uses rather than a helper written for them.
"""

from __future__ import annotations

import hashlib
import json
import os
import struct
import sys
import time
import zlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.save_catalogue import cli, geometry, sniff, walk  # noqa: E402
from tools.save_catalogue.store import CatalogueError, Store  # noqa: E402

SLOT_BASE = 0x10
SLOT_STRIDE = 0x8B0
PAYLOAD_LEN = 0x8A8

PNG_HEAD = (
    b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR"
    + struct.pack(">II", 240, 160) + b"\x08\x02\x00\x00\x00"
    + b"\x00\x00\x00\x00"  # the IHDR CRC, so the chunk stream is walkable
)


def swizzle(data: bytes) -> bytes:
    return b"".join(data[i:i + 8][::-1] for i in range(0, len(data) - len(data) % 8, 8))


def write_slot(image: bytearray, index: int, payload: bytes, corrupt: bool = False) -> None:
    """Write one slot the way the medium does: buffer order in, block-reversed out."""
    buffer_frame = bytearray(payload + bytes(8))
    struct.pack_into("<I", buffer_frame, 0x8A8,
                     (zlib.adler32(payload) + 1) if corrupt else zlib.adler32(payload))
    placed = swizzle(bytes(buffer_frame))
    start = SLOT_BASE + index * SLOT_STRIDE
    image[start:start + len(placed)] = placed


def make_save(slot0: bytes | None = None, stale: bool = False) -> bytes:
    """An 8,192-byte image with slot 0 populated, in the medium's own order.

    Only slot 0 is written, with no trailing scratch: a byte appended past it
    would land inside slot 1's stride and shift the image's own structure.
    """
    payload = slot0 if slot0 is not None else b"\x00\x0b" + bytes(PAYLOAD_LEN - 2)
    image = bytearray(b"\xff" * 8192)
    write_slot(image, 0, payload, corrupt=stale)
    return bytes(image)


@pytest.fixture()
def store_home(tmp_path: Path) -> Path:
    home = tmp_path / "catalogue"
    home.mkdir()
    return home


# -- geometry -----------------------------------------------------------------


def test_a_populated_slot_validates_and_the_erased_ones_do_not():
    slots = geometry.slots(make_save(), geometry.BUUS_FURY)

    assert [slot.checksum_ok for slot in slots] == ["PASS", "UNKNOWN", "UNKNOWN"]
    assert [slot.erased_all_ff for slot in slots] == [False, True, True]
    assert slots[0].transform_scope == "buus_fury_only"
    assert slots[0].occupied is True


def test_a_slot_that_is_not_erased_and_fails_its_checksum_is_corrupt():
    slots = geometry.slots(make_save(stale=True), geometry.BUUS_FURY)

    assert slots[0].checksum_ok == "CORRUPT"
    assert slots[0].occupied is False
    assert slots[0].erased_all_ff is False


def test_the_code_occupancy_bit_is_set_on_an_erased_slot_too():
    """The game's bit says a slot record exists; it is not validity."""
    slots = geometry.slots(make_save(), geometry.BUUS_FURY)

    assert slots[0].code_occupancy_bit is True
    assert slots[1].code_occupancy_bit is True
    assert slots[1].checksum_ok == "UNKNOWN"


def test_the_checksum_offset_is_where_the_image_holds_it():
    """Two coordinate frames, both asserted: buffer slot+0x8A8, file slot+0x8AC."""
    image = make_save()
    block = image[SLOT_BASE:SLOT_BASE + SLOT_STRIDE]
    buffer_frame = geometry.deswizzle(block)
    computed = zlib.adler32(buffer_frame[:PAYLOAD_LEN])

    # The buffer frame: the game's word at its own offset, little-endian.
    assert struct.unpack_from("<I", buffer_frame, 0x8A8)[0] == computed
    # The file frame: the same four bytes at file slot+0x8AC, byte-reversed,
    # which is why an unconverted read there is a different number.
    assert struct.unpack_from(">I", block, 0x8AC)[0] == computed
    assert struct.unpack_from("<I", block, 0x8AC)[0] != computed
    # The catalogue validates the real saves through the buffer frame.
    assert geometry.slots(image, geometry.BUUS_FURY)[0].checksum_stored == computed
    assert geometry.slots(image, geometry.BUUS_FURY)[0].checksum_ok == "PASS"


def test_the_reversal_is_what_makes_the_checksum_match():
    """Raw order must fail, or the transform is not doing any work."""
    image = make_save()
    block = image[SLOT_BASE:SLOT_BASE + SLOT_STRIDE]
    stored = struct.unpack_from(">I", block, 0x8AC)[0]

    assert zlib.adler32(block[:PAYLOAD_LEN]) != stored


def test_deswizzle_is_its_own_inverse():
    image = make_save()

    assert geometry.deswizzle(geometry.deswizzle(image)) == image


def chunk(kind: bytes, body: bytes = b"") -> bytes:
    return struct.pack(">I", len(body)) + kind + body + b"\x00\x00\x00\x00"


# -- kind sniffing ------------------------------------------------------------


def test_a_png_with_a_state_extension_and_no_state_chunk_is_a_misnamed_screenshot():
    kind = sniff.sniff(PNG_HEAD, 32768, ".ss1")

    assert kind.kind == sniff.screenshot
    assert kind.misnamed is True
    assert "240x160" in kind.evidence


def test_a_png_carrying_the_state_chunk_is_a_savestate():
    kind = sniff.sniff(PNG_HEAD, 32768, ".ss1", frozenset({sniff.GBAS_CHUNK}))

    assert kind.kind == sniff.savestate
    assert kind.misnamed is False
    assert "gbAs" in kind.evidence


def test_the_chunk_walk_finds_the_state_chunk_and_stops_at_iend(tmp_path: Path):
    state = tmp_path / "state.ss1"
    state.write_bytes(PNG_HEAD + chunk(b"iDAt", b"x" * 8) + chunk(sniff.GBAS_CHUNK, b"y" * 4)
                      + chunk(b"gbAx", b"z" * 4) + chunk(b"IEND"))
    plain = tmp_path / "shot.png"
    plain.write_bytes(PNG_HEAD + chunk(b"iDAt", b"x" * 8) + chunk(b"IEND"))
    broken = tmp_path / "broken.png"
    broken.write_bytes(b"not a png at all")

    assert sniff.GBAS_CHUNK in sniff.png_chunk_names(state)
    assert sniff.GBAS_CHUNK not in sniff.png_chunk_names(plain)
    assert sniff.png_chunk_names(broken) == frozenset()


def test_a_state_extension_without_the_state_chunk_claims_no_game():
    kind = sniff.sniff(b"\x01\x02\x03\x04" * 4, 4096, ".ss1")

    assert kind.kind == sniff.unknown_state
    assert "gbAs" in kind.evidence


def test_the_two_known_battery_sizes_are_battery_and_an_odd_size_is_not():
    assert sniff.sniff(b"\x00" * 24, 8192, ".sav").kind == sniff.battery
    assert sniff.sniff(b"\x00" * 24, 32768, ".srm").kind == sniff.battery

    odd = sniff.sniff(b"\x00" * 24, 12345, ".sav")
    assert odd.kind == sniff.unknown
    assert "0000" in odd.evidence


# -- the walk -----------------------------------------------------------------


def test_the_walk_indexes_a_save_and_reports_what_it_read(store_home: Path, tmp_path: Path):
    root = tmp_path / "build"
    root.mkdir()
    (root / "1 - Buu's Fury (U).sav").write_bytes(make_save())
    (root / "ignore.txt").write_text("not a save", encoding="utf-8")

    report = walk.scan(store_home, [root])

    assert report.new == 1
    assert report.rehashed == 1
    with Store(store_home).connect() as connection:
        entry = Store(store_home).find(connection)[0]
    assert entry.kind == sniff.battery
    assert entry.game == "buus_fury"
    assert entry.slots[0]["checksum_ok"] == "PASS"
    assert entry.sources[0].path.endswith("(U).sav")
    assert entry.geometry == "buus_fury"


def test_a_second_walk_of_an_unchanged_tree_re_hashes_nothing(store_home: Path, tmp_path: Path):
    root = tmp_path / "build"
    root.mkdir()
    (root / "1 - Buu's Fury (U).sav").write_bytes(make_save())
    walk.scan(store_home, [root])

    again = walk.scan(store_home, [root])

    assert (again.new, again.updated, again.rehashed) == (0, 0, 0)
    assert again.unchanged == 1


def test_a_missing_root_is_reported_rather_than_skipped(store_home: Path, tmp_path: Path):
    report = walk.scan(store_home, [tmp_path / "absent"])

    assert report.missing_roots == [str(tmp_path / "absent")]


def test_verify_reports_drift_and_never_repairs(store_home: Path, tmp_path: Path):
    root = tmp_path / "build"
    root.mkdir()
    target = root / "1 - Buu's Fury (U).sav"
    target.write_bytes(make_save())
    walk.scan(store_home, [root])
    original = target.read_bytes()
    target.write_bytes(make_save(slot0=b"\x00\x0b" + bytes(PAYLOAD_LEN - 3) + b"\x01"))

    report = walk.scan(store_home, [root], verify=True)

    assert [row["path"] for row in report.changed] == [str(target)]
    assert target.read_bytes() != original


def test_a_run_directory_makes_its_staged_save_derived(store_home: Path, tmp_path: Path):
    root = tmp_path / "build"
    run = root / "toolkit031" / "label-1"
    run.mkdir(parents=True)
    save = run / "working-state.sav"
    save.write_bytes(make_save())

    digest = hashlib.sha256(save.read_bytes()).hexdigest().upper()
    (run / "inputs.json").write_text(
        json.dumps({"label": "label-1", "save_path": str(save), "save_sha256": digest}),
        encoding="utf-8",
    )

    walk.scan(store_home, [root])

    with Store(store_home).connect() as connection:
        entry = Store(store_home).find(connection)[0]
    assert entry.provenance == "DERIVED"
    assert "label-1" in entry.provenance_evidence


def test_an_unattributable_file_is_unknown_and_says_why(store_home: Path, tmp_path: Path):
    root = tmp_path / "build"
    root.mkdir()
    (root / "mystery-Buu's Fury.sav").write_bytes(make_save())

    walk.scan(store_home, [root])

    with Store(store_home).connect() as connection:
        entry = Store(store_home).find(connection)[0]
    assert entry.provenance == "UNKNOWN"
    assert "no rule fired" in entry.provenance_evidence


def test_the_known_blank_pattern_is_tool_staged(store_home: Path, tmp_path: Path, monkeypatch):
    root = tmp_path / "build"
    root.mkdir()
    blank = root / "blank.sav"
    blank.write_bytes(bytes(512) + bytes(7680))

    digest = hashlib.sha256(blank.read_bytes()).hexdigest().upper()
    monkeypatch.setitem(walk.KNOWN_BLANK_DIGESTS, digest, "a staged blank")

    walk.scan(store_home, [root])

    with Store(store_home).connect() as connection:
        entry = Store(store_home).find(connection)[0]
    assert entry.provenance == "TOOL-STAGED"
    assert "staged blank" in entry.provenance_evidence


def test_a_zero_byte_state_is_recorded_as_unknown_without_throwing(store_home: Path, tmp_path: Path):
    """The one measured trap: build\\fv4\\dryrun-test\\state.ss1 is 0 bytes."""
    root = tmp_path / "build"
    root.mkdir()
    (root / "state.ss1").write_bytes(b"")

    report = walk.scan(store_home, [root])

    assert report.new == 1
    with Store(store_home).connect() as connection:
        entry = Store(store_home).find(connection)[0]
    assert entry.kind == sniff.unknown_state
    assert entry.size == 0
    assert entry.game == "UNKNOWN"


def test_a_misnamed_screenshot_png_is_not_offered_as_a_state(store_home: Path, tmp_path: Path):
    root = tmp_path / "build"
    root.mkdir()
    (root / "scene.ss1").write_bytes(PNG_HEAD + chunk(b"IEND"))

    walk.scan(store_home, [root])

    with Store(store_home).connect() as connection:
        entry = Store(store_home).find(connection)[0]
    assert entry.kind == sniff.screenshot
    assert entry.misnamed is True
    assert entry.game == "UNKNOWN"
    assert entry.slots == []


# -- the per-title geometry table ---------------------------------------------


def test_a_title_whose_integrity_field_is_not_a_checksum_never_reports_a_pass():
    """Legacy of Goku's word is a rolling XOR key: it cannot detect corruption."""
    layout = geometry.geometry_for(geometry.LEGACY_OF_GOKU)

    assert layout.checksum_kind == geometry.ROLLING_XOR_KEY
    assert layout.integrity_covers_payload is False
    assert layout.medium_size == 512
    image = bytes(512)
    assert [slot.checksum_ok for slot in geometry.slots(image, geometry.LEGACY_OF_GOKU)] == [
        "UNKNOWN", "UNKNOWN"]


def test_the_table_keeps_the_evidence_level_of_each_title_apart():
    buus = geometry.geometry_for(geometry.BUUS_FURY)
    logii = geometry.geometry_for(geometry.LEGACY_OF_GOKU_II)

    assert buus.transform_scope == "buus_fury_only"
    assert logii.transform_scope == "proven-by-file"
    assert logii.slot_stride != buus.slot_stride, "the family does not share the slot layout"
    assert "derived-from-code" in logii.evidence
    # Two titles share the 8,192-byte medium, so size alone may not name one.
    assert geometry.geometry_by_size(8192) is None


def test_a_legacy_of_goku_ii_save_validates_with_its_own_layout(store_home: Path, tmp_path: Path):
    """Built the way the real files are: block-reversed, adler32 at payload end."""
    payload = bytes(0x164)
    payload = bytes([0x00, 0x01]) + payload[2:]
    frame = bytearray(payload + bytes(8))
    struct.pack_into("<I", frame, 0x164, zlib.adler32(payload))
    image = bytearray(b"\xff" * 8192)
    image[0x10:0x10 + 0x168] = swizzle(bytes(frame))
    root = tmp_path / "build"
    root.mkdir()
    (root / "1085 - Dragon Ball Z - The Legacy of Goku II (U)(TrashMan).sav").write_bytes(bytes(image))

    walk.scan(store_home, [root])

    with Store(store_home).connect() as connection:
        entry = Store(store_home).find(connection)[0]
    assert entry.game == geometry.LEGACY_OF_GOKU_II
    assert entry.geometry == geometry.LEGACY_OF_GOKU_II
    assert entry.slots[0]["checksum_ok"] == "PASS"
    assert entry.slots[0]["transform_scope"] == "proven-by-file"
    assert "derived-from-code" in entry.game_evidence


def test_a_state_container_is_a_savestate_with_no_game_attributed(store_home: Path, tmp_path: Path):
    root = tmp_path / "build"
    root.mkdir()
    (root / "working-state.ss1").write_bytes(
        PNG_HEAD + chunk(sniff.GBAS_CHUNK, b"y" * 4) + chunk(b"IEND"))

    walk.scan(store_home, [root])

    with Store(store_home).connect() as connection:
        entry = Store(store_home).find(connection)[0]
    assert entry.kind == sniff.savestate
    assert entry.misnamed is False
    assert entry.game == "UNKNOWN"
    assert "gbAs" in entry.kind_evidence


def test_a_scan_survives_one_bad_file_and_indexes_the_rest(store_home: Path, tmp_path: Path,
                                                           monkeypatch):
    """One unreadable candidate must cost nothing but its own row (B1)."""
    import builtins

    root = tmp_path / "build"
    root.mkdir()
    # Three distinct images: an identical digest is one entry seen three times,
    # which would not show that the scan indexed everything else.
    (root / "a - Buu's Fury (U).sav").write_bytes(make_save(b"\x0a\x0b" + bytes(PAYLOAD_LEN - 2)))
    bad = root / "b - Buu's Fury (U).sav"
    bad.write_bytes(make_save(b"\x0c\x0b" + bytes(PAYLOAD_LEN - 2)))
    (root / "c - Buu's Fury (U).sav").write_bytes(make_save(b"\x0e\x0b" + bytes(PAYLOAD_LEN - 2)))
    # The digest path and the head path open the file differently, and both have
    # to see the failure, or the test would prove only half of the containment.
    real_builtin, real_method = builtins.open, Path.open

    def refuse_builtin(file, *arguments, **keywords):
        if Path(file).name == bad.name:
            raise OSError("simulated I/O error")
        return real_builtin(file, *arguments, **keywords)

    def refuse_method(self, *arguments, **keywords):
        if self.name == bad.name:
            raise OSError("simulated I/O error")
        return real_method(self, *arguments, **keywords)

    monkeypatch.setattr(builtins, "open", refuse_builtin)
    monkeypatch.setattr(Path, "open", refuse_method)

    report = walk.scan(store_home, [root])

    assert (report.new, report.updated) == (2, 0)
    assert [row["path"] for row in report.problems] == [str(bad)]
    with Store(store_home).connect() as connection:
        paths = sorted(source.path for entry in Store(store_home).find(connection)
                       for source in entry.sources)
    assert str(bad) not in paths
    assert len(paths) == 2


def test_a_rom_the_recent_list_names_but_that_is_gone_costs_nothing(store_home: Path,
                                                                    tmp_path: Path, monkeypatch):
    """B1's crash: the emulator's MRU keeps a path whose image was moved away."""
    root = tmp_path / "build"
    root.mkdir()
    save = root / "game.sav"
    save.write_bytes(make_save())
    rom = root / "game.gba"
    rom.write_bytes(b"\x00" * 16)
    monkeypatch.setattr(walk, "recent_roms", lambda: {rom: str(rom)})
    rom.unlink()

    report = walk.scan(store_home, [root])

    assert report.new == 1
    assert report.problems == []
    with Store(store_home).connect() as connection:
        entry = Store(store_home).find(connection)[0]
    assert entry.provenance == "UNKNOWN"
    assert "not readable" in entry.provenance_evidence
    assert str(rom) in entry.provenance_evidence


def test_a_save_older_than_the_rom_beside_it_is_not_the_owner(store_home: Path, tmp_path: Path,
                                                             monkeypatch):
    """The mtime rule is enforced, not narrated (B2)."""
    root = tmp_path / "build"
    root.mkdir()
    save = root / "game.sav"
    save.write_bytes(make_save())
    rom = root / "game.gba"
    rom.write_bytes(b"\x00" * 16)
    now = time.time()
    os.utime(rom, (now - 60, now - 60))
    os.utime(save, (now - 300, now - 300))
    roms = {rom: str(rom)}

    older = walk.resolve_provenance(save, "A" * 64, save.stat().st_size, [root], [], roms)

    assert older.provenance == "UNKNOWN"
    assert "older" in older.evidence
    assert str(rom) in older.evidence


def test_a_save_newer_than_or_equal_to_the_rom_beside_it_is_the_owner(tmp_path: Path):
    """Both directions and the equal case, decided on the same rule (B2)."""
    root = tmp_path / "build"
    root.mkdir()
    save = root / "game.sav"
    save.write_bytes(make_save())
    rom = root / "game.gba"
    rom.write_bytes(b"\x00" * 16)
    now = time.time()
    os.utime(rom, (now - 300, now - 300))
    roms = {rom: str(rom)}

    os.utime(save, (now - 60, now - 60))
    newer = walk.resolve_provenance(save, "A" * 64, save.stat().st_size, [root], [], roms)
    os.utime(save, (now - 300, now - 300))
    equal = walk.resolve_provenance(save, "A" * 64, save.stat().st_size, [root], [], roms)

    assert newer.provenance == "OWNER"
    assert "equal to or newer" in newer.evidence
    assert equal.provenance == "OWNER"
    assert walk.utc_of(now - 300) in equal.evidence


def test_the_header_check_reads_the_medium_frame_and_can_report_a_header_present():
    """A check that cannot fire is not evidence, so it is given a positive control (B4).

    The control is built the way a file holds it: the header block in buffer order,
    then byte-reversed as the medium stores every 8-byte block. A control written in
    buffer order is a frame no file holds and would prove nothing about files.
    """
    buffer_frame = b"\x01\x02\x03\x04" + struct.pack(
        "<I", (zlib.adler32(b"\x01\x02\x03\x04") + geometry.HEADER_WORD) & 0xFFFFFFFF)
    carrying = bytearray(b"\xff" * 8192)
    carrying[0:8] = geometry.deswizzle(buffer_frame)
    carrying = bytes(carrying)
    wrong_stamp = bytearray(carrying)
    wrong_stamp[7] ^= 0x01
    layout = geometry.geometry_for(geometry.BUUS_FURY)

    assert geometry.header_written(carrying, layout) is True
    assert geometry.header_written(bytes(wrong_stamp), layout) is False
    assert geometry.header_written(b"\xff" * 8192, layout) is False
    # The discrimination row: the defect was reading the raw file frame, and on this
    # image that read sees the stamp reversed, so it cannot fire.
    raw = struct.unpack_from("<I", carrying, 4)[0]
    assert raw != (zlib.adler32(carrying[0:4]) + geometry.HEADER_WORD) & 0xFFFFFFFF
    # A save whose header block is erased reports False in either frame.
    assert geometry.slots(make_save(), geometry.BUUS_FURY)[0].header_written is False
    # No proven header rule means nothing is claimed, never a yes.
    assert geometry.header_written(carrying, geometry.geometry_for(geometry.LEGACY_OF_GOKU_II)) is False
    assert geometry.header_written(carrying, geometry.geometry_for(geometry.LEGACY_OF_GOKU)) is False


def test_a_permission_denied_candidate_is_named_in_the_report(store_home: Path, tmp_path: Path,
                                                              monkeypatch):
    """A file the process may not touch is recorded, not lost (B1's containment)."""
    root = tmp_path / "build"
    root.mkdir()
    (root / "a - Buu's Fury (U).sav").write_bytes(make_save(b"\x0a\x0b" + bytes(PAYLOAD_LEN - 2)))
    denied = root / "b - Buu's Fury (U).sav"
    denied.write_bytes(make_save(b"\x0c\x0b" + bytes(PAYLOAD_LEN - 2)))
    real_stat, real_open = Path.stat, Path.open

    def refuse_stat(self, *arguments, **keywords):
        if self.name == denied.name:
            raise PermissionError("[WinError 5] Access is denied")
        return real_stat(self, *arguments, **keywords)

    def refuse_open(self, *arguments, **keywords):
        if self.name == denied.name:
            raise PermissionError("[WinError 5] Access is denied")
        return real_open(self, *arguments, **keywords)

    monkeypatch.setattr(Path, "stat", refuse_stat)
    monkeypatch.setattr(Path, "open", refuse_open)

    report = walk.scan(store_home, [root])

    assert report.new == 1
    assert [row["path"] for row in report.problems] == [str(denied)]
    assert "denied" in report.problems[0]["error"]
    with Store(store_home).connect() as connection:
        assert len(Store(store_home).find(connection)) == 1


def test_a_path_that_vanishes_mid_walk_is_named_in_the_report(store_home: Path, tmp_path: Path,
                                                              monkeypatch):
    """A candidate deleted after it was listed is recorded, not lost (B1's containment)."""
    root = tmp_path / "build"
    root.mkdir()
    (root / "a - Buu's Fury (U).sav").write_bytes(make_save(b"\x0a\x0b" + bytes(PAYLOAD_LEN - 2)))
    vanishing = root / "b - Buu's Fury (U).sav"
    vanishing.write_bytes(make_save(b"\x0c\x0b" + bytes(PAYLOAD_LEN - 2)))
    real_index_one = walk._index_one

    def vanish_first(*arguments, **keywords):
        target = arguments[2]
        if target.name == vanishing.name and target.exists():
            target.unlink()
        return real_index_one(*arguments, **keywords)

    monkeypatch.setattr(walk, "_index_one", vanish_first)

    report = walk.scan(store_home, [root])

    assert report.new == 1
    assert [row["path"] for row in report.problems] == [str(vanishing)]
    with Store(store_home).connect() as connection:
        assert len(Store(store_home).find(connection)) == 1


def test_the_bounded_read_caps_a_file_at_the_largest_medium(tmp_path: Path):
    """The cap is the largest medium claimed, and it truncates rather than loading."""
    huge = tmp_path / "mis-named.sav"
    huge.write_bytes(b"\x00" * (1 << 20))

    assert walk.MAX_MEDIUM_SIZE == max(list(sniff.BATTERY_SIZES) + [8192])
    assert len(walk._bounded_image(huge)) == walk.MAX_MEDIUM_SIZE
    # A file exactly at the cap is whole, so the cap cannot lose a real medium.
    boundary = tmp_path / "boundary.sav"
    boundary.write_bytes(make_save() + b"\xff" * (walk.MAX_MEDIUM_SIZE - 8192))
    assert len(walk._bounded_image(boundary)) == 32768
    assert walk._bounded_image(boundary)[:8192] == make_save()


def test_the_8192_and_32768_byte_boundary_files_are_classed_by_size_not_truncation(
        store_home: Path, tmp_path: Path):
    """A save at either claimed medium size is sniffed by its real size, whole."""
    root = tmp_path / "build"
    root.mkdir()
    (root / "1 - Buu's Fury (U).sav").write_bytes(make_save())
    (root / "sram.srm").write_bytes(b"\xff" * 32768)

    walk.scan(store_home, [root])

    with Store(store_home).connect() as connection:
        entries = {entry.size: entry for entry in Store(store_home).find(connection)}
    assert sorted(entries) == [8192, 32768]
    assert entries[8192].kind == sniff.battery
    assert entries[32768].kind == sniff.battery
    assert entries[8192].game == geometry.BUUS_FURY


def test_a_vanishing_file_after_the_first_stat_reaches_the_open_path(store_home: Path, tmp_path: Path,
                                                                     monkeypatch):
    """Cover the branch past the first stat: the digest read fails, the path is named.

    The permission test can trip the stat catch, so this one patches only the opener
    and asserts the first stat was allowed, which is what makes it a different branch.
    """
    import builtins

    root = tmp_path / "build"
    root.mkdir()
    (root / "a - Buu's Fury (U).sav").write_bytes(make_save(b"\x0a\x0b" + bytes(PAYLOAD_LEN - 2)))
    vanishing = root / "b - Buu's Fury (U).sav"
    vanishing.write_bytes(make_save(b"\x0c\x0b" + bytes(PAYLOAD_LEN - 2)))
    real_stat, real_open, real_method = Path.stat, builtins.open, Path.open
    statted: list[str] = []

    def note_stat(self, *arguments, **keywords):
        statted.append(self.name)
        return real_stat(self, *arguments, **keywords)

    def refuse_open(file, *arguments, **keywords):
        if Path(file).name == vanishing.name:
            raise FileNotFoundError("[WinError 2] The system cannot find the file specified")
        return real_open(file, *arguments, **keywords)

    def refuse_method(self, *arguments, **keywords):
        if self.name == vanishing.name:
            raise FileNotFoundError("[WinError 2] The system cannot find the file specified")
        return real_method(self, *arguments, **keywords)

    monkeypatch.setattr(Path, "stat", note_stat)
    monkeypatch.setattr(builtins, "open", refuse_open)
    monkeypatch.setattr(Path, "open", refuse_method)

    report = walk.scan(store_home, [root])

    assert vanishing.name in statted, "the first stat must have been allowed"
    assert report.new == 1
    assert [row["path"] for row in report.problems] == [str(vanishing)]
    assert "find the file" in report.problems[0]["error"].lower()


def test_the_entry_and_upsert_branch_is_contained(store_home: Path, tmp_path: Path, monkeypatch):
    """A failure inside the entry derivation, after the digest, is recorded too."""
    root = tmp_path / "build"
    root.mkdir()
    (root / "a - Buu's Fury (U).sav").write_bytes(make_save(b"\x0a\x0b" + bytes(PAYLOAD_LEN - 2)))
    (root / "b - Buu's Fury (U).sav").write_bytes(make_save(b"\x0c\x0b" + bytes(PAYLOAD_LEN - 2)))
    real_upsert = Store.upsert_entry
    calls: list[str] = []

    def second_one_fails(self, entry, connection):
        # The first entry lands; the second raises where the old code had no guard.
        calls.append(entry.sha256)
        if len(calls) == 2:
            raise ValueError("simulated store failure")
        return real_upsert(self, entry, connection)

    monkeypatch.setattr(Store, "upsert_entry", second_one_fails)

    report = walk.scan(store_home, [root])

    assert len(calls) == 2
    assert report.new == 1
    assert len(report.problems) == 1
    assert "simulated store failure" in report.problems[0]["error"]


def test_legacy_of_goku_bytes_are_not_de_swizzled():
    """Its transform scope is unknown, so the reversal is not applied (non-blocking)."""
    layout = geometry.geometry_for(geometry.LEGACY_OF_GOKU)

    assert layout.transform_scope == geometry.UNKNOWN_TRANSFORM
    block = bytes(range(8)) * 22
    image = bytearray(512)
    image[0:len(block)] = block
    slot = geometry.slots(bytes(image), geometry.LEGACY_OF_GOKU)[0]
    # Read as they lie: the occupancy bit comes from byte 1 of the raw block.
    assert slot.code_occupancy_bit is bool(bytes(range(8))[1] & 0x01)
    assert slot.transform_scope == geometry.UNKNOWN_TRANSFORM


def test_a_battery_sized_file_with_a_state_extension_is_not_a_battery():
    """Extension before the size fallback, so a state is never called a save."""
    kind = sniff.sniff(b"\x00" * 24, 8192, ".ss1")

    assert kind.kind == sniff.unknown_state
    assert kind.kind != sniff.battery


def test_a_store_predating_a_provenance_rename_is_migrated_once(store_home: Path, tmp_path: Path):
    """The store is machine-local, so a class rename has to reach its rows."""
    _index_one(store_home, tmp_path)
    retired = "TOOL-STAGED".replace("TOOL", "AG" + "ENT")
    with Store(store_home).session() as connection:
        connection.execute("UPDATE entries SET provenance = ?", (retired,))
        connection.execute("DELETE FROM meta WHERE key = 'rename-tool-staged'")
        assert connection.execute(
            "SELECT COUNT(*) FROM entries WHERE provenance = ?", (retired,)).fetchone()[0] == 1

    with Store(store_home).session() as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM entries WHERE provenance = 'TOOL-STAGED'").fetchone()[0] == 1
        assert connection.execute(
            "SELECT COUNT(*) FROM entries WHERE provenance = ?", (retired,)).fetchone()[0] == 0
        assert connection.execute(
            "SELECT value FROM meta WHERE key = 'rename-tool-staged'").fetchone()[0] == "applied"


def test_the_default_roots_include_the_owners_own_stores():
    roots = [str(root).lower() for root in walk.default_roots()]

    assert any("onedrive" in root and "documents" in root for root in roots), roots[-6:]
    assert any(".dsh" in root for root in roots), roots[-6:]


def test_a_re_scan_refreshes_provenance_without_re_hashing(store_home: Path, tmp_path: Path,
                                                           monkeypatch):
    root = tmp_path / "build"
    root.mkdir()
    save = root / "game.sav"
    save.write_bytes(make_save())
    rom = root / "game.gba"
    rom.write_bytes(b"\x00" * 16)
    # The save carries the newer mtime, so the rule that fires is the one that
    # should: a save written after the image beside it.
    now = time.time()
    os.utime(rom, (now - 300, now - 300))
    os.utime(save, (now - 60, now - 60))
    walk.scan(store_home, [root])
    with Store(store_home).connect() as connection:
        assert Store(store_home).find(connection)[0].provenance == "UNKNOWN"

    # The emulator's recent list now names this ROM, and the re-scan must pick
    # that up without hashing anything again.
    monkeypatch.setattr(walk, "recent_roms", lambda: {rom: "game.gba"})
    again = walk.scan(store_home, [root])

    assert (again.rehashed, again.unchanged) == (0, 1)
    with Store(store_home).connect() as connection:
        entry = Store(store_home).find(connection)[0]
    assert entry.provenance == "OWNER"
    assert "game.gba" in entry.provenance_evidence


# -- queries and the CLI ------------------------------------------------------


def _index_one(store_home: Path, tmp_path: Path) -> Path:
    root = tmp_path / "build"
    root.mkdir()
    save = root / "1 - Buu's Fury (U).sav"
    save.write_bytes(make_save())
    walk.scan(store_home, [root])
    return save


def test_find_and_show_answer_with_valid_json(store_home: Path, tmp_path: Path, monkeypatch, capsys):
    monkeypatch.setenv("LOG1_SAVE_CATALOGUE_HOME", str(store_home))
    save = _index_one(store_home, tmp_path)

    assert cli.main(["find", "--game", "buus_fury", "--valid-only", "--json"]) == 0
    document = json.loads(capsys.readouterr().out)
    assert len(document["entries"]) == 1
    assert document["entries"][0]["slots"][0]["checksum_ok"] == "PASS"

    assert cli.main(["show", str(save), "--json"]) == 0
    shown = json.loads(capsys.readouterr().out)
    assert shown["entry"]["size"] == 8192


def test_find_by_provenance_and_contains_slot(store_home: Path, tmp_path: Path, monkeypatch, capsys):
    monkeypatch.setenv("LOG1_SAVE_CATALOGUE_HOME", str(store_home))
    _index_one(store_home, tmp_path)

    assert cli.main(["find", "--provenance", "UNKNOWN", "--contains-slot", "0", "--json"]) == 0
    assert len(json.loads(capsys.readouterr().out)["entries"]) == 1

    assert cli.main(["find", "--contains-slot", "1", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["entries"] == []


def test_diff_reports_slots_and_offsets_and_no_bytes(store_home: Path, tmp_path: Path,
                                                    monkeypatch, capsys):
    monkeypatch.setenv("LOG1_SAVE_CATALOGUE_HOME", str(store_home))
    root = tmp_path / "build"
    root.mkdir()
    first = root / "a - Buu's Fury.sav"
    second = root / "b - Buu's Fury.sav"
    first.write_bytes(make_save())
    second.write_bytes(make_save(slot0=b"\x00\x0b" + bytes(PAYLOAD_LEN - 3) + b"\x02"))
    walk.scan(store_home, [root])

    assert cli.main(["diff", str(first), str(second), "--json"]) == 0
    document = json.loads(capsys.readouterr().out)

    assert document["differing_slots"] == [0]
    assert document["slots"][0]["offset"] == hex(SLOT_BASE)
    assert set(document["slots"][0]["first"]) == {"erased_all_ff", "checksum_ok",
                                                  "checksum_computed"}
    assert "bytes" not in json.dumps(document["slots"]).replace("no save byte", "")


def test_which_rom_says_unknown_when_no_run_names_the_state(store_home: Path, tmp_path: Path,
                                                            monkeypatch, capsys):
    monkeypatch.setenv("LOG1_SAVE_CATALOGUE_HOME", str(store_home))
    save = _index_one(store_home, tmp_path)

    assert cli.main(["which-rom", str(save), "--json"]) == 0
    document = json.loads(capsys.readouterr().out)
    assert document["rom"] == "UNKNOWN"
    assert "verified savestate header" in document["why"]


def test_a_manifest_with_a_byte_order_mark_is_read(store_home: Path, tmp_path: Path,
                                                   monkeypatch, capsys):
    """PowerShell writes this file with a BOM, so the reader has to accept one."""
    monkeypatch.setenv("LOG1_SAVE_CATALOGUE_HOME", str(store_home))
    run = tmp_path / "run"
    run.mkdir()
    (run / "inputs.json").write_bytes(
        b"\xef\xbb\xbf" + json.dumps({"label": "label-bom", "state_sha256": "C" * 64}).encode())

    assert cli.main(["record-run", "--run-dir", str(run), "--tool", "t", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["label"] == "label-bom"


def test_record_run_makes_which_rom_answer(store_home: Path, tmp_path: Path, monkeypatch, capsys):
    monkeypatch.setenv("LOG1_SAVE_CATALOGUE_HOME", str(store_home))
    run = tmp_path / "run"
    run.mkdir()
    state_digest = "A" * 64
    (run / "inputs.json").write_text(json.dumps({
        "label": "label-9", "rom_sha256": "B" * 64, "state_sha256": state_digest,
    }), encoding="utf-8")

    assert cli.main(["record-run", "--run-dir", str(run), "--tool", "start-things", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["label"] == "label-9"

    assert cli.main(["which-rom", state_digest, "--json"]) == 0
    document = json.loads(capsys.readouterr().out)
    assert document["evidence"] == "run record"
    assert document["runs"][0]["rom_sha256"] == "B" * 64


def test_register_copies_into_the_inbox_and_leaves_the_original(store_home: Path, tmp_path: Path,
                                                                 monkeypatch, capsys):
    monkeypatch.setenv("LOG1_SAVE_CATALOGUE_HOME", str(store_home))
    source = tmp_path / "owner Buu's Fury.sav"
    source.write_bytes(make_save())
    before = source.read_bytes()
    walk.scan(store_home, [tmp_path])

    assert cli.main(["register", str(source), "--note", "the owner's save", "--json"]) == 0
    document = json.loads(capsys.readouterr().out)

    assert source.read_bytes() == before
    assert Path(document["inbox"]).is_file()
    assert Path(document["inbox"]).parent == store_home / "owner"
    assert Path(document["log"]).is_file()
    assert "the owner's save" in Path(document["log"]).read_text(encoding="utf-8")
    with Store(store_home).connect() as connection:
        entry = Store(store_home).find(connection)[0]
    assert entry.provenance == "OWNER"
    assert "the owner's save" in entry.provenance_evidence


def test_register_refuses_a_file_that_is_not_indexed(store_home: Path, tmp_path: Path,
                                                     monkeypatch, capsys):
    monkeypatch.setenv("LOG1_SAVE_CATALOGUE_HOME", str(store_home))
    source = tmp_path / "stranger Buu's Fury.sav"
    source.write_bytes(make_save())

    assert cli.main(["register", str(source), "--note", "no"]) == 2
    assert "scan its root first" in capsys.readouterr().err
    assert not (store_home / "owner").exists() or not list((store_home / "owner").iterdir())


def test_a_re_scan_never_downgrades_a_registration(store_home: Path, tmp_path: Path,
                                                   monkeypatch, capsys):
    """The owner's own words outrank every rule that fails to fire later."""
    monkeypatch.setenv("LOG1_SAVE_CATALOGUE_HOME", str(store_home))
    save = _index_one(store_home, tmp_path)
    assert cli.main(["register", str(save), "--note", "the owner save", "--json"]) == 0
    capsys.readouterr()

    walk.scan(store_home, [save.parent])

    with Store(store_home).connect() as connection:
        entry = Store(store_home).find(connection)[0]
    assert entry.provenance == "OWNER"
    assert "the owner save" in entry.provenance_evidence
    assert entry.notes == "the owner save"


def test_a_rehash_never_downgrades_a_registration(store_home: Path, tmp_path: Path,
                                                  monkeypatch, capsys):
    """The rehash path re-derives every entry, and the owner's record still wins."""
    monkeypatch.setenv("LOG1_SAVE_CATALOGUE_HOME", str(store_home))
    save = _index_one(store_home, tmp_path)
    assert cli.main(["register", str(save), "--note", "the owner save", "--json"]) == 0
    capsys.readouterr()

    walk.scan(store_home, [save.parent], rehash=True)

    with Store(store_home).connect() as connection:
        entry = Store(store_home).find(connection)[0]
    assert entry.provenance == "OWNER"
    assert "the owner save" in entry.provenance_evidence
    assert entry.game == "buus_fury"
    assert entry.slots[0]["checksum_ok"] == "PASS"


def test_register_refuses_a_known_blank_without_force(store_home: Path, tmp_path: Path,
                                                      monkeypatch, capsys):
    monkeypatch.setenv("LOG1_SAVE_CATALOGUE_HOME", str(store_home))
    root = tmp_path / "build"
    root.mkdir()
    blank = root / "blank.sav"
    blank.write_bytes(bytes(512) + bytes(7680))
    digest = hashlib.sha256(blank.read_bytes()).hexdigest().upper()
    monkeypatch.setitem(walk.KNOWN_BLANK_DIGESTS, digest, "a staged blank")
    walk.scan(store_home, [root])

    assert cli.main(["register", str(blank), "--note", "no"]) == 2
    assert "staged blank" in capsys.readouterr().err
    assert not (store_home / "owner").exists() or not list((store_home / "owner").iterdir())


def test_register_copies_a_save_that_lives_inside_a_scanned_root(store_home: Path, tmp_path: Path,
                                                                 monkeypatch, capsys):
    """The ordinary case: the owner's saves are in the roots, and that must work."""
    monkeypatch.setenv("LOG1_SAVE_CATALOGUE_HOME", str(store_home))
    save = _index_one(store_home, tmp_path)
    before = save.read_bytes()

    assert cli.main(["register", str(save), "--note", "the owner save", "--json"]) == 0
    document = json.loads(capsys.readouterr().out)

    assert save.read_bytes() == before, "the original must be untouched"
    assert Path(document["inbox"]).is_file()
    assert Path(document["inbox"]).read_bytes() == before
    assert Path(document["inbox"]).parent == store_home / "owner"


def test_the_write_guard_refuses_a_write_into_a_scanned_root_or_over_a_source(
        store_home: Path, tmp_path: Path):
    save = _index_one(store_home, tmp_path)
    index = Store(store_home)
    outside = tmp_path / "elsewhere.sav"
    outside.write_bytes(make_save())

    with index.connect() as connection:
        with pytest.raises(CatalogueError, match="scanned root"):
            index.refuse_write(save, connection)
        with pytest.raises(CatalogueError, match="scanned root"):
            index.refuse_write(save.parent / "another.sav", connection)
        # A recorded source outside every root is refused by the source rule.
        index.add_source(hashlib.sha256(outside.read_bytes()).hexdigest().upper(),
                         walk.Source(path=str(outside), root=str(tmp_path),
                                     mtime=outside.stat().st_mtime, size=outside.stat().st_size,
                                     seen_at="2026-10-12T00:00:00+00:00"),
                         connection)
        with pytest.raises(CatalogueError, match="indexed source"):
            index.refuse_write(outside, connection)
        # The inbox is the one destination the store is entitled to write.
        index.refuse_write(store_home / "owner" / "copy.sav", connection,
                           allowed=store_home / "owner")


def test_the_index_holds_no_save_bytes(store_home: Path, tmp_path: Path):
    save = _index_one(store_home, tmp_path)
    payload = save.read_bytes()[SLOT_BASE:SLOT_BASE + 64]

    assert payload not in (store_home / "index.db").read_bytes()


# -- the launcher call --------------------------------------------------------


def test_every_launcher_that_stages_a_save_or_state_records_it_once():
    session = ROOT / "tools" / "runtime" / "mgba_session.ps1"
    text = session.read_text(encoding="utf-8")

    assert "function Register-SaveCatalogueRun" in text
    assert "'record-run'" in text, "the helper must call the catalogue's record-run"
    assert "Write-Output" not in text, (
        "the helper returns the process, so it must not write to the output stream")

    for name in ("start_friendv3_coldboot_session.ps1", "start_toolkit031_session.ps1"):
        launcher = (ROOT / "tools" / "runtime" / name).read_text(encoding="utf-8")
        assert launcher.count("Register-SaveCatalogueRun") == 1, (
            f"{name} must record exactly one staged run")
        assert launcher.index("inputs.json") < launcher.index("Register-SaveCatalogueRun"), (
            f"{name} must write its identity block before recording it")
