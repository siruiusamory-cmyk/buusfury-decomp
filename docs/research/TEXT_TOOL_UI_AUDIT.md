# The text tool's UI/UX audit

Date: 2026-10-10. Scope: `tools/buufury_text/`, the Buu's Fury text editor's window.

The owner's rule (`ui-ux-toolbelt`) is that every UI deliverable lists the
reference entries it applied and the rules taken from them, the entries rejected as
a poor fit, and confirmation that nothing private went to a hosted service. This
document is that record, and it carries the measurements the audit ran.

The project's own spec wins wherever it conflicts with a generic rule. Every
conflict found is named in "Conflicts" below rather than silently resolved.

## Entries read

Read directly, in this session, from the pages named. Where a repository landing
page returned only navigation chrome, the file inside it is named instead.

| Entry | Read from | Rules taken |
| --- | --- | --- |
| Refactoring UI skill | `raw.githubusercontent.com/s0xDk/refactoring-ui-skill/main/SKILL.md` | design from a scale, never ad hoc; two weights are enough; three text colours maximum, all at 4.5:1; never colour as the only signal; labels are a last resort; more space around a group than within it; dense UIs are legitimate by decision |
| Impeccable | `impeccable.style/` (landing page only; `/docs`, `/slop` and `/designing` were not read, and no rule is attributed to them) | polish within the existing design system; the system is the project's own theme, not a second one |
| Hallmark | `skills/hallmark/SKILL.md`, `references/interaction-and-states.md`, `references/copy.md`, `references/motion.md`, `references/layout-and-space.md`, `references/slop-test.md` | eight states per interactive element; border width constant across states; focus must be instant; input height equals button height; empty states name what is empty and why; honest copy labels a missing value rather than inventing one; cut motion before adding it; no motion on high-frequency interaction |
| Make Interfaces Feel Better | `skills/make-interfaces-feel-better/SKILL.md`, `animations.md`, `surfaces.md` | tabular figures for numbers that update; at least 40x40 logical px in dense desktop UI; one icon recoloured per state, never a second asset; borders for dividers, cells and input outlines; no custom animation on high-frequency interaction |
| UserInterface.wiki | `skills/SKILL.md`, `skills/AGENTS.md`, `skills/rules/type-tabular-nums-for-data.md`, `skills/rules/ux-jakobs-familiar-patterns.md` | progressive disclosure: critical features prominent, the rest behind a menu; minimise choices; chunk data for scanning; targets at least 32 px; instant keyboard navigation; tabular figures for columns of numbers; familiar patterns |
| Laws of UX | `lawsofux.com/`, `hicks-law/`, `choice-overload/` | decision time grows with the number of choices; narrow choices with search and filtering up front; do not simplify to the point of abstraction |

Two pages were unreachable and no rule is attributed to them:
`userinterface.wiki/rules/ux-progressive-disclosure` returns 404, so the
progressive-disclosure rule above is cited from `skills/AGENTS.md` section 9.8.

## Applied

1. **A real empty state for the left list** (Hallmark `copy.md`: three beats, and
   "never show a generic No results with no context"). A term that matches nothing,
   a chip set that excludes everything, and the wrong tab each name what is empty
   and offer the one action that fixes it, because the user can fix those.
