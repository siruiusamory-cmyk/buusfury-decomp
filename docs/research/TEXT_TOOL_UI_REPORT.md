# TEXT-TOOL-UI-001 report: the Buu's Fury text editor

Ticket: TEXT-TOOL-UI-001, the standalone text editor for Buu's Fury in-game dialogue.
Preset: DragonByte Z Product Studio. Worktree: `log1-remake-text-tool-ui-001`, branch
`ticket/text-tool-ui-001`, cut from `4b9e55e4`.

## 1. What was asked, and what changed underneath it

The deliverable is a standalone Windows application that edits the game's in-game text
without any generated content, reusing the merged engine rather than restating it. Two
owner decisions arrived mid-ticket and reshaped it:

1. **Rebuild the presentation layer from the design references rather than audit it.**
   The first presentation layer was written before the reference skills were installed.
   The rebuild discarded it: theme, shell, panes, list, delegates, editors, context
   pane, preview, both dialogs, menus, status bar and iconography were replaced in new
   commits. History is intact; nothing was deleted from it.
2. **The in-game preview must be a real render, never an approximation.** It is now a
   real render or a line that says it is waiting, with the data contract it will consume
   written down, and nothing drawn in between.

What was kept because it was proven and is not presentation: the engine fix, the model
layer (`session.py`, `project.py`, `status.py`), the engine seams, the authored project
format, the release-3.1 export proof, the packaging approach and the Tabler icon
licence notice.

## 2. Feature checklist

Owner's MUST items, all present:

| Item | Where it stands |
| --- | --- |
| Open an image and detect its profile | `session.open_image`, the profile readout in the header, refusals surfaced verbatim |
| Search the text | the header field, `Ctrl+F`, the empty state names the term that matched nothing |
| Edit a line | the NEW section, one edit path through `session.set_edit` |
| Undo and redo | one `QUndoStack`, one step per user action, one step per rename batch |
| The three-way comparison | RETAIL, CURRENT and NEW, identical in treatment, one emphasis |
| The length meter | two segmented bars, character and byte, with the threshold and a stated budget |
| The move notice | persistent, names the covering records and the site count, never expires |
| Rename with per-occurrence decisions | the rename dialog, one table, a decision per hit |
| Export a new image | always Save As, always a new file, readback clean, the input untouched |
| Settings persist | theme, splitter, shape, order, grouping |
| A visible version | the title bar and Help, from `identity` |
| Determinism | the same authored input and the same edit list produce the same bytes |

Owner's SHOULD items: the shares/coverage statements, the context pane's evidence, the
address disclosure and the export summary are all present.

Owner's additions from the coordinator relay, all present:

| Addition | Where it stands |
| --- | --- |
| One row per spoken line, with the record list behind a toggle | the Dialogue tab defaults to Lines; the shape control switches to Records |
| Line-level separation, order of appearance | the line rule splits at the soft end and the line break; Appearance is the first handle site |
| A speaker column and speaker grouping | `Speaker (by portrait)`, a filter, and a grouping whose headings are the 67 labels and the four honest gaps |
| Group by map in map-table order | the placement route, 26 groups, ending in one `Unplaced` group whose reason line states why |
| The in-game preview | a real render, decoded from the image the reader opened, proved pixel for pixel against native captures and against the RE Lab's own model; the scroll case states itself instead of guessing |

## 3. The design the UI was written from

`docs/research/TEXT_TOOL_UI_DESIGN.md` was written before the rebuild and the rebuild
follows it. It names, per screen and component, which rules were applied from which
entry: Refactoring UI for the scales, the two weights and the border-versus-divider
distinction; Impeccable for hierarchy and disclosure; UserInterface.wiki for the
control sizes, the tabular figures and Jakob's law; Laws of UX for Fitts, Hick,
Von Restorff, Doherty, Peak-End and the active user; Make Interfaces Feel Better for
the state set, the icon stroke and the review protocol; Hallmark for the eight states,
the honest copy and the anti-generic gates; Nothing Design for the row rule, the
chips, the segmented meter and the bracket status text; Swiss for the accent and the
grid; and Taste only for its anti-generic tells and its content rules, because Taste's
own text excludes dashboards and data tables from its scope.

The note also records the conflicts with the adopted spec rather than resolving them
quietly, and section 7 records what each build taught, including the light-theme
control defect described in section 6 below.

## 4. Gates and tests

At the frozen candidate:

