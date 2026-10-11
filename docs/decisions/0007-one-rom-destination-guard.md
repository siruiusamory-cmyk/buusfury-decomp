# ADR 0007 - One ROM-destination guard

- **Status:** accepted (2026-10-10)
- **Evidence:** `docs/ROM_SAFETY.md` (the write paths that must refuse a protected
  destination); `docs/DEVELOPMENT.md` (one owner per rule); the merged guard itself in
  `tools/webfoot/destination.py`.

## Decision

Destination-write protection lives in `tools/webfoot/destination.py` and only there.
`tools/webfoot/output_identity.py` is a verification tool for the canonical-storage
migration and must not be called from any write path.

The second module is **not on main**: it lives on the unmerged branch
`ticket/canonical-hardlink-guard-001`, part of the canonical-storage migration, which is
prepared and not executed and whose go-ahead the owner has not given. This rule therefore
binds the merged guard today and binds that module when and if the migration lands. A
reader looking for the file before then will not find it, and that absence is expected
rather than a lost decision.

## Context

The merged guard in `tools/webfoot/destination.py` refuses a protected destination by file
identity, and it is what every publisher calls before it creates anything. The
canonical-hardlink work on `ticket/canonical-hardlink-guard-001` additionally added
`tools/webfoot/output_identity.py`, which also refuses a shared destination, because that
branch predates the merge that landed the first one. The owner adopted the view that one
guard should own the rule and the second module should verify the migration instead of
guarding writes.

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
- `tools/webfoot/output_identity.py` does not exist on main. It is present on
  `ticket/canonical-hardlink-guard-001`, whose guard commit
  `be6677f8f77d15dc7a90263790066ef626627905` adds the module, its test and the incident
  record together. Measured here: `git ls-tree origin/master tools/webfoot/` lists no such
  file, and `git log --all -1 -- <that path>` resolves only to that branch.
- The storage migration is prepared and **not executed**: nothing in the canonical store
  has been unlinked, repointed or copied, and no worktree has been repointed. The go-ahead
  for it is the owner's and has not been given.
