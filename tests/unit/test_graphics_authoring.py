"""GRAPHICS-IMPORT-BOUNDARY-001: authored graphic pixels, portably.

Everything here runs over synthetic bytes: a small fabricated image, a
fabricated graphics reference document and a duck-typed stand-in for the decoded
sprite corpus. That split is deliberate rather than convenient. The corpus walk
and the real container codec are ROM-derived and cannot be exercised without the
canonical image, so they live in
`tests/integration/test_graphics_pixel_override_build_rom.py`; what is decided
HERE is the part this ticket actually adds - which PNG is an authored override,
which reference set may be rewritten, where the allocator puts a payload, and
what is refused.

The stubs are narrow on purpose. `plan_graphic_overrides` consumes exactly four
things from the corpus object (`profile`, `graphics()`, `encode_pixels()` and
`reference_document()`), so a fake supplying those four is a faithful stand-in
rather than a mock of internals, and the reference document it returns is a real
`RomDocument` built by the real validator.
"""

from __future__ import annotations

import re

import pytest

from tests.helpers import make_synthetic_rom, profile_for

from tools.webfoot import graphics_authoring as ga
from tools.webfoot.allocation import (Addressability, AllocationKind,
                                      DEFAULT_ADDRESSABILITY, InsufficientSpaceError,
                                      StorageModel)
from tools.webfoot.binary import FileOffset
from tools.webfoot.document import RomDocument
from tools.webfoot.formats import indexed_png
from tools.webfoot.graphics import CharacterIdentity, FrameRef, Graphic, GraphicIdentity
from tools.webfoot.layout import (Anchor, AnchorId, Provenance, Reference,
                                  ReferenceClass, ReferenceEncoding,
                                  RELOCATION_ELIGIBLE_KINDS, RomRange,
                                  relocation_eligible)
from tools.webfoot.project.format import dump_toml
from tools.webfoot.project.model import (GraphicsOverrides, PixelOverride,
                                          ProjectValidationError)
from tools.webfoot.write import apply_plan, plan_changes

# --- the synthetic world -----------------------------------------------------

ROM_SIZE = 0x4000
ROM_BASE = 0x08000000
PROFILE_ID = "synthetic_exact"

#: Two canonical containers, and three piece records naming them. Graphic A is
#: named by two pieces (a shared payload); graphic B by one.
CONTAINER_A = 0x0800
CONTAINER_B = 0x0900
CONTAINER_SIZE = 0x40
PIECE_A = 0x1000
PIECE_B = 0x1100
PIECE_C = 0x1200
#: A word-aligned numeric hit on a container address that no frame piece record
#: owns: the shape of an undiscovered reference, published as CANDIDATE.
CANDIDATE_PIECE = 0x1300

#: One declared verified-free canonical region, and a generated expansion. The
#: region is deliberately larger than a container so that the two relocation
#: destinations - canonical verified-free and declared expansion - are both
#: reachable and can be told apart by which one the allocator picks.
FREE_OFFSET = 0x2000
FREE_SIZE = 0x80
EXPANSION_SIZE = 0x8000

#: An authored payload that must move, and one that must leave the canonical
#: image entirely (above FREE_SIZE as well as above the container extent).
MOVED_PAYLOAD = 0x60
EXPANDED_PAYLOAD = 0x90

EVIDENCE = "synthetic fixture for graphics pixel-override planning"


def _address(file_offset: int) -> bytes:
    return (ROM_BASE + file_offset).to_bytes(4, "little")