- Focused tests: 276 passed, none skipped, across the theme, the dialogue preview, the
  render, the list, the editor, the shell, colour vision, the model, the engine and the
  release files. Nothing was run from the full suite or `scripts/test.ps1`.
- The preview's two ROM-gated cases RUN rather than skip, because the canonical image is
  present in this worktree: 5,610 (record, limit) pairs compared against the RE Lab's own
  model with no compared pair disagreeing, and native 240x160 captures reproduced pixel for
  pixel. What each case counted rather than compared, and why, is stated in section 9.
- `python -m tools.quality.public_release`: 4 products, 0 findings.
- `python -m tools.quality.architecture`: 0 violations, 5 observations, all pre-existing
  large-module readings in the other desktop application.
- `python -m tools.quality.public_surface --all`: 0 findings over 1,154 tracked files.
- `python -m tools.quality.readability --all`: 0 hard hits, with 103 advisories, a
  pre-existing reading list that never changes the exit code.
- `python -m tools.buufury_text --smoke`: exits 0.
- The export end to end on release 3.1 passes, and the artifact is unchanged.
- The one-folder package builds, carries the Qt SVG plugin and all 19 icons, and its
  executable smokes to exit 0: `914c1d57d10343e27da5431b759960983bcfab7b6365b4a2394d8612a7459e1c`,
  88.5 MB in 122 files.
- The mechanical anti-generic runner reports exactly one finding, the recorded prose
  measure conflict, and prints what it cannot see.

## 5. Screenshots and colour vision

Nine captures of the running application: dark and light at 100 percent, dark and light
at 150 percent, and dark at the window's minimum size, which were taken before the preview
landed, plus four of the in-game preview itself. They live under the ignored
`build/acceptance/text-tool-ui-001/` and are not committed. Each one's SHA-256, so a
reviewer can tell whether a file was replaced:

| Capture | SHA-256 |
| --- | --- |
| `final-dark-100.png` | `9f98245e3c0de4f6659d1f5a022bf2e4800b55f1400d2a82a2eee1d3d7ec8088` |
| `final-light-100.png` | `c9ab8f41fe36c9ba2d093ec8d0a180a67c5ccf73d1a07a29736ac8bab64bf2bf` |
| `final-dark-150.png` | `d56e59b2c4700c9fe73071227797479917bb9d94282981c51e32221cd42c9c73` |
| `final-light-150.png` | `795db31d384935caafb6fa54948b455b4a99b01d709bb810b0331622ea7b722b` |
| `final-dark-minimum.png` | `24bbac8270ff3b8c3eef9c370ca3a5db576d6f9d2ee87b2ca1f799cd82734b76` |
| `preview-render-dark.png` | `76ea08e68cb7f7e3663632e754fa7da97a2ec66650a397529718b8744177df19` |
| `preview-render-light.png` | `7fe29feedb5d8aace46c4e9139ce91132a4690ec9605c0ba669bf7467f3cf113` |
| `preview-render-dark-150.png` | `ba5bcd945bb2e30e34e4a46162f30339a1fc57b4d9e3d1fb2f9cb026541174c5` |
| `preview-limited-dark.png` | `8348fe49ed38a124d746ad4dd513405b3475904b6d380bd6450ed43c894c6040` |
| `preview-slot-dark.png` | `78aafb640604844edbd5cac7de4ca2e7e43eec8de74dcdd13572fe94a6f7df0a` |

The first three preview captures are the game's own box drawn in the pane, with the
record's text in the game's own font over the game's own art, at 100 percent in dark and
light and at 150 percent. The fourth is the honest refusal: a record the box cannot hold,
saying how many lines it needs, how many the box holds, and which rule is missing, with no
box drawn at all. The fifth is the other refusal, reached from the Names and bios tab: a
string slot, which the engine never draws in a dialogue box, says
`no box is drawn, because this row is a string slot`.

Thirty colour-vision conversions accompany them: each capture through deuteranopia,
protanopia and tritanopia.

**The conversions are a scripted simulator, not Color Oracle.** Color Oracle 1.3 is
installed and launches, but its tray menu could not be driven from this harness: the
tray is a transient X11-composited panel that the driver does not enumerate as a
window, a desktop-scope click needs a foreground swap that fails on this busy desktop,
and the panel closes on focus loss. This is reported as a substitution with its reason
rather than presented as the tool the owner asked for. The substitute is
`tools/qa/colorvision.py`, which applies the Machado, Oliveira and Fernandes 2009
matrices at severity 1.0, read from the authors' own page, in linear RGB as the model
defines. Every row of every matrix sums to one, which a test asserts.

