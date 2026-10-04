# SPRITE-NEW-ATTACHMENT-CORE-001: attaching one new actor to a map object array

Baseline `origin/master` = `5f3fab5fdd9fa57da73d1e3fb16efab76de7c9c7`. Ticket branch
`ticket/sprite-new-attachment-core-001`. Canonical image (sha256 `940ad5f0...36f059e`)
read only and re-verified after every run.

## Verdict

**The research controlled-actor emitter is no longer required to plan the proven
Cui attachment.** `tools/webfoot/sprite_attachment.py` plans the map-102 case in
production, through the shared allocator and the shared write path, and imports
no research module at all. This ticket is the planner only: no CLI, no project
surface, no `sprite_identity.py` change, no placement-authoring generalization,
and no frame-composition-budget work.

## 1. The mechanism that moved

`docs/research/SPRITE_NEW_RUNTIME.md`, `SPRITE_NEW_RECORD_RUN.md`,
`SPRITE_NEW_BEHAVIOR_REGISTRATION.md` and `SPRITE_NEW_MOVEMENT_DATA.md` established
the mechanism across four runtime tickets. What the production planner takes from
them:

| fact | standing |
| --- | --- |
| the engine's object loop reads its bound from `MapEntry+0x04` (`ldrb`) and its base from `+0x14`, with no sentinel | CONFIRMED (TOOLKIT-024, re-used) |
| a new actor means a new slot: the array is re-emitted one element longer and the field that named the old array is repointed | measured at runtime |
| the record's `+0x18` is the dispatcher's entry word, and `table[0] = *(record+0x14)` is the entry count | CONFIRMED statically and at runtime |
| a record whose `+0x18` names some other record's entry inherits that entry's behaviour; naming its OWN entry is what makes it dispatch its own | measured (one word, `br010-after`) |
| the class-`0x0800A7A1` entry carries the wander box as four halfwords at entry `+0x08`, and the class-A walk method accepts a step only while the translated actor rect stays inside it | measured (`mv003-bounds` made the actor walk) |
| the record's `+0x0C` is retained data, not the movement boundary | measured (`mv001-data` changed nothing) |
| `MapEntry+0x2C` and the run's tail do not move when only the array does | measured in the parity composition |

### The record family, measured on the canonical image

Map 102's `MapEntry` is at file `0x08F930`: zone/area/variation `1/1/3`, count 10,
array `0x080784B4`, `+0x2C` slice base `0x0807830C`. The ten slot pointers run
`0x0807831C` to `0x08078498`. A record is `0x1C` bytes of header followed by an
inline behaviour entry:

```text
+0x00  factory        0x08017DA3
+0x04  retained word  measured: 0 on nine of the ten; slot 0 holds 0x08078310
+0x08  position u32   low half = map x, high half = map y
+0x0C  retained pointer, in the ROM window on all 191 sibling slots
+0x10  sprite id
+0x14  entry count (1 on all ten)
+0x18  the dispatcher's entry word
+0x1C  the behaviour entry: +0x00 class word, +0x04 0x00000080 on all seven
      class-A entries, +0x08..+0x0F the four box halfwords
```

The run census is the reason the planner authors `+0x18` explicitly instead of
copying a neighbour: `+0x18` is `record+0x1C` on 81 of the image's 191 sibling
slots, the address `0x080716EC` on 67, and something else on 44. A clone that
inherits one is a clone that inherits another actor's behaviour, which is exactly
what the registration ticket measured.

A whole-image census over those 191 slots also decided two API fields: `+0x04` is
0 on 82 of them and a pointer or small value on the rest, and `+0x0C` is inside
the ROM window on all 191. Neither has a proven meaning, so both are caller-
supplied retained words rather than defaults this planner would invent.

For map 102 the old array address occurs exactly once in the image as a
word-aligned word: `0x08F944`, the `MapEntry+0x14` field itself. The planner
re-measures that census and refuses if anything else names the array, rather than
rewriting a reference it has not modelled.

## 2. The production API

`tools/webfoot/sprite_attachment.py`:

- `SupportedActorFamily`: one measured layout per family, with the field offsets
  above. `SUPPORTED_FAMILIES` has exactly one member, `map-sibling-08017da3`.
- `WanderBox(x1, y1, x2, y2)`: the four map-pixel bounds, authored explicitly.
  The planner neither chooses a box nor checks it against the position.
