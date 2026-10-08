# Dialogue expansion tokens: the encoder, the engine patch, and the rename splice

Ticket: DIALOGUE-TOKEN-PRODUCTIZATION-001. This record carries what the ticket
measured, what it showed at runtime, and what it has not done. Baseline
`origin/master` `b7f90a42393c42cea03cfbd36b8967621dbefca6`, branch
`ticket/dialogue-token-productization-001`.

The canonical image is unchanged:
`940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`. Every
derivative, capture and screenshot lives under ignored `build/`; no ROM, savestate,
capture or screenshot is committed. The private v3 base images and the rename map
are NOT in this repository and are passed to the tools as arguments.

## 1. What was recovered, and what this ticket adds

The approved design is on master: `docs/research/DIALOGUE_EXPANSION_TOKEN_DESIGN.md`
(token window `0xE000..0xE0FF`, the `DTKN` dictionary blob, the three hook sites,
the relocated line fitter, the fail-closed rules). The prior proof is
`docs/research/DIALOGUE_TWO_GLYPH_POC.md`, which runtime-proved the composition hook
at `0x0800B066` with a cave at `0x082ED210`.

This ticket adds five things:

1. the production encoder and dictionary codec, `tools/webfoot/token_dictionary.py`,
   with every design rule a refusal and a test per rule;
2. the authored-window refusal wired into the dialogue authoring path, which the
   design names as the prerequisite of the first build that emits a token;
3. the **token branch of the engine patch**, built and executed at runtime:
   `token_lookup`, the shared `glyph_advance`, `token_advance` in the relocated
   fitter, the composition cave, and the dictionary blob;
4. a rename splice that is **prefix-preserving**, `tools/research/splice_dialogue_tokens.py`,
   so a rename cannot move another word;
5. the verifier that proves it, `tools/research/verify_token_splice.py`, over every
   record the image's own inventory can name.

## 2. The five named expansions, checked against the design

The ticket names `[Ya]`, `[ha]`, `[Kr]`, `[in]`, `[Ti]` as the token allocation.
Under the recovered design an expansion is **text** and its id is **generated**: the
document lists expansions in key order and the build assigns `0xE000 + index`
(design section 4). So the five names are expansion texts, not ids, and nothing may
be inferred from a name: `[Ya]` expands to the glyphs `Y` and `a` and to nothing else.

Checked against the design's entry rules, each of the five is admissible: two
glyphs, below the `0xFF` class threshold, not a stream control, has a glyph record,
expansion advance under 108 px, not a duplicate.

Two glyphs is the design's own minimum, and a two-glyph entry replaces two units
with one, so every applied expansion saves exactly one unit. That is the whole
mechanism this feature exists for.

## 3. The engine patch, and what running it proved

`tools/research/build_dialogue_token_engine.py` builds the patch:

| piece | address | what it is |
| --- | --- | --- |
| fitter copy | `0x082ED210` | 144 bytes; prologue and epilogue edited, width site replaced by `bl token_advance` |
| `token_lookup` | cave + `0x90` | `r4 = unit -> r5 = entry or 0`; the table base and count are literals |
| `glyph_advance` | after it | `r0 = strip, r1 = glyph -> r2 = width + 1`, the same two-level read the engine uses |
| `token_advance` | after it | prices a unit and jumps back into the copy; never returns through LR |
| `cave_compose` | after it | the ordinary path resumes the game's own `bl 0x0803DE50`; the expansion path composes each glyph |
| dictionary blob | cave + `0x16C` | `DTKN`, ten entries, 92 bytes; the descriptor points PAST its 12-byte header |

Three defects were found by building and running it, and each is now a refusal:

* **The descriptor pointed at the blob's magic.** The engine indexes
  `base + (unit - 0xE000) * 8` and the design's section 4 puts the entries at
  `+0x0C`, so the header is builder metadata the engine never reads. Handed the
  header, the lookup returned `DTKN` as glyph codes: the probe logged glyphs 21572
  and 20043 (`"DT"`, `"KN"`) being composed, the fitter priced a name as six garbage
  glyphs, and the line broke after six units. The build now reads the table back out
  of the finished cave exactly as the engine reads it and refuses a mismatch.
* **A jump back into the copy used an even address.** `bx` with bit 0 clear switches
  the CPU to ARM state; the four bytes there are not ARM code, so the frame never
  completed and both token builds wedged at frame 187 while the relocation-only
  control ran to 3000. The builder now refuses any `bx` target without the Thumb bit.
* **The composition cave's source-consume store is `str r1,[r2,#0x14]`,** and its
  address is exported as a label rather than derived by hand, so a probe can watch
  the consumption the expansion performs itself.

### 3.1 The three cases, run on the canonical image

