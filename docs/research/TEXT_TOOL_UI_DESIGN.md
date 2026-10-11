# The text tool: UI design note

Date: 2026-10-10. This note is the design the Buu's Fury text editor's presentation
layer is rebuilt from. It was written before the rebuild, from the reference entries
named below, and the build follows it rather than the other way round.

## 0. Authority, in order

1. **This repository's recorded policy**, `docs/ROM_SAFETY.md` and
   `docs/DEVELOPMENT.md`.
2. **The adopted visual direction**, Cartridge Workbench: the deep research report the
   coordinator holds, plus its text tool decisions brief. It owns the palette, the
   three-pane layout, the component list and the density band. Where a reference
   entry disagrees with it, the conflict is recorded in section 6 and the spec
   governs.
3. **The owner's hard constraints**, which nothing below may override: the owner is
   red-green colourblind so no state may be carried by red against green; the look
   is dense and native rather than web; the pixel font appears only in the dialogue
   preview; the shipped tool generates no content of its own.
4. **The reference entries**, listed in section 1, used for everything the spec does
   not decide: hierarchy, rhythm, states, comparison semantics, list and table
   craft, meters, empty states, dialogs, iconography and the anti-generic gate.

**What is not rebuilt.** The engine fix, the model layer (`session.py`,
`project.py`, `status.py`), the engine seams (`units`, `locked_tokens`,
`rename_occurrences`, `lines`, `portraits`), the release-3.1 export test and the
packaging approach are proven and stay. This note rebuilds presentation only.

## 1. Entries applied, and the rules taken from each

| Entry | Applied rules | Where |
| --- | --- | --- |
| **Refactoring UI** | One spacing scale and one type scale, no ad hoc values; two weights only (400 and 700, never a 300 layer, never a lighter weight to de-emphasize); three text colours maximum, all at 4.5:1; **control borders and content dividers are two different tokens**; never grey text on a coloured background; never colour as the only signal; more space around a group than within it; labels are a last resort; numeric columns right-aligned; dense is legitimate as a stated decision; work in grayscale first | tokens (section 2), list (3.2), editor (3.3), context (3.4) |
| **Impeccable** | Operate mode: make the frequent action easy to find and carry out; hierarchy by weight, size and space rather than by colour or boxes; reading order and keyboard order must agree; distill by removing repetition and revealing occasional options on demand; every defect, missing state and empty state is a polish item; the audit priority ladder for triage | whole window, editor labels, control disclosure |
| **UserInterface.wiki** | Interactive elements at least 32 px; expand hit areas with padding; minimise choices and use progressive disclosure; Miller's law chunking for the long list; respond within 400 ms; Jakob's law: follow the platform's own conventions; tabular figures for columns of numbers; keyboard navigation is instant; modal backgrounds dim; one focal point | chips and combos, group headings, list, dialogs |
| **Laws of UX** | Fitts: the action sits near the work and the target is large; Hick: minimise choices, and do not simplify to the point of abstraction; Miller: chunk, and do not use seven as an excuse; Jakob: platform conventions; Von Restorff: exactly one emphasis channel and use restraint; Doherty: feedback under 400 ms; Tesler: the tool carries the complexity, so the meter and the notice stay; Peak-End and Serial Position: the export summary is the end and Export sits far right; Choice Overload: comparison is legitimate when it is side by side, and narrowing tools come first; Goal-Gradient: show progress; Paradox of the Active User: guidance is in context, never in a manual | header, status bar, meter, move notice, export dialog |
| **Make Interfaces Feel Better** | One styling system, never a second; concentric radius (outer = inner + gap); shadows for elevation and borders for structure, so dividers and focus stay borders and nothing else gets a shadow; no animation on load; tabular figures for numbers that update; **in a dense desktop interface a hit area is at least 40x40 px**; match the icon stroke to the text weight and never mix icon libraries; one SVG recoloured per state; motion is never the only feedback; follow the review protocol and record rejected candidates | tokens, chips, icons, review (section 8) |
| **Hallmark** | Eight states per interactive element; border width constant across states; focus visible, 2 to 3 px, at least 3:1, instant, never removed; input height equals adjacent button height; a right-edge slot reserved; helper text has a stable height and an error replaces it; empty states name what is empty and offer the action that fixes it, and never offer an action for a gap the user cannot close; honest copy, no invented metric and no fabricated count; token discipline, every colour and family from a named token; the anti-generic gates as the exit check | list states, editor sections, dialogs, empty states, exit check (section 7) |
| **Nothing Design** | Three-layer hierarchy plus a data layer, four levels maximum; labels in caps with 0.06 to 0.1 em tracking at 11 to 12 px; data and numbers always in mono; spacing on an 8 px base with 2 px reserved for optical adjustment; hover brightens border or text, no scale and no shadow; icons monoline at 1.5 px stroke inheriting the text colour; **rows: one 1 px full-width divider, 12 to 16 px vertical padding, no alternating fills, no cell backgrounds**; **tables: label-style header with a bottom border, numbers right and text left, no zebra**; active row is the raised surface plus a 2 px accent indicator; chips are a 1 px border with no fill and a changed border and text when active; a segmented control caps at 4 segments; **the segmented progress bar**: label and value above, square-ended discrete segments with 2 px gaps and no radius, always paired with a numeric readout, compact height; overlays layer by background contrast and borders; `[SAVED]` style inline status text instead of toasts; disabled is opacity or the disabled text token with a stated reason | list rows, table headers, chips, the meter, status text, empty and disabled states |
| **Swiss Design System** | One accent per system; an 8 px base unit; grid and column discipline; the 60-character measure for prose; a weight ladder from 400 to 600 for chrome | tokens, list columns, prose measure |
| **Taste** | Used only for its anti-generic tells and its content rules: no oversized headline type, hierarchy by weight and colour rather than raw scale, one accent, no serif, mixed-family emphasis is amateur, emphasis inside a line uses bold or italic of the same face, no neon or glow, no pure black, one accent used consistently, one radius rule, a button's text must fit on one line, no duplicate action with the same intent, label above field and never a placeholder as a label, the trailing `·` is rationed to one per line, no decorative status dots on every row | type, colour, buttons, the field in the rename dialog |

