# FRIEND-V3-WT-SPLIT-CONTAINER-001, release 2.1: the registration scene and Bulma's biography

Three owner-authored changes on top of release 2, delivered before the release-3 work because
the owner wants them in the build that gets streamed.

## What ships

| field | value |
| --- | --- |
| file | `v3-wt-split-2-1-a.gba` |
| bytes | 10,146,000 |
| SHA-256 | `018757c4e0dda9f463364675f32b307dff9e5ad89c7a0b932939aec320032389` |
| base | release 2 `v3-wt-split-a.gba`, sha256 `0b5ac8f470277f3c674710e07ce9d744433acd6a331736a628e00d6f72a6ef22`, 10,143,256 bytes |
| builders | `apply_friend_v3_text_slot.py` (the biography), then `apply_friend_v3_registration_rows.py` (all three sites in one final image) |
| verifiers | `verify_friend_v3_text_slot.py`, `verify_friend_v3_registration_rows.py` |

The artifact lives under the ignored `build/` tree and is not in git. The single-slot
intermediate `v3-wt-split-bio1083-a.gba` (`7ecad484…`) is kept as the base of this build and is
superseded as a release by the file above.

## The three changes

| what | record or slot | read before | reads now | units |
| --- | --- | --- | --- | --- |
| Oolong, registration scene | `2:60432:98` | `Good luck, you guys! This is just like old times!` | `It's definitely Tulma. Just look at her in that dress! Yowza.` | 49 -> 61 |
| Master Roshi, registration scene | `2:60922:140` | `I have a feeling that this is not going to be your typical tournament.` | `Oolong and I are debating, I say Bulma is the hotter twin!` | 70 -> 58 |
| Bulma, scanner biography | text slot 1083 | `Bulma is Yamcha's wife and Krillin and Videl's mother. She is the daughter of the Ox-King.` | `Bulma is Yamcha's wife and Krillin and Videl's mother. A genius inventor, she is the heiress of Capsule Corporation.` | 90 -> 116 |

No record keeps a control prefix it did not already carry: the two dialogue records begin with
a plain letter both before and after, the biography is a text-table string with no prefix, and
the speaker and portrait of each record are the record's own and are untouched.

## How each site is written, and why

**The two dialogue rows are copied, not written in place.** Both sit inside covering records:
`2:60432:98` is covered by `2:57304:4046` and `2:57336:4046`, and `2:60922:140` by those two
plus `2:60720:2578`. Writing either text into its own span would leave bytes those covering
records read holding something else, which is the corruption this project measured on
`1:38856:252`. Each row's text is therefore copied into the selector-7 container and its handle
word is repointed; every covering record's bytes are untouched and it still reads exactly what
it read before.

**The biography string is copied to the end of the image** and its single table pointer at file
`0x6BFD4` is repointed from `0x089AC618` to `0x089ACFE6`. It is copied rather than left where
release 2.1 put it because that offset lies inside the payload window of the selector-7
container, whose declared size cannot be widened without placing the new records outside it.

**Nothing is truncated and nothing moves.** The tool refuses to rebuild the container in place,
because the container release 2 appended is referenced by fifteen World Tournament handle
words.

### The step that is worth recording, because the verifier caught it

A first version of `apply_friend_v3_registration_rows.py` rebuilt selector 7's container where
it was, which deleted the container release 2 had appended at file `0x9ABE24` and the string
release 2.1 had appended after it: fifteen World Tournament records were orphaned. The
assembled layout was also wrong in a second way, and the second version failed its own
verifier for that reason: the fifteen World Tournament handles name **selector 7 at their own
start offsets**, so a new container that declared only the two new records would place those
offsets past its declared size, and a decoder honouring the declared size would stop before the
World Tournament text.

The tool now carries the previous container's whole payload forward as the prefix of the new
one and appends the new records after it, so the old offsets still land inside the declared
size. Measured: 2,028 carried bytes, then Oolong at 2,028 and Roshi at 2,144, container declared
2,266. Both failures are recorded here rather than quietly fixed, and the builder now reads its
own output back and refuses if the carried prefix does not hold the release-2 wording.

## Verified

| check | result |
| --- | --- |
| both dialogue rows resolve through the table and read the owner's wording exactly | PASS |
| text slot 1083 reads the owner's wording from its new home, recomputed from the tracked approval constant | PASS |
| the selector-7 container declares 2,266 bytes and decodes to 2,266 | PASS |
| all fifteen World Tournament rows still read their release-2 wording, resolved from a handle site the baseline image itself reports, at the start offset that handle names | PASS, 15 of 15 |
| the 18 "record words" the container yields to the inventory are not 18 records: three records were placed, the rest are text units that happen to decode as handles. Nothing is claimed from that count | noted |
| bytes differing from the base outside the declared sites | 0 |
| differing bytes in the base | 12, exactly three sites of four bytes |
| reproduced from the release-2 base in one chain (`build_friend_v3_release21.py`), which is the check an independent rebuild needs | byte-identical, `018757c4…` |
| reproduced twice from the intermediate | byte-identical, both `018757c4…` |
| BOOST absence, re-measured on this image: the 25 bytes the BOOST builder declares all hold the foundation's byte | PASS, 25 of 25, and the BOOST image differs at all 25 so the check is not vacuous |
| relocation guard, its refusal path and its word alignment | `tests/unit/test_friend_v3_text_slot.py`, 6 passed |
| the container prefix arithmetic: the carried payload, the new record's offset, the declared size, the unaligned-input pad, and the refusal on a site that does not carry the expected handle | `tests/unit/test_friend_v3_registration_rows.py`, 5 passed |

## Runtime

**The biography is runtime-verified.** On the single-slot intermediate, loaded cold with the
route battery save and driven by the owner, the running game fetched the repointed pointer and
drew the new wording: at frame 2012 the draw call carries pointer `0x089AC618` with the text
`Bulma is Yamcha's wife and Krillin and Videl's mother. A genius inventor, she is the heiress of
Capsule Corporation.`, after the screen had drawn the name `Bulma` and the HP/STR/POW/END
labels. The observer's liveness channel fired 54,428 times in that run, so the silence of the
panel's own table-load sites is a fact about the route the text took, not an unproven
instrument. The screenshot is `scanner-screen-bulma-frame2160.png` in the ignored run tree.

**The two dialogue rows are owner-attested at runtime.** The owner played
`v3-wt-split-2-1-a.gba` (sha256 `018757c4…`) in the registration scene and confirmed both lines:
Master Roshi at `2:60922` and Oolong at `2:60432`. That is human attestation against this
image's own digest, not a capture, and it carries the weight a player's report carries and no
more: no screenshot or observer log exists for those two rows. A driven run with the observer
would upgrade it to a machine observation, and it is prepared the way the World Tournament
scene was.

## Continuity note, for the owner only

The approved Roshi line calls Bulma and Tulma twins. No biography is changed to reconcile that,
and the tracker carries it as an owner-review item.

## Save compatibility

Unchanged: no save layout, game code or base-stat table is touched. Battery saves carry over; a
savestate made on an older image can show text it already copied.
