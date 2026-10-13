# Developer tools: the five commands the retros asked for

Each tool here exists because a measured failure cost a session, and each carries a
guard that can fail. They are developer entry points, not product surfaces: nothing
under `src/` reads them, no capability claims them, and nothing here publishes.

| Tool | Replaces | Guard |
| --- | --- | --- |
| `tools/dev/worktree_owners.ps1` | the 40-second ad hoc ownership sweep (dbz-dev retro 1.1) | `tests/unit/test_worktree_owners.py` |
| `tools/dev/check_citations.py` | re-deriving stale `path:line` citations by hand (dbz-dev retro 1.2) | `tests/unit/test_dev_tools.py` |
| `tools/dev/probe_worktree.ps1` | a `cmd` redirect that silently changed the bytes a probe ran (dbz-dev retro 1.6) | `tests/unit/test_dev_tools.py` |
| `tools/dev/commit_msg.ps1` | the here-string split and the BOM that broke two commits (dbz-dev retro 1.7) | `tests/unit/test_dev_tools.py` |
| `tools/dev/merge_mr.py` | guessing whether `glab mr merge` merged (dbz-dev retro 6.5) | `tests/unit/test_dev_tools.py` |
| `tools/dev/review_queue_index.py` | joining the review queue's two directories by hand (dbz-dev retro 1.5) | `tools/dev` is outside the repository; its guard moves the queue to a fixture |

`scripts/new-ticket-worktree.ps1` calls the ownership sweep instead of carrying its
own copy: one definition per compared fact (freeze checklist line 14). A cut now
also exits 0 on success. It used to inherit the exit code of the last native call, so
a stale worktree entry made a fully successful cut report 128.

## Where each guard runs, and where the behaviour is proved

CI is Linux, where no `.ps1` can execute. A behavioural guard for a PowerShell tool
therefore SKIPS there with a named reason, and a pure-Python TEXT guard over the
script's own bytes runs everywhere and pins the invariant the behaviour rests on.
Both layers exist on purpose: an acceptance that rests only on a test that skips in
CI proves nothing there. The table below is GENERATED from
`tests/unit/test_skip_coverage_guard.py`, which derives which nodes skip from the
AST of the two test modules and fails when this block and the code disagree. Do not
edit it by hand; regenerate it.

<!-- BEGIN skip-guard-table -->
`15` nodes skip on a runner without PowerShell: 8 in `tests/unit/test_dev_tools.py`, 7 in `tests/unit/test_worktree_owners.py`.
13 of these were counted from the test-sdk trace of job `17121704860` at `9c34f1ae`; the probe module's two escape guards were added after that trace. On Windows these nodes run, so no local run can produce the number.

| Test file | Nodes that skip without PowerShell |
| --- | --- |
| `tests/unit/test_dev_tools.py` | 8 |
| `tests/unit/test_worktree_owners.py` | 7 |

Each one names the text guard that holds its invariant:

| Node that skips | Text guard that runs in CI |
| --- | --- |
| `tests/unit/test_dev_tools.py::test_the_message_writer_writes_no_byte_order_mark` | `tests/unit/test_dev_tools.py::test_the_message_writer_keeps_the_no_bom_spelling` |
| `tests/unit/test_dev_tools.py::test_the_no_bom_claim_is_driven_to_failure` | `tests/unit/test_dev_tools.py::test_the_bom_failure_probe_names_the_shell_whose_utf8_writes_a_mark` |
| `tests/unit/test_dev_tools.py::test_the_probe_worktree_copies_and_verifies_when_the_bytes_match` | `tests/unit/test_dev_tools.py::test_the_probe_refuses_with_both_digests` |
| `tests/unit/test_dev_tools.py::test_the_probe_worktree_leaves_the_caller_worktree_untouched` | `tests/unit/test_dev_tools.py::test_the_probe_refuses_with_both_digests` |
| `tests/unit/test_dev_tools.py::test_the_probe_worktree_refuses_a_file_whose_copy_differs` | `tests/unit/test_dev_tools.py::test_the_probe_refuses_with_both_digests` |
| `tests/unit/test_dev_tools.py::test_the_probe_worktree_refuses_a_parent_relative_name_that_would_escape` | `tests/unit/test_dev_tools.py::test_the_probe_pins_its_escape_refusal_as_text` |
| `tests/unit/test_dev_tools.py::test_the_probe_worktree_still_copies_a_nested_relative_name` | `tests/unit/test_dev_tools.py::test_the_probe_pins_its_escape_refusal_as_text` |
| `tests/unit/test_dev_tools.py::test_the_writer_refuses_an_empty_message` | `tests/unit/test_dev_tools.py::test_the_message_writer_keeps_the_no_bom_spelling` |
| `tests/unit/test_worktree_owners.py::test_a_carrier_is_not_reported_as_a_writer_without_its_blob_match` | `tests/unit/test_worktree_owners.py::test_the_sweep_pins_the_classification_branches` |
| `tests/unit/test_worktree_owners.py::test_a_deleted_file_is_classified_as_deleted_not_unreadable` | `tests/unit/test_worktree_owners.py::test_the_sweep_pins_the_delete_branch_as_text` |
| `tests/unit/test_worktree_owners.py::test_a_file_that_differs_from_master_is_classified_as_authored` | `tests/unit/test_worktree_owners.py::test_the_sweep_pins_the_classification_branches` |
| `tests/unit/test_worktree_owners.py::test_a_staged_blob_equal_to_masters_is_classified_as_carrying_master` | `tests/unit/test_worktree_owners.py::test_the_sweep_pins_the_classification_branches` |
| `tests/unit/test_worktree_owners.py::test_a_worktree_file_equal_to_master_is_carrying_not_authored` | `tests/unit/test_worktree_owners.py::test_the_sweep_pins_the_classification_branches` |
| `tests/unit/test_worktree_owners.py::test_an_unmerged_file_is_classified_as_conflicted` | `tests/unit/test_worktree_owners.py::test_the_sweep_pins_the_classification_branches` |
| `tests/unit/test_worktree_owners.py::test_the_sweep_exits_zero_when_a_worktree_entry_is_unreadable` | `tests/unit/test_worktree_owners.py::test_the_sweep_sets_its_own_exit_code` |

