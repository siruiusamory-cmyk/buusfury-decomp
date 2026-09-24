# CQA-03-15-IDENTITY-AND-EXTENTS-001, ROM/atlas identity refusal and single-source extents

Audit findings: [`../research/PROJECT_CODE_QUALITY_AUDIT.md`](../research/PROJECT_CODE_QUALITY_AUDIT.md)
sections C.2 (CQA-03, CQA-15) and the section F group table.

| | |
| --- | --- |
| Start SHA | `170dc8151b6cf0b7dba9cf2454708ff67d6522fd` (`origin/master`) |
| Frozen SHA | `1067a539a0e1215043812be3d80e39bdd9272e06` |
| Correction commit | `03779c2`, data-contract hash authority (made before review began; the frozen candidate was not amended) |
| Ticket | CQA-03 [HIGH] + CQA-15 [MEDIUM], audit group C |
| Scope | identity refusal, one atlas/ROM identity contract, single-source profile extents |
| Product capability | none: `READ 5/5`, `EDIT 4/8`, `AUTHOR 3/7`, `DELIVER 4/4`, 16/24, 67% |
| `public progress impact` | `NONE`, internal identity guard and duplicate-authority removal, no user-visible capability, frontier or questline change |
| CQA-04 | **still open** (the duplicated decode stacks were deliberately not touched) |
| ROM-CAPACITY-AND-ALLOCATION-001 | **still blocked** |

---

## 1. CQA-03, the defect, reproduced before it was fixed

`Session.open_rom` identified the ROM, resolved the profile, loaded the one
global `build/atlas/atlas.jsonl` and assigned it, **never comparing the atlas's
own `profile_id` / `base_sha256` with the identity it had just verified**.
`Atlas.validate()` checks only internal self-consistency, so a Buu-built atlas
paired with a different image was accepted silently, and every offset, coverage
class and `VERIFIED_FREE` span then described bytes that were not there.

### Reproduction, no second commercial ROM required

`tools/qa/cqa03_atlas_identity_probe.py` drives the **real** `Session.open_rom`
with the identification stubbed to a verified catalog profile and only the atlas
identity varied. Recorded pre-fix, on the unmodified tree:

```text
wrong profile id (same image):    refused = False, atlas in session state = True
correct profile id, wrong base:   refused = False, atlas in session state = True
matching identity:                refused = False, atlas in session state = True
RED
```

Both mismatches were **accepted**. Post-fix:

```text
wrong profile id (same image):    refused = True,  atlas in session state = False
correct profile id, wrong base:   refused = True,  atlas in session state = False
matching identity:                refused = False, atlas in session state = True
GREEN
```

The same matrix is pinned permanently in `tests/unit/test_atlas_identity.py`,
which needs no ROM and so runs on every checkout.

### The one shared identity owner

`tools/webfoot/profile.py`:

| symbol | role |
| --- | --- |
| `AtlasIdentity` | the base image an atlas describes: `profile_id`, `base_sha256`, `image_size` |
| `AtlasIdentityMismatch` | the typed refusal, carrying expected **and** actual identity |
| `RomProfile.identity` | the profile's one statement of its canonical identity |
| `RomProfile.require_identity(atlas)` | **the single comparison rule for the whole product** |

Ownership sits in the profile/atlas domain, not in the Workbench, the CLI or any
editor. It is a factory-free method on `RomProfile` that reads the atlas's
identity **structurally**, so `webfoot.profile` does not import `webfoot.atlas`
(no cycle) and a value that does not declare the triple is refused by name
rather than defaulted. Both halves are checked, plus image size, because each
alone is insufficient: the id alone would accept a differently-revised dump of
the same game, the hash alone would accept an atlas whose offsets were resolved
against another profile sharing the image, and a differently-sized atlas cannot
describe this image even when both named values agree.

### Canonical vs derivative rules (section 4 of the ticket)

The existing derivative-trust model was determined from the repository, not
invented:

- **Canonical ROM.** `identify_rom` matches a profile exactly; the atlas must
  declare **that profile's** identity. `require_identity` is called with
  `match_profile`.
