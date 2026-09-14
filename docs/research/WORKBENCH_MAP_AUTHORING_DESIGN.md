# WORKBENCH-006 -- Visual map-authoring workspace -- DESIGN NOTE

Design analyst note. No production code written. Every mechanism claim is
grounded in `file:line` or a research doc section per the project #1 rule
NEVER GUESS. Design follows `dragonbyte-ui-design` the guide.

Status of the three load-bearing verdicts (full evidence in SC2/SC3/SC5):

| Verdict | Class |
|---|---|
| SC2 coordinate contract | **BLOCKED-NEEDS-RE** (halfword->pixel unproven) |
| SC3 authoring round-trip | **ROUND-TRIP-PROVEN** (structural build; runtime unverified) |
| SC5 placement->sprite identity | **PROVEN-COUNT = 0 / NEUTRAL-only** |

The headline consequence: the TOOLKIT-022 ownership refusal that threatened
Outcome A is **superseded** -- a built playable-shaped ROM with an added
placement exists today. But Outcome A's *visual* premise (drag a marker to a
pixel, see it there in-game) is **not** deliverable, because the placement
coordinate->map-pixel transform is not established. WORKBENCH-006 can ship a
real visual **viewer + semantic authoring** workspace now; direct pixel-move is
the part that would hit a §42-style block. Details below.

---

## SC1 -- The 10-question design pass

| # | Question | Answer (evidence) |
|---|---|---|
| 1 | User's primary task | See the rendered retail map, see its placements overlaid on it, select one, inspect/author its behavior/text, add or clone a supported placement, build, run. This is the scene-authoring loop of `scene_tab.py` given a visual surface. `dragonbyte-ui-design` the guide:29-34 (visual game content -> tools -> inspector). |
| 2 | Primary visual object | The composited map image. `render_map(rom, map_id)` returns `MapRenderResult` with `width`, `height`, 8-bit indexed `composite` bytes, `layers`, and 256-triple `palette` (`map_render.py:558,632-641`). Overlaid on it: placement markers. |
| 3 | Selection/context model | ONE selected placement persists while its behavior/text/trigger are edited in the inspector -- mirrors `scene_tab.py`'s navigation stack (`scene_tab.py:172,384,432-437`) which keeps `("map", id)` context under a placement. Map identity + selected placement live in `Session` (`session.py:57-58 selected_map`), not in the widget. |
| 4 | Primary actions (on the canvas) | Select placement (click), pan (middle-mouse), zoom (scroll) -- `desktop-editor-patterns.md:24-27`. Drag-to-move is DESIRABLE but blocked on SC2 (see there); ship click-select first, keep drag behind the coordinate transform. Add/Clone placement (canvas-anchored button or context action). |
| 5 | Secondary actions (inspector) / menus/toolbars | Inspector: choose behavior (existing descriptor or authored `show_centered_sprite_text` script), set trigger, edit position halfwords, revert a pending change -- all already exist in `scene_tab.py:298-335,439-455,486-504`. Toolbar: layer/overlay toggles, zoom, Add/Clone, Build/Run (`desktop-editor-patterns.md:9-12`). Menus: File/project-level only (`desktop-editor-patterns.md:4-6`). |
| 6 | Hidden / progressively disclosed | Every ROM address, file offset, `position_raw` word, `id_raw`, descriptor pointer, allocation/relocation. The workspace names things by semantic identity `map:NNNN` / `map:NNNN/placement:NNNN` (`scene.py:6-11`; webfoot-workbench the guide:65-84 "Navigate concepts, not storage"). Raw halfword spinboxes are the one leak today (`scene_tab.py:89-98`) -- see SC2. |
| 7 | Keyboard path | Tab order through map list -> canvas -> inspector fields; Ctrl+Z/Ctrl+Y undo/redo via `QUndoStack.createUndoAction` exactly as `graphics_tab.py:323-339`; arrow-key nudge of the selected placement is a keyboard alternative to drag (`accessibility-and-input.md:1-3,12`). Every mouse action needs a keyboard alternative. |
| 8 | Empty / error / read-only / disabled states | No ROM open -> tab disabled (`app.py:33,57-58`). Map with no supported placement source -> READ-ONLY, no fallback (`scene.py:126-131` MapSupport.READ_ONLY; the guide fail-closed). Render failure -> `MapRenderError` caught at the slot boundary, QMessageBox not a dead click (webfoot-workbench the guide:31-37; the parent-catch rule). No project open -> authoring disabled with reason (`scene_tab.py:339-341`). |
| 9 | Expected data volume | Maps are small: a BG layer is W×H 32×32-tile chunks; a chunk = 256×256 px. Map 39 is 3×2/3×2/4×2 chunks per BG -> composite ≈ up to 1024×512 px; map 40 is 1×1/2×2 (`MAP_RENDER_FORMAT.md:176-178`; `SCREEN_CHUNK_SIDE`/`map_render.py:61,316`). Worst realistic case ≈ ~1024×1024 px. Placements: **1,442 total across 240 maps**, max **69 placements for one type across 36 maps** but per-map counts are modest (`PLACEMENT_CODEC.md:39-43`; `PLACEMENT_TYPES.md:112`). So: one moderate image + tens of markers per map, never thousands. |
| 10 | Performance risks | `render_map` is **1.03 s (map 39) / 0.53 s (map 40)** uncached (`MAP_RENDER_FORMAT.md:222-224`) -- over the ~400 ms Doherty threshold (`qt-widgets-patterns.md:48-51`). So render MUST NOT run on pan/zoom/select; cache by map identity+revision (`performance.md:6`). Never decode in `paintEvent` (`performance.md:4`). Marker overlays are cheap; the risk is re-rendering the base needlessly. |

