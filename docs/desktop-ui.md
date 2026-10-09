# Desktop UI design and review

This document governs how a DragonByte Z editor surface should look and behave,
and the review a visible change must pass before it closes. It applies to
anything under `tools/webfoot/workbench/` (the beta engineering surface) and to
the application under `tools/dragonbyte/`: the application shell, an editor, a
panel, a toolbar, an inspector, a status line, or a direct-manipulation canvas.

DragonByte Z is a dense desktop game editor, not a website. It is also a thin
client: widgets render structured SDK results and never own ROM semantics
([workbench-architecture.md](workbench-architecture.md)). Thin client does not
mean simplistic UI. Standard desktop-editor conventions are allowed when they
improve a concrete authoring workflow; speculative chrome is not. `app.py:34-35`
records what was deliberately not built: a docking system, editor layout
profiles, or any control the product cannot actually drive.

## Information hierarchy

The order a surface should lead with:

```text
visual game content
-> contextual tools
-> selected-object inspector
-> supporting asset/data browser
-> project/build state
-> optional technical detail
```

Two consequences:

- Show the actual game visuals whenever they are known. A sprite, tile, palette
  or map preview beats a numeric identifier.
- Raw addresses, IDs and provenance are diagnostics. They are one disclosure
  away, copyable when wanted, and never the primary label or an authoring input.
  `inspector.py` is the worked example: content, then editing context, then
  authoring state, then the raw handle and offset rows behind a `Detail`
  disclosure (`inspector.py:7-23`).
- **One surface inverts that rule, deliberately and by name.** The ROM
  destination (`tools/dragonbyte/rompage.py`) has the image itself as its
  subject, so it is address-first: the address gutter leads every row, a range
  row leads with its address rather than a name, and `Go to address` is an
  authoring input. This is the single inversion of the rule above, and it is
  bounded on three sides. It applies only to that destination, because every
  other surface is object-first and reaches the image through `Open bytes` with
  a proven extent. It never becomes a way to edit a semantic object by address:
  a write into bytes a declared structure owns is refused with the owner named.
  And wherever it shows a byte it shows both spellings, the image address and
  the file offset, saying which of the two it read from the input, so the reader
  never has to guess which space a number is in.

## Design language and palette intent

`theme.py` is the single source. `theme.apply_app_theme` is called once, from
`workbench/__main__.py`, and sets both the application `QPalette` and the
application stylesheet. A widget reads a role through `theme.color`,
`theme.qcolor`, `theme.css_rgba` or `theme.mono_font`; it does not carry its own
hex values or per-tab stylesheet.

The palette is derived from the game itself, not from a generic theme and not
from the licence's brand colours. `theme.py:3-15` names the source (the Majin
Buu actor sprite, graphics 903 and 904), `docs/research/UI_BUU_SPRITE_COLOR_SOURCE.md`
records the sampling, and `tools/qa/buu_sprite_palette.py` reproduces it from
ROM data. Three rules follow from that provenance and are worth preserving if
the palette is ever revised:

1. **Light and mid-light, not dark-first.** The sprite's white mantle family
   becomes the work surfaces; the outline becomes the type ramp.
2. **Identity comes from one hue, not from convention.** The interaction family
   is the pink-magenta ramp: active editor, active mode, selection, focus,
   primary action. There is no conventional desktop blue in the file.
3. **Most of the UI is neutral.** A source colour marks a state or an
   interaction; it is never a background wash and never body text.

Named roles, rather than raw values, are what a surface refers to:

- surfaces: `background`, `chrome`, `surface`, `surface_raised`,
  `surface_input`, `canvas`;
- borders: `border`, `border_strong`;
- text: `text_primary`, `text_secondary`, `text_muted`, `text_disabled`;
- state: `success`, `pending`/`warning`, `danger`, `research`, plus the
  interaction ramp.

Geometry and type come from the same module, so one new control cannot invent a
margin:

- spacing scale: `SPACE_XS` 2, `SPACE_SM` 4, `SPACE_MD` 8, `SPACE_LG` 12,
  `SPACE_XL` 16 (`theme.py:270-275`);
- radii: `RADIUS_INPUT` 3, `RADIUS_BUTTON` 2, small on purpose so the chrome
  reads as a desktop tool rather than a web card (`theme.py:277-281`);
- control geometry: `ROW_HEIGHT` 20, `TOOLBAR_HEIGHT` 28,
  `PANEL_HEADER_HEIGHT` 22, `STATUS_HEIGHT` 22 (`theme.py:283-287`);