**An honest note about scope.** Taste states in its own text that it is "not
dashboards, not data tables, not multi-step product UI", Hallmark's macrostructure,
hero, footer and mobile apparatus is page-scoped, and Impeccable's detector says it
checks web interfaces. Those parts are marked not applicable rather than passed.
The load-bearing rules for this application came from Refactoring UI, Nothing
Design, Hallmark's interaction and states file, and Make Interfaces Feel Better.

## 2. Tokens

**Colour.** The Cartridge Workbench table, unchanged, plus the state badge fills
already in `theme.py`. Recorded conflicts in section 6.

**Spacing.** The spec's ramp is 2, 4, 6, 8, 12, 16, 24. This build uses the subset
**2 (optical adjustment only), 4, 8, 12, 16, 24**, which stays inside the spec's own
set and also satisfies the gate that wants every gap on a four-based scale.
Nothing is spaced 6.

**Radius.** One rule, documented: panes and tables square (0), the editor frame and
chips 3, badges 3. Concentric where nested: an inner element's radius is the outer's
minus the gap, which for a 1 px framed pane with a 3 px chip means the chip is 3 and
the frame is 0.

**Two border tokens, not one.** A **control border** (`border`) is 1 px in a colour
that carries 3:1 against the surface, because it is what identifies a control. A
**content divider** (`border`) is 1 px in a lower-contrast treatment and is what
separates rows and sections. The spec supplies one token; this build uses it at
`border` for controls and at the same value for dividers, and records that a
separate divider token is the cleaner end state.

**Type.** A fixed integer ladder, not a ratio, because whole pixels are what survive
100, 125 and 150 percent display scaling. Five steps maximum:

| Role | Size | Weight | Face | Use |
| --- | --- | --- | --- | --- |
| label | 11 | 600 | sans, caps, 0.08 em track | column headers, section labels |
| caption | 12 | 400 | sans | hints, explanations, counters, empty states |
| body | 12 | 400 | sans | chrome, list prose, menus, buttons |
| prose | 13 | 400 | sans | the three editor sections and the retail text |
| data | 12 | 400 | mono, tabular | ids, offsets, sizes, hashes, meter figures, chip internals |