---

## SC2 -- Coordinate contract -- **BLOCKED-NEEDS-RE**

A placement's stored position is a single 32-bit word `position_raw` at record
`+0x0C`; `position_low = raw & 0xFFFF`, `position_high = (raw>>16) & 0xFFFF`
(`formats/map_placements.py:106-107`).

The **axis meaning of those halfwords is explicitly UNKNOWN**, stated in three
independent places:

- `formats/map_placements.py:6` -- "Prefix meanings stay raw, including position halfwords."
- `PLACEMENT_CODEC.md:20` -- "+0C position_raw; position_low/high remain axis-UNKNOWN".
- `PLACEMENT_TYPES.md:81` -- "position_low/high retained; **no axis claim added**"; and :189 "Coordinates remain deferred as before."

Nothing in `MAP_RENDER_FORMAT.md` connects a placement position to a render
pixel -- that doc is the BG tile-assembly chain (selectors, chunks, layers) and
never mentions placement coordinates. The rendered image's own coordinate
origin is logical chunk `(0,0)` row-major (`MAP_RENDER_FORMAT.md:159-166`);
whether `position_low/high` are pixels, tiles, subpixels, or a different origin
is not measured anywhere.

**Consequence.** The toolkit can READ the two halfwords, round-trip them, and
WRITE new values (`scene.py:151-187`, `PlacementRecord.with_position`
`map_placements.py:109-112`). It CANNOT place a marker at the correct pixel, and
therefore cannot convert a dragged pixel back to a correct halfword. Correct
overlay positioning **requires NEW substantial RE** (a runtime capture that
observes an object's on-screen pixel against its `position_raw`, of the kind
`MAP_RENDER_FORMAT.md` cites for the BG chain but has not done for placements).

