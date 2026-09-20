# DRAGONBYTE-Z-AUTHORED-IMAGE-PIPELINE-001 - independent review record

Ticket: **DRAGONBYTE-Z-AUTHORED-IMAGE-PIPELINE-001** - extract the DragonByte Z
Save As / provenance / derivative-trust machinery out of the Map Layout Editor into
one shared authored-image pipeline, with no new ROM capability and no change to the
accepted Map Layout Editor behaviour.

Worktree `<checkout>-authored-image-001`, branch
`authored-image-pipeline-001`, created from `origin/master` at
`41e218e93d6a54793a975fff734a4e93b7b672f5`. Frozen, uncommitted; nothing staged.

```text
CODE REVIEW

Verdict: APPROVE WITH NON-BLOCKING NOTES

Scope reviewed:
- NEW  tools/webfoot/authored_image.py                       (631 lines)
- NEW  tests/unit/test_authored_image.py                     (608 lines)
- MOD  tools/webfoot/map_layout_edit.py                      (save -> shared transaction)
- MOD  tools/webfoot/map_layout_provenance.py                (map-layout half only)
- MOD  tests/unit/test_map_layout_provenance.py
- MOD  docs/workbench.md                                     (one paragraph)
- Read for context (unchanged): tools/webfoot/write.py,
  tools/webfoot/map_layout_write.py, tools/webfoot/workbench/session.py,
  tools/webfoot/workbench/map_browser_tab.py, tools/webfoot/workbench/atlas_browser.py,
  tests/integration/test_map_layout_editor_rom.py, tests/unit/test_workbench_map_browser.py
- Compared against HEAD's tools/webfoot/map_layout_provenance.py and
  tools/webfoot/map_layout_edit.py, loaded from git into throwaway modules.

Blocking findings:
- None.

Non-blocking findings:
- [MEDIUM] tests/unit/test_authored_image.py - the decisive canonical-reconstruction
  equality check (authored_image.py:512-536) has no discriminating test, and the test
  that pinned it at HEAD was deleted. Evidence: with the check removed, 60 tests pass.
  Impact: the shared verifier is now the single trust boundary for every domain and its
  own decisive rule is unpinned; in this domain MapLayoutWriter's SHA gate redundantly
  enforces the same property, so no ROM is accepted today. Fix: one negative control.
- [MEDIUM] tools/webfoot/authored_image.py:388-402 (_load_manifest) - the documented
  "Raises AuthoredImageError for ... a malformed ... manifest" contract is incomplete:
  a non-UTF-8 manifest raises UnicodeDecodeError and a deeply nested one raises
  RecursionError, both escaping verify_authored_rom and Session.open_rom, whose only
  GUI call site catches SessionError. Pre-existing at HEAD (reproduced against HEAD's
  own module), carried forward unchanged.
- [LOW] tools/webfoot/authored_image.py:129-162,290 - normalize_changes collapses exact
  duplicate writes, so the save path now accepts a pair that write.plan_changes refuses
  (OverlappingChangeError). Emitted bytes and manifest are identical, and the Map Layout
  Editor cannot construct the case, so no accepted image widens.
- [LOW] tools/webfoot/authored_image.py:222-343 - save_authored_image takes no
  field_bytes, so it cannot guarantee the derivative it publishes satisfies
  verify_authored_image's field-width rule; unreachable from MapLayoutEditor.save.
- [LOW] tools/webfoot/map_layout_provenance.py:163-165,238-241 - only
  AuthoredImageError is translated into ProvenanceError; MapLayoutWriteError from the
  domain hook's own MapLayoutWriter would escape (unreachable while reconstruction runs
  first). Not "one public error type for every reason".
- [LOW] test/portability and pre-existing notes: the map-range negative control moved
  from portable to ROM-gated only; the manifest-only publish failure is still probe-only;
  a hard link to the source is not detected by the path-based alias guard (unchanged from
  HEAD); LayoutSave.changes is annotated tuple[LayoutEdit, ...] but holds ByteChanges.

Correctness:
- PASS. Every refusal the pre-refactor modules made still fires in the same situation
  with its own message (46/46 reproduced against a real emitted derivative). Every
  accepted-derivative decision matches HEAD's verifier over a 265-case fuzz (0
  mismatches). Every accepted Map Layout Editor save matches HEAD's byte for byte.

Architecture/product alignment:
- PASS. The generic logic exists once; no map/chunk/layer rule leaked into the shared
  module; no generic logic left duplicated in the domain module; no plugin system,
  editor registry, abstract factory, command bus, second manifest format, new ROM
  capability, UI change or site change.

ROM/data safety:
- PASS. Canonical ROM byte-identical (8,388,608 bytes, SHA-256 940ad5f0...f059e) after
  every run, including the save-over-source, junction-alias and hard-link probes. No
  save can replace or delete the source through any of the four names it touches.

Determinism:
- PASS. Edit order does not change the emitted image or the manifest; the normalized
  plan is ordered by offset; the manifest is the existing deterministic WriteManifest.

Tests/evidence:
- PASS with the MEDIUM note above. The new tests are discriminating negative and
  positive controls, the ROM-gated evidence is intact and unmodified, and no previously
  passing assertion was weakened. Two coverage items moved rather than disappeared.

Compatibility:
- PASS. A derivative written by HEAD's code still verifies and reopens; the document
  format, suffix, schema version, owner vocabulary, reason string and field width are
  unchanged; the Map Browser still renders a derivative from the reconstructed canonical
  bytes with the declared edits as overrides, and still refuses to edit it.

Maintainability:
- PASS. The domain module is now ~260 lines and holds only owner vocabulary, reason,
  the same-layer rule and the typed records; the shared module is the one place that
  knows about staging, aliases, publication order and manifest structure.

Public-release hygiene:
- N/A / PASS. No tracked file other than this record was added; `git diff --check` is
  clean; only build/ was written to; no ROM, save, state, generated image or generated
  document appears in the diff.
```

