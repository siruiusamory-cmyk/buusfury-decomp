"""ROM-gated proof of DIALOGUE-VARIABLE-LENGTH-001 through the production path.

This is the deterministic half of the ticket: the acceptance string is authored
into the real Buu's Fury image by the shipping build (`extract_project`,
`resolve_dialogue_target`, `set_dialogue_replacement`, `build_project`), and the
derivative is then read back and checked for every property the ticket names -
the re-authored handle, the container re-layout, the complete reference update,
the untouched unrelated words, the surviving neighbours, the allocator's
placement, the manifest's provenance, and a reopen that still resolves the same
semantic record.

The runtime half (mGBA displaying the whole line) is recorded separately in
`docs/research/ROM_DIALOGUE_VARIABLE_LENGTH.md`; this file pins the derivative
digest that run must reproduce.

Nothing ROM-derived is committed. The only quoted text is the ticket's own
authored line; neighbouring dialogue is compared image-to-image, never written
down.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tools.webfoot.build import build_project, extract_project, validate_project
from tools.webfoot.compressed_dialogue import (read_container_layout,
                                               target_named)
from tools.webfoot.dialogue import (get_dialogue_original, resolve_dialogue_target,
                                    set_dialogue_replacement)
from tools.webfoot.formats.webfoot_lz import unpack
from tools.webfoot.handles import DialogueHandle, recover_handle
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.project import read_project


ROM = Path("roms/Dragon Ball Z - Buu's Fury (U).gba")
SHA = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"

ACCEPTANCE = "Hot take: SSJ3 is the worst form imo"
RESOURCE = "goku-greeting"
RETAIL_LINE = "Good luck, Goku!"
OLD_HANDLE = 0x02002641
NEW_HANDLE = 0x04802641
DECODED_START = 0x132
OLD_DECODED_LENGTH = 32
NEW_DECODED_LENGTH = 72
DISPLACEMENT = NEW_DECODED_LENGTH - OLD_DECODED_LENGTH
SELECTOR = 1
SELECTOR_TABLE = 0x7B5B64
SELECTOR_SLOT = SELECTOR_TABLE + SELECTOR * 4
RETAINED_SHELF = 0x7A04F0
RETAIL_ALLOCATION = 16856
#: The twelve superseded handles that also occur, word-aligned, in ROM words the
#: engine never reads as handles. Measured on the canonical image: five distinct
#: values, fifteen sites, every one of them data. They are the M4 control.
UNRELATED_EQUAL_WORDS = (0x733E04, 0x20E4D0, 0x2C994C, 0x312E9C)

#: The digest the production path produces for this one authored substitution.
#: The runtime artifact must reproduce it byte for byte.
DERIVATIVE_SHA256 = "dbeba9abc58db5343bd4a7c004207636c8fa6932b0f9527a866fe09ee2aba036"


def canonical_rom() -> bytes:
    if not ROM.is_file() or hashlib.sha256(ROM.read_bytes()).hexdigest() != SHA:
        pytest.skip("canonical Buu ROM is not available")
    return ROM.read_bytes()


@pytest.fixture(scope="module")
def authored(tmp_path_factory):
    """One real build of the acceptance edit, reused by every assertion."""
    canonical = canonical_rom()
    catalog = RomProfileCatalog.load("config/roms.yaml")
    profile = catalog.profiles[0]
    root = tmp_path_factory.mktemp("dialogue-varlen")
    project = root / "project"
    extract_project(ROM, project, catalog, graphics=False)
    target = resolve_dialogue_target(
        {"source": "decoded-container-text",
         "identity": {"packed_handle": f"0x{OLD_HANDLE:08X}"}}, profile)
    assert target is not None and target.name == RESOURCE
    set_dialogue_replacement(project, profile, target, ACCEPTANCE, canonical)
    assert validate_project(project, ROM, catalog).passed

    output = root / "authored.gba"
    result = build_project(project, ROM, output, catalog)
    generated = output.read_bytes()
    return {
        "canonical": canonical, "profile": profile, "project": project,
        "target": target, "output": output, "generated": generated, "result": result,
        "layout": read_container_layout(canonical, profile, target),
        "after": read_container_layout(generated, profile, target),
    }


# --- the acceptance string really is longer, and really encodes to 72 bytes ----


def test_the_authored_line_is_not_the_retail_line_and_encodes_to_72_bytes(authored):
    encoded = ACCEPTANCE.encode("utf-16le")
    assert len(ACCEPTANCE) == 36
    assert len(encoded) == NEW_DECODED_LENGTH
    assert len(RETAIL_LINE.encode("utf-16le")) == OLD_DECODED_LENGTH
    assert get_dialogue_original(authored["canonical"], authored["profile"],
                                 authored["target"]) == RETAIL_LINE


# --- the durable handle was authored, not preserved ---------------------------


def test_the_durable_handle_is_re_derived_from_semantic_fields(authored):
    edit, = authored["result"].manifest.dialogue_edits
    assert edit.resource == RESOURCE
    assert edit.old_handle == OLD_HANDLE
    assert edit.new_handle == NEW_HANDLE
    assert DialogueHandle.decode(NEW_HANDLE) == DialogueHandle(
        SELECTOR, DECODED_START, NEW_DECODED_LENGTH)
    assert edit.old_decoded_length == OLD_DECODED_LENGTH
    assert edit.new_decoded_length == NEW_DECODED_LENGTH
    # The anchor holds: the record is replaced in place, so the semantic identity
    # that survives the edit is the record's own decoded start.
    assert edit.old_decoded_start == edit.new_decoded_start == DECODED_START


def test_every_true_reference_is_repointed_and_no_other_word_is(authored):
    canonical, generated = authored["canonical"], authored["generated"]
    edit, = authored["result"].manifest.dialogue_edits

    target_record = next(record for record in authored["layout"].records
                         if record.handle == DialogueHandle(
                             SELECTOR, DECODED_START, OLD_DECODED_LENGTH))
    assert len(target_record.sites) == 3
    for site in target_record.sites:
        assert canonical[site:site + 4] != generated[site:site + 4]
        assert int.from_bytes(generated[site:site + 4], "little") == NEW_HANDLE

    assert edit.reference_site_count == 3 + sum(
        len(record.sites) for record in authored["layout"].records
        if record.handle.decoded_start >= DECODED_START + OLD_DECODED_LENGTH)

    # No carrier site still names a superseded handle.
    for record in authored["layout"].records:
        if record.handle.decoded_start < DECODED_START + OLD_DECODED_LENGTH:
            continue
        new_start = record.handle.decoded_start + DISPLACEMENT
        expected = record.handle.replace(decoded_start=new_start).encode()
        for site in record.sites:
            assert int.from_bytes(generated[site:site + 4], "little") == expected, hex(site)

    # And the words that merely EQUAL a superseded handle are untouched (M4).
    for site in UNRELATED_EQUAL_WORDS:
        assert canonical[site:site + 4] == generated[site:site + 4], hex(site)


# --- the container was re-laid out, and the neighbours survived ---------------


def test_the_container_grew_by_exactly_the_text_delta(authored):
    before, after = authored["layout"], authored["after"]
    assert len(before.decoded) + DISPLACEMENT == len(after.decoded)
    assert len(before.records) == len(after.records)
    assert before.decoded[:DECODED_START] == after.decoded[:DECODED_START]
    assert after.decoded[DECODED_START:DECODED_START + NEW_DECODED_LENGTH] \
        == ACCEPTANCE.encode("utf-16le")


def test_every_other_record_still_decodes_to_its_own_bytes(authored):
    """The neighbour invariant, over all 447 records of the real container."""
    before, after = authored["layout"], authored["after"]
    edited = DialogueHandle(SELECTOR, DECODED_START, OLD_DECODED_LENGTH)
    by_span = {(record.handle.decoded_start, record.handle.decoded_length): record
               for record in after.records}
    compared = 0
    for record in before.records:
        if record.handle == edited:
            continue
        start = record.handle.decoded_start
        if start >= DECODED_START + OLD_DECODED_LENGTH:
            start += DISPLACEMENT
        landed = by_span[(start, record.handle.decoded_length)]
        assert landed.handle.decoded_start == start
        expected = before.decoded[record.handle.decoded_start:record.handle.decoded_end]
        actual = after.decoded[landed.handle.decoded_start:landed.handle.decoded_end]
        assert actual == expected, hex(record.raw_handle)
        compared += 1
    assert compared == len(before.records) - 1 == 446


def test_the_record_that_followed_the_greeting_moved_by_the_displacement(authored):
    """A named semantic control for the neighbour, not just a byte comparison."""
    def record_at(layout, start):
        return next(record for record in layout.records
                    if record.handle.decoded_start == start
                    and record.handle.decoded_length == 0x0A0)

    before = record_at(authored["layout"], 0x152)
    after = record_at(authored["after"], 0x152 + DISPLACEMENT)
    assert before.handle.encode() == 0x0A002A41
    assert after.handle.encode() == 0x0A002F41
    assert authored["layout"].decoded[0x152:0x1F2] \
        == authored["after"].decoded[0x152 + DISPLACEMENT:0x1F2 + DISPLACEMENT]
    assert authored["canonical"][before.sites[0]:before.sites[0] + 4] \
        != authored["generated"][before.sites[0]:before.sites[0] + 4]


# --- packed stream, allocation, pointer ---------------------------------------


def test_the_packed_container_is_rebuilt_and_relocated_by_the_allocator(authored):
    result = authored["result"]
    edit, = result.manifest.dialogue_edits
    assert edit.old_packed_size == RETAIL_ALLOCATION
    assert edit.new_packed_size == len(_payload_of(authored))
    assert edit.new_packed_size > RETAIL_ALLOCATION
    allocation, = result.manifest.generated_allocations
    assert allocation.domain == "compressed_dialogue"
    assert allocation.owner == f"compressed-dialogue:{RESOURCE}"
    assert allocation.allocated_range.start.value >= 0x800000
    assert allocation.allocated_range.size == edit.new_packed_size
    assert edit.pointer_moved is True
    assert edit.container_pointer_offset == SELECTOR_SLOT
    assert edit.container_pointer_address == allocation.allocated_rom_address
    assert allocation.source_range.start.value == RETAINED_SHELF
    # The engine-visible selector word is the allocator's address, and the other
    # six table words are untouched.
    generated, canonical = authored["generated"], authored["canonical"]
    assert generated[SELECTOR_SLOT:SELECTOR_SLOT + 4] \
        == allocation.allocated_rom_address.to_bytes(4, "little")
    for slot in range(SELECTOR_TABLE, SELECTOR_TABLE + 28, 4):
        if slot != SELECTOR_SLOT:
            assert generated[slot:slot + 4] == canonical[slot:slot + 4], hex(slot)


def _payload_of(authored) -> bytes:
    allocation, = authored["result"].manifest.generated_allocations
    return authored["generated"][allocation.allocated_range.start.value:
                                allocation.allocated_range.end]


def test_the_relocated_payload_satisfies_the_retail_termination_contract(authored):
    from tools.webfoot.formats.webfoot_lz import validate_retail_termination

    payload = _payload_of(authored)
    container = validate_retail_termination(payload)
    assert container.data[DECODED_START:DECODED_START + NEW_DECODED_LENGTH] \
        == ACCEPTANCE.encode("utf-16le")


def test_the_manifest_records_the_dialogue_edit(authored):
    result = authored["result"]
    assert result.manifest_path is not None
    document = json.loads(Path(result.manifest_path).read_text(encoding="utf-8"))
    entry, = document["dialogue_edits"]
    assert entry["resource"] == RESOURCE
    assert entry["old_handle"] == f"0x{OLD_HANDLE:08X}"
    assert entry["new_handle"] == f"0x{NEW_HANDLE:08X}"
    assert entry["old_decoded_length"] == OLD_DECODED_LENGTH
    assert entry["new_decoded_length"] == NEW_DECODED_LENGTH
    assert entry["decoded_length_delta"] == DISPLACEMENT
    assert entry["affected_record_count"] == 443
    assert entry["affected_handle_count"] == 443
    assert entry["old_packed_size"] == RETAIL_ALLOCATION
    assert entry["packed_size_delta"] == entry["new_packed_size"] - RETAIL_ALLOCATION
    assert entry["container_pointer_offset_hex"] == "0x7B5B68"
    assert entry["pointer_moved"] is True
    assert document["base"]["sha256"] == SHA
    assert document["output"]["sha256"] == hashlib.sha256(
        authored["generated"]).hexdigest()


# --- reopen -------------------------------------------------------------------


def test_the_derivative_reopens_as_the_same_semantic_record(authored):
    """Section 10: the authored record survives its own handle change.

    The Atlas path recovers whatever handle the image now holds, which is the
    re-authored one; resolution has to map that back to `goku-greeting` without
    an "old handle not found" failure and without inventing a second entry.
    """
    profile = authored["profile"]
    generated = authored["generated"]
    recovered = recover_handle(generated, SELECTOR, DECODED_START, NEW_DECODED_LENGTH)
    assert recovered["packed_handle"] == f"0x{NEW_HANDLE:08X}"
    assert recovered["handle_decoded_start"] == f"0x{DECODED_START:X}"
    assert recovered["handle_decoded_length"] == f"0x{NEW_DECODED_LENGTH:X}"

    reopened = resolve_dialogue_target(
        {"source": "decoded-container-text", "text": ACCEPTANCE,
         "identity": recovered}, profile)
    assert reopened is not None and reopened.name == RESOURCE

    # The record reads back through its CURRENT handle, not the retail one.
    assert get_dialogue_original(generated, profile, authored["target"]) == ACCEPTANCE
    # One semantic entry, and no phantom keyed on the new handle.
    dialogues = read_project(authored["project"]).dialogues
    assert dialogues == {RESOURCE: ACCEPTANCE}
    assert all(f"0x{NEW_HANDLE:08X}" not in key for key in dialogues)


def test_the_derivative_is_deterministic_and_the_canonical_rom_is_untouched(authored):
    digest = hashlib.sha256(authored["generated"]).hexdigest()
    if DERIVATIVE_SHA256 != "PENDING":
        assert digest == DERIVATIVE_SHA256
    assert len(authored["generated"]) == 0x1000000
    assert hashlib.sha256(ROM.read_bytes()).hexdigest() == SHA
    assert authored["output"] != ROM


def test_the_container_inventory_is_unchanged_apart_from_the_edited_record(authored):
    before = {record.raw_handle for record in authored["layout"].records}
    after = {record.raw_handle for record in authored["after"].records}
    assert len(before) == len(after) == 447
    assert OLD_HANDLE in before and OLD_HANDLE not in after
    assert NEW_HANDLE in after and NEW_HANDLE not in before
    # Every displaced handle differs from its predecessor by exactly the shift.
    for record in authored["layout"].records:
        if record.handle.decoded_start < DECODED_START + OLD_DECODED_LENGTH:
            continue
        moved = record.handle.replace(
            decoded_start=record.handle.decoded_start + DISPLACEMENT)
        assert moved.encode() in after
