# Friend v3 content pass: implementation record

Ticket FRIEND-V3-CONTENT-PASS-001. Baseline `origin/master`
`0fa1aa70fe22aecb4aa58d6e3c19098f14f10b92`. Plan and change table:
`FRIEND_V3_CONTENT_PASS_PLAN.md`. This record states what was applied, what is
blocked, and how each claim was measured.

**Review status.** Independent review of `a671a7ecf4e524e1e799eed9841f0b8b795bdbdc`
returned **PASS** with no open findings (tag `friend-v3-content-pass-001-reviewed`).
It came after three BLOCKED rounds: the first found a self-consistent check that could
not see its own span error, the second found five false sentences in these documents,
and the third found two guard gaps and two more false sentences. The commit immediately
after the PASS, `33b2b7ee33a1bd1fdd0dc41d03b4504c8f13bf0b`, changes one sentence the
reviewer had explicitly marked non-blocking.

The commits after `33b2b7e` are NOT covered by that PASS. A follow-up review of the
tip `a53adabf0ee35acc92f42c3d438f2e3d94d6eef9` returned BLOCKED on one false sentence
in this paragraph, which is the sentence you are reading the correction of; it also
noted that the review range from `a671a7e` contains four commits rather than two, and
that it could not check the tool claims about `appearance_authoring.py` or the
launcher's `-MGBPath` with the commands it was permitted. A later review read both
sources and confirmed them, so that limitation is closed.

## 1. The derivative

| artefact | sha256 | bytes |
| --- | --- | --- |
| rename base `roms\v3-safe.gba` | `b0de6ddffe53961bcade893107b7f9a8004d684b919552480ca688207e8f56d5` | 9740320 |
| splice output `ticket-splice.gba` | `cffdb81e471567fab623d3ec3a0b920cc0b5ef3f0a11bc5f3c70e5bab1395446` | 10132968 |
| engine output `ticket-engine.gba` | `d401d71c0ed3fbf93476aaa1825ea8c680e3caac7f7d7fbc05cbfe16344ab0f5` | 10132968 |
| **ticket derivative `v3-content-pass.gba`** | **`b3344a3fed42f13c34bdd28d74463e1f6a0d3e071f2a3cd159f73ef68e5885a7`** | 10132968 |
| canonical `roms\Dragon Ball Z - Buu's Fury (U).gba` | `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e` | 8388608 |

The splice and engine outputs landed on the digests the earlier cold-boot
acceptance recorded, byte for byte, which is how the composition is known to sit
on the verified foundation rather than beside it.

Composition, three steps, each digest-gated:

```text
python -m tools.research.splice_dialogue_tokens --base roms\v3-safe.gba \
  --base-sha256 b0de6ddff... --map build\crash-repro\rename_map.json \
  --tokens Ya ha Kr in Ti YA HA KR IN TI --out build\fv3cp001\ticket-splice.gba \
  --report build\fv3cp001\ticket-splice-report.json

python -m tools.research.build_dialogue_token_engine --variant token \
  --rom build\fv3cp001\ticket-splice.gba \
  --expect-sha256 cffdb81e471567fab623d3ec3a0b920cc0b5ef3f0a11bc5f3c70e5bab1395446 \
  --out build\fv3cp001\ticket-engine.gba --tokens Ya ha Kr in Ti YA HA KR IN TI \
  --splice-report build\fv3cp001\ticket-splice-report.json

python tools\research\apply_friend_v3_text_edits.py \
  --base build\fv3cp001\ticket-engine.gba --base-sha256 <the engine digest> \
  --out build\fv3cp001\v3-content-pass.gba \
  --report build\fv3cp001\v3-content-pass-report.json
```

## 2. What changed

One artefact supports this section and it is named here: the writer's own report,
`build\fv3cp001\v3-content-pass-report.json`. It records seven edits, a
`changed_byte_count` of **204**, and the exact changed offsets and their per-edit byte
counts, which sum to 204. Every other number an earlier draft of this section carried
was measured once and then written down with no archived artefact behind it, so those
rows are DELETED here rather than restated: the dialogue-container comparison, the
slot-diff count, the credits offset check, the slot-292 byte, the level table and the
two graphics regions. They are not re-asserted anywhere in this record.

Applied (seven sites): slot 1032 `Bulma` -> `Tulma`; slot 1033 the biography,
rewritten to daughters-of-Brief with the twin canon and **no marriage line**; slots
122 and 1453 `Great Saiyaman` -> `Great Soyman`; slot 603 `Great Saiyaman Saga` ->
`Great Soyman Saga`; slot 1346 `Saiyaman` -> `Soyman`; slot 1347 the ability line,
now `Great Soyman` / `back into Goku`. Each site's offset, current text and replacement
are the plan's section 3.1 table, and the tool's `SECTION_3_1` is the same seven sites.

## 3. A defect this ticket found and fixed