- **Trusted derivative** (`map_layout_provenance.verify_authored_rom`). The
  manifest names the canonical base by profile id and SHA-256, the file's own
  digest must equal the manifest's declared output digest, and restoring every
  declared `old` byte must reproduce the canonical image **exactly**. So, before
  the atlas is consulted, the session has already proved
  `authored.canonical_sha256 == match_profile.sha256`
  (`session.py`, the derivative branch), and the atlas must declare that same
  canonical base identity.

A derivative's **output** bytes hash differently from the canonical image, and
that is correct and intended: every accepted reader runs against the
reconstructed canonical bytes (`Session.map_image`), so the atlas is required to
describe the canonical base, **not** the derivative's output digest. The
ticket's warning, do not make a derivative appear to need a rebuilt atlas
merely because its current output SHA differs, is satisfied by construction,
and `test_E_a_derivative_is_checked_against_its_canonical_base` pins both halves
of it. No second derivative identity system was created.

### Fail-closed behaviour (sections 5, 19, 20)

- The comparison runs **before** `self.atlas = atlas` and before `maps` /
  `text_strings` are loaded, so a refusal leaves the session untouched: the
  probe and tests assert `session.atlas is None`, `session.profile is None`,
  `session.rom_image is None` after a refusal.
- The failure is raised as the established `SessionError` on the Workbench path
  (the product exception family its tabs already catch), from the typed
  `AtlasIdentityMismatch`, and the message names both identities.
- **No silent rebuild** and no automatic atlas regeneration: generation stays
  explicit evidence-producing work. The message points at the existing
  `atlas build` command.
- No classification is downgraded and the open continues; the open is refused.
- `test_verified_free_evidence_cannot_reach_a_mismatched_base` is the focused
  regression the ticket asks for: a structurally valid atlas carrying a real
  `VERIFIED_FREE` span built for another profile is refused, and the same span
  under the right identity is accepted, so the refusal is about identity, not
  about the classification.

### Other production ROM+atlas paths

Audited by grep for every `load_atlas` / atlas-consuming production path. The
Workbench `open_rom` was the only production path that **combined a ROM/profile
identity with an atlas** and assigned it to live state. The CLI's atlas
subcommands (`cli.py`) operate on the atlas artifact alone, `atlas coverage`,
`atlas find`, `atlas refs` take no `--rom`, so there is no ROM identity for
them to disagree with. `atlas text --rom` opens the ROM only for the text
search path; that path is reached from the Workbench through
`Session.open_rom`, which is now guarded, and `handles.recover_handle`'s own
profile-contract gap is audit finding **CQA-16**, explicitly out of this
ticket's scope.

---

## 2. CQA-15, the inventory, re-run against the current tree

The audit's list was 25 commits old and materially incomplete. Re-run by
measurement (owner + an independent read-only delegate), the corrections are:

| # | Audit said | Measured on `170dc815` |
| --- | --- | --- |
| 1 | `placement_links.py:305` restates the text count | it **reads** `placement_contracts.py:60`. `placement_contracts.py:60` and `script_effects.py:11` are two live index bounds the audit missed |
| 2 | `GBA_ROM_BASE` in "eight modules under three spellings" | **11** production modules under **four** spellings, plus **2** using a bare `0x08000000` = **13** |
| 3 | SHA list | omitted live gates in `tools/qa/visual_pass_capture.py`, `tools/mgba_probe/runtime.py` + the emulator patch, `tools/runtime/rom006_gdb_probe.py`, seven `tools/ghidra/*.java`, eight `tools/research/*_probe.py` |
| 4 | text count `1534` in six | omitted `pool_size 82874`; and `canonical.py:480` spelled the pointer stride `* 4` instead of the codec's width |
| 5 | `placement_contracts.py:61` `text_table` | a declared-but-**never-read** key, so stale |
| 6 |, | `formats/stat_tables.py` `BASE_STAT_NAMES` is a per-game Buu roster literal live in production via `stats.character_alias` |

### Migrated: live duplicates that drove production behaviour

