# Reference-fidelity matrix, DRAGONBYTE-Z-VISUAL-DIRECTION-PASS-001

Companion to [`UI_REFERENCE_MATRIX.md`](UI_REFERENCE_MATRIX.md) (what the real
tools do) and [`UI_FUNCTIONAL_DIFF.md`](UI_FUNCTIONAL_DIFF.md) (what behaviour
changed). This file records, area by area, **what the shipped candidate borrowed,
what it deliberately did differently, and what is missing**.

Verdicts: **BORROWED PATTERN PRESENT** / **JUSTIFIED DEVIATION** /
**MISSING / REGRESSION**. A MISSING on a primary structural row is a block.

Evidence is a real capture in `<temp>\dbz-visual-pass\after`, named per row, taken
from the running PySide6 application against the canonical ROM.

## Reference set

Beyond the eight already studied, this correction named four more real ROM-hacking
editors whose shared model is the target:
**Porymap**, **HexManiacAdvance**, **Lunar Magic**, **FEBuilderGBA**,
**Polished Map++**, **Advance Map**.

The recurring model across all of them, and the one this candidate now follows:

```text
MENU BAR  ->  compact global/editor toolbar  ->  active editor workspace
          ->  editor-local modes / tools
```

Every one of those tools is a *single-window editor with an internal mode strip*,
not a global tab strip listing implementation panels. Lunar Magic has a level
editor and an overworld editor, each with its own internal modes; FEBuilderGBA and
Advance Map open a map editor rather than a "Map Browser" tab; Polished Map++
presents one map editor with its own tools. DragonByte Z previously exposed
`Maps` / `Map` / `Map Browser` as three global destinations and `Build` / `Launch`
as two more, which is the shape this correction removed.

## Matrix