## Findings, in detail

### 1. [MEDIUM] The decisive provenance check has no discriminating test

`tools/webfoot/authored_image.py:512-536` (`_reconstruct_canonical`) is the rule both
the module docstring and the ticket call decisive: undoing every declared change must
reproduce the canonical image by SHA-256, which is what bounds an accepted derivative to
canonical-plus-declared and so needs no copy of the canonical file. HEAD pinned it
directly in `tests/unit/test_map_layout_provenance.py::test_canonical_reconstruction_is_required`
(synthetic bytes whose inversion cannot hash to the canonical image). That test is gone
and nothing replaced it.

No test in the new suite reaches the branch. The nearest candidates are all refused
earlier by a different rule:

| Candidate | What actually refuses it |
| --- | --- |
| `test_authored_image.py:449-458` byte flipped outside the field, manifest untouched | `_output_identity` (digest mismatch) |
| `test_authored_image.py:462-467` byte flipped inside the field, manifest re-hashed | `_check_declared_values` - reconstruction *passes*, because it overwrites the whole declared field with `old` |
| `test_map_layout_editor_rom.py:554-565` the same case on the real ROM | `_check_declared_values` |
| `test_authored_image.py:524` a declared span past the image | `_declared_changes` alignment rule (offset 2046 is not 4-aligned); confirmed by the reviewer, which reaches the intended branch only at `offset == len(image)` |

**Evidence.** `build/review/mutate_recon_off.py` loads as a pytest plugin and replaces
`_reconstruct_canonical` with the same inversion minus the SHA-256 equality:

```text
> pytest tests/unit/test_authored_image.py tests/unit/test_map_layout_provenance.py \
    tests/integration/test_map_layout_editor_rom.py -p no:cacheprovider -p mutate_recon_off \
    --basetemp=build/pytest-review-mutA
60 passed in 54.50s
```

The check is load-bearing, so this is a real hole in the *suite*, not a redundant rule:
with the mutation loaded, the reviewer's refusal inventory loses two rows -
`[FAIL] undeclared byte change, honest digest` and `[FAIL] declared old is not the
canonical value` (44/46) - and an arbitrary modified ROM stops being refused by the
shared verifier.

