# ROM and atlas identity refusal with single-source extents

One atlas and ROM identity contract, fail-closed refusal on mismatch, and a
single source for per-profile extents.

Audit findings: [`PROJECT_CODE_QUALITY_AUDIT.md`](PROJECT_CODE_QUALITY_AUDIT.md)
sections C.2 (CQA-03, CQA-15) and the section F group table.
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

### Canonical vs derivative rules (section 4 of the record)

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
record's warning, do not make a derivative appear to need a rebuilt atlas
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
  regression the record asks for: a structurally valid atlas carrying a real
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
record's scope.

---

## 2. CQA-15, the inventory, re-run against the current tree

The audit's list was 25 commits old and materially incomplete. Re-run by
measurement (a lead and an independent read-only delegate), the corrections are:

| # | Audit said | Measured on `680f70bd85d6c1866e3749b8791753130266d300` |
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

## 3. Retained literals, classification (section 21 of the record)

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
| `256` palette entries, `768` background-palette bytes | `canonical.OBJECT_PALETTE_ENTRIES` / `BG_PALETTE_ENTRIES` / `BG_PALETTE_BYTES`, `map_render` | palette sizes: OAM is 256 halfwords, the global BG palette 256 RGB888 triples. The **addresses** are the profile's (`tables.actor_sprites.object_palette_address` / `bg_palette_address`), read through `Rom.object_palette_address()` / `Rom.bg_palette_address()` and `map_render._bg_palette_address` |

### Evidence / provenance labels (EVID)

| value | location | why retained |
| --- | --- | --- |
| canonical profile id in `atlas_build.PROFILE_ID` | `webfoot/atlas_build.py` | the one id this assembler stamps into atlas provenance; hash and size are read from it, not restated |
| canonical profile id in `export/profile_authority.CANONICAL_EXPORT_PROFILE_ID` | `tools/export/` | names which catalog entry the export readers resolve; the values come from it |
| `map_render._CANONICAL_PROFILE_ID` | `webfoot/map_render.py` | the Buu-only default profile for callers that supply none; identity is still compared against the bytes |
| `EXPECTED_SHA` in `code_functions.py` | atlas producer | read from the packaged profile, so it is a view of A, not a rival copy |
| `ENEMY_TABLE_START`/`LAST`/`COUNT`, `BASE_STAT_TABLE_START`/`COUNT` | `formats/stat_tables.py` | the **measured extent**, kept as the evidence a record verified; their only readers are `iter_enemy_records` / `iter_base_stat_records`, which have **no production caller**. A test asserts they still describe a whole number of records and that the profile's GBA address equals their file offset plus the sanctioned base |
| `BASE_STAT_NAMES` | `formats/stat_tables.py` | **the one remaining per-game literal in this layer, and the verification pass was right to name it.** An INFERRED Buu display roster, live in production via `stats.character_alias` for `CharacterEntry.alias`. It is not a duplicate authority (nothing else declares it), but it is not format data either. Now guarded rather than silently reused: `character_alias(index, count)` refuses a profile whose declared roster is not this one, and refuses an index past the verified names. Owning it as profile data is recorded debt (section 8) |
| `PROFILE_ID` keys in `data/placement_contracts.py`, `data/script_effects.py`, `data/behavior_triggers.py`, `data/script_specs.py` | `webfoot/data/` | these dicts are **selected by** profile id; the id is the selector. Their per-game **counts** were removed and are read from the profile. Their `sha256` fields were **live gates** and are now compared against `profile.sha256` (review finding 1) |
| `940ad5f0…f059e` in production | **two sites, both cross-checks, no gate** | the literal survives as data at `data/behavior_triggers.py:12` and `data/placement_contracts.py:518`; it is no longer an authority and no longer gates, because all four comparisons that read it compare it against `profile.sha256` (`maps.py:830`, `authored_placements.py:120`, `authored_placements.py:245`, `placement_events.py:44`), and `test_the_data_contract_hashes_agree_with_the_profile` pins each value to its catalog declaration. An earlier draft of this row said "none left", which was false as written: the literals are still present, they simply no longer decide anything |
| `tools/research/*_probe.py`, `tools/runtime/*.lua`, `tools/ghidra/*.java`, `tools/mgba_probe/`, `tools/qa/` literals | research / probe / runtime tooling | independent measurements used to *check* production. CQA-15 is about production behaviour-driving authorities; a probe that imported its expectations from the code under test could not detect that code drifting. Two probes were updated from the deleted codec constants to their own measured literals for exactly this reason |
| provenance strings inside atlas producers (`seed.py` prose, `evidence` fields) | atlas producers | reported into the atlas artifact, never branched on |