| case | derivative | result |
| --- | --- | --- |
| relocation-only control | `8fa424d9` | compose 941, advance 941, consume 941, qwrite 6, copier 5 |
| token build, window matching nothing (`0xE000`, ten entries) | `186871ac` | compose 941, advance 941, consume 941, qwrite 6, copier 5 |
| token build, window on a unit that occurs (`0x65`, entry `"A!"`) | `efc15cc5` | lookup 2767, tokenpath 250, glyphadv 706, **cexpand 309, consume 103**, compose 940, copier 4 |

The two controls are identical to each other and to the published canonical control,
so the patch is a no-op on ordinary text. In the third case the composer expands the
token into the entry's two glyphs with the design's own advances, measured from the
live text object: the walker moves `0x082ED388 -> 0x38A -> 0x38C` while x moves
`64 -> 72 -> 78`, i.e. `+8` for `Y` and `+6` for `a`, and the cave consumes exactly
one source unit per expansion.

VISIBLE, same savestate and same driver as the control: the control reads
`Awwww, yeah! I'm the bomb! No one can beat me` and this build reads
`Awwww, yA!ah! I'm thA! bomb! No onA! can bA!at mA!!`. Every `e` is composed as the
entry's two glyphs at the right x, and the text reflows to three lines because each
token is wider than the unit it replaced.

### 3.2 The shipping window, planted in a displayed record

The window `0xE000` cannot be exercised by retail text, because no retail unit is in
it: a token has to be planted. `tools/research/splice_dialogue_tokens.py` replaced
ONE unit of the record that carries the displayed line (selector 0, byte span
60046 + 168, 84 units) with `U+E000`, leaving the record's decoded length untouched,
and the engine patch was applied on top. Derivative `89ca497b`.

Runtime, unit `57344 = 0xE000`, priced by BOTH sides (`caller fitter` at the
`token_advance` return address and `caller composer` at the `cave_compose` one):
cexpand 309, consume 103, tokenpath 250, copier 5 liveness. The line reads
`Awwww, Yaeah! I'm the bomb! No one can beat me` - the `y` of "yeah" is gone and the
token's `Ya` is composed in its place, with the record's 84 units and 168 bytes
unchanged.

## 4. The rename splice, and the no-bleed property

The v3 rename line measured the constraint: a rename is safe when the record's
decoded byte length lands exactly on retail. The first version of this ticket's
splice did that by tokenising anywhere in the record and padding the end. It kept
each record's total length and still corrupted neighbours, because retail records
**overlap**: about 40 percent of decoded units are read by more than one record, so
rewriting one record's bytes rewrites what its neighbours display, and a substituted
name of a different length slides every character after it inside the span.

Measured on that first build: 12 renamed records and 87 untouched records displayed
text the map never asked for. One example, a record whose retail text is
`!Listen to your mother, Trunks! I need the Dragon Balls.` read
`isten to your mother, Uub! I need the Dragon Balls.@Bulm` - a one-unit shift plus
the neighbouring record's text.

**The fix is to pay for each substitution INSIDE the name it changes.** Growth is
paid for by tokenising inside the new name; a shrink is paid for with spaces
immediately after it. The replacement then occupies exactly as many units as the
text it replaced, so no prefix of any record changes length, no offset in the
container moves, and no neighbouring record can be shifted. Of the 84 distinct
substitutions the map performs, all are payable this way: 31 growths by tokenising
inside the name with zero unpayable, 41 shrinks with spaces, 12 needing no change.

### 4.1 The verifier, and what it found

`tools/research/verify_token_splice.py` reads the finished image the way the engine
does - the image's own relocated table, every record's own span - and holds every
record to a **positional** oracle: the splicer exports each substitution as
`(start, length, replacement)` in the decoded container, and every record must equal
its retail text with those regions applied, character for character outside them.
Two earlier oracles that matched old and new strings instead were tried and both
produced false failures, because a table of names matches ambiguously; that is
recorded in the tool's own docstring so it is not tried a third time.

Over the 7 containers, 2,814 records read back out of the image:

| result | count |
| --- | --- |
| text entirely untouched | 2,303 |
| only substituted names differ | 511 |
| **anything else differs** | **0** |
| unresolvable token | 0 |
| stored length preserved | every record |

So a rename changes the names and nothing else, anywhere in the image, and no
record's bytes moved.

## 5. The v3 candidate, and the Kibito A/B

Built from the verified friend baseline `v3-safe.gba`
(`b0de6ddffe53961bcade893107b7f9a8004d684b919552480ca688207e8f56d5`, the friend's
work plus levels, menu text, credits and the slot-292 fix, WITHOUT spoken-dialogue
renames) by `tools/research/splice_dialogue_tokens.py` with the ten-entry shipping
dictionary:

