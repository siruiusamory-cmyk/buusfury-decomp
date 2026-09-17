# GitLab integration workflow

How to push a branch, open a merge request and finalize after merge in this
repository without tripping on environment or tooling traps. Operational only:
permanent rules stay in [`../DEVELOPMENT.md`](../DEVELOPMENT.md) and
[`../docs/DEVELOPMENT.md`](../docs/DEVELOPMENT.md).

Read this before pushing, and before reporting any authentication failure. The
most expensive mistake in this area is misreading an environment problem as a
permissions problem: agent sessions are non-interactive, so a credential helper
that depends on an interactive login profile can hand git an empty password and
produce an "Access denied" that says nothing about authorization. Diagnose the
resolved helper before concluding anything, and never retry a push in a loop,
weaken a credential check, or work around one.

This document is deliberately not summarized in `docs/DEVELOPMENT.md`: that file is bound
to 300 lines as an always-loaded context budget and is already at 299, so a new
rule has to be condensed to fit rather than displace an existing one.

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

`<home>\.gitconfig` (seen from MSYS2 as `<home>/.gitconfig`)
previously set a per-host helper that read a shell variable:

```text
helper = "!f() { echo username=oauth2; echo password=$GITLAB_TOKEN; }; f"
```

`GITLAB_TOKEN` is set by an interactive login profile. **Agent and scripted
sessions are non-interactive and do not run that profile, so the variable is
empty**, the helper emits an empty password, and GitLab refuses the push. The
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
git worktree add --detach <temp>\<verify> origin/master
```

Portable tests should pass with no ROM present; ROM-gated tests skip and report
the reason. Run the ROM-gated subset against the canonical ROM when the change
touches decode or extraction paths, then re-hash the ROM to prove it was only
read.