Proven on Windows only, because the check needs a host that can run the script:

| Invariant | Why it cannot be asserted as text |
| --- | --- |
| a message file's first three bytes | the writer's own self-check reads the file it just wrote, and the BOM the probe reproduces is Windows PowerShell 5.1's, which only exists on Windows |
| the committed identity of a copy | a probe copy is verified by hashing it; that the destination really holds the source's bytes needs a filesystem and a PowerShell host |
| the sweep's classification branches | the four branch conditions are pinned as text by test_the_sweep_pins_the_classification_branches and the delete branch by test_the_sweep_pins_the_delete_branch_as_text, but which ONE fires for a given `git status` entry is decided by git at run time and can only be observed on a host that can execute the script |
<!-- END skip-guard-table -->

The behavioural proof is a Windows run, recorded in the ticket's report; the same
tools were used to cut and commit that ticket, which is the strongest form of it.
The `rom-local` GitLab runner is Windows too, but it only takes protected refs, so it
cannot run a feature-branch job: the Linux text guards are the regression net for
every branch, and a Windows run is a deliberate act.

The skip path itself is proved twice: one test neuters the lookup and asserts the
helpers raise `pytest.skip`, and a second reruns three of the behavioural tests in a
subprocess with `shutil.which` disabled and asserts three skips and no failure.

`test_mgba_extra_script.py`'s launcher guards follow the same rule: the four `-DryRun`
checks need the canonical image and skip without it, one check proves the optional
`-StatePath` needs neither image nor emulator, and the text guards run everywhere.

## `worktree_owners.ps1` - who holds which file

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\dev\worktree_owners.ps1
```

Read-only. For every registered worktree it prints the branch, each dirty file's
mtime, whether the dirt is staged, in the worktree or untracked, and one
classification from a `git hash-object` comparison against
`<baseline>:<path>`:

| Classification | Meaning |
| --- | --- |
| `carries-master` | the file's bytes are the baseline's own blob: a mid-merge carrier, not a writer |
| `authored` | the bytes exist only here: a lane is holding this file |
| `conflicted` | an unmerged path (`UU` and friends) |
| `new-in-branch` | untracked, or not in the baseline at all |
| `deleted` | tracked and absent, staged delete included |
| `unreadable` | git refused the entry (a stale worktree registration) |

`-Markdown` prints the same rows as a table for a check-in comment, `-Json` prints
the same data for a script, `-MaxFiles N` bounds the rows shown per worktree, and
`-Repository`/`-Baseline` point it at another repository.

Two measured traps are encoded in it. `git hash-object --stdin` does NOT apply the
clean filter, so on a CRLF checkout it hashes 14 bytes where the blob is 13 and
every file looks `authored`; the path form does apply it. And `git worktree list`
prints some entries in the MSYS spelling (`/c/<dir>/...`) and others in the native
Windows spelling, in the same output.

## `check_citations.py` - does `file:line` still point at what it claims

```powershell
.venv\Scripts\python.exe -m tools.dev.check_citations docs/research/PROJECT_STATE_AUDIT_RECONCILIATION.md
.venv\Scripts\python.exe -m tools.dev.check_citations --fail-on-orphan --quiet <file-or-directory>
```

Run it at freeze over ticket prose, debt-node text and ledger rows. It reports
`RESOLVES`, `MOVED` (with the symbol's new line) or `ORPHAN` for every `path:line`
and `path:A-B` token. An explicit target is required: there is no whole-tree scan,
because that is noise. `--fail-on-orphan` is the only thing that makes it exit
non-zero, so a moved citation never blocks a freeze by itself.

`MOVED` is earned by finding a symbol, never by guessing: a token counts as the
symbol only when it is backticked and looks like a name (an underscore or an inner
capital), which is what `_saved`, `unsaved_edit_count` and `open_rom` look like and
what `Merged` does not. A citation with no name beside it is reported unmarked.

Measured on `docs/research/PROJECT_STATE_AUDIT_RECONCILIATION.md` at the commit that
added it: 117 RESOLVES, 10 MOVED, 13 ORPHAN, including the real drift the retro
named - `map_browser_tab.py:5169` `unsaved_edit_count` is at 5297.

## `probe_worktree.ps1` - a probe with its own provenance

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\dev\probe_worktree.ps1 `
    -Path tools\webfoot\journal.py,tests\unit\test_dragonbyte_rawbytes.py -Sha <commit>
