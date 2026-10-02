# ARCH_INVENTORY -- Webfoot SDK architecture inventory

**Status:** inventory only; no code changed.
**Scope:** every `.py` file under `tools/webfoot/` -- 49 files, 16,119 lines.
**Method:** every claim below cites a `file:line` actually opened. The import
graph, the cycle analysis and the test-coverage map were built by AST parse of
the tree, not by reading import lines by eye.

---

## 0. Headline

**`cli.py` (1664 lines) does not need decomposition for architectural reasons.
`build.py` (1008 lines) does -- but only for one specific responsibility, not as
a general split.** The detailed evidence is in §7 and §8. Both files are large;
only one of them is large *because two different things live in it*.

The single highest-value finding is in §5 (AUTHOR_NEW ownership): of the ten
TOOLKIT-029..034 concepts, **one and only one is understood nowhere but in
`build.py` -- the authored-materialization control sequence at
`build.py:855-905`**, which decides when to call `materialize_authored_runs`,
when to fall back to `require_materialization_contract`, and how the authored
changes join the merged plan. Everything else in that feature set has a real
domain owner.

---

## 1. Layer map as built (measured, not as documented)

`docs/architecture.md:35-58` declares the intended layering. The measured
static-import graph matches it. Only module-level (`static`) edges are shown;
function-body (`lazy`) edges are listed per module in §2.

```
binary                 (no webfoot imports)              -- layer 0
gba_header, hashing    (no webfoot imports)              -- layer 0
layout        -> binary
profile       -> binary, gba_header, hashing, layout
rom           -> gba_header, hashing, profile
capability    -> profile, rom
write         -> layout, rom
document      -> binary, gba_header, hashing, layout, profile
allocation    -> binary, layout, profile
relocation    -> allocation, binary, document, layout, write
formats/*     -> binary, hashing, profile, rom, capability (map_entry only)
stats/text    -> formats, hashing, profile, rom, write
maps          -> binary, formats, formats.map_entry, hashing, profile, rom, write
graphics      -> binary, formats, profile, rom
entities      -> binary, document, formats, layout, maps
placement_events -> binary, data.*, formats.*, layout, write
scripts       -> binary, data.script_specs, formats.script_vm, rom
project/*     -> formats (model only), project.format
authored_placements -> allocation, formats.map_entry, layout, maps, project.placements
build         -> capability, formats.map_entry, layout, maps, profile, project,
                 rom, stats, text, write
cli           -> analysis.*, build, formats.*, gba_header, layout, maps, profile,
                 project, rom, stats, text, write
__main__      -> cli
```

Direction is downward everywhere. No module below `build` statically imports
`build` or `cli` (§4 A/B).

---

## 2. Per-module inventory

Format: **module** -- lines · responsibility · key symbols · static deps ·
inbound callers · domain · public/internal (by evidence) · verdict.

### Layer 0 -- binary primitives

**`binary.py`** -- 58 · Address arithmetic: `FileOffset` ↔ `GbaRomAddress`, GBA
ROM-window bounds. · `FileOffset(L13)`, `BinaryAddressError(L28)`,
`GbaRomAddress(L33)` · deps: none · inbound: 17 webfoot modules (allocation,
analysis.*, authored_placements, document, entities, formats.map_entry,
formats.placement_links, graphics, layout, maps, placement_events, profile,
relocation, relocation_proof, scripts) · cross-cutting · **PUBLIC** -- imported
directly by 16 test files (`tests/unit/test_binary.py` characterizes it) ·
**LEAVE ALONE.** 58 lines, zero dependencies, universally reused. This is the
correct shape for a bottom primitive.

**`hashing.py`** -- 65 · Streaming SHA-256/MD5/CRC over a file or stream for
exact ROM identity. · `RomHashes(L16)`, `hash_stream(L23)`, `hash_file(L60)` ·
deps: none · inbound: analysis.variation_arrays, document, formats.map_entry,
maps, profile, rom, stats, text · cross-cutting · **PUBLIC**  --
`tests/unit/test_hashing.py` · **LEAVE ALONE.**

**`gba_header.py`** -- 104 · Minimal GBA cartridge-header parse and checksum. ·
`calculate_header_checksum(L22)`, `GbaHeader(L39)`, `parse_gba_header(L100)` ·
deps: none · inbound: cli, document, profile, rom · cross-cutting · **PUBLIC**  --
`tests/unit/test_gba_header.py` · **LEAVE ALONE.**

**`layout.py`** -- 273 · Pure physical layout contracts: anchors, owned regions,
typed references, free regions, relocation eligibility. Explicitly holds no
record-layout knowledge (`layout.py:1`). · `AnchorId(L27)`, `RomRange(L35)`,
`Provenance(L64)`, `OwnedRegion(L79)`, `Anchor(L88)`, `ReferenceClass(L114)`,
`ReferenceEncoding(L120)`, `Reference(L162)`, `FreeRegion(L213)`,
`relocation_eligible(L233)` · deps: binary · inbound: 12 modules · cross-cutting
· **PUBLIC** -- 14 test files · **LEAVE ALONE.** Coherent single concept.

### Layer 1 -- identity and access

**`profile.py`** -- 742 · Data-driven exact ROM profiles: parse
`config/roms.yaml`, validate every declared table shape, and match a hashed
image against exactly one profile. · `VerificationStatus(L72)`,
`MapEntryTableProfile(L79)`, `RecordTableProfile(L86)`, `TextTableProfile(L104)`,
`ScriptProfile(L308)`, `PlacementTypeProfile(L407)`, `ActorSpriteProfile(L417)`,
`RomProfile(L500)`, `ProfileMatch(L613)`, `RomProfileCatalog(L620)` · deps:
binary, gba_header, hashing, layout · inbound: 14 modules · cross-cutting ·
**PUBLIC** -- **36 test files reference it, the most of any module** ·
**LEAVE ALONE.** It is 742 lines because each `_optional_*` parser
(`_optional_text_table(L135)`, `_optional_record_table(L204)`,
`_optional_map_entry_table(L242)`, `_optional_scripts(L325)`,
`_optional_actor_sprites(L434)`, `_optional_placement_types(L470)`) is a
schema validator for one profile section. They are the same responsibility  --
"validate the trusted metadata document" -- repeated per section, not several
responsibilities colocated. Splitting it into six files would fragment one
schema across six places for zero dependency gain. TOOLKIT-005's rule
(semantic layer must not be titled or branched for one game) is respected:
no game name appears in a branch here.

**`rom.py`** -- 73 · Read-only identification control flow: one descriptor,
hash + header, then re-check device/inode/size/mtime. ·
`RomIdentification(L23)`, `identify_rom(L31)` · deps: gba_header, hashing,
profile · inbound: 12 modules · cross-cutting · **PUBLIC**  --
`tests/unit/test_rom_safety.py` · **LEAVE ALONE.**

**`capability.py`** -- 183 · Profile-declared capability gate. Its own docstring
(`capability.py:1-12`) records why it exists: TOOLKIT-005 removed a hard-coded
game-id check from four subsystems and replaced it with this. ·
`Capability(L48)`, `CapabilityError(L65)`, `declared(L76)`,
`packaged_contract(L100)`, `require(L120)` · deps: profile, rom · inbound:
build, entities, formats.map_entry, graphics, maps, scripts, stats, text ·
cross-cutting · **PUBLIC** -- `tests/unit/test_capability.py` +6 ·
**LEAVE ALONE.** This is the module that makes the TOOLKIT-005 rule enforceable.

**`document.py`** -- 199 · Verified immutable ROM document plus reference graph;
no filesystem access. · `RomDocument(L18)` with `.anchor(L44)`,
`.inbound(L56)`, `.validate(L73)`, `.to_json(L126)`, `.to_compact_json(L132)`;
`scan_pointer_candidates(L173)` · deps: binary, gba_header, hashing, layout,
profile · inbound: authored_placements, entities, graphics, placement_events,
relocation, relocation_proof · cross-cutting · **PUBLIC** -- 4 test files ·
**LEAVE ALONE.**

**`allocation.py`** -- 83 · Deterministic lowest-aligned first-fit over
profile-declared free regions only. · `InsufficientSpaceError(L11)`,
`AllocationRequest(L16)`, `Allocation(L32)`, `allocate(L43)` · deps: binary,
layout, profile · inbound: authored_placements, relocation · cross-cutting ·
**PUBLIC** -- 5 test files · **LEAVE ALONE.** Textbook small module.

**`relocation.py`** -- 149 · Atomic anchor movement with reference rewriting,
compiled into the shared write path. · `CandidateReferenceError(L15)`,
`RelocationRequest(L20)`, `RelocationResult(L32)`, `plan_relocation(L47)`,
`emit_relocation(L144)` · deps: allocation, binary, document, layout, write ·
inbound: authored_placements, relocation_proof · cross-cutting · **PUBLIC**  --
`tests/unit/test_relocation.py`, `test_text_relocation.py`,
`tests/integration/test_placement_run_relocation_rom.py` · **LEAVE ALONE.**

