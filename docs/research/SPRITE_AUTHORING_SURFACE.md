# The authored-sprite surface: the required design pass

SPRITE-PROJECT-SURFACE-001. This is the design pass
[`docs/desktop-ui.md`](../desktop-ui.md) requires before widget code for a
substantial surface (`:92-106`), and the record of what the surface does and
refuses. The build path it drives is already merged and unchanged by this ticket:
`sprites/sprites.toml` is read by `read_project`, planned by
`sprite_authoring.materialize_authored_sprites`, and emitted by `webfoot build`.
What did not exist is a product entry point that CREATES that document. Before
this ticket the only caller of `write_authored_sprites`
(`tools/webfoot/project/model.py:3434`) anywhere in the tree was a unit test.

## SC1 -- The 10-question design pass

| # | Question | Answer (evidence) |
|---|---|---|
| 1 | User's primary task | Create, review and remove the project's one authored actor-sprite identity: a sprite the image does not contain, its sheet-backed animation slots and frames, and the map actor that draws it. The engine permits exactly one such identity per build, so the task is a project-level one-off, not a per-object editing loop (`project/model.py:2538-2560`). |
| 2 | Primary visual object | The author's own sheet cells at the donor's proven frame rect. The sheet is a truecolour PNG the author drew; the surface shows the frames it will become rather than a path string. Decoding goes through the SDK (`sprite_authoring.read_source_sheet`), and the widget converts to a `QPixmap` only at the presentation boundary (`docs/desktop-ui.md:143-147`). Where no sheet is chosen yet, the donor is shown by its decoded thumbnail from the existing sprite corpus, which the Graphics tab already holds (`graphics_tab.py:740-746`). |
| 3 | Selection and context model | Project-scoped, not selection-scoped: the tab strip states the document's current authorship, and the dialog edits a draft. Nothing new lives in the widget: the open project directory is `Session.project_dir` (`session.py:96`) and the image is `Session.map_image`/`Session.profile`, exactly as the Maps editor's chunk writes use them (`map_browser_tab.py:7669`). |
| 4 | Primary actions | "New authored sprite..." opens the create dialog; "Edit..." reopens it on the committed document; "Remove" deletes it after a confirmation. Each commit calls one SDK function and then the standard pair, `session.project_mutated()` and `projectChanged.emit()` (`docs/workbench-architecture.md:122-124`). |
| 5 | Secondary actions | Undo and Redo of a commit through the tab's existing `QUndoStack` (`graphics_tab.py:312`), matching `PaletteRecolourCommand` (`graphics_tab.py:116-185`), which writes on both `redo()` and `undo()`. The dialog's own secondary action is Cancel, which writes nothing. |
| 6 | Hidden technical information | The engine id (derived, shown read-only), the donor's measured rect/anchor/piece count, the two carried header words whose meaning is unresolved, and every ROM address. `retained_raw` and `data_pointer_raw` are shown read-only as carried values, never as authoring inputs (`project/model.py:2273-2278`). The document path is not shown at all. |
| 7 | Keyboard path | Full tab order through the dialog's fields; Enter accepts through the dialog's default button, Escape cancels; Ctrl+Z and Ctrl+Y on the tab keep working through `createUndoAction` (`graphics_tab.py:582-597`); the strip's buttons are ordinary focusable `QPushButton`s. |
| 8 | Empty, error and disabled states | No ROM open, or no project open: the strip is disabled with the reason stated, as the Graphics tab already does for palette authoring. No authored document: the strip reads "This project authors no new sprite" and only "New" is enabled. A refused draft is a FORM STATE, not an error dialog: the dialog's summary becomes the SDK's own refusal text while the button stays enabled, matching `_StructureDialog` (`map_browser_tab.py:923-938`); pressing Create then raises the same message once, and the dialog stays open. |
| 9 | Expected data volume | One identity, at most 23 animation slots, at most 64 frames per facing per slot (`project/model.py:2139-2140`). A handful of small PNG sheets. No collection and no model/view is needed. |
| 10 | Performance risks | Three decodes, none on a timer: the sheet PNG per animation (bounded by the author's own files), the donor's structure walk for the admissibility probe, and the draft's dry-run plan on Create. Each is a click-scale operation on one sprite, not the 7,390-sprite corpus the browser already batches (`graphics_tab.py:813-856`). Nothing decodes in `paintEvent`. |

## SC2 -- What the surface exposes, and what it refuses

The supported model is the document the build already accepts, and nothing more.
Fields a surface MUST collect, because no legal default exists:

- `donor_sprite_id`: any registry entry, but only some are admissible. The
  donor must decode, name at least one frame, prove ONE frame rect at ONE anchor,
  hold exactly one piece in its first frame, keep that piece 8bpp and unflipped,
  and agree with its own frame box (`sprite_identity.py:952-1019`,
  `:1022-1092`). Measured on the canonical image: 130 of 297 entries admit and
  167 refuse (`docs/research/SPRITE_NEW_COMPOSITION_GUARD.md`). The dialog probes
  the chosen donor through the shipped planner and shows the refusal when it
  refuses.
- one sheet PNG per animation, and `frames` per facing. The sheet is a single row
  of square cells, four facing groups of equal counts, so its width must equal
  `frames * 4 * height` (`sprite_authoring.py:131-137`), and its cell side must
  equal the donor's measured rect exactly (`sprite_identity.py:1105-1126`).
- the actor's `position` and `wander_box`, in map pixels. Both are offered from
  the chosen template's own record and entry - where its actor stands and the box
  its behaviour already walks inside - so the author starts from an actor the
  engine runs rather than from an invented placement.
- `behaviour_template`, one existing object array slot of the SAME map
  (`project/model.py:2304-2313`), which also fixes the actor's map.
- `free_palette_entries`: the author's claim about which object-palette entries
  the artwork may use. The SDK cannot derive it completely and verifies the claim
  instead (`sprite_identity.py:275-281`, `:1206-1215`).

Derived or carried, and therefore read-only in the surface:

- `sprite_id`: exactly one value is addressable, `10 + character_count`, which is
  307 for the canonical image (`sprite_identity.py:881-896`). The dialog displays
  it and never offers a choice.
- `family`: exactly one measured layout, `map-sibling-08017da3`
  (`sprite_attachment.py:214-240`).
- `retained_raw` and `data_pointer_raw`: carried verbatim from the chosen
  template slot's own record, shown read-only. Their meaning is unresolved and
  the build never dereferences them.
- animation slot index: derived by sorting the names (`project/model.py:2459-2467`).

Out of contract, and unavailable rather than faked: arbitrary piece or OAM
composition, piece-count editing, tile-index editing, arbitrary frame geometry,
animation duration or delay authoring, and the direction-slot-to-facing mapping.
The document has no field for any of them (`git grep -n
"tile_index|piece_index" tools/webfoot/project/model.py` finds none), and the
authored frame copies the donor's own geometry byte for byte
(`sprite_identity.py:1262-1271`). The surface states that boundary rather than
offering controls that cannot work.

## SC3 -- The evidence chain for the capability claim

```text
AUTHORED PROJECT RESOURCE   sprites/sprites.toml written through the surface
        -> BUILT ROM RESOURCE     webfoot build, unchanged domain
        -> RUNTIME PROVEN         engine resolved sprite 307 and drew its frames
        -> SHIPPED                reachable from the Graphics tab
```

`docs/research/SPRITE_NEW_RUNTIME.md:17-44` records the engine resolving an
identity the image does not contain (`new_sprite_id=307`, `structure=0x088005B4`),
and `docs/research/SPRITE_NEW_ATTACHMENT_RUNTIME_PARITY.md:10-19` records both
production planners run together in the retail engine, drawing the identity's own
frames across all four facings with a liveness channel that fired
(`:161-165`).

**The runtime observation is evidence for the mechanism, not for this exact
document, and the difference is one word.** The recorded runtime document states
`data_pointer_raw = 142104172`, taken from a NEIGHBOURING sibling slot of map 102,
while the surface carries the chosen template slot's own `+0x0C` word, which is
`142104156`. Map 102's ten sibling records carry ten distinct values 16 bytes
apart, and slots 7, 8 and 9 all draw sprite 69, so the two are equally plausible
and neither is derivable from the field's meaning, which is unresolved. The
surface's choice is the honest one - it carries what the template it was pointed
at carries - and it means the surface's own image is NOT byte-identical to the
image the engine ran.

So the capability is registered at `proof: "application"`, with a ROM-gated build
proof of the surface's own output, and the engine observation stays attached to
the mechanism and the research records. The surface writes the same document in
every other field: `tests/integration/test_sprite_project_surface_rom.py` compares
the two field by field, asserts the one difference, builds the surface's document,
and checks that it authors the same identity and actor while touching exactly the
canonical fields and retail records the runtime case touches.

## SC4 -- What shipped, and the two measurements that shaped it

| Piece | What it is |
| --- | --- |
| `tools/webfoot/sprite_project.py` | the facade: the request a surface collects, the cheap validation, and the ONE write path for the document |
| `tools/webfoot/workbench/sprite_dialog.py` | the dialog that collects a draft and reports the validated document |
| `tools/webfoot/workbench/graphics_tab.py` | the Graphics tab's authored-sprite strip, the commit, and the undo command |
| `tools/webfoot/sprite_identity.py` | a profile-based probe: the addressable id, and one donor's measured envelope |
| `tools/webfoot/sprite_authoring.py` | template resolution and enumeration, carrying the slot's own words and position |

Two measurements decided the design, and both were taken on the canonical image:

1. **A donor probe through the reference document costs about 82 seconds**, because
   naming a donor used to build the whole registry document and its inbound
   census. The probe now reads the profile's declared entry count and one registry
   word, so it answers in **0.000 s** for the id and **0.001 s** for a donor. That
   is what lets a dialog answer while the author is still choosing.
2. **A full plan costs about 239 seconds.** `validate` followed by `apply` costs
   **8 ms** and **7 ms**. So the surface validates every field-level refusal
   cheaply and writes; the plan itself - the palette claim against the decoded
   graphics, the allocation and the relocation census - stays where it already
   lived, in Validate and Build, which report the same refusals with the same text.
   A dialog that blocked for four minutes would be a worse product than the
   hand-written TOML it replaces.

Enumeration (`supported_actor_templates`) reads every map entry and its array: it
returned the image's 24 supported slots in **0.0 s**.

## SC5 -- Validation

- `tests/unit/test_sprite_project_surface.py`: 14 tests, no ROM. The writer is
  product-reachable, an unchanged document is a no-op, an empty one removes the
  file, reopen keeps the semantic identity, a directory that is not a project is
  refused, the actor block carries the template's words and authors the position,
  and the model still refuses a malformed request.
- `tests/unit/test_workbench_sprite_authoring.py`: 13 tests, offscreen Qt, listed
  in `REQUIRED_GUI_MODULES` so CI cannot let it collapse to a skip. The strip's
  disabled states, the create path through the dialog, the revision bump and the
  re-armed project actions, undo and redo, remove and its undo, reopen, editing
  the committed document, an unreadable project, and four refusal paths.
- `tests/integration/test_sprite_project_surface_rom.py`: 12 tests, ROM-gated,
  read-only. The id the surface offers is the one the planner accepts (307 of a
  297-entry registry), an admissible donor's measured envelope, a donor that
  proves several shapes refused, the templates are real slots, the document the
  surface writes reopens with its identity, a repeat write is a no-op, removing
  leaves the project loadable, and four refusals: a cell that is not the donor's
  rect, a sheet that is not there, and a sheet whose dimensions disagree with its
  frames.

Measured with the whole-tree gates, after staging every new file (the gates read
`git ls-files`, so an untracked file is invisible to them): `architecture` 869
files, 0 violations; `public_surface --all` 864 files, 0 findings;
`readability --all` 608 files, 0 hard hits; `public_release` 0 findings;
`site_check` ok. The capability registry, the rendered status and the built page
agree at 22 / 24, and the built page states 92%.

## SC6 -- The visual and interaction review

`docs/desktop-ui.md:215-309` requires the running application, opened images, and
defects recorded and fixed. The captures come from a driver that runs the real
`MainWindow` with `theme.apply_app_theme` exactly as `workbench/__main__.py` does,
opens the canonical image through `Session.open_rom` followed by the shell's own
`_on_rom_opened`, opens a REAL extracted project through the shell's own
`open_project_dialog` (only the file chooser is answered programmatically, because
a person would click it), shows the Graphics editor, then drives the dialog and
the strip's commit, undo and redo, saving what the widgets render with `grab()`.

States captured and inspected: the strip with no authored sprite, the dialog on
open, the dialog ready to create, the dialog refusing a donor, the strip after the
commit, after Undo, and after Redo.

Four defects were found by LOOKING at those images, and fixed:

1. **The strip's three buttons were not on screen.** A long, word-wrapping
   `StateChip` inside the fixed-height `ToolStrip` grew to two lines and laid the
   buttons outside the visible row. The chip now states the state in a few words
   with wrapping off, and the sentence moved to the summary line beneath the strip.
2. **The dialog opened too short** (660x470), putting the sheet preview, the donor
   disclosure and the out-of-contract note below the fold. It now opens at
   760x780, and the body still scrolls.
3. **The wander box defaulted to `0,0,0,0`** while the chosen template's own box is
   measured in its behaviour entry. `ActorTemplate` now carries that box, read at
   the family's declared offset and value width, and the dialog offers it.
4. **The first capture run was not evidence of the application.** It skipped the
   entry point's `theme.apply_app_theme`, so the widgets rendered unstylesheeted
   and showed controls the real application draws differently. The driver now
   replicates the entry point and the captures were retaken.

Confirmed by eye in the final captures: the empty and disabled states; the ready
state with its plan summary; a refused donor quoting the planner's own message
("the donor structure at 0x6A8A2C draws frames of several shapes (32x32, 64x32),
so it proves no single composition shape; choose a donor whose own frames all
occupy one rect") with Create disabled; and the authored state summarising the
identity, engine id, donor, animation slots, actor map and behaviour template with
Undo enabled.

Driven in the running application: create, invalid input (a refused donor, and a
sheet whose dimensions disagree with its frames), Undo and Redo. Covered instead
by the GUI module tests, which drive the same widgets without a display: Remove
and its undo, reopening the surface, editing a committed document, an unreadable
project, and the disabled states. Not applicable to this surface: drag and drop, a
canvas, and switching between staged assets.

One process note, so the captures are not misread: the first successful run reused
a project directory an earlier attempt had already written to, so the dialog
picked up the committed identity and the strip reported three animation slots. The
final captures come from a freshly extracted project and show one.

## SC7 -- The independent review, and what it found

Reviewed at the frozen candidate `6c0d841` by a fresh-context reviewer that did
not implement the change, with the review scope, the evidence document and the
candidate diff. Verdict: **BLOCKED**, three blocking findings. All three held up
under inspection, and the fourth fixed a claim of mine that the tests did not
support.

**B1, the Edit path overwrote the author's own placement.** `_load` called the
template handler unconditionally after loading a committed document, and that
handler reset the position and all four wander-box values to the template's own;
it also cleared the loading guard partway through the load. Fixed: the defaults
apply only to a NEW draft, the guard is no longer touched by the handler, the
spin boxes are filled under `QSignalBlocker`, and a test now commits a document
whose position and box differ from the template's and asserts Edit shows them and
saves them back.

**B2, Undo wrote into whichever project was open.** The command resolved
`session.project_dir` when it ran, so creating a sprite in one project and then
opening another let Undo delete the second project's document. Fixed: the command
captures its project directory and refuses a mismatch with a message, and the
strip retires the whole history when the open project changes. Two tests cover it.

**B3, the `runtime` proof label was not supported.** The reviewer was right twice
over: no test built a document the surface wrote, and when that test was written
the two documents turned out not to be identical (see SC3). Fixed: the record is
`proof: "application"`, the difference is stated in the registry's own limits, and
a ROM-gated test builds the surface's document and checks the authored identity,
the actor and the canonical field set.

**Non-blocking, all fixed anyway.** An inverted wander box passed the surface and
stopped the build, so the surface now validates the box through the planner's own
`WanderBox` and the registry limit text says exactly which fields it refuses. A
no-op commit bumped the project revision, so it now writes nothing, records no
history and leaves the validation and build current. A failed write inside a
command left the history out of step with the disk, so the command now reports the
refusal instead of raising. And a saved donor or template that the open image no
longer offers was silently replaced by the first entry, so the dialog now keeps
what the document says and lets validation refuse it.

**Confirmed by the reviewer as holding:** the probe refactor reads the same word
the planner read, the profile-based probe returns the id `_require_appended_id`
enforces, the template entry bytes are unchanged, no write path reaches the
canonical image, and no ROM-derived artifact is in the diff. The reviewer could
not run the ROM-gated tests (no canonical image in its session) and said so
rather than guessing; those are the commands this ticket ran itself.

**Sign-off: PASS** at `f32bfe7`, on all three blocking findings and all four
non-blocking ones. The reviewer also caught one slip the fix round introduced and
named its exact correction: an edit had deleted the `def` line of
`test_an_empty_draft_is_refused_in_the_summary`, folding that test's body into the
one above it. The line is restored, the test collects under its own name again,
and the two suites re-run at 31 passed. That is the one change made after the
sign-off, on the reviewer's own instruction, and it touches no source.

