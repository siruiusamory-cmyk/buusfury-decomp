# DragonByte Z visual direction: the real-application reference matrix

This is the research artifact for the DragonByte Z visual direction pass. It is
not production code and changes no behaviour.

It exists because the previous generated-reference approach was rejected: a
machine-generated mockup introduced generic interface patterns and invented visual
and content conventions. This pass therefore uses **real, shipped desktop and
game-development tools** as the reference set, and every DragonByte Z decision
below names the actual borrowed pattern rather than "inspiration".

**No generated image, mockup, style board or screenshot is used here, and none
was produced.** The tools studied were read from their own documentation, their
own shipped UI source (Qt `.ui` files, C++ widget construction, SCSS themes, XAML,
bitmap theme manifests) and their own published screenshots.

## Tools studied (8)

| # | Tool | Role in this pass |
|---|---|---|
| 1 | **GB Studio 4.x** (Project Editor) | primary: approachable hierarchy, project/navigation pane, inspector that selection changes |
| 2 | **Porymap** (huderlem, through 6.3.1) | primary: map-first editing geometry, the strongest direct reference |
| 3 | **Tiled 1.12** | primary: canvas dominance, palettes subordinate to the map |
| 4 | **LDtk** (Deepnight) | primary: compact side panel, context-sensitive palette, modern desktop personality |
| 5 | **Godot 4.x** editor shell | secondary: global-versus-local action hierarchy |
| 6 | **Aseprite 1.3** | secondary: compact density, context bar, split status bar |
| 7 | **RPG Maker MZ** (map editor) | secondary: first-time legibility sanity check |
| 8 | **HexManiacAdvance** | depth only: naming machinery for deep ROM detail |

Primary evidence, by tool:

- **Porymap**, `forms/mainwindow.ui` (0 `QToolBar`, 0 `QDockWidget`; `gridLayout_4`
  puts the tool strip at row 0 and the canvas at row 1), `src/mainwindow.cpp`
  (tab-to-`EditMode` maps at 2232–2298, the `stackedWidget_MapEvents` inspector
  swap, layout-only `setTabEnabled` + explanatory tooltip at 1212–1231),
  `src/editor.cpp` (status-bar format strings at 1246–1286), and the official
  manual's shortcuts and navigation pages.
- **Tiled**, `src/tiled/mapeditor.cpp` (`resetLayout()` dock geometry at
  550–593; `statusBarWidgets` / `permanentStatusBarWidgets` at 491–504),
  `src/tiled/mainwindow.cpp` (per-editor status-bar re-population at 2561–2595;
  Clear View at 1791–1825), `src/tiled/tilesetview.cpp` (`TileDelegate::paint`
  selection fill at 168–194), and the 1.12 manual.
- **GB Studio**, `src/components/app/AppToolbar.tsx` (38 px global toolbar,
  workspace dropdown, save-stage title composition), `src/components/ui/*/style.ts`
  (panel-header and list-row geometry), `src/consts.ts` (`NAVIGATOR_MIN_WIDTH`),
  `src/components/world/WorldPage.tsx` (pane-width collapse rules), and the
  project-editor / navigator documentation.
- **LDtk**, `app/assets/css/app.scss` (300 px panel, layer-list height clamp,
  radii, the single gradient), `app/assets/tpl/pages/editor.html` (panel order),
  `src/electron.renderer/page/Editor.hx` (`updateGuide()` per layer type,
  `updateTitle()`), `src/electron.renderer/ui/ToolPalette.hx` (per-layer-type
  palette subclasses).
- **Godot**, `editor/editor_node.cpp` (title-bar layout, `(*)` dirty prefix),
  `editor/gui/editor_bottom_panel.cpp`, `editor/themes/editor_theme_manager.cpp`
  (read-only de-emphasis, corner-radius token), `editor_settings.cpp`
  (spacing/corner-radius/accent tokens), and the editor documentation.
