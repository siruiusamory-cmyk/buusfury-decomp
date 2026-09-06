# TOOLKIT-003 review record

Result: COMPLETE, owner accepted. Narrow local acceptance commit authorized;
TOOLKIT-004 is not started. Full specification: `archive/TOOLKIT-003.md`.
Exact changing test counts are recorded only in `../PROJECT_<local-state-name>`.

## Baseline and activation

Implementation HEAD stayed `f66007b34d81c7f7c5aac0d1bf8cbf796918a07e`. The index was
empty at implementation and acceptance start. Existing TOOLKIT-001/002 code and many
research/remake files were already unstaged or untracked. They were used as the
baseline, not attributed to this ticket. No baseline commit was requested.

The owner explicitly authorized replacing the stop-only active slot. Its full
closure text was archived in `archive/TOOLKIT-002-COMPLETE.md` before activation;
the archived P-009/P-010 debts remain intact. The two lifecycle assertions that
required the old active-slot contents were updated without dropping their
archived-evidence checks (`tests/unit/test_workflow_migration.py:76`).

## Ticket-only files

New files:

- `tools/webfoot/layout.py`: typed ranges, anchors, ownership and evidence/encoding contracts.
- `tools/webfoot/document.py`: verified immutable document, graph validation and candidate scan.
- `tools/webfoot/allocation.py`: deterministic profile-only allocator.
- `tools/webfoot/relocation.py`: batch transaction and existing-writer integration.
- `tools/webfoot/relocation_proof.py`: constructed synthetic CLI demonstration.
- `tests/unit/test_relocation.py`: portable success/failure proofs.
- `docs/relocation.md`: APIs, trust boundaries and limitations.
- `docs/research/archive/TOOLKIT-002-COMPLETE.md`: prior placeholder preserved.
- `docs/research/archive/TOOLKIT-003.md`: accepted specification and closure.
- This review record.

Modified files (additions made on top of existing content):

- `tools/webfoot/binary.py`: explicit `FileOffset` primitive.
- `tools/webfoot/profile.py`: strict verified free-region declarations.
- `tools/webfoot/write.py`: relocation provenance, revalidated public plans,
  manifest alias/overwrite checks and staged exclusive publication/rollback.
- `tools/webfoot/cli.py`: synthetic `relocation-proof` inspection command.
- `tests/unit/test_workflow_migration.py`: authorized lifecycle activation checks.
- `docs/architecture.md`: new layers and retained scope boundaries.
- `docs/PROJECT_<local-state-name>`: verified state and exact test results.
- `docs/PROJECT_<local-state-name>`: activation and closure.

No modifications to the existing stat codecs, stat semantic APIs, project
format/build code, canonical profile data, runtime tools or Godot files were
needed. Hash comparison against the captured dirty-file inventory confirms
unchanged unrelated files.

## Evidence and proofs

- Synthetic growth and exact rewrite: `tests/unit/test_relocation.py:69` proves
  `0x100/8 -> 0x208/39`, old-region preservation, exact absolute and relative
  source bytes, ownership and complete manifest attribution.
- Allocation determinism: `tests/unit/test_relocation.py:101` permutes both
  requests and free-region declarations. Stable anchor order yields offsets
  `0x208`, `0x204`, `0x220`, reusing the earlier alignment gap safely.
- Candidate failure: `tests/unit/test_relocation.py:177` blocks and names
  `0x000000C0`; the scanner test at line 184 retains candidate classification,
  preserves an interior delta and blocks at `0x000000C8` after graph insertion.
- Multi-anchor movement: `tests/unit/test_relocation.py:242` moves an embedded
  relative reference source and target, checks both batch orders, and preserves
  original bytes. Shrinking away an interior target is rejected at line 214.
- Transaction failure tests cover insufficient space, alias/existing-manifest
  collisions, wrong actual file, staging errors, publication rollback and
  post-validation failure without output (lines 287, 314, 328, 389, 412, 424).