What the conversions establish: the only chroma in the window is the accent, and every
state is carried by a word, a glyph, a marker shape and a brightness step. Measured for
the rule itself: pure red and pure green start 120 degrees apart in hue and collapse to
under 3 degrees under both protanopia and deuteranopia while their lightness stays
about 40 apart, which is why a state may never ride on a hue. Under the conversions the
selected row's fill and its accent indicator both survive as lightness steps.

## 6. The two audits, before and after

Two independent read-only passes ran against the rebuilt window. Both are quoted with
their own counts, because the owner asked for the before and after numbers.

### Hallmark audit

| | `a19b587` | `a4c0a28` | `e83ec25` |
| --- | --- | --- | --- |
| Gates assessed | 58 | 58 | 58 |
| Pass | 24 | 25 | 31 |
| Fail | 4 (4, 40, 41, 48) | 4 (26, 39, 40, 41) | 3 (25, 35, 46) |
| Pass as recorded deviation | 4 | 4 | 4 |
| Not applicable to a native desktop tool | 24 | 23 | 23 |
| Could not check | 2 | 2 | 2 |
| Severity | 1 critical, 2 major, 5 minor | 0 critical, 3 major, 4 minor | 0 critical, 3 major, 3 minor |
| Verdict | needs changes | needs changes, critical gone | the critical is gone and the three remaining fails are settled below |

Of the third pass's three remaining fails, one is a recorded conflict (gate 25, the prose
measure at a wide centre pane), one is a mislabel in this repository's own mechanical
runner and is corrected there rather than in the build (gate 46, the invented-metric
gate, which the audit showed is APPLICABLE and passing because every figure on screen is
the engine's own: the meter's counts, the container offset, the span), and one was real
and is fixed: gate 35, the changed run carrying a word but no underline.

The critical is the one worth naming. With a stylesheet installed but no rule naming it,
Qt paints a control with ink of its own choosing: the light theme rendered the menu bar,
the four combo boxes and the address disclosure as white on the `#F3F4F6` window, about
1.09:1, while the dark theme painted all of them correctly, so every dark reading was
green. The theme now names every control class and gives it a token, and the guard is a
rendered-pixel case in `tests/unit/test_text_tool_theme.py` that renders each class and
requires 4.5:1 between a widget's own ink and its own fill in both themes. Proved
against the defect rather than assumed: with the control rules removed the same
measurement returns 1.09:1 in light and 14.98:1 in dark, the exact asymmetry that hid
it, and with them in place 15.59:1 and 14.24:1.

Every major from the second pass is closed and each has a measurement behind it: the
combo boxes carry their drop-down arrow again, measured by the rule's effect on the
painted band rather than by reading the stylesheet; the status badge stops where its word
does, so the row's own fill and its divider run to the cell's edge; and the meter's
untouched state states the row's own budget instead of printing one placeholder twice.
The third pass's three majors are closed too, and two of them were not cosmetic: the
rename dialog had no entry point anywhere, so the per-occurrence flow the owner asked
for was unreachable, and the counters line painted zero pixels at every window size
after a fix that was meant to let it elide.

One finding of the third pass is contested and not actioned, with both measurements
named: it reported the panes squeezed below their natural minimums with a list-pane floor
of 664 px. That figure comes from the offscreen Qt platform, which on this machine has no
font directory and falls back to a font about 50 percent wider. The same pane measures
350 px on the real platform and the window's own minimum is 1018x611, which is what this
worktree measured independently, so the 664 px floor is an artifact of the offscreen font
rather than a defect.

### break-ui worst-case pass

| | `a19b587` | `a4c0a28` | `e83ec25` |
| --- | --- | --- | --- |
| Observations | 89 | 142 in the primary pass, 394 with the scaling passes | 199 per platform, 796 across four |
| Case families | 13 base, 24 identity strings | 19 base, 42 identity strings | 28 base, 64 identity strings |
| Families with a break | 8 | 11 | 3 |
| Severity split | 2 blockers, 5 majors, 1 minor, 1 nit | 1 blocker, 2 major, 4 minor, 2 nit | 1 blocker, 2 major, 2 minor, 3 nit |