**Impact.** Today the blast radius is bounded: `_check_layout_changes` builds
`MapLayoutWriter(canonical_image)` (`map_layout_provenance.py:165`), whose constructor
re-verifies the image by SHA-256 (`map_layout_write.py:43`), so the same property is
enforced a second time and the mutation's only symptom on this path is a
`MapLayoutWriteError` escaping instead of a `ProvenanceError`. But the shared module's
docstrings explicitly invite reuse by other domains, and a domain whose change checker
does not happen to build a SHA-verifying writer would inherit an untested decisive check
with no second guard.

**Smallest correction.** Add one negative control to `tests/unit/test_authored_image.py`:
a derivative with a byte changed somewhere no declaration covers, the manifest's
`output.sha256`/`size` recomputed to match, asserting `AuthoredImageError` and the
`"not the canonical ROM plus the changes"` message; plus the variant where the declared
`old` is valid hex that the canonical image does not hold. `build/review/probe_shared.py`
probes 15/15b and the corresponding `build/review/probe_refusals.py` rows are exactly
these two cases, and both refuse correctly on the frozen code.

### 2. [MEDIUM] The manifest loader's documented refusal contract is incomplete

`authored_image.py:388-402` catches `OSError` and `json.JSONDecodeError` only, and the
docstring at `:579-583` promises `AuthoredImageError` for "no manifest, a malformed or
unsupported manifest". Two malformed shapes escape:

```text
> (real derivative, manifest bytes b'{\xff\xfe\x00 not utf8}')
verify_authored_rom -> ESCAPED UnicodeDecodeError 'utf-8' codec can't decode byte 0xff in position 1
Session.open_rom     -> ESCAPED UnicodeDecodeError ...
> (manifest = '['*60000 + ']'*60000)
deeply nested arrays  -> ESCAPED RecursionError maximum recursion depth exceeded while decoding a JSON array
deeply nested objects -> ESCAPED RecursionError ...
```

`verify_authored_rom` wraps only `AuthoredImageError` (`map_layout_provenance.py:229-241`)
and `Session._verify_derivative` catches only `ProvenanceError`
(`workbench/session.py:270-276`), so the exception reaches the Qt slot
`AtlasBrowser._on_open_rom`, whose `except SessionError` (`atlas_browser.py:86`) does not
cover it: the intended "Load failed: ..." message becomes an unhandled exception on a
user-chosen file. Nothing is accepted, so this fails closed.

**Pre-existing, not a regression** - the reviewer loaded HEAD's module from git and ran
the same two inputs through it: `OLD non-UTF-8 bytes -> ESCAPED UnicodeDecodeError` and
`OLD deep nesting -> ESCAPED RecursionError`. The refactor copied the loader's structure
into the new shared module, which is now the right place to fix it.

**Smallest correction.** In `_load_manifest`, catch `(OSError, UnicodeDecodeError)` for
the read and `(json.JSONDecodeError, RecursionError)` for the parse, raising
`AuthoredImageError` as the docstring already promises. One extra unit case each.

### 3. [LOW] The save path now accepts duplicate identical writes that `plan_changes` refuses

`normalize_changes` (`authored_image.py:129-162`) collapses two changes that write the
same bytes to one field into one, and `save_authored_image:290` runs it *before*
`write.plan_changes`. `write.plan_changes` itself refuses the pair:

```text
> plan_changes(base, [c, c], ...)
OverlappingChangeError o (0x00000010+4) and o (0x00000010+4) would write the same bytes
```

HEAD's `MapLayoutEditor.save` handed the caller's changes straight to `plan_changes`, so
that pair was refused then and is accepted now
(`test_authored_image.py::test_a_duplicate_physical_write_is_collapsed`). The emitted
image and manifest are byte-identical either way, and the Map Layout Editor cannot
construct the case - `self._edits` is keyed by `(map, layer, cell)` and
`map_layout_edit.py:616` still cross-checks `sorted(edit.offset ...) ==
pending_offsets`, which also covers the two-maps-share-one-dominant-record state the
previous review recorded - so nothing in the trusted-image set widens. It is a deliberate
behaviour difference from `write.py`'s stated invariant ("two planned changes would write
the same byte ... refusing is the only safe outcome", `write.py:58-64`). Either say so in
`write.plan_changes`' docstring as the caller's responsibility, or drop the collapse.

