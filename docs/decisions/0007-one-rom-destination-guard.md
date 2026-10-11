# ADR 0007 - One ROM-destination guard

- **Status:** accepted (2026-10-10)
- **Evidence:** `docs/ROM_SAFETY.md` (the write paths that must refuse a protected
  destination); `docs/DEVELOPMENT.md` (one owner per rule); the merged guard itself in
  `tools/webfoot/destination.py`.

## Decision

Destination-write protection lives in `tools/webfoot/destination.py` and only there.
`tools/webfoot/output_identity.py` is a verification tool for the canonical-storage
migration and must not be called from any write path.

## Context

Two mechanisms answering one question grew in the same package. The merged guard in
`tools/webfoot/destination.py` refuses a protected destination by file identity, and it
is what every publisher calls before it creates anything. The canonical-hardlink work
added `tools/webfoot/output_identity.py`, which also refuses a shared destination,
because that branch predates the merge that landed the first one.

Two guards are worse than one here. A destination rule changed in one file and not the
other would be obeyed on some paths and not others, and the disagreement would be
silent, because a guard's failure mode is a refusal that looks exactly like a correct
refusal.

## Consequences

- A change to what a destination must not be is made in one file, and a reviewer looks
  there first.
- The migration that gives every worktree independent ROM inputs keeps the checks it
  needs: `require_singly_linked` and `findings` are what its verification step calls.
- A write path that calls `output_identity.py` is a defect rather than an alternative,
  and a reviewer should treat it as one.
- The migration may delete that module once it is complete and the checks are no longer
  needed.

## Evidence

- The decision was adopted on 2026-10-10.
- The guard that stays was merged by `8acaf883f81dc17039f536b228908b858a1c5f86`.
- The storage migration is prepared and **not executed**: nothing in the canonical store
  has been unlinked, repointed or copied, and no worktree has been repointed.