**Design implication** (not a fix -- surfaced per Karpathy "surface, don't
invent"): the visual workspace can plot markers at a *documented-unproven*
position only if it is labelled as such, OR it defers marker positions until the
transform is proven. It must NOT silently draw a marker at `(low, high)` as if
that were a pixel -- that would fabricate a coordinate claim the evidence forbids.

Classification: **BLOCKED-NEEDS-RE.**

---

## SC3 -- Authoring round-trip verdict -- **ROUND-TRIP-PROVEN** (structural)

The TOOLKIT-022 refusal quoted in the ticket's CONTEXT is **stale**. The
`AUTHORED_PLACEMENTS.md` header still opens "Materialization is refused"
(:1-6), but its own body carries superseding banners and the code has moved past
every blocker:

- TOOLKIT-024 proved the engine array contract: counted loop at `0x08008C9E`
  over `MapEntry+0x04` (`ldrb`, one byte), array at `+0x14`, no sentinel/suffix,
  so a run owns exactly `count*4` bytes (`AUTHORED_PLACEMENTS.md:70-76`;
  `authored_placements.py:238-241`).
- TOOLKIT-025 removed the count blocker -- the new count is DERIVED and emitted as
  an attributed `ByteChange` (`AuthoredRun.derive_count_change`,
  `authored_placements.py:296-343`).
- TOOLKIT-026 published the array anchor as relocatable where its reference set
  satisfies the safety contract; `plan_relocation` moves it and rewrites the
  `+0x14` owner pointer (`authored_placements.py:2-11,1055-1060`).
- TOOLKIT-027/032 created the appended body + descriptor + script anchors and
  their references (`authoring_overlay` / `plan_authored_materialization`,
  `authored_placements.py:477-548,624-767`).
- The gate `require_materialization_contract` "no longer asserts a boundary at
  all. It RUNS the materialization and reports whatever production actually
  refuses" (`authored_placements.py:1070-1073,1104-1112`).

What production refuses now is **capacity**, and even that is resolved for one
case: TOOLKIT-028 verified and declared one CONFIRMED free region
`[0x007EA400, 0x007EA500)`, 256 bytes (`BUU_VERIFIED_CAPACITY.md:1-8,130-137`).
The canonical map 10 authored `+1` case **builds end-to-end** through
`build_project`: body at `0x7EA400`, expanded array at `0x7EA420`, owner pointer
rewritten `0x08E524`, count `2->3` at `0x08E514`, **output ROM produced,
8,388,608 bytes**, 48 bytes changed, byte-identical on rebuild
(`BUU_VERIFIED_CAPACITY.md:139-171`). The GUI already has the Extract->Validate->
Build->Run path that emits this (`build_panel.py:266-273 build_project`).

So Add/Clone + halfword-write **round-trips to a built ROM today**.

**The two limits that keep this from being unconditional Outcome A:**

1. **Runtime is NOT proven.** "Structural, not runtime. The ROM contains the new
   placement. Whether the engine behaves correctly with it in-game is a different
   proof and is not claimed." (`BUU_VERIFIED_CAPACITY.md:186-188`). Outcome A
   requires the mGBA "see it in-game" step, which is unverified.
2. **Capacity is 256 bytes, one region.** "It is not large: the next authoring
   case may need a further verified window." (`BUU_VERIFIED_CAPACITY.md:196-197`;
   every other profile declares zero, :137). A build needing >256 bytes of
   authored bodies raises `InsufficientSpaceError` (`allocation.py:119-121`).
   Every non-Buu ROM still blocks at capacity.

Verdict: **ROUND-TRIP-PROVEN** for a single small authored placement on canonical
Buu, structurally. The ownership refusal that would have been the §42 Outcome B
is gone. The residual §42 risks are the **runtime proof** and **>256-byte
capacity**, plus -- decisively for a *visual* workspace -- the SC2 coordinate
transform: a placement can be added and built, but not placed at a chosen pixel.

Smallest missing backend relation for full Outcome A: the runtime-proven
`position_raw`->screen-pixel transform (SC2). Capacity is already a known,
separately-tracked prerequisite for anything larger than the declared window.

---

## SC4 -- Canvas architecture recommendation

**Recommend: `QGraphicsView` / `QGraphicsScene` with a single cached background
`QGraphicsPixmapItem` and lightweight `QGraphicsItem` markers.**