```

Adds a detached worktree at the named commit under `build/`, byte-copies only the
named files into it, hash-verifies every copy against its source, and prints both
full SHA-256 digests. A mismatch prints both digests and exits 3 with the worktree
left in place; a match removes the worktree. `-VerifyOnly <worktree>` re-audits an
existing probe instead of building one. The caller's worktree is never modified.

## `commit_msg.ps1` - a message that survives the shell

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\dev\commit_msg.ps1 `
    -Message 'Add the one-writer sweep' -Path scripts\new-ticket-worktree.ps1
```

Writes the message with `[System.IO.File]::WriteAllText` and
`UTF8Encoding($false)`, verifies its own first three bytes are not `EF BB BF`, then
runs `git commit -F <file>`. `-NoCommit` writes the message and stops. An empty or
all-blank message is refused by name. The machine's pre-commit hook rules are stated
in the file: no em dash in a staged `.md` or `.txt`, and a subject that describes
the change rather than the process that produced it.

## `merge_mr.py` - merge the SHA that was signed off

```powershell
.venv\Scripts\python.exe -m tools.dev.merge_mr --mr 240 --sha <signed-off sha> [--dry-run]
```

Reads the MR, refuses unless `<sha>` is its current head, merges, reads the MR
again, and spends at most ONE retry - only when there was no server-side effect.
The pin is checked before EVERY attempt, including the retry, and the merge call
itself carries `--sha <sha>`: a rebase under a frozen candidate is refused rather
than merged. It never trusts an exit code: a `glab` that exits non-zero after a merge
that landed **the pinned head** is reported merged, and a `glab` that exits 0 without
moving the MR is refused. Only an MR whose state is `merged` AND which carries a merge
commit counts as an effect, so a move to `closed` or `locked` is never reported as a
merge; a merge that landed a DIFFERENT head is refused with exit 4, because a merged
state is not this review's merge unless the merged head is the pin.

**The 405 contradiction, resolved.** The memory store records 405 as a flake
("immediate retry merged", MRs !233 and !236); GitLab documents it as deterministic
when merge-train enforcement is on and the request omits `auto_merge=true`. This
wrapper assumes the DETERMINISTIC reading, because that is the one where a blind
retry masks a real failure, and it stays safe under the flake reading too: a 405
with no effect is retried once, a 405 that recurs is refused with both readings
quoted. The match is on an HTTP status, never on the substring `405`, so an error
text like `pipeline 4057 failed` is a real failure and is not retried.

## `review_queue_index.py` - what is open

```powershell
.venv\Scripts\python.exe -m tools.dev.review_queue_index [--ticket TICKET-001] [--json]
```

Lists the requests in `~/.dsh/review-queue/requests`, each with the ticket, the
review SHA, the age in hours, whether a claim exists, and the verdict read from the
matching result file. The verdict is the LAST line of that file, where every result
in this queue puts it, so prose above it cannot turn a BLOCKED review into a pass. A
negative age is labelled as clock skew rather than printed as a bare negative
number. It prints the open count and the claimed-and-awaiting count. It is strictly
read-only over the queue and its `build()` is a pure function over a queue
directory, which is what the guard exercises: the real queue belongs to other lanes
and a test must not read or write it.
