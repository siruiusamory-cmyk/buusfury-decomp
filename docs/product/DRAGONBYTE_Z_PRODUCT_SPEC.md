# DragonByte Z product specification

The design of the DragonByte Z desktop application: an all-in-one ROM editor
for the Webfoot Dragon Ball Z GBA games.

**Status: design only.** Nothing in this document is implemented. It describes
the product that will be built, not behaviour that exists today. Where this
document and a tracked authority disagree, the authority wins:

- [`../architecture.md`](../architecture.md) - the SDK layers and the safety invariants.
- [`../project-format.md`](../project-format.md) - the authored project format and its determinism guarantees.
- [`../ROM_SAFETY.md`](../ROM_SAFETY.md) - the mandatory safety contract.
- [`../workbench-architecture.md`](../workbench-architecture.md) and [`../desktop-ui.md`](../desktop-ui.md) - what the desktop surface may own and how it must look.

**Evidence base.** The design is driven by the merged ROM editor coverage
census, [`../research/ROM_EDITOR_COVERAGE_SUMMARY.md`](../research/ROM_EDITOR_COVERAGE_SUMMARY.md),
its ledger and its normative data file
[`../research/rom_editor_coverage.json`](../research/rom_editor_coverage.json),
at merge `178814c5f45a02a482b404b3831b2f72bfeb6a53`, the merge that landed it.
(The census file itself records its own ticket baseline,
`486e3c665929a8dc57c63b7915f74606e30ccb0d`, because origin/master advanced while
that ticket was open.) That census is referenced here as evidence; its 40-row
ledger is not restated.

The 24-entry public capability registry (`src/data/capabilities.json`) measures
a different question, is unchanged by this document, and reads 24 of 24.

---

## 1. Product identity

DragonByte Z is an all-in-one ROM editor for the Webfoot Dragon Ball Z GBA
games: Buu's Fury, The Legacy of Goku and The Legacy of Goku II. It opens a
verified ROM, shows the game's own structures, lets the user change what the
tool understands, builds a new image from an authored project, plays it and
exports a distributable patch.

It is not an engine reimplementation and it is not a game maker with a ROM
hidden underneath. The unit of work is the ROM's own data and the game's own
concepts, and the product's job is to make those reachable.

**Core principle: hide needless complexity, not ROM-hacking concepts.**

Normal UI may show a ROM, a map id, an entity id, a script id, a sprite id, a
record identity, and an address where an address is the honest answer.
Implementation detail is progressively disclosed, never erased. There is no
Beginner mode and no Expert mode, because a mode switch moves the difficulty
into the wrong place: it hides the data a serious user came for and it teaches
a beginner that the concepts do not exist.

## 2. Target users

Four users, in decreasing frequency. Every design decision names which one it
serves.

1. **The experienced ROM hacker.** Works from IDs, offsets and reference
   tables. Cares about speed, density, exactness and not being blocked. Serves:
   the ROM surface, the inspector's Technical details, keyboard navigation,
   copyable identities, raw byte authoring.
2. **The returning hacker of this family.** Knows the games and a previous
   editor, does not know this one's vocabulary. Cares about finding a thing by
   name or id and about being told honestly what can be changed. Serves: the
   five destinations, search over names and ids, the support vocabulary.
3. **The newcomer with a specific goal.** Wants one change (a line of text, a
   statistic, one sprite) and no theory. Serves: one destination, one list, one
   inspector, and a refusal that names what to do next.
4. **The maintainer and the researcher.** Needs to know what the product does
   and does not understand, and needs the same answers the census gives.
   Serves: the Coverage view, Technical details, provenance on every value.

## 3. Design principles

1. **The SDK owns truth.** The application holds paths and the values the SDK
   returns and asks the SDK for everything about ROM semantics. It computes no
   ROM-format value, ever (`../workbench-architecture.md:17-18`, `:34-35`).
2. **One canonical project.** The GUI and the CLI build the same authored
   project through the same build path. No second file format, no GUI-only
   state that the build path cannot see.
3. **Plain objects under a thin window.** Session, journal, index and the edit
   model are importable and drivable with no window open, so a test can prove
   them without Qt.
4. **Show the small correct path first, and the escape hatch where it is
   asked for.** A destination leads with the ordinary operation and puts
   addresses, provenance and raw bytes one deliberate step away.
5. **Fail closed with the reason stated.** An unresolvable target stays
   read-only and says why. There is no accept-anything switch and no silent
   partial write (`../workbench-architecture.md:151-152`).
6. **Confirm destructive steps and name what will be replaced.** Discard,
   overwrite and raw writes inside another structure's bytes each name the
   object and the bytes.
7. **Never teach that unknown means free.** An unowned byte range is unmapped
   until evidence says otherwise. The census states this for the whole image
   (`../research/ROM_EDITOR_COVERAGE_SUMMARY.md:84`) and one 256-byte window in
   the whole catalog is `VERIFIED_FREE` (`tools/webfoot/atlas.py:93`).
8. **Determinism is a product feature.** Same project files, same base ROM,
   same toolkit, byte-identical output (`../project-format.md:320-334`). Any
   design that would break that is rejected in this document's own terms.
9. **Density over decoration.** A dense desktop tool for people who read ids.
   No cards, no dashboards, no animation (`../desktop-ui.md`).
10. **Support is stated, not implied.** What the product can edit, inspect,
    know about but not support, and does not understand are four different
    answers and the UI gives the true one.

---

## 4. Information architecture

Six conceptual destinations. Five are peer destinations; the sixth is the ROM
itself, which is summoned rather than parked because that is what its use looks
like (section 5).

| Destination | Owns | Today's SDK behind it |
| --- | --- | --- |
| **Maps** | map identity and header records, layout chunk grids, chunk containers, warps and transitions, map graphics as they are read | `maps.py`, `map_authoring.py`, `map_layout_edit.py`, `map_chunk.py`, `map_paint.py`, `map_resize.py`, `map_transitions.py` |
| **Entities** | placement-family object records, the unmodelled sibling families as unknown structures, behaviours and their attachments, character and enemy stat records, item records as read-only | `entities.py`, `scene.py`, `placement_events.py`, `stats.py`, `project/placements.py` |
| **Scripts & Text** | script families and roots, the event resource corpus, dialogue records and their text, the string tables | `scripts.py`, `dialogue.py`, `text.py`, `compressed_dialogue.py` |
| **Graphics** | actor sprite identity, sprite frames and their payloads, appearance records, object palettes | `graphics.py`, `sprite_identity.py`, `sprite_authoring.py`, `graphics_authoring.py`, `appearances.py`, `appearance_authoring.py` |
| **Data** | stat tables, map-entry tables, item table, and the coverage view of what is and is not understood | `stats.py`, `maps.py`, `build.py`, `atlas.py` |
| **ROM** | the image as an address space: ranges, ownership, bytes, raw write, raw search, modified-byte state | `binary.py`, `layout.py`, `atlas.py`, `write.py`, `authored_image.py` |

**Why the six are not six equal tabs.** The census says the ROM surface is
first-class and that integrated hex editing is a 1.0 requirement; it does not
say it is used as often as Maps. Making it the sixth peer tab would spend a
permanent slot on a surface most sessions visit for a minute, and it would
still be reached the same way in practice (from an object, or from an address).
Making it an advanced-settings dialog would be the opposite error: the census
records that the write stack refuses any change without a named owner
(`ROM_EDITOR_COVERAGE_SUMMARY.md:56`) and that serious hacking extends past the
semantic editors, so hiding the raw surface behind a settings affordance would
misrepresent the product. Section 5 chooses the third option.

**Edges the product may navigate** (approved by the census,
`ROM_EDITOR_COVERAGE_SUMMARY.md:125`):

```text
map -> layout -> chunk -> map graphics
map -> warp -> map
object array -> placement -> behaviour -> script -> text
script root -> owning record
sprite -> animation -> frame -> container
appearance -> sprite -> text
item -> text
item -> script
```

**Edges the product must not assert** (`ROM_EDITOR_COVERAGE_SUMMARY.md:126`):

```text
placement -> the sprite it draws
enemy stat -> sprite
map trigger -> script
shop -> item list
anything -> audio
```