### Independent test oracles (ORACLE)

| value | location | why retained |
| --- | --- | --- |
| `940ad5f0…f059e` | ~46 test sites (`tests/conftest.py`, per-file `CANONICAL_SHA`) | pins the local image to the expected identity; a test that read the hash from the code under test would detect nothing |
| `1534`, `0x0005792C`, `0x0006BCE6`, `0x0006BCE8` | `tests/integration/test_text_rom.py` | the record's own words: repeated rather than imported so the test fails if the profile drifts |
| MapEntry address/count/stride | many integration tests | same |
| `452`, `0x0808E2E0` in `tests/unit/test_map_render.py` | replaced by a **synthetic non-Buu profile** | the old form could not fail; the new form fails if a Buu literal is reintroduced |
| stat extents | `tests/unit/test_stat_tables.py`, `tests/integration/test_stat_tables_rom.py` | independent measurement of the same bytes |

---

## 4. Synthetic-profile proof (sections 16, 24.8)

`tests/unit/test_extent_profile_authority.py`, no commercial ROM, no
constant-to-constant comparison. A profile is built from the canonical one by
replacing **every** load-bearing extent with a different value (different id,
different SHA, map table at `0x08400000` with count 3, text table at
`0x08410000` with count 2, pool at `0x08420000`, object palette at `0x08430000`,
background palette at `0x08440000`), and the production readers are driven
through it:

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
| `render.object_palette_rgb` returns the palette that exists only at the synthetic address | the object palette address is a literal |
| `render.bg_palette_rgb` and `map_render.decode_bg_palette` return the palette that exists only at the synthetic address | the background palette address is a literal |
| `MapLayoutWriter`'s identity gate reads `profile_authority`, owns no hash, and bounds by `map_entry_count()` | the writer restates the hash or the count |
| a profile declaring a 1,000-entry text table refuses index 1,525 that the canonical profile accepts | the text bound is a literal (the canonical count is 1,534, so a same-count check proves nothing) |

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
each extent ends inside the image (`profile.py`). This record added only the
identity-value invariants `AtlasIdentity.__post_init__` needs (non-empty id and
hash, positive image size) and the length/alignment checks the codec gets from
`stat_tables`. No second schema framework.

---

## 6. Focused validation

Two stages are reported, because the second pass found real defects the first
could not.

### Stage 1, frozen candidate (`7ca59792d9b97a4de4887cb54b1732926f4f6172`), no ROM and no PySide6 in the worktree

| suite | result |
| --- | --- |
| `tests/unit` (portable, whole directory) | **2140 passed, 23 skipped, 0 failed** |
| `tests/integration` (whole directory) | **28 passed, 973 skipped, 0 failed** |
| `tests/unit/test_atlas_identity.py` (new) | 17 passed |
| `tests/unit/test_extent_profile_authority.py` (new) | 12 passed |
| `tests/unit/test_profile_authority_contract.py` (new) | 11 passed |
| `git diff --check` | clean, exit 0 |
| canonical ROM | **absent from the working copy**; never read, hashed or written |

**The weakness of stage 1, stated plainly:** the ROM-gated families
(`test_map_layout_editor_rom`, `test_map_layout_write_rom`, `test_map_browser_rom`,
`test_text_rom`, `test_stat_tables_rom`, the Workbench ROM tests) **skipped**
because no canonical image was configured, and every Workbench GUI test skipped
because PySide6 was not installed. Three of the ROM-gated files were in fact
broken by this record (review finding 2), and five Workbench defects were hidden.
A green `tests/unit` total with 23 skips was **not** adequate evidence, and the
claim in an earlier draft of this record that the ROM-gated call sites "were
updated for the new signatures" was false for three files.

### Stage 2, corrected revision, PySide6 + canonical ROM + atlas configured

Running the previously-skipping gates exposed five further record-caused defects
(section 9). Section 9 also holds the full focused-command list, the historical
broad measurements with their commits, and the test-policy statement.

**BROAD / FULL SUITE: NOT MANUALLY RUN, HUMAN POLICY.** A broad `tests/unit` run
was started once after the `cff4a75448309be70480a97a63922b5462d06c1b` fix and **terminated on instruction**; it was
not restarted, and the focused files listed in section 9 replace it.

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