**`relocation_proof.py`** -- 41 · A single portable proof
(`synthetic_relocation_proof(L13)`) over constructed bytes, surfaced by
`webfoot relocation-proof`. · deps: binary, document, layout, profile,
relocation · inbound: cli (lazy, `cli.py:1482`) · cross-cutting ·
**INTERNAL-ish** -- no test imports it directly; it is exercised only through
the CLI (`tests/unit/test_relocation.py` invokes `main(["relocation-proof"])`) ·
**LEAVE ALONE.** 41 lines, one function, correct place.

**`write.py`** -- 439 · **The single ROM write authority** (see §6).
Attributed, validated emission of a NEW image. · `ByteChange(L68)`,
`ReferenceRewrite(L127)`, `RelocationProvenance(L141)`, `WritePlan(L159)`,
`ProjectProvenance(L190)`, `WriteManifest(L208)`, `plan_changes(L260)`,
`apply_plan(L311)`, `emit_image(L344)` · deps: layout, rom · inbound:
authored_placements, build, cli, maps, placement_events, relocation, stats,
text · cross-cutting · **PUBLIC** -- 10 test files ·
**LEAVE ALONE.** The atomic staging in `emit_image(L410-437)` (stage to a temp
file, `os.link` publish, roll back on failure) is a single indivisible
guarantee; splitting `plan_changes`/`apply_plan`/`emit_image` apart would break
the ordering rules documented at `write.py:353-358`.

### Layer 2 -- pure codecs (`formats/`)

Per TOOLKIT-005, a `formats/` module **should** name the game it was verified
against. Every game name below is correct, not a defect.

**`formats/__init__.py`** -- 1 · namespace only · **LEAVE ALONE.**

**`formats/stat_tables.py`** -- 453 · Pure Buu's Fury enemy/base-stat record
codec with upstream provenance recorded in its docstring. ·
`EnemyRecord(L91)`, `BaseStatRecord(L114)`, `decode_enemy_record(L133)`,
`encode_enemy_record(L408)`, `encode_base_stat_record(L432)`,
`StatIdentity(L328)` · deps: none · inbound: cli, entities, stats ·
enemy/character stats · **PUBLIC** -- 9 test files ·
**LEAVE ALONE.** No I/O, no addresses -- matches the codec contract at
`docs/architecture.md:63-64`.