These get no link, no preview, no inferred panel and no disabled-but-hopeful
button. Where a user's task would obviously want one, the inspector says
`Relationship not modelled` and offers the ROM surface. A dead link is a
defect, not a placeholder.

**Graph, not tree.** The eight approved edges are edges. Forcing them into one
hierarchy invents parentage that the evidence does not support (the same reason
`../desktop-ui.md:117-118` asks for a browser chosen by data type rather than a
tree by default). Each destination presents its own list or canvas and the
cross-links are actions, not a folder path.

---

## 5. Main-window architecture

The main window has four fixed regions and no docks.

```text
+---------------------------------------------------------------+
| menu | project identity + revision state | search | goto | ....|  action bar
+---------------------------------------------------------------+
| Maps | Entities | Scripts & Text | Graphics | Data || ROM      |  destination strip
+---------------------------------------------------------------+
| mode row for the active destination (hidden when it has one)   |
+---------------------------------------------+-----------------+
|                                             |                 |
|              centre editor                  |   inspector     |
|         (the active destination)            |  (contextual)   |
|                                             |                 |
+---------------------------------------------+-----------------+
| status: build/validate state, counts, provenance               |
+---------------------------------------------------------------+
```

**Chosen architecture: five destinations plus a summoned ROM surface.**

The strip carries `Maps`, `Entities`, `Scripts & Text`, `Graphics`, `Data`, a
separator, then `ROM`. The ROM entry is a checkable button in the same strip, in
the same history and in the same centre area as the others, so it is a real
editing and exploration surface. It is separated by one rule because it is a
different kind of surface: address-first rather than identity-first. Three other
routes reach it, and they are the routes used in practice:

1. `Ctrl+G`, or the action bar's `Go to address` field.
2. `Open bytes` on any selection whose extent the SDK can prove (disabled, with
   the reason, when it cannot).
3. A search hit whose region class is not a known structure.

There is no ROM entry in a Tools menu, no modal, no second window and no hidden
shortcut.

**Rejected alternatives.**

| Candidate | What it is | Why not |
| --- | --- | --- |
| Six equal destinations | Six peer tabs, ROM with the same weight as Maps | Spends a permanent, equal slot on a surface whose work is episodic, and implies the six have comparable depth when the census shows five domains of partial support and one address space. It also pushes the raw surface toward "the hex tab", a place you go to instead of a lens you use. |
| Resource tree with document editors | A left tree of maps, entities, scripts, sprites, tables and ranges; centre is one document per open resource; tabs to switch documents | The census's edges are a graph, so a tree would invent hierarchy. It multiplies state owners (per-document dirty and undo), which is exactly the beta defect this design removes (four separate `QUndoStack` instances today). It has no honest place for address-first exploration. The ticket's own rule applies: no document model unless it solves a real workflow, and section 5's concession below names the one workflow it would help. |
| Address-first hex shell | The hex view is the centre; semantic editors are lenses over ranges | Inverts the product identity. Most of the user's work is about game objects, and most of the image is not a modelled structure. It would also make the honest per-range ownership problem (section 8) the very first thing a new user meets. |

**The ten architecture questions, answered.**

