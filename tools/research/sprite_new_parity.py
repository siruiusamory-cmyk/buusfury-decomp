"""SPRITE-NEW-RUNTIME-PARITY-001: build the runtime image from the production planner.

The ticket this serves asks one question: can the supported API,
``webfoot.sprite_identity.plan_new_sprite_identity``, produce the identity the
landed runtime experiment proved? This script answers it by construction and by
comparison, then hands the emulator an image whose **identity** comes from the
production planner and whose **controlled actor harness** comes from the research
tooling that already produced the walking build.

What is production and what is research is kept explicit:

* the identity - the grown registry, the new character structure, the two
  animation records, the 24 frame records, the 24 packed containers and the
  object-palette entries the art needs - is planned by
  :func:`webfoot.sprite_identity.plan_new_sprite_identity`;
* the controlled actor - map 102's object array re-emitted one element longer, the
  new object record, its ``+0x18`` registration word, its ``+0x0C`` data pointer
  and the widened wander box - is copied verbatim out of the research build the
  movement ticket measured. That part is placement authoring and is deliberately
  not productized.

Two identity variants are emitted from the same sheets, because the sheets are
5-bit artwork stored in 8-bit channels and the two 8-bit encodings of one 5-bit
value are not the same number:

* ``as-authored`` - the production planner on the sheets exactly as they are
  drawn. This is the honest end-to-end path and the image the emulator runs.
* ``palette-grid`` - the same planner on the same artwork expressed in the
  object palette's own canonical 8-bit form, ``(v << 3) | (v >> 2)``. The change
  is lossless and involves no rounding decision (``v = channel >> 3`` is exact for
  this art), and it isolates the mechanism from the art's encoding.

    python tools/research/sprite_new_parity.py \\
        --rom <canonical> --stand <stand.png> --walk <walk.png> \\
        --reference <research bounds image> --reference-manifest <research json> \\
        --identity-out <gba> --runtime-out <gba> --manifest <json>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_REPO = _HERE.parents[2]
_TOOLS = _HERE.parents[1]
for _candidate in (str(_REPO), str(_TOOLS)):
    if _candidate not in sys.path:
        sys.path.insert(0, _candidate)

CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
ROM_BASE = 0x08000000

#: The identity the runtime experiment authored, and the donor whose own 32x32
#: frame geometry every authored frame copies.
NEW_SPRITE_ID = 307
DONOR_SPRITE_ID = 10

#: The object-palette entries SPRITE-NEW-RUNTIME-001 measured as drawn by no
#: actor-sprite graphic and no portrait payload. They are offered here as the
#: caller's explicit claim about which entries are free.
RESEARCH_FREE_ENTRIES = (6, 8, 9, 103, 193, 217, 218, 223, 224, 225, 236)

#: The sheets the runtime experiment's identity carries, in animation-slot order.
SHEETS = (("stand", 2), ("walk", 4))
CELL_SIDE = 32


class ParityError(ValueError):
    """An input this comparison cannot honour."""


def read_sheet(path: Path, *, palette_grid: bool):
    """One Cui sheet as a production :class:`SourceSheet`.

    The sheet is one row of ``32x32`` cells and the production field holds its
    cells laid end to end in sheet order, so each cell is extracted row-major and
    appended. The sheet's own frame count is derived from its width, which is what
    the research reader does as well.

    ``palette_grid`` rewrites each channel to the 8-bit form the object palette
    itself stores. That is exact here - the art is 5-bit, in either the
    zero-padded or the bit-replicated form of the same value - and it is done
    before the planner sees the pixels, so it decides nothing the planner owns.
    """
    from PIL import Image

    from webfoot.formats import sprite_graphics as sg
    from webfoot.sprite_identity import SourceSheet

    with Image.open(path).convert("RGB") as image:
        width, height = image.size
        if height != CELL_SIDE or width % (CELL_SIDE * 4):
            raise ParityError(
                f"{path.name} is {width}x{height}; the measured sheet layout is one "
                f"row of {CELL_SIDE}x{CELL_SIDE} cells in four-cell facing groups")
        cells = width // CELL_SIDE
        pixels = image.load()
        out = bytearray()
        five_bit = True
        for cell in range(cells):
            for y in range(CELL_SIDE):
                for x in range(CELL_SIDE):
                    colour = pixels[cell * CELL_SIDE + x, y]
                    for channel in colour:
                        five = channel >> 3
                        if channel not in ((five << 3),
                                           sg.expand_rgb888_channel(channel)):
                            five_bit = False
                    if palette_grid:
                        colour = tuple(sg.expand_rgb888_channel(channel)
                                       for channel in colour)
                    out += bytes(colour)
    if not five_bit:
        raise ParityError(
            f"{path.name} carries a channel that is not a 5-bit value in either "
            "encoding, so the palette-grid rewrite would not be lossless")
    return cells // 4, SourceSheet(frames_per_direction=cells // 4,
                                   cell_width=CELL_SIDE, cell_height=CELL_SIDE,
                                   pixels=bytes(out))


def identity_ranges(materialization):
    """Every span of the emitted image that carries only identity material."""
    authored = materialization.identity
    spans = [("containers", authored.containers_range),
             ("registry", authored.registry_range),
             ("structure", authored.structure_range)]
    for animation in authored.animations:
        spans.append((f"animation:{animation.name}", animation.animation_range))
        for frame in animation.frames:
            spans.append((f"frame:{animation.name}:{frame.slot}",
                          frame.record_range))
    return spans


def build_variant(name, canonical, identification, profile, sheets, palette_grid,
                  free_entries, reference, reference_manifest, out_dir,
                  reference_digest):
    """Plan one identity, compose the runtime image, and compare both."""
    from webfoot.sprite_identity import (AnimationSource, NewSpriteIdentity,
                                         plan_new_sprite_identity)
    from webfoot.write import apply_plan, plan_changes

    animations = []
    for sheet_name, expected_frames in SHEETS:
        frames, sheet = read_sheet(sheets[sheet_name], palette_grid=palette_grid)
        if frames != expected_frames:
            raise ParityError(
                f"{name}/{sheet_name}: the sheet holds {frames} frames per facing, "
                f"but the runtime experiment's identity carries {expected_frames}")
        animations.append(AnimationSource(name=sheet_name, sheet=sheet))
    identity = NewSpriteIdentity(
        sprite_id=NEW_SPRITE_ID, donor_sprite_id=DONOR_SPRITE_ID,
        animations=tuple(animations), free_palette_entries=tuple(free_entries))

    materialization = plan_new_sprite_identity(canonical, identification, identity)
    generated = profile.generated_expansion.generated_image(
        len(canonical),
        tuple(a.allocated_range for a in materialization.generated_allocations))
    plan = plan_changes(
        canonical, materialization.changes, profile_id=profile.id,
        base_sha256=profile.sha256, relocations=materialization.relocations,
        generated_image=generated,
        generated_allocations=materialization.generated_allocations)
    identity_image = apply_plan(canonical, plan)
    identity_path = out_dir / f"{name}-identity.gba"
    identity_path.write_bytes(identity_image)

    spans = identity_ranges(materialization)

    # --- the controlled actor, re-emitted after the identity block ------------
    # The movement builder wraps the runtime planner's report, so the actor block
    # is either at the top level or inside the wrapped identity report.
    actor_report = reference_manifest.get("controlled_actor") \
        or reference_manifest["base_identity_report"]["controlled_actor"]
    placement = actor_report["placement"]
    array = actor_report["array"]

    # The production identity's own length decides where the harness can go, so
    # the array and the object record are re-emitted in the first free word-aligned
    # span above it rather than copied to the addresses the research build happened
    # to use. Only three words have to move with them: the array's last element,
    # which names the record, and the record's ``+0x18``, which names its own
    # behaviour template at ``+0x1C``.
    records_end = (max(span.end for _name, span in spans) + 3) & ~3
    array_at = records_end
    record_at = array_at + 4 * array["new_count"]
    record_template = reference[int(placement["file_offset"], 16):
                                int(placement["file_offset"], 16) + placement["size"]]
    if len(record_template) != placement["size"]:
        raise ParityError(f"{name}: the research object record is short")
    retail_array = canonical[int(array["old_file_offset"], 16):
                             int(array["old_file_offset"], 16)
                             + 4 * array["old_count"]]
    if len(retail_array) != 4 * array["old_count"]:
        raise ParityError(f"{name}: the retail object array is short")
    new_array = bytearray(retail_array) + (ROM_BASE + record_at).to_bytes(4, "little")
    new_record = bytearray(record_template)
    new_record[0x18:0x1C] = (ROM_BASE + record_at + 0x1C).to_bytes(4, "little")

    actor_writes = [
        ("actor:object-array", array_at, bytes(new_array)),
        ("actor:placement", record_at, bytes(new_record)),
        ("actor:object-count", int(array["count_field_file_offset"], 16),
         bytes([array["new_count"]])),
    ]
    for rewrite in array["references_rewritten"]:
        start = int(rewrite["file_offset"], 16)
        actor_writes.append((f"actor:array-pointer@{rewrite['file_offset']}", start,
                             (ROM_BASE + array_at).to_bytes(4, "little")))

    runtime = bytearray(identity_image)
    for region_name, start, payload in actor_writes:
        end = start + len(payload)
        for span_name, span in spans:
            if start < span.end and span.start.value < end:
                raise ParityError(
                    f"{name}: the controlled actor region {region_name} overlaps "
                    f"the identity region {span_name}")
        runtime[start:end] = payload
    runtime_bytes = bytes(runtime)
    runtime_path = out_dir / f"{name}-runtime.gba"
    runtime_path.write_bytes(runtime_bytes)

    # --- comparisons --------------------------------------------------------
    region_comparison = []
    for span_name, span in spans:
        start, end = span.start.value, span.end
        left, right = identity_image[start:end], reference[start:end]
        first = next((offset for offset in range(start, end)
                      if identity_image[offset] != reference[offset]), None)
        region_comparison.append({"region": span_name, "file_offset": start,
                                  "size": end - start,
                                  "identical": left == right,
                                  "first_difference": first})

    def differing(left: bytes, right: bytes) -> list[int]:
        return [index for index in range(len(left)) if left[index] != right[index]]

    def canonical_changes(image: bytes) -> list[int]:
        return differing(canonical, image[:len(canonical)])

    frame_map = []
    for animation in materialization.identity.animations:
        for frame in animation.frames:
            frame_map.append({
                "rom_address": f"0x{frame.record_range.start.to_gba_address(len(identity_image)).raw:08X}",
                "file_offset": frame.record_range.start.value,
                "animation": animation.name,
                "animation_slot": animation.slot,
                "slot": frame.slot,
                "frame_index": frame.frame_index,
                "direction": frame.direction,
                "sheet_cell": frame.sheet_cell,
                "container_file_offset": frame.container_range.start.value,
            })

    return {
        "identity_out": str(identity_path),
        "identity_sha256": hashlib.sha256(identity_image).hexdigest(),
        "identity_size": len(identity_image),
        "runtime_out": str(runtime_path),
        "runtime_sha256": hashlib.sha256(runtime_bytes).hexdigest(),
        "runtime_size": len(runtime_bytes),
        "free_entries_offered": list(free_entries),
        "palette_entries_written": [entry.to_json()
                                    for entry in materialization.identity.palette_entries],
        "identity": materialization.identity.to_json(),
        "identity_allocations": [a.to_json() for a in
                                 materialization.generated_allocations],
        "identity_relocations": [r.to_json() for r in materialization.relocations],
        "identity_changed_canonical_offsets": [
            f"0x{offset:06X}" for offset in canonical_changes(identity_image)],
        "runtime_changed_canonical_offsets": [
            f"0x{offset:06X}" for offset in canonical_changes(runtime_bytes)],
        "runtime_copies": [{"region": region_name, "file_offset": start,
                            "size": len(payload)}
                           for region_name, start, payload in actor_writes],
        "identity_region_comparison": region_comparison,
        "identity_material_identical": all(item["identical"]
                                           for item in region_comparison),
        "identity_identical_region_count": sum(1 for item in region_comparison
                                               if item["identical"]),
        "identity_region_count": len(region_comparison),
        "container_bytes_differing": next(
            (item["size"] - sum(1 for offset in range(item["file_offset"],
                                                      item["file_offset"] + item["size"])
                                if identity_image[offset] == reference[offset])
             for item in region_comparison if item["region"] == "containers"), 0),
        "runtime_vs_reference_differences": [
            f"0x{offset:06X}" for offset in differing(runtime_bytes, reference)],
        "runtime_vs_reference_difference_count": len(differing(runtime_bytes, reference)),
        "frame_map": frame_map,
        "reference_digest_expected": reference_digest,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--rom", required=True, help="the canonical image")
    parser.add_argument("--stand", required=True, help="the stand sheet PNG")
    parser.add_argument("--walk", required=True, help="the walk sheet PNG")
    parser.add_argument("--reference", required=True,
                        help="the research build to compare against and to take "
                             "the controlled actor from")
    parser.add_argument("--reference-manifest", required=True,
                        help="that build's research manifest")
    parser.add_argument("--out-dir", required=True,
                        help="where the variant images are written")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--free-entries", default=",".join(
        str(index) for index in RESEARCH_FREE_ENTRIES))
    args = parser.parse_args(argv)

    from webfoot.profile import RomProfileCatalog
    from webfoot.rom import identify_rom

    canonical_path = Path(args.rom)
    canonical = canonical_path.read_bytes()
    if hashlib.sha256(canonical).hexdigest() != CANONICAL_SHA256:
        raise ParityError("refusing: the input is not the canonical image")
    identification = identify_rom(canonical_path, RomProfileCatalog.load(
        str(_REPO / "config" / "roms.yaml")))
    profile = identification.profile_match.profile

    reference = Path(args.reference).read_bytes()
    reference_manifest = json.loads(
        Path(args.reference_manifest).read_text(encoding="utf-8"))
    reference_digest = hashlib.sha256(reference).hexdigest()

    free_entries = tuple(int(part) for part in args.free_entries.split(",") if part)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    as_authored = build_variant(
        "as-authored", canonical, identification, profile,
        {"stand": Path(args.stand), "walk": Path(args.walk)}, False, free_entries,
        reference, reference_manifest, out_dir, reference_digest)
    palette_grid = build_variant(
        "palette-grid", canonical, identification, profile,
        {"stand": Path(args.stand), "walk": Path(args.walk)}, True, free_entries,
        reference, reference_manifest, out_dir, reference_digest)

    report = {
        "ticket": "SPRITE-NEW-RUNTIME-PARITY-001",
        "canonical_sha256": hashlib.sha256(canonical).hexdigest(),
        "reference": {"path": str(args.reference), "sha256": reference_digest},
        "variants": {"as-authored": as_authored, "palette-grid": palette_grid},
    }
    Path(args.manifest).write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    for name, variant in report["variants"].items():
        print(f"=== {name}")
        print("  identity sha256:", variant["identity_sha256"])
        print("  runtime  sha256:", variant["runtime_sha256"])
        print("  palette entries written:",
              [(e["index"], e["word_hex"]) for e in variant["palette_entries_written"]])
        print("  identity regions identical to the research build:",
              f"{variant['identity_identical_region_count']}/"
              f"{variant['identity_region_count']}")
        print("  container bytes differing:",
              variant["container_bytes_differing"])
        print("  runtime vs reference differing bytes:",
              variant["runtime_vs_reference_difference_count"])
        print("  canonical offsets changed:",
              variant["identity_changed_canonical_offsets"])
    print("=== reference", reference_digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