Two weights only, 400 and 600, with 600 reserved for labels and the active tab. No
serif, no italic anywhere, no third face. Mono is a **role** for data, never for
prose, never for a button label, never for column headers.

**States.** Every interactive element ships default, hover, focus-visible, pressed,
disabled and, where it can fail, an error state. Border width is constant across all
of them. Focus is a 2 px ring at 3:1 or better against both the element and the page,
drawn instantly, never animated, never removed.

**Motion.** None. Every entry that discusses motion either bans it for
high-frequency interaction or says to cut it before adding it. Nothing animates on
load, on hover or on focus. The one thing that changes on hover is a border or text
colour.

**Iconography.** Tabler outline only, one library, 1.5 px stroke at the 16 px render
size, recoloured per state from the token table through `theme.icon(name, ink)`.
Where the icon is the state channel it sits beside the state word, never instead of
it.

## 3. The window, surface by surface

### 3.1 Header row

One line, capped at the spec's control height plus padding. Left to right: the
product name, the image name, the detected profile and the project state as
`name value` pairs with the labels dropped where the value is self-describing
(a `buus-fury` chip needs no "format:" in front of it), then the search field
stretched, then nothing else. The project state is static text, never a pulsing dot,
and it carries a word plus a glyph rather than a tint alone.

### 3.2 The list (left pane)

- **Two tabs**, `Dialogue` and `Names & bios`, never merged, with the row counts
  beside them.
- **One control row** for the four filter chips, and **one control row** for the
  shape, order and grouping combos. The speaker control has its own row with its
  caption, because it is the one control whose meaning needs a sentence.
- **Chips**: 1 px border, a changed fill when checked, plus the check glyph and the
  word. The check is what makes the state readable without hue.
- **Rows**: one full-width 1 px divider between rows, no alternating fill, no cell
  background, vertical padding from the metric. The text column elides right; the
  full text is the cell tooltip and the editor shows it in full. This is a local
  decision, recorded in section 5, because no entry covers long prose rows.
- **Columns**: identity (mono) first, then the line, then the speaker, then the
  status last, because the status is the end of the sentence the row tells. Numeric
  columns are right-aligned and tabular. In the line list the identity column is
  hidden, because the spec calls IDs diagnostics and the key is on the status bar.
- **Group headings**: one row, bold label plus the count, on the raised surface,
  spanning the table. More space above a heading than below it, per the spacing
  rules, and the heading is not selectable and not reachable by keyboard. The Place
  grouping orders its headings by the map table's own row order, not by name, and
  ends with the `Unplaced` heading carrying the reason its rows are there.
- **Selected row**: the spec's selection fill across the whole row, plus a 2 px
  focus edge when the table has keyboard focus, plus Nothing's 2 px accent indicator
  at the left edge so the selection survives a colour-vision check.
- **Empty state**: a heading that names what is empty, one line saying why, and the
  single action that fixes it when the user can fix it. A gap in the image gets a
  labelled absence and no button, because a button would be a lie.
- **Keyboard**: arrows move rows, `Home` and `End` the ends, type-ahead does not
  exist because `Ctrl+F` is the search, and the visual order equals the tab order.

### 3.3 The editor (centre)

Three stacked sections, **identical in treatment**, in the order the data flows:
`RETAIL` (the original game), `CURRENT` (this image), `NEW` (this project). Each
keeps the spec's own explanation line so a read-only section is never merely dimmed
and unexplained.

- **Exactly one section is emphasised**, and it is NEW: one accent hairline above its
  frame plus the caret. The type ladder allows two weights, so a weight step is not
  available and the hairline carries the emphasis alone. Von Restorff says use
  restraint, so nothing else in the editor competes.
- The two read-only sections show **no caret**, because a blinking cursor on static
  text is a named tell of a generated interface.
- **The changed run** inside NEW is marked by an underline that is 2 px in the
  accent, plus a section-level word (`changed`) so the mark is never colour alone.
