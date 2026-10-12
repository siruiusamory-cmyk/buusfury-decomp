"""Land a merge request pinned to the exact SHA that was signed off.

The need (dbz-dev retro 6.5, this ticket's B9b): `glab mr merge` failed once with a
local git errno-1 error and NO server-side effect, and the immediate retry merged.
A wrapper that knows the difference removes the ambiguity about whether the merge
happened.

## The 405 contradiction, resolved

Two readings exist and they are both documented:

* The memory store calls 405 a flake: "hit the known 405 flake once, immediate
  retry merged" (RETRO-GUARDS-001, MRs !233 and !236).
* GitLab documents `405 Method Not Allowed` as DETERMINISTIC when merge-train
  enforcement is on and the request omits `auto_merge=true`.

A wrapper that blindly retries once is unsafe on the deterministic reading: the
retry repeats exactly the request GitLab already refused. So this wrapper assumes
the CONSERVATIVE reading - 405 may be deterministic - and makes the retry safe
under both:

1. read the MR state before the merge;
2. run the merge;
3. read the MR state after it;
4. retry at most ONCE, and ONLY when there was no server-side effect (the MR is
   still `opened` and its `merge_commit_sha` is still empty) AND the merge has not
   already been attempted with an error that recurs;
5. refuse a second retry and refuse a 405 that recurs, naming both readings.

Read the state, never the exit code alone: a `glab` that exits nonzero after a
successful merge (the push-exits-1 pattern) is a success, and a `glab` that exits 0
without moving the MR is not.

    python -m tools.dev.merge_mr --mr 240 --sha <signed-off sha>
    python -m tools.dev.merge_mr --mr 240 --sha ... --dry-run

Exit codes: 0 merged (or already merged), 2 usage or an unreadable MR, 3 refused
after a retry or for any merge that did not happen, 4 the pinned SHA is not the
MR's head.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_PROJECT = "siruiusamory/log1-remake"

#: An HTTP status, not a number that merely appears in error text: "pipeline 4057
#: failed" is a real failure and must not earn the single retry.
HTTP_405 = re.compile(r"\b405\b|Method Not Allowed")

#: The two readings of a 405, quoted so a refusal names them rather than guessing.
FLAKE_READING = (
    "memory store: 'hit the known 405 flake once, immediate retry merged' "
    "(RETRO-GUARDS-001 !233, !236)"
)
DETERMINISTIC_READING = (
    "GitLab: 405 Method Not Allowed is deterministic when merge-train enforcement "
    "is on and the request omits auto_merge=true"
)


@dataclass
class Attempt:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str
    state_before: dict
    state_after: dict
    had_effect: bool
    error: str | None = None

    def as_dict(self) -> dict:
        return {
            "command": self.command,
            "returncode": self.returncode,
            "stdout": self.stdout.strip(),
            "stderr": self.stderr.strip(),
            "state_before": self.state_before.get("state"),
            "state_after": self.state_after.get("state"),
            "merge_commit_sha_before": self.state_before.get("merge_commit_sha"),
            "merge_commit_sha_after": self.state_after.get("merge_commit_sha"),
            "had_effect": self.had_effect,
            "error": self.error,
        }


@dataclass
class Outcome:
    status: str
    detail: str
    attempts: list[Attempt] = field(default_factory=list)
    reading_assumed: str = DETERMINISTIC_READING

    def as_dict(self) -> dict:
        return {
            "status": self.status,
            "detail": self.detail,
            "reading_assumed": self.reading_assumed,
            "attempts": [attempt.as_dict() for attempt in self.attempts],
        }


def read_state(mr: str, project: str, api) -> dict:
    result = api.project_api(project, f"merge_requests/{mr}")
    if result.returncode != 0:
        raise RuntimeError(f"cannot read merge request {mr}: {result.stderr or result.stdout}")
    return json.loads(result.stdout)


def had_effect(after: dict) -> bool:
    """A merge happened only when the MR says `merged` AND carries a merge commit.

    A move to `closed` or `locked` is not a merge: reporting it as one is how a
    refused or abandoned MR would read as landed.
    """
    return after.get("state") == "merged" and bool(after.get("merge_commit_sha"))


def merge(
    mr: str,
    sha: str,
    api,
    project: str = DEFAULT_PROJECT,
    dry_run: bool = False,
) -> Outcome:
    before = read_state(mr, project, api)
    head = (before.get("sha") or "").lower()
    if sha.lower() != head:
        return Outcome(
            status="refused",
            detail=(
                f"the pinned SHA is not this MR's head: asked for {sha}, the MR is at "
                f"{head or '(no sha)'}. Re-freeze and re-review, or merge the reviewed "
                "SHA by hand after checking what moved."
            ),
        )
    if before.get("state") == "merged":
        return Outcome(status="merged", detail="already merged")
    if dry_run:
        return Outcome(
            status="dry-run",
            detail=f"MR {mr} is open at {head}; a merge would be attempted",
        )

    outcome = Outcome(status="refused", detail="no attempt was made")
    for number in (1, 2):
        state_before = read_state(mr, project, api)
        # The head is re-checked before EVERY attempt, not only before the first:
        # a rebase under a frozen candidate is exactly how the reviewed SHA moves.
        if (state_before.get("sha") or "").lower() != sha.lower():
            attempt = Attempt(
                command=[],
                returncode=0,
                stdout="",
                stderr="",
                state_before=state_before,
                state_after=state_before,
                had_effect=False,
                error="the MR's head is no longer the pinned SHA",
            )
            outcome.attempts.append(attempt)
            outcome.detail = (
                f"the MR is no longer at the signed-off SHA: asked for {sha}, it is at "
                f"{state_before.get('sha')}. Nothing was merged; re-freeze and re-review."
            )
            return outcome
        result = api.merge(mr, project, sha)
        state_after = read_state(mr, project, api)
        effect = had_effect(state_after)
        attempt = Attempt(
            command=list(getattr(result, "args", []) or []),
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            state_before=state_before,
            state_after=state_after,
            had_effect=effect,
        )
        outcome.attempts.append(attempt)

        if effect:
            outcome.status = "merged"
            outcome.detail = (
                f"merged on attempt {number}; MR state {state_before.get('state')} -> "
                f"{state_after.get('state')}, merge commit "
                f"{state_after.get('merge_commit_sha')}"
            )
            return outcome

        failed = result.returncode != 0
        if not failed:
            attempt.error = "no server-side effect"
            outcome.status = "refused"
            outcome.detail = (
                "the merge command reported success and the MR never merged: refusing "
                "to report a merge that did not happen"
            )
            return outcome

        text = f"{result.stdout}\n{result.stderr}"
        is_405 = bool(HTTP_405.search(text))
        if is_405 and number == 1:
            attempt.error = "405 with no effect"
            continue
        if is_405 and number == 2:
            attempt.error = "405 recurred"
            outcome.status = "refused"
            outcome.detail = (
                "a 405 recurred on the single retry, so it is the deterministic reading "
                f"and not the flake: {DETERMINISTIC_READING}. The other reading exists "
                f"({FLAKE_READING}) and this wrapper does not bet on it twice. "
                "If a merge train is enforcing here, name auto_merge=true explicitly."
            )
            return outcome
        attempt.error = "merge failed with no effect"
        outcome.status = "refused"
        outcome.detail = (
            f"attempt {number} failed with no server-side effect; refusing to retry a "
            f"real failure. Command said: {(result.stderr or result.stdout).strip()[:400]}"
        )
        return outcome

    outcome.detail = "exhausted the single permitted retry"
    return outcome


class GlabApi:
    """The real calls: `glab api` for state, `glab mr merge` for the merge."""

    def __init__(self, repository: Path | None = None, runner=None):
        self.repository = repository
        # The one seam a test needs: hand in a runner and read the exact command this
        # class builds, instead of intercepting subprocess for the whole process.
        self._run = runner or self._subprocess_run

    def _subprocess_run(self, command: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            command, capture_output=True, text=True, cwd=self.repository, timeout=300
        )

    def project_api(self, project: str, path: str) -> subprocess.CompletedProcess:
        return self._run(["glab", "api", f"projects/{project.replace('/', '%2F')}/{path}"])

    def merge(self, mr: str, project: str, sha: str) -> subprocess.CompletedProcess:
        # The merge carries the signed-off SHA, and NO --auto-merge: a merge train's
        # own auto-merge is not the SHA a human signed off, so it is not this rule.
        return self._run(["glab", "mr", "merge", mr, "--sha", sha, "--yes"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--mr", required=True, help="merge request iid")
    parser.add_argument("--sha", required=True, help="the signed-off candidate SHA")
    parser.add_argument("--project", default=DEFAULT_PROJECT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        outcome = merge(args.mr, args.sha, GlabApi(), args.project, args.dry_run)
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(outcome.as_dict(), indent=2))
    else:
        print(f"{outcome.status}: {outcome.detail}")
        for attempt in outcome.attempts:
            print(
                "  attempt: exit {0}, MR {1} -> {2}, merge commit {3}, effect {4}".format(
                    attempt.returncode,
                    attempt.state_before.get("state"),
                    attempt.state_after.get("state"),
                    attempt.state_after.get("merge_commit_sha"),
                    attempt.had_effect,
                )
            )
    if outcome.status == "refused" and "not this MR's head" in outcome.detail:
        return 4
    return {"merged": 0, "dry-run": 0}.get(outcome.status, 3)


if __name__ == "__main__":
    raise SystemExit(main())
