# ADR 0008 - Interrupted work resumes from committed state

- **Status:** accepted (2026-10-10)
- **Evidence:** `docs/decisions/0004-proof-levels.md` (a claim is only as strong as
  the proof behind it); `docs/DEVELOPMENT.md` ("Testing and validation",
  "Focused validation and the full suite"); `docs/testing.md` (the gates a
  resumed contributor re-runs).

## Decision

Long-running work in this repository is **checkpointed by committing a green
tree**, and interrupted work is resumed from that commit and from the written
task record, never from conversation, memory or a summary. A resumption is
treated as verified only when the resuming contributor re-measures what it
inherits: the authoritative remote, the commit, the working tree, and the gates
that bind the frozen tree.

Three rules follow, and later work is expected to obey them:

1. **Commit green state as it is reached.** An uncommitted working tree is not a
   checkpoint. Work that cannot be committed yet states, in its own record, what
   is finished and what is not.
2. **Never re-do what the record shows as done, and never re-run what the record
   binds.** A gate result is valid for the tree it ran on; a resumed contributor
   confirms that the tree is unchanged rather than paying for the same suite
   again.
3. **Never push, merge or publish work whose own record says it is deliberately
   local.** Pushing "to be safe" is not caution; it is a second mutation of a
   state that was already correct.

## Context

Ordinary causes stop long work in this repository: a tool is closed, a machine
restarts, a long measurement is interrupted. When the only record of the
interrupted step is the tail of a conversation, resumption costs the whole step
again, and it can silently repeat a mutation that already landed - a second
commit, a second merge request, a second write to an input that must be written
once.

Committing green state makes the cost of an interruption proportional to the
work since the last commit rather than to the whole task, and it gives a later
contributor something verifiable to stand on: a commit, a clean tree and a
written record of what remains.

## Consequences

- Resumption begins with measurement - remote, commit, tree, gates - and the
  measurements are recorded where the next contributor reads them.
- The evidence for a resumption is durable repository and record state, so it
  survives a lost terminal, a restarted machine and a change of contributor.
- Work that is deliberately local stays local, and its record says so, so no
  later contributor publishes it as an accident of caution.
- A resumed step may legitimately wait rather than proceed when ownership of the
  work cannot be established; waiting is the failure that costs time, and
  resuming a live writer is the failure that loses work.