- `relocation.py:47` verifies the original profile before layout use; its
  resulting graph is validated before emission. `document.py:65` checks source
  bytes, target deltas, bounds, ownership, provenance and graph consistency.
- Existing canonical stat/build tests passed, including the unchanged entire
  ROM rebuild, deterministic extraction/repeated outputs/manifests, semantic
  Wolf HP edit and one-byte attribution. These are local-ROM integration
  checks, not fresh emulator/runtime observations.

All new binary-layout proof is synthetic. No numeric game observation was
promoted to CONFIRMED and no new commercial format was decoded. The canonical
relocation proof is omitted because checked-in profiles declare no verified
free space; new research is outside this ticket.

## Defects and architectural limits

Pre-implementation review identified that the old writer could overwrite the
source through `manifest_path`, and published the image before writing a
potentially failing manifest. Both are fixed through path preflight, staging,
exclusive publication and rollback. Public `WritePlan` construction also no
longer bypasses change validation in `apply_plan`.

One new test initially expected a monotonic allocator cursor. The specified
lowest-address first-fit policy correctly reused a gap; the test expectation
was corrected and both input orderings are covered. Lifecycle tests needed
activation updates. No unrelated regression was weakened.

Atomicity means no partial image and rollback on caught failures; this is not a
crash journal across multiple files. An OS crash between manifest and image
publication may leave a complete manifest only. One transaction batches all
moves against the original verified base. Modified-image reopening, persistent
graphs, complete discovery and canonical relocation authority remain deferred.
The bounded pointer scanner is never a completeness proof.

## Independent review and safety

Independent an independent reviewer review approved code, tests, CLI and documentation with
no blocking finding. An initial reviewer test run encountered pytest temp-folder
permissions; its isolated-temp rerun passed. The reviewer caught a prospective
test-count misstatement before final reporting; the recorded counts use actual
collection/results. Its documentation ordering suggestion was incorporated.

Canonical ROM hash stayed
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`; its size and
mtime stayed unchanged. Local save/state hashes and mtimes also stayed unchanged.
No mGBA, Ghidra or new reverse engineering was performed. Generated integration
outputs are pytest temporary artifacts, not tracked proprietary fixtures.
Tracked-file checks found no ROM/save/state/dump/upstream artifact. The owner
subsequently authorized narrow staging and one local commit. No push, stash or
destructive Git operation is authorized or needed.

Raw `git diff --check` reports pre-existing CRLF whitespace in the dirty remake
files and workflow test; those unrelated edits were preserved. The full check
passes with `git -c core.whitespace=cr-at-eol diff --check`. New ticket files
were also checked for trailing whitespace. Acceptance staging selects only
ticket-owned paths/hunks; pre-existing stat/profile/CLI/documentation changes
remain in the worktree. The reviewed `write.py` was previously untracked: its
first tracked version necessarily includes the fixed-length writer primitives
used by relocation, but no stat/project semantic implementation is included.
No next ticket is authorized by completion or acceptance.

## Acceptance validation

The staged file list and complete staged diff were inspected before commit;
`git diff --cached --check` passes without a CRLF override. CLI/profile changes
were staged independently of pre-existing stat and project work; workflow-test
line endings were preserved in the index, leaving the original CRLF-only
worktree condition unstaged. The architecture section was staged separately.

The full worktree suite was rerun after staging and passed. An isolated export
of the staged snapshot passed the relocation, binary, profile, CLI and workflow
suite. Its broader unit run exposed existing tests depending on excluded
untracked `p006_reaction_trace.lua` and `p006_hit_bracket_scan.lua` files, plus a
wheel subprocess error. The staged wheel test then passed with filesystem
access and a fresh ignored pytest temp directory. No unrelated runtime file or
test change was staged to hide those baseline dependencies. Exact results are
recorded in `../PROJECT_<local-state-name>` and distinguish worktree from index validation.

ROM/save/state hashes and mtimes were rechecked against the pre-staging snapshot
and remain unchanged. No canonical relocation proof or new research was added.