| value | was owned by | now owned by |
| --- | --- | --- |
| canonical SHA-256 | `map_render.SUPPORTED_ROM_SHA256`, `export/map_browser.SUPPORTED_ROM_SHA256`, `export/buu_resource_export.CANONICAL_ROM_SHA256`, `atlas_build.BASE_SHA256`, `atlas_producers/graphics_extents.EXPECTED_SHA`, `atlas_producers/code_functions.EXPECTED_SHA` | `profile.py` via the packaged catalog; `tools/export/profile_authority.py` for the export stack |
| canonical SHA-256 (**2 live gates**) | `data/placement_contracts.py` `CONTRACTS[id]['sha256']`, `data/behavior_triggers.py` `BEHAVIOR_TRIGGER_CONTRACTS[id]['sha256']`, compared at `authored_placements.py:236` and `placement_events.py:40` | compared against `profile.sha256`; the contract value stays as a cross-check asserted for every catalogued profile |
| atlas profile id / image size | `atlas_build.PROFILE_ID` + `IMAGE_SIZE` literals | same profile's `identity` |
| MapEntry table address | `export/canonical.MAP_ENTRY_TABLE_ADDRESS`, `map_render.MAP_ENTRY_TABLE_ADDRESS` | `RomProfile.map_entries.address` (through `Rom.map_entry_table_address()`, `map_render.resolve_entry_table`, `MapLayoutEditor.map_entry_count`) |
| MapEntry count (**4 live bounds**) | `export/canonical.MAP_ENTRY_COUNT` (+ its 6 readers) | `RomProfile.map_entries.count` |
| MapEntry stride | `canonical.MAP_ENTRY_STRIDE = 0x38`, `map_render` via `me.MAP_ENTRY_SIZE` | `profile.map_entries.record_size`; the format width stays in `formats/map_entry` |
| text pointer table address | `export/canonical.TEXT_POINTER_TABLE_ADDRESS` | `RomProfile.text_strings` |
| text pointer count (**live index bound**) | `export/canonical.TEXT_POINTER_COUNT` | `RomProfile.text_strings.count` |
| text count (**3 more live bounds**) | `placement_contracts['dialog_text']['count']`, `script_effects['text_count']` | the loaded profile's `text_strings.count`, threaded to the consumer |
| text pool / table extents (dead copies) | `formats/text_tables.TEXT_ENTRY_COUNT` / `TEXT_TABLE_START` / `TEXT_POOL_START` / `TEXT_POOL_END` | deleted; the codec's extent-taking functions now take them from the caller |
| stat table address / count | `formats/stat_tables.ENEMY_TABLE_START`-family read as live bounds | `RomProfile.enemy_stats` / `.character_base_stats`; `character_identity` takes the caller's count |
| object palette address | `export/canonical.OBJECT_PALETTE_ADDRESS` | `RomProfile.actor_sprites.object_palette_address` |
| GBA ROM base | 13 production definitions under 4 spellings + 2 bare literals | `tools/webfoot/binary.GBA_ROM_BASE`, aliased where a name is public API |
| pointer stride `4` | `export/canonical.py:480` as `index * 4` | `formats/text_tables.TEXT_POINTER_SIZE` |

### One new module

`tools/export/profile_authority.py`, resolves the export readers' profile from
the **packaged** catalog (the same trusted in-repo authority
`webfoot.capability` uses). It stores no address, count or hash; every value is
read through the resolved `RomProfile` at the point of use. Thin on purpose: a
"master constants module" would have been a new second owner rather than the
removal of one.

### Where the extents now live on the export reader

`export/canonical.Rom` carries the profile and exposes
`map_entry_count()`, `map_entry_table_address()`, `map_entry_stride()`,
`text_table()` and `object_palette_address()`. The module-level
`MAP_ENTRY_TABLE_ADDRESS`, `MAP_ENTRY_COUNT`, `TEXT_POINTER_TABLE_ADDRESS`,
`TEXT_POINTER_COUNT` and `OBJECT_PALETTE_ADDRESS` are **gone**, and
`test_profile_authority_contract.py` asserts their absence so they cannot be
reintroduced quietly.

---

## 3. Retained literals, classification (section 21 of the ticket)

