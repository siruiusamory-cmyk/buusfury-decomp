# Dialogue expansion tokens: the encoder, and the engine patch's relocation

Ticket: DIALOGUE-TOKEN-PRODUCTIZATION-001. This record carries what the ticket
measured, what it showed at runtime, and what it neither showed nor ran. It is
explicit about the gap: the token branch of the engine patch has not executed, and
the friend-image acceptance run has not been made.

Baseline: `origin/master` `b7f90a42393c42cea03cfbd36b8967621dbefca6`, branch
`ticket/dialogue-token-productization-001`. The canonical image is unchanged:
`940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`. Every
derivative this ticket built lives under ignored `build/`; no ROM, savestate,
capture or screenshot is committed.

## 1. What was recovered, and what this ticket adds

The approved design is already on master: `docs/research/DIALOGUE_EXPANSION_TOKEN_DESIGN.md`
(token window `0xE000..0xE0FF`, the `DTKN` dictionary blob, the three hook sites,
the relocated line fitter, the fail-closed rules). The prior proof is
`docs/research/DIALOGUE_TWO_GLYPH_POC.md`, which runtime-proved the composition
hook at `0x0800B066` with a cave at `0x082ED210`.

This ticket adds three things:

1. the **production encoder and dictionary codec**, `tools/webfoot/token_dictionary.py`,
   with every design rule as a refusal and a test per rule;
2. the **authored-window refusal** wired into the dialogue authoring path, which
   the design names as the prerequisite of the first build that emits a token;
3. the **first runtime evidence for the measure side** of the engine patch: the
   relocated copy of the line fitter with its two retargeted callers. The counters
   it produced are observed; that the copy is what ran is inferred, and section 4
   keeps those two claims apart.

## 2. The five named expansions, checked against the design