**`formats/text_tables.py`** -- 317 · UTF-16LE string pool + pointer table
codec (Buu's Fury). · `decode_string(L105)`, `encode_string(L145)`,
`TextIdentity(L208)`, `iter_text_entries(L286)`,
`pool_is_exhaustively_tiled(L304)` · deps: none · inbound: cli,
formats.ascii_text_tables, text · text · **PUBLIC**  --
`tests/unit/test_text_tables.py` +4 · **LEAVE ALONE.**

**`formats/ascii_text_tables.py`** -- 213 · ASCII NUL-terminated pool codec
(Legacy of Goku II). Reuses `TextCodecError` from `text_tables`
(`formats/ascii_text_tables.py:3`), which is the correct sharing. ·
`decode_string(L76)`, `encode_string(L107)`,
`pool_is_exhaustively_tiled(L193)` · deps: formats.text_tables · inbound:
`text.py` selects it via `_codec_for(text.py:279)` · text ·
**PUBLIC** -- `tests/integration/test_logii_text_rom.py` · **LEAVE ALONE.**

**`formats/map_entry.py`** -- 315 · Byte-exact MapEntry records and read-only
table validation. Note: this codec **does** perform I/O
(`_file_identity(L172)`, `read_map_entry_table(L226)`,
`validate_map_entry_round_trips(L284)` all take a path) and imports `rom` and
`capability` -- the only `formats/` module that does. · `MAP_ENTRY_SIZE(L21)`,
`MapEntryField(L46)`, `MapEntry(L88)`, `MapEntryTable(L146)`,
`MapEntryValidationResult(L161)`, `resolve_map_entry_table_range(L207)` · deps:
binary, capability, hashing, profile, rom · inbound: analysis.*,
authored_placements, build, cli, maps · maps · **PUBLIC** -- 8 test files ·
**REFACTOR TARGET (low value, see §8).** Its I/O breaks the "codecs never
perform I/O, so the byte source is swappable" rule stated at
`docs/architecture.md:63`. This is a documented-invariant violation, but the
functions doing it (`read_map_entry_table`, `validate_map_entry_round_trips`)
are the *table-level* entry points, not the record codec, and every consumer
already uses them that way. Low priority.

**`formats/map_slots.py`** -- 230 · 8-byte map-linked slot arrays; lossless
bytes first, typed decode second. · `ArrayShape(L110)`, `MapSlot(L124)`,
`MapSlotArray(L175)`, `decode_slot_array(L197)` · deps: none · inbound: maps ·
maps · **PUBLIC** -- `tests/unit/test_map_slots.py` +2 · **LEAVE ALONE.**

**`formats/map_placements.py`** -- 251 · Variable-length TOOLKIT-016
factory-led placement family codec. · `DescriptorRecord(L42)`,
`PlacementRecord(L63)`, `read_placement_record(L122)`, `ObjectSlot(L157)`,
`iter_object_slots(L195)`, `iter_placement_offsets(L221)`,
`SCRIPT_DISPATCH_HANDLER(L22)` · deps: none · inbound: authored_placements,
formats.placement_links, placement_events, project.model · placements ·
**PUBLIC** -- 13 test files · **LEAVE ALONE.**

**`formats/placement_links.py`** -- 361 · Physical bindings between placement
descriptors, VM dispatch, event resources and dialog text. ·
`descriptor_source(L25)`, `payload_source(L29)`, `thumb_fetch(L33)`,
`native_bindings(L49)`, `operand_references(L115)`,
`event_resource_records(L209)`, `dialog_text_references(L270)`,
`dialog_code_block(L318)` · deps: binary, formats.map_placements,
formats.script_vm · inbound: placement_events · events/dialog ·
**PUBLIC** -- 4 integration test files · **LEAVE ALONE.**

**`formats/script_vm.py`** -- 375 · Bounded instruction codec and control-flow
IR; the module `authored_placements` uses to assemble authored behavior. ·
`Opcode(L20)`, `OpcodeSet(L36)`, `Instruction(L55)`, `ScriptIR(L85)`,
`decode_instruction(L126)`, `encode_instruction(L182)`, `disassemble(L208)`,
`assemble_source(L269)`, `assemble(L351)` · deps: none · inbound:
authored_placements, cli, data.script_specs, formats.placement_links,
placement_events, scripts · scripts · **PUBLIC** -- 15 test files ·
**LEAVE ALONE.** Assembler and disassembler in one file is correct: they are
the two directions of one grammar and must not drift.

**`formats/sprite_graphics.py`** -- 525 · Tiles, palette, OBJ pieces, frames,
animations. · `Palette(L128)`, `decode_palette(L168)`,
`unswizzle_tiles(L183)`, `swizzle_tiles(L218)`, `Piece(L268)`, `Frame(L344)`,
`Animation(L352)`, `decode_graphic(L436)`, `plan_graphic_payload(L477)` · deps:
formats.webfoot_lz · inbound: build, cli, graphics · graphics · **PUBLIC**  --
`tests/unit/test_sprite_graphics.py`, `tests/integration/test_graphics_rom.py`
· **LEAVE ALONE.**

**`formats/webfoot_lz.py`** -- 519 · The container format + LZ bitstream, the
only place bit layout is known. · `Container(L81)`, `_WordBitReader(L103)`,
`unpack(L274)`, `build_stored(L315)`, `_WordBitWriter(L353)`, `pack(L408)` ·
deps: none · inbound: formats.sprite_graphics · graphics · **PUBLIC**  --
`tests/unit/test_webfoot_lz.py` · **LEAVE ALONE.**

**`formats/indexed_png.py`** -- 229 · Minimal colour-type-3 PNG codec. ·
`encode(L56)`, `decode(L120)` · deps: none · inbound: build, cli · graphics ·
**PUBLIC** -- `tests/unit/test_indexed_png.py` · **LEAVE ALONE.**

### Layer 3 -- semantic / domain

**`stats.py`** -- 426 · Semantic access to enemy/character records: name a
record and a field, never an offset. · `StatTables(L170)` with
`.enemies(L208)`, `.set_enemy_field(L241)`, `.changes(L280)`, `.plan(L323)`;
`load_stat_tables(L343)` · deps: formats, hashing, profile, rom, write ·
inbound: build, cli · stats · **PUBLIC** -- 3 test files ·
**LEAVE ALONE.** Mirrors `text.py`/`maps.py` exactly.

**`text.py`** -- 556 · Semantic string access with two codecs selected by
profile (`_codec_for(L279)`), plus `_enumerate_utf16le(L142)` /
`_enumerate_ascii(L184)`. · `TextStrings(L342)` with `.entries(L386)`,
`.set_text(L407)`, `.changes(L435)`, `.plan(L472)`;
`load_text_strings(L489)` · deps: formats, formats.text_tables, hashing,
profile, rom, write · inbound: build, cli · text · **PUBLIC** -- 3 test files ·
**LEAVE ALONE.** TOOLKIT-005 compliant: the two codecs are chosen by profile
metadata at `text.py:279`, not by a game-name branch.

**`maps.py`** -- 930 · Semantic map records, slot extents, placements and
connections, plus its own change/plan emission. · `MapIdentity(L70)`,
`PlacementIdentity(L150)`, `MapGraph(L249)`, `_resolve_slot_extent(L262)`,
`_resolve_object_slots(L343)`, `_resolve_placements(L371)`, `Maps(L455)` with
`.legacy_view(L520)`, `.map_placements(L548)`, `.set_field(L625)`,
`.set_placement_position(L640)`, `.changes(L664)`, `.plan(L738)`;
`load_maps(L775)` · deps: binary, formats, formats.map_entry, hashing, profile,
rom, write · lazy: data.placement_contracts, placement_events · inbound:
authored_placements, build, cli, entities, scripts · maps/placements ·
**PUBLIC** -- 17 test files · **LEAVE ALONE.** 930 lines is the sum of four
resolvers over one ROM structure plus one facade over them. The `authored_maps`
yield logic in `changes(L664-735)` is the correct owner of "which map structures
does an authored expansion take over", and its docstring
(`maps.py:673-682`) explains why. See §4 A for its one lazy cycle edge.

**`graphics.py`** -- 613 · Semantic sprite assets: stable IDs, shared-consumer
answers, palette/pixel edit plans. · `GraphicIdentity(L54)`,
`CharacterIdentity(L71)`, `FrameRef(L94)`, `Graphic(L119)`,
`ActorSprites(L177)` with `.reference_document(L341)`,
`.plan_palette_entry(L441)`, `.palette_users(L471)`, `.plan_pixels(L489)`,
`.apply_plan(L508)`; `load_actor_sprites(L612)` · deps: binary, formats,
profile, rom · lazy: document, layout · inbound: build, cli · graphics ·
**PUBLIC** -- `tests/integration/test_graphics_rom.py` (only one direct
importer) · **LEAVE ALONE** (but see §7 characterization gap G3: it is the
least-tested semantic module of its size).

**`entities.py`** -- 237 · Read-only static placement↔type relationships, and
the reference graph the relocator consumes. · `PlacementTypeIdentity(L26)`,
`PlacementType(L41)`, `PlacementTypes(L66)` with `.type_of(L116)`,
`.placements_of_type(L122)`, `.factory_of(L125)`, `.project_document(L154)`,
`.reference_document(L170)`; `load_placement_types(L236)` · deps: binary,
document, formats, layout, maps · inbound: authored_placements, build, cli ·
placements · **PUBLIC** -- 7 test files · **LEAVE ALONE.**

**`placement_events.py`** -- 321 · Shared read-only placement descriptors and
proven script attachments; identity follows first semantic consumer, never
address order. · `Descriptor(L21)`, `Event(L30)`, `PlacementEvents(L36)` with
`.descriptor_of(L101)`, `.operand_references(L107)`, `.resource_show(L125)`,
`.dialog_text_references(L153)`, `.consumers_of(L189)`, `.corpus(L203)`,
`.project_document(L226)`, `.changes(L257)`, `.extend_references(L265)` ·
deps: binary, data.placement_contracts, data.script_specs, formats,
formats.map_placements, formats.script_vm, layout, write · lazy: document,
scripts · inbound: authored_placements, build, cli, entities, maps, scripts ·
events/dialog · **PUBLIC** -- 5 integration test files · **LEAVE ALONE.**

**`scripts.py`** -- 176 · Verified script-corpus loading; parsing never writes. ·
`Attachment(L14)`, `ScriptCorpus(L36)`, `reverse_text_consumers(L66)`,
`script_references(L82)`, `script_families(L109)`, `load_scripts(L120)` · deps:
binary, data.script_specs, formats.script_vm, rom · lazy:
data.placement_contracts, maps, placement_events · inbound:
authored_placements, cli, placement_events · scripts · **PUBLIC** -- 8 test
files · **LEAVE ALONE.** See §4 A for its lazy cycle edge.

**`authored_placements.py`** -- 974 · **The AUTHOR_NEW domain module.** Owns
nine of the ten TOOLKIT-029..034 concepts (§5): trigger contract validation,
behavior resolution, script assembly, run preparation, count derivation,
authoring overlay, allocation binding, materialization planning, and the
ownership-contract gate. · `PlannedPlacement(L22)`,
`AuthoredBehaviorError(L93)`, `AuthoredTriggerError(L97)`,
`_require_trigger_contract(L101)`, `_resolve_behavior(L140)`,
`_expand_semantic_source(L173)`, `_assemble_script(L210)`,
`AuthoredCountError(L244)`, `AuthoredRun(L249)` with
`.allocation_request(L288)` and `.derive_count_change(L296)`,
`_canonical_slots(L360)`, `prepare_authored_runs(L380)`,
`AuthoringOverlayError(L462)`, `authoring_overlay(L477)`,
`AuthoredBody(L551)`, `_withhold(L580)`, `_bind_pointers(L608)`,
`plan_authored_materialization(L652)`, `AuthoredMaterialization(L786)`,
`materialize_authored_runs(L811)`, `require_materialization_contract(L893)` ·
deps: allocation, formats.map_entry, layout, maps, project.placements · lazy:
binary, data.behavior_triggers, data.placement_contracts, data.script_effects,
data.script_specs, document, entities, formats.*, placement_events, project,
relocation, scripts, write · inbound: **build only** · authored placements ·
**PUBLIC** -- 4 test files (`tests/unit/test_authored_placements.py`,
`test_authored_behavior_trigger.py`, `test_gameplay_effect_native.py`,
`tests/integration/test_authored_placements_rom.py`) ·
**LEAVE ALONE -- deliberately.** 974 lines and 15 lazy imports look alarming,
but this is one pipeline: project state → planned records → allocation request
→ overlay anchors → materialized byte changes. Every stage consumes the
previous stage's dataclass. Splitting it would create modules that can only
be called in one order by one caller -- fragmentation, not decomposition. Its
lazy imports are deliberate deferral of heavy subsystems, not cycle-breaking:
none of them is a back-edge (§4 A).

### Layer 4 -- authored source (`project/`)

**`project/__init__.py`** -- 37 · Re-export surface only
(`project/__init__.py:1-6` states the boundary: it never opens a ROM, never
computes an offset, never emits an image). · deps: format, model · inbound:
authored_placements, build, cli · cross-cutting · **PUBLIC** -- 13 test files ·
**LEAVE ALONE.**

**`project/format.py`** -- 134 · Deterministic TOML writer (stdlib `tomllib`
reads). Its docstring explains the read/write asymmetry. ·
`ProjectFormatError(L36)`, `_format_value(L76)`, `_emit_table(L92)`,
`dump_toml(L114)`, `load_toml(L129)` · deps: none · inbound: build,
project.model, project.placements · cross-cutting · **PUBLIC** -- 6 test files ·
**LEAVE ALONE.**

**`project/model.py`** -- 827 · The on-disk project: schema, read, write,
per-table document builders. · `ProjectMeta(L133)`, `StatProject(L202)`,
`_require_hex_blob(L264)`, `_enemy_document(L287)`, `_character_document(L311)`,
`_text_document(L326)`, `_map_document(L343)`, `write_project(L400)`,
`_read_records(L464)`, `_read_strings(L526)`, `_read_maps(L589)`,
`read_project(L765)` · deps: formats, project.format · lazy:
formats.map_placements, project.placements · inbound: build,
project.placements · cross-cutting · **PUBLIC** -- 4 test files ·
**LEAVE ALONE.** Same shape as `profile.py`: one schema, one `_x_document`
writer and one `_read_x` reader per authored table. Cohesive.

**`project/placements.py`** -- 210 · Authored clones as a project concept,
separate from extracted canonical rows. · `BehaviorTrigger(L30)`,
`AuthoredPlacement(L37)` with `.authored_behavior(L57)`, `.to_document(L116)`,
`.serialize(L127)`; `parse_authored(L152)`, `validate_templates(L169)`,
`clone_placement(L185)` · deps: project.format · lazy: project.model · inbound:
authored_placements, cli, project.model · authored placements · **PUBLIC**  --
8 test files · **LEAVE ALONE.** See §4 A for its lazy cycle edge.

### Layer 5 -- control flow and presentation

**`build.py`** -- 1008 · Extract / validate / build control flow, plus
authored-materialization sequencing. Full analysis in §8. · `BuildError(L74)`,
`ProjectRomMismatchError(L78)`, `ValidationReport(L88)`, `BuildResult(L108)`,
`_require_extractable_profile(L131)`, `extract_project(L153)`,
`_extract_graphics(L277)`, `_map_documents(L362)`, `_check_identity(L406)`,
`_check_records(L440)`, `_check_strings(L504)`, `_check_maps(L547)`,
`_load_for_project(L715)`, `validate_project(L754)`,
`_apply_project_to_tables(L789)`, `_apply_project_to_maps(L808)`,
`build_project(L838)`, `_placement_document(L976)`,
`authored_capacity_plan(L992)` · deps: capability, formats.map_entry, layout,
maps, profile, project, rom, stats, text, write · lazy: authored_placements,
data.placement_contracts, entities, formats, graphics, placement_events,
project.format, project.model · inbound: cli · cross-cutting · **PUBLIC**  --
14 test files · **REFACTOR TARGET -- one extraction (§8 R1).**

**`cli.py`** -- 1664 · Argument parsing, dispatch, and terminal presentation.
Full analysis in §7. · `development_profile_path(L53)`, `load_catalog(L57)`,
`build_parser(L86)`, 20 `_print_*`/`_parse_*` helpers, `_run_graphics(L1221)`,
`_run_event(L1331)`, `main(L1438)` · deps: 15 static + 8 lazy · inbound:
`__main__` only · cross-cutting · **PUBLIC** -- 16 test files ·
**MOSTLY LEAVE ALONE -- three narrow extractions (§8 R2, R3).**

**`__main__.py`** -- 5 · `from .cli import main` + `sys.exit(main())`. · **LEAVE
ALONE.**

**`__init__.py`** -- 5 · Package docstring + `from .rom import identify_rom`. ·
**LEAVE ALONE.**

### Layer X -- research tooling (`analysis/`)

`analysis/` is imported by `cli.py` and **by nothing else in production**
(verified §4 B). It sits beside the SDK, not on its path.

**`analysis/__init__.py`** -- 1 · namespace · **LEAVE ALONE.**

**`analysis/thumb.py`** -- 227 · Shared Thumb decoders for static research; its
docstring records the historical Python-precedence scanner bug and requires
every bit test be parenthesized. · `RomReader(L32)`, `decode_bl(L84)`,
`encode_bl(L122)`, `ldr_literal_address(L165)`, `scan_bl(L177)`,
`scan_push_prologues(L196)`, `find_aligned_words(L211)` · deps: binary ·
inbound: **no production module** -- only tests · research · **PUBLIC (to
tests)** -- 6 test files including `tests/unit/test_thumb.py` ·
**LEAVE ALONE.**

**`analysis/map_entry_pointers.py`** -- 410 · Read-only census of raw
pointer-labelled MapEntry words. · `PointerObservation(L54)`,
`PointerFieldStats(L84)`, `MapEntryPointerCensus(L125)`,
`analyze_map_entry_pointers(L330)`, `census_map_entry_pointers(L399)` · deps:
binary, formats.map_entry, profile · inbound: cli only · research ·
**PUBLIC** -- 2 test files · **LEAVE ALONE** (but see §4 B note: it is research
tooling reachable from the shipped CLI).

**`analysis/variation_arrays.py`** -- 481 · Reads exactly the first u32 at each
variation-array target and classifies it. · `VariationArrayFirstWordCensus(L106)`,
`find_first_word_observations(L229)`, `analyze_variation_array_first_words(L350)`,
`census_variation_array_first_words(L449)` · deps: binary, formats.map_entry,
hashing, profile, rom · inbound: cli only · research · **PUBLIC** -- 2 test
files · **LEAVE ALONE.**

### Layer D -- trusted data (`data/`)

**`data/__init__.py`** -- 1 · also the package that holds the packaged
`roms.yaml` (`cli.py:64`, `capability.py:87`). · **LEAVE ALONE.**

**`data/placement_contracts.py`** -- 520 · Trusted profile-specific placement
ownership metadata; numeric provenance only. · `CONTRACTS(L7)` · deps: none ·
inbound: authored_placements, build, entities, maps, placement_events, scripts
· placements · **PUBLIC** -- 7 test files · **LEAVE ALONE.** A data table, not
code.

**`data/script_specs.py`** -- 87 · Verified VM opcode variants as data. ·
`STACK_BE7_V1(L21)`, `STACK_BE16_BUU_V1(L71)`, `OPCODE_SETS(L80)`,
`REFERENCE_RULES(L84)` · deps: formats.script_vm · inbound:
authored_placements, placement_events, scripts · scripts · **PUBLIC** -- 11 test
files · **LEAVE ALONE.**

**`data/behavior_triggers.py`** -- 51 · Profile-bound authored behavior-trigger
evidence contracts (TOOLKIT-034). · `BEHAVIOR_TRIGGER_CONTRACTS(L10)` · deps:
none · inbound: authored_placements · authored placements · **PUBLIC**  --
`tests/unit/test_authored_behavior_trigger.py` · **LEAVE ALONE.**

**`data/script_effects.py`** -- 20 · One evidence-backed authored script effect. ·
`SCRIPT_EFFECTS(L4)` · deps: none · inbound: authored_placements · scripts ·
**PUBLIC** -- `tests/unit/test_gameplay_effect_native.py` · **LEAVE ALONE.**

---

## 3. Duplicated logic actually observed

**D1 -- the events-document + reference-graph construction, built twice.**
`build.py:263-265` (extract writes it):

```python
events = PlacementEvents(loaded_maps)
document = events.project_document()
document['reference_graph'] = load_placement_types(rom_path, catalog).reference_document().to_compact_json()
```

`build.py:569-570` (validate re-derives it to compare):

```python
expected_events = relationships.project_document()
expected_events['reference_graph'] = PlacementTypes(maps).reference_document().to_compact_json()
```

Same two-key structure assembled in two places. The two must stay byte-identical
or every extracted project fails validation -- the coupling is silent and the
compiler cannot see it. This is the strongest concrete duplication in the tree.

**D2 -- the "bytes changed" manifest renderer, three copies.**
`cli.py:790-797`, `cli.py:1128-1135`, `cli.py:1194-1201`. Identical
`differing = [change.offset + i for i, (a,b) in enumerate(zip(change.old, change.new)) if a != b]`
plus three identical `print` lines. Cosmetic, but three copies.

**D3 -- the "Base/Output SHA256 + Output + Manifest" block, three copies.**
`cli.py:781-788` (`_print_stats_set`), `cli.py:1118-1125` (`_print_text_set`),
`cli.py:1186-1191` (`_print_build`). Same five fields, same order.

**D4 -- the round-trip printers share a shape but not code.**
`_print_round_trip(cli.py:738)` uses `plan.is_noop`;
`_print_text_round_trip(cli.py:1072)` re-encodes each entry;
`_print_map_round_trip(cli.py:995)` re-encodes records, slots and placements.
These are **not** duplication -- three different verification algorithms -- but
they are three *domain* algorithms living in the presentation layer (§7 C1).

**D5 -- `resource:index` identity parsing, three copies.** `cli.py:1358`,
`cli.py:1365`, `cli.py:1381` each do
`kind, _, index = args.resource.rpartition(':')` followed by a
`kind not in (...) or not index.isdigit()` check with a differently-worded
error. Small, but the third one accepts a different kind set than the first two.

---

## 4. Requested analyses

### A. IMPORT CYCLES

**Method.** AST-parsed every `.py` under `tools/webfoot/`, resolved relative and
absolute `tools.webfoot.*` imports to module names, separated module-level
(*static*) edges from function-body (*lazy*) edges, and ran Tarjan SCC over both
graphs. Script run from the system temp directory; nothing written to the repo.

**Result -- static graph: NO CYCLES.** Every module-level import chain is
acyclic. Python could import every module in dependency order with no deferral.

**Result -- including lazy imports: two cycles.**

**Cycle 1: `maps` → `placement_events` → `scripts` → `maps`**
- `maps.py:928` -- `from .placement_events import PlacementEvents`, inside
  `load_maps`, to validate descriptor/child provenance on every normal map read.
- `placement_events.py:204` -- `from .scripts import Attachment, ScriptCorpus,
  ScriptSegment, OPCODE_SETS`, inside `PlacementEvents.corpus()`.
- `scripts.py:127` -- `from .maps import load_maps`, inside `load_scripts`, only
  on the `family == FAMILY` branch (`scripts.py:125-128`).

  Also `scripts.py:115` and `scripts.py:125` import `FAMILY` from
  `placement_events`, making the `scripts ↔ placement_events` pair a two-node
  cycle in its own right.

  **Verdict: a real design cycle, currently harmless.** The three modules are
  mutually recursive through the placement-descriptor script family: a map read
  validates its descriptors, descriptors form a script corpus, and that corpus
  family is loaded through a map read. Nothing is broken today (the deferral
  makes it import-safe and no infinite recursion exists because
  `PlacementEvents(result)` at `maps.py:929` is constructed on an
  already-built `Maps`), but it means these three modules are effectively one
  unit that cannot be reasoned about, tested, or moved independently.

**Cycle 2: `project.model` ↔ `project.placements`**
- `project/model.py:744` and `:804` -- `from .placements import parse_authored` /
  `validate_templates`.
- `project/placements.py:62`, `:136`, `:153`, `:170`, `:192` -- five separate
  deferred imports back into `model`, including
  `from .model import read_project, _read_document, _MAP_FILE,
  ProjectValidationError` at `placements.py:192` (note: reaching for two
  underscore-private names across the cycle).

  **Verdict: a real cycle and the cheaper of the two to fix.** The shared items
  are only the exception classes (`ProjectError`/`ProjectLoadError`/
  `ProjectValidationError`, `project/model.py:115-123`) plus the document I/O
  helpers. See §8 R4.

### B. REVERSE DEPENDENCIES -- every named violation checked

| Named violation | Verdict | How checked |
|---|---|---|
| formats → CLI | **ABSENT** | `grep -rn "from .cli\|from ..cli\|import cli" tools/webfoot` returns exactly one hit: `tools/webfoot/__main__.py:1`, which is the entry point and correct. |
| allocator → argparse | **ABSENT** | `grep -rn argparse tools/webfoot --include=*.py` excluding `cli.py` returns **zero** hits. `argparse` appears only in `cli.py`. |
| domain → terminal formatting | **ABSENT** | `grep -rn "^\s*print(" tools/webfoot` excluding `cli.py`: **zero** hits. `grep -rn "sys.stdout\|sys.stderr"` excluding `cli.py`: **zero** hits. No production module prints. |
| binary codec → project command logic | **ABSENT** | No `formats/*` or `binary.py`/`layout.py` module imports `project`, `build` or `cli`. Static graph §1 confirms: `formats.*` reach at most `binary, hashing, profile, rom, capability`. |
| build core → runtime research probe | **ABSENT** | `build.py` imports nothing from `analysis/`, `tools/runtime/`, or `tools/mgba_probe/`. Its full import set is listed in §2. |
| research tooling on the required SDK production path | **PARTIAL -- one finding** | `analysis/*` is imported by `cli.py:11-19` (`analysis.map_entry_pointers`, `analysis.variation_arrays`) and **by no other production module**. So research code is *not* on the extract/validate/build path -- but it *is* statically imported at CLI module load, meaning `import tools.webfoot.cli` pulls in 891 lines of research census code even for `webfoot build`. This is an import-weight issue, not a layering violation: no build-path function calls into `analysis/`. |

**One additional reverse dependency, not in the original list:**
`formats/map_entry.py` imports `..rom` and `..capability`
(`formats/map_entry.py:9-13`) and takes filesystem paths
(`read_map_entry_table(L226)`, `validate_map_entry_round_trips(L284)`). This
contradicts the invariant at `docs/architecture.md:63` -- "codecs never perform
I/O, so the byte source is swappable". It is the only `formats/` module that
does so. Reported as an inventory finding; see §8 R5 for why it is low priority.

### C. AUTHOR_NEW OWNERSHIP -- the ten TOOLKIT-029..034 concepts

| # | Concept | Owner today | Only in build/cli? |
|---|---|---|---|
| 1 | Authored entity description | `project/placements.py:37` `AuthoredPlacement`, serialized at `:116`/`:127`; parsed at `:152` `parse_authored` | No |
| 2 | Authored placement materialization | `authored_placements.py:652` `plan_authored_materialization` + `:811` `materialize_authored_runs` | No |
| 3 | Map-array expansion | `authored_placements.py:249` `AuthoredRun` (`target_slot_count` L278, `canonical_slots` via `_canonical_slots` L360) + count derivation at `:296` `derive_count_change`; the *yield* side is `maps.py:664` `Maps.changes(authored_maps=...)` | No |
| 4 | Relocation | `relocation.py:47` `plan_relocation`; invoked for authored bodies at `authored_placements.py:769` (`from .relocation import RelocationRequest, plan_relocation`) | No |
| 5 | Verified allocation | `allocation.py:43` `allocate`; the authored request is built at `authored_placements.py:288` `AuthoredRun.allocation_request` and free space withheld at `:580` `_withhold` | No |
| 6 | Behavior descriptor construction | `authored_placements.py:140` `_resolve_behavior` + `AuthoredBody(L551)` + `_bind_pointers(L608)`; the physical field offsets are named at `authored_placements.py:453-458` from `formats/placement_links.py` | No |
| 7 | Script allocation | `authored_placements.py:210` `_assemble_script` (assembles via `formats.script_vm.assemble_source`) and the script body is allocated as part of `plan_authored_materialization(L652)` | No |
| 8 | Behavior trigger attribution / validation | `authored_placements.py:101` `_require_trigger_contract` against `data/behavior_triggers.py:10` `BEHAVIOR_TRIGGER_CONTRACTS`; the authored value is `project/placements.py:30` `BehaviorTrigger` | No |
| 9 | Generated change ownership | Split, correctly: `write.py:68` `ByteChange(owner=, reason=)` is the mechanism; `authored_placements.py:296` `derive_count_change` and `:811` `materialize_authored_runs` name authored owners; `maps.py:664` `Maps.changes(authored_maps=)` is what *cedes* ownership | No |
| 10 | **Build control of authored materialization** | **`build.py:855-905` ONLY** | **YES** |

**THE HIGHEST-VALUE FINDING.** Concept 10 has no domain owner. `build.py:855-905`
is the only code in the tree that knows the *sequence*:

```python
authored_runs = prepare_authored_runs(project, maps)          # build.py:857
authored_map_identities = frozenset(MapIdentity(run.map_index) # build.py:869
                                    for run in authored_runs)
if authored_runs and maps is not None:                         # build.py:870
    document = _placement_document(maps)                       # build.py:871
    if document is None:
        require_materialization_contract(authored_runs, maps.base_bytes, None)
    else:
        try:
            authored_changes = materialize_authored_runs(      # build.py:876
                document, authored_runs, maps.base_bytes)
        except LayoutError:
            require_materialization_contract(...)              # build.py:882
            raise
elif authored_runs:
    require_materialization_contract(authored_runs, None, None)
```

Four decisions live only here and nowhere else:
1. that a missing reference document means "report the ownership contract"
   rather than "fail";
2. that a `LayoutError` must be re-raised **through** the gate so the blocker
   carries measured context (`build.py:880-884`);
3. that `authored_map_identities` (`build.py:869`) is what `maps.changes()` must
   be told to yield (`build.py:920`) -- the coupling between the expansion and
   the map subsystem's change emission is expressed nowhere else;
4. that `authored_changes` must be appended to the merged plan **after** every
   subsystem (`build.py:928`), so an authored body colliding with another
   subsystem is a hard overlap error.

`authored_placements.py` owns every *step*. `build.py` owns the *policy* joining
them. That policy is domain knowledge and it is stranded in the build driver.

**Secondary finding, same shape:** `_check_maps(build.py:547-708)` contains the
authored-placement validation policy -- `structured`/`legacy` determination
(`build.py:559-561`), the `legacy_view()` fallback (`build.py:573`), the
descriptor-catalog comparison (`build.py:568-572`), the structural-field
comparison per placement (`build.py:677-686`), and a terminal
`prepare_authored_runs` dry-run (`build.py:705-709`). That is roughly 160 lines
of placement-domain rules inside a function whose siblings
(`_check_records`, `_check_strings`) are ~60 lines of pure project-vs-ROM
reconciliation.

### D. CLI COMMAND CENSUS

`cli.py` has **no `set_defaults(func=...)`** anywhere. Dispatch is a sequence of
`if args.command == ...` blocks inside `main(cli.py:1438-1664)`. Four commands
are dispatched *before* the shared ROM-loading block, for the reason documented
at `cli.py:1486-1488` (they take `--rom` rather than a positional `rom`).

**The proposed four families do not fit the code.** The actual code supports
**five** groupings, because *presentation weight* -- not conceptual family  --
is what determines whether a handler is thin. I report the real five and map
them to the four proposed.

| Command / subcommand | Handler | Thin or domain? |
|---|---|---|
| **A. Lifecycle (proposed: lifecycle)** | | |
| `extract` | `main:1508` → `extract_project` + `_print_extract(L1142)` | **Thin.** Printer lists paths. |
| `validate` | `main:1519` → `validate_project` + `_print_validate(L1159)` | **Thin.** |
| `build` | `main:1523` → `build_project` + `_print_build(L1178)` | **Thin** (but see D2/D3 duplication). |
| **B. Authoring (proposed: authoring)** | | |
| `placement clone` | `main:1494` → `project.placements.clone_placement` | **Thin.** |
| `placement plan` | `main:1500` → `build.authored_capacity_plan` | **Thin.** JSON dump. |
| `stats set` | `_print_stats_set(L759)` | **DOMAIN.** Reads `before` off the record (`L762`,`L768`), calls `tables.plan()` and `emit_image` (`L771`) directly -- the CLI is the only caller sequencing a single-field stat edit into a written image. |
| `text set` | `_print_text_set(L1103)` | **DOMAIN.** Same shape: `strings.set_text` then `emit_image(L1109)`. |
| **C. Inspection (proposed: inspection)** | | |
| `identify` | `_print_identification(L473)` | Thin. |
| `entity list/show/type/types/placements-of-type/summary/references` | inline in `main:1442-1472` | **Mostly thin**, but `main:1454-1458` parses a `placement_type:NNNN` identity inline and `main:1468-1470` builds the list-projection dict -- small domain logic. |
| `event families/summary/list/show/attachments/for-owner/owners-of/validate-round-trip` | `_run_event(L1331)` | **Mixed.** `L1387-1398` reconstructs the block for an entity by matching `b.instructions[0].source_offset` against `entry.offset` -- a corpus-navigation rule that belongs in `scripts.py`/`ScriptCorpus`. |
| `event for-map/for-placement/references/consumers-of/resource-show/dialog-refs/dialogs-for-text` | `_run_event(L1342-1385)` | **Mixed.** Three copies of `resource.rpartition(':')` identity parsing (D5). |
| `graphics summary/list/show/consumers/characters/references/export/palette` | `_run_graphics(L1221)` | **DOMAIN.** `L1240-1249` computes the whole corpus summary (`shared_by_frame`, `shared_by_character`, `packed_bytes`, `tile_bytes`) -- aggregations over `sprites.graphics()` that `graphics.py` does not expose. `L1279-1291` performs the PNG export including a filesystem write (`out.write_bytes(blob)`, `cli.py:1289`). |
| `map list/show/connections/placements/placement` | `_print_map_list(L913)`, `_print_map_show(L942)`, `_print_map_connections(L969)`, `_print_map_placements(L862)`, `_print_placement_show(L891)` | Thin. |
| `map validate-round-trip` | `_print_map_round_trip(L995)` | **DOMAIN.** Re-encodes every record, slot array and placement and counts failures (`L997-1027`). |
| `stats list` | `_print_stats_list(L707)` | Thin. |
| `stats validate-round-trip` | `_print_round_trip(L738)` | **Semi-thin.** Uses `plan.is_noop` -- the domain already answers it. |
| `text list/show` | `_print_text_list(L818)`, `_print_text_show(L1057)` | Thin. |
| `text validate-round-trip` | `_print_text_round_trip(L1072)` | **DOMAIN.** Re-encodes every string (`L1085-1089`). |
| **D. Research proof (proposed: research-proof)** | | |
| `relocation-proof` | `main:1481-1484` | Thin. |
| `validate-map-entries` | `_print_map_entry_validation(L510)` | Thin -- `formats.map_entry` computes it. |
| `map-entries pointer-census` | `_print_map_entry_pointer_census(L539)` | Thin -- `analysis` computes it. |
| `variation-arrays first-word-census` | `_print_variation_array_first_word_census(L597)` | Thin. |
| `variation-arrays find-first-word` | `_print_first_word_matches(L670)` | Thin. |
| **E. (fifth, real) Identity parsing helpers** | `_parse_identity(L695)`, `_parse_text_identity(L803)`, `_parse_map_identity(L838)`, `_parse_placement_identity(L845)`, `_parse_graphic_identity(L1211)`, `_parse_u32(L72)` | Presentation-adjacent; each raises `ValueError`/`argparse.ArgumentTypeError` with a human message. Correct in CLI. |

**Count:** 6 domain-bearing handlers out of ~35 commands. The other ~29 are
genuinely thin printers. See §7.

### E. BUILD WRITE AUTHORITY

**Confirmed single. The authority is `write.py`, and specifically:**

- `write.py:260 plan_changes(base, changes, profile_id, base_sha256) -> WritePlan`
  -- validates and sorts; the only place overlap becomes an error.
- `write.py:311 apply_plan(base: bytes, plan) -> bytes` -- pure; produces the
  new image in memory.
- `write.py:344 emit_image(base_path, output_path, plan, *, manifest_path, project) -> WriteManifest`
  -- **the only function in `tools/webfoot/` that writes a ROM image to disk.**

Evidence that it is single: `grep -rn "write_bytes\|open(.*'w'\|\.write("` over
`tools/webfoot/` returns exactly three hits:
- `write.py:425` -- inside `emit_image`'s staging loop. The ROM write.
- `build.py:312` -- `_extract_graphics` writing a PNG **into the project
  directory**, not a ROM.
- `cli.py:1289` -- `graphics export` writing a PNG to a user path, not a ROM.

Plus two project-file writes outside that grep's shape:
`build.py:268` and `build.py:401` (`target.write_text`, project TOML/JSON) and
`project/placements.py:203` (`path.write_text`, the project map file). All
project source, none ROM bytes.

**Callers of `emit_image`:** `build.py:957` (`build_project`), `cli.py:771`
(`stats set`), `cli.py:1109` (`text set`), `relocation.py:149`
(`emit_relocation`). Four call sites, one function.

**Does any domain module write ROM bytes directly rather than producing a change
plan? NO.** Every domain module emits `ByteChange` tuples:
- `stats.py:280 StatTables.changes()`
- `text.py:435 TextStrings.changes()`
- `maps.py:664 Maps.changes(authored_maps=)`
- `placement_events.py:257 PlacementEvents.changes()`
- `authored_placements.py:296 derive_count_change` returns a `ByteChange`;
  `:811 materialize_authored_runs` returns a list of them.
- `graphics.py:489 plan_pixels` / `:441 plan_palette_entry` return plans;
  `graphics.py:508 apply_plan` is a *codec-level* method returning
  `tuple[int, bytes]` (a payload), not a file write -- it shadows the name of
  `write.apply_plan` but is unrelated.

`build_project(build.py:906-950)` merges all of them into **one** `changes` list
and calls `plan_changes` **once** (`build.py:951`), with the reason documented
at `build.py:906-913`: two separate plans could each validate while together
writing the same bytes. That invariant is intact.

One caveat worth recording: `authored_placements.py:774` calls
`apply_plan(relocated, ...)` -- the *pure* `write.apply_plan`, in memory, to
produce bytes for its own subsequent planning. It does not touch the filesystem.
The single-write-path rule holds.

### F. CHARACTERIZATION GAPS

Behaviors NOT pinned by any test, that a future extraction would silently break.
Named as contracts, not as "more tests".

**G1 -- `webfoot stats` CLI contract is completely uncharacterized.**
`grep -rn '"stats"' tests/` returns **zero** hits. No test invokes
`main(["stats", ...])`. The `stats set` handler `_print_stats_set(cli.py:759)`
contains real domain sequencing (read `before`, mutate, `plan()`, `emit_image`)
and its stdout format -- "Buu's Fury Stat Edit", the `Field: x  A -> B` line, the
per-change `bytes changed:` list -- is a user-facing contract with zero
protection. **Required before any movement of `_print_stats_set` or
`_print_stats_list`/`_print_round_trip`.**

**G2 -- `webfoot placement plan` CLI contract is uncharacterized.**
`authored_capacity_plan(build.py:992)` is tested at the API level
(`tests/integration/test_authored_placements_rom.py:53`,
`test_authored_behavior_trigger_rom.py:74`,
`tests/unit/test_authored_placements.py:348`), but the CLI path
(`cli.py:1500-1502`, which JSON-dumps `[r.to_json() for r in runs]` sorted) is
invoked by no test. Only `placement clone` is
(`tests/unit/test_authored_placements.py:581`). **Required before touching the
`placement` dispatch block.**

**G3 -- `graphics.py` semantic layer has one direct test importer.**
Only `tests/integration/test_graphics_rom.py` imports `tools.webfoot.graphics`;
`tests/unit/test_graphics_cli.py` exercises refusals through the CLI with a
synthetic ROM. So `ActorSprites.reference_document(L341)`,
`.plan_palette_entry(L441)`, `.palette_users(L471)`, `.plan_pixels(L489)` and
`.apply_plan(L508)` are pinned only by a test that **skips when the canonical
ROM is absent**. On a machine without the ROM, that module has effectively no
coverage. **Required before moving anything in `graphics.py`.**

**G4 -- the `graphics summary` aggregation is CLI-only and untested.**
`cli.py:1240-1249` computes `shared_by_frame`, `shared_by_character`,
`packed_bytes`, `tile_bytes`. No API equivalent exists in `graphics.py` and no
test asserts the numbers. If R3 (§8) moves it, nothing catches an off-by-one.
**Required before R3.**

**G5 -- the extract↔validate events-document identity (D1) is not directly
pinned.** No test asserts that the document written at `build.py:263-268` equals
the document derived at `build.py:569-570`. It is only *transitively* enforced
by round-trip project tests
(`tests/integration/test_toolkit017_rom.py` imports both `placement_events` and
`project.model`). A characterization test asserting
`extract(...) then validate(...) reports zero problems for the events catalog`
is needed **before** the D1 duplication is collapsed.

**G6 -- the four `build.py:855-905` control decisions are pinned only in
aggregate.** `tests/integration/test_authored_placements_rom.py` and the three
`test_authored_behavior_*_rom.py` files exercise the happy path and some
refusals end to end, but no test isolates: (a) `document is None` →
`require_materialization_contract` with `None`; (b) `LayoutError` re-raised
*through* the gate so the message carries measured context
(`build.py:880-884`); (c) `authored_map_identities` correctly suppressing the
canonical MapEntry and array changes at `build.py:920`. All three are integration
tests that skip without the ROM. **Required before R1 -- this is the extraction
with the most to lose.**

**G7 -- `formats/map_entry.py`'s path-taking entry points.**
`read_map_entry_table(L226)` and `validate_map_entry_round_trips(L284)` re-check
file identity via `_file_identity(L172)` and raise `RomChangedError`. No test
exercises the "file changed mid-read" branch. **Required before R5.**

**G8 -- `_run_event`'s block-lookup rule.** `cli.py:1390-1392` builds
`starts = {b.instructions[0].source_offset: b for b in corpus.ir.blocks}` and
indexes it by `entry.offset`. A `KeyError` here would be an unhandled crash
(the `except` at `cli.py:1432` catches `ScriptError, ProfileConfigError,
RomReadError, ValueError, OSError` -- not `KeyError`). `event show` is invoked by
no test with a valid identity; `tests/integration/test_buu_event_cli_rom.py`
invokes `['event', 'show', rom, 'nope']`, which takes the earlier
`entry is None` branch. **Required before moving `_run_event`.**

**What IS well characterized** (so a future reader does not re-test it):
`profile` (36 files), `maps` (17), `cli` (16), `binary` (16),
`formats.script_vm` (15), `layout` (14), `build` (14),
`formats.map_placements` (13), `project` (13), `data.script_specs` (11),
`write` (10), `formats.stat_tables` (9).

---

## 5. REFACTOR TARGETS

Only modules with a concrete architectural reason. Each carries its evidence.

### T1 -- `build.py` -- extract the authored-materialization policy
**Reason:** §4 C concept 10. `build.py:855-905` is the only code that
understands the authored materialization *sequence*, and it is domain knowledge
sitting in the build driver. **Evidence:** `build.py:857`, `:869`, `:870-887`,
`:920`, `:928`; contrast with `authored_placements.py:811`
`materialize_authored_runs`, which owns every step but not the joining.
**Scope:** ~50 lines out of 1008.

### T2 -- `build.py` -- `_check_maps` is doing two jobs
**Reason:** `_check_maps(build.py:547-708)` is 161 lines against
`_check_records`'s 64 (`:440-503`) and `_check_strings`'s 43 (`:504-546`). The
excess is entirely placement-domain policy: `structured`/`legacy` detection
(`:559-561`), `legacy_view()` fallback (`:573`), descriptor-catalog equality
(`:568-572`), placement-type catalog equality (`:578-590`), per-placement
structural-field equality (`:677-686`), and a `prepare_authored_runs` dry-run
(`:705-709`). Its siblings do pure project-vs-ROM reconciliation.
**Evidence:** the line spans above; the asymmetry is measurable.

### T3 -- `build.py` -- the events-document duplication (D1)
**Reason:** `build.py:263-265` and `build.py:569-570` construct the same
two-key structure. They must remain byte-identical or every extracted project
fails validation, and nothing enforces that.
**Evidence:** both sites quoted in §3 D1.

### T4 -- `project/model.py` ↔ `project/placements.py` cycle
**Reason:** §4 A cycle 2. Five deferred back-imports
(`placements.py:62,136,153,170,192`) including two private names
(`_read_document`, `_MAP_FILE` at `:192`). Nothing structural requires the
cycle -- the shared items are three exception classes
(`project/model.py:115-123`) and two document helpers.

### T5 -- `maps` / `placement_events` / `scripts` cycle
**Reason:** §4 A cycle 1. Three modules that cannot be reasoned about or moved
independently. **Evidence:** `maps.py:928`, `placement_events.py:204`,
`scripts.py:115`, `scripts.py:125`, `scripts.py:127`.
**Caveat:** unlike T4 this is a *semantic* cycle -- placement descriptors really
are both a map property and a script family. Fixing it may require a genuine
design decision, not a mechanical move. Listed as a target because it is real;
ranked last in §8 because the risk is high and the payoff is understanding
rather than behavior.

### T6 -- `cli.py` -- three narrow extractions only
**Reason:** six of ~35 handlers contain domain logic (§4 D). Specifically:
`_print_map_round_trip(cli.py:995)`, `_print_text_round_trip(cli.py:1072)` and
the `graphics summary` aggregation (`cli.py:1240-1249`) compute answers the
domain layer should be able to answer. **This is NOT a case for splitting
`cli.py` into a package.** See §6.

### T7 (low) -- `formats/map_entry.py` I/O in a codec
**Reason:** §4 B. Contradicts `docs/architecture.md:63`. **Evidence:**
`formats/map_entry.py:9-13` (imports `..rom`, `..capability`),
`:172 _file_identity`, `:226 read_map_entry_table`,
`:284 validate_map_entry_round_trips`.

---

## 6. LEAVE ALONE

Each with the reason its responsibility is already coherent.

**`cli.py` -- DOES NOT NEED DECOMPOSITION.**
This is the owner's explicit question and the answer is no. Evidence:
1. It has **exactly one inbound caller** (`__main__.py:1`). No module depends
   on its internals, so splitting it improves no dependency.
2. `argparse` appears in no other module; `print` appears in no other module;
   `sys.stdout/stderr` appear in no other module (§4 B). The presentation
   boundary is already perfectly clean *in the direction that matters*.
3. Of ~35 commands, ~29 handlers are pure printers. The file is long because
   the SDK has 35 commands and each needs a parser stanza plus a formatter  --
   that is linear, expected size, not tangled responsibility.
4. `build_parser(L86-472)` is 386 lines of declarative `add_parser` calls. It
   is data, not logic. Splitting it per family would scatter the argument
   surface across eight files and make "what does the CLI accept" unanswerable
   from one place.
5. The dispatch ordering in `main(L1438)` is load-bearing and documented at
   `cli.py:1486-1488`: four commands must be handled before the shared
   ROM-loading block because they take `--rom` rather than positional `rom`.
   That ordering is easier to keep correct in one function than across modules.

The correct action is T6: move **three** domain computations out and leave the
remaining 1600 lines alone. A cohesive 1600-line presentation layer is healthier
than eight 200-line modules plus a dispatcher.

**`profile.py` (742)** -- one schema validator, one `_optional_*` parser per
profile section (`:135`, `:204`, `:242`, `:325`, `:434`, `:470`). Same
responsibility repeated per section. Splitting fragments one document across six
files.

**`authored_placements.py` (974)** -- one linear pipeline where each stage
consumes the previous stage's dataclass (`PlannedPlacement` → `AuthoredRun` →
`AuthoredBody` → `AuthoredMaterialization`). Splitting produces modules callable
only in one order by one caller.

