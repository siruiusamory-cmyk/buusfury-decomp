"""TOOLKIT-003 synthetic proofs. No commercial bytes or private inputs."""

from dataclasses import replace
import hashlib
import json
from itertools import permutations

import pytest

from tools.webfoot.allocation import (AllocationKind, AllocationRequest,
                                      InsufficientSpaceError, allocate)
from tools.webfoot.binary import BinaryAddressError, FileOffset, GbaRomAddress
from tools.webfoot.document import RomDocument, scan_pointer_candidates
from tools.webfoot.layout import (Anchor, AnchorId, LayoutError, OwnedRegion, Provenance,
    Reference, ReferenceClass as RC, ReferenceEncoding as RE, RomRange,
    RELOCATION_ELIGIBLE_KINDS, relocation_eligible)
from tools.webfoot.profile import ProfileConfigError, RomProfile
from tools.webfoot.relocation import (CandidateReferenceError, RelocationRequest,
                                      emit_relocation, plan_relocation)
from tools.webfoot import write

#: The allocator now requires a semantic kind on every request. These cases drive
#: it through the relocation document, whose only relocatable anchor kind is the
#: placement reference array, so that is the kind they state. Nothing else about
#: the cases changed.
KIND = AllocationKind.PLACEMENT_REFERENCE_ARRAY


ID = AnchorId("fixture:payload")
PAYLOAD = b"synthetic payload grew from eight bytes"


def span(start, size):
    return RomRange(FileOffset(start), size)


@pytest.fixture
def document():
    image = bytearray(1024)
    image[0xA0:0xAC] = b"SYNTHETIC   "
    image[0xAC:0xB0] = b"TEST"
    image[0xB0:0xB2] = b"00"
    image[0xB2] = 0x96
    image[0xBD] = (-(sum(image[0xA0:0xBD]) + 0x19)) & 255
    image[0x100:0x108] = b"old-data"
    image[0xC0:0xC4] = (0x08000100).to_bytes(4, "little")
    image[0xC4:0xC8] = (0x104 - 0xC4).to_bytes(4, "little", signed=True)
    profile = RomProfile.from_mapping({
        "id": "synthetic-v1", "game": "synthetic", "region": "test",
        "revision": 0, "game_code": "TEST", "size": len(image),
        "sha256": hashlib.sha256(image).hexdigest(),
        "free_regions": [{"file_offset": 0x201, "size": 0xFF,
            "status": "CONFIRMED", "evidence": "synthetic fixture construction"}],
    })
    provenance = Provenance(profile.id, profile.sha256, "synthetic verified layout contract")
    anchor = Anchor(ID, span(0x100, 8), "opaque-test", "fixture:owner", 8, True, provenance)
    refs = (
        Reference(FileOffset(0xC0), ID, 0, RE.ABSOLUTE_ROM_U32_LE, RC.DECLARED_REFERENCE, provenance),
        Reference(FileOffset(0xC4), ID, 4, RE.RELATIVE_I32_LE, RC.CONFIRMED_REFERENCE, provenance),
    )
    return RomDocument.from_bytes(bytes(image), profile, anchors=(anchor,), references=refs)


def reprofile(document, image):
    """Test-only trust declaration for a newly constructed synthetic image."""
    profile = replace(document.profile, sha256=hashlib.sha256(image).hexdigest())
    provenance = Provenance(profile.id, profile.sha256, "synthetic fixture construction")
    return RomDocument(bytes(image), profile,
        tuple(replace(a, provenance=provenance) for a in document.anchors),
        tuple(replace(r, provenance=provenance) for r in document.references))


def request(payload=PAYLOAD):
    return RelocationRequest(ID, payload)


