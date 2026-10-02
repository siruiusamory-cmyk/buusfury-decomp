# Allocator checkpoint B: canonical-EOF straddle guard and default provenance

The safety precondition for the production allocator: the canonical-EOF straddle
guard, default sibling provenance publication, and the mutation proofs behind
both.

## Scope, and what is deliberately out of it

| In scope | Out of scope (untouched) |
|---|---|
| CQA-09: the canonical-EOF straddle regression, with its mutation proof | CQA-05, CQA-06, CQA-07, CQA-08 |
| CQA-12: default sibling provenance manifest, `.gitignore` coverage, focused regression + mutation proof | Any redesign of `WriteManifest` or the provenance architecture |
| CQA-10: documentation / re-scope only | Any general audit cleanup, and any broadening of CQA-10 |
| - | Production allocator code (Checkpoint C) and any promotion of candidate free space |

Nothing in Checkpoint A's measurements changed. The promotable census is still
115 runs / 23,595 bytes and the declared free space is still the single 256-byte
TOOLKIT-028 window.

---

## 1. CQA-09 - the canonical-EOF straddle guard

### 1.1 What the finding measured

`write.plan_changes` refuses a change that begins in the last canonical byte and
ends in the appended padding:

```python
if change.offset < len(base) < change.end:
    raise ChangeValidationError(
        f"{change.owner}: change at 0x{change.offset:08X} straddles canonical EOF")
```

For exactly that shape, `offset >= len(base)` is false, so the
allocator-authorization branch never runs and the bounds, size and overlap checks
all pass. The guard is the only thing refusing it - which is why removing it was
invisible: the audit measured the `writer` gate at 443 passed and
`fast and (map or research)` at 1003 passed with the branch deleted.

### 1.2 The regression, at the shape the finding specified

`tests/unit/test_rom_expansion.py` gains two tests:

* `test_a_change_straddling_canonical_eof_is_refused_even_when_it_is_authorized`
  - a 10-byte base, a 16-byte generated output, a one-byte authorized allocator
    span in the expanded region, and a 2-byte change at offset 9 - expecting
    `ChangeValidationError` matching `straddles canonical EOF`;
* `test_a_change_inside_the_authorized_span_is_accepted` - the **positive
  control**: the same authorized span accepts a change that does not straddle, so
  the refusal above cannot be explained by any other check on that plan.

`plan_changes` was not rewritten and CQA-09 was not generalised.

### 1.3 Mutation proof M4 - the guard removed

`write.py`'s straddle branch was deleted in an isolated copy of the tree (created
with `robocopy`, so the reviewed tree was never modified):

```text
tests/unit/test_rom_expansion.py ... 1 failed, 11 passed

FAILED test_a_change_straddling_canonical_eof_is_refused_even_when_it_is_authorized
       Failed: DID NOT RAISE <class 'tools.webfoot.write.ChangeValidationError'>
```

That is the finding reproduced exactly: the case fails, and **the other eleven
tests in the file still pass**, which is the invisibility CQA-09 recorded. The
copy was deleted afterwards.

---

## 2. CQA-12 - provenance published by default

### 2.1 What the finding measured

The Workbench Build tab never supplied `manifest_path` (`build_panel.py`'s
`_run_build` passes four positional arguments), and the CLI only recorded one when
`--manifest` was given, so the primary authoring surface emitted an 8 MiB
derivative whose only provenance was in memory.

### 2.2 The change, and how small it is

`build.build_project` gains one sentinel and one resolver:

```python
MANIFEST_BESIDE_OUTPUT   # the default: publish beside the emitted image
None                     # explicit opt-out: publish nothing
<path>                   # explicit redirect
```

* The sibling path is **not** respelled: `manifest_path_for_build` delegates to
  `authored_image.manifest_path_for`, the function the authored-image transaction
  already owns, so both writers agree on where a derivative's provenance lives
  (`<image>.gba.dragonbyte.json`).
* `WriteManifest`, `emit_image` and the provenance architecture are unchanged.
  The default simply supplies the `manifest_path` argument that was already
  supported, so publication inherits every existing guarantee: source-alias
  refusal, new-destination refusal, staged publication with rollback, and the
  refusal to clobber an existing manifest **before** anything is written.
* The CLI keeps `--manifest` (now a redirect) and gains `--no-manifest`, the two
  being mutually exclusive, so no caller loses provenance by omission.