**`maps.py` (930)** -- four resolvers over one ROM structure
(`_resolve_slot_extent(L262)`, `_declared_run(L327)`,
`_resolve_object_slots(L343)`, `_resolve_placements(L371)`) plus one facade
(`Maps(L455)`). One subject.

**`project/model.py` (827)** -- one authored schema; one `_x_document` writer and
one `_read_x` reader per table.

**`graphics.py` (613)** -- one semantic layer over one codec, with sharing as a
first-class answer per `docs/architecture.md:77-88`.

**`text.py` (556)**, **`stats.py` (426)** -- the canonical semantic-layer shape
the architecture doc describes; `maps.py` mirrors them. Changing any one breaks
the symmetry that makes the layer learnable.

**`write.py` (439)** -- the single write authority (§4 E). `plan_changes`,
`apply_plan` and `emit_image` are three steps of one indivisible guarantee with
documented ordering rules (`write.py:353-372`).

**Every `formats/*` module** -- pure codecs, no I/O (except T7), correctly named
for the game they were verified against per TOOLKIT-005.

**Every `data/*` module** -- trusted data tables, not code.

**Every `analysis/*` module** -- research tooling, correctly isolated: imported
by `cli.py` and by nothing else in production (§4 B).

**All of `binary.py`, `hashing.py`, `gba_header.py`, `layout.py`, `rom.py`,
`capability.py`, `document.py`, `allocation.py`, `relocation.py`,
`relocation_proof.py`, `project/format.py`, `project/__init__.py`,
`__init__.py`, `__main__.py`** -- each under 300 lines with one responsibility
and a clean dependency set.