- fixed-width text for addresses, offsets and raw records: `theme.mono_font`;
- keep three to four active type sizes per surface, and respect the
  operating-system font scale.

**State is never conveyed by colour alone.** Every status role also carries a
glyph and a brightness difference: `theme.status_glyph` returns the glyph and
`theme.STATE_COLORS` resolves the role to a colour, so a caller names a state
rather than mixing a colour (`theme.py:335-379`). This is a hard requirement,
not a preference, because red and green alone are indistinguishable to a
red-green colourblind reader. Specify all five selection states distinctly:
inactive, hover, selected, keyboard-focused, disabled.

## Required design pass before implementation

For each substantial surface, answer these before writing widget code. Skip an
item only when the answer is already fixed by the surrounding editor:

1. the user's primary task;
2. the primary visual object;
3. the selection and context model;
4. the primary actions;
5. the secondary actions;
6. the technical information that should be hidden;
7. the keyboard path;
8. the empty, error and disabled states;
9. the expected data volume;
10. the performance risks.

## Desktop-editor patterns

- **Menu bar.** Global and project commands only: File, Edit, View, Tools,
  Help. Do not put frequent per-object editing here.
- **Toolbar.** Frequent contextual actions: select, paint, erase, place, zoom,
  overlay toggles, and the justified project actions. Do not duplicate every
  menu command.
- **Status bar.** Transient contextual state: cursor coordinates, the selected
  object, zoom, and validation or build state.
- **Content browser.** A tree, list or thumbnail view chosen by data type. A
  large collection uses model/view, not one widget per row.
- **Canvas.** The primary surface for spatial content, with middle-drag pan and
  scroll zoom as expected conveniences.
- **Inspector.** Edits the current selection with progressive disclosure; do not
  make every field permanently visible.
- **Asset palette.** For tiles, sprites, entities and brushes, show the actual
  visual rather than a numeric list.
- **Splitters and docks.** Allowed when they improve a real workflow. Do not
  build docking infrastructure merely because other editors have it.
- **Dialogs.** Reserved for destructive confirmation, complex one-off
  operations, import/export and genuinely modal decisions. Not for routine
  editing.

`widgets.py` holds the shared chrome so a new surface does not re-invent it:
`PanelHeader`, `StateChip`, `DisclosureRow`, `AlignedFieldTable`,
`TechnicalLabel`, `ToolStrip`, `ScrollPane`.

## Qt widget patterns

- **Model/view for large collections.** Use `QListView`, `QTreeView`,
  `QTableView` or a grid with a custom delegate rather than thousands of
  standalone widgets.
- **Canvas.** Choose by measured need: `QGraphicsView`/`QGraphicsScene`, custom
  `QWidget` painting, or a pre-rendered backing image with overlays. The Maps
  editor canvases use `QGraphicsView` (`map_browser_tab.py:1591`, `map_tab.py:365`).
- **Image presentation.** Decode game data outside the widget, through the SDK.
  Convert to `QImage` or `QPixmap` only at the presentation boundary, cache the
  result, and invalidate the cache explicitly. `graphics_tab.py:292` keys its
  pixmap cache by the semantic graphic identity and clears it on an explicit
  invalidation (`graphics_tab.py:714`).
- **Undo.** Use `QUndoStack` / `QUndoCommand`. For a continuous interaction,
  give the command an `id()` and implement `mergeWith()` so a drag or a paint
  stroke collapses into one undo step (`map_browser_tab.py:317-321`,
  `graphics_tab.py:159-177`). Track a clean state to drive Save and the title.
- **Long-running work.** Never block the UI thread for bulk decode, indexing,
  build or expensive rendering. Give feedback within about 400 ms or show a
  progress indicator. The shipping pattern for a large decode is a chained
  `QTimer.singleShot` batch drain, which yields between batches with no thread
  and fills the rest of the view afterwards (`graphics_tab.py:813-856`).
- **Error boundaries.** Translate domain exceptions into a clear on-screen
  message, never a routine traceback dialog. A slot that calls the SDK must
  catch the SDK exception family parent, not one leaf subclass; the per-family
  lists are in [workbench-architecture.md](workbench-architecture.md).
- **State.** Selection, project and authoring state live in the shared
  `Session`. Do not let a widget become a hidden source of truth.

## Direct manipulation

Prefer click-to-select, drag-to-move, paint-to-paint and visible handles over
typing coordinates. The Maps editor canvases already implement the expected
conveniences: a wheel event steps the zoom (`map_browser_tab.py:1662-1667`), a
middle-button press starts a pan and switches the cursor to a closed hand
(`map_browser_tab.py:1669-1689`), and pointer motion over the canvas feeds a live
readout into the status line (`map_browser_tab.py:1690-1695`). A drag target must
be discoverable, and a pointer workflow should have a keyboard alternative where
one is reasonable.