### 4. [LOW] `save_authored_image` has no field-width contract

`save_authored_image` (`authored_image.py:222`) takes no `field_bytes`, while
`verify_authored_image` (`:555-565`) does. `verify_emitted_image` proves only "the output
is the base plus the spans the caller declared", of any width, and the manifest it writes
can then never satisfy `_declared_changes`' `size == field_bytes`. The reviewer confirmed
that e.g. a 2-byte no-op at the last field is accepted and published. Unreachable from
this domain: `MapLayoutEditor.save` builds only four-byte changes
(`edit.replacement.to_bytes(4, "little")` with a four-byte `old` slice) and its own
`_verify_output` re-reads every pending cell through the accepted layer reader. Worth a
parameter or a docstring sentence, since the module docstring claims the accepted
derivative is "exactly the canonical image plus the declared, domain-legal fields".

### 5. [LOW] Not every domain-hook failure is translated into the module's public error

`map_layout_provenance.py:229-241` translates `AuthoredImageError` only. The hook builds
`canon.Rom`, `canon.read_map_entries` and `MapLayoutWriter(canonical_image)` at
`:163-165`, all of which raise their own types. It is unreachable on the frozen code
because reconstruction has already proved the canonical bytes equal `mb.SUPPORTED_ROM_SHA256`
before the hook runs, and the reviewer confirmed that by symptom: under mutation A the
only difference on this path was `MapLayoutWriteError: expected the canonical Buu rev0
image` escaping instead of a `ProvenanceError`. The claim "one public error type for every
reason a derivative is not accepted" would be true if `verify_authored_image` wrapped the
hook's own exceptions too. Defence in depth only; non-blocking.

### 6. [LOW] Test portability and pre-existing limits

- The negative control for `map_index >= canon.MAP_ENTRY_COUNT` is now ROM-gated only
  (`test_map_layout_editor_rom.py:602`) - it left the portable suite with
  `test_a_declared_change_must_be_this_tools_output`. In CI without the ROM, the newest
  domain rule in `_check_layout_changes` is unexercised. The owner-vocabulary half is
  still portable (`test_map_layout_provenance.py:73-94`). Recommend restoring a portable
  case through `authored_image._declared_changes` + `_check_layout_changes` with an
  owner of `map:0452`.
- The manifest-only publish failure (image published, manifest rename refused) is still
  verified only by probe, as the previous review recorded; the refactor preserves it
  (reviewer probe 11: `AuthoredImageError` naming the manifest path, image present,
  manifest absent, no staging left, and the published image then refuses to reopen).
  A committed test for it is still missing.
- The alias guard is path-based: a hard link to the source at a different path is not
  detected (`Path.resolve()` has no inode identity). The reviewer reproduced it
  synthetically: the save is accepted, the source's own bytes survive at the source path,
  and the *chosen output path* is replaced - correct for a deliberately chosen output,
  and identical to HEAD's behaviour. Worth one docstring clause, since the module says
  "Every path is resolved, so a symlink or junction alias is caught too".
- `LayoutSave.changes` (`map_layout_edit.py:261`) is annotated `tuple[LayoutEdit, ...]`
  but has always held `write_sdk.ByteChange`; the GUI only reads `len()`. Pre-existing;
  the shared `AuthoredImageSave.changes` uses the correct type.

## Reviewer validation performed

Focused only, per the human's policy override: the eight-file gate below plus throwaway
probes the reviewer wrote under `build/`. No full-suite run and no broad `tests/unit` run
was started. All pytest runs used an explicit `--basetemp`.

1. `git status --porcelain=v1` - exactly the four modified and two untracked files in the
   ticket; nothing staged and no other tracked path touched.
   `git diff --check` - exit 0 (no whitespace errors).
2. The ticket's focused gate verbatim, `--basetemp=build/pytest-review-focused`:
   **125 passed in 103.75 s, 0 skipped** (the atlas is present, so every ROM-gated test
   ran). This matches the implementer's measured total.