## 7. What this record did **not** do

- **CQA-04 stays open.** The two map/graphics decode stacks were not
  consolidated, merged or re-pointed at each other. `map_render` and
  `export/canonical` remain separate readers; only their *profile identity and
  extents* were moved onto one authority, which is what the record asked for.
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
  literal key inside a profile-free API. Directly adjacent to this record and
  **not fixed here**; it is the next identity-adjacent finding.
- **CQA-17**, `placement_types.table_address` and `enemy_stats.address` both
  declare `0x08711274` in the profile, and `entities.py` mints a CONFIRMED link
  from address alignment rather than from the shared declaration.
- `formats/stat_tables.BASE_STAT_NAMES` is still an unprofiled per-game roster;
  it is now guarded against wrapping but should become profile data.
- The export stack still reads through `tools/export/canonical.py` rather than
  the SDK's `formats` layer (that dependency *is* CQA-04).
- Line endings: `tools/webfoot/profile.py` is one of the nine documented
  mixed-ending files. Its edits were applied with the byte-safe line-indexed
  recipe in `../line-endings.md` after editor round-trips were detected and
  reverted. `git diff --check` is clean. The CRLF total moves from 732 to 731:
  exactly one line changed content (the `ActorSpriteProfile` argument line that
  gained `bg_palette`), and `git diff --check` reads a CR before the newline of
  an *added* line as trailing whitespace, so a changed line must end with a bare
  LF. Every other pre-existing line is byte-identical.

---

## 9. Findings from independent verification and their resolution

A independent read-only verification pass examined the frozen revision `7ca59792d9b97a4de4887cb54b1732926f4f6172`
(a pristine `git archive` export, so the later commits could not contaminate it)
with the canonical ROMs configured, and returned **BLOCKING = 2**. Both
are resolved.

### Finding 1 (H/N), BLOCKING: two data-module SHA literals still gated behaviour

`data/behavior_triggers.py` and `data/placement_contracts.py` carried their own
copy of the canonical SHA-256, compared against the **loaded image's** hash. They
were live gates and appeared in the record's classification only as profile-id
selectors.

**Resolved** (`bd99daca72546421b00fdda972e3ce691cad6b0f`, completed in `cff4a75448309be70480a97a63922b5462d06c1b`): all **four** comparisons now
read the profile's declared identity (`authored_placements.py` two sites,
`placement_events.py` one, `maps.py` one), so the catalog declaration is the
authority and the contract value is a cross-check.
`test_the_data_contract_hashes_agree_with_the_profile` asserts the relationship
for **every** catalogued profile, so a contract that drifts from the catalog
fails loudly.

**The first correction was incomplete, and that is worth recording precisely.**
There were **four** gates in this class, not the two the finding's summary
implied. The round-1 verification pass named **three** of them (`authored_placements.py`
two sites, `placement_events.py` one). `bd99daca72546421b00fdda972e3ce691cad6b0f` migrated **two** of those three
and skipped the behavior-trigger gate inside `_require_trigger_contract`. A
follow-up grep for `identification.hashes.sha256` then found that skipped site and
one genuinely unlisted fourth, the placement-contract gate inside `load_maps`.
Both landed in `cff4a75448309be70480a97a63922b5462d06c1b`.

An earlier draft of this section said the follow-up "found a third and fourth that
neither the verification pass nor the author had listed", which is wrong on the
attribution: the verification pass did list the `_require_trigger_contract` site, and
`bd99daca72546421b00fdda972e3ce691cad6b0f` simply failed to migrate it. What is true, and was the real cause, is
that the correction was driven by the finding's *summary* rather than by an
exhaustive search for the pattern. The fix is now proved exhaustive by grep: four
gates, four profile comparisons, no fifth.

**And `cff4a75448309be70480a97a63922b5462d06c1b` itself cost a regression, found by a delta review.** Widening
that gate's attribute contract to read `maps.profile.sha256` broke four tests in
`tests/unit/test_authored_behavior_trigger.py`, whose stand-in supplied only
`profile.id`. The commit was made without re-running those tests. Fixed by giving
the stand-in a declared hash (`tests/unit/test_authored_behavior_trigger.py:42`),
which is also the more faithful fixture: a case that overrides it now genuinely
exercises the profile-authority comparison rather than the old image-hash one.
All 15 tests in that file pass. The wider lesson is recorded below: a commit that
changes an attribute contract must re-run the files that stub it, and the
record's test totals must be re-measured whenever a commit lands after them.

