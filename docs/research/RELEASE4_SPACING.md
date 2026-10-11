# Release 4: interior double spaces removed by a stream rebuild

Ticket RELEASE4-SPACES-001, tracker row A24. Base image: Release 4A Broly
(`a21c1e27f7b4f04cbe6952d70eb102b350adac04e6eaba106fa10e2b90a55021`, 10,170,720
bytes). Canonical reference:
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`.

## 1. Identity

| | |
| --- | --- |
| input | `v4a-broly.gba`, 10,170,720 bytes, `a21c1e27f7b4f04cbe6952d70eb102b350adac04e6eaba106fa10e2b90a55021` |
| output | 10,170,720 bytes, `6398e202c4f8d947313fccf7e99948ae4087fdf28afc42d5ccf10285d18911ff` |
| builder | `tools/research/build_release4_spacing.py` |
| engine edit | `tools/webfoot/textedit` `SpacingEdit` |
| verifier | `tools/research/verify_release4_spacing.py` (imports neither the builder nor the engine) |
| reproduced | twice, byte-identical |

Nothing was added to or removed from the file: every container is rewritten at the
offset it already occupied, so the container table is untouched.

## 2. What it changes, and why the earlier pass failed

The rename passes replaced longer words with shorter ones and paid the difference
with spaces inside the sentence, so a name of six units replacing one of five left
a doubled space. The containers are chain-shared: one record's bytes are read by
every longer record covering them. An in-place pass that collapsed a run inside a
record and paid the difference back as trailing spaces therefore re-created the run
inside a covering record; measured on 2026-10-10, it collapsed 118 runs and the
corpus total barely moved (pitfall P-023).

This pass collapses the run in the DECODED STREAM instead. Every view loses it at
once, and each record's handle is rewritten to its new span, so no record keeps a
length it paid for and there is no payback space to re-create anything.

| selector | payload before | after | units deleted | handle words rewritten | retail runs kept |
| --- | --- | --- | --- | --- | --- |
| 0 | 65,348 | 65,270 | 39 | 514 | 2 |
| 1 | 65,474 | 65,398 | 38 | 302 | 2 |
| 2 | 65,464 | 65,222 | 121 | 477 | 3 |
| 3 | 65,334 | 65,140 | 97 | 388 | 8 |
| 4 | 65,322 | 65,140 | 91 | 496 | 4 |
| 5 | 65,394 | 65,238 | 78 | 470 | 1 |
| 7 | 23,790 | 23,738 | 26 | 44 | 0 |

Totals: 490 space units removed, 2,691 handle words rewritten across 2,818 live
records. Selector 6 is packed (kind 1) and carries no run, so it is not touched.

A run survives where the canonical image's record at the same identity carries a
2+ space run at the same unit offset. Twenty runs qualify, listed by the builder
and in the manifest: `0:5428`, `0:47756`, `1:11508`, `1:64970`, `2:61432`,
`2:61540`, `2:62366`, `3:8742`, `3:15126`, `3:15246`, `3:15382`, `3:16308`,
`3:16386`, `3:26134`, `3:58490`, `4:29318`, `4:47780`, `4:49770`, `4:51474`,
`5:61074`.

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

* **Every handle word still resolves.** 3,016 record words in the base, 3,016 in
  the output, the same site set. Each site is read at its own word in the output,
  decoded, and the record read at the span that word names: same selector, a
  length no longer than before, every non-space character identical and in the same
  order. 755 space units are removed across those record views (a stream unit is
  counted once per record that read it).
* **Every interior run left is retail.** Each surviving run is mapped back to the
  base offset through the record it lives in, and the canonical image's record at
  that identity is asked whether it carries a 2+ run at the same unit offset. Every
  one answered yes.
* **Containment preserved.** 4,869 pairs of records where one base span held
  another still hold in the output.
* **Nothing else moved.** 187,756 bytes differ between the two images; every one
  lies inside a dialogue container's stored extent or inside a four-byte handle
  word. That is what keeps the image's other data intact.
* **Release 4A content.** 23 ranges from the 4A manifest (both stat selectors, the
  appearance records, the name slot, both definition copies and their entry
  pointers) are byte-identical.

Result: `VERIFY PASS`.

## 5. Runtime smoke

`tools/runtime/run_release4_spacing_smoke.ps1`, a bounded, visible, self-exiting
cold boot on a COPY of a battery save (the owner is asleep; nothing here needs a
human at the keyboard).

| | |
| --- | --- |
| image under test | the output above, `6398e202c4f8d947313fccf7e99948ae4087fdf28afc42d5ccf10285d18911ff` |
| mGBA | 0.11 dev build, version 0.11.0.0, visible and not minimised |
| save (copy) | `AACF7B33A78C26E5481621F6D8B06FE56507207B09A8C244FD3005F9C7C75291`, copied into the run directory and hash-verified |
| run directory | `build/release-spacing/r4spaces-smoke-01` |
| bounded | 75 seconds, then the runner stopped the emulator itself |
| ROM after the run | unchanged, `6398e202...` |

What the run produced: 15 screenshots, 10 distinct hashes, and the dialogue record
copier breakpoint (`0x0801227A`, the observer's liveness channel) fired. Frame 900
hashes `458fdf73ca13760c1e643394a2709ec7f812a9f25ee33d3f8115f332ddbaa528`, which is
the same title screen this project measured on a cold boot in an earlier ticket, so
the run really booted this image. The later frames were read as images: the player
is on a map with the HUD drawn, and a dialogue box opens over it. That is the
boot-to-gameplay smoke this ticket asks for.

It is NOT a text-rendering proof. The sampled frames catch the dialogue box while
it is revealing, no line is fully drawn in them, and whether the wording looks
right on screen is the owner's visual acceptance, which is owner-reserved.

## 6. Limits

* **One kept run is also read by a record that is not the retail holder.**
  `0:47756` is retail spacing (`0:47718:144` carries it in the canonical image) and
  it is also inside `0:47124:790`'s span, so that longer record still shows two
  spaces there. Keeping it is correct: the canonical image carries the same run at
  the same offset. Every other kept run is read only by its retail holder.
* **The output is not bit-identical to retail spacing.** 22 records carry 26 runs
  against the canonical image's 24 records and 30 runs. The records themselves are
  not the same shapes after five releases of edits, so the remainder is expected;
  what is proven is that no run survives that retail does not carry at the same
  offset.
* **The runtime evidence is a smoke, not an acceptance.** See section 5.
* **The verifier trusts the offset correspondence** between the base and the
  canonical image (same identity, same offsets) exactly as every release pass does.
  Where a record's span runs past the canonical payload the verifier skips that
  candidate rather than aligning by guess; none occurred here.
