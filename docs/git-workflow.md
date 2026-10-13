# GitLab integration workflow

How to push a branch, open a merge request and finalize after merge in this
repository without tripping on environment or tooling traps. Operational only:
the permanent rules stay in [`DEVELOPMENT.md`](DEVELOPMENT.md) and
[`REVIEW.md`](REVIEW.md).

Read this before pushing, and before reporting any authentication failure. The
most expensive mistake in this area is misreading an environment problem as a
permissions problem: a non-interactive session does not run an interactive login
profile, so a credential helper that depends on one can hand git an empty
password and produce an "Access denied" that says nothing about authorization.
Diagnose the resolved helper before concluding anything, and never retry a push
in a loop, weaken a credential check, or work around one.

This document is operational detail and is deliberately not summarized in the
policy documents, which stay readable by being concise.

## Credential helper: the canonical setup

The remote is HTTPS (`https://gitlab.com/siruiusamory/log1-remake.git`) and
authentication goes through the `glab` CLI, which already holds a working token
for `gitlab.com`:

```bash
glab auth status                 # confirms host, protocol and token presence
glab auth git-credential get     # prints the credential git will be handed
```

Both the global config and the repository config must resolve to:

```text
credential.https://gitlab.com.helper = !glab auth git-credential
```

Check what git actually resolves, including where each value came from:

```bash
git config --list --show-origin | grep credential
```

### The failure this prevents

`~/.gitconfig` (seen from MSYS2 as `/home/<user>/.gitconfig`)
previously set a per-host helper that read a shell variable:

```text
helper = "!f() { echo username=oauth2; echo password=$GITLAB_TOKEN; }; f"
```

`GITLAB_TOKEN` is set by an interactive login profile. **A scripted or
non-interactive session does not run that profile, so the variable is empty**,
the helper emits an empty password, and GitLab refuses the push. The
trap is that this global helper is consulted *before* the correct repository
helper, so the working configuration never gets a chance. Reads such as
`git ls-remote` had already been satisfied by an earlier credential lookup,
which makes the failure look like a permissions problem rather than a
configuration one.

Symptom:

```text
remote: HTTP Basic: Access denied. If a password was provided for Git
authentication, the password was incorrect or you're required to use a token
instead of a password.
fatal: Authentication failed for 'https://gitlab.com/siruiusamory/log1-remake.git/'
```

### Diagnose before concluding anything about permissions

Never report a permissions or token-scope problem from the error text alone.
Confirm which helper produced the credential and whether its password was empty:

```bash
GIT_TRACE=1 GIT_TERMINAL_PROMPT=0 git push --dry-run origin <branch> 2>&1 \
  | grep -E "credential|helper"
```

An empty `password=` in the helper output, or a `run_command` line naming a
helper that is not `glab auth git-credential`, is the cause. Token scope, SSH
keys and account state are separate questions; a working read path does not
prove the write path is authorized, and a broken helper does not prove it is
not.

### Fix the resolved helper, not the symptom

Do not work around this by exporting a token for one command; the next session
loses it. Point the offending config at `glab`:

```bash
cp ~/.gitconfig ~/.gitconfig.bak-<ticket>
git config --global credential.https://gitlab.com.helper "!glab auth git-credential"
```

Back up the file first, and mention the change in the final report, because it
is a change outside the repository. To push once without touching any config,
reset the offending helper to empty and re-add the correct one, since a
per-host helper is cumulative:

```bash
git -c credential.https://gitlab.com.helper= \
    -c credential.https://gitlab.com.helper="!glab auth git-credential" \
    push -u origin <branch>
```

If authentication is genuinely required and cannot be resolved, stop and report
it. Never retry a push in a loop, and never weaken or bypass a credential check.

## Pushing and opening the merge request

```bash
git push -u origin <branch>
git ls-remote origin refs/heads/<branch>   # confirm the remote tip equals HEAD
glab mr create --source-branch <branch> --target-branch master \
  --title "<title>" --description "<body>" --yes
```

`glab mr create` needs `--yes` to skip the confirmation prompt in a
non-interactive session. It has no `--description-file` flag.

Verify the result rather than trusting the creation output:

```bash
glab api "projects/siruiusamory%2Flog1-remake/merge_requests/<iid>"
```