The verification pass's related point, that two further behaviour-driving literals were
unnamed in the classification, is also fixed: `BG_PALETTE_ADDRESS` is now
profile-declared (below), and `BASE_STAT_NAMES` is documented as the one
remaining per-game literal in that layer, now guarded against a foreign roster
rather than silently reused.

### Finding 2, BLOCKING: record-caused ROM-gated test failures

With the canonical ROM configured, the frozen revision failed where `680f70bd85d6c1866e3749b8791753130266d300`
passed: `1 failed + 7 errors`, because three test files were left calling removed
API (`st.character_identity(0)`; `mr.SUPPORTED_ROM_SHA256`;
`map_browser.SUPPORTED_ROM_SHA256`). The record's claim that their call sites
were updated was **false for those three files**, and its integration evidence
could not be reproduced in the environment the record says they must run in.

**Resolved**: the three files now derive the identity from
`profile_authority.canonical_export_identity()` / `mr.canonical_profile()` and
pass the profile's character count. Verified with the ROM configured: the same
four-file selection the verification pass used
(`test_stat_write_rom.py`, `test_map_render_rom.py`,
`test_map_layout_write_rom.py`, `test_buu_dialog_runtime_rom.py`) gives
**49 passed, 2 skipped, 0 failed** at both base `680f70bd85d6c1866e3749b8791753130266d300` and the corrected
revision, measured before the test-policy correction.

### What the verification pass could not verify, and what that exposed

The verification pass recorded that PySide6 was absent, so **every Workbench GUI test
skipped in both revisions** and the Workbench claims were code-level only. That
gap was closed rather than accepted:

- PySide6 6.11.2 was installed into the environment pytest runs in (the project
  already declares it under the `workbench` extra; only the install was missing),
  the canonical ROM was configured for the ROM gate, and the atlas artifact was
  regenerated from it (`atlas regenerate`, ROM SHA-256 identical before and
  after).

  Reproduction of the **environment** (the ROM and GUI gates need these present):

  ```text
  python -m pip install "PySide6"                       # the `workbench` extra
  set WEBFOOT_BUU_ROM=<path to the canonical Buu's Fury image>
  set LOGX_CANONICAL_ROM=%WEBFOOT_BUU_ROM%
  python -m tools.webfoot atlas regenerate "%WEBFOOT_BUU_ROM%" --out build/atlas
  ```

  Then run **named files only**, never a broad suite (`docs/testing.md`, and the
  human test policy in force for this record). The exact focused commands and
  their results are listed below.

  **ROM discovery is not uniform, and this bites the exact command an earlier
  draft quoted.** Some ROM-gated files honour `WEBFOOT_BUU_ROM` /
  `LOGX_CANONICAL_ROM`; others locate the image by a hard-coded relative path and
  ignore both. Measured by the verification pass: with only the two environment variables
  set, the four-file selection returns **5 passed, 46 skipped**;
  `49 passed, 2 skipped` appears only once the image is also discoverable at
  `roms/Dragon Ball Z - Buu's Fury (U).gba`. The two files that bypass the
  variables are `tests/integration/test_stat_write_rom.py:47` (a `roms/*Buu*.gba`
  glob) and `tests/integration/test_buu_dialog_runtime_rom.py:31` (a literal
  path). This is pre-existing path logic, not introduced here, and
  `test_stat_write_rom.py` was edited by this record without aligning it; a
  follow-up should make every ROM-gated file read the same variables so a record
  can state one command.

  Measured on the two workbench files that gate this way, run singly:

  | image discoverable at `roms/`? | `test_workbench_graphics.py` + `test_workbench_session.py` |
  | --- | --- |
  | no | **46 passed, 5 skipped** (1 + 4) |
  | yes | **51 passed, 0 skipped** |

  So the workbench-gate total moves by exactly those 5 tests depending on
  discovery, which is why an earlier draft's figure of 178 (no image at `roms/`)
  and the round-2 verification pass's 181 differ by a bounded, now-observed amount rather
  than an unexplained one.