The ticket names `[Ya]`, `[ha]`, `[Kr]`, `[in]`, `[Ti]` as the token allocation.
Under the recovered design an expansion is **text**, and its id is **generated**:
the document lists expansions in key order and the build assigns `0xE000 + index`
(`DIALOGUE_EXPANSION_TOKEN_DESIGN.md` section 4, "Token ids are generated, not
authored"). So the five names are expansion texts, not ids, and nothing about
them may be inferred from the name: `[Ya]` expands to the two glyphs `Y` and `a`
and to nothing else.

Checked against the design's entry rules, each of the five is admissible:

| rule | source | `Ya` | `ha` | `Kr` | `in` | `Ti` |
| --- | --- | --- | --- | --- | --- | --- |
| 2 to 3 glyphs | design section 4 | 2 | 2 | 2 | 2 | 2 |
| below the `0xFF` class threshold | design section 2.3 | yes | yes | yes | yes | yes |
| not a stream control (`0x00 0x08 0x0A 0x0B 0x20 0x2D`) | design section 4 | yes | yes | yes | yes | yes |
| has a glyph record | design section 2.3 | yes | yes | yes | yes | yes |
| expansion advance at or under 108 px | design section 11 | yes | yes | yes | yes | yes |
| not a duplicate | design section 4 | yes | yes | yes | yes | yes |

Two glyphs is the design's own minimum, and a two-glyph entry replaces two units
with one, so every applied expansion saves exactly one unit. That is the whole
mechanism this feature exists for.

## 3. The measured coverage, and the one adjustment it needs

The 451 records are the spoken-dialogue rename set of the v3 line (a local
artifact, see section 7). Measured against the canonical image's own text stores,
the corpus of handle-defined records is 2,805 spans over seven containers with
194,717 reachable units, 89 distinct values and a highest value of `0x00EF`; the
menu and quest pool tops out at `0x00E9`. Nothing in either store is in the token
window, which is what makes the window reservable at all.

For each rename record the requirement is arithmetic: the record's new text is
`g` units longer than retail, and each applied expansion saves one unit, so the
record lands exactly on retail when exactly `g` non-overlapping occurrences are
tokenised. Measured over the rename set:

| expansion set | entries | growing records closed | short |
| --- | --- | --- | --- |
| the five, case-sensitive | 5 | 210 | 5 |
| the five plus their uppercase forms | 10 | 215 | 0 |

The five records the case-sensitive set cannot close are the all-caps lines, for
example `COME ON, KRILLIN! SHOW US WHAT YOU GOT! GO GO KRILLIN!` and `YAMCHA!`.
Adding the uppercase forms is not a design change: the window holds 256 ids and
the blob for ten entries is 92 bytes.

Result, produced by the shipped encoder rather than by an independent count:
**215 of 215 growing records land on exactly their retail unit count, the other
236 are already at or under it, and all 451 round-trip**. So the set that ships
today (236) and the set it withholds (215) together become 451 records whose
encoded lengths are unchanged, which is the property the friend-image defect
turned on.

The record enforces that result rather than trusting it: `encode_to_length`
refuses a target the text cannot reach and refuses a record the dictionary cannot
close, so a dictionary that does not cover a record fails at build time and never
degrades into a padded or truncated line.

## 4. The engine patch: the runtime evidence, and what it does not show

The design's measure side is a **relocated copy** of the line fitter
`FUN_0803DE6A`, because that function is a leaf (`push {r4,r5,r6,r7}` at
`0x0803DE6A`, `pop {r4,r5,r6,r7}` + `bx lr` at `0x0803DEA2`/`0x0803DEA4`, with no
saved LR), so a `BL` written into it in place would destroy the return address of
all six of its callers. The design retargets the two dialogue call sites
`0x0800AF3A` and `0x0800AFC8` to the copy.

That relocation was the design's riskiest unexecuted step, so it was built and
run as a **control that changes no behaviour**: the copy is the original 144-byte
body with the production prologue and epilogue (`push {r4,r5,r6,r7,lr}` /
`pop {r4,r5,r6,r7,pc}`), and the two callers are retargeted, with no token logic
anywhere. If the counters had moved, the fault would have been the relocation
rather than the feature.

| instrument | canonical control (DIALOGUE-TWO-GLYPH-POC record) | relocated-fitter control |
| --- | --- | --- |
| compositions | 941 | 941 |
| advances | 941 | 941 |
| consumes | 941 | 941 |
| queue writes | 6 | 6 |
| copier (liveness) | 5 | 5 |
| OAM snapshots | 30 | 30 |
| VRAM window changes | 55 | 55 |

Identical on every channel. **What that proves, and how it was observed, stated
separately.** Observed: the route ran to 3,000 frames with the two dialogue call
sites patched to branch into the cave, and every instrument counts exactly what
the canonical control counts. Inferred, not directly observed: that the cave's
copy is what executed, because the observer arms no breakpoint inside the cave and
its ROMCHECK reads only the two hook words. A cave that never ran would produce
the same counters, which is why the conclusion is "the relocation changed no
observed behaviour" and not "the copy was watched running". The counter argument
is that the two retargeted `BL`s are the only fitter calls reachable from
`FUN_0800AE74`, and 941 compositions happened, so the calls did arrive somewhere;
the cave is where they were pointed.

Built by `tools/research/build_dialogue_token_engine.py --variant fitter-control`:

```text
derivative sha256  8fa424d93a256239a82626eab99ec30074f421a82334676d8a14a9fb6fbdeb7d
cave               0x082ED210, 144 bytes
retargeted         0x0800AF3A, 0x0800AFC8  (both decode back to the cave)
image              8388608 bytes, game code BG3E, digest unchanged after the run
run                build/fitter-control-run-01, marker done:StripProbe
```

The build refuses, rather than discovers: a source digest other than the declared
one, a cave region that is not a uniform filler run, a caller whose bytes are not
the expected `BL`, any `BL` displacement outside the ARMv4T 23-bit range or needing
`J1`/`J2` other than 1, a copy that differs from the original anywhere but its
prologue and epilogue, a copy whose last branch leaves the copy, and any stray byte
outside the two patched regions.

## 5. The authored-window refusal

The design makes this rule the prerequisite of any build that emits a token: the
window is safe for authored text only while a validator refuses it, so without
the rule a paste could produce a unit the decoder would silently expand.

`tools/webfoot/token_dictionary.py` now exposes the predicate, and it is applied
at both seats an authored replacement passes through:

* `tools/webfoot/dialogue.py::validate_dialogue_replacement`, which the editor's
  live validation, the apply path and the build's `_check_dialogues` all funnel
  through, reports it as `reserved_token_window`;
* `tools/webfoot/compressed_dialogue.py::_prepare_replacement`, which encodes
  directly and is therefore reachable without the validator.

## 6. Reproduction

```text
python -m pytest tests/unit/test_token_dictionary.py -q

python -m tools.research.build_dialogue_token_engine --variant fitter-control \
    --rom "<canonical>.gba" \
    --expect-sha256 940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E \
    --out build/runtime-roms/dialogue-fitter-control.gba

powershell -File tools/runtime/run_token_engine_session.ps1 -Phase start `
    -RomPath build/runtime-roms/dialogue-fitter-control.gba `
    -ExpectedRomSha256 8fa424d93a256239a82626eab99ec30074f421a82334676d8a14a9fb6fbdeb7d `
    -RunDir build/fitter-control-run-01 -MGBPath "<0.11 dev build>" `
    -StatePath "<retail savestate>"
powershell -File tools/runtime/run_token_engine_session.ps1 -Phase finish `
    -RomPath build/runtime-roms/dialogue-fitter-control.gba `
    -ExpectedRomSha256 8fa424d93a256239a82626eab99ec30074f421a82334676d8a14a9fb6fbdeb7d `
    -RunDir build/fitter-control-run-01 -StatePath "<retail savestate>"
```

The launcher and the savestate are not inside a ticket worktree (`build/` and
`roms/` are not shared with one), so the run script takes `-MGBPath` and
`-StatePath`. The 0.11 dev build is required: the observer asserts
`emu.setBreakpoint`.

## 7. What is NOT proven, and the limits of the measurements

* **The token branch has not executed.** No build has yet composed an expansion:
  the dictionary lookup, the shared per-glyph advance helper and the
  `token_advance` call at the copy's width site are designed and statically
  consistent, but unrun. The composition hook and the relocated fitter each have
  separate runtime evidence; the two together, with a token in the stream, do not.
* **No token has been planted in a displayed record**, so no in-game visible
  text has been shown to change. The two-glyph POC planted its trigger by gating
  on a unit that occurs naturally (`K`, twice in the 3,000-frame route); a token
  unit does not occur naturally anywhere in retail text, so this needs a
  length-neutral container edit, which this ticket did not build.
* **The friend-image acceptance run has not been made.** The Kibito cutscene A/B
  on a token-compressed 451-rename image is the acceptance the ticket asked for,
  and it is outstanding. Nothing here says the cutscene will survive.
* **The 451-record measurement rests on an untracked artifact.** The rename set is
  `rename_map.json` under the working checkout's ignored `build/crash-repro/`
  directory, beside the bisection harness. It is not committed, deliberately: it
  carries dialogue text derived from a proprietary image. The arithmetic in
  section 3 is reproducible where that file exists and from nothing in this
  repository. Recovering it needs the v3 images and `extract_rename_map.py`, both
  local.
* **`451 dialogue records` is not a repository measurement.** The tracked corpus is
  2,805 record spans over the seven containers (447 in selector 1, the only
  container with a registered editable target). Every literal `451` in tracked
  files is `MapEntry 451` or a map-root count. The 451 here is the v3 rename
  set's own size, and it is stated as such wherever it appears.
* **The unrelated defects are untouched**, as the ticket required: the
  `F0674DD8` crash and the unsafe tail allocation are not investigated here and
  no claim is made that tokens affect either.
* **Two design rules are enforced only when a caller opts in**, and this ticket
  did not build the caller that would: the "no glyph record" image check is the
  `has_glyph` seam on `build_blob` and `decode_blob`, and the 108 px expansion
  bound is `check_widths`, which nothing calls yet. The C0 block is refused
  unconditionally, because the design measures it as glyph-less, but a build that
  emits a token must still pass the font and call `check_widths` or those two
  rules are inert. The `DTKN` table base and count literals the engine reads have
  no producer at all yet, so the design's section 14 check that they agree with
  the blob header is likewise still to be written.
* **The cave address is still a constant.** The design requires taking the region
  from the project's free-space machinery and running a cave-only control against
  it; the builder checks that its 512 reserved bytes are one uniform filler run
  and nothing more. It does not re-derive the 3,019-byte run the design measures.
* Three measurements of this ticket are worth carrying even though they touch
  other records: the `BL` at `0x0800B06A` targets `0x0803DE50`, the composition
  wrapper, while the fitter `0x0803DE6A` is a separate six-caller function; the
  `0x082ED210` run is 3,019 bytes, so it is below a 4,096-byte threshold rather
  than above one; and the only other uniform run that large is the `0xFF` ROM
  tail. None of the three changes the design's plan.

## 8. Next steps, in order

1. Extend `build_dialogue_token_engine.py` with the token variant: the `DTKN` blob
   in the cave region, `token_lookup`, a shared `glyph_advance`, the
   `token_advance` call at the copy's width site, and the composition cave gated
   on the unit window. Re-decode the cave from the finished image against a
   written instruction table, the check that caught the first cave's encoding
   error.
2. Plant token units length-neutrally in the record the NPC-front route displays,
   and run the same route to see the expansion in game.
3. Only then build the 451-rename v3 image with the encoder of section 3 and run
   the Kibito A/B.