The third pass's blocker is the one this report would put first if it could keep only one
finding: **a document position is not a string position.** A control unit is two
characters in the canonical string, the escape byte and its operand, and one character in
the document that draws it, so every edit route handed the document's number to a
function that counts the string's. Measured before the fix, typing `XYZ` at the end of a
line carrying a unit produced `Line one <unit> enXYZd`, the two-unit line landed two
characters early, and a line ENDING in a unit dropped the keystrokes with no refusal and
no message, which is a silent write failure rather than a display one. The conversion is
now three pure functions applied at every boundary, and the case is parametrised over
five shapes including the trailing one.

The pass's two majors were the unreachable rename dialog and the counters line, both
described above. Its minors were the status bar never releasing its message region, which
now clears when the selection moves; an unraisable exception at process exit from a
context-free lambda on the undo stack's clean signal, which now connects the bound
method; and the check glyph being drawn twice, once by the themed rule and once as a
character in the chip's own text.

Its blocker was the worst defect the rebuilt layer had, and it was found only by feeding
the widget a line that carries a control unit: `ChipObject.intrinsicSize` and
`drawObject` were declared without the position argument Qt passes positionally, so the
character format bound to an integer and both raised inside the Qt override. The
consequence was not a missing chip. The failure happened part way through rebuilding the
document, so the editor was left holding the PREVIOUS row's text while the list had
already moved on, and a commit from that state wrote the previous row's text under the
new row's key. Both stubs now take the position; the atom is measured in the face it
paints in rather than through a paint device that carries no font; and `set_text`
assigns the canonical string only after the document is built.

Why every test missed it: `intrinsicSize` runs during layout, so a widget that is never
shown never calls it. The new case resizes and shows the widget and reads the laid-out
size. Proved against the defect: with the old signature the same route raises
`'int' object has no attribute 'property'`, and with the fix the document lays out at
276x35 with its string intact.

Its other majors and their outcome: the window opened with the editor and the context
pane empty because the pane selects its first row before the shell can hear about it,
now replayed once after the panes are built; the read-only sections' cap was inert at a
short window height, now applied from the editor's own height; and at 150 and 200
percent Windows text the list pane's own minimum grows past its fixed floor so the chips
and counters elided, now the floor is the larger of the constant and the pane's own
minimum.

A defect this pass also caused to surface: the chip's check glyph, which is the channel
the owner reads a chip's state by, had never painted at all. A base64 data URI is
accepted by Qt's stylesheet parser and then paints nothing, silently. Measured on one
button: 40 ink pixels for its text alone, 40 with the data URI, 100 with the same icon
written to a file. The recoloured icons now go to temporary files and paint; a checked
chip carries 118 ink pixels against 78 unchecked.

### The independent review, and its four blockers

The independent review of the frozen candidate returned BLOCKED with four blockers. It
held five other claims and reproduced the release-3.1 export independently at
`59d7fb22`. All four are fixed, and the fix carries a case that bites:

**Two edits to one record kept only the second, silently.** The one that lost work: the
edit for a row was built from the original record text and stored under the record, so a
second row's edit overwrote the first and undo could not bring the first back, because
undo restores the record's text and the first edit was no longer in it; a rename batch did
the same. Every edited row is now an entry of its own carrying its span in the original
record, and the record's text is rebuilt from the original with all of them applied in
offset order. A whole-record text is a base the pending rows are re-applied to, and where
a row cannot be located exactly once the combination is REFUSED with a reason rather than
guessed. Measured before the fix on release 3.1, a record with eleven lines: editing its
first line then its second left only the second. Three session cases and one window case
now cover the two-line edit, the clear of one row, the rename composed with a pending line
edit, and the undo of each.

**A one-character control unit was converted as if it were two.** Only the ink escape
`0x08` plus its operand is two canonical characters; `0x0A`, `0x0B` and every other code
below `0x20` are one, so the document-to-string conversion put the caret one character
late for each such unit before it, accumulating. The exposure is the Records shape, 306 of
release 3.1's 2,818 records. Proved by falsification against the restored old code: typing
just after a one-character unit landed one character late in five of six probe strings.
An insertion at a unit's own start edge was also refused contrary to its docstring, and
now is allowed while the interior stays refused.

**The preview's states were dishonest in two ways.** It turned ready when data files
merely existed, without the harness the design requires, and a malformed part counted as
present. That whole file-presence path is gone with the runtime decode, and the equivalent
rule is that the pane is ready only when it can actually render the record, with any
decode failure a stated missing part and a waiting state.