One paragraph: the base map is one static raster produced by an expensive
(~1 s) SDK call, and the overlays are a few dozen selectable, individually
movable items -- this is exactly the case `QGraphicsScene` is built for, and it
gives pan/zoom/hit-testing/per-item selection for free (`qt-widgets-patterns.md:9-14`
offers three options "based on measured need"; `desktop-editor-patterns.md:24-27`
expects middle-mouse pan + scroll-zoom). Build the background once with
`indexed_pixmap`-style conversion (the `graphics_tab.py:154-168`
`QImage.Format_Indexed8 + setColorTable` path, reused because the SDK yields the
same tightly-packed indexed bytes + rgb table), cache the `QPixmap` keyed by map
identity + `Session.project_revision` (`performance.md:6`; `session.py:63`), and
set the view transform for crisp nearest-neighbour zoom
(`Qt.FastTransformation`, the `graphics_tab.py:540-557` pixel-art rule) -- never
re-render on pan/zoom. Markers are cheap `QGraphicsItem`s so a selection or a
nudge repaints only the item, not the base (`performance.md:4,10-12`). Future
tile/collision overlays are just additional item layers on the same scene, no
rewrite.

Do NOT build a generic reusable canvas framework (`desktop-editor-patterns.md:59-63`;
webfoot-workbench the guide:76-78 "not a giant editor framework"). Qt classes:
`QGraphicsView`, `QGraphicsScene`, `QGraphicsPixmapItem`, `QGraphicsItem`
subclass for markers, `QUndoStack`/`QUndoCommand`.

---

## SC5 -- Placement overlay & sprite-honesty -- **PROVEN-COUNT = 0 / NEUTRAL-only**

**No placement->sprite identity is proven.** A placement resolves to a
placement-*type* -> enemy-*stat* identity (1,284/1,295 placements, `PLACEMENT_TYPES.md:107`),
never to a decodable graphic. The field audit is explicit:
`Graphics/resource attachment | UNKNOWN; no sprite/graphics identity promoted`
(`PLACEMENT_TYPES.md:183`) and `+10 id_raw` "resource/graphics role not promoted"
(`PLACEMENT_TYPES.md:82`). The `ActorSprites` corpus the Graphics tab shows is
keyed by `GraphicIdentity`/`CharacterIdentity` (`graphics_tab.py:62,531-538`)
with **no** SDK edge from a placement or enemy to a graphic.

- **PROVEN-COUNT (placement->sprite thumbnail): 0.**
- **NEUTRAL marker: all placements.**