3. The "before" number, arithmetically rather than by re-running: HEAD's
   `test_map_layout_provenance.py` (extracted with `git show` to
   `build/review/old_map_layout_provenance_test.py`) collects **11**, the new one
   collects **12**, the new `test_authored_image.py` collects **23**, and the other six
   files collect **90**. So HEAD = 90 + 11 = **101** = 98 passed + 3 skipped and the
   frozen tree = 90 + 12 + 23 = **125**. The reviewer did not reproduce the pass/skip
   split itself, because that needs a second checkout or a change to git state.
4. `build/review/probe_shared.py` - **27/27** adversarial probes against the shared layer
   with the reviewer's own toy domain: conflicting writes (same field, overlapping spans,
   same offset/different width) fail closed before publication with an existing
   destination and manifest untouched; all four source collisions plus `sub/../source.gba`,
   a case-only alias and a symlink alias refused with the source byte-identical and
   nothing else created; failed emit, failed verification, failed image publish and
   failed manifest-only publish each preserve the destination and leave no staging file;
   tampered image outside/inside a declared field with the manifest re-hashed; a
   swapped `old`/`new`; ~40 tampered-manifest shapes (base, profile, output digest/size,
   old/new, changed byte count, reason, width, alignment, duplicate offsets, no-op, span
   past the image, malformed documents, duplicate JSON keys); an undeclared byte change
   with a fully honest manifest; malformed plans; determinism in either edit order.
5. `build/review/probe_rom_path.py` - **8/8** against the real canonical ROM: a real
   two-map derivative round-trips and reconstructs the canonical bytes; `Session.open_rom`
   with `RomProfileCatalog.load("config/roms.yaml")` yields `map_image == canonical`,
   `rom_image == derivative`, `identification is None`, `maps`/`text_strings` None, and
   `render_map(map_image, index, chunk_overrides=layout_overrides(index))` is identical
   layer-for-layer to `MapLayoutEditor.preview(index)`; the canonical ROM itself and all
   four derived names refused as outputs with the ROM untouched; 13 tamper/defeat
   variants refused by both the SDK verifier and the open path; a derivative with no
   manifest refused; the census still **452 / 341 / 111** with map 19 read-only and its
   every read-only slot explained and the proven Grand Kai field still `0x082928DC`;
   no-op save byte-identical and accepted by identity; failed emit and failed
   verification preserving an existing destination with no staging file.
6. `build/review/probe_refusals.py` - **46/46**: every refusal extracted from HEAD's
   `map_layout_provenance.py` and HEAD's `map_layout_edit.save` re-fired on a real
   derivative and asserted by its own message, including the decisive reconstruction
   refusals, the declared-value rule, the owner vocabulary, the map-range rule, the
   non-dominant-layer rule, the cell-range rule, the owner/offset cross-check, the null
   and foreign-chunk replacement rules.
7. `build/review/probe_parity.py` - **265 fuzzed cases, 0 decision mismatches** between
   HEAD's verifier loaded from git and the frozen one (26 `ACCEPT -> ACCEPT`, 239
   `REFUSE -> REFUSE`), over mutated images with and without an honest manifest digest
   and mutated manifest fields.
8. `build/review/probe_ab.py` - **30/30 A/B checks** against HEAD's `MapLayoutEditor.save`
   loaded from git: identical emitted image bytes, identical manifest documents,
   identical `no_op`, `verified` layout edits, `changed_offsets`, output digest/size and
   derived manifest path, for a no-edit, a one-edit and a two-map save; the same refusal
   type and on-disk effect for saving over the source, for a source copy written to a new
   name, and for a failing emit over an existing destination.
9. Mutation testing of the two load-bearing shared checks:
   `mutate_recon_off.py` (reconstruction equality removed) -> **60 passed**, i.e. not
   pinned (finding 1); `mutate_emit_off.py` ("no byte outside a declared field changed"
   removed) -> **1 failed / 59 passed**, i.e. pinned by
   `test_the_byte_level_verification_refuses_a_wrong_size_digest_or_extra_byte`.
10. Alias attempts beyond the tests: a directory junction to `roms/` used as the output
    is refused (and the ROM is untouched); a hard link to the source at a different path
    is not detected (finding 6), reproduced synthetically, never against the real ROM.
