# FRIEND-V3-WT-SPLIT-CONTAINER-001, release 2: the World Tournament text release

This is the integration record for the cumulative mainline release that lands all fifteen
owner World Tournament rows on the split-container route. Route evidence is
`FRIEND_V3_WT_SPLIT_CONTAINER.md` (bytes) and `FRIEND_V3_WT_SPLIT_CONTAINER_RUNTIME.md`
(emulator).

## What ships

| field | value |
| --- | --- |
| file | `v3-wt-split.gba` |
| bytes | 10,143,256 |
| SHA-256 | `0b5ac8f470277f3c674710e07ce9d744433acd6a331736a628e00d6f72a6ef22` |
| base | `v3-mainline-text-dialogue-pass.gba`, sha256 `d2a25f9a56c9980e27ad4a6f4c23d653e87d15b71b908ee27bced48b88885543`, 10,141,220 bytes |
| base's lineage | the pre-BOOST foundation `a4c12a95…`; the BOOST image `acd98c2a…` is **not** an ancestor |
| builder | `tools/research/build_friend_v3_world_tournament_split.py` |
| verifier | `tools/research/verify_friend_v3_world_tournament_split.py` |
| reproducer | `tools/research/verify_friend_v3_boost_absence.py` for the BOOST check |

The artifact lives under the ignored `build/` tree and is not in git.

## The edit, exactly

Three changes, and nothing else:

1. **One appended container.** File offset `0x9ABE24` (runtime `0x089ABE24`), 4-byte aligned,
   header `kind=0` and `declared_size=2028`, then 2,028 bytes of UTF-16LE: the fifteen rows'
   texts laid out back to back. Each row's offset in that payload is its new decoded start.
2. **One table slot.** File `0x9A9D04` (selector 7, inside the table's own 64-slot block, past
   the seven live pointers, in copied retail data this image never reads):
   `0x03004A68` -> `0x089ABE24`.
3. **Fifteen handle words**, one per row, each at that record's single handle site, each
   rewritten from `DialogueHandle(3, old_start, old_length)` to
   `DialogueHandle(7, new_start, new_length)`.

No container byte of the original image moves, and no game code changes.

## The fifteen rows

| # | Speaker | Record | Units before | Units now | Route |
| --- | --- | --- | --- | --- | --- |
| 1 | Uub | `3:7406:136` | 68 | 86 | moved |
| 2 | Videl | `3:7542:42` | 21 | 34 | moved |
| 3 | Uub | `3:7584:80` | 40 | 36 | moved |
| 4 | Videl | `3:7664:60` | 30 | 44 | moved |
| 5 | Uub | `3:7724:72` | 36 | 31 | moved |
| 6 | Videl | `3:7796:204` | 102 | 51 | moved |
| 7 | Idasa | `3:8000:214` | 107 | 67 | moved |
| 8 | Uub | `3:8214:118` | 59 | 31 | moved |
| 9 | Idasa | `3:8332:218` | 109 | 74 | moved |
| 10 | Announcer | `3:8550:414` | 207 | 207 | unchanged |
| 11 | Gameplay instructions | `3:8964:148` | 74 | 74 | unchanged |
| 12 | Idasa | `3:9112:62` | 31 | 36 | moved |
| 13 | Uub | `3:9174:114` | 57 | 37 | moved |
| 14 | Idasa's mother | `3:9288:282` | 141 | 120 | moved |
| 15 | Tulma | `3:9570:92` | 46 | 46 | unchanged |
| 16 | Tulma | `3:9662:116` | 58 | 57 | moved |
| 17 | Idasa's mother | `3:9778:114` | 57 | 52 | moved |
| 18 | Announcer | `3:9892:486` | 243 | 258 | moved, passage replaced |

Twelve rows carry the owner's wording, three are unchanged, and row 18 has one passage
replaced while the rest of the announcement, its control units included, is preserved:

```
old:  Championship between eight-year-old Uub    and seven-year-old Videl!
new:  Championship between adopted siblings, ten-year-old Uub and sixteen-year-old Videl!
```

Every row keeps the control unit its record carried (fifteen of the eighteen begin `#`, the
others begin `!` or nothing). The `#` is why this ticket's overflow numbers differ by one unit
from the previous ticket's on rows 1, 2, 4 and 13: the approved wording is applied after the
record's own prefix, not in place of it.

**Why every row moved rather than only the five that grow.** All eighteen rows sit inside a
3,872-byte covering record (`3:6232:3872`, span 6232..10104 of container 3). Writing a shorter
text in place would leave bytes the covering record reads holding something else, which is the
defect the previous ticket measured on `1:38856:252`. The covering record does not move and its
bytes are untouched; only the eighteen handle words that the scene actually reads are
repointed, and the covering record still reads exactly what it read before.

## Verified

| check | result |
| --- | --- |
| every placed row resolves through the table the literal names, indexed by its handle's selector, and reads the approved wording back exactly | PASS, 15 of 15 |
| the three unchanged rows are byte-identical to the base | PASS |
| the seven live slots are byte-identical to the base | PASS |
| the other 63 table slots are byte-identical to the base | PASS |
| bytes differing from the base outside the declared sites | 0 |
| output byte count matches the manifest | PASS |
| reproduced twice | byte-identical, both `0b5ac8f4…` |
| BOOST absence: the 25 bytes the BOOST builder declares all hold the foundation's byte | PASS, 25 of 25, and the BOOST image differs at all 25 (the check is not vacuous) |
| the row table's own integrity (unique identities, three no-change rows, unshortened wordings) | `tests/unit/test_friend_v3_world_tournament_rows.py`, PASS |

## Runtime check

Recorded in `FRIEND_V3_WT_SPLIT_CONTAINER_RUNTIME.md` and in the release's own run: the World
Tournament scene in mGBA on this candidate, which this release exists to get in front of a
stream. The verdict and its exact row are stated there and not restated here.

## Save compatibility

Battery saves are compatible: no stage touches the save layout, the game code or the base-stat
table. A savestate written on the base image is not interchangeable with one written on this
release, for the same reason it was not between earlier stages: a state whose EWRAM holds
already-decoded text will show the text it copied. Start from a battery save, or from a state
made on this image.

## What this release deliberately does not contain

- Interior padding removal, `Great Soyman`, and the punctuated `Kakarot` -> `Bandit` set: that
  is release 3, on the same route.
- The 133 padded records that can be repaired in place: also release 3.
- Any change to a record the owner marked NO CHANGE, or to a record outside the eighteen.

## Continuity implications for owner review

The approved rows call Uub Videl's brother and the announcer calls them adopted siblings, while
the biographies this release inherits describe Uub as the son of Tien and Tulma. The owner
decided both wordings deliberately. No biography or parentage text is rewritten here; the
inconsistency is recorded so it is a decision, not a discovery.