def _world(*, free: bool = True, expansion: bool = True, candidate: bool = False):
    """A 16 KiB synthetic image with a graphics anchor/reference graph."""
    image = bytearray(make_synthetic_rom(size=ROM_SIZE))
    image[CONTAINER_A : CONTAINER_A + 4] = b"\x10\x00\x00\x00"
    image[CONTAINER_B : CONTAINER_B + 4] = b"\x10\x00\x00\x00"
    for piece, target in ((PIECE_A, CONTAINER_A), (PIECE_B, CONTAINER_A),
                          (PIECE_C, CONTAINER_B)):
        image[piece : piece + 4] = _address(target)
    if candidate:
        # An unresolved numeric hit on the shared payload's address. It decodes
        # correctly - a candidate is a shape match, not a malformed field - so it
        # is a legitimate member of the graph and only the eligibility rule
        # withdraws the anchor.
        image[CANDIDATE_PIECE : CANDIDATE_PIECE + 4] = _address(CONTAINER_A)
    image = bytes(image)
    overrides: dict = {}
    if free:
        overrides["free_regions"] = [{
            "file_offset": FREE_OFFSET,
            "size": FREE_SIZE,
            "status": "CONFIRMED",
            "evidence": EVIDENCE,
        }]
    if expansion:
        overrides["generated_expansion"] = {
            "output_size": EXPANSION_SIZE,
            "padding_byte": 0xFF,
            "evidence": EVIDENCE,
        }
    profile = profile_for(image, **overrides)
    references = _references(profile)
    if candidate:
        references = references + (
            Reference(FileOffset(CANDIDATE_PIECE), AnchorId(_identity(0)), 0,
                      ReferenceEncoding.ABSOLUTE_ROM_U32_LE,
                      ReferenceClass.CANDIDATE_REFERENCE,
                      Provenance(profile.id, profile.sha256, EVIDENCE)),
        )
    return image, profile, _document(image, profile, references)


def _identity(index: int) -> str:
    return f"{PROFILE_ID}/graphic:{index:04d}"


def _proof(profile) -> Provenance:
    return Provenance(profile.id, profile.sha256, EVIDENCE)


def _anchors(profile, *, relocatable=(False, False)) -> tuple[Anchor, ...]:
    return tuple(
        Anchor(AnchorId(_identity(index)), RomRange(FileOffset(offset), CONTAINER_SIZE),
               "graphics_container", _identity(index), 4, relocatable[index],
               _proof(profile))
        for index, offset in enumerate((CONTAINER_A, CONTAINER_B))
    )


def _references(profile) -> tuple[Reference, ...]:
    proof = _proof(profile)
    return tuple(
        Reference(FileOffset(piece), AnchorId(_identity(index)), 0,
                  ReferenceEncoding.ABSOLUTE_ROM_U32_LE,
                  ReferenceClass.CONFIRMED_REFERENCE, proof)
        for piece, index in ((PIECE_A, 0), (PIECE_B, 0), (PIECE_C, 1))
    )


def _document(image, profile, references, *, eligible: bool = True,
              relocatable=(False, False)):
    """A real `RomDocument`; `eligible` applies the shared eligibility rule.

    With `eligible=False` the anchors keep whatever the caller passed, which is
    how a defensive branch whose precondition the rule would otherwise make
    unreachable - a relocatable anchor with no inbound reference - is exercised.
    """
    anchors = _anchors(profile, relocatable=relocatable)
    if eligible:
        anchors = tuple(
            Anchor(a.identity, a.range, a.kind, a.owner, a.alignment,
                   relocation_eligible(a, references), a.provenance)
            for a in anchors
        )
    return RomDocument.from_bytes(image, profile, anchors=anchors,
                                  references=references)


def _graphic(index: int, offset: int, packed_size: int, consumers: tuple) -> Graphic:
    identity = GraphicIdentity(PROFILE_ID, index)
    return Graphic(
        identity=identity,
        file_offset=offset,
        width=8,
        height=8,
        colour_256=False,
        pixels=bytes(64),
        packed_size=packed_size,
        consumers=consumers,
        characters=(CharacterIdentity(PROFILE_ID, 0),),
    )


