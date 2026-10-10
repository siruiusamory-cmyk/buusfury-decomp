"""Reproduce release 2.1 from release 2 in one run.

The release was built in two stages: `apply_friend_v3_text_slot.py` placed the biography, then
`apply_friend_v3_registration_rows.py` placed the two dialogue rows and moved the biography
string. Reproducing it by hand means running two tools in the right order, which is the sort of
step a later reader gets wrong, so the chain lives here as one command.

Usage:
  python tools/research/build_friend_v3_release21.py --image IN.gba --expect-sha256 <hex> \
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

from tools.research.apply_friend_v3_registration_rows import (  # noqa: E402
    apply as apply_rows, plan as plan_rows)
from tools.research.apply_friend_v3_text_slot import apply as apply_slot  # noqa: E402
from tools.research.friend_v3_text_approvals import APPROVED_TEXT_SLOTS  # noqa: E402
from tools.webfoot.write import WriteError, ensure_not_source_alias  # noqa: E402


class Release21Error(ValueError):
    """The chain refused rather than writing a byte it could not verify."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    source = Path(args.image)
    image = source.read_bytes()
    got = sha256_bytes(image)
    if got != args.expect_sha256.lower():
        raise Release21Error(
            f"REFUSED: {source} is {got}, expected {args.expect_sha256.lower()}")

    edit = APPROVED_TEXT_SLOTS[0]
    stage_one, first = apply_slot(image, edit.slot, edit.old, edit.new)
    bio, rows = plan_rows(stage_one)
    stage_two, second = apply_rows(stage_one, bio, rows)
    report = {
        "input": str(source), "input_sha256": got, "input_bytes": len(image),
        "stages": [
            {"tool": "apply_friend_v3_text_slot",
             "slot": first["slot"], "method": first["method"],
             "new_offset": first["new_offset"], "old_span_bytes": first["old_span_bytes"]},
            {"tool": "apply_friend_v3_registration_rows",
             "container_file_offset": second["container_file_offset"],
             "container_declared_size": second["container_declared_size"],
             "carried_prefix_bytes": second["carried_prefix_bytes"],
             "string_file_offset": second["string_file_offset"],
             "site_changes": second["site_changes"]},
        ],
        "output_bytes": len(stage_two),
    }
    target = Path(args.out)
    try:
        ensure_not_source_alias(source, target)
    except WriteError as error:
        raise Release21Error(f"REFUSED: {error}") from error
    staged = target.with_name(target.name + ".staged")
    staged.write_bytes(stage_two)
    if staged.read_bytes() != stage_two:
        raise Release21Error("REFUSED: the staged write does not match the plan")
    staged.replace(target)
    report["output"] = str(target)
    report["output_sha256"] = sha256_bytes(stage_two)
    Path(args.manifest).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"# stage 1: slot {edit.slot} {first['method']} at file 0x{first['new_offset']:X}")
    print(f"# stage 2: container at file 0x{second['container_file_offset']:X} "
          f"({second['container_declared_size']} bytes, "
          f"{second['carried_prefix_bytes']} carried), string at "
          f"0x{second['string_file_offset']:X}")
    print(f"# wrote {target} {len(stage_two)} bytes sha256 {report['output_sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
