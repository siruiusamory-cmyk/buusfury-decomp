"""Run a token dictionary's glyph and width rules against the real font.

WHY THIS EXISTS. Two of the design's entry rules need the image, not just the text:
every glyph in an expansion must have a glyph record in the code map, and the
expansion's composed advance must fit the narrowest line the fitter is handed. The
production codec takes both as seams (`has_glyph`, `check_widths`) precisely so it can
stay a pure data module, which means that until something passes the real font in,
those two rules are statements about the code rather than about this game. This tool
passes the real font in.

IT ALSO PRINTS THE SUBSTITUTION BREAKDOWN, because the rename splice's growth, shrink
and unchanged counts had no tool behind them either: they came from a scratch script,
and a number with no tool is a number a reviewer has to take on trust.

The font is read exactly as the renderer reads it, through
`tools/research/dialogue_wrap_sim.py`, which asserts the canonical digest itself.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tools.research.dialogue_wrap_sim import load_font
from tools.webfoot.token_dictionary import (LINE_WIDTH_FLOOR, TokenDictionary,
                                            TokenDictionaryError, build_blob,
                                            check_widths, expansion_advance)

CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", required=True, help="the canonical image")
    parser.add_argument("--tokens", nargs="*", required=True)
    parser.add_argument("--map", help="a rename map, to print its substitution breakdown")
    args = parser.parse_args()

    font = load_font(Path(args.rom))
    dictionary = TokenDictionary(tuple(args.tokens))

    print(f"font: glyph records present for the expansions' glyphs")
    for entry in dictionary.entries():
        expansion = dictionary.expansions[entry.index]
        advances = [(glyph, font.glyph_advance(glyph)) for glyph in entry.glyphs]
        total = expansion_advance(expansion, font.glyph_advance)
        missing = [f"{glyph:#06x}" for glyph in entry.glyphs if not font.has_glyph(glyph)]
        print(f"  U+{entry.unit:04X}  {expansion!r}  "
              f"{' + '.join(f'{glyph:#06x}:{width}' for glyph, width in advances)} = "
              f"{total} px  missing glyph records: {missing or 'none'}")

    # The refusals, run against the real font. Either one raising is the tool's
    # answer, so both are exercised before the blob is built.
    check_widths(dictionary, font.glyph_advance)
    blob = build_blob(dictionary, has_glyph=font.has_glyph)
    print(f"glyph records : every glyph has one (build_blob accepted the dictionary)")
    print(f"width bound   : every expansion is at or under {LINE_WIDTH_FLOOR} px "
          f"(check_widths accepted)")
    print(f"blob          : {len(blob)} bytes for {dictionary.count} entries")

    # NEGATIVE CONTROLS. On this image every code that passes the codec's other rules
    # has a glyph record, so `has_glyph` rejects nothing above and the check would look
    # the same if the seam were disconnected. These show both seams can refuse, which
    # is what makes the acceptances above mean something. A control that does NOT
    # refuse is a failure of this tool, so it exits non-zero.
    failures = []
    denied = dictionary.entries()[0].glyphs[0]
    try:
        build_blob(dictionary, has_glyph=lambda code: code != denied)
        failures.append("build_blob accepted a dictionary whose glyph has no record")
    except TokenDictionaryError:
        print(f"negative control: build_blob refuses when {denied:#06x} has no record")
    try:
        check_widths(dictionary, lambda code: LINE_WIDTH_FLOOR)
        failures.append("check_widths accepted an over-wide expansion")
    except TokenDictionaryError:
        print(f"negative control: check_widths refuses a {LINE_WIDTH_FLOOR} px glyph")
    for failure in failures:
        print(f"FAILED: {failure}")
    return 1 if failures else 0

    if args.map:
        import json
        from tools.research.splice_dialogue_tokens import substitution_table
        rows = json.loads(Path(args.map).read_text(encoding="utf-8"))
        table = substitution_table(rows)
        growth = sum(1 for old, new in table.items() if len(new) > len(old))
        shrink = sum(1 for old, new in table.items() if len(new) < len(old))
        unchanged = sum(1 for old, new in table.items() if len(new) == len(old))
        print(f"substitutions : {len(table)} distinct, {growth} grow, {shrink} shrink, "
              f"{unchanged} unchanged")
        unpaid = [f"{old!r} -> {new!r}" for old, new in table.items()
                  if len(new) > len(old)
                  and not _payable(new, len(old), dictionary)]
        print(f"unpayable     : {unpaid or 'none'}")
    return 0


def _payable(new_side: str, target: int, dictionary: TokenDictionary) -> bool:
    from tools.webfoot.token_dictionary import TokenDictionaryError, encode_to_length
    try:
        return len(encode_to_length(new_side, dictionary, target)) == target
    except TokenDictionaryError:
        return False


if __name__ == "__main__":
    sys.exit(main())