| # | Question | Answer |
| --- | --- | --- |
| 1 | Where the six live | Five peers in the strip; ROM after a separator in the same strip. Order and shortcuts are fixed once: `Ctrl+1`..`Ctrl+6`. The strip is a non-floatable text toolbar; the active entry is checked, bold and bordered, never colour-only. |
| 2 | Switching destinations | One click, or `Ctrl+N`. Switching never clears a selection, a staged edit or the undo stack, because those live in the session and the journal, not in a widget. Inside a destination, a mode row (the pattern Maps already proves: `Browse`, `Layout`, `Objects`, `Warps`) selects what the centre shows. A mode is disabled with a reason when this title has no data for it, never hidden and never silently redirected. |
| 3 | Opening another resource | The value is a link. It pushes one history entry, switches to the destination that owns the target, selects the target and focuses its row. When the target is not modelled the value stays plain text and the inspector says `Relationship not modelled`. |
| 4 | The inspector | One inspector, shared by every destination, 320 px default with a 260 px floor. It renders the section list the active mode declares: content, then editing context, then authoring state, then a collapsed `Technical details` disclosure. Nothing selected is not a blank pane: it shows the destination, the mode, the precondition that mode needs, and project state. Multi-selection is explicit: a mode either supports bulk editing (fields identical across the selection are editable, differing fields read `multiple values`, one Apply is one undo entry) or it does not (all fields disabled, with the single-record operation that is required instead). |
| 5 | Raw/hex integration | As a destination reachable from anywhere, with two views over one cursor: `Ranges` (ownership map with a bytes preview) and `Bytes` (the hex editor). Everywhere else, raw is one disclosure away and is never a label: no semantic editor shows a byte grid or an offset column in its header. See sections 8 and 9. |
| 6 | Multiple open resources | "Open" means exactly one image per project. Each destination keeps one live cursor. A bounded 20-entry `Recent` menu holds recently visited resources, newest first, deduped by identity. That is the whole model. No document tabs, no close action, no per-resource dirty dot, no `Ctrl+W`, no second window. A staged edit is not tied to a cursor and survives navigating anywhere. |
| 7 | Returning | One navigation history: `Alt+Left` / `Alt+Right`, 100 entries, in memory only. An entry stores destination, mode, resource type and identity, sub-selection (a placement, or a byte range), scroll position and inspector disclosure state. It does not store edits or undo. Repeated selection within 500 ms coalesces. Navigation undo is not edit undo: `Ctrl+Z` after panning a map must not undo the pan. |
| 8 | Global actions | The action bar: project identity, global search, `Go to address`, `Validate`, `Build`, `Run`, `Export patch`. They are global because each concerns the whole image and every edit invalidates all of them. Menus carry open/save/extract/output, edit (undo, redo, back, forward, recent), view (destinations, modes, panels) and help. An action has exactly one home: it is not repeated in a menu, a strip and a context menu. |
| 9 | Incomplete coverage | Three mechanisms, each chosen against a rejected alternative. The three unmodelled per-area object families appear as sibling rows under the modelled family in Entities: `Object families: 1 of 4 modelled`, each unmodelled row showing only its pointer slot and stride, labelled `Family not modelled`, with no invented name. Rejected: a badge on every row of every list, which repeats one fact dozens of times. Adopted: support is a property of a record family and appears in the record list's trailing column and the inspector chip. The 266 script handlers appear in Scripts & Text as `Handler <n> - semantics unknown` beside an address that can be copied; no pseudo-name, no guessed mnemonic. `Data` carries a `Coverage` view: what is modelled, what is known but unsupported, what is unmapped, and what the evidence basis is. Save data and audio appear there as unmapped and have no editor surface at all, because an empty editor with a title is a claim the census does not support. The `Open bytes` route from Technical details is adopted with its gate: it appears only when the extent is proven. Hiding unknown systems entirely was rejected: 83 of 120 cells are unmapped and most LOG1 and LOGII cells rest on not-investigated, so hiding that would ship a false impression of completeness. |
| 10 | Support states without shouting | Four support states plus two that are not support states; see section 12. They appear in exactly three places (a list's trailing column, the inspector chip, the Coverage view) and never colour a canvas, a toolbar button or a navigation label. |

**The strongest objection, and the concession.** One centre editor with no
document tabs is weaker than a document model for one real task: comparing two
resources, most concretely editing one dialogue record while reading another
(`../journeys/dialogue-editing.md`). The contract answers it partly (the recent
list is two keystrokes, and nothing is lost on navigation because edits live in
the journal) and does not answer side-by-side comparison. The named fix, if a
real session shows it is needed, is a split centre holding two cursors into the
same destination, never a tab bar. That is a deliberate deferral, recorded here
so it is not rediscovered as a defect.

---

## 6. Navigation model

- **One history.** Push on destination switch, on resource selection, on
  cross-link traversal, and on `Go to address`. Cap 100, in memory, not
  persisted.
- **One entry, one step.** A cross-link that changes destination, mode and
  selection is one entry, not three.
- **Focus follows the landing.** After a cross-link, focus moves to the target
  row and its accessible name says what it is, so a screen reader announces the
  landing rather than the departure.
- **Recents.** 20 entries, deduped by resource identity, cleared when a
  different image is opened.
- **Search is a route, not a view.** The action bar's search is one field over
  both semantic search (`tools/webfoot/atlas.py:626`) and, once it exists, raw
  byte search. A hit is a link into the destination that owns it. Search results
  are a temporary list, not a destination and not a document.
- **No history of edits.** Back/Forward never changes data.

## 7. Resource identity model

Three tiers, each with one job. All three are always available for a selected
object; the tier shown first depends on the surface.

| Tier | Example | Job | Where it appears |
| --- | --- | --- | --- |
| Friendly display identity | `Placement 037`, `Map 0012 - West City`, `Text 1525`, `Sprite 149`, `Enemy 034` | Scannable label, unique inside its parent | List rows, headers, breadcrumbs |
| Stable technical identity | `map:0012/placement:0037`, `enemy:0034`, `event_resource:0290`, `item:0000` | The key: stable, copyable, searchable, recorded | Inspector identity row, search, project files, manifests, refusals, bug reports |
| Address identity | image `0x08711274+0x1C`, file `0x711274+0x1C`, range `[0x08711274, 0x08711290)` (half-open, as the plan's own `end` is) | The join between a semantic object and the bytes | Technical details everywhere; primary in the ROM surface |

Rules.

1. **Nothing stable is hidden.** The stable identity is one row under the
   friendly label in the inspector, copyable, present for every selection. It is
   never a tooltip and never behind a disclosure. This resolves the deferred
   question: the SDK identity `map:0012/placement:0037` is shown as the record
   identity, while the list says `Placement 037`.
2. **Addresses are diagnostics outside the ROM surface.** One disclosure away,
   copyable, never the primary label and never an authoring input
   (`../desktop-ui.md:33-34`). The ROM surface is the deliberate exception: it
   is address-first by nature, and that exception must be written into
   `../desktop-ui.md` when the surface is built rather than left as a
   contradiction. Until then this document is the record of it.
3. **Ids are never hidden or renamed.** A map's display name is content and can
   change; its id cannot and is always visible next to it.
4. **Unknown records are named as unknown.** `Unclassified structure`,
   `Object family not modelled`, `Handler 128 - semantics unknown`.

Terminology, resolved.

| Concept | User word | Identity form | Notes |
| --- | --- | --- | --- |
| Whole image | ROM / canonical image | profile id + sha256 prefix | The verified base. Never editable, never overwritten. |
| A build input | project | project directory | Authored TOML plus referenced assets. |
| Object family in an area | object family | `area:0012/family:<slot>` | One of four is modelled. The rest are unknown structures. |
| A placed object | placement | `map:0012/placement:0037` | The modelled family. |
| What controls a placement | behaviour | `behaviour:0004` | Attachment and trigger/effect contract. |
| Script body | script | `event_resource:0290` | Roots and family matter; the family is shown. |
| Text | text | `text:1525` | One string, addressed by its table and index. |
| A drawn actor | sprite | `sprite:0149` | Registry identity: what the actor is. |
| How it looks | appearance | `appearance:0149` | The record binding an actor to what is drawn. Both are shown; neither is called the other. |
| Byte position | image address / file offset | `0x08xxxxxx` / `0x0xxxxx` | Both spellings always, never a bare "offset". |
| Changed bytes | changed bytes | a range plus the owning edit | Differs from the canonical image. |
| Base bytes of a range | canonical bytes | a range | Read-only. The comparison column. |

## 8. Raw and semantic ROM surface

The ROM destination is the census's "raw and semantic browser over byte ranges
with an integrated hex surface"
(`ROM_EDITOR_COVERAGE_SUMMARY.md:124`). It owns: address and range lookup for
the whole image, range to owner and owner to range, the honest population of
owned bytes, raw byte search beside semantic search, modified-range state, and
canonical-base comparison for a range.

**One cursor, two views.**

```text
Ranges view:  a vertical map of the image, one row per covered span, with
              classification, confidence, owner(s) where known, and a byte
              preview; a jump list of declared tables; a changed-bytes overlay
Bytes view:   16 bytes per row, an address gutter (image address and file
              offset), an ASCII gutter, and a write caret
```

Both views share one selection and one `Go to address`. An owner, a reference
(`tools/webfoot/atlas.py:554`, `:565`) or a range query (`:571`) can be opened
from either.

**Honest range state.** For any range the surface can say exactly four things,
and it says the weakest one that is true.

| State | Meaning | What is offered |
| --- | --- | --- |
| Owned | a declared structure claims these bytes | read, select, search, copy, `Go to owner`; a write is refused here and offered as the semantic edit |
| Shared | more than one structure's extent covers the range | read, select, and a list of the owners; a write requires the owner to be named |
| Known shape, no owner | classified by the atlas with a classification and confidence but no semantic identity | read, select, search, copy, and a raw write behind the confirmation |
| Unmapped | neither owner nor known structure | read, select, search, copy, and a raw write behind the confirmation, labelled `Unmapped` |

`Unmapped` never reads `free`, `empty`, `padding` or `safe`. The atlas's own
`PADDING_CANDIDATE` is not free, and `VERIFIED_FREE` covers one 256-byte window
in the catalog (`tools/webfoot/atlas.py:93`).

**What the surface does not pretend.** The atlas classifies every byte exactly
once (`tools/webfoot/atlas.py:154-155`) and carries classification, confidence
and provenance per span (`:124-129`), but **no semantic owner identity per
span**. The owner column is therefore populated from the range index
(section 14), from the journal and from the build manifest, and where none of
those has an answer the surface says `no semantic owner known` rather than
leaving a blank that reads as "nothing there".

## 9. Hex editor contract

**Selection.** A byte range with a caret. It is addressable, copyable and
reported by image address and file offset. Selection and scroll live in the
session, so leaving the destination and returning preserves them.

**Write path.** A write is accepted only as a `ByteChange` with a non-empty
owner (`tools/webfoot/write.py:313-325`), a fixed length (`:316-321`), an offset
inside the image, `old` bytes that match the base (`:1203-1235`) and no overlap
with another change. The product adds the checks the format cannot express.

1. **Owner namespace.** A raw write carries `raw:<image address>` (plus a parent
   record identity when the range lies inside a known record). The namespace is
   what makes the manifest answer which edit changed these bytes; the census's
   attributable-change invariant is preserved rather than waived.
2. **Claimed bytes are refused.** A write into bytes a declared structure owns
   is refused with `These bytes back <owner>; edit that object instead`, plus a
   `Go to owner` action. Making the same change through the semantic editor is
   the offered route.
3. **Unclaimed bytes are confirmed.** The confirmation names the range, the old
   bytes, the new bytes and the owner the write will carry.
4. **Growth is refused with a reason.** Fixed-length overwrite only; a change
   that resizes says which relocation or encoder path is needed and does not
   silently fail (`tools/webfoot/write.py:316-321`).
5. **One undo entry per write**, with a `mergeWith` id so a continuous
   interaction collapses (`../desktop-ui.md:148-151`).
6. **Two writes to one field is a contradiction.** The authored-image layer
   already refuses it (`tools/webfoot/authored_image.py:550-554`), its tolerant
   duplicate rule lives at `:195-200`, and a manifest change with no owner is
   malformed (`:537-538`). The product must not create any of those states.

**Why this is a design and not a description.** The census records arbitrary
byte authority as absent, with a new owner class required. Measured against the
code at the merge above: the check is a non-empty owner string
(`tools/webfoot/write.py:324-325`) and the rest live in the plan's own
validation. So what is genuinely missing is narrower than "a class": it is a
typed raw owner, a raw-versus-claimed-bytes check over the range index, an
entry point, and undo. Section 14 assigns each of those. The census's
`CORE_AUTHORITY_REQUIRED` verdict stands; its wording is refined here rather
than repeated.

**Reading the canonical column.** The ROM surface shows the canonical bytes of
a range read-only, beside the current bytes. That column is never editable and
never written to in place; the write always lands in the project and is emitted
as a new image (`../architecture.md:75-76`).

## 10. Core workflows

Twenty jobs, each with the service that carries it and the honest constraint.
`NEW` marks work this document designs and the roadmap schedules.

1. **Open a supported ROM / project.** Open a `.gba`; hash and match it against
   `config/roms.yaml` (`tools/webfoot/rom.py:31`, `profile.py`); on a match show
   profile, region, revision and sha256 prefix; on no match refuse and print the
   measured digest beside the accepted ones. Then open or extract a project
   (`cli.py:530-533`) and validate it against that base (`cli.py:553-556`).
   *Refuse*: no compatibility mode, no near match, no writable project against
   an unidentified image. A profile with no declared tables (two of the four)
   opens read-only for domains and stays live for the ROM surface.
2. **Find a map and change its layout.** Maps -> search by name or id -> select
   -> `Layout` mode -> paint chunk cells and the structural grid, resize, add a
   layer. Each mutation is one journal entry owned by the map or layer.
   *Carried by* `map_layout_edit.py`, `map_paint.py`, `map_resize.py`.
   *Refuse*: layout is Buu's Fury only today; LOGII and LOG1 have no declared
   grid, so the mode is disabled with that reason rather than empty.
3. **Find an NPC and inspect what controls it.** Entities -> placement list for
   the map (`cli.py:122-130`) -> inspector shows identity, position, type,
   behaviour and attachment (`event attachments`, `event for-owner`,
   `cli.py:151-160`) -> script root -> owning record. Every hop shows the
   evidence class that supports it. *Refuse*: no sprite is drawn beside the row;
   that edge is unproven. Three of four object families show as unknown
   structures, not as arrays.
4. **Make an NPC show or change text, using proven relationships only.**
   placement or behaviour -> script (`event for-placement`, `cli.py:159-160`) ->
   resource extent and dialog type (`event resource-show`, `cli.py:163-165`) ->
   dialog -> text (`event dialog-refs`, `event dialogs-for-text`,
   `cli.py:166-171`) -> edit the string (`text set`, `cli.py:448`). Or through
   the item path: `event for-owner item:NNNN` -> the item's text indices.
   *Refuse*: no map-trigger-to-script edge and no map-scene-to-text query exist
   (`cli.py:145`), so "the trigger that shows this text" is never offered; a
   dialog whose text index is computed at runtime reports a stated absence, not
   a guess.
5. **Modify enemy stats.** Entities or Data -> enemy records (141 records of
   28 bytes at `0x08711274`, `config/roms.yaml`) -> `stats list` -> edit a named
   field -> `stats validate-round-trip` must pass before the edit is accepted
   (`cli.py:381-405`, `tools/webfoot/stats.py:343-375`). *Refuse*: fields whose
   game meaning is not recovered stay unnamed and read-only, never labelled with
   a guess. No sprite beside the record (unproven edge).
6. **Replace or import graphics.** Graphics -> `graphics list` / `show`
   (`cli.py:194-222`) -> export an indexed PNG (`graphics export`,
   `cli.py:223`) -> edit externally -> import, validating index count,
   dimensions and container extent -> commit one authored-sprite or appearance
   entry. *Refuse*: containers are packed with no retail slack, so a
   size-changing import needs the growth encoder (roadmap step 6) and is refused
   with that reason until it ships. Map tilesets are read-only today.
7. **Inspect a script and follow references.** Scripts & Text -> a family
   (`event list --family`, `cli.py:151-154`) -> a root -> its body -> forward
   references (`event references`), reverse consumers (`event consumers-of`,
   `cli.py:142-144`) and owners (`event owners-of`, `cli.py:161-162`). Unknown
   handlers show number, address and `semantics unknown`. *Refuse*: the corpus
   is fixed-size, there is no event editor and no authoring verb
   (`cli.py:131-134`); assembly the product cannot do is displayed read-only.
8. **Inspect an item and follow text and script relationships.** item record
   (`0x083BD2F8`, 83 records of 52 bytes, `config/roms.yaml`) -> `event
   for-owner item:NNNN` -> script halfword and text indices -> the on-screen
   name comes from the text index the engine draws. *Refuse*: item fields are
   not editable (`items-and-inventory` is known but unsupported) and the
   shop-to-item edge does not exist. Inspect and follow only.
9. **Find a known ROM address.** `Go to address` accepts image address or file
   offset; the ROM surface opens centred with the range's classification,
   confidence and provenance (`atlas addr`, `cli.py:290`). *Refuse*: the surface
   never hides classification behind raw bytes; an address with no owner says so.
10. **Search raw bytes or a pattern.** One search field, semantic and raw.
    Semantic hits come from `atlas.py:626`; hex and pattern hits are `NEW` and
    list the offset plus the range's classification. *Refuse*: a hit is never
    presented as an editable owner.
11. **Jump from a semantic object to its backing bytes.** `Open bytes` in
    Technical details, enabled only when the extent is proven. Object extents
    exist for atlas objects (`tools/webfoot/atlas.py:288-293`) and for the
    journal; for a domain without one this is `NEW` (roadmap step 3) and the
    button is disabled with that reason. *Refuse*: an extent is never guessed.
12. **Make a raw byte edit safely.** Section 9: owner namespace, claimed bytes
    refused, confirmation naming the range and the owner, fixed length only.
    *Carried by* `write.py:295-350` plus `NEW` checks. *Refuse*: a write into
    bytes a declared structure owns, and a write that resizes.
13. **See exactly what bytes the project changed.** One journal list covering
    every edit kind (owner, reason, offset, old to new, size), plus, after a
    build, the manifest's own change list (`write.py:1050-1061`, `:1147`) and
    the changed-byte count (`:1024`). The list is split into "in the project,
    not yet built" and "built, with output sha256". *Refuse*: the journal is
    never labelled as proof that an image changed; only a build and its manifest
    are that.
14. **Undo and redo across semantic and raw edits.** One stack, one timeline,
    ordered by moment of edit rather than by surface. See section 11 for the
    model and its two hard cases.
15. **Validate.** Action bar -> project validation against the base ROM, writing
    nothing (`cli.py:553-556`); findings grouped by destination and each naming
    the object that owns it; refusals state overlap, resize or wrong base
    (`write.py:1206-1233`, `:986-989`). *Refuse*: Validate is never presented as
    proof of how the ROM behaves; it proves the plan applies to that base.
16. **Build.** Action bar -> an output path that must not exist (`cli.py:560`)
    -> a new image plus a manifest; report output sha256, size and changed-byte
    count (`build.py:1408`, `write.py:1329`, `:1290`). *Refuse*: no in-place
    save, no overwrite, no build from an unvalidated project, and no build while
    the project has unsaved edits (section 11).
17. **Play.** Action bar `Run`, offered after a build, launching mGBA on the
    built image with the image path and digest shown (`workbench/launcher.py`).
    Where the run must produce governed evidence, the route is the tracked
    runtime capture pipeline, never this button. *Refuse*: the button never
    claims runtime proof.
18. **Export a BPS patch.** Action bar -> requires a verified source
    (`tools/webfoot/patch.py:151`) -> the patch is built through the same build
    path (`:303`, `cli.py:584-588`) -> verified before it is offered (`:390`).
    *Refuse*: a patch is never exported for an image the project does not
    currently produce.
19. **Encounter a partially understood structure without being misled.** Every
    list row carries its support state and its evidence basis in words; an
    unidentified range is never rendered as free space; and no affordance
    appears that the state does not support (no edit control, no link, no
    `New`). Section 12 fixes the vocabulary.
20. **Recover from an invalid or unsupported edit.** A refusal names the object,
    the reason and the next action; validation failure leaves the journal
    intact and writes nothing (`write.py:1151` raises before any byte moves);
    the user undoes or edits the entry and validates again. A changed base is
    reported as a changed base (`write.py:986-989`). *Refuse*: no force-apply
    switch, no accept-anything switch, no silent partial write.

**Workflow steps blocked on missing core authority**, which is where the
product must say "not yet" rather than behave badly:

| Step | Missing authority | What the user can do meanwhile |
| --- | --- | --- |
| 2 for LOGII and LOG1 | no declared grid or map-entry table for those profiles | ROM surface and read-only inspection |
| 3 for three of four object families | the families are not modelled | inspect the modelled family; treat the rest as unknown structures |
| 4 for a runtime-computed text index | no proven dialog-to-text edge | read the dialog; edit only text with a proven index |
| 5 for unrecovered fields | 266 handler meanings unknown | edit named fields; other bytes only through the ROM surface as a named raw edit |
| 6 for a size-changing payload | no growth-capable container encoder | import same-size payloads; growth in roadmap step 6 |
| 8 for item fields | item records are known but unsupported | follow the proven edges read-only |
| 11 for a domain without an extent | no owner-bearing range index yet | use atlas objects; otherwise address-first |
| 14 across a structural relocation | no offset-rebasing authority | undo the structural edit first (section 11) |
| 16 and 18 for LOGII and LOG1 beyond text | those cells are unmapped | builds remain byte-exact no-ops for unmodelled domains |
| 19 for save data and audio | no format at all | nothing yet; no affordance |

## 11. Edit, save and undo model

**One authoritative model.** Three things, one owner each, all outside the
widgets so a test can drive them without a window.

```text
EditJournal   the ordered list of committed edits and their byte effects
UndoStack     one QUndoStack over the journal, the only history in the app
Session       selection, cursors, revisions and the derived dirty state
```

**Edit kinds.**

| Kind | Owner it carries | Effect |
| --- | --- | --- |
| Semantic | the record identity, e.g. `enemy:0034` | replaces a field's bytes through the domain's own setter |
| Raw | `raw:0x08711274`, with a parent identity when inside a known record | replaces bytes directly |
| Asset | the asset identity, e.g. `sprite:0149/import-1` | introduces referenced content and the record change that uses it |
| Structural | the record identity | resizes or relocates, producing a relocation plan and reference rewrites |

**Immediately represented, persisted on save.** An edit enters the in-memory
project model and the journal at once, so Validate and Build see it and the
inspector can show its effect. It reaches disk only on Save, which is one atomic
document write (`tools/webfoot/project/atomic.py`, `replace_document`). Imported
assets are content-addressed files beside the project; an unreferenced file is
ignored by load and removed only by an explicit project cleanup, so undo never
has to delete a file and determinism still depends only on referenced content.

**Build requires a saved project.** Build and Export refuse while the project
has unsaved edits and offer `Save and build`, which saves atomically and then
builds. The reason is the determinism guarantee: the built image must be
reproducible from the tracked project files, and a build from unsaved state is
not reproducible. The cost is one extra write per build, stated here rather than
hidden. Raw edits participate: they are project state and must be saved before a
build, exactly like a semantic edit.

**Dirty state is derived, not flagged.** Three counters and the journal position
produce three user-visible facts: `saved` (project revision equals the saved
revision), `modified` (an edit exists that Save has not written), `built`
(the current revision has been built and validated). The beta's counter model is
the right shape (`workbench/session.py:100-102`, `:169-175`) and is carried
forward; the beta's four separate undo stacks are not.

**Undo semantics.**

1. One linear timeline over every edit kind, ordered by the moment of edit.
2. An entry stores the inverse bytes (`ByteChange.old`, `write.py:298-300`);
   a structural entry additionally stores its relocation plan, because it moves
   the offsets a raw entry addresses.
3. **Crossing a structural edit.** If a structural edit moved the offsets a
   later raw entry addresses, undoing the raw entry is refused, naming the
   structural entry to undo first. The re-projection is mechanical when the
   entry lies wholly inside a relocated record and ambiguous otherwise; an
   ambiguous case refuses rather than improvises.
4. **Undo never rewrites an image.** Undo changes the project; an image already
   built keeps its bytes, and the UI says so where the build is reported
   (`Undo affects the project, not images already built`).
5. **Undo reveals what it changes.** Crossing surfaces moves the view to the
   affected resource, so a Graphics view never silently undoes a map paint.
6. **The dirty flag is the stack index**, not a boolean, so undoing back to the
   saved point restores `saved` exactly.

**Conflict detection between a semantic edit and a raw edit inside one record.**

| Moment | Rule |
| --- | --- |
| Commit | A raw write into bytes a declared structure claims is refused at the point of the write and offered as a semantic edit. The query consults three sources and must consult all three: the journal (a pending edit with no word in the SDK), the range index, and the atlas objects and declared table extents. This is the primary prevention and it exists nowhere today. |
| After a structural edit | Every raw entry whose extent moved is re-projected. A re-projection that is unambiguous is applied silently; an ambiguous one marks the entry `Conflict` and it must be undone or converted into a named override inside the object. |
| After a build that relocated a structure | A raw entry addresses canonical file offsets and is validated against the canonical bytes (`tools/webfoot/write.py:1203-1235`), so it never silently re-targets. A build can still move a structure out from under it: `../journeys/dialogue-editing.md:67-73` measures a container recompressed 1,076 bytes larger and placed in generated expansion. When a build's relocation provenance moves a structure containing a raw entry's range, the entry is marked `Conflict` and names that relocation, and the user has three choices: undo it, re-address it to the relocated copy at the offset the provenance records, or keep it as an explicit edit of bytes the product can no longer show anyone reading them. |
| Build | The last gate is the plan's own check: two owners writing one byte is an error (`tools/webfoot/write.py:187-190`, `:1232-1233`), and two changes writing one field is a contradiction in the authored image (`tools/webfoot/authored_image.py:550-554`). The product must never rely on either as the first check. |

The user-facing form of a conflict is one dialog naming both entries, their
offsets and three choices: undo the raw change and keep the semantic edit
(recommended), keep both when the re-projected extents are provably disjoint,
or convert the raw change into a named override inside the object so one owner
still owns every byte.

**Close with unsaved changes.** The shell asks, and the question names the
counts: how many edits, in which destinations, over how many byte ranges. The
choices are `Save`, `Discard` and `Cancel`. Discard is the destructive step and
names what will be replaced (the project's authored files and the edits they
carry).

**Immutable and atomic, restated.** The canonical ROM is opened read-only, an
output that resolves to the source is refused
(`tools/webfoot/authored_image.py:111`), a generated image is always a new file
in an ignored output directory, and no partial project write exists.

**Generated and relocated data is not authored state.** Anchors, pointer graphs,
relocation and free space never appear in the authored files
(`../project-format.md:391-393`). They are build-time effects recorded in the
plan and the manifest, they are not undoable, and an edit invalidates the build
and validation revisions. This is why undo has nothing to do about them.

## 12. Error and support model

**The vocabulary.** Four support states and two facts that are not support
states. Each is one short sentence, and the exact census token is quoted only in
Technical details.

| User word | One sentence | Census token it stands for |
| --- | --- | --- |
| Editable | You can change this. | `FULLY_EDITABLE` |
| Editable with limits | You can change this, and this stays fixed: N. | `PARTIALLY_EDITABLE` |
| Read-only | The product can show you this and cannot change it. | `SEMANTIC_READ_ONLY` |
| Not supported yet | It is a real thing in the game and there is no model for it yet. | `KNOWN_BUT_UNSUPPORTED` |
| Not mapped | This exists and its meaning is not established yet. | `UNKNOWN_UNMAPPED` |
| Not in this game | The evidence says this does not exist in this title. Reserved for the census vocabulary: no current row emits it, and the product shows it rather than a blank if one ever does. | `N_A` |

The last three transient states are results, never decoration before an attempt.

| Transient | When | Ends |
| --- | --- | --- |
| Refused | after a refused write or a failed Validate | when the offending entry is undone or edited |
| Unsafe | on a write into bytes another structure claims | when the selection leaves those bytes |
| Conflicting | when two entries intersect in one extent | when one is undone or converted |

**Where each appears.** The support state appears in exactly three places: the
trailing column of a record list (glyph plus tooltip plus accessible name), the
inspector chip for the selection, and the `Coverage` view. It never colours a
canvas, a toolbar, a navigation label or a background. A project-level banner is
reserved for project-level facts only: the profile declares no tables, the base
image changed under the project, or the project is read-only.

**Escalation.** `Technical details` is the last section of the inspector,
collapsed by default, keyboard reachable, and holds the semantic identity, the
image address and file offset, the extent, the range classification and its
confidence, the owner(s), the SDK entry point that produced the value, and the
evidence reference. It quotes the exact vocabulary: the six census coverage
states and the two bases (`MEASURED`, `NOT_INVESTIGATED`), the engine knowledge
levels, the atlas confidence levels (`tools/webfoot/atlas.py:45-60`) and the
atlas's non-semantic shape tokens (`:85-103`), including `PADDING_CANDIDATE` and
`VERIFIED_FREE`.

**Wording rules.**

1. Never call a read-only thing supported. Read-only means identified and not
   writable; raw hex does not count as support for it.
2. Never imply an unclassified range is free or safe. `PADDING_CANDIDATE` is not
   free, and `VERIFIED_FREE` is one 256-byte window.
3. Never show `Not mapped` without an action, and where the basis is
   `NOT_INVESTIGATED` add that this describes our evidence, not the game.
4. Never render an evidence level as a percentage and never average two levels;
   confidence in the atlas deliberately has no arithmetic.
5. A refusal reads `Refused` plus the reason. Never `Error` alone.
6. Never promise behaviour from a plan or a built image. Only a governed runtime
   capture proves behaviour.

**Accessibility.** Every state is a word plus a glyph plus an accessible name;
colour is decoration. The three state colours in use differ in lightness as well
as hue, and the glyphs are already centralised in the beta's theme
(`tools/webfoot/workbench/theme.py:382-427`), which the new application keeps.
The test is mechanical: remove colour and the state must still be readable.

## 13. Visual direction

The beta Workbench is reference, not foundation: it is an engineering surface,
not the shipping product, and it is not reskinned.

**Measured facts about the beta** (read from `tools/webfoot/workbench/theme.py`
and `widgets.py`, plus an offscreen Qt measurement; no live window was captured,
so no claim here is a claim about how the shipped window looks).

- One authored palette, derived from a Buu's Fury sprite rather than from a
  stock theme, with a four-step pink ladder as its lightness ramp and no
  conventional desktop blue (`theme.py:22-25`, `:63-91`).
- One spacing scale and five named control heights: `SPACE_XS..XL` 2/4/8/12/16,
  `ROW_HEIGHT 20`, `CONTROL_HEIGHT 24`, `TOOLBAR_HEIGHT 28`,
  `PANEL_HEADER_HEIGHT 22`, `STATUS_HEIGHT 22` (`theme.py:272-294`).
- Two measured facts worth carrying correctly rather than as defects:
  `CONTROL_HEIGHT` is declared 24 while the stylesheet derives a control's height
  from the button metrics, so a rendered button, input and combo measure 22 px;
  and several surfaces put monospace on body text, which is what makes a tool
  read as a hex editor by accident. The first is a constant to keep in step with
  what is rendered, not a bug to repair by overriding the stylesheet: a control
  that sets its own smaller minimum is the two-pixel drift the constant exists to
  prevent (`theme.py:286-290`).
- Shared chrome already exists and is worth keeping as a vocabulary:
  `PanelHeader`, `DisclosureRow`, `AlignedFieldTable`, `TechnicalLabel`,
  `StateChip`, `ToolStrip`, `ScrollPane` (`widgets.py:43`, `:161`, `:233`,
  `:259`, `:274`, `:345`, `:526`).

**Kept:** the palette's provenance and role vocabulary; the lightness ladder;
small radii and 1 px separators; the spacing and height constants, with the
declared control height and the rendered height kept in step rather than
overridden; glyph plus brightness plus word for every state; one forced
stylesheet applied once from the entry point; the shared chrome vocabulary.

**Changed:** density is stated as a target (20 px semantic record rows, 18 px
hex rows, 22 px group headers, two density levels and no third); monospace is
restricted to fixed-width technical values; a four-step type scale is named once
instead of per-widget deltas; and the five interaction states get five distinct
mechanisms (inactive, hover, selected, keyboard focus as an outer ring that can
coexist with selection, disabled) rather than three nearby pinks.

**Discarded:** a tab bar as a surface switcher; per-editor undo stacks; a
duplicate status line inside an editor; and any decoration that is not carrying
information.

**The ROM surface inside the same product.** It differs in exactly four ways:
monospace as the primary type, a fixed 16-byte grid instead of a columnar table,
an address gutter as a permanent label rather than a disclosed one, and no
thumbnail browser. It shares chrome, borders, chips, glyphs, the disclosure row,
the inspector, the history and the undo stack. Identity is carried by one extra
colour role, never by a second theme.

**Allowed:** domain-specific layouts, because a canvas, a dense table, a tree
with a text pane, a thumbnail grid and a byte grid genuinely differ. Each is
allowed when it uses the shared chrome, takes every measurement from the theme,
declares its mode's purpose, and survives a narrow window without a horizontal
scrollbar.

**Forbidden:** large-radius cards, hero headers, dashboard or mobile patterns,
novelty UI, decorative animation, animated hover fills or pulsing dirty
indicators, a second accent hue for a new state, an icon-only control without a
tooltip, and any colour literal outside the theme module.

## 14. Application architecture

**Where the code lives.** A new package `tools/dragonbyte/`, not inside
`tools/webfoot/`. The purity gate pins the shipping package to `tools/webfoot`
and requires every tracked file under it to be Python or YAML
(`tools/quality/architecture.py:41`, `:122-138`), so a Qt application inside it
would change what "the shipping package" means. Adding the new root to
`ALLOWED_ROOTS` (`:45-53`) plus one test asserting the new package imports no Qt
at module level is the whole gate consequence, and it is scheduled in roadmap
step 1.

**Boundaries.**

| Boundary | Owns | Does not own | SDK behind it | Headless testable | Exists today |
| --- | --- | --- | --- | --- | --- |
| Application shell | window, region layout, the destination registry, the single wiring point, the unsaved-work policy | any ROM semantics, any edit state | none | no | new (shape proven by `workbench/app.py`) |
| Session and project state | selection, per-destination cursors, revisions, derived dirty state, unsaved-edit count | edits, bytes, file I/O | `project/model.py` | yes | shape exists (`workbench/session.py:80`, headless) |
| Command and undo layer | the journal, one undo stack, edit kinds, conflict detection, the saved revision point | rendering | `write.py` (`ByteChange`, `WritePlan`) | yes | new |
| Semantic editors | one per destination and mode: the list, the canvas, the fields, the validation calls | ROM semantics, byte arithmetic | the domain modules | partly (models yes, widgets no) | new; logic exists in `webfoot` domain modules |
| Raw byte authority | the `raw:` owner namespace, the claimed-bytes check, the write confirmation, the address model | the SDK's plan validation | `write.py`, `binary.py` | yes | new |
| Range and owner index | range to owners, owner to ranges, honest `UNKNOWN`, table extents | classification (the atlas owns it) | `atlas.py` (`CoverageMap`, objects, references) | yes | partly (`CoverageMap` exists, owners do not) |
| Search | one query over semantic search and raw bytes, result ranking, hit to resource | the search implementations | `atlas.py:626` plus a new byte scan | yes | partly |
| Validation | running it, grouping findings, naming the owning object | the rules | `build.py:1295` | yes | yes |
| Build, play, export | action bar actions, output identity, reporting sha256 and changed bytes | the build, the patch codec | `build.py:1408`, `patch.py:303`, `workbench/launcher.py` | yes for build and export; no for launch | mostly yes |
| Settings | window geometry, last project, recent files, disclosure defaults | anything the project owns | none | yes | shape exists (`workbench/settings.py`) |
| Navigation and history | the back/forward stack, recents, cross-link dispatch | data | none | yes | new |

**Module layout.** New package `tools/dragonbyte/`, beside the SDK so the layer
law still holds. Everything except the destination modules is importable with no
window open.

```text
tools/dragonbyte/__init__.py       package marker
tools/dragonbyte/__main__.py       entry point
tools/dragonbyte/session.py        state, cursors, revisions, dirty derivation
tools/dragonbyte/journal.py        edit kinds, the journal, the one undo stack, history
tools/dragonbyte/index.py          range to owner, owner to range, extents, references
tools/dragonbyte/rawbytes.py       the one owner-bearing free byte edit
tools/dragonbyte/search.py         one query over semantic search and raw bytes
tools/dragonbyte/validate.py       validate, build and export orchestration
tools/dragonbyte/launch.py         emulator detection and launch
tools/dragonbyte/settings.py       per-user machine facts, outside the repo
tools/dragonbyte/diagnostics.py    one catch surface: SDK exception family to one message
tools/dragonbyte/shell.py          window, regions, destination registry, single wiring point
tools/dragonbyte/dest_maps.py      Maps read-model and change production
tools/dragonbyte/dest_entities.py  Entities
tools/dragonbyte/dest_text.py      Scripts & Text
tools/dragonbyte/dest_graphics.py  Graphics
tools/dragonbyte/dest_data.py      Data tables and coverage
```

Two import rules are mechanical and tested, following the precedent in
`tests/unit/test_architecture.py`:

1. Nothing under `tools/webfoot/` imports `tools/dragonbyte`. The SDK does not
   depend on the application.
2. The application never imports `tools/webfoot.workbench`. The beta desktop
   package is not an application dependency; every behaviour it needs is either
   in the SDK or extracted into the package above.

**Extraction boundaries** against the beta, module by module.

| Beta | Verdict |
| --- | --- |
| `workbench/session.py` | The model is reused: which ROM, which profile, which project, the derived read-only domains, the revision counters and the derived currentness. It is already headless. Its per-editor staged-work registry is **deleted, not ported**: under one journal, two answers to "is there unwritten work" is exactly the defect the beta already had to fix once. Its selection fields become per-destination cursors. |
| `workbench/settings.py` | Extracted as a settings service. It is 64 lines and one Qt import (`QStandardPaths`, `settings.py:21`) used only to find the config directory; the existing environment override stays as the documented headless escape hatch and the shell supplies the Qt path. |
| `workbench/launcher.py` | The behaviour is about 25 lines: emulator discovery, the initial path, and a fire-and-forget launch (`launcher.py:37`, `:46`, `:219`). That becomes a plain service; the tab is not carried. |
| `workbench/theme.py`, `widgets.py` | Presentation. The palette, spacing scale, control heights and glyph table are carried as values; the chrome classes are rebuilt in the new package rather than imported, because their stylesheet and constructor signatures are tuned to the beta's layout. `PanelHeader`, `StateChip`, `ToolStrip`, `ScrollPane` and `CheckBox` carry no domain rule and their behaviour is the pattern to copy. |
| `workbench/app.py` | Not carried. The shell is rewritten, keeping only the proven shape: one window, one strip, one centre area, one inspector, one status line, one wiring point, one session, no globals. |
| `workbench/map_browser_tab.py` (8,282 lines), `warp_tab.py` (3,271), `graphics_tab.py`, `map_tab.py`, `inspector.py`, `atlas_browser.py` | Not carried. Their Qt-free collaborators (`map_view.py`, `map_authoring.py`, `scene.py`, `map_transitions.py`, `placement_events.py`) are the reusable layer, and `workbench/scene.py` is the worked precedent for a domain model with no Qt in it. Every one of the four undo stacks disappears into the single journal. |
| `workbench/*_dialog.py` | Not carried as widgets. The operations they perform become semantic-editor actions. |
| Everything else under `tools/webfoot/` | Used as-is. It is headless and layered (`../architecture.md:32-53`). |

**What the SDK must grow, and where.**

| Need | Shape | Invariant it must not break |
| --- | --- | --- |
| A raw owner, typed | The product mints `raw:<image address>` and passes it through; `write.py` may gain the raw owner form and its validation, or keep the string | Every emitted change still names an owner and the manifest still answers which edit changed these bytes (`write.py:302-304`); nothing weakens the non-empty-owner refusal (`:324-325`) |
| A claimed-bytes query | The range index (new module) answering owners for a range and ranges for an owner, built over the atlas the way the atlas's own coverage statistics are | Ownership stays honest: an unowned range is `UNKNOWN`, never free (census summary line 84). Coverage stays an exact-once partition (`atlas.py:154`, `validate()` `:167-195`): the index is derived, never a second partition, and confidence levels are never averaged |
| Raw byte search | A byte scanner beside `atlas.search_text` (`atlas.py:626`), returning per hit the offset, the coverage classification, the owners and the references that intersect it, and for a hit inside a compressed container both the container offset and the offset inside the decoded stream | Codecs still do no I/O (`../architecture.md:69-71`); a hit is never reported as a pointer or as an owner |
| A growth-capable container encoder | One reusable growth operation: allocate, re-encode, rewrite references, emit relocation provenance, generalised from the compressed dialogue relayout path that already does this for one domain | Determinism and one plan per build (`../project-format.md:318-334`, `:382-387`); every change still names an owner; a stored rewrite is not enough, because it exceeds the original allocation in every measured sprite container |
| Undo in core | Not required. The journal lives in the product and drives the same `plan_changes` the CLI uses | One plan per build; no second write path |

## 15. SDK and beta extraction boundaries

1. **The SDK stays the only authority.** No format constant, record stride,
   bitfield or address literal appears in the application. If a widget needs a
   ROM value it cannot get, the answer is a public SDK function, not a local
   computation (`../workbench-architecture.md:34-35`).
2. **The CLI stays the second entry point, not a dependency.** The application
   calls public Python APIs; it never shells out and parses stdout
   (`../workbench-architecture.md:37-38`).
3. **Behaviour is extracted, widgets are not.** Anything worth keeping from the
   beta is either already in the SDK or becomes a plain module in
   `tools/dragonbyte/`.
4. **No second project format.** The GUI and the CLI read and write the same
   authored project, and a build from either is byte-identical.
5. **The beta keeps working while the new product is built.** This document
   neither freezes nor deletes the Workbench; the owner decision that it is not
   the shipping product is already recorded in the release review. Two tracked
   sentences still name it as the product (`../workbench-architecture.md:3` and
   the journeys under `../journeys/`), and the roadmap records both as
   documentation owed when the new application ships.
6. **The registry is not touched by this document.** `src/data/capabilities.json`
   stays at 24 of 24 until a capability is actually shipped.
7. **The import direction is one way, and tested.** Nothing under
   `tools/webfoot/` imports `tools/dragonbyte`, and the application never
   imports `tools/webfoot.workbench`. Both directions get a test with a positive
   and a negative control, in the shape `tests/unit/test_architecture.py`
   already uses.

## 16. First vertical slice

The slice proves four things and nothing else: the shell, unified navigation,
the state and undo model, and the semantic-to-raw bridge. It uses only proven
relationships.

**Steps.**

1. Open the canonical Buu's Fury ROM; identify by sha256; open or extract a
   project.
2. The shell starts on Maps. Select a map; the canvas renders it.
3. Switch to `Objects`. Select a placement in the modelled family. The three
   unmodelled families appear as sibling rows labelled as not modelled, with
   their pointer slot and stride and no invented names.
4. The inspector shows the three identities, the support state, and the
   collapsed Technical details with classification, confidence and provenance.
5. Follow the proven edge placement -> behaviour -> script with one click; then
   a dialog -> text edge where one exists.
6. Return with `Alt+Left` twice; the view, mode, selection and disclosure state
   are as they were.
7. `Open bytes` on the script resource opens the ROM surface at its extent; the
   ownership strip shows the owner that the range index reports.
8. Attempt a raw write inside that owned range: it is refused, names the owner
   and offers `Go to owner`.
9. Perform a raw write in a range with no declared owner: it is accepted, and
   the journal gains one entry owned by `raw:<image address>`.
10. `Ctrl+Z` removes it and the bytes revert; `Ctrl+Shift+Z` restores it. The
    stack index drives the dirty state: after undoing back to the saved point
    the title reads `saved` again.
11. Edit one proven semantic field (a placement position) and confirm the
    changed bytes appear in the ROM surface's changed overlay.
12. `Validate`, then `Build` (which saves first), then `Run`, then
    `Export patch`. These are shipped services newly reachable from the action
    bar; they are acceptance steps, not new work.

**Acceptance criteria**, all objective.

1. `webfoot identify` on the canonical image returns
   `buus_fury_usa_rev0_01c1707f` before and after the walkthrough, and the four
   configured digests in `config/roms.yaml` are unchanged.
2. A headless test with no window drives the journal: commit a semantic edit and
   a raw edit, undo and redo both, and assert the resulting plan's owners and
   `changed_byte_count` (`tools/webfoot/write.py:1024`).
3. A raw write into owned bytes is refused, the refusal text names the owner
   exactly once, and no `ByteChange` is created.
4. The shell exposes six strip entries with `Ctrl+1`..`Ctrl+6`, each asserted by
   accessible name rather than by pixels.
5. Back and Forward restore destination, mode, identity, sub-selection and
   disclosure state, asserted from session state.
6. The built image differs from the canonical image in exactly the manifest's
   change set: set equality of offsets, not a count.
7. `patch verify` on the exported patch reproduces the built image byte for
   byte, and the patch applies to the canonical image.
8. The failed paths are exercised too: the unmodelled-family row offers no edit,
   the disabled `Open bytes` states its reason, and a size-changing import is
   refused with the encoder reason.
9. The headless boundary is asserted both ways: importing the model modules
   (`session`, `journal`, `index`, `rawbytes`) succeeds with no `QApplication`,
   and no module under `tools/webfoot/` imports the application package.
10. `Go to address` accepts an image address and a file offset, converts between
    them, and says which spelling it read.
11. `verify_emitted_image` returns exactly the offset set the journal produced,
    asserted as a set rather than a count, and a save whose destination hashes
    to the canonical image is refused (`tools/webfoot/authored_image.py:111`),
    asserted rather than assumed.
12. Reverting every step of an edit before it is committed leaves no effective
    journal entry, and the resulting plan reports itself a no-op
    (`tools/webfoot/write.py:1020`).

**ROM-gated proof.** The slice builds a real image from the canonical ROM
(digest `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`),
verifies the digest before and after, compares the built image against the
canonical image, verifies the patch, and, for the runtime half, follows the
tracked capture pipeline at `../skills/mgba-runtime.md` with the generated
image's exact digest. Generated images live under an ignored output directory
and are never committed.

**Deliberately not in the slice:** growth and insertion (no growth-capable
encoder yet), map layout painting, graphics import, the data tables, LOGII and
LOG1 domains, search, and the coverage view. Each has a roadmap step; none is
needed to prove the four properties.

## 17. V1.0 scope

**Required.**

1. The shell: five destinations, the summoned ROM surface, the shared
   inspector, one navigation history, the action bar.
2. One session, one journal and one undo stack over semantic and raw edits,
   headless-testable.
3. Raw byte authority: the raw owner namespace, the claimed-bytes check, the
   confirmation, the journal entry.
4. A range-to-owner index that can answer for the whole image and can say
   `UNKNOWN`.
5. The integrated hex editor: address navigation, byte selection, canonical and
   current views, changed-byte overlay, and raw write.
6. Raw byte search beside semantic search.
7. Surfaces over the SDK models that already exist and are already verified:
   enemy stat records, character base stats, map-entry headers, plus the
   coverage view that reports honestly.
8. The existing build, play and patch services reachable from the action bar,
   with output identity reported.
9. Validation grouped by destination and naming the owning object.

**Deliberately deferred.**

- Map graphics below the chunk level and tileset authoring (read-only today).
- Portraits, UI and HUD graphics, fonts and glyph metrics.
- Item field editing, shops and scenarios (known but unsupported).
- A dedicated editor for compiler-embedded strings, the colour lookup block and
  debug debris (the census calls these not product-worthy).
- Side-by-side comparison of two resources (the section 5 concession).
- Any docking or layout-profile system.

**Research first, and never silently promoted.** Four items are the V1.0-relevant
research dependencies, each with what it unblocks and what it does not block.
Section 19 adds two further evidence items that are correctness guards rather
than dependencies.

| Research item | Unblocks | Does not block |
| --- | --- | --- |
| The three unmodelled per-area object families | an honest Entities list of every family, and any editor over them | everything else; the modelled family is enough for the slice |
| The save format, including whether the expansion path preserves it | any save-domain support and a certified save round-trip after a build | building and playing; the product must state that it does not certify saves |
| Audio: the engine, tables and sequence or sample data | any audio surface | nothing in V1.0; the census recommends no audio editor before the format exists |
| The game meaning of the 266 script handlers | semantic script editing beyond the proven handlers | reading scripts, following references and editing text |

**The one growth dependency, stated plainly.** A size-changing payload import
requires a growth-capable container encoder. V1.0 requires it for the sprite and
text container paths; until it ships, the importer refuses a size-changing import
with that reason and the census's own words are quoted in the refusal. It is a
V1.0 gap, not a silent one.

## 18. Post-1.0 scope

- Map graphics below the chunk level: chunk-level file authoring, tileset and
  screen-entry editing, once the graphics chain is modelled.
- Portraits, UI, HUD and font authoring, as the census recommends (rank 10).
- Item and shop surfaces if and when those rows move.
- LOGII and LOG1 domains as their research lands, per profile, never assumed
  from Buu's Fury.
- The three unmodelled object families, as editors, once their records are
  recovered.
- A save-domain surface, if the format is recovered and the expansion
  interaction is certified.
- Side-by-side comparison, if real sessions show it is needed (section 5).

## 19. Research dependencies

The bounded list, each a ticket rather than a product design. None of them
becomes a V1.0 blocker, and this document does not create an open-ended queue.
Items 1 to 4 are the V1.0-relevant research dependencies; items 5 and 6 are
evidence corrections that no step waits on.

1. The three unmodelled per-area object arrays and their record families
   (the four-array model is `INFERRED` and disputed; the census does not pick a
   reading).
2. The save format and whether the expansion path preserves it.
3. Audio, end to end.
4. The 266 script native handlers' game meaning.
5. The two drift-affected dialogue rows, which may be conservative after the
   dialogue token merge
   (`../research/ROM_EDITOR_COVERAGE_LEDGER.md` baseline note).
6. Two open disagreements the product must not resolve by choosing: the portrait
   pointer array (`0x086F393C` against `0x086F395C`) and the background palette
   (`0x080701B0` against `0x0805632C`). Until they are resolved the product
   states neither address.

The four claims the census already refuted against the bytes stay refuted; the
product cites none of them.

## 20. Implementation sequence

The ordered roadmap, its acceptance proof per step and its dependency chain live
in [`DRAGONBYTE_Z_IMPLEMENTATION_ROADMAP.md`](DRAGONBYTE_Z_IMPLEMENTATION_ROADMAP.md).
Nine steps, one ticket each, from the foundation through the raw byte authority,
the range index, the ROM surface, the existing data tables, the four semantic
destinations, container growth and the release surface, to a V1.0 whose promise
is exactly section 17.

## Appendix A: how the census changed this design

1. The census's first-class raw and semantic requirement produced the ROM
   destination and section 9 rather than an advanced dialog.
2. Zero fully editable systems and 20 of 120 writable cells produced the four
   support states and the rule that a coverage claim is never shown without its
   per-title table.
3. One of four object families modelled produced the not-modelled sibling rows
   and forbade any array-shaped presentation of the other three.
4. No save format and no audio produced the absence of both surfaces and the
   `Coverage` view that says so.
5. 266 unknown handlers produced the honest handler display and the refusal to
   invent mnemonics.
6. The five unproven edges produced the explicit forbidden-edge list and the
   `Relationship not modelled` rule.
7. The `V1.0 ESSENTIAL` recommendations were adopted for arbitrary byte
   authority, the range-to-owner index, raw search, stat-table surfaces and
   map-header surfaces; the growth-capable encoder was scoped to the two
   container paths it gates; and the four research items were kept out of V1.0.
8. The census's `CORE_AUTHORITY_REQUIRED` verdict for arbitrary byte writes was
   refined by measurement: the guard is an owner string
   (`tools/webfoot/write.py:324-325`), so the missing authority is a typed raw
   owner, a claimed-bytes check, an entry point and undo, not a new class alone.

## Appendix B: what this document does not claim

- It does not claim any of it is implemented.
- It does not claim the beta Workbench is correct or complete, only that its
  shapes and its measured constants are evidence.
- It makes no runtime claim: no emulator was run for this design, so every
  statement about game behaviour is quoted from the census and its sources.
- It does not amend the tracked authority. Three amendments are owed instead,
  each owned by a roadmap step: the ROM surface's address-first exception in
  `../desktop-ui.md` (S5), the sentence in `../workbench-architecture.md:3` that
  names the beta as the shipped editor (S9), and the journey documents' mapping
  onto the new destinations (S7).