The first span writer measured a site's span as the distance to the next string the
1,534-pointer table names. That is wrong for this image: the earlier rename pass
relocated some slots into the appended block and left their retail copies behind,
unenumerated. The consequence, in the shape the report records rather than in round
numbers: the writer wrote far more bytes than the seven sites needed, because it
cleared everything between a site and the next named string. The fix is the rule this
document states below. The exact byte counts of that first bad run were measured once
and no report of it survives, so they are not quoted.

The tool's own stray-byte guard could not see it, because it computed the permitted
region with the same rule; and a slot-by-slot readback could not see it, because
nothing references the orphaned bytes. It was found by reading the raw region.

The shipped rule is now: a site's span is its own text plus its own terminator, the
replacement is written over the front of it, and every byte after the replacement
keeps its base value. Nothing is zero-padded, so no byte is written that the tool
did not prove was the site's own.

**Untested refusals, recorded as outstanding.** The refusals added to close independent
review findings are not covered by `tests/unit/test_friend_v3_text_edits.py`: a
table-named string starting inside the written span, a span offset a second table slot
aliases, a slot outside the table's range, and a `--report` path equal to the base or
the output. That suite's six tests cover the original four refusals only. This is debt,
not a known defect: each guard was exercised by hand against the real image and against
a synthetic case during review, and the writer's output on the shipped image is
unchanged by all four.

## 4. Blocked: the four spoken `Bulma` references

`1:26476:306`, `4:10050:156`, `4:18714:142`, `5:42592:1086` should read `Chi-Chi`
under the closure, and cannot be closed with the SHIPPING dictionary. The splice pays
for a substitution inside the replaced span, `Bulma` is shorter than `Chi-Chi`, and the
shipping ten-entry dictionary cannot compress the difference. Two independent reviews
reproduced those refusals; the exact refusal text was produced by a command that is not
archived here, so it is described rather than quoted.

The four records' recorded slack is record-level and already spent on the operator's
own padding, and the substitution table is global across all 451 records, so the
wording cannot be re-tuned for four of them.

This is a dictionary limit, NOT an impossibility, and the independent review is right
to say so: add one admissible two-letter token (`Ch` or `hi`) and `Chi-Chi` closes to
5 units, against a 256-token window with room to spare. The real cost of that route is
a dictionary change plus an engine rebuild plus its own Kibito runtime re-check,
because a new token alters the id order the engine patch and the dictionary blob are
built from.

Three routes exist, all outside this pass and all for the owner:

1. **Add the token and rebuild.** The route the review demonstrated, at the cost above.
2. **Widen the four records' decoded length** by the documented handle length field and
   `relayout_for_length`. This cannot use the supported authoring entry point as it
   stands: `target_named` refuses these records because they are not in
   `AUTHORED_DIALOGUE_TARGETS`, so it needs either a registry extension or a deliberate
   decision to call the low-level API past that gate.
3. **Accept the inconsistency** and close with the four lines carrying `Bulma`.

Extending the splice to accept a length change is rejected, because a plain grown
rename is what froze the Kibito scene.

## 5. Open owner decisions, unchanged

The addresses and values behind items 1 and 2 were surveyed during this pass but the
survey left no archived artefact, so they are NOT restated here as measurements. They
are stated as pointers to be re-derived:

1. Hercule's opponent difficulty: the lever is Hercule's enemy stat record, reached
   through the appearance-definition record that names him. Both were located during
   the pass; the survey is not archived, so any target numbers must be re-measured
   before they are written. Two constraints that do not depend on the survey: only hit
   points have measured consumption evidence, and the shipped enemy-stat randomizer
   also writes that record, so build order must be declared.
2. Tulma's blonde appearance: OWNER STATES IT WILL EXIST, and it does not exist yet.
   What is established without a survey: no appearance record was added or changed by
   this pass, and the biography deliberately makes no appearance claim, because a claim
   about hair colour in text would be false until the art lands. Two consequences for
   whoever builds it: a distinct appearance record (the table is append-only through
   `tools/webfoot/appearance_authoring.py`, with a documented ceiling above the
   canonical count and only the zero-argument lookup path taking it), and a distinct
   actor-sprite slot plus palette, since the object palette is shared.