- `NewMapActor(map_index, family, sprite_id, position, flags_raw,
  data_pointer_raw, behaviour_entry, wander_box)`: the caller's request. Every
  field the SDK has not proven a meaning for is supplied, not inferred.
- `AuthoredMapActor` and `ActorAttachment`: the result, in the same four-field
  shape every authoring domain returns (`changes`, `reserved`,
  `generated_allocations`, `relocations`) so a caller threads it into
  `write.plan_changes` unchanged.
- `plan_new_map_actor(image, identification, request, *, profile=None,
  reserved=())`: pure. It reads the MapEntry through the map-entry codec, walks
  the array with the engine's own counted walk
  (`formats.map_placements.iter_object_slots`), allocates the new record and the
  re-emitted array with `allocation.allocate` under the new
  `AllocationKind.MAP_OBJECT_RECORD` and `PLACEMENT_REFERENCE_ARRAY`, both
  `EXPANDED_ONLY`, and emits four attributed changes.

It refuses, naming the reason, when: the family is not supported; any existing
slot is another family (including the other sibling factory `0x080111A9` and the
`0x0800FD55` placement family); the array is named by any word other than its own
MapEntry field; the map declares no object array; the array is already 255 slots;
the behaviour entry is the wrong size or leads with another class word; the wander
box is inverted or out of range; the retained data pointer is outside the image
window; the sprite id is not one; the profile declares no map table, the wrong
record size, or a different image size.

## 3. What is proven where

Portable, `tests/unit/test_sprite_attachment_authoring.py`, over synthetic bytes:
the object bound increases by exactly one; the MapEntry field repoints to the new
array; the new array carries every existing slot verbatim plus the new record's
address; the new record carries the requested sprite id, position, flags and
count; `+0x18` names the record's own inline entry and the class word is there;
`+0x0C` equals the requested pointer; the box bytes are the requested four
halfwords; every existing record and the old array are byte-identical; only the
bound byte and the array field move canonically; the other map is untouched; both
spans are above EOF and outside the declared free region; the relocation record
names the field it rewrote; two identical requests plan byte-identically; a second
attachment sharing the first's reservation set lands elsewhere; and each refusal
above.

ROM-gated, `tests/integration/test_sprite_attachment_rom.py`, against the
canonical image: the fixture is the measured map-102 array (10 slots, all
`0x08017DA3`, base `0x080784B4`); the ten retail records are byte-identical and
the bound goes 10 to 11; the new array pointer is the re-encoded array; the new
record is the controlled actor the runtime ran (donor factory and retained words,
sprite 307, position, donor data pointer); `+0x18` names the inline entry whose
class word is `0x0800A7A1` and whose box is the authored one; the relocation is
recorded; unrelated maps are unchanged; planning is deterministic; the verified
identification resolves the same profile as the explicit one; and the canonical
file hash is unchanged afterwards.

No emulator run is part of this ticket.

## 4. Research logic replaced

`tools/research/sprite_new_runtime.py`'s `new-actor` arm and the controlled-actor
composition in `tools/research/sprite_new_parity.py` are no longer on any path
that plans the attachment. They remain as measurement instruments - the parity
tool still composes the runtime image against a recorded build digest - and the
production planner imports neither. The two planners' controlled actor is the
same shape: a donor-shaped record with the authored position, sprite id, inline
entry word and box.

## 5. Remaining work before runtime parity

- **No runtime run of the production planner yet.** The image the retail engine
  followed was composed by research code. Re-running the planner through the
  existing mGBA harness and observing the actor is the next ticket, and until it
  lands this is a planning capability, not a runtime one.
- **No caller.** Nothing in the project format, the build transaction or the
  command surface reaches `plan_new_map_actor`; wiring it into a build is
  deliberately out of this ticket.
- **The wander box is the caller's.** Nothing measures how a template's box
  relates to the actor's own spawn, so a box that does not contain the spawn
  declines every step. That is the measured behaviour, not a defect, and it is
  why the box is required rather than chosen.
- **The frame-composition budget is still unmodelled.** This planner appends any
  object; the budget that makes an actor's frame size safe at runtime is not
  checked here, and the identity planner's own note on it still stands.
- **The family's retained words are uninterpreted.** `+0x04` and `+0x0C` are
  carried, not understood, and no codec decodes the family's behaviour entries.
- Other open items from the runtime records - the direction-slot-to-facing
  mapping, dialogue and script bodies - are unchanged by this ticket.