The defect was multiple independent **behaviour-driving authorities**, not
repetition. Each retained copy is classified; there is no unexplained
load-bearing duplicate.

| class | meaning |
| --- | --- |
| **A** | authoritative profile data (`config/roms.yaml`, `tools/webfoot/data/roms.yaml`) |
| **FMT** | format constant: true for every image of this format, not one game |
| **EVID** | evidence / provenance label: a record of what was verified, not a runtime authority |
| **ORACLE** | independent test oracle: a second measurement that must be able to disagree |

### Format constants (FMT)

| value | owner | why it is not per-game |
| --- | --- | --- |
| `0x08000000` GBA ROM base | `webfoot/binary.GBA_ROM_BASE` | the Game Pak ROM window base; every GBA image shares it |
| `0x38` MapEntry record size | `webfoot/formats/map_entry.MAP_ENTRY_SIZE` | the record shape; LOGII has a `0x38`-stride table too, so the stride alone is not Buu identity |
| `4` pointer-table entry width | `webfoot/formats/text_tables.TEXT_POINTER_SIZE` | one little-endian GBA address |
| `0x0000` / `0x0008` / `0x000A` | `formats/text_tables` | string terminator and control units |
| `0x1C` / `0x12` stat record strides | `formats/stat_tables` | record shapes the codec enforces; asserted against the profile's `record_size` |
| `0x2C` MapEntry scene-pointer offset | `webfoot/formats/map_entry`, `map_render.MAP_ENTRY_SCENE_POINTER_OFFSET` | field position inside the record |
| `1024`, `0x800`, `256`, `32` | `export/canonical`, `map_render`, `formats/bg_tilemap` | GBA screenblock / chunk geometry |
| handler addresses `0x08008087` etc. | `export/canonical`, `map_render.SUPPORTED_LAYER_HANDLER` | the accepted layer forms this renderer implements, a **capability** limit, stated as a gate, not an identity literal |
| `256` palette entries | `canonical.OBJECT_PALETTE_ENTRIES`, `map_render.BG_PALETTE_ENTRIES` | OAM/BG palette size |

### Evidence / provenance labels (EVID)

| value | location | why retained |
| --- | --- | --- |
| canonical profile id in `atlas_build.PROFILE_ID` | `webfoot/atlas_build.py` | the one id this assembler stamps into atlas provenance; hash and size are read from it, not restated |
| canonical profile id in `export/profile_authority.CANONICAL_EXPORT_PROFILE_ID` | `tools/export/` | names which catalog entry the export readers resolve; the values come from it |
| `map_render._CANONICAL_PROFILE_ID` | `webfoot/map_render.py` | the Buu-only default profile for callers that supply none; identity is still compared against the bytes |
| `EXPECTED_SHA` in `code_functions.py` | atlas producer | read from the packaged profile, so it is a view of A, not a rival copy |
| `ENEMY_TABLE_START`/`LAST`/`COUNT`, `BASE_STAT_TABLE_START`/`COUNT` | `formats/stat_tables.py` | the **measured extent**, kept as the evidence a ticket verified; their only readers are `iter_enemy_records` / `iter_base_stat_records`, which have **no production caller**. A test asserts they still describe a whole number of records and that the profile's GBA address equals their file offset plus the sanctioned base |
| `BASE_STAT_NAMES` | `formats/stat_tables.py` | the INFERRED Buu display roster (not an identity). Now guarded: `character_alias` refuses an index past the verified names instead of wrapping, and `stats` is gated on the profile's declared count |
| `PROFILE_ID` keys in `data/placement_contracts.py`, `data/script_effects.py`, `data/behavior_triggers.py`, `data/script_specs.py` | `webfoot/data/` | these dicts are **selected by** profile id; the id is the selector. Their per-game **counts** were removed and are read from the profile |
| `tools/research/*_probe.py`, `tools/runtime/*.lua`, `tools/ghidra/*.java`, `tools/mgba_probe/`, `tools/qa/` literals | research / probe / runtime tooling | independent measurements used to *check* production. CQA-15 is about production behaviour-driving authorities; a probe that imported its expectations from the code under test could not detect that code drifting. Two probes were updated from the deleted codec constants to their own measured literals for exactly this reason |
| provenance strings inside atlas producers (`seed.py` prose, `evidence` fields) | atlas producers | reported into the atlas artifact, never branched on |