class _StubSprites:
    """The four members `plan_graphic_overrides` reads from the corpus."""

    def __init__(self, profile, document, graphics, encoder) -> None:
        self.profile = profile
        self._document = document
        self._graphics = tuple(graphics)
        self._encoder = encoder
        self.encoded: list[tuple[str, bytes]] = []

    def graphics(self):
        return self._graphics

    def encode_pixels(self, identity, pixels: bytes) -> bytes:
        self.encoded.append((str(identity), bytes(pixels)))
        return self._encoder(str(identity), bytes(pixels))

    def reference_document(self):
        return self._document


def _corpus(*, payload_sizes: dict[int, int] | None = None, candidate: bool = False):
    image, profile, document = _world(candidate=candidate)
    sizes = payload_sizes or {}
    graphics = [
        _graphic(0, CONTAINER_A, CONTAINER_SIZE, (
            FrameRef(0x2000, 0, 0, 0, 0, PIECE_A),
            FrameRef(0x2100, 1, 0, 0, 0, PIECE_B),
        )),
        _graphic(1, CONTAINER_B, CONTAINER_SIZE, (FrameRef(0x2200, 0, 0, 0, 0, PIECE_C),)),
    ]

    def encoder(identity: str, pixels: bytes) -> bytes:
        index = int(identity.rsplit(":", 1)[1])
        return bytes(sizes.get(index, 8))

    return image, profile, document, _StubSprites(profile, document, graphics, encoder)


def _override(identity: str) -> PixelOverride:
    index = int(identity.rsplit(":", 1)[1])
    return PixelOverride(identity=identity, file=f"graphics/assets/graphic_{index:04d}.png",
                         pixels=bytes(64), width=8, height=8, colour_256=False)


# --- the project model carries authored pixel content ------------------------


def test_pixel_override_refuses_a_pixel_count_that_is_not_its_dimensions():
    with pytest.raises(ProjectValidationError, match="do not describe"):
        PixelOverride(identity="p/graphic:0000", file="a.png", pixels=bytes(63),
                      width=8, height=8, colour_256=False)


def test_pixel_override_refuses_an_unreadable_bit_depth():
    with pytest.raises(ProjectValidationError, match="boolean bit depth"):
        PixelOverride(identity="p/graphic:0000", file="a.png", pixels=bytes(64),
                      width=8, height=8, colour_256="4")


def test_graphics_overrides_start_with_no_authored_pixels():
    """A project that authored nothing has an empty pixel half, not a guess."""
    assert GraphicsOverrides().pixels == {}
    assert GraphicsOverrides(palette={1: (0, 0, 0)}).pixels == {}


# --- the extracted manifest --------------------------------------------------


def _manifest_document(*, digests: bool = True, extra: dict | None = None) -> dict:
    entry = {
        "file": "graphics/assets/graphic_0000.png",
        "width": 8,
        "height": 8,
        "bit_depth": 4,
        "packed_size": 32,
        "shared": False,
        "consumer_count": 1,
        "characters": [],
    }
    if digests:
        entry["png_sha256"] = "0" * 64
        entry["pixels_sha256"] = "1" * 64
    if extra:
        entry.update(extra)
    return {
        "graphics": {"profile_id": PROFILE_ID, "transparent_index": 0, "palette_raw": [0, 0]},
        "asset": {f"{PROFILE_ID}/graphic:0000": entry},
        "character": {},
    }


def _write_project(tmp_path, document: dict) -> "object":
    (tmp_path / "graphics").mkdir(parents=True, exist_ok=True)
    (tmp_path / "graphics" / "graphics.toml").write_text(
        dump_toml(document), encoding="utf-8", newline="\n"
    )
    return tmp_path


def test_a_project_without_a_graphics_manifest_authors_no_pixels(tmp_path):
    assert ga.read_graphics_manifest(tmp_path) is None
    assert ga.resolve_pixel_overrides(tmp_path, None, lambda identity: None) == {}