11. Canonical ROM verified before and after every probe run: 8,388,608 bytes, SHA-256
    `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`. All probe output
    was written under `build/review/` and the scratch directories were removed.

## Remaining uncertainty

- I did not run `pytest tests` (out of scope by the human's override, and the implementer
  had already started it), so no full-suite statement is made. Everything above is
  focused and independently reproduced.
- I did not re-run the pre-change suite, so the "98 passed, 3 skipped" figure is
  confirmed by collection arithmetic only, as stated in item 3.
- No Qt event loop was driven in this pass. The derivative path was exercised at the
  session level - which is exactly what `map_browser_tab._render_map` calls
  (`map_image` + `layout_overrides`) - and the existing synthetic-tab test
  `test_workbench_map_browser.py::test_a_verified_derivative_renders_its_edits_and_stays_read_only`
  passed in the focused gate; a live click-through was not repeated.
- 8.3 short-name aliasing could not be tested: this volume generates no short names for
  the ROM files, so the `Path.resolve()` claim is verified for relative, dot-dot,
  case-only, symlink and junction aliases only.
- Whether a future domain will reuse this layer is the ticket's premise, not something
  this review can measure; findings 1 and 4 are stated in those terms.

## Post-fix addendum - re-review of the accepted delta

**Final verdict on the fixed artifact: APPROVE WITH NON-BLOCKING NOTES.** No blocking
finding remains; all four accepted items are verified fixed, and the residue is
non-blocking by decision or pre-existing.

### The delta I inspected

| File | Delta | Reviewer's reading |
| --- | --- | --- |
| `tools/webfoot/authored_image.py` | +11 lines total (631 -> 642): 1 module-docstring bullet, 5 `save_authored_image` docstring lines, 5 `_load_manifest` lines | Exactly the two docstring additions and the two `except` clauses described. I confirmed the size by checking every top-level definition's line number against the revision I reviewed (+1 to +11, monotonic and fully accounted for); the `save_authored_image` body, `verify_emitted_image`, `_reconstruct_canonical`, `_declared_changes`, `_canonical_base`, `_output_identity` and `_field` are byte-for-byte where they were. |
| `tools/webfoot/write.py` | +5 docstring lines in `plan_changes` only | `git diff` shows additions inside the docstring, before the body. No logic change. |
| `tests/unit/test_map_layout_provenance.py` | +1 test (`test_a_declared_change_may_not_name_a_map_out_of_range`) | Drives `map:0452 layer 1 cell 0` through `_check_layout_changes` with no image and asserts `"out of range"`. The range check precedes `canon.Rom(...)` in the hook, so the branch is reached and the test is discriminating; the message is the one my refusal inventory already pinned. |
| `tests/unit/test_authored_image.py` | +2 tests | Read in full below. |

### Item-by-item disposition, each re-verified

1. **Finding 1 (reconstruction untested) - FIXED, verified by mutation.**
   `test_an_undeclared_byte_change_is_refused_by_reconstruction` (a) flips byte 64 of an
   honest derivative - outside every declaration, with the declared replacement still
   present and `output.sha256`/`size` recomputed - and (b) declares an `old` of
   `01020304` at offset 16 where the image carries the declared `new`. I traced both
   through `verify_authored_image`: neither is refused by an earlier rule (digest honest,
   declared value present, structure valid), so both reach
   `_reconstruct_canonical` and assert the `"canonical ROM plus the changes"` message.
   Discriminating. The mutation now fails the suite:
   `pytest tests/unit/test_authored_image.py tests/unit/test_map_layout_provenance.py
   tests/integration/test_map_layout_editor_rom.py -p no:cacheprovider -p mutate_recon_off
   --basetemp=build/pytest-review-mutA2` -> **1 failed, 62 passed**, failing in the new
   test at `tests/unit/test_authored_image.py:474` (`DID NOT RAISE`). The decisive check
   is pinned.