### Independent test oracles (ORACLE)

| value | location | why retained |
| --- | --- | --- |
| `940ad5f0…f059e` | ~46 test sites (`tests/conftest.py`, per-file `CANONICAL_SHA`) | pins the local image to the expected identity; a test that read the hash from the code under test would detect nothing |
| `1534`, `0x0005792C`, `0x0006BCE6`, `0x0006BCE8` | `tests/integration/test_text_rom.py` | the ticket's own words: repeated rather than imported so the test fails if the profile drifts |
| MapEntry address/count/stride | many integration tests | same |
| `452`, `0x0808E2E0` in `tests/unit/test_map_render.py` | replaced by a **synthetic non-Buu profile** | the old form could not fail; the new form fails if a Buu literal is reintroduced |
| stat extents | `tests/unit/test_stat_tables.py`, `tests/integration/test_stat_tables_rom.py` | independent measurement of the same bytes |

---

## 4. Synthetic-profile proof (sections 16, 24.8)

`tests/unit/test_extent_profile_authority.py`, no commercial ROM, no
constant-to-constant comparison. A profile is built from the canonical one by
replacing **every** load-bearing extent with a different value (different id,
different SHA, map table at `0x08400000` with count 3, text table at
`0x08410000` with count 2, pool at `0x08420000`), and the production readers are
driven through it:

| assertion | fails if |
| --- | --- |
| `canon.Rom(..., profile=synthetic).map_entry_count() == 3` | a Buu count literal is reintroduced |
| `read_map_entries` returns exactly 3 records at the synthetic address; a larger declared count returns more | the loop bound is not the declaration |
| `mb._check_map_index` accepts 2 and refuses 3 | the browser bound is not the declaration |
| `Rom.text(0) == "AB"`, `text(1) == "CD"`, `text(2) is None` | the text index bound is not the profile's |
| a profile declaring count 3 bounds differently from one declaring 2 | the bound is not read per profile |
| `map_render.resolve_descriptor(..., profile=synthetic)` returns the synthetic row | the renderer's table address is not the profile's |
| a profile declaring no map table is refused by name | the renderer defaults a table |
| the four `GBA_ROM_BASE` spellings all equal `binary.GBA_ROM_BASE` | a base is redefined |
| the stat strides equal the profile's `record_size`; `character_identity(n, n)` refuses | a stat bound is a literal |
| `config/roms.yaml` and the packaged catalog are byte-identical | the two catalog copies drift |
| every `data/*` contract's `sha256` equals its profile's declaration, for every catalogued profile | a contract hash drifts from the catalog |

`test_profile_authority_contract.py` additionally asserts the **absence** of
every removed symbol (`map_render.SUPPORTED_ROM_SHA256`,
`map_render.MAP_ENTRY_TABLE_ADDRESS`, `canon.MAP_ENTRY_COUNT`,
`canon.TEXT_POINTER_COUNT`, `text_tables.TEXT_ENTRY_COUNT`, …), so a
reintroduced duplicate fails even before it disagrees with anything.

---

## 5. Profile validation (section 15)

Reused, not rebuilt: `RomProfile.from_mapping` already validates that every
declared address is inside the GBA ROM window, that counts and strides are
positive, that the pointer table and pool tile their declared extents, and that
each extent ends inside the image (`profile.py`). This ticket added only the
identity-value invariants `AtlasIdentity.__post_init__` needs (non-empty id and
hash, positive image size) and the length/alignment checks the codec gets from
`stat_tables`. No second schema framework.

---

## 6. Focused validation

