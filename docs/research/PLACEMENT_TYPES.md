# TOOLKIT-009: static placement type relationships

## Scope and evidence level

Primary profile: `buus_fury_usa_rev0_01c1707f`, SHA-256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`.
The constructor relationship is **CONFIRMED canonical static evidence (LEVEL 2)**;
corpus counts are direct static measurements. No fresh runtime
capture, gameplay test, type swap, or axis experiment was performed.
The 1,295 supported placements across 215 maps remain the only project corpus.
The 108 unreachable well-formed and 168 non-conforming occurrences stay excluded.

## Sources exhausted before new static examination

| Source | Result and limits |
| --- | --- |
| `ENTITY_FORMAT.md:60-115`, `TOOLKIT-008-review.md` | Ownership/32-byte representation only; type fields and tails unclassified |
| `MAP_FORMAT.md`, TOOLKIT-007 findings | Keep corrected opaque 112 arrays/596 slots and typed 35/89; no placement type proof |
| ROM-006/007/008, `consumer-analysis.md:236-256,326-371` | Selected variation +40/+44 dispatches descriptors through 08012664; separate heterogeneous family |
| ROM-011/012, `consumer-analysis.md:807-865` | Descriptor 08294948 -> 08007675 rectangle-aware object and exact runtime attribution; no FD55 link |
| P-003/P-004, `tickets/archive/P-004.md:1-12,78-80` | Retracted actor attribution is not placement/enemy evidence |
| `AUTO_RE_<local-state-name>:265-275,379-403`, `PROJECT_STATE*.md`, `SUBSYSTEM_MAP.md:70-96` | Separate map-loader/per-character mechanisms; reused runtime slots never identity |
| `build/ghidra/reports/p001-entity-ctors.txt:204-235` (ignored) | Existing canonical type getter 0801713C, no FD55 link; prior reports/research contain no FD55 trace |
| DragonByteZ `b2691209fa873cc0c1d7aa9cdea7c1da4430afe4`, `src/analysis.cpp:462-487,587-618` | Names MapEntry fields, follows +2C; no FD55 consumer. NPC/item/object labels remain INFERRED |
| Arefu/Legacy `d22a556cd33dee56513d5b606b6ae8065ccc5752`, `DBZKit/DrGero/Types.cs:5-54`, `DBZLOG2.cs:20-30` | LoGII labels/config, not a Buu placement parser |
| 2genkidev/buusfury `cc53d0cd2d1c167e749419187e2d92017ac07468`, `buu.s:6-11`, `rest_of_the_game.s:8-12` | Matching canonical profile; relevant code/data unresolved INCBIN |
| BuusFuryToolkit `4353f6a23aa4ac980f1ed42a2c65bc281fa45cc7`, `BuusFuryStudio.py:17-64,167` | Independent stat/person structures only; no placement-field mapping |
| Buu recomp `453a913a9f67916b9b358776da1c1229b09a6c80`, `baserom.md:5-14`, `game.toml:3851-3853,5707-5713` | Different e657... profile; generated directory has only README, no FD55 source. Other constructor labels not transferable |
| [Data Crystal ROM map](https://datacrystal.tcrf.net/wiki/Dragon_Ball_Z:_Buu%27s_Fury/ROM_map) | Public NPC claim uses 08017DA3, a different family. Sprite table names explicitly contain guesses; no FD55 mapping |
| [Data Crystal main page](https://datacrystal.tcrf.net/wiki/Dragon_Ball_Z:_Buu%27s_Fury) | Public 08007675 waypoint example, separate family. Debug/breakpoint leads do not establish this placement chain |

Thus the narrow blocker was **which placement field selects the constructor's
static record**. No canonical generated native function was available to read;
matching disassembly leaves it INCBIN. A bounded direct Thumb read of the known
factory and its immediate consumers resolved the blocker without runtime,
Ghidra project mutation, native recompilation, or a broad behavior investigation.

## Confirmed constructor chain

The canonical factory raw is `0x0800FD55`; Thumb fetch is `0x0800FD54`.
The raw pointer is retained separately, never silently normalized as data.

| Fetch address | Direct canonical observation | Consequence |
| --- | --- | --- |
| 0800FD56 | load u32 from input placement +08 into r2 | Field is an engine table selector, not the enemy identity itself |
| 0800FD58-0800FD60 | `(r2*8-r2)*4`, add literal loaded at FD5C | Stride/address formula is 28 * selector + base |
| 0800FD70 | literal word is 08711274 | Exact base equals independently verified enemy-stat table base |
| 0800FD62-0800FD68 | r1=placement, r2=selected target, r3=incoming context; call 0800F68C with r0=0 | Shared constructor receives selected record directly |
| 0800F68E/0800F692 | retain selected target in r7, placement in r5 | Tracks arguments through constructor |
| 0800F69C-0800F6A0 | request 0xA7 << 2 = 0x29C bytes from allocator | Structural allocation request, not gameplay taxonomy |
| 0800F6E8-0800F6EE | selected target stored at object+224 | Static record retained by constructed object |
| 0800F700-0800F708 | read target+04, shift left 10, store object+28C | Consumes the independently verified HP field |
| 0800F724-0800F72A | reload selected record, read u32 +08, call 0800AA9C | Selected record supplies the initial behavior-controller selector |

Existing independent anchors: authoritative HP at object+28C
(`PROJECT_<local-state-name>`, P-006A/P-006B section); controller push 0800AA9C
(`PROJECT_<local-state-name>`, P-006C section); enemy layout/identity
`tools/webfoot/formats/stat_tables.py:133-170,327-364` and uniqueness gate
`tools/webfoot/stats.py:379-402`.

Reproduce the narrow static reads (read-only input; exact profile/hash guards
and post-read immutability check in `tools/research/placement_type_audit.py`):

```powershell
.venv/Scripts/python.exe -m tools.research.placement_type_audit "roms/Dragon Ball Z - Buu's Fury (U).gba" 0x0800fd54 0x0800fd6e
.venv/Scripts/python.exe -m tools.research.placement_type_audit "roms/Dragon Ball Z - Buu's Fury (U).gba" 0x0800f68c 0x0800f740
.venv/Scripts/python.exe -m tools.webfoot entity summary "roms/Dragon Ball Z - Buu's Fury (U).gba"
```

The research disassembler is optional local tooling, not a toolkit dependency.
Instruction-shaped output beyond a function boundary or at a literal is never
treated as executable evidence; the boundaries above exclude FD70's data word.

## Field audit

| Offset | Status | Meaning established in this ticket |
| --- | --- | --- |
| +00 factory_raw | CONFIRMED | Static wrapper pointer; one factory across supported corpus |
| +04 flags_raw | UNKNOWN | Preserved; no flag meanings assigned |
| +08 type_raw | CONFIRMED | u32 selector in base+28*selector formula; exposed as stable placement type ID |
| +0C position_raw | Existing structural DECODE/EDIT | low/high raw halfwords encode signed map/world X/Y pixels; preserve raw bits losslessly (`PLACEMENT_POSITION_PROVENANCE.md`, Phase 3) |
| +10 id_raw | CONFIRMED load, semantics UNKNOWN | F6AE loads it and passes it to 08000158; resource/graphics role not promoted |
| +14 tail0_raw | CONFIRMED retention, semantics UNKNOWN | F6F0/F6F4 copy it to object+228; not sufficient to name script/graphics/descriptor |
| +18/+1C tail1_raw/tail2_raw | CONFIRMED structural attachment, semantics UNKNOWN | F6D2/F6D6 passes address placement+18 to A93C; A956 retains that address. No VM/script/event interpretation |

No direct dialogue reference is established. A separately passed construction
argument and retained configuration exist; this does **not** establish that
changing only +08 is compatible with them. Type reassignment stays unsupported.
No ROM mutation was made just to demonstrate a type change.

## Corpus measurements and corrections

**OLD CLAIM:** TOOLKIT-008 recorded 111 distinct +08 values as though measured
over the supported 1,295 records.

**NEW EVIDENCE:** enumeration through the unchanged supported placement walker
returns **101** distinct selectors, independently remeasured twice.

**RESOLUTION:** 101 is canonical for this corpus. The source of the old 111 is
not established. No change to 1,295 placements, 215 maps, their extents or ownership.

| Quantity | Result |
| --- | ---: |
| Placement -> static target coverage | 1,295 / 1,295 |
| Unique selectors / unique physical targets | 101 / 101 |
| Targets in existing enemy-stat extent | 95 |
| Placements structurally linked to existing enemy identity | 1,284 (99.15%) |
| Targets beyond verified enemy-stat extent | 6, used by 11 placements |
| Shared types (more than one placement) | 67 |
| Single-placement types | 34 |
| Types shared across maps | 67 |
| Maximum placements / maps for one type | 69 / 36 |
| Factory wrappers / reached common constructors | 1 / 1 |
| Supported record sharing between maps | 0, unchanged |

Outside the existing enemy extent: selectors **141 (1 placement), 142 (6),
146 (1), 147 (1), 148 (1), 149 (1)**. The constructor computes these targets,
but that does not prove that each is an ordinary 28-byte enemy record.
Independent review found selector 141 fails the existing stat shape predicate;
therefore a uniform stat-table extension would be especially unjustified.
No new enemy records, new type records, or extended table count are authored.

Placements-per-type histogram (`placements: number of types`):
`1:34, 2:2, 3:1, 4:3, 5:2, 6:5, 7:2, 8:2, 9:2, 10:2, 11:2, 12:6,
13:3, 15:2, 16:2, 17:5, 18:1, 19:1, 20:1, 21:3, 22:2, 23:1, 24:1,
25:2, 26:1, 28:1, 30:1, 31:2, 37:1, 38:1, 40:1, 43:1, 47:1, 50:1,
60:1, 63:1, 69:1`.

Maps-per-type histogram (`maps: number of types`):
`1:34, 2:3, 3:2, 4:3, 5:4, 6:10, 7:6, 8:7, 9:3, 10:6, 11:5, 12:5,
13:1, 14:1, 15:2, 16:2, 18:2, 19:1, 24:1, 30:1, 33:1, 36:1`.

## Identity, graph, project, and codec boundaries

`profile-id/placement_type:NNNN` is rooted in the engine selector. Placement
identity remains `map:NNNN/placement:NNNN`. Physical targets and runtime object
pointers are separate; no EWRAM identity is used.

For example **selector 1 -> target 08711290 -> enemy:0023**, not enemy:0001.
The exact enemy key is obtained from the selected verified record, never a
nearby number, sprite, runtime slot, or upstream label. This proves an enemy-stat
association; it does not prove aggression, friendliness, AI, or a human name.

`PlacementTypes.factory_of(type_id)` exposes the shared wrapper and constructor.
There is no per-type factory pointer proven inside the selected stat records.
The common reference graph contains **4,100** confirmed references: 215 map-array
pointers plus 1,295 array-placement, placement-factory, and indexed placement-type
references each. Index encoding includes an explicit table base and stride;
it is read-only and refuses relocation encoding/reassignment. Candidate graph
references retain existing fail-closed behavior.

Graph type anchors use the existing enemy owner where verified: the type and
enemy are two identities for the **same physical record**, not a fabricated
pointer edge between duplicate records. Six unknown target anchors cover only
the entry address (one byte for graph membership), explicitly not a record size.
All these anchors are non-relocatable. Constructor calls remain documented
control flow, not misencoded as absolute data-pointer references.

The existing pure enemy-stat codec covers **95 selected records / 2,660 bytes**,
exhaustively byte-exact. No duplicate type codec was created; the other six
targets are **reference-only**, with record extent and codec UNKNOWN. All 141
existing enemy records remain owned/edited through the stat subsystem.

Optional v1 project file `placement_types/types.toml` deduplicates the shared
types and maps placement IDs to type IDs. It carries no second copy of stat
bytes, no human aliases, and no addresses needed for semantic queries. Builds
validate any present catalog against the verified base and reject edits to it.
Older v1 projects without this optional file remain loadable/buildable.
Existing map-position/stat/text editing remains the authoring surface.

## Capability rungs and deferred questions

| Family | Rung / scope |
| --- | --- |
| Placement records | ROUND_TRIP + position EDIT; unchanged 1,295 |
| Placement type references | DECODE, 1,295; reassignment unsupported |
| Shared selected type records | ROUND_TRIP through existing stat codec, 95; remaining 6 reference-only |
| Factory classification | DECODE structural indexed-stat constructor, 1 wrapper/1 common constructor |
| Enemy linkage | DECODE confirmed stat identity, 95 types/1,284 placements |
| NPC/friendly actor linkage | UNKNOWN |
| Item/pickup linkage | UNKNOWN |
| Script/event attachment | UNKNOWN; retained configuration location alone is not script semantics |
| Graphics/resource attachment | UNKNOWN; no sprite/graphics identity promoted |
| AUTHOR_NEW | Unsupported |

Unresolved: six out-of-stat-extent targets and their actual extents, flags,
remaining construction arguments/configuration, type-swap compatibility,
human names/behavior, script/event/graphics attachment. Coordinate semantics are
now established for the supported Buu placement constructor: signed raw low/high
halfwords are map/world X/Y pixels (`PLACEMENT_POSITION_PROVENANCE.md`, Phase 3).
None warrants expanding TOOLKIT-009 into gameplay RE.

## Addendum 2026-09-21 - `+0x10 id_raw` is a sprite id

Source: HUMAN-4-SPAWN-LOOKUP-001 and HUMAN-4-USAGE-CLOSURE-001 (recorded by
HUMAN-4-RESEARCH-CAPTURE-001); read-only static work on the canonical image.

Two statements above are refined, not overturned:

* the field-audit row `+10 id_raw | CONFIRMED load, semantics UNKNOWN` - the load
  is `0x0800F6AE ldr r0,[r5,#0x10]` followed by `0x0800F6B0 bl 0x08000158`, so the
  field is a **sprite id**: the resolver indexes the actor character pointer table
  `0x086B6BDC` at `argument - 10`, and a curated sprite id is `run index + 10`.
  Arguments below 10 take the player/party path instead;
* the capability row `Graphics/resource attachment | UNKNOWN` - graphics identity
  is now decodable from the record itself through that field.

Still standing: `NPC/friendly actor linkage | UNKNOWN`, `Item/pickup linkage |
UNKNOWN` and `Script/event attachment | UNKNOWN`. Nothing here classifies a
placement as an NPC, friendly, item or enemy, and no `+0x10` **write** is
authorised - the constructor's remaining arguments and type-swap compatibility are
untouched. The same field contract holds for the two sibling families
(`0x08017DA3` at `+0x10`, `0x080111A9` at `+0x0C`). Full statement and the
map-object census result: [actor sprite graphics](GRAPHICS_FORMAT.md) §12 and
[map object arrays](BUU_MAP_OBJECT_ARRAYS.md).

Validation and independent final review results are recorded in
`../tickets/TOOLKIT-009-review.md` after completion.
