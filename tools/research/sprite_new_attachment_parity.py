"""SPRITE-NEW-ATTACHMENT-RUNTIME-PARITY-001: compose the runtime image from production.

Both halves of the runtime image come from the supported SDK in this ticket:

* the identity - the grown registry, the new character structure, its animation
  and frame records, the packed containers and the object-palette entries - is
  planned by :func:`webfoot.sprite_identity.plan_new_sprite_identity`;
* the controlled actor - map 102's object array re-emitted one element longer,
  the new object record, its ``+0x18`` entry word, its retained ``+0x04`` and
  ``+0x0C`` words and its authored wander box - is planned by
  :func:`webfoot.sprite_attachment.plan_new_map_actor`.

Nothing here re-implements either planner. The research tooling this repository
already had for the attachment is used only as the **reference**: the proven
walking image is read to recover the actor's own inputs (sprite id, position,
retained words, behaviour entry and box) and to compare the result byte for byte.
That direction of use is the point of the ticket - the reference supplies the
parameters, the production planner decides the bytes.

The two production plans are merged the way a build merges domains: the identity
is planned first, its spans are handed to the attachment planner as the shared
reservation set, and both change lists go into one
:func:`webfoot.write.plan_changes` against the canonical image.

    python tools/research/sprite_new_attachment_parity.py \\
        --rom <canonical> --stand <stand.png> --walk <walk.png> \\
        --reference <the proven walking image> \\
        --out-dir <fresh directory> --manifest <fresh json path>
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
#: actor-sprite graphic and no portrait payload.
RESEARCH_FREE_ENTRIES = (6, 8, 9, 103, 193, 217, 218, 223, 224, 225, 236)

SHEETS = (("stand", 2), ("walk", 4))
CELL_SIDE = 32

#: The map the controlled actor is appended to, and the family the production
#: attachment planner supports.
MAP_INDEX = 102
FAMILY = "map-sibling-08017da3"

#: The proven build's own map-entry table location, read from the profile rather
#: than restated; these two are the fields the census and the count use.
MAP_ENTRY_SIZE = 0x38
COUNT_FIELD = 0x04
ARRAY_FIELD = 0x14

#: The engine's direction index for each frame-record slot.
DIRECTIONS = {0: "down", 1: "up", 2: "left", 3: "right"}


class AttachmentParityError(ValueError):
    """An input this composition cannot honour."""


def read_sheet(path: Path, *, palette_grid: bool):
    """One Cui sheet as a production :class:`SourceSheet`."""
    from PIL import Image

    from webfoot.formats import sprite_graphics as sg
    from webfoot.sprite_identity import SourceSheet

    with Image.open(path).convert("RGB") as image:
        width, height = image.size
        if height != CELL_SIDE or width % (CELL_SIDE * 4):
            raise AttachmentParityError(
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
        raise AttachmentParityError(
            f"{path.name} carries a channel that is not a 5-bit value in either "
            "encoding, so the palette-grid rewrite would not be lossless")
    return cells // 4, SourceSheet(frames_per_direction=cells // 4,
                                   cell_width=CELL_SIDE, cell_height=CELL_SIDE,
                                   pixels=bytes(out))


def word(image: bytes, offset: int) -> int:
    return int.from_bytes(image[offset:offset + 4], "little")


def reference_actor(reference: bytes, *, profile) -> dict:
    """The proven record's own inputs, read out of the proven image.

    The proven image is self-describing: map 102's object array was re-emitted
    with one more slot, and that last slot names the authored record. So the
    parameters the ticket says to keep - sprite id, position, the retained
    ``+0x04`` and ``+0x0C`` words, the class-A behaviour entry and the wander box
    - are read from the reference's own bytes instead of restated here.
    """
    from webfoot.formats import map_entry as me
    from webfoot.formats import map_placements as mp
    from webfoot.sprite_attachment import (FAMILY_MAP_SIBLING, WanderBox,
                                           supported_family)

    table = profile.map_entries
    entry_at = (table.address.to_file_offset(profile.size)
                + MAP_INDEX * table.record_size)
    record = me.MapEntry.from_bytes(reference[entry_at:entry_at + MAP_ENTRY_SIZE])
    count = record.trigger_count_raw
    array_at = record.scripts_pointer_raw - ROM_BASE
    if count != 11:
        raise AttachmentParityError(
            f"the reference's map 102 declares {count} object slots, not the 11 "
            "the proven composition wrote")
    slot = word(reference, array_at + 4 * (count - 1))
    at = slot - ROM_BASE
    family = supported_family(FAMILY_MAP_SIBLING)
    if word(reference, at) != family.factory_raw:
        raise AttachmentParityError(
            f"the reference's last array slot 0x{slot:08X} is not the supported "
            f"family 0x{family.factory_raw:08X}")
    entry = reference[at + family.entry_inline_offset:
                      at + family.entry_size + family.entry_inline_offset]
    if len(entry) != family.entry_size:
        raise AttachmentParityError("the reference's behaviour entry is short")
    if word(entry, 0) != family.entry_class_raw:
        raise AttachmentParityError(
            f"the reference's behaviour entry leads with 0x{word(entry, 0):08X}, "
            f"not the class word 0x{family.entry_class_raw:08X}")
    position = mp.decode_position(
        word(reference, at + family.position_offset) & 0xFFFF,
        (word(reference, at + family.position_offset) >> 16) & 0xFFFF)
    box = tuple(int.from_bytes(entry[family.box_offset + 2 * index:
                                     family.box_offset + 2 + 2 * index], "little")
                for index in range(4))
    return {
        "record_file_offset": at,
        "record_rom_address": f"0x{slot:08X}",
        "array_file_offset": array_at,
        "array_rom_address": f"0x{record.scripts_pointer_raw:08X}",
        "entry_file_offset": at + family.entry_inline_offset,
        "sprite_id": word(reference, at + family.sprite_id_offset),
        "position": list(position),
        "retained_04_raw": word(reference, at + family.retained_04_offset),
        "data_pointer_raw": word(reference, at + family.data_pointer_offset),
        "entry_word": word(reference, at + family.table_entry_offset),
        "behaviour_entry_hex": entry.hex(),
        "wander_box": list(box),
        "_wander_box": WanderBox(*box),
        "_behaviour_entry": entry,
    }


def build_variant(name, canonical_path, canonical, identification, profile, sheets,
                  palette_grid, free_entries, reference_bytes, out_dir):
    """Plan both halves in production, merge them, and compare with the proven build."""
    from webfoot.sprite_attachment import (FAMILY_MAP_SIBLING, NewMapActor,
                                           plan_new_map_actor)
    from webfoot.sprite_identity import (AnimationSource, NewSpriteIdentity,
                                         plan_new_sprite_identity)
    from webfoot.write import emit_image, plan_changes

    animations = []
    for sheet_name, expected_frames in SHEETS:
        frames, sheet = read_sheet(sheets[sheet_name], palette_grid=palette_grid)
        if frames != expected_frames:
            raise AttachmentParityError(
                f"{name}/{sheet_name}: the sheet holds {frames} frames per facing, "
                f"but the runtime experiment's identity carries {expected_frames}")
        animations.append(AnimationSource(name=sheet_name, sheet=sheet))
    identity = NewSpriteIdentity(
        sprite_id=NEW_SPRITE_ID, donor_sprite_id=DONOR_SPRITE_ID,
        animations=tuple(animations), free_palette_entries=tuple(free_entries))

    # --- half one: the identity, production
    materialization = plan_new_sprite_identity(canonical, identification, identity)

    # --- half two: the attached actor, production, sharing the reservation set
    actor = reference_actor(reference_bytes, profile=profile)
    request = NewMapActor(
        map_index=MAP_INDEX, family=FAMILY_MAP_SIBLING, sprite_id=actor["sprite_id"],
        position=tuple(actor["position"]), retained_04_raw=actor["retained_04_raw"],
        data_pointer_raw=actor["data_pointer_raw"],
        behaviour_entry=actor["_behaviour_entry"],
        wander_box=actor["_wander_box"])
    attachment = plan_new_map_actor(canonical, None, request, profile=profile,
                                    reserved=materialization.reserved)

    # --- one merged plan, exactly as a build merges two domains
    generated_allocations = (materialization.generated_allocations
                             + attachment.generated_allocations)
    generated = profile.generated_expansion.generated_image(
        len(canonical), tuple(a.allocated_range for a in generated_allocations))
    plan = plan_changes(
        canonical, materialization.changes + attachment.changes,
        profile_id=profile.id, base_sha256=profile.sha256,
        relocations=materialization.relocations + attachment.relocations,
        generated_image=generated, generated_allocations=generated_allocations)
    runtime_path = out_dir / f"{name}-runtime.gba"
    emit_image(canonical_path, runtime_path, plan)
    runtime_bytes = runtime_path.read_bytes()
    return _describe(runtime_path, canonical, profile, reference_bytes, runtime_bytes,
                     materialization, attachment, actor)


def _describe(runtime_path, canonical, profile, reference_bytes, runtime_bytes,
              materialization, attachment, actor):
    """Compare the emitted image with the proven build and report the checks."""
    from webfoot.sprite_attachment import FAMILY_MAP_SIBLING

    identity_ranges = []
    authored_identity = materialization.identity
    identity_ranges.append(("containers", authored_identity.containers_range))
    identity_ranges.append(("registry", authored_identity.registry_range))
    identity_ranges.append(("structure", authored_identity.structure_range))
    for animation in authored_identity.animations:
        identity_ranges.append((f"animation:{animation.name}",
                                animation.animation_range))
        for frame in animation.frames:
            identity_ranges.append((f"frame:{animation.name}:{frame.slot}",
                                    frame.record_range))

    image_size = len(runtime_bytes)
    # The reference is one specific composition. Its own actor sits at the
    # addresses the palette-grid variant reproduces; the as-authored variant's
    # identity is 8 bytes longer, so its actor sits elsewhere and comparing that
    # region against the reference would compare unrelated bytes. Say so instead
    # of reporting a difference that is an artefact of the offset.
    comparable = (attachment.actor.record_range.start.value
                  == actor["record_file_offset"]
                  and attachment.actor.array_range.start.value
                  == actor["array_file_offset"])
    region_rows = []
    for region_name, span in identity_ranges:
        left = runtime_bytes[span.start.value:span.end]
        right = reference_bytes[span.start.value:span.end]
        region_rows.append({"region": region_name, "file_offset": span.start.value,
                            "size": span.size, "identical": left == right,
                            "first_difference": next(
                                (span.start.value + index
                                 for index in range(span.size)
                                 if left[index] != right[index]), None)})
    array_row = {
        "region": "map102:object-array",
        "comparable": comparable,
        "file_offset": attachment.actor.array_range.start.value,
        "size": attachment.actor.array_range.size,
        "identical": None if not comparable else (
            runtime_bytes[attachment.actor.array_range.start.value:
                          attachment.actor.array_range.end]
            == reference_bytes[attachment.actor.array_range.start.value:
                               attachment.actor.array_range.end])}
    record_row = {
        "region": "map102:object-record",
        "comparable": comparable,
        "file_offset": attachment.actor.record_range.start.value,
        "size": attachment.actor.record_range.size,
        "identical": None if not comparable else (
            runtime_bytes[attachment.actor.record_range.start.value:
                          attachment.actor.record_range.end]
            == reference_bytes[attachment.actor.record_range.start.value:
                               attachment.actor.record_range.end])}
    region_rows.extend([array_row, record_row])

    differing = [offset for offset in range(min(len(runtime_bytes), len(reference_bytes)))
                 if runtime_bytes[offset] != reference_bytes[offset]]

    # The ten retail object records and the retail array, straight out of the
    # emitted image: the ticket's own required checks.
    canonical_entry = profile.map_entries.address.to_file_offset(profile.size) \
        + MAP_INDEX * profile.map_entries.record_size
    canonical_array = word(canonical, canonical_entry + ARRAY_FIELD)
    retail_records = []
    for index in range(10):
        pointer = word(canonical, canonical_array - ROM_BASE + 4 * index)
        at = pointer - ROM_BASE
        retail_records.append({
            "slot": index, "rom_address": f"0x{pointer:08X}",
            "preserved": (runtime_bytes[at:at + 0x2C] == canonical[at:at + 0x2C])})
    new_array = attachment.actor.array_rom_address
    old_array_words = canonical[canonical_array - ROM_BASE:
                                canonical_array - ROM_BASE + 40]
    new_array_words = runtime_bytes[attachment.actor.array_range.start.value:
                                    attachment.actor.array_range.start.value + 40]
    record_at = attachment.actor.record_range.start.value

    frame_map = []
    for animation in authored_identity.animations:
        for frame in animation.frames:
            frame_map.append({
                "rom_address": f"0x{frame.record_range.start.to_gba_address(image_size).raw:08X}",
                "file_offset": frame.record_range.start.value,
                "animation": animation.name, "animation_slot": animation.slot,
                "slot": frame.slot, "frame_index": frame.frame_index,
                "direction": frame.direction, "sheet_cell": frame.sheet_cell,
                "container_file_offset": frame.container_range.start.value})

    canonical_changes = [offset for offset in range(len(canonical))
                         if runtime_bytes[offset] != canonical[offset]]

    return {
        "runtime_out": str(runtime_path),
        "runtime_sha256": hashlib.sha256(runtime_bytes).hexdigest(),
        "runtime_size": len(runtime_bytes),
        "identity": authored_identity.to_json(),
        "palette_entries_written": [entry.to_json()
                                    for entry in authored_identity.palette_entries],
        "identity_allocations": [a.to_json() for a in
                                 materialization.generated_allocations],
        "attachment_allocations": [a.to_json() for a in
                                   attachment.generated_allocations],
        "identity_relocations": [r.to_json() for r in materialization.relocations],
        "attachment_relocations": [r.to_json() for r in attachment.relocations],
        "canonical_changed_offsets": [f"0x{offset:06X}" for offset in canonical_changes],
        "canonical_changed_count": len(canonical_changes),
        "actor": {"request": {
            "map_index": MAP_INDEX, "family": FAMILY_MAP_SIBLING,
            "sprite_id": actor["sprite_id"], "position": actor["position"],
            "retained_04_raw": actor["retained_04_raw"],
            "data_pointer_raw": actor["data_pointer_raw"],
            "wander_box": actor["wander_box"]},
            "reference_record": actor["record_rom_address"],
            "reference_entry": f"0x{actor['entry_file_offset'] + ROM_BASE:08X}",
            "record_file_offset": record_at,
            "record_rom_address": f"0x{attachment.actor.record_rom_address:08X}",
            "array_file_offset": attachment.actor.array_range.start.value,
            "array_rom_address": f"0x{new_array:08X}",
            "behaviour_entry_address": f"0x{attachment.actor.behaviour_entry_address:08X}",
            "record_size": attachment.actor.record_range.size,
            "array_slots": attachment.actor.array_slots},
        "required_checks": {
            "existing_records_preserved": all(r["preserved"] for r in retail_records),
            "retail_records": retail_records,
            "count_is_eleven": runtime_bytes[canonical_entry + COUNT_FIELD] == 11,
            "map_entry_repoints_to_new_array":
                word(runtime_bytes, canonical_entry + ARRAY_FIELD) == new_array,
            "existing_array_words_verbatim":
                new_array_words[:40] == old_array_words,
            "last_array_slot_names_the_record":
                word(runtime_bytes, attachment.actor.array_range.start.value + 40)
                == attachment.actor.record_rom_address,
            "entry_word_names_own_entry":
                word(runtime_bytes, record_at + 0x18)
                == attachment.actor.record_rom_address + 0x1C,
            "sprite_id_is_the_requested_one":
                word(runtime_bytes, record_at + 0x10) == actor["sprite_id"],
            "retained_words_carried":
                (word(runtime_bytes, record_at + 0x04) == actor["retained_04_raw"]
                 and word(runtime_bytes, record_at + 0x0C) == actor["data_pointer_raw"]),
            "wander_box_is_the_requested_one":
                tuple(int.from_bytes(runtime_bytes[
                    record_at + 0x1C + 0x08 + 2 * index:
                    record_at + 0x1C + 0x0A + 2 * index], "little")
                    for index in range(4)) == tuple(actor["wander_box"])},
        "reference": {"record": actor["record_rom_address"],
                      "array": actor["array_rom_address"],
                      "retained_04_raw": actor["retained_04_raw"],
                      "data_pointer_raw": actor["data_pointer_raw"],
                      "entry_word": actor["entry_word"]},
        "region_comparison": region_rows,
        "regions_identical": sum(1 for row in region_rows if row["identical"]),
        "region_count": len(region_rows),
        "reference_difference_count": len(differing),
        "reference_differences": [f"0x{offset:06X}" for offset in differing[:64]],
        "reference_difference_truncated": len(differing) > 64,
        "frame_map": frame_map,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--rom", required=True)
    parser.add_argument("--stand", required=True)
    parser.add_argument("--walk", required=True)
    parser.add_argument("--reference", required=True,
                        help="the proven walking image, whose own last map-102 array "
                             "slot names the actor record to reproduce and against "
                             "which the palette-grid result is compared byte for byte")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--free-entries", default=",".join(
        str(index) for index in RESEARCH_FREE_ENTRIES))
    args = parser.parse_args(argv)

    from webfoot.profile import RomProfileCatalog
    from webfoot.rom import identify_rom
    from webfoot.write import ensure_new_destination, ensure_not_source_alias

    canonical_path = Path(args.rom)
    canonical = canonical_path.read_bytes()
    if hashlib.sha256(canonical).hexdigest() != CANONICAL_SHA256:
        raise AttachmentParityError("refusing: the input is not the canonical image")
    identification = identify_rom(canonical_path, RomProfileCatalog.load(
        str(_REPO / "config" / "roms.yaml")))
    profile = identification.profile_match.profile

    reference_path = Path(args.reference)
    reference_bytes = reference_path.read_bytes()

    free_entries = tuple(int(part) for part in args.free_entries.split(",") if part)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    sheets = {"stand": Path(args.stand), "walk": Path(args.walk)}

    variants = {}
    for name, palette_grid in (("as-authored", False), ("palette-grid", True)):
        variants[name] = build_variant(
            name, canonical_path, canonical, identification, profile, sheets,
            palette_grid, free_entries, reference_bytes, out_dir)

    report = {
        "ticket": "SPRITE-NEW-ATTACHMENT-RUNTIME-PARITY-001",
        "canonical_sha256": hashlib.sha256(canonical).hexdigest(),
        "reference": {"path": str(reference_path),
                      "sha256": hashlib.sha256(reference_bytes).hexdigest()},
        "variants": variants,
    }
    manifest_path = Path(args.manifest)
    ensure_not_source_alias(canonical_path, manifest_path)
    ensure_new_destination(manifest_path)
    manifest_path.write_text(json.dumps(report, indent=2, sort_keys=True),
                             encoding="utf-8")

    for name, variant in variants.items():
        print(f"=== {name}")
        print("  runtime sha256:", variant["runtime_sha256"])
        print("  actor record  :", variant["actor"]["record_rom_address"],
              " array", variant["actor"]["array_rom_address"],
              " entry", variant["actor"]["behaviour_entry_address"])
        print("  canonical bytes changed:", variant["canonical_changed_count"])
        print("  regions identical to the reference:",
              f"{variant['regions_identical']}/{variant['region_count']}")
        print("  reference byte differences:",
              variant["reference_difference_count"])
        print("  required checks:",
              {key: value for key, value in variant["required_checks"].items()
               if isinstance(value, bool)})
        frames = ",".join(str(int(frame["rom_address"], 16))
                          for frame in variant["frame_map"])
        print("  observer frames:", frames)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