2. **The missing-data story is labelled where the value would be** (Hallmark
   `SKILL.md` discipline 2: "if the user did not supply a metric, do not invent
   one"). The speaker control leads with the count of unattributed lines, the
   context pane states the share as a fact, and the place grouping names why every
   line is unplaced. No button is offered for a gap the user cannot close.
3. **Tabular figures are declared, not inherited** (Make Interfaces Feel Better
   section 9; UserInterface.wiki `type-tabular-nums-for-data`), in
   `theme.mono_font()`.
4. **The focus ring is drawn, never removed** (Hallmark
   `interaction-and-states.md`), as a 2 px ring in the proxy style.
5. **One base height for inputs and adjacent buttons** (Hallmark, same file), the
   proxy style's `sizeFromContents` floors every field and button at one value.
6. **Borders do the work dividers need in a dense UI** (Make Interfaces Feel
   Better `surfaces.md`), through the 1 px rules and hairlines.
7. **No animation anywhere** (Hallmark `references/motion.md`: "cut motion before
   adding it"; Make Interfaces Feel Better section 19: no custom animation on
   high-frequency interaction). The absence is the finding: nothing was added.
8. **Token discipline** (Hallmark `slop-test.md` gate 48). The preview module's
   four colours were literals; they are now four mode-invariant tokens in the one
   token table, so the count of colour literals outside `theme.TOKENS` is zero.
9. **The icon ink is correct** (gates 30 and 41). See "A defect the gates caught".
10. **The prose measure was measured, not assumed** (gate 25). See "Conflicts".
11. **The label vocabulary is honest** (gate 46). Where the data does not
    attribute a face, the surface says which gap it is.

## Already satisfied, with the evidence

- State is never carried by hue: `status.py` gives every state an icon, a glyph,
  the full word and a marker shape, and a test asserts all four are distinct.
- The focus ring is a drawn ring and is never suppressed (`theme.EditorProxyStyle`).
- The disabled path explains itself: the export button's tooltip carries the
  engine's own refusal reason.
- The right pane discloses raw addresses behind a button rather than leading with
  them.
- Row height, column widths and the elide priority are the adopted spec's numbers,
  derived from the font, and a test asserts the elide mode.

## Rejected

| Entry and rule | Why it does not apply here |
| --- | --- |
| Hallmark's motion prescription, in full | The application animates nothing and should not. Every rule in that file is about how to animate; the correct reading for a dense data tool is to take none of it. |
| Make Interfaces Feel Better's 44x44 touch target; UserInterface.wiki's 32 px minimum | The contract's own chip geometry is 24 to 26 px and the adopted spec wins. A mouse-and-keyboard desktop tool at a 260 px pane floor cannot carry touch targets. |
| Hallmark gate 34 and gates 50 to 57 (horizontal scroll, image grid tracks, sticky offsets, all-caps line height) | They are CSS and browser-viewport gates with no Qt Widgets equivalent. The principle behind them is kept: the window is checked at its minimum size instead. |
| Gate 8 and gates 20 and 21 (macrostructure stamps, the art-directed hero rotation) | They govern a marketing page's structure. This is a three-pane data editor whose layout the owner adopted deliberately from the artefact-tooling precedent. |
| Gate 47 (re-drawn UI chrome) | The dialogue preview draws a game box, which is the artefact under edit rather than chrome the user already has, and the adopted spec allows exactly one such surface. |
| Impeccable's own rule set | Only its landing page was reachable; it states no rules there, so nothing is claimed from it. |

## A defect the gates caught

Gate 41 asks whether an icon is legible against what it sits on. Measured, before
the fix, every state icon painted essentially BLACK on both themes, because the
bundled Tabler SVGs carry `stroke="currentColor"` and Qt's SVG renderer does not
resolve it:

    dark  minus           24 px painted, dominant #0a0b0c
    dark  pencil          82 px painted, dominant #020203
    dark  arrow-up-right  44 px painted, dominant #000000

On the dark surface that is about 1.2:1, invisible. The icons are now rendered
with the stroke substituted and at both pixel sizes, and are measured again on
their own badge fill:

    dark  arrow-up-right  44 px, dominant #201b12  (the will-move ink)
    dark  refresh         88 px, dominant #e2ddff  (the base-changed ink)
    light refresh         88 px, dominant #4b4098  (the base-changed ink)

## Measured contrast

Every pair the application actually renders, computed with the WCAG 2.1 relative
luminance formula. Text needs 4.5:1; icons, markers and focus rings need 3:1.

| Pair | Light | Dark |
| --- | ---: | ---: |
| body text on the editor surface | 15.59:1 | 14.24:1 |
| body text on the window | 14.16:1 | 15.52:1 |
| body text on a raised panel | 14.80:1 | 12.86:1 |
| secondary text on the surface | 5.82:1 | 7.88:1 |
| secondary text on a raised panel | 5.52:1 | 7.12:1 |
| selected row text on the selection fill | 12.55:1 | 10.02:1 |
| accent as text on the surface | 6.33:1 | 7.32:1 |
| export button ink on the accent fill | 6.33:1 | 7.32:1 |
| focus ring on the window | 4.21:1 | 8.78:1 |
| the splitter rule on the window | 3.64:1 | 3.93:1 |
| badge ink on its own fill, worst of five states | 4.59:1 | 5.71:1 |
| state marker on the row surface, worst of five | 4.83:1 | 5.71:1 |

No pair fails its threshold, in either mode, for any of the five states. The
badge FILL against the row surface is deliberately low (1.11:1 to 1.74:1): the
fill is not what conveys the state, so the 3:1 non-text floor does not apply to
it, and the glyph, word and marker carry the state instead.

## Conflicts with the adopted Cartridge Workbench spec

Each of these is a gate the application does not pass, where the project's spec
wins. They are recorded rather than resolved in the code.

1. **Gate 1, the system font.** The gate fails a page whose display font is a
   system default. The adopted spec mandates the Windows system family, and the
   owner's own rule is "dense native Windows, not web". The spec wins.
2. **Gate 7, pure white.** The light theme's `surface` is `#FFFFFF`, exactly as the
   spec's token table sets it. The dark theme's surface is not pure black.
3. **Gate 22, zero-chroma neutrals.** The spec's neutrals are untinted greys.
   Tinting them is a change to the adopted palette, not to this ticket.
4. **Gate 24, the spacing scale.** The spec's ramp is 2, 4, 6, 8, 12, 16, and the
   gate wants multiples of four only. The spec wins; 6 is in its ramp.
5. **Gate 25, the prose measure, and this one is a real decision.** Measured with
   the real platform font (Segoe UI 9 pt; 10 pt prose averages 5.86 px per glyph),
   the centre pane at the default 1440 px window holds about **128 characters per
   line**, against the gate's 45 to 75 range. Bringing it into range would cap the
   prose at about 440 px, which is NARROWER than the "generic 80-column
   programming width" the adopted spec explicitly rejects. The spec wins, so the
   editor still wraps to its viewport, and the measurement is recorded here because
   only the owner can choose between the two.

## Nothing private left this machine

Every rule above came from a public page or a file on this disk. No screenshot, no
game text, no ROM byte, no save and no project content was sent to any hosted
service. No plugin, package or MCP server was installed. The one program installed
in this ticket's service was Color Oracle, which the owner asked for, and it runs
locally.