**The empty state claimed a speaker field the data does not have.** `no line in this image
is spoken by` now says the portrait is not drawn, which is what the record supports. The
rest of that file was read for the same over-claim and that sentence was the only one.

The review's non-blocking findings are also in: the licence notice said eighteen icons
while nineteen ship, and a case now checks the notice against the icon directory; the
engine research doc said no map link exists and now records the measured route with its
inferred step named as inferred; the recoloured-icon directory is removed when the process
ends; the rendered-ink guard covers the menu, the popup, the tab bar, a header, a table
body and the tooltip, which were unverified in pixels; and the per-keystroke undo
granularity with its unmeasured plan-recompute cost is recorded rather than left implied.

Two of the review's statements are contested with both measurements named. Its pane-floor
finding reports 664 px from the offscreen platform, whose missing font directory falls
back to a font about 50 percent wider; the same pane measures 350 px on the real platform
and the window's own minimum is 1018x611. And its "178 lines span a non-cutter record
boundary" could not be reproduced under any definition tried; what was measured instead,
and recorded in the engine doc, is 179 records that never cut a line and 821 lines that
run across a boundary one of those records owns.

### The delta review, and the two blocking findings it found in that fix

The delta review returned BLOCKED again, and it was right about both. It held B2 (0
failures in 20,000 randomized conversion checks), B3's states and engine rules, the four
counted cases recomputed, the scroll refusal, the edge insertion, the icon count and the
five earlier claims.

**F1. The fix for the first blocker introduced a wedge.** `set_edit` wrote its whole-record
text BEFORE checking that the combination composed, so a refusal left the record holding a
text nothing could be read through: the review's own repro is edit line 2, rename line 1,
then Undo, which raised, did nothing, and left `pending_text`, `state`, `counts` and
`matching` raising for that record until the window closed. A second Undo then baked the
line edit into the record with an empty undo stack. The root cause was that a whole-record
text was a base and line entries were found inside it by SEARCHING for their old text,
which has no answer once the base already contains a different version of that line, and
which is why the same wedge appeared from the Records shape on every keystroke.

**F2. Renames did not compose.** Two rename batches on one record kept only the second,
because each built its text from the original and replaced the whole of it: `One\nTwo`
renamed `One` to `Uno` and then `Two` to `Dos` read `One\nDos`. The same silent-loss class
as the first blocker, on the very path the fix claimed was closed.

**How they are closed.** Every edit this session holds is now a SPAN of the ORIGINAL
canonical text: one per edited row, plus one per span a rename batch contributes, each
carrying the row it came from and nothing else. The composed text is rebuilt from the
original by applying them in offset order, so two entries compose by construction, a
rename and a line edit compose, and two renames compose, none of them ever located by
searching. Three placement rules replace the search: an entry wholly inside a new one is
superseded, an identical span is replaced, and a PARTIAL overlap is the one case with no
honest answer and is refused BEFORE anything is written. Undo stores SNAPSHOTS of what a
record held rather than texts, so restoring one cannot be refused, which is what makes the
review's own repro restore cleanly and leave every reader of that record answering.

The cases that carry it: two renames of one record both land; a rename and a line edit
compose and a snapshot restores them; a rename inside an edited line is reported and
wedges nothing; typing the whole record in the Records shape supersedes the line entries
inside it and is never refused; and at the window, undo of a rename beside a pending line
edit restores both and leaves the record's state, counts and matching answering.

Under three more findings: the layout choice is a coordinator instruction that is not
measured and it is now disclosed where a render is read; the capture comparison mapped a
`per_character` index onto unit positions and cut every multi-line reveal short, so the
instrument was wrong rather than the render, and it now asserts the outcome; the corpus
case counted 588 pairs it can compare and now compares them; the pane's soft end and a
string slot both reported ready while drawing something the engine would not; the
vendored model's provenance names a commit that exists on origin, and six lines of
decompiled pseudocode left the committed test in favour of the address and the source
document.

## 7. End to end, on release 3.1, with digests

- Input: `roms/v3-release31.gba`,
  `f5c9648bbf7a9b448d801866cc775eb76abd270f7c16fb93d4e01630ef236201`, unchanged after
  the export.
- The plan renames one retail-attributed occurrence and grows one line, both chosen by
  the acceptance test's own helper so the artifact and the tested export are the same
  bytes: 2 records moved, 0 in place, 0 refused.
- Output: `build/acceptance/text-tool-ui-001/release31-edited.gba`, 10,194,636 bytes,
  sha256 `59d7fb22673848f9f45678dc0011ebee166404d256108afdc2a231be58ceab3d`.