- **The meter**: the spec's two aligned bars, one for characters and one for bytes,
  drawn as Nothing's discrete segments: square-ended blocks with 2 px gaps, no
  radius, no track behind them, with the numeric readout above in tabular mono.
  Three states. Under the limit is neutral. At the limit the number carries the
  accent. Over the limit the overflowing segments change **shape** (they rise 2 px
  and take a cap mark) as well as taking the accent, and the word changes. A limit
  the engine did not state is drawn without a threshold and labelled as unstated
  rather than invented.
- **The move notice**: a persistent inline disclosure, never a toast, never
  dismissible by time, first line naming the fact and second line naming the
  covering records and the site count, with a one-click way to select them. When the
  edit target is unproven the notice says so.

### 3.4 The context pane (right)

Sections separated by 1 px dividers and spacing, never cards, in this order:
speaker and portrait evidence; `Retail says`; the records that contain the line with
each one's own speaker; the site count; the preview; and the address disclosure.

`Retail says` **does not repeat the retail text when the two agree**: it says that
they agree, in one line. It shows the wording only where the image differs, which is
the only case where the reader needs to compare it. This resolves the "same text
repeated inside one container" tell without removing the section.

Addresses, offsets and sizes stay behind one disclosure and are copyable.

### 3.5 The preview

**It must be a real in-game render or it must say it is waiting.** The requirement
is pixel fidelity: the game's own glyphs, the real box art and palette, the real text
origin, line width, wrap and page-break rules, and the portrait as drawn. The build
therefore ships three things and no approximation:

1. **A waiting state**, which is what ships until the data lands: one line reading
   `In-game preview: waiting on extracted game font`, plus what is missing, and no
   drawn box at all. No fake.
2. **A renderer seam** that consumes the RE Lab's data. The contract it expects is
   in section 9. Until every part of it is present the seam reports which part is
   absent and the pane stays in the waiting state.
3. **A validation harness** that renders a set of lines and compares them
   pixel-for-pixel with reference mGBA captures, skipping loudly when either the
   data or the captures are absent. Game art and captures live under ignored
   `build/` paths and are never committed.

### 3.6 The rename dialog

A resizable window, not a wizard. One sentence at the top saying what the rename
does, a concrete `Default for undecided hits` control, then the per-occurrence table
with `Record | Line | Retail says | Decision`, then Cancel and `Apply N decisions` at
the right edge. The table follows the table rules: label-style header with a bottom
border, 1 px row dividers, numbers right, no zebra, the active row raised with a 2 px
accent indicator. The decision cell is one delegate with a combo on activation; Space
cycles it. Escape closes, the backdrop dims, first focus goes to the table rather
than to the close button, and the dialog carries no nested containers.

### 3.7 The export dialog

The end of the task, so it is the one place worth composing carefully. `Export
complete` as the heading, then the facts as `value` with labels only where the value
is ambiguous: the file, the edits applied, the records moved, the output size, and
the SHA-256 in mono with a copy action. Exactly one primary action, at the right
edge. No celebration, no confetti, no toast.

### 3.8 Menus and status bar

A conventional menu bar, because Jakob's law is the strongest argument available for
platform conventions: `File`, `Edit`, `View`, `Help`, with every shortcut written
beside its item. The status bar carries the selected line's identity, the container
offset, the span in bytes, the last export time and hash, and Export at the far
right. Disabled menu items state why in their tooltip.

## 4. What the entries do not cover, decided locally

These are decisions, not citations. Each names the entries that constrain it.

1. **Long prose rows in a list.** No entry gives an eliding policy. Decided: single
   line, elided right, full text on hover and in the editor. Impeccable prefers
   wrapping and a scrolling region; a 3,024 row list of wrapped paragraphs cannot be
   scanned, and Hallmark's "never let a clickable label wrap" points the same way for
   the controls inside the row.
2. **Row height for multi-line prose.** No figure exists. Decided: the spec's row
   height for single-line rows, and variable height only if the reader turns a
   wrapped view on, which this build does not ship (recorded in section 5).
3. **A three-way comparison.** Only Choice Overload endorses side-by-side
   comparison, and nothing describes labelling three versions. Decided: stacked,
   identical treatment, ordered by the data's lineage, exactly one emphasised, and
   the read-only two explain themselves.