def test_the_manifest_records_the_baseline_it_was_extracted_at(tmp_path):
    manifest = ga.read_graphics_manifest(_write_project(tmp_path, _manifest_document()))
    assert manifest.profile_id == PROFILE_ID
    asset = manifest.assets[f"{PROFILE_ID}/graphic:0000"]
    assert asset.width == 8 and asset.height == 8 and asset.colour_256 is False
    assert asset.png_sha256 == "0" * 64 and asset.pixels_sha256 == "1" * 64
    assert manifest.records_a_baseline is True


def test_a_manifest_without_digests_is_not_a_fast_baseline(tmp_path):
    manifest = ga.read_graphics_manifest(
        _write_project(tmp_path, _manifest_document(digests=False))
    )
    assert manifest.records_a_baseline is False


@pytest.mark.parametrize(
    "document, message",
    [
        ({}, "no [graphics] header"),
        ({"graphics": {"profile_id": PROFILE_ID}, "asset": {}}, "no [asset] table"),
        (_manifest_document(extra={"bit_depth": 5}), "not 4 or 8"),
        (_manifest_document(extra={"packed_size": 0}), "not a positive integer"),
        (_manifest_document(extra={"png_sha256": "beef"}), "not a sha256 digest"),
    ],
)
def test_a_malformed_manifest_is_refused_rather_than_skipped(tmp_path, document, message):
    with pytest.raises(ga.GraphicsManifestError, match=re.escape(message)):
        ga.read_graphics_manifest(_write_project(tmp_path, document))


# --- resolving which assets are authored -------------------------------------


def _png(pixels: bytes, *, width: int = 8, height: int = 8, entries: int = 16) -> bytes:
    palette = tuple((index * 7 % 256, 0, 0) for index in range(entries))
    return indexed_png.encode(pixels, width, height, palette, transparent_index=0)


def _authored(tmp_path, document, raw: bytes):
    root = _write_project(tmp_path, document)
    (root / "graphics" / "assets").mkdir(parents=True, exist_ok=True)
    (root / "graphics" / "assets" / "graphic_0000.png").write_bytes(raw)
    return root


def _manifest_with_digests(raw: bytes, pixels: bytes, **extra) -> dict:
    from hashlib import sha256

    document = _manifest_document(digests=False, extra=extra)
    entry = document["asset"][f"{PROFILE_ID}/graphic:0000"]
    entry["png_sha256"] = sha256(raw).hexdigest()
    entry["pixels_sha256"] = sha256(pixels).hexdigest()
    return document


def test_an_untouched_asset_is_decided_by_hashing_its_file(tmp_path):
    pixels = bytes(range(16)) * 4
    raw = _png(pixels)
    root = _authored(tmp_path, _manifest_with_digests(raw, pixels), raw)
    manifest = ga.read_graphics_manifest(root)
    # A canonical-pixel lookup that fails loudly proves the fast path never
    # decoded anything.
    assert ga.resolve_pixel_overrides(root, manifest, lambda i: pytest.fail("decoded")) == {}


def test_an_editor_that_resaved_identical_art_is_not_an_edit(tmp_path):
    """Different PNG bytes, same indices: a no-op, not an authored change."""
    pixels = bytes(range(16)) * 4
    original = _png(pixels)
    resaved = _png(pixels, entries=32)
    assert resaved != original
    root = _authored(tmp_path, _manifest_with_digests(original, pixels), resaved)
    manifest = ga.read_graphics_manifest(root)
    assert ga.resolve_pixel_overrides(root, manifest, lambda i: pytest.fail("decoded")) == {}


def test_an_authored_asset_resolves_to_its_decoded_pixels(tmp_path):
    pixels = bytes(range(16)) * 4
    edited = bytes(range(15, -1, -1)) * 4
    root = _authored(tmp_path, _manifest_with_digests(_png(pixels), pixels), _png(edited))
    manifest = ga.read_graphics_manifest(root)
    resolved = ga.resolve_pixel_overrides(root, manifest, lambda i: pytest.fail("decoded"))
    override = resolved[f"{PROFILE_ID}/graphic:0000"]
    assert override.pixels == edited
    assert override.width == 8 and override.height == 8
    assert override.colour_256 is False
    assert override.file == "graphics/assets/graphic_0000.png"


