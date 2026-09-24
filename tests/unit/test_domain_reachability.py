"""ROM-CAPACITY-AND-ALLOCATION-001 addendum: the reachable-capacity map.

Portable. These pin the properties that make the map trustworthy rather than the
numbers themselves, because the numbers come from Checkpoint A's cited evidence
and will move only when that evidence does:

* all sixteen Checkpoint A domains are represented, none invented;
* the three reachability levels cannot be collapsed - a value that is only
  encodable can never be recorded as runtime-proven;
* exactly one domain is runtime-proven above EOF, and it is the one Checkpoint D
  actually ran;
* the report's tables are the module's own output, so a figure cannot drift
  between the document and the data.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from tools.research.domain_reachability import (CANONICAL_VERIFIED_FREE, DOMAINS,
                                                GBA_ROM_BASE, MARKER_BEGIN, MARKER_END,
                                                PROVEN_GENERATED_SIZE, ProofLevel,
                                                StructuralClass, checkpoints,
                                                markdown_table, validate)

REPORT = Path("docs/research/ROM_CAPACITY_AND_ALLOCATION.md")


def test_the_map_covers_the_whole_checkpoint_a_inventory():
    validate()
    assert len(DOMAINS) == 16
    keys = [domain.key for domain in DOMAINS]
    assert len(set(keys)) == 16
    # The Checkpoint A inventory, verbatim: no domain added and none dropped.
    assert set(keys) == {
        "generic_rom_pointer", "compressed_dialogue_selector",
        "map_entry_scripts_pointer", "map_entry_variation_array",
        "map_entry_other_pointers", "placement_run", "map_slot_arrays",
        "placement_records", "text_table", "script_bodies", "actor_sprite_chain",
        "map_graphics", "palettes", "stat_tables", "relocation_families",
        "packed_text_handle"}
    assert all(domain.evidence for domain in DOMAINS), "every row cites evidence"


def test_exactly_one_domain_is_runtime_proven_and_it_is_the_one_we_ran():
    runtime = [d for d in DOMAINS if d.proof_level is ProofLevel.RUNTIME]
    assert [d.key for d in runtime] == ["compressed_dialogue_selector"]
    proven, = runtime
    assert proven.runtime_min_offset == 0x00800000
    assert proven.runtime_max_offset == 0x00800000 + 17932 - 1
    assert proven.expanded_runtime_bytes == 17932


def test_no_domain_records_a_theoretical_maximum_as_runtime_proven():
    """The addendum's central prohibition, enforced rather than trusted."""
    for domain in DOMAINS:
        if domain.engine_static_max_offset is None:
            assert domain.proof_level is not ProofLevel.ENGINE_STATIC, domain.key
        if domain.runtime_max_offset is None:
            assert domain.proof_level is not ProofLevel.RUNTIME, domain.key
        if domain.encoding_max_offset is not None and domain.runtime_max_offset:
            assert domain.runtime_max_offset <= domain.encoding_max_offset
    # Nothing claims the whole window.
    assert all((d.runtime_max_offset or 0) < 0x02000000 for d in DOMAINS)


def test_the_level_ordering_is_enforced_not_merely_documented():
    encodable, = [d for d in DOMAINS if d.key == "compressed_dialogue_selector"]
    # A runtime offset beyond what the format can encode is refused.
    with pytest.raises(ValueError, match="exceeds what the format encodes"):
        validate(tuple(replace(d, runtime_max_offset=0x03000000)
                       if d.key == encodable.key else d for d in DOMAINS))
    # A runtime offset beyond a stated static bound is refused.
    bounded = tuple(replace(d, engine_static_max_offset=0x00801000)
                    if d.key == encodable.key else d for d in DOMAINS)
    with pytest.raises(ValueError, match="exceeds the static bound"):
        validate(bounded)
    # A second runtime-proven domain is refused.
    with pytest.raises(ValueError, match="exactly one domain is runtime-proven"):
        validate(tuple(replace(d, runtime_min_offset=0x00800000,
                               runtime_max_offset=0x008000FF,
                               expanded_runtime_bytes=256)
                       if d.key == "text_table" else d for d in DOMAINS))


def test_domains_with_no_address_reach_say_so_instead_of_guessing():
    for key in ("palettes", "stat_tables"):
        domain = next(d for d in DOMAINS if d.key == key)
        assert domain.encoding_max_offset is None
        assert domain.proof_level is ProofLevel.NONE
        assert domain.canonical_reachable_bytes == 0
        assert domain.expanded_encodable_bytes == 0
    handle = next(d for d in DOMAINS if d.key == "packed_text_handle")
    assert handle.encoding_max_offset is None
    assert handle.proof_level is ProofLevel.NONE
    assert "not itself an above-EOF carrier" in handle.notes


def test_structural_limits_stay_visible_wherever_bytes_are_plentiful():
    """A domain can have reachable bytes and still be unable to add anything."""
    dialogue = next(d for d in DOMAINS if d.key == "compressed_dialogue_selector")
    assert dialogue.expanded_encodable_bytes > 8_000_000
    assert dialogue.structural_class is StructuralClass.FIXED
    assert "7" in dialogue.structural_limit
    assert "selector table" in dialogue.bottleneck
    text = next(d for d in DOMAINS if d.key == "text_table")
    assert text.structural_class is StructuralClass.THEORETICALLY_WIDENABLE
    assert "1,535" in text.bottleneck


def test_the_headline_numbers():
    facts = checkpoints()
    assert facts["domains"] == 16
    assert facts["raw_physical_expanded_bytes"] == 8_388_608
    assert facts["canonical_verified_free_bytes"] == CANONICAL_VERIFIED_FREE == 256
    assert facts["proven_generated_size"] == PROVEN_GENERATED_SIZE == 16_777_216
    assert len(facts["domains_encoding_capable_above_eof"]) == 13
    assert facts["domains_engine_static_capable_above_eof"] == []
    assert facts["domains_runtime_proven_above_eof"] == ["compressed_dialogue_selector"]
    assert facts["allocator_expanded_default_domains"] == ["compressed_dialogue_selector"]
    assert facts["runtime_proven_address_range"] == [GBA_ROM_BASE + 0x800000,
                                                     GBA_ROM_BASE + 0x800000 + 17931]


def test_the_report_embeds_this_module_s_own_tables():
    """The document and the data cannot drift apart."""
    text = REPORT.read_text(encoding="utf-8")
    assert MARKER_BEGIN in text and MARKER_END in text
    embedded = text.split(MARKER_BEGIN, 1)[1].split(MARKER_END, 1)[0]
    generated = markdown_table().split(MARKER_BEGIN, 1)[1].split(MARKER_END, 1)[0]
    assert embedded.strip() == generated.strip()
    for domain in DOMAINS:
        assert domain.title in embedded, domain.key