So every marker is a **neutral semantic marker**, never a real sprite thumbnail.
Marker design (honest + legible over complex map art, per
`accessibility-and-input.md:5-9` and the maintainer's red-green colorblindness):

- A filled shape (e.g. rounded pin) with a **strong outline** (light halo /
  contrasting border) so it reads against any BG -- legibility by luminance +
  shape, NEVER color alone (`accessibility-and-input.md:8`).
- Distinguish placement *classes* (enemy-linked type vs. authored clone vs.
  read-only) by **shape/glyph/brightness**, not hue.
- Selection cue: a distinct ring + raised elevation, not merely a color swap.
- The marker's label is the semantic identity (`map:NNNN/placement:NNNN`), the
  known enemy-stat identity where present (`scene.py:329-331`), and nothing else
  -- no fabricated name (`PLACEMENT_TYPES.md:142` "does not prove ... a human name").

Do NOT infer sprite identity from numeric similarity, names, or adjacency
(explicitly forbidden, `PLACEMENT_TYPES.md:141-142`).

---

## SC6 -- Workspace layout & integration

**Add ONE new tab, "Map"** (a visual sibling of the existing "Maps"/Scene tab),
plugged into the existing `QTabWidget` shell. Do **not** replace `scene_tab.py`
this ticket -- reuse it. The shell already enumerates tabs and enables them on ROM
open via signal wiring (`app.py:32-33,44-78`); a new tab follows the same
`on_session_changed` + `projectChanged`->`_build.on_project_mutated` pattern
(`app.py:74-75`).

Panel hierarchy (all within the one tab):

- **Left: map list** -- `list_maps`/`list_authorable_maps` with support state
  (`scene.py:102-148`), as the existing `scene_tab.py:206-226` selector but as a
  list. The map is the composition hub (webfoot-workbench the guide:70-72).
- **Center: canvas** -- the `QGraphicsView` of SC4 with markers.
- **Right: inspector** -- selected placement's relationships + editors, REUSED
  from `scene_tab.py`: behavior chooser (`scene_tab.py:298-313`), authored
  `show_centered_sprite_text` script controls (`scene_tab.py:107-119,315-324`),
  trigger (`scene_tab.py:326-335`), position halfwords (`scene_tab.py:89-98`,
  labelled unproven per SC2), and the semantic relationship navigator
  (`scene_tab.py:139-165,346-385`). Named reused editors: scene, behavior,
  script, text -- the same `scene`/`PlacementEvents`/`TextStrings` facades
  (`scene.py:265-279,383-393`).
- **Toolbar:** Add/Clone, layer/overlay toggles, zoom, Build/Run.
- **Status bar:** selected placement identity, zoom, validation/build currency
  (`desktop-editor-patterns.md:14-16`; the `graphics_tab.py:966-980` status
  pattern).
- **Menus:** project-level only.

**Selection context survives contextual editing** by holding
`selected_map` + selected placement in `Session` (`session.py:57-58`) and using
the `scene_tab.py:172,432-437` navigation stack so "Open Behavior"/"Open Script"
and "Back to Map" return to the same placement.

**Narrow vs wide:** the three panels sit in nested `QSplitter`s (the
`graphics_tab.py:356-360` pattern); at narrow width the map list collapses to a
dropdown and the inspector docks below the canvas.

**Undo/redo:** one `QUndoStack` per the `graphics_tab.py:79-151,197,323-339`
pattern; **one drag = one undo step** via `QUndoCommand.id()` + `mergeWith()`
(`qt-widgets-patterns.md:42-46`; `graphics_tab.py:120,143-151`). Note the
graphics_tab hard-won rule: perform+validate the SDK write in the slot BEFORE
`stack.push()`, because a Python exception inside `redo()` is swallowed by Qt yet
still records a corrupt command (`graphics_tab.py:94-102,882-902`) -- the Map
tab's add/clone/move commands must follow the same apply-before-push shape.

---

## SC7 -- Phased implementation outline (for the next spec, not code)

Ordered implementable chunks, each with rough SDK touch-points:

1. **Canvas render** -- new Map tab; render one map to a cached pixmap.
   SDK: `map_render.render_map` (`map_render.py:558`); convert via the indexed
   pixmap path (`graphics_tab.py:154-168`); cache by map id + `project_revision`.
2. **Map list + selection** -- populate from `scene.list_maps` (`scene.py:102`);
   support-state labels; enable/disable per ROM (`app.py`, `session.py`).
3. **Placement overlay (markers)** -- plot NEUTRAL markers from
   `scene.scene_placements` (`scene.py:190-224`). **Gated on SC2**: until the
   coordinate transform is proven, either (a) label markers "position unproven"
   or (b) list placements beside the canvas without pixel positions. Do not
   fabricate a pixel from `(low, high)`.
4. **Selection + inspector** -- click a marker -> reuse `scene.placement_relationships`
   (`scene.py:282`) and the `scene_tab.py` relationship navigator + editors.
5. **Direct-move + undo** -- arrow-nudge / drag -> `with_position` write via
   `scene`/project (`map_placements.py:109`); one `QUndoCommand` per gesture
   (SC6). **Gated on SC2** for correctness; nudging raw halfwords works now but
   is not a proven pixel move -- ship as "adjust position value", not "drag on map",
   until RE lands.
6. **Add / Clone** -- `scene.add_authored_npc` -> `clone_placement`
   (`scene.py:425-481`; `project/placements.py:188`); fail-closed on validation.
7. **Inspector behavior/script/text integration** -- behavior chooser, authored
   `show_centered_sprite_text`, trigger; all via `scene` facade
   (`scene.py:265-422`), reused from `scene_tab.py`.
8. **Layer / overlay toggles** -- toggle `MapRenderResult.layers`
   (`map_render.py:632-641`); marker-class visibility filters.
9. **Build/Run wiring** -- reuse `build_panel.py`'s Validate->Build path
   (`build_panel.py:178-273`) and the safety invariant (`build_panel.py:44-52`);
   emit `projectChanged`->`on_project_mutated` (`app.py:74-75`).
10. **Tests** -- headless: render-cache invalidation, marker plotting from SDK
    rows, undo/merge for a move, add/clone round-trip; per webfoot-workbench
    the guide the SDK-parent-catch behavior must be tested.
11. **QA** -- mandatory `dragonbyte-ui-qa` live launch/screenshot/inspect pass
    (`dragonbyte-ui-design` the guide:89-92; webfoot-workbench the guide:62).
    Feedback GUI except-breadth is a known live-walkthrough-only defect
    (MEMORY.md).

Scope honesty: chunks 1-2, 4, 6-11 are deliverable on today's backend. Chunks 3
and 5's *visual-pixel* correctness are the parts blocked by SC2 and are the
ticket's real Outcome-A risk.

---

## BLOCKERS

- **SC2 coordinate transform (BLOCKED-NEEDS-RE).** `position_low/high`->map-pixel
  is unproven (`map_placements.py:6`, `PLACEMENT_CODEC.md:20`,
  `PLACEMENT_TYPES.md:81,189`). Blocks true drag-to-pixel and honest marker
  positioning. This is a research prerequisite, not a design gap -- surfaced, not
  invented around.
- **SC3 runtime proof + capacity.** Structural build is proven; in-game behavior
  is not (`BUU_VERIFIED_CAPACITY.md:186-188`); only 256 bytes of Buu capacity
  declared (`:196-197`), zero elsewhere (`:137`).

Neither stopped the note; both are reported with exactly where the evidence sits.

## SCOPE ADHERENCE

The note follows the design brief exactly; no scope changes were made.

## RECOMMENDED NEXT

Resolve SC2 first: a runtime RE ticket proving `position_raw`->screen-pixel is the
single unblock for visual drag-authoring. WORKBENCH-006 implement can still
proceed on chunks 1-2,4,6-11 (viewer + semantic authoring + build/run) in
parallel, treating marker pixel-position as deferred rather than fabricated.

---

## Decision, 2026-09-14

This decision takes precedence over the Recommended Next paragraph above.

WORKBENCH-006 stops at design. Implementation is blocked by deliberate decision,
not by inability to write GUI code. Rationale: the core acceptance
(`see object on actual map -> drag object -> build -> object appears there in
retail`) depends on the placement coordinate transform, which is unproven. A
"best-known" provisional marker would make the canvas visually assert a location
the project cannot prove -- that undermines the entire purpose of a visual editor.
No viewer-only reduced WORKBENCH-006. No provisional markers. No direct-manipulation
UI built around an unproven coordinate meaning. The parallel-viewer path in
RECOMMENDED NEXT above is explicitly NOT taken.

### Dependency graph at design close

- placement materialization / build round-trip: **PROVEN**
- visual map renderer: **PROVEN**
- placement read/write halfwords: **PROVEN**
- placement -> sprite identity: **UNKNOWN**, non-blocking (neutral markers acceptable)
- placement raw position -> logical map pixel coordinate: **BLOCKED-NEEDS-RE**
- logical map pixel coordinate -> authored raw position: **BLOCKED-NEEDS-RE**

The prior WORKBENCH-006 threat around TOOLKIT-022 materialization refusal is
**STALE** -- superseded by later authoring/materialization work
(TOOLKIT-024/025/026/027/032, per SC3). It is not carried forward as a blocker.

### Handback

    WORKBENCH-006 STATUS: DESIGN COMPLETE / IMPLEMENTATION BLOCKED
    EXACT BLOCKER: placement position_raw <-> logical map pixel coordinate transform
    PLACEMENT MATERIALIZATION: PROVEN
    PLACEMENT -> SPRITE IDENTITY: UNKNOWN / NON-BLOCKING
    PROVISIONAL MAP MARKERS ALLOWED: NO
    NEXT REQUIRED WORK: focused runtime RE of placement coordinate semantics

The next ticket is NOT defined here (ticket section 44: do not define or begin the next ticket).
