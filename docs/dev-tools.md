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
| `deleted` | tracked and absent |
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
It never trusts an exit code: a `glab` that exits non-zero after a merge that landed
is reported merged, and a `glab` that exits 0 without moving the MR is refused.

**The 405 contradiction, resolved.** The memory store records 405 as a flake
("immediate retry merged", MRs !233 and !236); GitLab documents it as deterministic
when merge-train enforcement is on and the request omits `auto_merge=true`. This
wrapper assumes the DETERMINISTIC reading, because that is the one where a blind
retry masks a real failure, and it stays safe under the flake reading too: a 405
with no effect is retried once, a 405 that recurs is refused with both readings
quoted.

## `review_queue_index.py` - what is open

```powershell
.venv\Scripts\python.exe -m tools.dev.review_queue_index [--ticket TICKET-001] [--json]
```

Lists the requests in `~/.dsh/review-queue/requests`, each with the ticket, the
review SHA, the age in hours, whether a claim exists, and the verdict read from the
matching result file. It prints the open count and the claimed-and-awaiting count.
It is strictly read-only over the queue and its `build()` is a pure function over a
queue directory, which is what the guard exercises: the real queue belongs to other
lanes and a test must not read or write it.