Confirm `state`, `source_branch`, `target_branch`, `sha`, `detailed_merge_status`
and that `description` is the body you intended. A long multi-line description
passed through a Windows shell can be split into several arguments and silently
truncated, so check its length and tail. To set or repair a title or description
without fighting shell quoting, write a JSON body to a file and send it:

```bash
glab api --method PUT "projects/.../merge_requests/<iid>" \
  -H "Content-Type: application/json" --input body.json
```

The `Content-Type` header is required; without it the API answers `HTTP 415`.

## Two credential and output traps on the Windows workflow

Both were measured on this machine and this repository on 2026-09-28. They are
local observations, not a claim about GitLab generally.

**The git and REST API paths may need different header forms from the same
stored credential.** `git push` uses the credential `glab` already provides
through `glab auth git-credential`, and `glab api "<path>"` authenticates for
reads. A direct REST call from a script needs the credential spelled as a header
instead: `Authorization: Bearer <token>`. Measured on this token, against
`/api/v4/user`, `Authorization: Bearer` answered `200`, while both
`PRIVATE-TOKEN: <token>` and `Authorization: Basic` with the same token answered
`401`. The stored `glab` credential here is an OAuth-style token, which is why
the bearer form is the one that works; a personal access token may differ. Use
this form only when a `glab` subcommand cannot express what is needed, such as a
merge pinned to a reviewed SHA that must be passed as a request field.

**Redirected `glab` output is UTF-16 on this shell.** `glab ... > file` writes
UTF-16LE with a BOM (`FF FE 7B 00 22 00` for `{"`), so the file is not readable
UTF-8 text and a naive read produces NUL-separated garbage. Either read the file
with the encoding it was written in, or call the API from a process that decodes
the response explicitly rather than through a shell redirect.

## Before merging

Wait for the merge-request pipeline to settle and read its jobs, rather than
assuming a green pipeline means the gate ran:

```bash
glab api "projects/.../merge_requests/<iid>"                # head_pipeline.id
glab api "projects/.../pipelines/<id>"
glab api "projects/.../pipelines/<id>/jobs?per_page=20"
glab api "projects/.../jobs/<job_id>/trace" | tail -20
```

`.gitlab-ci.yml` runs `pytest tests/unit -q` in `test-sdk` on merge requests,
and on `master` it additionally runs `deploy-site`, which deploys the public
site. Merging therefore publishes; treat a merge to `master` as a deploy even
when the change looks internal.

Since 2026-10-12 the four test-stage jobs (`test-sdk`, `test-integration`,
`adjacency`, `test-site`) are configured to run on a self-hosted runner on the
owner's PC, tagged `local-ci`, rather than on the shared GitLab runners, whose
free monthly quota is spent. `deploy-site` did not move: it is the only job that
publishes and the only one that reads the protected Cloudflare credential, so it
stays on the shared runners with its `image: node:22`. **Unproven, not measured:**
no pipeline has been created since the routing landed, because GitLab refuses
pipeline creation while the namespace is over quota, so no routed job has run
from this configuration. The first proof is the first pipeline after the quota
resets. Until then a merge to the default branch neither runs the test gate nor
publishes. `docs/testing.md` ("Where each job runs, and why") owns the routing,
the runner's own limits, the credential scrub and the measured costs.

### Is the reviewed candidate still valid against live master?

A merge-request pipeline runs on the branch's own commit. It does not run on
master as master is at the moment the merge lands, and master moved while these
branches were open: measured 2026-10-12 from this session's own three merges.

| MR | recorded `diff_refs.base_sha` | master tip at merge | commits master gained between fork and merge | paths both sides changed |
|---|---|---|---|---|
| 230 | `1016ab49` | `c3fc145c` | 10 | 1 |
| 234 | `f097898b` | `f097898b` | 0 | 0 |
| 235 | `a8a2da5d` | `a8a2da5d` | 0 | 0 |

So 1 of 3 merges had drifted at merge time, and on that one the two sides did
change the same path: from fork `1016ab49`, both master and MR 230 changed
`docs/research/PROJECT_STATE_AUDIT_RECONCILIATION.md`. That merge composed
cleanly (`git merge-tree` reproduces its recorded tree `e3466f9a`) and its
post-merge master pipeline (`2938640540`) was green.