- **Aseprite**, `data/extensions/aseprite-theme/theme.xml` (chrome dimensions),
  the Context Bar, Timeline and Status Bar documentation pages.
- **RPG Maker MZ**, the official MZ help pages (`01_03`, `01_07_01`, `01_07_02`,
  `01_07_03`, `01_04`) for window regions, the layer-highlight rule, the modal
  map-properties path and the toolbar; plus one independent beginner review for
  the legibility finding.
- **HexManiacAdvance**, the project wiki (Understanding the User Interface,
  Glossary, Formats, Pointers and Anchors), `src/HexManiac.WPF/Controls/TabView.xaml`
  (field-row anatomy, bottom bar), `Windows/MainWindow.xaml` (menu, minimum size).

## Verified findings that changed a decision

These are the reference facts that directly determined a DragonByte Z choice.

1. **Porymap has no toolbars and no docks at all**, its whole window is
   splitters and frames, and its "tool contexts" are a *tab bar that sets an
   `EditMode` enum*, with a per-mode *stacked inspector swap* in one pane.
2. **Tiled's palette selection is a 50 %-opacity highlight fill, not a marquee.**
   The common assumption (a marquee rectangle) is factually wrong for Tiled and
   was rejected.
3. **Tiled re-populates the status bar per editor**, and puts the active-layer
   combo and zoom combo in the status bar's *permanent* zone.
4. **Porymap's status bar is a transient, mode-aware instrument readout** -
   `X: %1, Y: %2, Metatile: … , Scale = %4x`, not a fixed coordinate ticker.
5. **GB Studio has no canvas-local toolbar**: its tools float over the canvas at
   (10, 10); Godot has a strong canvas-local toolbar and a *separate* centred
   workspace switcher. Both separate global from local actions; they do it
   differently, and DragonByte Z follows Godot because it has a real document tab
   strip where GB Studio does not.
6. **Godot's read-only treatment is "dim in place, never reflow"**, and its
   unsaved marker is a literal `(*)` placed *first* in the title so the OS task
   bar shows it.
7. **LDtk's palette is regenerated per active layer type**, and its `#guide` hint
   strip rewrites its key chips per layer type.
8. **HexManiacAdvance's default surface IS a hex editor** by the author's own
   words, and its named editors are the accommodation. This is the *opposite* of
   what DragonByte Z must do, so only its naming machinery is borrowed.
9. **RPG Maker MZ's properties are a modal**, and its independent beginner review
   calls the interface "a familiar if confusing mess". Its one strong borrowable
   idea is layer selection that highlights exactly the tiles that layer owns.
10. **Aseprite's Context Bar is an 18 px strip above the canvas whose entire
    control set is swapped per tool**, and its modified state is a 5×5 px icon on
    the document tab, with `[Read-Only]` in the title.

## The matrix

Rows are the surfaces and states DragonByte Z actually has. Every cell names the
real mechanism in that tool. The final column is the decision, with the borrowed
pattern named.

