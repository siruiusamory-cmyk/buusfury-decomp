# Release 4: interior double spaces removed by a stream rebuild

Ticket RELEASE4-SPACES-001, tracker row A24. Base image: Release 4A Broly
(`a21c1e27f7b4f04cbe6952d70eb102b350adac04e6eaba106fa10e2b90a55021`, 10,170,720
bytes). Canonical reference:
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`.

Revision 2. Revision 1 (candidate `e1a223e4`) was BLOCKED by the coordinator
review: the pass rewrote 155 record-shaped words outside the event-resource pool,
142 of them shape coincidences in code and graphics. Section 2 records the rule
that fixes it; section 4 the independent check that now catches it.

## 1. Identity

| | |
| --- | --- |
| input | `v4a-broly.gba`, 10,170,720 bytes, `a21c1e27f7b4f04cbe6952d70eb102b350adac04e6eaba106fa10e2b90a55021` |
| output | 10,170,720 bytes, `2867b2cc43103e4b02d92f2942f557d249ec17ff4fc96b64dd75683fade67f08` |
| builder | `tools/research/build_release4_spacing.py` |
| engine edit | `tools/webfoot/textedit` `SpacingEdit` |
| verifier | `tools/research/verify_release4_spacing.py` (imports neither the builder nor the engine) |
| reproduced | twice, byte-identical |

Nothing was added to or removed from the file: every container is rewritten at the
offset it already occupied, so the container table is untouched.

## 2. What it changes, and the two rules that make it safe

The rename passes replaced longer words with shorter ones and paid the difference
with spaces inside the sentence, so a name of six units replacing one of five left
a doubled space.

**Rule 1: collapse the STREAM, not the record.** The containers are chain-shared:
one record's bytes are read by every longer record covering them, so an in-place
pass that collapses a run inside a record and pays the difference back as trailing
spaces re-creates the run inside a covering record. Measured on 2026-10-10, that
pass collapsed 118 runs and the corpus total barely moved (pitfall P-023). This
pass deletes the run's extra units from the DECODED STREAM, so every view loses it
at once, and rewrites each record's handle to the span its text now occupies. No
record keeps a length it paid for, so there is no payback space to re-create
anything.

**Rule 2: write only PROVEN carriers.** `dialogue_record_inventory` matches an
aligned word whose `+1` is zero and `+2` is `0x05` followed by a word that decodes
to a legal span. Inside the event-resource pool (`0x77C5A4..0x79B704`, the
placement contract's `pool_start`/`table` pair) that is a reference; outside it the
filter is near-random, measured at 281 passing words out of 907, 256 of which name
spans sharing no edge with any real record. A handle word is therefore rewritten
only inside that pool. The pool is stored on the `Layout` at open, so it travels
with the validated image. Two consequences:

* a word outside the pool keeps its bytes, and a `SpacingEdit` reports only the
  words it wrote;
* a targeted `RecordEdit` on a record no pool word names is REFUSED rather than
  written, because nothing would read it.

| selector | payload before | after | units deleted | handle words rewritten | retail runs kept |
| --- | --- | --- | --- | --- | --- |
| 0 | 65,348 | 65,270 | 39 | 461 | 2 |
| 1 | 65,474 | 65,398 | 38 | 296 | 2 |
| 2 | 65,464 | 65,222 | 121 | 454 | 3 |
| 3 | 65,334 | 65,140 | 97 | 378 | 8 |
| 4 | 65,322 | 65,140 | 91 | 479 | 4 |
| 5 | 65,394 | 65,238 | 78 | 439 | 1 |
| 7 | 23,790 | 23,738 | 26 | 29 | 0 |

Totals: 490 space units removed, 2,536 handle words rewritten over 2,818 live
records. Selector 6 is packed (kind 1) and carries no run, so it is not touched.
Revision 1 wrote a further 155 words outside the pool; those writes are gone.

A run survives where the canonical image's record at the same identity carries a
2+ space run at the same unit offset, and a longer base run is cut down to the
canonical run's length. Twenty stream positions qualify, listed in the manifest:
`0:5428`, `0:47756`, `1:11508`, `1:64970`, `2:61432`, `2:61540`, `2:62366`,
`3:8742`, `3:15126`, `3:15246`, `3:15382`, `3:16308`, `3:16386`, `3:26134`,
`3:58490`, `4:29318`, `4:47780`, `4:49770`, `4:51474`, `5:61074`.

## 3. Census before and after

Counted over every live record, in byte coordinates (a run counts once per record
whose span contains it):

| image | records with an interior 2+ space run | run occurrences |
| --- | --- | --- |
| base, Release 4A | 238 | 351 |
| this output | 22 | 26 |
| canonical | 24 | 30 |

The tracker's A24 row quoted 349 occurrences; this count is 351. The difference is
in the definition of a boundary run, and both figures are recorded rather than
reconciled silently.

## 4. Verification

`tools/research/verify_release4_spacing.py` re-derives everything from the base
image and the built image with the toolkit's own readers:

* **No out-of-pool word was written.** 281 record-shaped words lie outside the
  pool; all 281 are byte-identical in the output. This is the check revision 1
  failed, and it is what the pool rule exists for. Two of the 281 also stopped
  being "record-shaped" at all, because the shrunken payload moved the span they
  named past its end; their bytes are unchanged, which is checked too.
* **Every in-pool handle word still resolves.** 2,735 record words inside the pool
  in the base and 2,735 in the output, the same site set. Each site is read at its
  own word in the output, decoded, and the record read at the span that word
  names: same selector, a length no longer than before, every non-space character
  identical and in the same order. 454 space units are removed across those record
  views (a stream unit is counted once per record that read it).
* **Every interior run left is retail.** Each surviving run is mapped back to the
  base offset through the record it lives in, and the canonical image's record at
  that identity is asked whether it carries a 2+ run at the same unit offset. Every
  one answered yes.
* **Containment preserved.** 65 pairs of in-pool records where one base span held
  another still hold in the output.
* **Nothing else moved.** 187,388 bytes differ between the two images; every one
  lies inside a dialogue container's stored extent or inside the event-resource
  pool. The verifier's allowed set is the contract's pool range, deliberately NOT
  the shape-filtered site list it also uses to read records, so sharing that filter
  with the builder cannot hide a write.
* **Release 4A content.** 23 ranges from the 4A manifest (both stat selectors, the
  appearance records, the name slot, both definition copies and their entry
  pointers) are byte-identical.

Result: `VERIFY PASS` on `2867b2cc`.

## 5. Runtime smoke, paired

`tools/runtime/run_release4_spacing_smoke.ps1`, a bounded, visible, self-exiting
cold boot on a COPY of a battery save (the owner is asleep; nothing here needs a
human at the keyboard). It runs the same inputs twice: once on the Release 4A base
and once on this output.

| | base run | this output |
| --- | --- | --- |
| image | `a21c1e27...` | `2867b2cc...` |
| run directory | `build/release4-spacing/r4spaces-pair-base` | `build/release4-spacing/r4spaces-pair-out` |
| mGBA | 0.11 dev build, 0.11.0.0, visible, not minimised | same |
| save (copy) | `AACF7B33A78C...`, copied and hash-verified | same |
| bounded | 75 seconds, then the runner stopped the emulator itself | same |
| ROM after the run | unchanged | unchanged |
| screenshots | 15, 10 distinct | 15, 10 distinct |
| dialogue copier | fired twice, text `........Game Saved` | fired twice, text `........Game Saved` |

**All 15 sampled frames are byte-identical between the two runs.** The scene this
save boots into is the save banner, so the box under test is that banner, and both
images render it the same way at every sample. The copier read the same text at
both liveness hits. That is the paired comparison the reviewer asked for.

It is NOT a text-rendering proof. The sampled box draws no visible glyphs in
either image, which is why an earlier revision's "revealing" was wrong, and no
sampled frame shows a dialogue line. Whether a real line's spacing looks right on
screen stays the owner's visual acceptance, which is owner-reserved.

## 6. Limits

* **One kept run is also read by a record that is not the retail holder.**
  `0:47756` is retail spacing (`0:47718:144` carries it in the canonical image) and
  it is also inside `0:47124:790`'s span, so that longer record still shows two
  spaces there. Keeping it is right: the canonical image carries the same run at
  the same offset, so removing it would change the retail holder's spacing. Four
  further kept runs (`0:5428`, `3:8742`, `4:29318`, `4:49770`, `4:51474`) are each
  read by two records as well; in each case both readers carry the run in the
  canonical image.
* **The output is not bit-identical to retail spacing.** 22 records carry 26 runs
  against the canonical image's 24 records and 30 runs. The records themselves are
  not the same shapes after five releases of edits, so the remainder is expected;
  what is proven is that no run survives that retail does not carry at the same
  offset.
* **A record no pool word names is skipped by a rename and refused by an edit.**
  Eight of release 3.1's 34 renamed records are of that kind; they are listed in
  `plan.listed` and their text is still placed, matching the release's layout, but
  no word is written for them.
* **The runtime evidence is a paired smoke, not an acceptance.** See section 5.
* **The keep rule and the verifier's `retail_predicate`** compare by stream offset
  over any covering base record, not by record identity. Every release preserved
  record lengths, so the correspondence holds for this corpus; section 6 of
  `TEXT_ENGINE.md` states the same limit.
