"""The Tulma and Bulma line rewrite, as a preset over the reusable dialogue engine.

WHAT THIS IS NOW. The engine lives in `tools/webfoot/dialogue_edit.py` and the invocable front
end in `tools/webfoot/character_swap.py`. This module names this ticket's two lines so the
record's measurements stay reproducible through one command, and it states each record's span
explicitly, which the engine cross-checks against the wording.

WHY THE SPANS ARE STATED HERE. Wording locates a record but does not prove who speaks it: a
record is reached by a scene that names its handle, and the speaker is that scene's actor. So
this preset states the record it means, and `speaker` below is a label for the report rather
than evidence. The engine refuses when the wording matches no record or more than one, and
refuses when a stated span disagrees with the wording's own single match.

WHY THE TWO RECORDS ARE LAID OUT TOGETHER. Records are back-to-back and a record's length lives
only in its handle, so a replacement longer than its own span cannot grow in place. Bulma's
record and Tulma's are contiguous (112 + 138 = 250 bytes) and the replacements need 220, so the
pair is re-laid out inside that combined region and both handles are rewritten. Nothing else in
the container moves, which keeps every other record's absolute offset valid.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# The repository root, so this preset runs as a script as well as a module.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.webfoot import character_swap as cs  # noqa: E402
from tools.webfoot.dialogue_edit import (CONTAINER_HEADER, ROM_BASE, SPACE,  # noqa: E402
                                         TABLE_LITERAL, DialogueEditError, DialogueRewrite,
                                         LineEdit, context, container_file_offset, find_record,
                                         rewrite_dialogue, sha256, stored_payload)
from tools.webfoot.dialogue_edit import apply as _apply  # noqa: E402
from tools.webfoot.dialogue_edit import plan as _plan  # noqa: E402
from tools.webfoot.dialogue_edit import verify as _verify  # noqa: E402

TICKET = "FRIEND-V3-TULMA-GRAPHICS-001 dialogue expansion (owner-authorized)"
SELECTOR = 2

#: The two slots, each with the wording it held and the wording the owner asked for. Each
#: record's span is stated, and the engine refuses if it disagrees with the wording.
TARGETS = (
    LineEdit(speaker="bulma",
             old_text="Isn't this wonderful? Our family is back together again!",
             new_text="Look at how mad Tulma is! Do you think I went too far this time?",
             decoded_start=60182, decoded_length=112),
    LineEdit(speaker="tulma",
             old_text=("It's great that \ue000mc\ue001 is back. "
                       "Everyone seems so happy to be together."),
             new_text="That bitch! She knew I was going to wear this!",
             decoded_start=60294, decoded_length=138),
)
TULMA_REWRITE = DialogueRewrite(selector=SELECTOR, lines=TARGETS)

#: The engine's error type, under the name this ticket's tests and record already use.
TulmaDialogueError = DialogueEditError


def plan(image: bytes) -> dict:
    """This ticket's rewrite, planned against an image."""
    return _plan(image, TULMA_REWRITE)


def apply(image: bytes, planned: dict) -> bytes:
    return _apply(image, planned)


def verify(base: bytes, out: bytes, planned: dict) -> dict:
    return _verify(base, out, planned)


def run(base_path: Path, expect_sha256: str, out_path: Path, report_path: Path) -> dict:
    """Reproduce this ticket's dialogue candidate from the base and the expected digest."""
    def transform(image: bytes) -> tuple[bytes, dict]:
        out, report = rewrite_dialogue(image, TULMA_REWRITE)
        report.update({"ticket": TICKET, "base_path": str(base_path),
                       "base_sha256": sha256(image), "base_size": len(image),
                       "output_path": str(out_path), "output_sha256": sha256(out),
                       "output_size": len(out)})
        return out, report

    return cs.guarded_apply(base_path, expect_sha256, out_path, report_path, transform,
                            error=DialogueEditError)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", required=True, type=Path)
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        report = run(args.base, args.expect_sha256, args.out, args.report)
    except (DialogueEditError, cs.WriteError) as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    for handle in report["handles"]:
        key = f"{handle['new_start']}:{handle['new_length']}"
        print(f"  {handle['speaker']:6s} {handle['was']} -> ({key}) reads "
              f"{report['verification']['read_back'][key]!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