- Running the gates that had always skipped **found five real defects that this
  record had introduced and that no previous run could have caught**:
  - `render_map` gained a `profile=` keyword and two Workbench test stubs still
    had the old signature, so the map tab never loaded its map: two failures and
    one **hang**. All three pass at base, so all three were record-caused.
  - `map_browser_tab`'s read-only detail text assertion still expected the word
    "canonical".
  - `scene.script_effect_options` reads the declared text count, which the shared
    synthetic profile fixture did not declare.
  - `test_graphics_cli`'s synthetic `actor_sprites` declaration lacked the new
    `bg_palette_address` field.
- `map_render`'s `BG_PALETTE_ADDRESS` was the verification pass's own escaped mutation
  (`export/render.py` object palette, `map_layout_write` count and
  `authored_placements` text bound were the others). `BG_PALETTE_ADDRESS` is now
  the profile's `tables.actor_sprites.bg_palette_address`, and new tests catch
  every one of those three mutations (section 6, below).

This is the honest reading: the frozen revision was **not** closure-ready, and
the verification pass was right on both counts. The corrected revision is materially
better tested than the frozen one because the gates now actually execute.

### Second review round

A fresh round-2 verification pass examined the corrected revision, and a separate delta
verification pass examined the follow-up. Verdict at the tip: **BLOCKING = NONE**. Between
them they found three things that the round-1 report and this record had wrong,
all now fixed:

| finding | disposition |
| --- | --- |
| The round-1 correction migrated only 2 of the 4 contract-hash gates; `authored_placements.py:117` and `maps.py:826` still compared the data literal against the loaded image's hash | fixed in `cff4a75448309be70480a97a63922b5462d06c1b`; all four read `profile.sha256` |
| `cff4a75448309be70480a97a63922b5462d06c1b` broke four cases in `tests/unit/test_authored_behavior_trigger.py` and the record's `tests/unit` total was stale for it | fixed in `2b7640896f3048f3bb975f5fe38a6ce876646f1b`; that file is 15 passed |
| This record claimed "none left" for the canonical literal in production, and misattributed which gate had been unlisted | both corrected above (the literals survive as pinned cross-checks; the verification pass *did* list the `_require_trigger_contract` site) |

Round-2 also downgraded two of the round-1 notes and one of its own:

- The ROM-hash comparison restated in several consumers is **restated code
  against one authority, not a duplicate authority** (NOTE, not blocking); the
  docstring in `export/map_browser.py` claiming "one statement of it rather than
  one per reader stack" slightly overstates, since the comparisons are per-reader
  even though the value has one owner.
- A meta line missing keys still raises a bare `KeyError` from
  `tools/webfoot/atlas.py:511`. It fails closed (no atlas is accepted) and that
  file is untouched by this record, so it is out of scope; recorded as debt.
- The `map_layout_write` count guard was caught only by a **source-text**
  assertion. Strengthened: `MapLayoutWriter` now accepts an injected profile, and
  `test_the_map_layout_writer_bound_is_the_profiles` drives a profile declaring
  only 3 maps through the writer and asserts its own gate refuses index 3 and 452.
  Re-running the verification pass's exact mutation (`count = 452`) against that single
  test fails it. The writer's identity gate is still satisfied by a declared
  identity rather than by stubbing.

### Test policy and what was actually run

**MANUAL TEST POLICY: FOCUSED FILE/NODE TESTS ONLY.** Broad manual runs
(`pytest`, `pytest tests/unit`, `pytest tests/integration`, any broad marker gate)
are forbidden on this project. Broad validation belongs to CI, after the candidate
is pushed and an MR exists; the record keeps manual and CI evidence distinct.

That policy is why the earlier broader runs appear below with a commit attached:
they happened before the policy correction and are reported as **historical
measurements at named commits**, not as a claim about the current tip.

#### Historical broad measurements (each at the named commit)

| command | commit | result |
| --- | --- | --- |
| `pytest tests/unit` | `bd99daca72546421b00fdda972e3ce691cad6b0f` | **2141 passed, 23 skipped, 0 failed** |
| `pytest tests/unit` | `72ca3a7e781bb51a3de5cb05c07b816622abb239` | **2327 passed, 7 skipped, 0 failed** |
| `pytest tests/integration` | `72ca3a7e781bb51a3de5cb05c07b816622abb239` | **956 passed, 45 skipped, 0 failed** (71 min) |
| `pytest tests/unit -m "fast and workbench"` | `72ca3a7e781bb51a3de5cb05c07b816622abb239` | **178 passed, 0 failed** |