---

## 7. RECOMMENDED REFACTOR PLAN

Ordered by value-to-risk, highest first. Each item names what moves, where,
why it is a real boundary, the dependency improvement, and the characterization
test required first.

### R1 -- Move the authored-materialization policy into `authored_placements.py`
**Value: highest. Risk: medium.**

**Move:** the block at `build.py:855-905`. Create in `authored_placements.py`
a single entry point, e.g.
`materialize_for_build(project, maps, document_factory) -> tuple[tuple[ByteChange, ...], frozenset[MapIdentity]]`,
absorbing: `prepare_authored_runs` invocation, the `authored_map_identities`
derivation (`build.py:869`), the `document is None` branch (`build.py:872-874`),
the `LayoutError`-through-the-gate re-raise (`build.py:880-884`), and the
`elif authored_runs` branch (`build.py:885-887`).

`build.py:976 _placement_document` moves with it or becomes the injected
`document_factory` -- it already lazily imports `entities` and `capability`
(`build.py:986-987`), which `authored_placements` also imports lazily
(`authored_placements.py` lazy set includes `entities`).

**Why a real boundary:** `authored_placements.py` already owns every step of
this pipeline (§4 C, concepts 1-9). The joining policy is the same domain. After
the move, `build_project` reads:

```python
authored_changes, authored_map_identities = materialize_for_build(project, maps)
```

 -- which is what a build driver should look like.

