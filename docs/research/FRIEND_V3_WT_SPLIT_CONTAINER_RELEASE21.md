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

The replacement is 26 units longer than the text it replaces, so it is **relocated**: the
string is appended past the end of the image, 4-byte aligned, with its terminator, and the
slot's single pointer at file `0x6BCE8 + 1083*4` is repointed from `0x089491E8` to
`0x089AC618`. The old span's bytes are left in place, past the new string's terminator, where
no reader reaches them.

The builder refuses unless the slot's bytes are exactly the text the approval replaces, and
it refuses a grown site that is named by more than one word-aligned reference, because moving
a string something else also points at would orphan that reader. This site had exactly one
reference: its own table entry.

## Verified

| check | result |
| --- | --- |
| slot 1083 reads the owner's replacement exactly | PASS |
| slot 1083 points at the write the plan made, file `0x9AC618` | PASS |
| the other 1,533 slots read the same text as the base | PASS, 0 drifted |
| bytes differing from the base outside the declared site | 0 |
| output byte count matches the manifest | PASS |
| reproduced twice | byte-identical, both `7ecad484…` |
| BOOST absence: the 25 bytes the BOOST builder declares all hold the foundation's byte | PASS, 25 of 25, and the BOOST image differs at all 25 so the check is not vacuous |

## Runtime check

The scanner entry is verified statically and by the release's own verifier. Whether a running
game renders it on the scanner screen, and on which save, is recorded in
`FRIEND_V3_WT_SPLIT_CONTAINER_RELEASE21_RUNTIME.md`; the claim is not widened here.

## Save compatibility

Unchanged from release 2: no save layout, game code or base-stat table is touched. Battery
saves carry over; a savestate made on an older image can show text it already copied.

## Continuity note for owner review

The replacement removes the Ox-King parentage line that the retail text carried. It is the
owner's own wording and is recorded here rather than reconciled against any other biography.