| | GB Studio | Porymap | Tiled | LDtk | Godot | Aseprite | RPG Maker MZ | HexManiacAdvance | **DragonByte Z decision** |
|---|---|---|---|---|---|---|---|---|---|
| **Application shell** | In-window menu bar (Win/Linux) + one persistent 38 px global toolbar | Menu bar only; no toolbar, no docks; splitter panes with 1 px raised frames | Menu bar + three top toolbars + nine docks | **No menu bar at all** (`removeMenu()`); top button bar lives inside the left panel | Menu bar left, workspace buttons centred, run cluster right, all in one title-bar row | Menu bar + dockable bars; layout switch top-right | Menu bar + one flat icon toolbar (≈22 buttons, ~89 px) | Menu bar with full gesture text; one row-width strip | **Menu bar + one global toolbar**, Godot hierarchy: project identity on the left, global actions on the right. No docks, no configurable IDE. |
| **Global navigation** | One dropdown button in the toolbar, label = current workspace | `mainTabBar` (Map/Events/Header/Connections/Wild Pokémon), a tab strip, not a dropdown | Document tabs above the canvas; docks carry their own titles | Icon-button bar inside the left panel | Five centred icon+label workspace buttons | Document tabs; layout dropdown | Toolbar mode button (Map/Event) | Tabs, one per open file | **Document tab strip** (the existing eight tabs), restyled as a desktop tab bar. Kept: eight tabs, order, enable contract. |
| **Collection navigation** | Navigator pane with uppercase collapsible section headers; search field per section | `mapListContainer` tab widget: Groups/Locations/Layouts, filter field, per-tab toolbar | Project dock; layers/objects tabified on the right | `ul#layers` fixed-height scroll region, min 100 px / max 250 px | Scene + FileSystem docks, filter always visible | Timeline is the resource panel, hidden by default | Map tree, drag-to-group (**display-only**) | Table selector: section ▸ table ▸ element dropdowns | **Left pane: a search field + a map list**, with the count shown. Porymap's filter-then-list geometry, not a tree. |
| **Central workspace** | Canvas with floating tool panel at (10,10); no local toolbar | Canvas framed by a 1 px raised `QFrame`; tool strip at grid row 0, canvas at row 1 | Canvas is the central widget, **edge to edge, no frame** | Canvas with a floating `#editingOptions` strip glued to the panel edge | Viewport with a context toolbar directly beneath the tab strip | Canvas with the Context Bar directly above it | Map view fills the middle zone | `HexContent` byte grid | **Canvas dominates and is the only undecorated region** (Tiled). One contextual strip directly above it (Porymap grid row 0). |
| **Contextual inspector** | Right sidebar, selection-driven, sections appear and disappear | One right pane that **swaps whole contents per mode** (`stackedWidget_MapEvents`) | Properties dock left; layer/object docks right | Modal definition panels + inline options rows | Right dock, `Inspector │ Node │ History` tabs in the header | Context Bar, not an inspector | **Modal** map properties from the map list | Side-by-side grouped field columns | **One right pane, tabbed** (`Layout editor │ Chunk │ Map`), mode-driven. Never modal. Inspector stays subordinate to the map. |
| **Editing toolbar** | Floating icon panel over the canvas; inapplicable tools are **absent, not greyed** | Six `QToolButton`s + `Smart Paths`/`Grid`/`Border` checkboxes + a structural button on **one line above the canvas** | Tools toolbar + a per-tool **tool-specific toolbar** | Tools are inline panel options rows | Canvas-local toolbar that **changes with selection** | Context Bar fully swapped per tool | One flat icon row; active mode drawn pressed | No icon toolbar; the tool rail is text-rotated | **One contextual strip above the canvas**, contents swapped between Browse and Edit Layout. Inapplicable controls are removed, not greyed (GB Studio). |
| **Asset/chunk palette** | Tile palette is a pane in the right sidebar, zoom levels user-set, default 200 % | Palette pane adjacent to the canvas with a **live "Selection" preview group box** | Tileset dock: filter → tabs → grid → action toolbar; selection by **50 % highlight fill** | Palette rebuilt per active layer type; pops out when it needs room | TileSet panel is a bottom panel with three columns | Left column swaps palette ↔ tileset in one widget | Tile palette with A–E tabs at its bottom edge | Image tool shows sprite + palette + addresses together | **Chunk palette adjacent to the canvas, in the right pane's Chunk tab**, showing the real chunk art as thumbnails with the selected one marked by a translucent fill plus a tag (Tiled + Porymap's live preview). |
| **Read-only state** | Remove the control, or opacity 0.3/0.5, or collapse to a header | **Grey the control and attach a tooltip naming the reason**; whole regions disabled as a unit | Layer lock glyph; disabled actions; greyed read-only property rows | `opacity: 0.4` row + italic red name; unsupported toggles striped + `not-allowed` | Read-only dims in place (25 % toward black/white, 0.65 alpha); unlock on the property | Title text `[Read-Only]` | Not applicable in the same form | Plain text in the tool panel | **Compact `⊘ READ ONLY · <reason>` strip in the inspector + editing controls absent/disabled + the reason named.** No giant badge, no dimming, map stays fully browsable. |
| **Pending/unsaved state** | Parenthesised **stage words** in the title: `(Modified)` / `(Saving…)` / `(Writing Files n/m)` | `* ` prefix in the title **plus per-map status glyphs in the map list** | `[*]` title placeholder + `isModified()` | `filename [UNSAVED]  @ Level` in the title | `(*)` **first** in the title so the task bar shows it; per-tab tooltip with last-saved age | 5×5 px icon on the document tab; title carries no marker | Not applicable | Footer `Address`/`Length` always visible | **Three channels**: a glyph+text change-count in the inspector, a per-map `●` glyph in the map list, and a glyph in the status bar. Never colour alone. |
| **Save / build** | Play button doubles as build progress; Save / Save As in File | `Ctrl+S` save current map, `Ctrl+Shift+S` save all; edit-history window | `Ctrl+S` / `Ctrl+Shift+S`; safe-write preference | `Ctrl+W` close project; settings panel | Save-before-run dialog; run cluster top-right | `Ctrl+S` | Playtest button in the toolbar | Menu with gestures | **Global toolbar right side**: Open ROM · Open Project · Validate · Build · Run, and Save As ROM… in the Map Browser's Edit Layout context (where it is real). Nothing invented. |
| **Validation/status** | Bottom Build Log pane, always opened on build **errors**; scoped floating 19 px status pill on the canvas | Status bar: mode-aware hover instrument + auto-clearing log messages | Status bar: transient tool text + **permanent layer combo and zoom combo** | `#mouseCoords` overlay bottom-right; `#miniNotif` bottom-left; `#guide` hint strip | Bottom `Output` panel with severity colours; script-local error/warning counts | Status bar shows cursor x/y, canvas size, frame, zoom | Status bar: chosen function, map name, coordinates | Footer bar: free space, address, length, element path, selected bytes | **One bottom status bar** carrying the map identity, geometry, a live hover readout (`X, Y · cell · chunk`), the edit state, and the unsaved count. Transient messages reuse the same bar. |
| **Advanced technical detail** | Raw GBVM view as an `Editor │ GBVM` segment **in the same pane header** | Addresses only in the log; no raw view in the editor | Read-only property rows | Not the idiom | `Advanced Settings` toggle in the same window | Not the idiom | **Never exposes offsets or pointers at all** | Row headers become **names**; the address stays in the footer; per-field jump arrows | **Raw field offset and pointer move behind a `Detail ▸` disclosure in the Layout editor tab** (Godot's advanced toggle). The default inspector speaks cells and chunks. |
| **Narrow-window behavior** | Hard 900×600 floor, then navigator auto-collapses below 100 px; overflow split **half to each side pane** | Nothing collapses; splitters only | `Tab` = Clear View (hides all docks/toolbars); Views menu toggles; layout lock/reset | `TAB` = zen mode: hides the whole panel, leaves a 16 px revealer strip | Hard 1024×600 × display-scale floor; distraction-free mode hides docks | `Tab` hides the timeline; elements can be undocked | Not documented | `MinWidth 400`, `MinHeight 300`; the grid scrolls horizontally | **The window can actually get narrow** (the current 1090×1246 floor is a defect). Side panes have real minimums, the canvas is allowed to shrink first, and the whole shell scrolls rather than clipping. |
| **Density** | Toolbar 38 px; panel headers 30 px uppercase 11 px bold; radius 4; base font 11 px | Stock Qt: 1 px raised frames, titled group boxes, ~11 px text | Tiled Fusion; zero margins in the tileset dock; icon-only toolbars | Panel 300 px; body 11 pt; buttons square with **no radius**; exactly **one** gradient in 10 819 lines | `base_spacing 4`, `corner_radius 3`, `border_size 0`, one accent, presets Compact/Default/Spacious | Chrome 12–18 px; 9-slice hard 1 px bevels; no gradients | ~22 controls in an 89 px strip; rows ~18 px | Field rows 18 px; anchor bar 19 px; gutter 70 px; jump buttons 22×18 | **Compact desktop density**: 3 px radius maximum on inputs, 2 px on buttons, **square panel regions** with 1 px separators, one accent (gold) spent once per surface, no gradients, no glow, no cards. |

## Constraints against generic generated interface patterns, and how the references justify them

The generated references were rejected for generic interface patterns. Each
banned pattern is rejected against a real reference, not against taste:

| Banned pattern | Reference that rejects it |
|---|---|
| marketing feature cards inside the editor | No studied editor uses a card container in its chrome. LDtk's entire stylesheet has no card idiom; Tiled's tileset dock sets `setContentsMargins(0,0,0,0)` and `setSpacing(0)`. |
| giant product logos / hero panels | No studied editor has one. Godot's largest non-editor chrome element is a 24 px bottom bar with a deliberately faded version label (alpha 0.65). |
| every section in its own rounded rectangle | Godot ships `corner_radius` 0–6 with 3 as default and **square** tab-joined panels (`content_panel_style` zeroes the top corners). |
| excessive corner radii | Aseprite's whole skin is hard 1 px bevels; LDtk's base button has **no** `border-radius`. |
| excessive padding | Tiled's tileset dock is flush; LDtk's panel is a 300 px fixed column with 4–10 px padding. |
| gradients / glow / glassmorphism | LDtk contains exactly one gradient in 10 819 lines and it is a functional scroll fade. |
| fake dashboard home page | Porymap's canvas is a live document from launch; MZ's documented beginner complaint is precisely not knowing what to do. |
| badge spam / multiple competing accents | Godot derives its entire palette from two greys and **one** accent; GB Studio has one `highlight` token used in both themes. |
| invented map names or game content | DragonByte Z's names come from the ROM's own `+0x0C` text relationship; the captures use real maps (`map:0040 East District 439`, `map:0019`). |
| decorative "workflow principles" in the app | No studied editor carries prose about itself in its editing surface. |

## Reference-fidelity targets

Each area is assessed against its assigned references and marked
**BORROWED PATTERN PRESENT**, **JUSTIFIED DEVIATION** or
**MISSING / REGRESSION**.

| Area | Assigned references |
|---|---|
| App shell | GB Studio + Godot |
| Map workspace | Porymap + Tiled + LDtk |
| Density | Aseprite + LDtk |
| First-time legibility | GB Studio + RPG Maker MZ |
| Technical depth | HexManiacAdvance |

## What was deliberately *not* copied

- GB Studio's colour scheme, its lighter web-like skin, its floating canvas tool
  overlay (DragonByte Z has a real document tab strip, so Godot's hierarchy fits
  better), and its Electron-only window chrome.
- Porymap's Pokémon terminology and content, its stock Qt skin, and its
  "nothing collapses" narrow-window behaviour.
- Tiled's nine-dock system, `Tab`-to-Clear-View, and any feature DragonByte Z
  does not actually support (tile painting, layer creation, resizing, arbitrary
  pointer entry).
- LDtk's zen mode, its modal definition panels, and its striped textures.
- Godot's docking, editor layouts and feature profiles.
- Aseprite's retro pixel skin, editing GBA content is not a reason to look
  retro.
- RPG Maker MZ's modal properties and its absent panel headers.
- HexManiacAdvance's hex-first default surface. **DragonByte Z must not look like
  a hex editor.**