def test_growing_payload_relocates_with_exact_rewrites_and_provenance(document):
    before = document.image
    result = plan_relocation(document, [request()])
    result.document.validate()
    assert result.document.anchor(ID).identity == document.anchor(ID).identity
    assert result.document.anchor(ID).range == span(0x208, len(PAYLOAD))
    assert result.document.image[0x208:0x208 + len(PAYLOAD)] == PAYLOAD
    assert result.document.image[0xC0:0xC4] == b"\x08\x02\x00\x08"
    assert result.document.image[0xC4:0xC8] == (0x20C - 0xC4).to_bytes(4, "little", signed=True)
    assert result.document.image[0x100:0x108] == b"old-data"
    changed = {i for i, (a, b) in enumerate(zip(before, result.document.image)) if a != b}
    assert changed <= set(range(0xC0, 0xC8)) | set(range(0x208, 0x208 + len(PAYLOAD)))
    assert document.image is before
    evidence = json.loads(json.dumps(result.to_json()))
    relocation = evidence["manifest"]["relocations"][0]
    assert relocation["owner"] == "fixture:owner"
    assert relocation["old_range"] == {"file_offset": 256, "size": 8}
    assert relocation["new_range"] == {"file_offset": 520, "size": len(PAYLOAD)}
    assert [r["classification"] for r in relocation["references_rewritten"]] == [
        "DECLARED_REFERENCE", "CONFIRMED_REFERENCE"]
    assert [r["source_file_offset"] for r in relocation["references_rewritten"]] == [192, 196]
    assert evidence["manifest"]["base"]["sha256"] == hashlib.sha256(before).hexdigest()
    assert evidence["manifest"]["output"]["sha256"] == hashlib.sha256(result.document.image).hexdigest()
    assert evidence["allocations"][0]["owner"] == "fixture:owner"


def test_reverse_inbound_lookup_includes_interior_targets(document):
    assert document.inbound(ID) == document.references
    assert document.inbound(span(0x104, 1)) == (document.references[1],)
    assert document.inbound(span(0x108, 1)) == ()


def test_allocation_determinism_across_request_and_free_region_order(document):
    requests = [AllocationRequest(AnchorId(name), name, size, alignment, kind=KIND)
                for name, size, alignment in [("z", 17, 16), ("a", 9, 8), ("m", 4, 4)]]
    second_free = replace(document.profile.free_regions[0], range=span(0x310, 32))
    profiles = [replace(document.profile, free_regions=free) for free in permutations(
        (*document.profile.free_regions, second_free))]
    results = [allocate(profile, order) for profile in profiles for order in permutations(requests)]
    assert all(result == results[0] for result in results)
    assert [a.range.start.value for a in results[0]] == [0x208, 0x204, 0x220]


def test_repeated_transaction_and_manifest_identical(document):
    assert plan_relocation(document, [request()]).to_json() == plan_relocation(document, [request()]).to_json()


def test_insufficient_space_is_explicit(document):
    with pytest.raises(InsufficientSpaceError):
        plan_relocation(document, [request(bytes(256))])


@pytest.mark.parametrize("alignment", [0, -1, 3, True])
def test_invalid_alignment_rejected(alignment):
    with pytest.raises(LayoutError, match="alignment"):
        AllocationRequest(ID, "owner", 4, alignment, kind=KIND)


def test_unaligned_anchor_rejected(document):
    with pytest.raises(LayoutError, match="alignment"):
        replace(document.anchor(ID), range=span(0x101, 8))


def test_alignment_padding_can_exhaust_free_space(document):
    profile = replace(document.profile, free_regions=(replace(document.profile.free_regions[0], range=span(0x201, 7)),))
    with pytest.raises(InsufficientSpaceError):
        allocate(profile, [AllocationRequest(ID, "owner", 1, 8, kind=KIND)])


def test_no_allocation_from_undeclared_zero_or_ff_runs(document):
    with pytest.raises(InsufficientSpaceError):
        allocate(replace(document.profile, free_regions=()), [AllocationRequest(ID, "owner", 1, 1, kind=KIND)])


def test_allocation_skips_existing_owned_ranges(document):
    result = allocate(document.profile, [AllocationRequest(ID, "new", 8, 8, kind=KIND)],
                      occupied=[OwnedRegion(span(0x208, 16), "existing")])
    assert result[0].range == span(0x218, 8)


def test_overlapping_ownership_rejected(document):
    with pytest.raises(LayoutError, match="overlapping"):
        allocate(document.profile, [AllocationRequest(ID, "new", 8, 8, kind=KIND)],
                 occupied=[OwnedRegion(span(0x210, 8), "one"), OwnedRegion(span(0x214, 8), "two")])


def test_overlapping_anchors_rejected(document):
    extra = replace(document.anchor(ID), identity=AnchorId("other"))
    with pytest.raises(LayoutError, match="overlapping ownership"):
        replace(document, anchors=document.anchors + (extra,)).validate()


def test_duplicate_identity_rejected(document):
    with pytest.raises(LayoutError, match="duplicate anchor"):
        replace(document, anchors=document.anchors * 2).validate()