def test_a_resized_asset_is_refused_naming_the_contract_it_violates(tmp_path):
    pixels = bytes(64)
    raw = _png(bytes(256), width=16, height=16)
    root = _authored(tmp_path, _manifest_with_digests(_png(pixels), pixels), raw)
    manifest = ga.read_graphics_manifest(root)
    with pytest.raises(ga.GraphicsAuthoringError, match="does not\\s+resize"):
        ga.resolve_pixel_overrides(root, manifest, lambda i: None)


def test_an_index_above_the_declared_depth_is_refused(tmp_path):
    pixels = bytes(64)
    raw = _png(bytes([200] * 64), entries=256)
    root = _authored(tmp_path, _manifest_with_digests(_png(pixels), pixels), raw)
    manifest = ga.read_graphics_manifest(root)
    with pytest.raises(ga.GraphicsAuthoringError, match="above the 15"):
        ga.resolve_pixel_overrides(root, manifest, lambda i: None)


def test_a_non_indexed_png_is_refused_rather_than_quantised(tmp_path):
    from tools.webfoot.formats import bg_tilemap  # noqa: F401  (import kept local)

    pixels = bytes(64)
    raw = b"\x89PNG\r\n\x1a\n" + b"not an indexed png"
    root = _authored(tmp_path, _manifest_with_digests(_png(pixels), pixels), raw)
    manifest = ga.read_graphics_manifest(root)
    with pytest.raises(ga.GraphicsAuthoringError, match="indexed PNG"):
        ga.resolve_pixel_overrides(root, manifest, lambda i: None)


def test_a_missing_asset_file_is_refused_rather_than_read_as_unchanged(tmp_path):
    pixels = bytes(64)
    root = _write_project(tmp_path, _manifest_with_digests(_png(pixels), pixels))
    manifest = ga.read_graphics_manifest(root)
    with pytest.raises(ga.GraphicsAuthoringError, match="no readable file"):
        ga.resolve_pixel_overrides(root, manifest, lambda i: None)


def test_a_manifest_without_digests_falls_back_to_the_base_image(tmp_path):
    """A project extracted before digests existed is still authored correctly."""
    pixels = bytes(range(16)) * 4
    edited = bytes(range(15, -1, -1)) * 4
    root = _authored(tmp_path, _manifest_document(digests=False), _png(edited))
    manifest = ga.read_graphics_manifest(root)
    assert manifest.records_a_baseline is False
    assert ga.resolve_pixel_overrides(root, manifest, lambda i: pixels) != {}
    assert ga.resolve_pixel_overrides(root, manifest, lambda i: edited) == {}


# --- two registrations, tested independently ---------------------------------


def test_graphics_is_a_first_class_allocation_kind():
    """Registration one: the single allocation authority knows the kind."""
    assert AllocationKind.GRAPHICS_CONTAINER.value == "graphics_container"
    assert (DEFAULT_ADDRESSABILITY[AllocationKind.GRAPHICS_CONTAINER]
            is Addressability.EXPANDED_PERMITTED)
    # ...and a canonical-only request can never be handed the expansion.
    _, profile, _ = _world()
    model = StorageModel.from_profile(profile)
    assert model.expanded_authorized is True
    assert any(region.range.start.value >= profile.size
               for region in model.allocatable_regions())


def test_a_graphics_container_anchor_is_relocation_eligible():
    """Registration two: the anchor kind may be relocated at all."""
    assert "graphics_container" in RELOCATION_ELIGIBLE_KINDS
    _, _, document = _world()
    anchor = document.anchor(AnchorId(f"{PROFILE_ID}/graphic:0000"))
    assert anchor.relocatable is True
    # A CANDIDATE in the consumer set withdraws it, which is the whole reason
    # the two registrations are separate claims.
    candidate = Reference(FileOffset(0x1300), AnchorId(f"{PROFILE_ID}/graphic:0000"), 0,
                          ReferenceEncoding.ABSOLUTE_ROM_U32_LE,
                          ReferenceClass.CANDIDATE_REFERENCE, anchor.provenance)
    assert relocation_eligible(anchor, (*document.references, candidate)) is False