- Readback through the product reader is clean, and the authored strings are read out of
  the output image: the renamed record reads
  `Oh, one more thing... Do you see that circle on the ground? It's called a
  \x08\x07Kakarotto Circle\x08\x02.` and the grown one ends
  `... Have you no respect? and friends`.
- Runtime: the image loads in mGBA and execution advances. Measured over 336 rows,
  frame 60 to 20160, `rom_size` 10194636 on every row, 62 distinct program counters and
  67 screenshots, with the title screen captured. Section 8 row three: execution
  observed. The dialogue copier never fired on that cold boot, so the on-screen
  rendering of the edited line is UNVERIFIED and is not claimed.
- The canonical image and the save are unchanged: `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`
  and `7cf0a516ebebbc74a959d6fc1ebc7aac808fc99683ccbb9e4b82a0d58ba02a86`.

The UI rebuild changes no generated byte, so the end-to-end proof is the same export the
model layer produced. No new emulator run was made for the rebuild.

## 8. Deviations from the visual spec, each with its reason

1. **The left pane's floor is 368 px, not the spec's 260.** The owner's speaker column,
   the four state chips, the status word and a readable text floor cannot all fit below
   it. The spec's own range is 260 to 470 and the default of 420 sits inside it.
2. **The row count is a tab tooltip, not part of the tab label.** Measured: the two tab
   names plus a total on the counters line want 399 px inside the pane's 350 px viewport,
   so one of the two must elide and the names are what a reader navigates by. The
   counters line carries the three state counts.
3. **The type ladder is six whole-pixel roles, not the spec's 9 and 10 pt.** Whole pixels
   are what survive 100, 125 and 150 percent display scaling.
4. **The light surface is pure white and the neutrals are pure greys.** Both are the
   adopted table's own values; the anti-generic gates prefer a tinted neutral and no pure
   white, and the spec governs.
5. **The control border carries 1.60:1 in light, not the 3:1 the design note itself
   asks for.** The adopted table calls the border intentionally subtle.
6. **Mono appears in more than two slots.** The spec mandates it for identifiers,
   offsets, sizes and hashes; it is a data role and never touches prose or labels.
7. **The prose measure exceeds the 45 to 75 character band at a 750 px centre pane.**
   Capping it would put the editor below the 80-column width the spec rejects.
8. **A text scale above 100 percent grows the window rather than compressing the
   controls**, because the pane's own minimum is larger than its floor.
9. **`NEW`'s emphasis is the accent hairline alone.** The two-weight ladder cannot give
   it a weight step; the note's wording was corrected rather than the build.
10. **Color Oracle was replaced by a scripted simulator** for the colour-vision
    conversions, with the reason in section 5.
11. **The changed-run underline is drawn at the font's thickness rather than a chosen
    2 px**, because Qt exposes no underline width. Recorded at the call site.

## 9. The in-game preview, and what it is proved against

The pane draws the game's own dialogue box from the image the reader opened: the font
through its 12-byte descriptor, the box art through the layout record's own container,
and the colours through the image's own 256-entry object palette. Nothing ROM-derived is
committed, no path is machine-specific, and the widget computes no engine value.

The layout rules are the seam document's, and two of them were settled by reading the
image's own code rather than by preference. **Which layout a record takes** is measured:
the dialogue box constructor at `0x08012012` picks layout index 1 only when the record's
portrait operand is EXACTLY 7 (`0x08012104` to `0x0801210A`), and index 0 otherwise, and
the builder composes the layout as `0x08071720 + 0x10 + index * 0x14` and stores it at
`0x0800B29E`. Index 0 is layout `0x08071730`, limit 144, art container `0x08071758`; index
1 is layout `0x08071744`, limit 128, art container `0x08071A6C`. The layout carries BOTH
the wrap limit and the box art, and the pane takes both from the same record.

This corrects an earlier version of this pane, which chose by whether a portrait was drawn
at all. That proxy is wrong for exactly one operand: operand 0 means no portrait and takes
index 0 with the 144 limit, where the proxy gave it 128. Operands 1 to 6 and 8 and above
take index 0, which the proxy got right by accident. The rule that first arrived with this
ticket, "portrait to 144 and no portrait to 128", was a coordinator instruction that also
claimed the seam document established it, which it did not; it is replaced here by the
measured rule, and the case for operand 0 is the one that proves the difference.