def test_duplicate_requests_rejected(document):
    with pytest.raises(LayoutError, match="unique"):
        plan_relocation(document, [request(), request()])


def test_fixed_anchor_rejected(document):
    document = replace(document, anchors=(replace(document.anchor(ID), relocatable=False),))
    with pytest.raises(LayoutError, match="non-relocatable"):
        plan_relocation(document, [request()])


def test_candidate_inbound_blocks_and_names_source(document):
    document = replace(document, references=(replace(document.references[0], classification=RC.CANDIDATE_REFERENCE),
                                            document.references[1]))
    with pytest.raises(CandidateReferenceError, match="0x000000C0"):
        plan_relocation(document, [request()])


def test_scanner_never_promotes_and_candidate_blocks(document):
    image = bytearray(document.image)
    image[0xC8:0xCC] = (0x08000103).to_bytes(4, "little")
    document = reprofile(document, image)
    candidates = scan_pointer_candidates(document, span(0xC0, 12))
    assert len(candidates) == 1
    assert candidates[0].classification is RC.CANDIDATE_REFERENCE
    assert candidates[0].source == FileOffset(0xC8)
    assert candidates[0].target_delta == 3
    assert document.image == bytes(image)
    with pytest.raises(CandidateReferenceError, match="0x000000C8"):
        plan_relocation(replace(document, references=document.references + candidates), [request()])


@pytest.mark.parametrize("raw", [b"\0\0\0\0", (0x08000101).to_bytes(4, "little"),
                                 (0x08000400).to_bytes(4, "little")])
def test_malformed_declared_reference_rejected(document, raw):
    image = bytearray(document.image)
    image[0xC0:0xC4] = raw
    with pytest.raises(LayoutError, match="malformed reference"):
        plan_relocation(reprofile(document, image), [request()])


@pytest.mark.parametrize("source,delta", [(1022, 0), (0xC0, 8)])
def test_reference_bounds_rejected(document, source, delta):
    ref = replace(document.references[0], source=FileOffset(source), target_delta=delta)
    with pytest.raises(LayoutError):
        plan_relocation(replace(document, references=(ref,)), [request()])


def test_shrink_stranding_interior_target_rejected(document):
    with pytest.raises(LayoutError, match="interior reference"):
        plan_relocation(document, [request(b"abc")])


@pytest.mark.parametrize("change", ["image", "sha", "metadata", "provenance"])
def test_wrong_rom_or_profile_rejected(document, change):
    if change == "image":
        document = replace(document, image=document.image[:-1] + b"x")
    elif change == "sha":
        document = replace(document, profile=replace(document.profile, sha256="0" * 64))
    elif change == "metadata":
        document = replace(document, profile=replace(document.profile, game_code="BAD1"))
    else:
        document = replace(document, anchors=(replace(document.anchor(ID),
            provenance=replace(document.anchor(ID).provenance, profile_id="wrong")),))
    with pytest.raises(LayoutError, match="wrong"):
        plan_relocation(document, [request()])


def test_post_relocation_graph_detects_tampered_reference(document):
    result = plan_relocation(document, [request()])
    image = bytearray(result.document.image)
    image[0xC0:0xC4] = document.image[0xC0:0xC4]
    with pytest.raises(LayoutError, match="target mismatch"):
        replace(result.document, image=bytes(image)).validate()


def test_multi_anchor_batch_moves_internal_source_and_relative_target(document):
    provenance = document.anchor(ID).provenance
    second = Anchor(AnchorId("fixture:second"), span(0x180, 8), "opaque-test", "second", 8, True, provenance)
    internal = Reference(FileOffset(0x100), second.identity, 2, RE.RELATIVE_I32_LE, RC.CONFIRMED_REFERENCE, provenance)
    document = replace(document, anchors=document.anchors + (second,), references=document.references + (internal,))
    image = bytearray(document.image)
    image[0x100:0x104] = (0x182 - 0x100).to_bytes(4, "little", signed=True)
    document = reprofile(document, image)
    requests = [request(), RelocationRequest(second.identity, b"second larger payload")]
    result = plan_relocation(document, requests)
    other = plan_relocation(document, reversed(requests))
    assert result.to_json() == other.to_json()
    moved = result.document.inbound(second.identity)[0]
    assert moved.source == FileOffset(0x208)
    raw = result.document.image[0x208:0x20C]
    assert moved.encoding.decode(raw, moved.source, 1024) == result.document.target_offset(moved)
    assert result.document.image[0x100:0x108] == document.image[0x100:0x108]