4. **Diff presentation.** Nothing in the nine entries mentions a diff. Decided: the
   changed run carries an underline plus a section word, never a colour wash alone,
   which is where Refactoring UI's, Hallmark's and Von Restorff's versions of "never
   colour alone" all land independently.
5. **Keyboard traversal of the list.** Only "instant" and "visual order equals
   keyboard order" exist. Decided as in 3.2.
6. **A speaker column.** Nothing covers an author column. Decided: the RE Lab's
   evidence governs the labels, and the column says `Speaker (by portrait)` because
   the record stores a portrait operand and never a speaker field.
7. **Grouping by map.** The link exists but is partial and one step of it is
   inferred: a map row's placements name descriptors whose payload is an event
   resource, and a record belongs to that map when one of its own handle sites falls
   inside that resource. Measured identically on three images, 486 of 2,805 records
   and 538 of 3,003 lines on the canonical image, 486 and 538 on release 3.1's 2,818
   and 3,024, across 26 groups in map-table order. Decided: group by map where a line
   has a map, put the rest in `Unplaced` with the reason stated, and state the
   coverage in the control rather than implying completeness. Never invent a chapter.

## 5. Considered but rejected

| Rejected | Why |
| --- | --- |
| Nothing's `#000000` OLED base | It collides with the anti-generic gate on pure black, and the spec's neutral ladder is already adopted. |
| Nothing's red, amber and green status palette | The owner cannot read red against green. The segmented shapes and the numeric pairing are kept; the hues are replaced by the state colours, a glyph and a word. |
| Nothing's Space Grotesk, Space Mono and Doto stack | Not on Windows, and the toolbelt rule is to take principles and never the stack. Two faces, both already present, satisfy the four-level hierarchy. |
| Multi-layer web shadows and six-layer button anatomy | Hallmark and Nothing both beat these for a native tool. This build has no custom shadow at all. |
| Taste's "long lists need a different component" | Taste's own scope excludes data tables and dense product UI, and this pane is the product's core. |
| A wrapped-row list view with a toggle | It adds a control to solve a reference gap, and Hick's law argues against it. The editor already shows the full text. |
| Hallmark's 16 px body floor and its bans on `system-ui` and system mono | Every other control in the window uses the Windows system face, Jakob's law favours it, and the toolbelt forbids bundling fonts. Recorded as a deviation against those gates, with the reason, rather than quietly excepted. |
| Skeleton loaders | Nothing argues for bracket status text; the list's shape is known and the load is one file, so a bounded inline status is enough. |
| A caret in the read-only sections | A blinking cursor on static text is a named tell. |
| `Retail says` repeating the whole retail line | It is the same text the centre already shows. |

## 6. Conflicts with the adopted spec, recorded not resolved

| Conflict | Spec says | Entry says | Decision |
| --- | --- | --- | --- |
| The light surface is pure white | `#FFFFFF` in the token table | gate 7 bans pure `#fff` as a base | the spec governs; recorded |
| Neutrals are pure greys | the greys in the table | gate 22 wants at least 0.005 chroma tinting | the spec governs; recorded |
| A selection is a full-width fill | the decisions document | Nothing says no cell backgrounds and prefers a raised row plus an accent indicator | both are used: the spec's fill plus Nothing's accent indicator, so the selection survives a colour-vision check |
| Chips carry a fill when active | the decisions document | Nothing's tags are a border with no fill | the spec governs, because a changed fill plus a glyph is the owner's own colour-blind requirement |
| Body text at 9 to 10 pt | the spec's density band | Hallmark's 14 px floor and 16 px body | the spec governs for chrome and the list; editor prose takes 13 px, one step above the chrome, which is the most the dense band allows |
| Mono in many slots | the spec mandates it for ids, offsets, sizes and hashes | the outlier face is capped at two slots | the spec governs; mono is a data role, not a register, and it never touches prose or labels |
| The status word always shows in full | the spec | narrow panes force eliding | the spec governs: the text column gives ground before the status does |
| A list's row count sits in its tab label | the spec's tab strip | the references put a count beside the tab rather than inside it | both readings are served: the tab names stand alone, each list's total is that tab's tooltip, and the counters line beside the tabs carries the three state counts. Measured, the two labels plus a total on the counters line want 399 px inside the pane's 350 px viewport, so one of the two must elide and the names are the ones a reader navigates by |
| The light theme needs no rule for a control Qt can draw itself | nothing in the spec | the references assume a surface resolves its own colours | the spec governs, and the build now names every control class in the stylesheet anyway, because a rule that does not exist is a rule Qt fills in with ink the theme never chose. See 7.4 |
| NEW is emphasis by one weight step | the design note's 3.3 | the type ladder allows two weights only | the accent hairline carries the emphasis; a third weight would break the ladder. The note's wording is corrected here rather than the build |