The `72ca3a7e781bb51a3de5cb05c07b816622abb239` figures are **stale at the tip**: `cff4a75448309be70480a97a63922b5462d06c1b` landed after them and
turned four `tests/unit/test_authored_behavior_trigger.py` cases into failures
(a delta review caught it). Those four now pass again, and the affected files were
re-run in isolation. No broad re-measurement was taken, by policy.

#### Focused manual runs on the current tip

Each command names explicit files that exercise a code path this record changed.

| command | result |
| --- | --- |
| `pytest tests/unit/test_authored_behavior_trigger.py -q` | **15 passed** (the file `cff4a75448309be70480a97a63922b5462d06c1b` broke; all four failures fixed) |
| `pytest tests/unit/test_authored_placements.py tests/unit/test_map_placements.py tests/unit/test_scene_authoring.py -q` | **112 passed** (the other consumers of the migrated trigger gate) |
| `pytest tests/unit/test_atlas_identity.py tests/unit/test_extent_profile_authority.py tests/unit/test_profile_authority_contract.py tests/unit/test_profile.py tests/unit/test_capability.py tests/unit/test_atlas_build.py -q` | **114 passed** (identity contract, profile/catalog parsing, synthetic profile, absence assertions) |
| `pytest tests/unit/test_map_render.py tests/unit/test_map_layout_provenance.py tests/unit/test_workbench_session.py -q` (ROM configured) | **41 passed, 1 skipped** (map renderer, derivative provenance, Workbench session identity) |
| `pytest tests/unit/test_text_tables.py tests/unit/test_text_growth.py tests/unit/test_text_project.py -q` | **81 passed** (text codec extents, the live index bound) |
| `pytest tests/unit/test_stat_tables.py tests/unit/test_stat_write.py tests/unit/test_project_format.py tests/unit/test_gameplay_effect_native.py -q` | **71 passed** (stat extents and the text-bound gate) |
| `pytest tests/unit/test_workbench_map_tab.py tests/unit/test_workbench_map_browser.py -q` | **44 passed** (the GUI paths PySide6 exposed) |
| `pytest tests/integration/test_map_render_rom.py tests/integration/test_map_layout_write_rom.py tests/integration/test_stat_write_rom.py -q` (ROM configured) | **25 passed, 2 skipped** |
| `git diff --check` | clean, exit 0 |

ROM-backed runs above are named by file and read the canonical image read-only;
the ROM's SHA-256 was verified unchanged before and after. The single remaining
skip in `test_map_render.py` needs the map-40 VRAM dump, which is not part of this
record.

**BROAD / FULL SUITE: NOT MANUALLY RUN, HUMAN POLICY.** A broad `tests/unit` run
started after the `cff4a75448309be70480a97a63922b5462d06c1b` fix was **terminated on instruction** and restarted
nowhere; the focused files above replace it.

### Additional mutations, on the corrected revision

Mutations were validated by running **only the specific test expected to detect
each one**, not a suite:

| mutation | location | test run (that file only) | outcome |
| --- | --- | --- | --- |
| object palette address -> literal `0x0805652C` | `export/render.py` | `test_extent_profile_authority.py` | 1 failed (detected) |
| background palette address -> literal `0x080701B0` | `webfoot/map_render.py` | `test_extent_profile_authority.py` | 2 failed (detected) |
| map-entry count -> literal `452` | `export/map_browser.py` (round 1) | `test_extent_profile_authority.py` | 1 failed (detected) |
| profile-id comparison bypassed (M1) | `webfoot/profile.py` | `test_atlas_identity.py` | 3 failed (detected) |
| base-SHA comparison bypassed (M2) | `webfoot/profile.py` | `test_atlas_identity.py` | 3 failed (detected) |
| text bound -> literal `1534` | `webfoot/authored_placements.py` | `test_gameplay_effect_native.py` | detected by the discriminating 1,000-entry profile |

`test_a_shorter_declared_text_table_moves_the_bound` exists specifically because
of the verification pass's observation that the canonical profile's own count is 1,534, so
the original test could not distinguish "reads the profile" from "hard-codes
Buu's number". Every mutation was reverted immediately and the tree verified
clean (`git status` empty, no `MUTATION` marker).

### CI

**CI BROAD SUITE: not yet run.** The candidate has not been pushed and no merge
request exists, so no CI result is available. Broad validation is CI's job on this
project; when the MR is opened, its result belongs in this section and must not be
duplicated by hand.