**Dependency improvement:** removes `build.py`'s lazy import of
`require_materialization_contract` and `materialize_authored_runs`
(`build.py:855-856`), and removes `LayoutError` from `build.py`'s static import
set (`build.py:63`) if no other use remains. `build.py` stops knowing that
authored materialization has a failure gate at all.

**Characterization tests required first: G6.** Three isolated tests  --
`document is None` path, `LayoutError` re-raise carrying measured context, and
`authored_map_identities` suppressing the canonical MapEntry/array changes.
Without these, R1 is the riskiest move in the plan; with them it is routine.

### R2 -- Collapse the events-document duplication (D1)
**Value: high. Risk: low.**

**Move:** add one function to `placement_events.py`, e.g.
`def catalog_document(maps, reference_document) -> dict` returning
`{**self.project_document(), 'reference_graph': reference_document.to_compact_json()}`.
Call it from both `build.py:263-265` and `build.py:569-570`.

**Why a real boundary:** the two-key structure IS the placement-events catalog
format. `placement_events.py:226 project_document` already owns the first key;
it should own the whole document.

**Dependency improvement:** removes the silent must-stay-identical coupling
between two `build.py` functions 300 lines apart. Neither site keeps `import
json` for this purpose (`build.py:262`, `build.py:568`).

**Characterization test required first: G5** -- assert that a fresh
`extract_project` followed by `validate_project` reports zero events-catalog
problems. This is a two-line test that should exist regardless.