## 7. The exit check

The anti-generic gate list is run against the new build as a check, not as a patch
pass. The gates that can fire on a desktop tool are the neutral chroma, the accent
coverage, the spacing scale, the prose measure, the focus, active and disabled
states, icon tells, the family count, the outlier count, italic headings, the input
state set, the contrast thresholds, the invented metric, the re-drawn chrome, the
token discipline, the clickable-label wrap and the sticky-element check. The gates
that are web or marketing shaped are recorded as not applicable with the reason. The
deviations in section 6 are recorded before the check runs, so a failure of one of
those gates is a known deviation rather than a surprise.

`build/ttui-exit-check.py` runs the mechanically checkable half and prints a
finding per gate: token discipline, the spacing scale, the family count, italic,
emoji codepoints, the icon library count, animation, shadows, the border width
set, the single control height, the focus ring, the contrast table for both modes
over every declared pair, and the prose measure. It reports rather than fixes, and
its output is quoted in the ticket report.

### What the first build taught, which is why these gates run

The first build was audited rather than designed, and three defects survived its own
tests until a gate or a measurement caught them. They are recorded here because each
one is now a rule above rather than a thing to remember:

1. **Every icon painted black.** The Tabler sources carry `stroke="currentColor"`,
   which Qt does not resolve, so the icons loaded as near black: the will-move badge
   measured `#000000` on its own ink, about 1.2:1, invisible. The fix was to
   substitute the ink before rendering. This is why the token table owns icons and
   why the exit check renders each one in the ink it will sit on.
2. **A grown line showed a truncated tail.** `pending_text` sliced a grown record to
   its old length, so the editor showed `One` and `\nTw` for an edit the engine then
   wrote correctly. A property test that grows and shrinks a span caught it. This is
   why the pending-text rule is stated in terms of the row that was typed into.
3. **A column of two dozen pixels.** Five columns at the adopted 330 px left pane
   left the text column about 24 px wide, measured with the real font. Counting rules
   in the references did not catch this; measuring did. This is why the pane widths
   are part of the build and why the acceptance pass measures rather than looks.

### What the rebuilt layer taught, found by the audit and the worst-case pass

4. **A control with no rule is a control Qt paints its own way.** The light theme
   rendered the menu bar, the four combo boxes and the address disclosure as white on
   a `#F3F4F6` window, about 1.1 to 1, because the stylesheet named no rule for
   `QMenuBar`, `QComboBox`, `QLineEdit` or a plain `QToolButton`. The dark theme
   painted all four correctly, so every dark pass missed it, and light is the default
   on a light Windows. Rule: the stylesheet names every control class the window uses,
   and a token-free fallback is treated as a defect even when it happens to look
   right in one mode. The mechanical exit check could not see this: it greps source
   for hex literals, and a widget with no rule contains no literal at all. A rendered
   pixel check found it, and the acceptance pass now reads the pixels of each theme.
5. **A floor that is negotiated away is not a floor.** `_fit_columns` asked the
   speaker column for `max(fixed_floor, room - text_floor)`, which keeps the fixed
   floor even when that starves the text: measured, 87 px against a documented 130.
   Rule: the stated priority order is enforced by arithmetic, not by intent, and the
   column that is allowed to give ground is the one that must have no floor.