def test_free_region_cannot_overlap_content_or_reference(document):
    for position in (0x100, 0xC0):
        profile = replace(document.profile, free_regions=(replace(document.profile.free_regions[0], range=span(position, 8)),))
        with pytest.raises(LayoutError, match="free region overlaps"):
            plan_relocation(replace(document, profile=profile), [request()])


@pytest.mark.parametrize("field,value", [("status", "CANDIDATE"), ("evidence", ""),
    ("file_offset", -1), ("size", 0), ("file_offset", 1024), ("extra", "bad")])
def test_profile_rejects_invalid_free_declarations(document, field, value):
    region = {"file_offset": 512, "size": 32, "status": "CONFIRMED", "evidence": "fixture"}
    region[field] = value
    with pytest.raises(ProfileConfigError):
        RomProfile.from_mapping({"id": "test", "game": "test", "region": "test", "game_code": "TEST",
            "size": 1024, "sha256": document.profile.sha256, "free_regions": [region]})


def test_encoding_types_do_not_silently_mask_or_normalize():
    assert RE.ABSOLUTE_ROM_U32_LE.decode(b"\x01\x01\x00\x08", FileOffset(0), 1024) == FileOffset(257)
    assert FileOffset(257).to_gba_address(1024) == GbaRomAddress(0x08000101)
    with pytest.raises(LayoutError):
        RomRange(0x08000100, 4)
    with pytest.raises(BinaryAddressError):
        FileOffset(True)


def test_failed_transaction_leaves_no_outputs_and_input_unchanged(document, tmp_path):
    base, output, manifest = (tmp_path / name for name in ("base.gba", "out.gba", "manifest.json"))
    base.write_bytes(document.image)
    before = base.stat()
    with pytest.raises(InsufficientSpaceError):
        emit_relocation(document, [request(bytes(512))], base, output, manifest_path=manifest)
    assert not output.exists() and not manifest.exists()
    assert base.read_bytes() == document.image
    assert base.stat().st_mtime_ns == before.st_mtime_ns


def test_successful_emit_is_deterministic_and_immutable(document, tmp_path):
    base = tmp_path / "base.gba"
    base.write_bytes(document.image)
    before = base.stat()
    manifests = []
    for name in ("one", "two"):
        output, manifest = tmp_path / f"{name}.gba", tmp_path / f"{name}.json"
        value = emit_relocation(document, [request()], base, output, manifest_path=manifest)
        assert output.read_bytes() == plan_relocation(document, [request()]).document.image
        assert manifest.read_text() == value.dumps()
        manifests.append(manifest.read_bytes())
    assert manifests[0] == manifests[1]
    assert base.read_bytes() == document.image and base.stat().st_mtime_ns == before.st_mtime_ns


@pytest.mark.parametrize("collision", ["source", "output", "existing"])
def test_manifest_path_collisions_fail_before_output(document, tmp_path, collision):
    base, output = tmp_path / "base.gba", tmp_path / "out.gba"
    base.write_bytes(document.image)
    manifest = {"source": base, "output": output, "existing": tmp_path / "existing.json"}[collision]
    if collision == "existing":
        manifest.write_text("preserve")
    with pytest.raises(write.WriteError):
        emit_relocation(document, [request()], base, output, manifest_path=manifest)
    assert not output.exists()
    assert base.read_bytes() == document.image
    if collision == "existing":
        assert manifest.read_text() == "preserve"


def test_publication_failure_rolls_back_manifest(document, tmp_path, monkeypatch):
    base, output, manifest = (tmp_path / name for name in ("base.gba", "out.gba", "manifest.json"))
    base.write_bytes(document.image)
    real_link = write.os.link
    def fail_image(source, destination):
        if destination == output:
            raise OSError("simulated publication failure")
        real_link(source, destination)
    monkeypatch.setattr(write.os, "link", fail_image)
    with pytest.raises(OSError, match="publication"):
        emit_relocation(document, [request()], base, output, manifest_path=manifest)
    assert not output.exists() and not manifest.exists()
    assert list(tmp_path.glob(".webfoot-*")) == []
    assert base.read_bytes() == document.image


