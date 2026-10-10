# FRIEND-V3-WT-SPLIT-CONTAINER-001, phase A: can the dialogue containers be split?

This is the route answer the successor ticket was handed. It is **measured on**
`v3-mainline-text-dialogue-pass.gba`, 10,141,220 bytes, sha256
`d2a25f9a56c9980e27ad4a6f4c23d653e87d15b71b908ee27bced48b88885543`, with the canonical retail
image `Dragon Ball Z - Buu's Fury (U).gba`, 8,388,608 bytes, sha256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`, as the pad reference. The
planner is `tools/research/plan_friend_v3_container_split.py`; the run's JSON is under the
ignored `build/` tree.

Verdict at the end. The four questions the previous ticket left open are answered in order.

## 1. Every reader of the container table or its literal

Two readers, both static, both byte-identical in shape, and **disagreeing with the previous
ticket's note about a third address**.

| what | address | bytes | instruction |
| --- | --- | --- | --- |
| table base literal | file `0x123CC` | `645b7b08` (retail) / `e89c9a08` (release) | `0x087B5B64` / `0x089A9CE8` |
| loader A, table read | `0x08012242`-`0x08012248` | `6249` `8006` `000e` `0858` | `ldr r1,[pc,#0x188]` / `lsls r0,#0x1A` / `lsrs r0,#0x18` / `ldr r0,[r1,r0]` |
| loader B, table read | `0x080122C8`-`0x080122CE` | `4940` `8006` `000e` `0858` | `ldr r1,[pc,#0x100]` / the same three |
| **the two mask words, decoded** | `0x08012244` / `0x08012246` | `8006` / `000e` | Thumb `0x0680` = `lsls r0,r0,#26`; `0x0E00` = `lsrs r0,r0,#24` |

Loader A's entry is `0x08012230`, loader B's is `0x080122B4`. Both load the handle from the
record's `+0x04`, both take the selector as `(handle << 26) >> 24` - that is `selector * 4`,
the word index - and neither compares the result against a count. A third `lsls #0x1A / lsrs
#0x18` pair exists at `0x0804034A`; it is a 6-bit field of a `ldrb` scaled by two into a flag
table at object `+0x8E`, not a container table access, and no literal load feeds it.

The literal census settles the rest: the word `0x087B5B64` appears at **exactly one file
offset**, `0x123CC`, in the retail image, and `0x089A9CE8` at exactly one, `0x123CC`, in the
release. No word names any address inside the table's own extent, and no code writes a table
slot: every complete encoding of `lsls rS,#0x1A ; lsrs rS,#0x18 ; str/strh/strb` over the
1 MiB code region has zero hits.

**One correction to the previous ticket's record.** Node `9c29d1df` states the literal
resolves to `0x080728AC`. The bytes say `0x087B5B64`. The raw nibble sequence `087b5b64` was
the little-endian word read as text, not the word. The later node `c5f52cc4` agrees with the
bytes; the bytes win.

So the table has **one point of control and two consumers**, and a new container pointer
written into a table slot is seen by both consumers at once. There is nothing else to update.

## 2. What owns the bytes after the seven entries, and can the table grow

The release table is at file `0x9A9CE8`. Slots 0-6 are live container pointers. Slot 7 at
file `0x9A9D04` holds `0x03004A68`, an IWRAM address; slots 7-63 are not free space either,
they are **228 bytes of retail data copied verbatim with the table**:

```
release file 0x9A9D04..0x9A9DE8  ==  retail file 0x7B5B80..0x7B5C64   (228 bytes, identical)
```

That retail block has its own readers, independent of the table literal: the pool word at
file `0x03D92C` = `0x087B5B80` is loaded by three Thumb sites, and `0x03E018` =
`0x087B5B94` by three more. So the words in slots 7+ are live retail data that this image
happens to contain twice; nothing in the release names this copy.

Three consequences, all measured:

1. **The table cannot grow at the retail offset.** At file `0x7B5B64`, slot 7 would be
   `0x7B5B80`, the first word of that live structure. Growth has to sit in the release's
   copy, which is already there.
2. **The release's copy already reserves the whole 6-bit selector range.** Slots 0-63 span
   file `0x9A9CE8..0x9A9DE8` exactly, and `0x9A9DE8` is the first byte of the appended
   `"Tiencha"` text, named by live pointers at file `0x06BF00`, `0x06BF04`, `0x06BF78`,
   `0x06BFB8`, `0x06D150`, `0x06D154` and `0x06D1F4`. Writing slot 7 therefore overwrites
   only dead copied bytes: **no literal repoint and no table move is needed for one or two
   more containers.**
3. **A second word equal to the base does not exist**, but interior addresses do appear as
   data elsewhere: `0x087B5B80` at file `0x03D92C` and `0x087B5B94` at file `0x03E018`.
   Neither is read as a table base by any code, and neither is an address inside the
   release's table extent.

## 3. The container plan, with the handle words counted

The tooling's own framework makes the answer cheaper than a wholesale repack. A record's
start ceiling is 65,534 decoded bytes and its length field holds 4,094; measured on this
image, **no record starts past 65,534 in any of the seven containers**, so the ceiling is not
displacing anything today. What the ticket needs room for is only what does not fit in a
record's own span.

Two routes exist and they are not the same size:

| route | what moves | bytes needed | containers |
| --- | --- | --- | --- |
| full duplication of every record's text | 2,808 records, every handle site | 572,888 | 12 shards, 9+ selectors |
| **targeted repair** | 133 padded records in place; 96 padded records whose pad a sharing record also reads; 4 grown rows | **47,532 in one new container** | **1 new selector (slot 7)** |

The full-duplication route is **not available**: it needs 559.5 KiB of text, and selectors 0-5
hold 384 KiB of containers between them, with a decoder ceiling of 65,536 bytes each. That is
the number the previous ticket recorded as `plan_duplicated`'s price, and it is why this
document names the targeted route instead of re-running that one.

The targeted route, per container, measured (`in place` / `shared tail` records, trimmed units):

| selector | decoded | records | handle sites | over ceiling | in place | shared tail | trimmed units |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 65,348 | 526 | 639 | 0 | 3 | 25 | 48 |
| 1 | 65,474 | 448 | 475 | 0 | 9 | 4 | 32 |
| 2 | 65,464 | 466 | 487 | 0 | 20 | 19 | 99 |
| 3 | 65,334 | 422 | 429 | 0 | 30 | 19 | 95 |
| 4 | 65,322 | 486 | 498 | 0 | 38 | 14 | 88 |
| 5 | 65,394 | 460 | 476 | 0 | 33 | 15 | 74 |
| 6 | 436 | 6 | 6 | 0 | 0 | 0 | 0 |
| **total** | | **2,814** | **3,010** | **0** | **133** | **96** | **436** |

The division is the boundary decision, and it is checkable per record: a trim is invisible
when nothing else reads the units it drops. Where another record's span covers the dropped
units, the pad cannot be removed in place, because that record would lose characters it
currently reads. Those 96 are copied into the new container with their target text and their
handle words rewritten; **the bytes they leave behind do not move**, so every other record's
view of them is byte-identical.

The four owner rows that grow their record join the same container (`#` is the record's own
leading control unit and is preserved):

| row | record | reads today | approved | delta |
| --- | --- | --- | --- | --- |
| 1 | `3:7406:136` | 68 units | 86 units | +18 |
| 2 | `3:7542:42` | 21 | 34 | +13 |
| 4 | `3:7664:60` | 30 | 44 | +14 |
| 12 | `3:9112:62` | 31 | 36 | +5 |
| 18 | `3:9892:486` | 243 | 258 | +15 |

The other rows fit in their own span and are repaired where they are, by the same
handle-length reduction the trailing-pad pass already used: 3 (-4), 5 (-5), 6 (-51), 7 (-40),
8 (-28), 9 (-35), 13 (-20), 14 (-21), 16 (-1), 17 (-5), and 10, 11, 15 unchanged. The
previous ticket's overflow column differs from this one by **one unit on rows 1, 2, 4 and
13**: it counted the approved wording alone, and the record's own leading `#` costs one more
unit. Row 18's `+15` reproduces exactly. That is a measurement disagreement, not a route
change: the count here is the one the writer has to satisfy.

The new container's budget, measured: 47,132 bytes of moved padded text + 916 bytes for the
four grown rows = **48,048 bytes** against a 65,536-byte container, 17,488 bytes of slack. The
largest single moved record is 4,044 bytes against the 4,094-byte length field.

**Handle words to rewrite: 113 sites over 100 records**, every site of every moved record,
including the 96 shared-tail records and the four grown rows. `plan_group`'s refusal is kept:
no row is planned that the record identity does not carry, and no wording is truncated to fit.

## 4. Runtime proof
Delegated to the runtime lane under `docs/skills/mgba-runtime.md`. The instrument and its
result are recorded in `docs/research/FRIEND_V3_WT_SPLIT_CONTAINER_RUNTIME.md` when the run
closes; the claim and the exact breakpoints are not stated here ahead of the measurement.

What the run has to show, stated now so a later reading cannot widen it:

1. the selector value at `0x08012248` and at `0x080122CE`, with the record copier at
   `0x0801227A` as the liveness channel, so "no selector above 6" is a real negative only if
   the copier fired;
2. a throwaway image whose table slot 7 names an appended container, whose target record's
   handle words name selector 7, and where the copied record's bytes come from the appended
   region.

The first census run came back `target silent / liveness fires` and was rejected as an
instrument defect rather than accepted as a negative: the observer's derived word address was
`site - 8` (`0x08012240`, a code word) where the handle load is at `site - 4`, so it never
read a handle. That run is retained as the reason the read address is now stated with the
offset, and it is why the two mask words are decoded byte-by-byte in section 1 above: the
same run raised a layout disagreement that the decoded words settle, not a redesign.

## This route already has a precedent in the project's own history

A search of the cross-session record found it after the measurements above were taken, and
it belongs here because two earlier nodes reached the opposite conclusion.

**Measured now, read-only, on the private image `v3-renames-spill.gba` under the local
`roms` store (10,170,280 bytes, sha256 prefix `4be840dd`, 2026-10-04):** its table sits at file
`0x9B2EA8`,
seven of its slots are live containers, and **slot 7 holds a real kind-0 container**:
pointer `0x089A9994`, declared and decoded 38,156 bytes, at file `0x9A9994`. Its six dialogue
containers were simultaneously reduced to 65,266 / 65,424 / 65,272 / 65,148 / 65,136 /
65,242 bytes, each under the ceiling. No word of that image's game code differs from this one
in the reaches measured here.

That is the same data edit this document plans, at an earlier revision of the image: records
whose spans had to move were carried by selector 7 and their handles repointed, and the
origin containers were left smaller rather than rewritten. Node `3dceafd2` records the intent
("their handles are repointed there", 38,156 bytes) and whether that image was ever loaded in
an emulator is not recorded anywhere found - so it is corroboration of the mechanism's shape,
**not** the runtime proof this ticket owes.

**Two earlier nodes are contradicted by the bytes and by that image, and the correction is
recorded rather than quietly dropped:**

- `b63df963` and `ced8eea1` state that "the selector is not something a ROM edit can
  reassign" because the selector "lives in the handle word the game's script data carries".
  The handle word is a packed u32 sitting in this image at 3,010 file offsets, and
  rewriting one is a four-byte data edit; the dialogue dispatch reads those words and looks
  the selector up in the table. Measured here: 2,814 records carrying 3,010 handle sites,
  every one in-image.
- The same nodes read the 65,534-byte start ceiling as a property of the image rather than of
  one container, and concluded that containers 0 and 2 "cannot" take the repair "by any
  re-layout". The ceiling is per container; a second container removes it. The measurement
  that survives from those nodes is the one this document re-derives: full duplication does
  not fit (572,888 bytes of record text against 384 KiB in selectors 0-5), which is exactly
  why the targeted route above is the one to plan.

The prior image also settles nothing about the risk in item 3 below, because it was never
observed running.

## What the runtime run then settled, and what is still unproven

The runtime lane's report is `FRIEND_V3_WT_SPLIT_CONTAINER_RUNTIME.md`. It settles two of the
items below and leaves the rest:

1. ~~No runtime observation yet.~~ **Settled.** A selector-7 container was resolved by the
   engine (`r1` = the table base, engine index 7, five times) and rendered on screen
   (`ZZSPLITZZ...` in the dialogue box); on the unmodified image every resolved selector was
   3, across nine resolutions in a run whose dispatch channel fired 102,995 times.
2. **A selector used by a record word elsewhere.** 462 record-shaped words in the image carry
   a selector above 6 and sit outside every dialogue payload; 3 more (selector 13) sit inside
   one. Slot **7 carries none inside a payload and 9 elsewhere**. The runtime census shows the
   engine resolving only the selectors records actually name, so those words are never
   resolved in the scene measured - but that is one scene, and slot 7 remains the safest
   available choice on this evidence rather than a proven-safe one for every scene.
3. **The pad reference is retail, and the World Tournament records are already renamed.** The
   join for those rows is a per-row decision to be measured against the row's own `#` prefix,
   as recorded above.
4. **Whether the engine collapses the space units a repaired record leaves in its stream.**
   The in-place repairs keep a trailing run of spaces inside the record's old span but reduce
   the handle length so nothing reads it. The trailing-pad pass of the previous ticket rested
   on the same argument; that ticket's render observation is still owed.
5. **Save compatibility is unchanged by this route**, because no save layout, base-stat table
   or game code is touched - but that is inherited reasoning, not a measurement of this
   route.
6. **Proven by the engine at runtime**: the derivative reads the table from `0x08012248`. A
   later, longer run falsified the *general* form of the claim that `0x080122CE` never runs:
   with a level-up and a stat screen in the run, it fires eight times and reads the same
   containers site A does. Both sites load the same literal, so the one table word this
   release writes is seen by both. The sentence that called site B dead is corrected in
   `FRIEND_V3_WT_SPLIT_CONTAINER_RUNTIME.md`; the route is unchanged.

## Verdict

**SPLIT ROUTE PROVEN**, statically and at runtime: one table word in dead copied data, one
appended container, 113 handle words, no engine change, no literal repoint, 17,488 bytes of
slack, and the engine resolving and rendering a selector-7 record.

Final verdict for phase A: `PHASE A: PROVEN`.