6. **A style sheet on a frame leaks to its children.** Qt applies a widget stylesheet
   to that widget and every descendant, so the editor's section frames put a border
   round the explanation captions and three nested rules inside the move notice. Rule:
   scope a frame rule by object name, and check the child's own border when a frame
   gains one.
7. **A source-level gate cannot see a paint.** The exit check reported zero findings
   while the light theme was unreadable, because the defect lives in the absence of a
   rule. Rule: an exit check claims only what its method can see, and the audit that
   reads rendered pixels is what covers what the grep cannot.

### What the second audit round taught

8. **A Qt override takes the arguments Qt passes, positionally.** The chip's
   `intrinsicSize` and `drawObject` were declared without the position argument, so the
   character format bound to an integer and both raised inside the override. The visible
   consequence was not a missing chip: the failure happened part way through rebuilding
   the editor's document, so the editor kept the previous row's text while the list had
   moved on, and a commit from that state wrote the wrong text under the wrong key. Rule:
   check a Qt virtual's signature against the binding, and make any rebuild of a widget's
   contents transactional so a failure cannot leave it claiming text it does not hold.
9. **A test that never shows the widget never runs its layout, so it never runs the
   virtuals that layout calls.** The round-trip case passed for as long as the editor
   could not open a line at all. Rule: a case about painting or measuring shows the
   widget and reads the laid-out size, which is what forces those overrides to run.
10. **A base64 data URI in a stylesheet paints nothing, silently.** Qt's parser accepts
    `url(data:image/svg+xml;base64,...)` and then draws no image and logs no warning, so
    the chip's check glyph, which is the channel a colour-blind reader uses, had never
    appeared. Measured on one button: 40 ink pixels for its text alone, 40 with the data
    URI, 100 with the same icon written to a file. Rule: an icon a stylesheet references
    is a file on disk with the ink substituted, and the rule is proved by rendering and
    counting pixels rather than by reading the stylesheet.
11. **A speculative rule is a defect waiting for a zoom.** Styling `QScrollBar` with a
    background, a handle and zero-sized add and sub lines left the sub-page area
    unpainted, which renders as a 1 px checkerboard down a 16 px track. The palette was
    already correct, so the rule was unnecessary and is removed rather than extended.
    Rule: a control that the base style already draws in the theme's colours is left
    alone, and every new rule is looked at on screen, not only in the stylesheet text.
12. **A selection made during construction is a selection nobody hears.** The list
    selects its first row while it is being built, before the window connects to its
    signal, so the editor and the context pane opened empty beside a highlighted row and
    clicking that row did nothing, because a table does not report a current-row change
    for the row already current. Rule: a surface that selects something while building
    replays that selection after the parts are connected.

## 8. Review protocol

Per Make Interfaces Feel Better: walk every state of every interactive element
(default, hover, focus, pressed, disabled, empty, error), review at the three display
scales in both themes, compare against the real captures for the preview, list every
unverified check beside the verdict, and give a verdict of Block, Needs changes or
Approve.

## 9. The preview data contract (what the renderer seam expects)

The RE Lab owns this data and validates it. The seam consumes it from an ignored
path, `build/gamedata/dialogue/`, and the pane stays in its waiting state until every
part below is present and passes the harness.

| Part | Shape |
| --- | --- |
| `palette.json` | the box's and the font's RGB555 palettes, as the game stores them |
| `glyphs.png` or `glyphs.bin` | the font's tiles, at their native bit depth, plus a per-glyph width table |
| `box.png` or `box.bin` | the dialogue box art, nine-slice or whole, with its draw size |
| `metrics.json` | the text origin, the line stride, the box rectangle, the wrap column count, the page stride and the page count |
| `rules.md` | the wrap and page-break rules as the game implements them, with the addresses they were measured at |
| `captures/` | reference mGBA screenshots with the exact line and state each one shows, for the harness |

The renderer takes the line's units, resolves each glyph through the width table, wraps
at the game's column count, breaks pages at the game's rule, blits the box, and draws
the portrait for the resolved operand. Scaling is integer and nearest-neighbour only.
The harness renders each capture's line and compares the images pixel by pixel,
reporting the count and the location of every differing pixel; it skips, loudly, when
either side is absent.