def test_unvalidated_write_plan_is_rechecked(document):
    change = write.ByteChange(1024, b"a", b"b", "owner", "bad bounds")
    plan = write.WritePlan(document.profile.id, document.profile.sha256, 1024, (change,))
    with pytest.raises(write.ChangeValidationError):
        write.apply_plan(document.image, plan)


def test_cli_proof_reports_graph_allocations_and_exact_rewrites(capsys):
    from tools.webfoot.cli import main
    assert main(["relocation-proof"]) == 0
    first = capsys.readouterr().out
    assert main(["relocation-proof"]) == 0
    assert capsys.readouterr().out == first
    result = json.loads(first)
    assert result["allocations"][0]["range"]["file_offset"] == 0x208
    assert len(result["document"]["references"]) == 2
    assert len(result["manifest"]["relocations"][0]["references_rewritten"]) == 2


def test_candidate_on_unmoved_anchor_is_preserved(document):
    other = replace(document.anchor(ID), identity=AnchorId("other"), range=span(0x180, 8))
    candidate = replace(document.references[0], target=other.identity, source=FileOffset(0xC8),
                        classification=RC.CANDIDATE_REFERENCE)
    document = replace(document, anchors=document.anchors + (other,), references=document.references + (candidate,))
    image = bytearray(document.image)
    image[0xC8:0xCC] = (0x08000180).to_bytes(4, "little")
    document = reprofile(document, image)
    result = plan_relocation(document, [request()])
    assert result.document.inbound(other.identity)[0].classification is RC.CANDIDATE_REFERENCE
    assert result.document.image[0xC8:0xCC] == document.image[0xC8:0xCC]


def test_out_of_bounds_anchor_fails(document):
    with pytest.raises(LayoutError, match="out of bounds"):
        plan_relocation(replace(document, anchors=(replace(document.anchor(ID), range=span(1024, 8)),)), [request()])


def test_failed_candidate_emit_has_no_output(document, tmp_path):
    document = replace(document, references=(replace(document.references[0], classification=RC.CANDIDATE_REFERENCE),))
    output = tmp_path / "out.gba"
    with pytest.raises(CandidateReferenceError):
        emit_relocation(document, [request()], tmp_path / "unused-base", output)
    assert not output.exists()


def test_emit_rejects_wrong_actual_base(document, tmp_path):
    base, output = tmp_path / "wrong.gba", tmp_path / "out.gba"
    base.write_bytes(b"wrong")
    with pytest.raises(write.ChangeValidationError):
        emit_relocation(document, [request()], base, output)
    assert base.read_bytes() == b"wrong" and not output.exists()


def test_overlapping_profile_free_regions_rejected(document):
    profile = replace(document.profile, free_regions=document.profile.free_regions * 2)
    with pytest.raises(LayoutError, match="overlapping"):
        allocate(profile, [AllocationRequest(ID, "owner", 8, 8, kind=KIND)])


def test_relative_encoding_signed_backwards_and_bounds():
    source, target = FileOffset(500), FileOffset(200)
    raw = RE.RELATIVE_I32_LE.encode(target, source, 1024)
    assert int.from_bytes(raw, "little", signed=True) == -300
    assert RE.RELATIVE_I32_LE.decode(raw, source, 1024) == target
    with pytest.raises(LayoutError, match="out of bounds"):
        RE.RELATIVE_I32_LE.decode((-501).to_bytes(4, "little", signed=True), source, 1024)


def test_staging_failure_emits_nothing(document, tmp_path, monkeypatch):
    base, output, manifest = (tmp_path / name for name in ("base.gba", "out.gba", "manifest.json"))
    base.write_bytes(document.image)
    def fail_fsync(*args):
        raise OSError("simulated staging failure")
    monkeypatch.setattr(write.os, "fsync", fail_fsync)
    with pytest.raises(OSError, match="staging"):
        emit_relocation(document, [request()], base, output, manifest_path=manifest)
    assert not output.exists() and not manifest.exists()
    assert list(tmp_path.glob(".webfoot-*")) == []


def test_post_validation_failure_emits_nothing(document, tmp_path, monkeypatch):
    original = RomDocument.validate
    def fail_post(self):
        original(self)
        if self.retired:
            raise LayoutError("simulated post-validation failure")
    monkeypatch.setattr(RomDocument, "validate", fail_post)
    output = tmp_path / "out.gba"
    with pytest.raises(LayoutError, match="post-validation"):
        emit_relocation(document, [request()], tmp_path / "unused-base", output)
    assert not output.exists()