* The Workbench Build tab is **unchanged**: it still passes no path, and
  therefore inherits the default. That is pinned as a mechanism rather than a
  spelling - `tests/unit/test_workbench_build_manifest.py` asserts the panel calls
  `build_project` with no `manifest_path` keyword at all.

`.gitignore` gains one narrow pattern:

```gitignore
*.dragonbyte.json
```

`*.gba` does not match `foo.gba.dragonbyte.json`, so a derivative saved outside an
ignored build directory would otherwise commit the manifest - which carries
ROM-derived provenance - while ignoring the ROM it describes.

### 2.3 Focused regressions

| Test | What it pins |
|---|---|
| `tests/unit/test_build_manifest_default.py::test_the_default_writes_the_manifest_beside_the_output` | the default resolves to the authored-image sibling |
| `::test_disabling_and_redirecting_are_both_explicit` | `None` and a path behave as documented |
| `::test_the_default_does_not_depend_on_the_output_directory_existing` | resolution is pure path arithmetic |
| `::test_the_cli_defaults_to_publishing_and_can_only_opt_out_explicitly` | CLI default and opt-out |
| `::test_the_cli_refuses_to_redirect_and_disable_at_once` | mutual exclusion |
| `::test_the_manifest_pattern_is_ignored_and_stays_narrow` | the `.gitignore` pattern matches the generated manifest and nothing unrelated |
| `tests/unit/test_workbench_build_manifest.py` | the Build tab inherits the default |
| `tests/integration/test_project_build_rom.py::test_a_default_build_publishes_its_manifest_beside_the_output` | a real build writes the document, and it names this output's SHA-256; `manifest_path=None` writes none and the image is byte-identical either way |
| `tests/integration/test_project_build_rom.py::test_a_default_build_refuses_to_clobber_an_existing_manifest` | publication is fail-closed and leaves no image behind |

### 2.4 Mutation proof M6 - default publication disabled

`manifest_path_for_build`'s sentinel branch was made to return `None` in an
isolated copy:

```text
tests/unit/test_build_manifest_default.py ... 2 failed, 5 passed
integration -k default_build ................. 2 failed, 22 deselected
```

Both the portable default-build regression and the ROM-gated one fail, while the
Workbench inheritance test still passes - as it should, because that test pins the
panel's *coupling* to the default rather than the default itself. The copy was
deleted afterwards.

---

## 4. Debt recorded, not fixed here

```text
ROM-CAPACITY-ATLAS-SEED-OVERLAY-001   OPEN
```

The atlas seed (`tools/webfoot/atlas_producers/seed.py:530-566`) declares four
SDK-authored derivative structures inside the canonical free window
`[0x7EA400,0x7EA500)`, whose canonical bytes are `FF` fill: 32 + 8 + 11 + 20 = 71
of the window's 256 bytes. The rows state plainly that the content "does not exist
in the canonical image", but a canonical atlas built from them disagrees with the
canonical free declaration. Found during Phase A; the capacity model deliberately
does not consume the atlas. Full description:
[`ROM_CAPACITY_AND_ALLOCATION.md`](ROM_CAPACITY_AND_ALLOCATION.md) §8.1, with the
tracking entry in the audit's remediation-status block. **Outside Checkpoint B's
scope and not touched by it.**

---

## 5. Validation

Focused file-scoped tests only; no broad suite was run manually.

```text
tests/unit/test_rom_expansion.py
tests/unit/test_build_manifest_default.py
tests/unit/test_workbench_build_manifest.py
tests/unit/test_build_panel_overwrite.py
tests/unit/test_build_panel_guard.py
tests/unit/test_workbench_build_run_dialogs.py
tests/unit/test_authored_image.py
tests/unit/test_relocation.py
tests/unit/test_capacity_proof.py
tests/unit/test_free_space_audit.py
    -> 149 passed

tests/integration/test_project_build_rom.py     (whole-ROM builds; build.py blast radius)
tests/unit/test_test_gates.py
    -> 35 passed   (24 whole-ROM build tests + 11 gate tests; 427s)

mutation M4 (straddle guard removed)     -> 1 failed, 11 passed in test_rom_expansion.py
mutation M6 (default publication off)    -> portable 2 failed / 5 passed;
                                            ROM-gated 2 failed / 22 deselected
```

`git diff --check` clean. The canonical ROM's SHA-256 is unchanged, and no ROM or
ROM-derived fixture is committed.