## Keyboard, accessibility and input

- Full keyboard navigation with a visible focus indicator and a sensible tab
  order. `theme.py` names the focus ring a required role; it must never rely on
  colour alone.
- Provide shortcuts for Undo, Redo, Delete, Duplicate, Save/Apply, Build, Run,
  zoom and tool switching where appropriate, and make sure they do not collide.
  The shell defines `Ctrl+O`, `Ctrl+Shift+O`, `Ctrl+Shift+V`, `Ctrl+B`, `Ctrl+R`,
  the platform standard Undo/Redo/Quit, and `Ctrl+1` to `Ctrl+4` for the four
  primary editors (`app.py:281-327`, `389`).
- Never require hover to reveal critical information. Icon-only controls are
  acceptable only where the convention is strong, and an unfamiliar icon needs a
  tooltip.
- A disabled action should say why where that is useful.
- Contrast targets, following WCAG 2.2: at least 4.5:1 for text, at least 3:1
  for large text and UI components. Check at a large operating-system font size
  and under a colour-vision-deficiency simulation.

## Performance

Never:

- decode ROM assets inside `paintEvent`;
- decode thousands of thumbnails synchronously at startup;
- create one heavyweight widget per tile;
- repaint a whole map for a small overlay change.

Prefer:

- lazy thumbnail generation;
- caches keyed by semantic asset identity, invalidated explicitly. The Maps
  editor keeps a bounded render cache and evicts the oldest entry rather than
  growing without limit (`map_browser_tab.py:141`, `1746`, `2984-3008`);
- background decoding for expensive work;
- lightweight visual items and pre-rendered static layers where appropriate;
- narrow dirty-region updates;
- command merging during a drag or paint;
- benchmarks over representative real data: large maps, thousands of assets,
  rapid scrolling, zoom, drag and overlay toggles. Do not optimise from theory.

## The visual and interaction review

**Hard rule: source inspection and passing tests are not evidence that the UI
looks correct.** A screenshot path alone is not evidence either; the reviewer
must open the image and look at it. Interaction is reviewed the same way: by
running the application, not by reading the diff.

### Required workflow

1. Launch the real application (`python -m tools.webfoot.workbench`).
2. Navigate the actual changed workflow.
3. Populate it with representative real data.
4. Capture screenshot evidence from the running application, with full-window
   context where useful and a detail capture only when needed.
5. Open the screenshots and inspect them.
6. Record defects.
7. Fix and repeat.
8. Capture the final evidence.

For major work, the minimum evidence set is: the normal working state, an active
selection or editing state, one edge or error or empty state, and the final
corrected state.

### States to inspect

Where applicable: normal, empty, loading, selected, hover and focus, disabled,
validation error, runtime/domain error, resized narrow, resized wide.

### Visual checklist

**Primary task**

- the primary task is obvious within a few seconds;
- the visual focal point is appropriate.

**Layout**

- consistent margins; controls aligned;
- no accidental dead space and no cramped region;
- splitters behave correctly.

**Typography**

- readable; hierarchy clear;
- technical text distinguished;
- no unnecessary font-size variation.

**Controls**

- primary actions visually clear;
- destructive actions differentiated;
- disabled state legible;
- every unfamiliar icon has a tooltip.

**Content**

- visual assets shown where available;
- raw identifiers secondary;
- the selection and the current context obvious.

**Scrolling and resize**

- no accidental horizontal scrollbar;
- resize does not destroy the layout;
- the minimum size is usable and a large window uses its space intelligently.

**Error and empty states**

- actionable, with no traceback and no unexplained blank pane.

**Consistency**

- matches the existing DragonByte Z visual language;
- no one-off padding, colour or control size;
- state conveyed by brightness and glyph, never by colour alone.

### Interaction checklist

Drive each of these in the running application, and cover the deterministic ones
with a GUI module test as well:

- click, and double-click where applicable;
- keyboard selection, Tab and Shift+Tab;
- shortcut activation;
- focus persistence and selection persistence;
- drag start, move and drop;
- Undo and Redo;
- Apply and Revert;
- invalid input;
- state invalidation (a change elsewhere must not leave a stale panel);
- switching map or asset while an edit is staged;
- closing and reloading.

Do not report a visible change as passing until both the visual and the
interaction review have passed.