The second rule re-read from the code is the fitter. `FUN_0803DE6A` accumulates each
glyph's advance, compares the sum against the caller's limit, and on overflow either
rewinds to the last space it saw or, when it saw no space, returns without advancing. The
advance is the record's stored width plus one, read from the same code. A run wider than
the limit is therefore broken inside the run, which is what this pane draws and what the
RE Lab's copied model does not.

**What it is proved against.** Two cases, both from the canonical image at test time. The
counts are (record, limit) PAIRS, not records: 2,805 records at two limits is 5,610 pairs,
and the first review of this section found the earlier wording calling them records. Both
cases were made stronger after that review, and both numbers below are the ones the tests
themselves print.

| Case | What it compared | Result |
| --- | --- | --- |
| The RE Lab's own model, whole corpus | 5,610 pairs, with the vendored reference adapted to the engine's control units: the `0x08` escape and its operand stripped, each `0x0A` a new line, `0x0B` the record's end | 3,964 exact pixel for pixel, 150 exact at their ink positions where a `0x08` escape selects another ink index the reference does not model, 14 carrying a run wider than the limit, 0 running past the box, 1,097 needing more lines than the box holds, 385 refused for keeping text after their own `0x0B`. No compared pair disagrees |
| Native 240x160 captures | the box located in each frame, its ink pixels against the render | 68 frames examined, 34 with a located box, 11 reproduced pixel for pixel, 0 located-and-identified frames disagreeing, one of the 11 over more than one line |

The capture case had an instrument bug of its own, which the review caught. It applied the
reference's reveal prefix, which counts the characters it kept and drops the space it
wrapped on, to UNIT positions, which cut every multi-line reveal short.
`shot-3000.png` in `log1-remake-fv4/build/friendv3-coldboot/friendv4a-box2` was reported as
3 pixels different; with the prefix mapped onto the unit it lands on, the frame reproduces
over a 93-character prefix in 4 lines, 1,194 ink pixels, exactly the reviewer's own
measurement. The case now asserts the outcome rather than that something was reproduced,
and that assertion was checked by re-patching the old cut in and requiring the case to
fail: it does, naming the frame and the 3 pixels.

The 600 pairs the old predicates counted on this tree (253 carrying a control unit, 347 the
unadapted reference ran past the box) are now compared rather than counted where they can
be: 65 exact pixel for pixel, 150 exact at their ink positions, 385 refused for the soft
end, 0 differing.

**The two documents disagree about the 20 px reduction.** `DIALOGUE_EXPANSION_TOKEN_DESIGN.md`
states that a reduction to 124 and 108 is handed in on the canonical image; the seam
document states that the `-0x14` reduction is not established. Both cannot be true, the
seam document is the later measurement, and this preview therefore treats the case as
unestablished and refuses it. The contradiction is recorded here instead of being resolved
by picking the convenient one.

**The states it refuses to guess.** `waiting` when there is no image, or the font or the
box art will not decode, and it names the exact missing part. `limited` when a case the
measurement leaves open is on screen, and it names WHICH rule is missing, because there
are two: a record that needs more lines than the box holds says so and names the
scroll-advance rule, and a record that keeps drawable text after its own `0x0B` says so
and names the reveal rule after the soft end, which no read code establishes a
continue-past path for. A string slot states that no box is drawn because the row is a
string slot. Measured on release 3.1: the largest record needs 92 lines at the 128 limit
and 80 at the 144 limit against a box that holds four, and a record reached from the list
shows `this record needs 81 lines and the box holds 4`. Every one of those states paints
one sentence and nothing else, so a case the measurement leaves open is visibly not drawn
rather than drawn approximately.

Three captures of the render and one of the refusal are in the colour-vision set: the
render at 100 percent in both modes, at 150 percent, and the limited state naming the
missing rule.

## 10. Boundaries held

- The canonical ROM, every save and every savestate were never written, moved or
  committed. The worktree keeps its own verified copies under the ignored `roms/`.
- No ROM, save, savestate, extracted game art, font or game text was committed to the
  repository, pasted into a report, or sent to any hosted service. Every extraction and
  capture lives under ignored `build/` paths.
- No new dependency was added. The colour-vision tool uses the Qt already required.
- Nothing was installed for the application. The one installation in this ticket's
  history is Color Oracle, which the owner ordered.
- One writer per file at all times: four rebuild lanes and two fix lanes ran against
  disjoint file sets, and the coordinator held the remainder.

## 11. Harvest