* 451 records encoded, **450 applied**, 1 refused and reported
  (`3:2184:2112`, whose bytes another record's replacement disagrees with);
* 435 tokenised, 15 exact, 0 padded at the record end;
* every rebuilt container is byte-for-byte the same decoded size as retail
  (65348, 65474, 65464, 65334, 65322, 65394);
* derivative `cffdb81e471567fab623d3ec3a0b920cc0b5ef3f0a11bc5f3c70e5bab1395446`,
  engine patch applied on top:
  `d401d71c0ed3fbf93476aaa1825ea8c680e3caac7f7d7fbc05cbfe16344ab0f5`.

The A/B, on the operator's Kibito savestate, driven by the A-tap driver, with the
frame heartbeat as the detector (the fault is a freeze with no emulator popup and a
normal idle program counter, so the detector has to be the frame count from
outside). A positive control is part of the A/B: if the known crash build does not
hang here, the instrument is not measuring the fault.

| image | frame reached | verdict |
| --- | --- | --- |
| `v3-fixed-credits.gba` `ddfdf780` (known crash) | 1946 of 3000 | **HANG**, as expected |
| `v3-renames-clean.gba` `328f5dcf` (shipped 236 renames) | 3000 of 3000 | SURVIVED, as expected |
| **candidate `d401d71c` (450 renames + token engine)** | 3000 of 3000 | **SURVIVED** |

Dialogue displays through the cutscene, and the tokens are expanded on this route:
cexpand 6, consume 2, tokenpath 4, copier 9 liveness. The cutscene frames match the
control where the text is unchanged, and the composed lines are coherent.

## 6. Reproduction

```text
python -m pytest tests/unit/test_token_dictionary.py tests/unit/test_dialogue_token_splice.py \
    tests/unit/test_dialogue_token_engine_build.py -q

python -m tools.research.build_dialogue_token_engine --variant fitter-control \
    --rom "<canonical>.gba" \
    --expect-sha256 940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E \
    --out build/runtime-roms/dialogue-fitter-control.gba

python -m tools.research.splice_dialogue_tokens --base "<friend baseline>.gba" \
    --base-sha256 <exact digest> --map <private rename map>.json \
    --tokens Ya ha Kr in Ti YA HA KR IN TI --out build/runtime-roms/v3.gba \
    --report build/token-analysis/v3-token-report.json

python -m tools.research.verify_token_splice --base "<friend baseline>.gba" \
    --spliced build/runtime-roms/v3.gba --map <private rename map>.json \
    --tokens Ya ha Kr in Ti YA HA KR IN TI \
    --splice-report build/token-analysis/v3-token-report.json

python -m tools.research.build_dialogue_token_engine --variant token \
    --rom build/runtime-roms/v3.gba --expect-sha256 <exact digest> \
    --out build/runtime-roms/v3-engine.gba --tokens Ya ha Kr in Ti YA HA KR IN TI
```

Unattended runs use `tools/runtime/run_token_engine_session.ps1` (start and finish
phases, so the launcher never owns the emulator's lifetime) and the A/B driver at
`build/token-analysis/kibito_ab.ps1`.

## 7. What is NOT proven, and the limits of the measurements

* **The base images and the rename map are not in this repository.** They are private
  derivatives of a proprietary image, so the v3 numbers cannot be reproduced from a
  clone alone. The tools take them as arguments and refuse anything that is not the
  declared digest; the canonical-image results in section 3 reproduce from a clone.
* **The Kibito route is driven from a savestate.** That state's EWRAM holds a decoded
  dialogue cache captured on an earlier build, and an earlier session recorded that
  the engine caches decoded containers there. So this A/B shows the route survives on
  the candidate; it does not by itself prove a cold boot reaches the same data. The
  cold-boot test needs the operator to drive.
* **One of the 451 records is not applied** (`3:2184:2112`), and a rename that does
  not apply is a gap, not a corruption. It stays at retail text and is listed by the
  tool.
* **Shrinking names are paid for with spaces.** The spaces sit immediately after the
  name they pay for and preserve every later offset, but they are visible as a wider
  gap, and extra spaces are extra wrap opportunities for the line fitter. The
  verifier reports these records separately; no word is created or destroyed.
* **The "no glyph record" image check and the 108 px width bound** on the production
  encoder are still opt-in seams (`has_glyph`, `check_widths`) with no caller from the
  product build; the splice path passes neither.
* **The cave address is still a constant** (`0x082ED210`, inside a measured
  3,019-byte zero run). The design asks for the region to come from the project's
  free-space machinery, and for a cave-only control; the builder checks that its 512
  reserved bytes are one uniform filler run and nothing more.
* **The unrelated defects are untouched**, as the ticket required: the `F0674DD8`
  crash and the unsafe tail allocation are not investigated here.

## 8. Next steps

1. Cold-boot the Kibito route from the battery save, with the operator driving, to
   remove the savestate-cache caveat from section 7.
2. Decide the content question for the one refused record, whose bytes two records
   both name.
3. Wire the dictionary document and the blob emission into the product build, and
   bring the two opt-in encoder rules into that path.