# --- planning: in place ------------------------------------------------------


def test_a_payload_that_fits_is_written_in_place_with_no_allocation():
    image, profile, _, sprites = _corpus(payload_sizes={0: 32})
    result = ga.plan_graphic_overrides(image, None, {f"{PROFILE_ID}/graphic:0000":
                                                     _override(f"{PROFILE_ID}/graphic:0000")},
                                       sprites=sprites)
    assert result.reserved == () and result.relocations == ()
    assert result.generated_allocations == ()
    assert len(result.changes) == 1
    change = result.changes[0]
    # Only the payload region is claimed; the original trailing bytes of the
    # container's extent are never part of the change.
    assert change.offset == CONTAINER_A
    assert change.size == 32
    assert change.owner == f"{PROFILE_ID}/graphic:0000"
    assert change.new == bytes(32)


def test_an_in_place_edit_leaves_the_container_tail_and_neighbours_intact():
    image, profile, _, sprites = _corpus(payload_sizes={0: 32})
    result = ga.plan_graphic_overrides(image, None, {f"{PROFILE_ID}/graphic:0000":
                                                     _override(f"{PROFILE_ID}/graphic:0000")},
                                       sprites=sprites)
    plan = plan_changes(image, result.changes, profile_id=profile.id,
                        base_sha256=profile.sha256)
    output = apply_plan(image, plan)
    assert output[CONTAINER_A:CONTAINER_A + 32] == bytes(32)
    assert output[CONTAINER_A + 32:CONTAINER_A + CONTAINER_SIZE] == \
        image[CONTAINER_A + 32:CONTAINER_A + CONTAINER_SIZE]
    assert output[CONTAINER_B:CONTAINER_B + CONTAINER_SIZE] == \
        image[CONTAINER_B:CONTAINER_B + CONTAINER_SIZE]
    assert output[:CONTAINER_A] == image[:CONTAINER_A]
    # Every reference word is untouched by an in-place edit.
    assert output[PIECE_A:PIECE_A + 4] == image[PIECE_A:PIECE_A + 4]


# --- planning: relocation ----------------------------------------------------


def test_an_oversized_payload_is_allocated_and_every_consumer_rewritten():
    """A shared payload moves ONCE and both of its pieces follow it."""
    image, profile, _, sprites = _corpus(payload_sizes={0: MOVED_PAYLOAD})
    identity = _identity(0)
    result = ga.plan_graphic_overrides(image, None, {identity: _override(identity)},
                                       sprites=sprites)
    assert len(result.relocations) == 1
    relocation = result.relocations[0]
    assert relocation.anchor == identity
    assert relocation.new_range.size == MOVED_PAYLOAD
    # One new payload, not one per consumer: 1 payload write + 2 reference words.
    assert len(result.changes) == 3
    assert sorted(change.size for change in result.changes) == [4, 4, MOVED_PAYLOAD]
    addressed = {change.offset for change in result.changes}
    assert addressed == {relocation.new_range.start.value, PIECE_A, PIECE_B}
    assert {rewrite.new_target_file_offset
            for rewrite in relocation.references} == {relocation.new_range.start.value}
    assert {rewrite.new_source_file_offset
            for rewrite in relocation.references} == {PIECE_A, PIECE_B}