| suite | result |
| --- | --- |
| `tests/unit` (portable, whole directory) | **2141 passed, 23 skipped, 0 failed** (at `03779c2`; `2140` at the frozen SHA, before the extra contract-equality test) |
| `tests/integration` (whole directory; ROM-gated families skip, no ROM in this worktree) | **28 passed, 973 skipped, 0 failed** |
| `tests/unit/test_atlas_identity.py` (new) | 17 passed |
| `tests/unit/test_extent_profile_authority.py` (new) | 12 passed |
| `tests/unit/test_profile_authority_contract.py` (new) | 11 passed |
| `git diff --check` | clean, exit 0 |
| canonical ROM | **absent from this worktree**; never read, hashed or written |
| full suite | **NOT MANUALLY RUN**, human policy; focused validation only |

Measured and derived are kept separate above: the unit/integration totals were
directly observed by running each directory; nothing here is an expected
aggregate.

The ROM-gated families (`test_map_layout_editor_rom`, `test_map_layout_write_rom`,
`test_map_browser_rom`, `test_text_rom`, `test_stat_tables_rom`, the Workbench
ROM tests) **skipped** here because no canonical image is configured in this
worktree. Their call sites were updated for the new signatures; they must be run
where the canonical ROM is available, and this record should not be read as
evidence that they passed.

### Mutation results

Performed on isolated scratch edits, each reverted immediately and verified
byte-identical afterwards.

| mutation | change | expected | result |
| --- | --- | --- | --- |
| **M1** profile-id check bypass | `require_identity`: id comparison disabled | mismatch regression fails | **PASS**, 3 tests failed (`test_B_wrong_profile_id_is_refused`, `test_session_refuses_a_wrong_profile_atlas`, `test_verified_free_evidence_cannot_reach_a_mismatched_base`) |
| **M2** base-SHA check bypass | `require_identity`: base comparison disabled | same-profile/wrong-base fails | **PASS**, 3 tests failed (`test_C_correct_profile_id_wrong_base_sha_is_refused`, `test_session_refuses_a_wrong_base_atlas`, `test_E_a_derivative_is_checked_against_its_canonical_base`) |
| **M3** reintroduced Buu literal | `map_browser._check_map_index`: `count = 452` instead of `rom.map_entry_count()` | synthetic-profile test fails | **PASS**, `test_the_map_browser_index_bound_is_the_profiles` failed |

After all three: files restored byte-identically (hash-compared), no
`MUTATION` / `if False` marker anywhere in the tree, all focused tests green.

---

## 7. What this ticket did **not** do

- **CQA-04 stays open.** The two map/graphics decode stacks were not
  consolidated, merged or re-pointed at each other. `map_render` and
  `export/canonical` remain separate readers; only their *profile identity and
  extents* were moved onto one authority, which is what the ticket asked for.
- No Workbench state-destruction fix (CQA-05), no Session error-family work
  beyond the identity refusal (CQA-06), no graphics performance work (CQA-07),
  no CI changes (CQA-08), no capacity or allocation work.
- No product capability was broadened. `map_render` remains Buu-only in what it
  can *render* (one layer handler form, one palette address), but that limit is
  now stated by the profile gate and named in the refusal, rather than carried
  as an accidental SHA literal. `handles.recover_handle`'s missing profile
  argument (CQA-16) was not touched.
- No generic configuration framework and no repo-wide magic-number
  normalisation. `tools/research/`, `tools/runtime/` and `tools/ghidra/`
  literals were left as independent measurements.

## 8. Remaining related debt

- **CQA-16**, `handles.recover_handle` still selects one profile's contract by
  literal key inside a profile-free API. Directly adjacent to this ticket and
  **not fixed here**; it is the next identity-adjacent finding.
- **CQA-17**, `placement_types.table_address` and `enemy_stats.address` both
  declare `0x08711274` in the profile, and `entities.py` mints a CONFIRMED link
  from address alignment rather than from the shared declaration.
- `formats/stat_tables.BASE_STAT_NAMES` is still an unprofiled per-game roster;
  it is now guarded against wrapping but should become profile data.
- The export stack still reads through `tools/export/canonical.py` rather than
  the SDK's `formats` layer (that dependency *is* CQA-04).
- Line endings: `tools/webfoot/profile.py` is one of the nine documented
  mixed-ending files; the edit to it was applied with the byte-safe line-indexed
  recipe in `../line-endings.md` after an editor round-trip was detected and
  reverted. Its CRLF count is unchanged at 732.