Toolbelt and tool entries added to the project:

- `tools/qa/colorvision.py`, the colour-vision simulator, with
  `tests/unit/test_colorvision.py`. Generic to any surface of this project, not specific
  to this ticket.
- `tools/webfoot/textedit`: `MapTable`, `MapRow`, `maps()`, `record_maps()`,
  `line_maps()` and the map fields on `TitleProfile`, which turn a map into a dialogue
  line's owner for any caller.
- `tools/buufury_text/session.py`: `Line.place`, `Line.place_index`, `place_coverage()`,
  `map_order()`, `PLACE_EVIDENCE`, and a `BY_PLACE` grouping in map-table order.
- `tests/unit/test_text_tool_theme.py::test_every_control_class_is_painted_in_the_theme_ink`,
  the rendered-pixel guard that a source-level gate structurally cannot be.
- `docs/research/TEXT_TOOL_UI_DESIGN.md`, the design note, which is the reusable part of
  this ticket: the entries applied, the token set, the per-surface build, the recorded
  conflicts and the rules each defect taught.
- `build/ttui-exit-check.py` (ignored, not committed), the mechanical gate runner for the
  anti-generic checks, which printed what it could not see. **It no longer exists**: a fix
  lane cleaned its own scratch files with a `ttui-*.py` pattern and removed this one with
  them, which is a real hazard of keeping an instrument inside a shared scratch directory.
  Its last result is the one recorded in section 6, one finding, the recorded prose
  conflict, and its blind-spot list is what the rendered-ink guards now cover.

## 12. Unverified, and the risk that carries

- **The in-game preview renders from the image, and the render is proved rather than
  asserted.** It was the ticket's own headline requirement, and it is met: the pane decodes
  the font, the box art and the palette from the image the reader opened, draws the box the
  engine would draw, and is compared pixel for pixel against the RE Lab's own model over the
  whole canonical corpus and against native 240x160 captures. What remains unproven inside
  it is named in section 12, and the two unproven branches are refused rather than guessed.
- **The edited line has not been seen on screen in the emulator.** The image loads and
  executes and the strings are present in the output, which is what was asked for here;
  seeing it in a dialogue box needs a driven route.
- **Most interactive states are unverified in pixels.** No capture shows a checked chip,
  a refusal, an edited row, the changed-run underline, `BASE CHANGED`, the address
  disclosure expanded, either dialog, or a menu open. The code declares them and the
  states carry a word, a glyph and a shape; no capture proves them.
- **Keyboard traversal, screen-reader names and focus order** were not exercised.
- **The two dialogs were not driven** in the audit pass.
- **125 percent display scaling** is claimed by the ladder and was not captured; 100, 150
  and the window minimum were.
- **The mGBA rule changed during this ticket**: runtime evidence now requires a visible,
  non-minimized window from the launcher the runtime skill names. No emulator run was
  needed for the rebuild, so the rule was not exercised here.
- **The frozen package was rebuilt and smoked at this candidate.** A one-folder
  PyInstaller build against this tree produced 88.5 MB in 122 files, and the packaged
  executable ran `--smoke` to exit 0 in under 120 seconds with no window. The Qt SVG
  image plugin travelled inside the bundle as
  `_internal\PySide6\plugins\imageformats\qsvg.dll`, with `Qt6Svg.dll` beside it, and all
  19 icons were staged, which is the requirement that the drawing plugin and the icon set
  survive packaging rather than only working from source. The executable's SHA-256 is
  `914c1d57d10343e27da5431b759960983bcfab7b6365b4a2394d8612a7459e1c`. An earlier attempt
  at this build was cancelled before it finished, which is why the first version of this
  report recorded the proof as resting on an earlier commit; this line supersedes that
  and records the measurement.
- **The application's own start paths are all exercised**: `python -m tools.buufury_text`
  runs, `--smoke` exits 0, `--version` prints the product name and version, and the
  packaged executable does the same.
- **The underline over a control unit was measured on the shipping platform only.** The
  offscreen runner paints an extra-selection underline in a plain document and none in a
  document carrying an inline object, measured at 91 accent columns against 0, so the
  atom case asserts its marked ranges offscreen and its pixels on Windows.
- **Every keystroke in `NEW` pushes its own undo command and invalidates the plan.** No
  command merging happens, and each invalidation recomputes the plan, which copies the
  whole image. The latency of that on release 3.1 is not measured. It is recorded as a
  known cost rather than a defect, which is how the review recorded it.