| Area | References | Verdict | The borrowed pattern, and the evidence |
|---|---|---|---|
| **ROM-editor top-bar structure** | Every tool in the set; Godot; GB Studio | **BORROWED PATTERN PRESENT** | Menu bar -> one compact editor strip -> the active workspace. `File / Edit / View / Tools / Help`; one 30px strip carrying the four editors on the left and the project actions on the right; the workspace begins immediately beneath it. No third chrome row. Evidence: `01-shell-no-rom`, `13-atlas-rom-open`. |
| **Primary editor taxonomy** | FEBuilderGBA, Advance Map, Lunar Magic, GB Studio | **BORROWED PATTERN PRESENT** | Only a place where content is *worked on* is a primary destination. Four: **Atlas, Inspector, Maps, Graphics**. Build and Run are project actions; the Scene editor is reached from the placement that owns it. Evidence: `01-shell-no-rom` (strip), `09-maps-objects` (Scene reachable from Objects). |
| **Map workspace consolidation** | Porymap (`mainTabBar`: Map / Events / Header / Connections inside one window), Lunar Magic (one level editor with internal modes) | **BORROWED PATTERN PRESENT** | **One Maps editor** with **Browse / Layout / Objects** modes on its own strip, replacing three global destinations. Porymap's mode-is-a-tab mechanism, one level down. Every previous function is retained: browse any map, edit a dominant layer's chunk cells, inspect and author placements. Evidence: `02-maps-browse`, `03-maps-layout`, `09-maps-objects`. |
| **Global action duplication** | Porymap (menu + one canvas strip, no duplicate), Tiled | **BORROWED PATTERN PRESENT** | No action is both a global button and a workspace. `Edit Layout` appears **once**, on the Maps editor's own strip, and the browser's internal toggle is hidden while the Maps editor owns mode selection; Undo/Redo are Edit-menu actions routed to whichever editor owns a history, not per-panel buttons in a global bar. Evidence: `03-maps-layout` (one Edit-Layout affordance). |
| **Application shell** | GB Studio (menu + one 38px toolbar), Godot (global vs local hierarchy), Porymap (no docks) | **BORROWED PATTERN PRESENT** | GB Studio's in-window menu bar over one persistent action row; Godot's rule that global actions live in the shell and editor-local actions live in the editor. Evidence: `01-shell-no-rom`. |
| **Global navigation / actions** | Godot (run cluster on the right), GB Studio, Porymap | **BORROWED PATTERN PRESENT** | The strip's right side holds exactly the real project actions - Open ROM, Open Project, Validate, Build, Run - and nothing else. Evidence: `01-shell-no-rom`. |
| **Collection navigation** | Porymap (`mapListContainer`: filter above the list), LDtk (bounded scroll region), GB Studio (uppercase single-line panel header) | **BORROWED PATTERN PRESENT** | Filter field over the map collection, header with a live count, eliding rows that scroll rather than widen the pane. Evidence: `02-maps-browse`. |
| **Map canvas** | Porymap (framed canvas, tools at grid row 0), Tiled (canvas is the only undecorated region), LDtk (chrome stays subordinate) | **BORROWED PATTERN PRESENT** | The map keeps the dominant area, is the only undecorated region, and refits on resize while a manual zoom is preserved. Evidence: `02`, `03`, `16-narrow-shell`. |
| **Map toolbar** | Porymap (one line carrying tools, view toggles and a structural action), Aseprite (context bar) | **BORROWED PATTERN PRESENT** | One contextual strip above the canvas; the editor's mode strip above *that* is the only other chrome. View toggles and zoom sit on the canvas strip, not in a second toolbar. Evidence: `03-maps-layout`. |
| **Chunk palette** | Tiled (translucent highlight fill on the active tile), Porymap (live brush preview), LDtk (palette only where usable) | **BORROWED PATTERN PRESENT** | Real chunk artwork adjacent to the canvas; the working chunk marked by a translucent fill **plus** the literal tag `current`; the palette collapses to its header on a map with no editable layer. Evidence: `03-maps-layout`, `08-maps-read-only-map19`. |
| **Contextual inspector** | Porymap (`stackedWidget_MapEvents`: whole pane swaps per mode), Godot (dock header tabs) | **BORROWED PATTERN PRESENT** | One right pane, contents swapped by mode: `Layout │ Browse │ Map`. Never two inspectors, never an empty one. Evidence: `02` vs `03`. |
| **Graphics empty state** | GB Studio (Editor Sidebar appears/disappears by context; inapplicable tools are absent, not greyed), Porymap (`label_NoEvents` named empty state) | **BORROWED PATTERN PRESENT** | With nothing selected the inspector is **one sentence** and nothing else: no empty preview rectangle, no rows reading `-`, no disabled Export button, no empty animation pane. Evidence: `11-graphics-empty`. |
| **Contextual inspector behaviour (Graphics)** | GB Studio (selection determines the sidebar), HexManiacAdvance (related records shown together), Porymap | **BORROWED PATTERN PRESENT** | Selection decides what appears: preview, size, shared state, frames, characters and Export on selection; the animation stepper appears **only** because a character uses the sprite. Evidence: `12-graphics-selected`. |
| **Status / validation** | Tiled (per-editor status-bar re-population; transient left, permanent right), Aseprite (positional bar), Porymap (mode-aware readout) | **BORROWED PATTERN PRESENT** | ONE compact line: the active editor's own status on the left, project state - `validation stale \| build stale \| n unsaved layout edit(s)` - in the permanent zone on the right, each with a glyph as well as a word. No second status row and no blank footer. Evidence: status bar in every capture. |
| **Read-only state** | Porymap (grey the control and tooltip the reason), GB Studio (remove what does not apply), Godot (dim in place) | **BORROWED PATTERN PRESENT** | `READ ONLY · <reason>` in the inspector, the full reason under it, editing controls absent or disabled, no giant badge, no dimming, map fully browsable. Evidence: `08-maps-read-only-map19`, `07-maps-derivative-read-only`. |
| **Edit state** | Porymap (visible mode tab), RPG Maker MZ (the chosen layer's tiles are the editable ones) | **BORROWED PATTERN PRESENT** | The mode is a selected, visible tab; entering Layout draws the chunk grid, auto-selects the first editable layer and forces that layer visible. Evidence: `03-maps-layout`, `04-maps-layout-cell`. |
| **Pending / unsaved state** | Porymap (per-document dirty glyph in the navigator **and** a title prefix), Godot (marker first in the title), Aseprite (tab indicator), GB Studio (stage words) | **BORROWED PATTERN PRESENT** | Three channels: glyph+count in the inspector, glyph on the map's own list row, count in the title and in the status bar's permanent zone. Never colour alone. Evidence: `06-maps-unsaved`. |
| **Advanced technical detail** | HexManiacAdvance (names first, address in the footer), Godot (`Advanced Settings` toggle) | **BORROWED PATTERN PRESENT** | The inspector speaks cells, chunks and layers; the pointer value and the four-byte field offset sit below in readable monospace. **DragonByte Z does not look like a hex editor.** Evidence: `03-maps-layout`. |
| **Narrow-window behaviour** | Porymap (panes shrink; scroll areas take the strain), Tiled (canvas is the elastic element), GB Studio (hard window minimum) | **BORROWED PATTERN PRESENT** with **JUSTIFIED DEVIATION** | Borrowed: panes shrink, the canvas takes the strain, the shell honours the requested size. Deviation: a deliberate **820x560** floor rather than Godot's 1024x600-plus-scale (which has an open complaint for making 1920x1080 tiling impossible) and rather than Tiled's nine-dock Clear View, because this application has no docks to hide. Evidence: `16`, `17`, `18` against the baseline's forced 1249x1628. |
| **Other editor surfaces** | GB Studio (one shared panel-header component), Aseprite (editor-owned context and status bars), HexManiacAdvance (progressive disclosure), LDtk (dense flat panels) | **BORROWED PATTERN PRESENT** | Atlas, Inspector, Graphics and the Scene editor share one header language, one spacing scale, one selection treatment and one status routing. Evidence: `10`, `11`, `12`, `13`. |
| **Build / Run as actions, not workspaces** | FEBuilderGBA and Advance Map (build/run are toolbar or menu actions), GB Studio (Play is a toolbar button, the Build Log is a pane you summon) | **BORROWED PATTERN PRESENT** | Build and Run are strip/menu actions; their report and their configuration live in one surface opened from the action that uses them, so no permanent workspace is kept alive for a panel nobody is reading and no configuration was discarded. Evidence: `14-build-surface`, `15-run-configuration`. |
| **Density** | Aseprite (18px context bar, 12-18px chrome), LDtk (square, no radius on the base button), Tiled (flush panel contents) | **BORROWED PATTERN PRESENT** | 3px radius on inputs, 2px on buttons, square panel regions with 1px separators, one accent spent once per surface, no gradients, no glow, no card containers. Evidence: every capture; the palette in `12-graphics-selected`. |
| **Shell visual coherence** | Tiled (Tiled Fusion: one customised Qt style everywhere), FEBuilderGBA / Advance Map (utilitarian and coherent rather than themed) | **BORROWED PATTERN PRESENT** | One palette resolves every surface: the toolbar and status bar are the darkest layer, panels are the dominant surface, headers and tool strips are raised, the canvas is deepest. No stock light Qt panel remains anywhere, and no dark header is pasted onto a light panel. Evidence: `01`, `11`, `12`, `13`. |
| **Data / content dominance** | Tiled ("the map is the product"), Aseprite (asset-first), RPG Maker MZ (content fills the middle) | **BORROWED PATTERN PRESENT** | Game content is the largest, brightest and least-decorated region on every editor: the map in Maps, the sprite grid in Graphics, the record text in the Inspector. Chrome is recessive and gold is spent once per surface. Evidence: `02`, `12`, `10`. |

## MISSING / REGRESSION

**None.** No primary structural pattern from the reference set is absent, and no
capability was removed (see `UI_FUNCTIONAL_DIFF.md`).

## Deliberately not copied

GB Studio's colours and web-like skin; Porymap's Pokémon content, stock Qt skin and
"nothing collapses" narrow behaviour; Tiled's nine docks and `Tab`-to-clear-view;
LDtk's zen mode, modal definition panels and striped textures; Godot's docking,
editor layouts and feature profiles; Aseprite's retro pixel skin; RPG Maker MZ's
modal properties and absent panel headers; HexManiacAdvance's hex-first default
surface; Lunar Magic's MDI child windows.
