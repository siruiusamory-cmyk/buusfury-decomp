# FRIEND-V3-WT-SPLIT-CONTAINER-001, release 2.1: Bulma's scanner biography

A one-slot correction to release 2, delivered before the release-3 work because the owner
wants it in the build that gets streamed.

## What ships

| field | value |
| --- | --- |
| file | `v3-wt-split-bio1083-a.gba` |
| bytes | 10,143,490 |
| SHA-256 | `7ecad4844b603fa4ad99734fcf654846be532ebd5c27149ae7dc56e9184e4000` |
| base | release 2 `v3-wt-split-a.gba`, sha256 `0b5ac8f470277f3c674710e07ce9d744433acd6a331736a628e00d6f72a6ef22`, 10,143,256 bytes |
| builder | `tools/research/apply_friend_v3_text_slot.py` |
| verifier | `tools/research/verify_friend_v3_text_slot.py` |

The artifact lives under the ignored `build/` tree and is not in git.

## The edit

One table slot, and nothing else.

**Before** (slot 1083, 90 units, file `0x9491E8`):

```
Bulma is Yamcha's wife and Krillin and Videl's mother. She is the daughter of the Ox-King.
```

**After** (116 units, file `0x9AC618`):

```
Bulma is Yamcha's wife and Krillin and Videl's mother. A genius inventor, she is the heiress of Capsule Corporation.
```

The replacement is 26 units longer than the text it replaces (116 units against 90, 232 bytes
plus a terminator), so it is **relocated**: the string is appended past the end of the image,
4-byte aligned, with its terminator, and the slot's single pointer at file
`0x6BCE8 + 1083*4` is repointed from `0x089491E8` to `0x089AC618`. The old span's bytes are
left in place, past the new string's terminator, where no reader reaches them.

The approved wording is a **tracked constant** in
`tools/research/friend_v3_text_approvals.py`, not a field of the manifest. The builder refuses
a slot without an approved entry and refuses text that does not match it, so the manifest's
copy cannot be the only authority for the wording, and the verifier recomputes the expected
text from the constant rather than reading it out of the artifact it is checking.

The builder also refuses a grown site that is named by more than one word-aligned reference,
because moving a string something else also points at would orphan that reader. This site had
exactly one reference: its own table entry.

## Verified

| check | result |
| --- | --- |
| slot 1083 reads the owner's approved wording exactly, recomputed from the tracked approval constant rather than from the manifest | PASS |
| the manifest's own copy of the wording agrees with the tracked approval | PASS |
| slot 1083 points at the write the plan made, file `0x9AC618` | PASS |
| the other 1,533 slots read the same text as the base | PASS, 0 drifted |
| differing bytes in the shared range, and the old span | 3 pointer bytes; the 182-byte old span at file `0x9491E8` is byte-identical to the base; 234 bytes appended |
| output byte count matches the manifest | PASS |
| reproduced twice | byte-identical, both `7ecad484…` |
| BOOST absence, re-measured on this image: the 25 bytes the BOOST builder declares all hold the foundation's byte | PASS, 25 of 25, and the BOOST image differs at all 25 so the check is not vacuous |
| the relocation guard's refusal path and its word alignment | `tests/unit/test_friend_v3_text_slot.py`, 6 passed |

## A disputed number, resolved by counting

The independent review of this release reported the replacement as **115** units and the
manifest and this document as wrong by one. The count is **116**: the first sentence is 54
units, the second is 61, and the space between them is the 116th. The review's own
decomposition read the first sentence as 55 and the second as 60, which does not sum to either
figure consistently, and its byte argument does not hold: 232 bytes is 116 units exactly, and
the append is 234 bytes = 232 + the 2-byte terminator, with the file 4-byte aligned afterwards.
The manifest field `new_units` now sits beside `new_bytes` and `new_span_bytes` so the three
numbers can be checked against each other.

## Runtime check

Static only, so far, and it is stated rather than pointed at. The runtime lane measured the
surface before it could run anything:

- slot 1083 is an **appearance record** field, not a loose string: appearance record 22 at file
  `0x74D4E0` carries name index 1082 and text index 1083, and the character screen draws
  exactly that pair. The engine fetches the description at `0x080252E6`-`0x080252EC` and the
  name at `0x080251B4`-`0x080251C2`, so a breakpoint there sees slot 1083's pointer being read.
- no available battery save can put Bulma on that screen: the seen-appearance bit for record 22
  is bit 6 of `0x0300112F`, and the map-134 route save has only index 17 set, the
  post-tournament save has 54 indices without 22, and the retail save has only 17.

**No run has shown the entry on screen yet**, so this release is statically verified only. The
one emulator slot is held by a hand-launched session, which the runtime lane will not stop
without the owner's word. If a run lands, it is recorded in
`FRIEND_V3_WT_SPLIT_CONTAINER_RELEASE21_RUNTIME.md`.

## Save compatibility

Unchanged from release 2: no save layout, game code or base-stat table is touched. Battery
saves carry over; a savestate made on an older image can show text it already copied.

## Continuity note for owner review

The replacement removes the Ox-King parentage line that the retail text carried. It is the
owner's own wording and is recorded here rather than reconciled against any other biography.