### R3 -- Move three domain computations out of `cli.py`
**Value: medium-high. Risk: low.** Do NOT split `cli.py` further.

**R3a -- `_print_map_round_trip(cli.py:995)`.** Move the verification loop
(`cli.py:997-1027`) into `maps.py` as
`Maps.round_trip() -> RoundTripResult` returning counts and failure identities,
mirroring `formats/map_entry.py:161 MapEntryValidationResult`. `cli.py` keeps
only the printing (`cli.py:1029-1056`).
*Real boundary:* "does every map structure re-encode exactly" is a property of
the map subsystem; `formats.map_entry` already returns exactly this shape for
its own records, so the pattern is established, not invented.
*Test first:* already covered  --
`tests/integration/test_local_maps_rom.py` invokes
`main(["map","validate-round-trip", ...])`.

**R3b -- `_print_text_round_trip(cli.py:1072)`.** Same move into `text.py` as
`TextStrings.round_trip()`. `cli.py:1085-1089` (the re-encode loop) is the
domain part.
*Test first:* covered -- `tests/integration/test_text_rom.py` invokes
`main(["text","validate-round-trip", rom])`.

**R3c -- the `graphics summary` aggregation (`cli.py:1240-1249`).** Move to
`graphics.py` as `ActorSprites.summary() -> dict`, alongside the existing
`.reference_document(L341)`.
*Real boundary:* `shared_by_frame` / `shared_by_character` / `packed_bytes` /
`tile_bytes` are corpus facts, and sharing is already the module's headline
responsibility per `docs/architecture.md:80-88`.
*Test first:* **G4 -- none exists.** Write one asserting the five numbers for a
synthetic corpus before moving.