def test_a_small_oversized_payload_lands_in_verified_canonical_storage():
    """First fit prefers a canonical verified-free span when one can host it."""
    image, profile, _, sprites = _corpus(payload_sizes={0: MOVED_PAYLOAD})
    identity = _identity(0)
    result = ga.plan_graphic_overrides(image, None, {identity: _override(identity)},
                                       sprites=sprites)
    allocation = result.relocations[0]
    assert allocation.new_range.start.value == FREE_OFFSET
    assert allocation.free_region_evidence == EVIDENCE
    assert result.generated_allocations == ()


def test_a_payload_too_large_for_canonical_space_takes_declared_expansion():
    image, profile, _, sprites = _corpus(payload_sizes={0: EXPANDED_PAYLOAD})
    identity = _identity(0)
    result = ga.plan_graphic_overrides(image, None, {identity: _override(identity)},
                                       sprites=sprites)
    assert len(result.generated_allocations) == 1
    provenance = result.generated_allocations[0]
    assert provenance.domain == ga.DOMAIN
    assert provenance.allocated_range.start.value == profile.size
    assert provenance.allocated_rom_address == ROM_BASE + profile.size
    # The single reported pointer is the lowest confirmed consumer field.
    assert provenance.pointer_offset == PIECE_A


def test_a_relocated_payload_validates_and_applies_as_one_transaction():
    image, profile, _, sprites = _corpus(payload_sizes={0: EXPANDED_PAYLOAD})
    identity = _identity(0)
    result = ga.plan_graphic_overrides(image, None, {identity: _override(identity)},
                                       sprites=sprites)
    generated = profile.generated_expansion.generated_image(
        profile.size, tuple(a.allocated_range for a in result.generated_allocations)
    )
    plan = plan_changes(image, result.changes, profile_id=profile.id,
                        base_sha256=profile.sha256, relocations=result.relocations,
                        generated_image=generated,
                        generated_allocations=result.generated_allocations)
    output = apply_plan(image, plan)
    start = result.relocations[0].new_range.start.value
    assert len(output) == EXPANSION_SIZE
    assert output[start:start + EXPANDED_PAYLOAD] == bytes(EXPANDED_PAYLOAD)
    # Both consumers carry the same new address.
    encoded = (ROM_BASE + start).to_bytes(4, "little")
    assert output[PIECE_A:PIECE_A + 4] == encoded
    assert output[PIECE_B:PIECE_B + 4] == encoded
    # The original payload is left byte-intact: an undiscovered reference still
    # points at the art it always pointed at.
    assert output[CONTAINER_A:CONTAINER_A + CONTAINER_SIZE] == \
        image[CONTAINER_A:CONTAINER_A + CONTAINER_SIZE]
    assert output[CONTAINER_B:CONTAINER_B + CONTAINER_SIZE] == \
        image[CONTAINER_B:CONTAINER_B + CONTAINER_SIZE]


def test_the_unrelated_graphic_is_byte_identical_after_a_relocation():
    image, profile, _, sprites = _corpus(payload_sizes={0: EXPANDED_PAYLOAD})
    identity = _identity(0)
    result = ga.plan_graphic_overrides(image, None, {identity: _override(identity)},
                                       sprites=sprites)
    generated = profile.generated_expansion.generated_image(
        profile.size, tuple(a.allocated_range for a in result.generated_allocations)
    )
    plan = plan_changes(image, result.changes, profile_id=profile.id,
                        base_sha256=profile.sha256, relocations=result.relocations,
                        generated_image=generated,
                        generated_allocations=result.generated_allocations)
    output = apply_plan(image, plan)
    assert output[PIECE_C:PIECE_C + 4] == image[PIECE_C:PIECE_C + 4]
    assert output[:CONTAINER_A] == image[:CONTAINER_A]
    assert output[CONTAINER_B:PIECE_A] == image[CONTAINER_B:PIECE_A]


def test_planning_is_deterministic_for_the_same_authored_project():
    image, profile, _, sprites = _corpus(payload_sizes={0: EXPANDED_PAYLOAD})
    identity = _identity(0)
    first = ga.plan_graphic_overrides(image, None, {identity: _override(identity)},
                                      sprites=sprites)
    second = ga.plan_graphic_overrides(image, None, {identity: _override(identity)},
                                       sprites=sprites)
    assert first == second


