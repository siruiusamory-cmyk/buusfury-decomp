"""ROM-gated proof that the authored compressed dialogue relocates as one payload."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tools.webfoot.build import build_project, extract_project, validate_project
from tools.webfoot.binary import FileOffset
from tools.webfoot.compressed_dialogue import (CompressedDialogueTarget,
                                                materialize_dialogues,
                                                plan_replacement)
from tools.webfoot.layout import RomRange
from tools.webfoot.formats.webfoot_lz import unpack
from tools.webfoot.dialogue import (get_dialogue_original,
                                    resolve_dialogue_target,
                                    set_dialogue_replacement)
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.write import apply_plan


ROM = Path("roms/Dragon Ball Z - Buu's Fury (U).gba")
SHA = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
TARGET = CompressedDialogueTarget("goku-greeting", 1, 0x7B5B64, 0x02002641, 0x132, 0x20)


def test_authored_compressed_dialogue_overflow_relocates_to_generated_expansion():
    if not ROM.is_file() or hashlib.sha256(ROM.read_bytes()).hexdigest() != SHA:
        pytest.skip("canonical Buu ROM is not available")
    profile = RomProfileCatalog.load("config/roms.yaml").profiles[0]
    canonical = ROM.read_bytes()
    result = plan_replacement(canonical, profile, TARGET, "Nice work, Goku!")
    assert result.old_allocation == 16856
    assert len(result.payload) == 17932
    assert result.allocation is not None
    assert result.allocation.range.start.value == 0x800000
    output = apply_plan(canonical, result.plan)
    assert len(output) == 0x1000000
    assert output[:0x800000] == canonical[:0x7B5B68] + (0x08800000).to_bytes(4, "little") + canonical[0x7B5B6C:]
    assert unpack(output, 0x800000).data[0x132:0x152] == "Nice work, Goku!".encode("utf-16le")
    assert all(output[offset:offset + 4] == canonical[offset:offset + 4]
               for offset in (0x781C4C, 0x781CB0, 0x781CFC))


def test_normal_project_build_materializes_semantic_dialogue_target(tmp_path):
    if not ROM.is_file() or hashlib.sha256(ROM.read_bytes()).hexdigest() != SHA:
        pytest.skip("canonical Buu ROM is not available")
    catalog = RomProfileCatalog.load("config/roms.yaml")
    profile = catalog.profiles[0]
    before_hash = hashlib.sha256(ROM.read_bytes()).hexdigest()
    project = tmp_path / "project"
    extract_project(ROM, project, catalog, graphics=False)
    target = resolve_dialogue_target(
        {"source": "decoded-container-text",
         "identity": {"packed_handle": "0x02002641"}},
        profile,
    )
    assert target is not None and target.name == "goku-greeting"
    assert get_dialogue_original(ROM.read_bytes(), profile, target) == "Good luck, Goku!"
    set_dialogue_replacement(project, profile, target, "Nice work, Goku!")
    assert validate_project(project, ROM, catalog).passed
    output = tmp_path / "authored.gba"
    manifest = tmp_path / "authored.json"
    result = build_project(project, ROM, output, catalog, manifest_path=manifest)
    assert output.stat().st_size == 0x1000000
    assert hashlib.sha256(output.read_bytes()).hexdigest() == (
        "3ccbef45940e8f5c27d3f88839639eb04d9cc50f8d942f18bc850872628724cb"
    )
    assert result.manifest.generated_allocations[0].resource == "goku-greeting"
    provenance = result.manifest.generated_allocations[0]
    assert provenance.domain == "compressed_dialogue"
    assert provenance.owner == "compressed-dialogue:goku-greeting"
    assert provenance.source_range.start.value == 0x7A04F0
    assert provenance.allocated_range.start.value == 0x800000
    assert provenance.allocated_rom_address == 0x08800000
    assert provenance.pointer_offset == 0x7B5B68
    generated = output.read_bytes()
    assert unpack(generated, 0x800000).data[0x132:0x152] == "Nice work, Goku!".encode("utf-16le")
    assert all(generated[offset:offset + 4] == ROM.read_bytes()[offset:offset + 4]
               for offset in (0x781C4C, 0x781CB0, 0x781CFC))
    assert hashlib.sha256(ROM.read_bytes()).hexdigest() == before_hash == SHA
    document = json.loads(manifest.read_text(encoding="utf-8"))
    allocation = document["generated_allocations"][0]
    assert allocation["allocation_class"] == "generated_expansion"
    assert allocation["domain"] == "compressed_dialogue"
    assert allocation["resource"] == "goku-greeting"
    assert allocation["source_range"]["file_offset"] == 0x7A04F0
    assert allocation["allocated_range"]["file_offset"] == 0x800000
    assert allocation["pointer_offset"] == 0x7B5B68


def test_build_project_passes_earlier_domain_reservations_to_dialogue(tmp_path, monkeypatch):
    """A prior build domain's issued span makes dialogue choose the next span."""
    if not ROM.is_file() or hashlib.sha256(ROM.read_bytes()).hexdigest() != SHA:
        pytest.skip("canonical Buu ROM is not available")
    import tools.webfoot.authored_placements as authored_placements

    issued = RomRange(FileOffset(0x800000), 0x100)

    def reserve_expansion_prefix(project, maps, document_factory, reserved=()):
        assert reserved == ()
        return [], frozenset(), (issued,)

    monkeypatch.setattr(authored_placements, "materialize_for_build", reserve_expansion_prefix)
    catalog = RomProfileCatalog.load("config/roms.yaml")
    profile = catalog.profiles[0]
    project = tmp_path / "project"
    extract_project(ROM, project, catalog, graphics=False)
    target = resolve_dialogue_target(
        {"source": "decoded-container-text",
         "identity": {"packed_handle": "0x02002641"}},
        profile,
    )
    set_dialogue_replacement(project, profile, target, "Nice work, Goku!")
    result = build_project(project, ROM, tmp_path / "authored.gba", catalog)
    allocation = result.manifest.generated_allocations[0]
    assert allocation.allocated_range.start.value == 0x800100
    assert allocation.allocated_rom_address == 0x08800100


def test_dialogue_respects_an_earlier_shared_expansion_reservation():
    if not ROM.is_file() or hashlib.sha256(ROM.read_bytes()).hexdigest() != SHA:
        pytest.skip("canonical Buu ROM is not available")
    profile = RomProfileCatalog.load("config/roms.yaml").profiles[0]
    # This is the allocator-issued span returned by an earlier build domain.
    # Dialogue receives it through build_project's one `reserved` set.
    result, reserved, _, provenance = materialize_dialogues(
        ROM.read_bytes(), profile, {"goku-greeting": "Nice work, Goku!"},
        reserved=(RomRange(FileOffset(0x800000), 0x100),),
    )
    assert result[0].allocation is not None
    assert result[0].allocation.range.start.value == 0x800100
    assert reserved == (result[0].allocation.range,)
    assert provenance[0].allocated_range.start.value == 0x800100