# --- TOOLKIT-026: the relocation eligibility rule, on synthetic anchors ------

_PROV = Provenance("synthetic-eligibility-v1", "0" * 64, "constructed TOOLKIT-026 fixture")


def _anchor(kind="placement_reference_array", start=0x100, size=8):
    return Anchor(AnchorId("fixture:array"), RomRange(FileOffset(start), size),
                  kind, "fixture:owner", 4, False, _PROV)


def _ref(source, target="fixture:array", delta=0, cls=RC.CONFIRMED_REFERENCE):
    return Reference(FileOffset(source), AnchorId(target), delta,
                     RE.ABSOLUTE_ROM_U32_LE, cls, _PROV)


def test_eligible_when_every_reference_is_confirmed_or_declared():
    anchor = _anchor()
    owner = _ref(0x200)
    slots = (_ref(0x100, "fixture:body", 0), _ref(0x104, "fixture:body", 0))
    assert relocation_eligible(anchor, (owner,) + slots) is True
    # DECLARED carries the same authority as CONFIRMED for this contract.
    assert relocation_eligible(anchor, (_ref(0x200, cls=RC.DECLARED_REFERENCE),) + slots) is True


def test_one_candidate_reference_withdraws_eligibility():
    """SC6: a CANDIDATE is an unresolved numeric hit; the rule refuses it here."""
    anchor = _anchor()
    inbound_candidate = _ref(0x200, cls=RC.CANDIDATE_REFERENCE)
    assert relocation_eligible(anchor, (inbound_candidate,)) is False
    # ...and one merely SOURCED inside the anchor is refused too, because its
    # field travels with the payload and its meaning is not established.
    interior_candidate = _ref(0x104, "fixture:body", 0, RC.CANDIDATE_REFERENCE)
    assert relocation_eligible(anchor, (_ref(0x200), interior_candidate)) is False


def test_unlisted_anchor_kinds_stay_fixed_however_clean_their_references():
    """SC8: eligibility is scoped by proven kind, never granted generally.

    Membership is asserted exactly, so a kind can only ever join it deliberately.
    TOOLKIT-024 proved `placement_reference_array`; TOOLKIT-036 proved
    `text-string`, whose whole inbound surface is its own pointer-table slot;
    GRAPHICS-IMPORT-BOUNDARY-001 added `graphics_container`, whose inbound surface
    is the CONFIRMED piece `+0x08` words the graphics reference walk publishes and
    which is a graph leaf by construction; SPRITE-NEW-RUNTIME-001 added
    `character_pointer_table`, whose inbound surface is a whole-image census
    result of exactly two CONFIRMED literal-pool words. A `character_structure`
    is asserted fixed below: it is reached by a table slot that travels with the
    structure only if the registry itself moves as one batch, which this constant
    does not decide on its own.
    """
    assert RELOCATION_ELIGIBLE_KINDS == frozenset(
        {"placement_reference_array", "text-string", "graphics_container",
         "character_pointer_table"}
    )
    owner = _ref(0x200)
    for kind in ("map_entry", "placement", "enemy_stat_record", "thumb_entry",
                 "placement_descriptor", "object_palette", "character_structure",
                 "opaque-test"):
        assert relocation_eligible(_anchor(kind=kind), (owner,)) is False


def test_an_anchor_nothing_points_at_is_not_eligible():
    """Moving an unreferenced anchor would orphan whatever really reaches it."""
    assert relocation_eligible(_anchor(), ()) is False
    assert relocation_eligible(_anchor(), (_ref(0x300, "fixture:other"),)) is False


def test_a_stranded_or_straddling_reference_withdraws_eligibility():
    anchor = _anchor(size=8)
    # An inbound reference pointing past the anchor's extent cannot be rehomed.
    assert relocation_eligible(anchor, (_ref(0x200, delta=8),)) is False
    # A source field starting inside but ending past the end would be split.
    assert relocation_eligible(anchor, (_ref(0x200), _ref(0x106, "fixture:body"))) is False


def test_eligibility_never_consults_an_address_or_an_identity():
    """The rule is a statement about references, not about which array it is."""
    owner_at = lambda start: (_ref(0x900),)
    for start in (0x100, 0x2000, 0x40000):
        assert relocation_eligible(_anchor(start=start), owner_at(start)) is True