The gate below therefore stops 1 of 1 drifted merges on the measured sample, and
that one was a documentation path with no textual conflict. What it trades is a
rebase onto live master plus a re-run of the focused tests - minutes - for the
class of interaction no pipeline checks before the merge: two lanes editing one
file with no textual conflict, so the composition is never tested on either
side. That shape is the MAP-PAINT-class regression. The trade is kept on the
review of RETRO-CI-002-20261012-112919: read an exit 1 as an instruction to
rebase rather than as a block.

```powershell
# in a ticket worktree, never in the primary checkout
.\scripts\pre-merge-check.ps1 -Ref <branch or SHA>
```

It fetches the target, prints the predicted merged tree
(`git merge-tree --write-tree <target> <candidate>`, verified to reproduce the
tree GitLab recorded for all three merges above), and exits 1 when the target
changed a path the candidate changed, or when the merge conflicts. It pushes and
merges nothing, and it refuses the primary checkout structurally rather than by
name: the primary is the checkout that answers `.git` for its own
`git rev-parse --git-dir`, and a bare `.` is refused too. A path with no `.git`
at its root - a subdirectory of the primary included - is refused before that
compare, by the test at the root, and its message names the checkout root git
reports for it. A linked worktree of the primary is allowed; every ticket
worktree is one. It does write, and the wording matters: `git fetch`
creates remote-tracking refs, and `merge-tree --write-tree` writes tree and blob
objects into the shared `.git` - in a linked worktree, into the primary's
`--git-common-dir`. No branch, index, working tree or remote is touched.
`-ReportOnly` reports without failing; `-ExpectMergedTree <sha>` additionally
fails when the predicted merged tree is not that digest, and no such digest is
recorded anywhere today, so nothing checks the printed tree by default.

The gate is not a re-test. A full re-test costs about 26 minutes (measured on
the shared two-core runner before the test jobs moved to the owner's PC; the
cost on that machine is unmeasured), which is more than this risk has ever cost
in the measured sample, so it
is not run on every merge. An exit 1 asks for a rebase onto live master and a
re-run of the change's own focused tests; it does not ask for a full suite, and
the post-merge `master` pipeline remains the full-suite gate.

Merge with a merge commit so recorded commit SHAs stay reachable, and do not
squash a branch whose individual commits are cited as evidence:

```bash
glab mr merge <iid> --yes
```

## Finalizing after the merge

Fetch and record the exact post-merge `origin/master` SHA, then check that the
closeout records are still true. Each of these has caught a real defect:

1. **Reachability.** Cherry-picking reproduces a change under a *new* SHA. If
   the closeout cites the authoring branch's hashes, they may not be ancestors
   of `master` and may never have been pushed. Verify every cited hash:

   ```bash
   git merge-base --is-ancestor <sha> origin/master && echo reachable
   git log --oneline origin/master..<authoring-branch>   # should be empty
   ```

2. **Baseline drift.** A documentation-only follow-up moves `origin/master`
   past the SHA the previous record named as the next ticket's baseline. Name
   the tip and allow later documentation-only commits, or the record is stale
   the moment it lands.

3. **Superseded wording.** Search the merged documents for statements that the
   integration invalidated, such as a review still asserting the branch is not
   merged or not archived.

4. **Equivalence.** Prove the accepted content survived integration by comparing
   blobs, not by re-reading prose:

   ```bash
   git diff --stat <authoring-tip> origin/master -- <paths>
   ```

5. **Cleanup only after reachability is proven.** Delete a worktree or branch
   only when it holds no unique commits or tree objects.

   ```bash
   git rev-list --objects <branch> --not origin/master | wc -l
   git worktree remove <path>
   git branch -D <branch>
   ```

   Keep a branch if it holds a unique revision of any file, even when the
   difference looks cosmetic. Implying safety from "the merged version is
   better" is not proof that nothing is lost.

Scratch files written under `build/` are ignored, so removing a worktree leaves
them behind; clean them up deliberately.

## Validating a merged result

Prefer a detached worktree of the merge commit over reusing a branch that has
already been deleted or moved:

```bash
git worktree add --detach <temporary directory>\<verify> origin/master
```

Portable tests should pass with no ROM present; ROM-gated tests skip and report
the reason. Run the ROM-gated subset against the canonical ROM when the change
touches decode or extraction paths, then re-hash the ROM to prove it was only
read.