3. The contradictory scan biographies. The plan's section 7 proposes wording for six
   sites, each measured to fit its span. Two further sites were found by reading every
   bio whose first sentence asserts a relation or an origin and are NOT in the plan's
   table: slot 1065, whose sentence is broken grammar inherited from retail ("Tien was
   once a rival of Yamcha is now a loyal Z-Fighter"), and slot 1043, which reads
   consistently under the closure and is recorded as ambiguous rather than wrong.
4. Chapter titles: ten saga strings, slots 602-612.
5. Spopo's target: `Android #13` or `Perfect Cell`. Both names exist in the game's text;
   whether either has its own actor was not established, so that is the first thing to
   check before choosing.

## 6. The runtime regression: RUN, PASS

Independent review is right that this section previously described the run as pending.
It was run on 2026-10-08 by the operator, on this image, from a cold boot with no
savestate. The launcher refused nothing and the run directory is
`build/friendv3-coldboot/content-pass/`:

| measurement | result |
| --- | --- |
| run copy of the image | sha256 `b3344a3fed42f13c34bdd28d74463e1f6a0d3e071f2a3cd159f73ef68e5885a7` and 10132968 bytes, as recorded in the run's own `inputs.json` |
| battery save used | `F6D79DC8896C52943DA38E012B3DEE0BBC119CFD4AC7D54EF3BC0862140315B7`, also from `inputs.json` |
| emulator | mGBA `0.11.0.0`, pid 18244, from `inputs.json` |
| frame heartbeat | frame 60 to **frame 15780**, 263 rows at a 60-frame cadence, **zero irregular gaps** |
| freeze detector | did NOT trip: the frame column grew to the end of the run |
| liveness channel | the dialogue copier fired **36** times, the first logged between frames 4500 and 4560 (`coldboot.csv` line 77), so execution was observed and the route reached dialogue |
| observed pc | mostly the idle `0x000001C4`, which is the normal idle address and is NOT the detector; the frame column is. Two rows after frame 4500 show another address |

Every row above is read from `inputs.json` or `coldboot.csv` in the run directory,
except the pc row, which is counted from `coldboot.csv`, and the freeze verdict, which
is the frame column reaching the end of the run. Earlier drafts carried a frame rate
from the emulator window title and a post-run hash claim; neither is written into any
run artefact, so both are deleted. One operator observation, attributed as such: the
session was launched from a cold boot with no savestate and driven by hand to the
Kibito scene, and the window was closed at the end.

**The mechanism line.** Copy 33 is the line the previous acceptance used as proof, and
it is present here: `It can't be! .ill.'s the Great S`, where the dots are two-glyph
token units composing `KRILLIN` at the retail unit count. Retail reads `Gohan` in that
line, so the image is displaying its own renamed text through its own dialogue engine
on a cold boot.

Controls, from the earlier cold-boot acceptance record, same route and same save: the
shipped reference `328f5dcf` survived to 10440 frames with 36 copies, the engine
candidate `d401d71c` survived to 13440 with 46, and the known-bad `ddfdf780` froze at
**frame 6900** (`FRIEND_V3_COLD_BOOT_ACCEPTANCE.md`, section 4). This run reached 15780
frames with 36 copies, past every one of those.

**Corrected figure.** An earlier draft of this section said the known-bad control
freezes "at about frame 1946". That number belongs to a different rig: the savestate
A/B in `DIALOGUE_TOKEN_PRODUCTIZATION.md` bounded at 3000 frames, where `ddfdf780`
reached 1946 of 3000. The cold-boot control's number is 6900. The independent review
caught the substitution; the sentence is corrected here.

### Reproducing the command

The Kibito route is played by hand: `tools/runtime/friendv3_coldboot_probe.lua` never
touches input and `start_friendv3_coldboot_session.ps1` exposes no input-route
parameter, so this leg needs an operator at the controls.

Every precondition was checked in this worktree before writing this section:

| precondition | measured |
| --- | --- |
| candidate image | present, 10132968 B |
| battery save | `roms\v3-fixed-credits.sav`, digest `f6d79dc8896c52943da38e012b3dee0bbc119cfd4ac7d54ef3bc0862140315b7`, the same digest the earlier acceptance used |
| mGBA dev binary | `0.11.0.0`, version read from the binary |

One trap worth recording: the launcher's DEFAULT `-MGBPath` is a path under
`build\tools\`, and in a fresh ticket worktree `build\` carries only the junctions
this ticket made, so that default does not resolve. Pass `-MGBPath` explicitly:

```text
powershell -NoProfile -ExecutionPolicy Bypass -File tools/runtime/start_friendv3_coldboot_session.ps1 `
  -RomPath <worktree>\build\fv3cp001\v3-content-pass.gba `
  -RomSha256 b3344a3fed42f13c34bdd28d74463e1f6a0d3e071f2a3cd159f73ef68e5885a7 `
  -SavePath <worktree>\roms\v3-fixed-credits.sav `
  -Label content-pass `
  -MGBPath <the mgba-dev extraction>\mGBA.exe `
  -ExpectedRomSize 10132968
```

The two text files and the worktree path are local to the holder of the private images;
the emulator binary is whichever `mGBA.exe` the `mgba-dev` extraction contains.

Then drive to the Kibito scene and close the window. For the negative control, the
same command with the known-bad image, digest
`ddfdf780591fd2fdbd37c6fe5118fe871088dc52ce3f6c7538bd5fc4d64c6286` and size 9764900,
froze at frame 6900 on this route and save. Evidence lands in
`build/friendv3-coldboot/<label>/`. The frame column of `coldboot.csv` is the freeze
detector, never the program counter.

## 7. Pre-existing gaps this pass did not introduce

The operator's 451-record pass leaves retail names in spoken dialogue. The per-name
counts were measured during this pass by decoding the engine containers, but no artefact
of that comparison was archived, so the counts are NOT restated here. What stands
without them: the four spoken records this ticket could not correct are examples of the
gap, and those records are the operator's, not this ticket's, so they are recorded
rather than repaired.