# --- planning: fail closed ---------------------------------------------------


def test_an_unknown_graphic_identity_is_refused():
    image, _, _, sprites = _corpus()
    identity = f"{PROFILE_ID}/graphic:9999"
    with pytest.raises(ga.GraphicsAuthoringError, match="does not contain"):
        ga.plan_graphic_overrides(image, None, {identity: _override(identity)},
                                  sprites=sprites)


def test_a_graphic_the_graph_has_not_published_relocatable_is_refused():
    """Registration two is per anchor: a kind being eligible is not a permission."""
    image, profile, document, sprites = _corpus(payload_sizes={0: 0x60})
    frozen = tuple(
        Anchor(a.identity, a.range, a.kind, a.owner, a.alignment, False, a.provenance)
        if a.identity.value.endswith("graphic:0000") else a
        for a in document.anchors
    )
    sprites._document = RomDocument.from_bytes(image, profile, anchors=frozen,
                                               references=document.references)
    identity = _identity(0)
    with pytest.raises(ga.GraphicsAuthoringError, match="not published relocatable"):
        ga.plan_graphic_overrides(image, None, {identity: _override(identity)},
                                  sprites=sprites)


def test_a_payload_with_no_confirmed_consumer_is_refused():
    """The defensive half of the same rule, reachable only from a foreign document.

    The shared eligibility rule refuses an anchor nothing points at, so this
    branch cannot arise from `ActorSprites.reference_document`. It is still
    checked, because a document produced anywhere else must not be able to move
    a payload with no consumer to repoint.
    """
    image, profile, _, sprites = _corpus(payload_sizes={0: 0x60})
    references = tuple(r for r in _references(profile) if not r.target.value.endswith("0000"))
    sprites._document = _document(image, profile, references, eligible=False,
                                  relocatable=(True, True))
    identity = _identity(0)
    with pytest.raises(ga.GraphicsAuthoringError, match="no confirmed reference"):
        ga.plan_graphic_overrides(image, None, {identity: _override(identity)},
                                  sprites=sprites)


def test_a_candidate_consumer_withdraws_relocatability_for_that_graphic():
    """One unresolved numeric hit is enough to refuse the whole move."""
    image, profile, document, sprites = _corpus(candidate=True,
                                                payload_sizes={0: 0x60, 1: 0x60})
    anchor = document.anchor(AnchorId(_identity(0)))
    assert anchor.relocatable is False, "the candidate must have withdrawn eligibility"
    identity = _identity(0)
    with pytest.raises(ga.GraphicsAuthoringError, match="not published relocatable"):
        ga.plan_graphic_overrides(image, None, {identity: _override(identity)},
                                  sprites=sprites)
    # The OTHER graphic, whose consumer set is entirely confirmed, still moves:
    # the withdrawal is per payload, not a global switch.
    other = _identity(1)
    result = ga.plan_graphic_overrides(image, None, {other: _override(other)},
                                       sprites=sprites)
    assert len(result.relocations) == 1


def test_allocator_exhaustion_is_reported_and_nothing_is_planned():
    image, profile, document, sprites = _corpus(payload_sizes={0: 0x60})
    # No free region and no expansion: there is nowhere legitimate to go.
    _, bare, _ = _world(free=False, expansion=False)
    sprites.profile = bare
    identity = _identity(0)
    with pytest.raises(InsufficientSpaceError):
        ga.plan_graphic_overrides(image, None, {identity: _override(identity)},
                                  sprites=sprites)


def test_planning_nothing_returns_nothing():
    image, _, _, sprites = _corpus()
    result = ga.plan_graphic_overrides(image, None, {}, sprites=sprites)
    assert result.changes == () and result.reserved == ()
    assert result.generated_allocations == () and result.relocations == ()
    assert sprites.encoded == []