2. **Finding 2 (manifest loader escapes) - FIXED, verified at both layers.**
   `build/review/probe_postfix.py` -> **10/10**: a non-UTF-8 manifest, a truncated
   multi-byte UTF-8 sequence, a 60,000-deep array and a 60,000-deep object each now
   produce `ProvenanceError` from `verify_authored_rom` ("no readable ... provenance
   manifest" / "malformed provenance manifest: maximum recursion depth ...") and
   `RomNotRecognizedError` (a `SessionError`) from `Session.open_rom`, i.e. the exception
   `atlas_browser._on_open_rom` catches. A valid derivative still reopens with the
   reconstructed canonical bytes, so the new catches are not over-broad.
3. **Finding 6, portability - FIXED.** See the table above; the map-range rule is
   exercised without the ROM again.
4. **Finding 6, probe-only manifest publish - FIXED.**
   `test_a_failed_manifest_publish_reports_an_image_without_provenance` fails the second
   `os.replace`, and asserts the raised `AuthoredImageError` carries "provenance could not
   be published", that the target of the second replace is the `.dragonbyte.json`
   document, that the image was published with the declared bytes, that the manifest does
   not exist, and that no staging file remains. That is exactly the behaviour my probe 11
   recorded; it now has a committed test.
5. **Findings 3, 4 (docstring option) - verified.** `write.plan_changes` now points a
   caller handed one physical field twice at `normalize_changes` while stating that a
   still-overlapping plan is refused here; `save_authored_image` now states that it proves
   the output is `base` plus the spans the caller declared, of whatever width, and that
   the declared-width contract is enforced by `verify_authored_image`. Both sentences
   match the code. I accept this closure for 3 and for the 4 docstring.
6. **Recorded as known limits, no objection:** the missing `field_bytes` parameter on
   `save_authored_image` (finding 4 body - unreachable from `MapLayoutEditor.save`, which
   builds only four-byte changes and re-reads every cell); the untranslated
   `MapLayoutWriteError` from the domain hook (finding 5 - unreachable while
   reconstruction runs first, and the SHA gate in `map_layout_write.py:43` is what makes
   it unreachable); the hard-link alias (pre-existing, identical to HEAD); and the
   `LayoutSave.changes` annotation (pre-existing). None of these blocks the ticket, and
   the reviewer's earlier severities for them stand as LOW.

### Re-validation on the fixed revision

- Focused eight-file gate, `--basetemp=build/pytest-review-postfix`:
  **128 passed in 111.57 s, 0 skipped** - reproduces the implementer's count
  (125 -> 128, the three added test functions).
- Mutation A (reconstruction equality removed): **1 failed, 62 passed** - pinned now.
- `build/review/probe_postfix.py` **10/10**; `build/review/probe_shared.py` **27/27**;
  `build/review/probe_refusals.py` **46/46**; `build/review/probe_rom_path.py` **8/8**;
  `build/review/probe_parity.py` **265 cases, 0 decision mismatches** against HEAD's
  verifier; `build/review/probe_ab.py` **30/30** against HEAD's `MapLayoutEditor.save`.
  Every probe was re-run on this revision, not reused from the first pass.
- `git diff --check` exit 0. Canonical ROM unchanged before and after every run
  (8,388,608 bytes, SHA-256 `940ad5f0...f059e`). Only `build/` was written to; the sole
  tracked addition remains this review record.

### Remaining non-blocking notes on the fixed revision

- [LOW] `tests/unit/test_authored_image.py:273-291` - the new manifest-publish test keys
  its fake `os.replace` on *call order* (`published[1]`), not on the target, and patches
  the process-global `os.replace`. It is correct today (the transaction replaces the image
  first and the manifest second) and passed, but it would be more robust to fail the call
  whose target name ends in `.dragonbyte.json`; as written, any unrelated `os.replace`
  between the patch and the save would misalign the assertions.
- [LOW] The known limits listed in item 6 above remain open by decision; nothing in this
  delta changes their reachability.
- The first pass's uncertainties stand unchanged: no full-suite run, the pre-change
  pass/skip split confirmed arithmetically only, no live Qt click-through, and 8.3
  short-name aliasing untestable on this volume.

## Stop

This record covers the frozen, uncommitted implementation on
`authored-image-pipeline-001`, including the post-review delta. It does not modify the
implementation, the tests, the canonical ROM or any other tracked file, and nothing was
committed, staged or pushed.
