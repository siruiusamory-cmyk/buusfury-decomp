"""Reproduce release 3 from release 2.1 in one command.

The release was built in three stages, each with its own tool and its own verifier:

  1. `apply_friend_v3_boss_retune.py`      - Hercule's and Olibu's stat records.
  2. `apply_friend_v3_behaviour_profile.py` - the measured aggressive profile on both of them.
  3. `apply_friend_v3_dialogue_text.py`     - the Great Soyman spacing repair and the ten lines
                                              that read Bandit.

Every value comes from `friend_v3_text_approvals.py`, so the chain cannot drift from the approved
wording, and each stage's expected input digest is checked before it runs. The final image's digest
is asserted against `APPROVED_RELEASES`, which is what makes "reproduce it twice" a check rather
than a hope.

The stages are invoked as commands rather than imported, because each one is a digest-gated,
byte-exact command line of its own and a failure in any of them must stop the chain. A stage that
refuses is reported with its own message and nothing is written.

Usage:
  python tools/research/build_friend_v3_release3.py --image IN.gba --expect-sha256 <hex> \
      --out OUT.gba --manifest OUT.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.research import apply_friend_v3_behaviour_profile as profile_stage  # noqa: E402
from tools.research import apply_friend_v3_boss_retune as retune_stage  # noqa: E402
from tools.research import apply_friend_v3_dialogue_text as wording_stage  # noqa: E402
from tools.research.friend_v3_text_approvals import (  # noqa: E402
    APPROVED_BOSS_PROFILES, APPROVED_BOSS_RETUNES, APPROVED_DIALOGUE_TEXT_EDITS, APPROVED_RELEASES)
from tools.webfoot.write import WriteError, ensure_not_source_alias  # noqa: E402

RELEASE = next(release for release in APPROVED_RELEASES if release.name == "release-3")


class Release3Error(ValueError):
    """The chain refused rather than writing a byte it could not verify."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def run_stage(module, arguments: list[str]) -> None:
    """Run one stage's command line in this process.

    In-process rather than through a child process on purpose: a second interpreter is a process
    start the tree's launch-coverage test has to classify, and there is nothing here that needs a
    fresh interpreter. The stage's own argparse still parses its arguments and its own refusals
    still raise, so a stage that disagrees with the chain stops the build.
    """
    saved = sys.argv
    sys.argv = [module.__name__, *arguments]
    try:
        module.main()
    except SystemExit as exit_code:
        if exit_code.code not in (0, None):
            raise Release3Error(f"stage {module.__name__} refused with {exit_code.code}") from None
    finally:
        sys.argv = saved


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--workdir", default=None,
                        help="where the intermediate images go; defaults beside the output")
    args = parser.parse_args()

    source = Path(args.image)
    image = source.read_bytes()
    got = sha256_bytes(image)
    if got != args.expect_sha256.lower():
        raise Release3Error(f"REFUSED: {source} is {got}, expected {args.expect_sha256.lower()}")
    if got != RELEASE.base_sha256:
        raise Release3Error(
            f"REFUSED: release 3 is cut from {RELEASE.base_sha256}, not {got}")

    target = Path(args.out)
    try:
        ensure_not_source_alias(source, target)
    except WriteError as error:
        raise Release3Error(f"REFUSED: {error}") from error
    workdir = Path(args.workdir) if args.workdir else target.parent
    workdir.mkdir(parents=True, exist_ok=True)
    stem = target.stem

    document: dict = {"release": RELEASE.name, "base": str(source), "base_sha256": got,
                      "stages": [], "output_bytes": None}

    # Stage 1: the two encounters. The tool applies the approved records itself, so the chain
    # cannot disagree with the authority about which encounters move.
    retune_out = workdir / f"{stem}.1-retune.gba"
    arguments = ["--image", str(source), "--expect-sha256", got,
                 "--out", str(retune_out), "--manifest", str(workdir / f"{stem}.1-retune.json")]
    run_stage(retune_stage, arguments)
    document["stages"].append({"name": "boss-retune", "output": str(retune_out),
                               "sha256": sha256_bytes(retune_out.read_bytes())})

    # Stage 2: the profile, on both records.
    profile_out = workdir / f"{stem}.2-profile.gba"
    profile = APPROVED_BOSS_PROFILES[0]
    arguments = ["--image", str(retune_out), "--expect-sha256",
                 sha256_bytes(retune_out.read_bytes()),
                 "--out", str(profile_out),
                 "--manifest", str(workdir / f"{stem}.2-profile.json"),
                 "--gate-radius", str(profile.gate_radius_squared),
                 "--attack-radius", str(profile.attack_radius_squared),
                 "--attack-percent", str(profile.attack_percent)]
    if profile.attack_first:
        arguments.append("--attack-first")
    if profile.attack_action_row is not None:
        arguments += ["--attack-action", str(profile.attack_action_row)]
    for selector in profile.selectors:
        arguments += ["--record", str(selector)]
    run_stage(profile_stage, arguments)
    document["stages"].append({"name": "behaviour-profile", "output": str(profile_out),
                               "sha256": sha256_bytes(profile_out.read_bytes())})

    # Stage 3: the wording.
    arguments = ["--image", str(profile_out), "--expect-sha256",
                 sha256_bytes(profile_out.read_bytes()),
                 "--out", str(target), "--manifest", str(workdir / f"{stem}.3-wording.json")]
    for edit in APPROVED_DIALOGUE_TEXT_EDITS:
        arguments += ["--edit", f"{edit.selector}:{edit.start}:{edit.length}:{edit.old}:{edit.new}"]
    run_stage(wording_stage, arguments)

    final = target.read_bytes()
    digest = sha256_bytes(final)
    document["stages"].append({"name": "dialogue-wording", "output": str(target),
                               "sha256": digest})
    document["output"] = str(target)
    document["output_sha256"] = digest
    document["output_bytes"] = len(final)
    document["expected_sha256"] = RELEASE.output_sha256
    document["intermediates"] = {"retune": document["stages"][0]["sha256"],
                                 "profile": document["stages"][1]["sha256"]}
    Path(args.manifest).write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")

    for stage in document["stages"]:
        print(f"  {stage['name']:>18}: {stage['sha256']}")
    if digest != RELEASE.output_sha256:
        raise Release3Error(
            f"REFUSED: the chain produced {digest}, and release 3 is "
            f"{RELEASE.output_sha256}. A byte moved somewhere in the three stages.")
    if len(final) != RELEASE.output_bytes:
        raise Release3Error(f"REFUSED: {len(final)} bytes, release 3 is {RELEASE.output_bytes}")
    print(f"# {target} {len(final)} bytes sha256 {digest} matches the frozen release identity")
    return 0


if __name__ == "__main__":
    sys.exit(main())