**Explicitly NOT moved:** `_print_stats_set(cli.py:759)` and
`_print_text_set(cli.py:1103)`. They contain real sequencing, but they are the
only callers of the single-field edit path and moving them requires G1 (which
does not exist) plus inventing a domain API that has exactly one consumer. Fix
G1 first; revisit only if a second consumer appears.

### R4 -- Break the `project.model` ↔ `project.placements` cycle
**Value: medium. Risk: low.**

**Move:** `ProjectError`, `ProjectLoadError`, `ProjectValidationError`
(`project/model.py:115-123`) into a new `project/errors.py` (or into
`project/format.py`, which both already import and which has no webfoot deps).
Then move `_read_document` and `_MAP_FILE` -- the two private names
`placements.py:192` reaches for -- to wherever `read_project` lives, or expose
them without the underscore.

**Why a real boundary:** exception types shared by a package belong at the
package's base, not in the largest module of the package. This is the standard
resolution and it removes four of the five back-imports outright
(`placements.py:62,136,153,170` are all exception imports).

**Dependency improvement:** `project.placements` → `project.errors` +
`project.format` only. Cycle gone. `project.model` keeps its one forward
import of `parse_authored`/`validate_templates`.

**Characterization tests required first:** none new. `project` has 13 test
files and `project.placements` has 8; exception identity is asserted in
`tests/unit/test_project_format.py` and `test_authored_placements.py`.
Verify `ProjectValidationError` remains importable from `tools.webfoot.project`
(the re-export at `project/__init__.py`), which every test uses.

### R5 -- Give `formats/map_entry.py` an I/O-free core
**Value: low. Risk: low.**

**Move:** keep `MapEntry(L88)`, `MapEntryRecord(L138)`, `MAP_ENTRY_LAYOUT(L60)`
and the pure decode/encode in `formats/map_entry.py`; move
`_file_identity(L172)`, `_require_target_profile(L181)`,
`read_map_entry_table(L226)` and `validate_map_entry_round_trips(L284)` up a
layer -- `maps.py` already imports both the codec and `rom`/`profile`, so it is
the natural home.

**Why a real boundary:** restores the invariant at `docs/architecture.md:63`
that codecs are byte-source-swappable. Removes the only `formats/ → rom` and
`formats/ → capability` edges in the tree.

**Characterization test required first: G7** -- the `RomChangedError` branch in
`_file_identity`.

**Why last:** the invariant violation is real but has caused no defect; the
functions are used as table-level entry points by every caller already. This is
hygiene, not risk reduction.

### R6 -- `_check_maps` split (T2)
**Value: low-medium. Risk: medium.** **Recommend deferring.**

`_check_maps(build.py:547-708)` really is doing two jobs. But R1 already removes
the `prepare_authored_runs` dry-run at `build.py:705-709` if the new
`materialize_for_build` owns validation too, and after that the function's
excess is mostly catalog-equality checks that are cheap to read in place.
**Re-measure after R1 lands.** If it is still over ~120 lines, extract the
descriptor/type catalog comparisons (`build.py:562-590`) into
`placement_events.py` / `entities.py` as `catalog_matches(project_document)`
predicates -- which R2 makes natural, since both modules will already own their
document shape.

### R7 -- the `maps`/`placement_events`/`scripts` cycle (T5)
**Value: understanding only. Risk: high.** **Recommend NOT doing it as a refactor.**

The cycle is real, but it encodes a real fact: placement descriptors are
simultaneously a map property, a script family, and a shared-resource graph.
Breaking it mechanically -- e.g. hoisting `FAMILY` and the descriptor validation
into a fourth module -- would produce a module with no independent meaning. The
honest recommendation is: **document it** (this file does) and revisit only if
a concrete need appears, such as loading a script corpus without loading maps.
Note that the cycle is currently invisible at import time (the static graph is
acyclic, §4 A), so it costs nothing operationally today.

### Explicitly left alone, with reasons

- **`cli.py` as a whole** -- one inbound caller, clean outbound boundary, 29 of
  35 handlers already thin. Size is linear in command count. §6.
- **`authored_placements.py`** -- one pipeline, not several responsibilities.
- **`profile.py`, `project/model.py`, `maps.py`, `graphics.py`, `text.py`,
  `stats.py`** -- cohesive; each is one subject expressed at the length that
  subject needs.
- **`write.py`** -- the single write authority; its three functions are one
  guarantee.
- **All of `formats/`** (except R5), **all of `data/`, all of `analysis/`**  --
  correctly layered and correctly isolated.

### Ordering summary

| Rank | Item | Value | Risk | Blocked on |
|---|---|---|---|---|
| 1 | R1 authored-materialization policy → `authored_placements` | Highest | Medium | G6 |
| 2 | R2 collapse events-document duplication | High | Low | G5 |
| 3 | R3a/R3b round-trip verification → `maps`/`text` | Med-high | Low | (covered) |
| 4 | R3c graphics summary → `graphics` | Medium | Low | G4 |
| 5 | R4 break `project` cycle | Medium | Low | -- |
| 6 | R5 `formats/map_entry` I/O-free core | Low | Low | G7 |
| 7 | R6 `_check_maps` split | Low-med | Medium | re-measure after R1 |
| 8 | R7 `maps`/`events`/`scripts` cycle | Understanding | High | do not do |

Before any of it: **write G1 and G2** (`stats` and `placement plan` CLI
characterization). They protect user-facing contracts that currently have zero
tests and they are cheap.

---

## 8. Coverage check

49 `.py` files under `tools/webfoot/`. All 49 are inventoried in §2:
`__init__`, `__main__`, `allocation`, `analysis/__init__`,
`analysis/map_entry_pointers`, `analysis/thumb`, `analysis/variation_arrays`,
`authored_placements`, `binary`, `build`, `capability`, `cli`, `data/__init__`,
`data/behavior_triggers`, `data/placement_contracts`, `data/script_effects`,
`data/script_specs`, `document`, `entities`, `formats/__init__`,
`formats/ascii_text_tables`, `formats/indexed_png`, `formats/map_entry`,
`formats/map_placements`, `formats/map_slots`, `formats/placement_links`,
`formats/script_vm`, `formats/sprite_graphics`, `formats/stat_tables`,
`formats/text_tables`, `formats/webfoot_lz`, `gba_header`, `graphics`,
`hashing`, `layout`, `maps`, `placement_events`, `profile`,
`project/__init__`, `project/format`, `project/model`, `project/placements`,
`relocation`, `relocation_proof`, `rom`, `scripts`, `stats`, `text`, `write`.
