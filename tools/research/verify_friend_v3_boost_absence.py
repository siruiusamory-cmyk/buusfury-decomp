"""Re-run the BOOST-absence proof on a World Tournament release.

The speedrun BOOST image is not an ancestor of this release, and the previous ticket proved it
by re-checking the 25 base-stat bytes the BOOST builder declares against the pre-BOOST
foundation after its own final write. This does the same for the World Tournament release,
from the BOOST builder's own manifest rather than from a copied list: every offset the BOOST
manifest changed must hold the FOUNDATION's byte in the release, and the BOOST image's byte
there must differ (which is what makes the check non-vacuous).

Usage:
  python tools/research/verify_friend_v3_boost_absence.py \
      --image OUT.gba --foundation FOUNDATION.gba --boost BOOST.gba --boost-manifest M.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def sha256_of(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def boost_offsets(manifest: dict) -> list[int]:
    """Every file offset the BOOST manifest declares, in order, with no duplicates."""
    offsets: list[int] = []
    for record in manifest["records"]:
        for field in record["fields"]:
            offsets.append(int(field["offset"]))
    seen: set[int] = set()
    unique = [offset for offset in offsets if not (offset in seen or seen.add(offset))]
    if len(unique) != int(manifest["changed_bytes"]):
        raise SystemExit(
            f"the BOOST manifest declares {manifest['changed_bytes']} changed bytes but "
            f"names {len(unique)} distinct offsets; refusing to guess")
    return unique


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--foundation", required=True)
    parser.add_argument("--boost", required=True)
    parser.add_argument("--boost-manifest", required=True)
    args = parser.parse_args()

    image = Path(args.image).read_bytes()
    foundation = Path(args.foundation).read_bytes()
    boost = Path(args.boost).read_bytes()
    manifest = json.loads(Path(args.boost_manifest).read_text(encoding="utf-8"))
    offsets = boost_offsets(manifest)

    problems: list[str] = []
    differs = 0
    for offset in offsets:
        if offset >= len(image) or offset >= len(foundation) or offset >= len(boost):
            problems.append(f"0x{offset:X} lies past an image's end")
            continue
        if image[offset] != foundation[offset]:
            problems.append(
                f"0x{offset:X}: release holds 0x{image[offset]:02X}, foundation "
                f"0x{foundation[offset]:02X}")
        if boost[offset] != foundation[offset]:
            differs += 1
    print(f"release  {args.image} {len(image)} bytes sha256 {sha256_of(image)}")
    print(f"foundation {args.foundation} {len(foundation)} bytes sha256 "
          f"{sha256_of(foundation)}")
    print(f"boost    {args.boost} {len(boost)} bytes sha256 {sha256_of(boost)}")
    print(f"{len(offsets)} BOOST-declared offsets; the BOOST image differs from the "
          f"foundation at {differs} of them")
    print(f"{len(offsets) - len(problems)} of {len(offsets)} offsets hold the foundation's "
          f"byte in the release")
    for problem in problems:
        print(f"FAIL {problem}")
    if differs != len(offsets):
        print("FAIL the check is vacuous: the BOOST image does not differ from the foundation "
              "at every declared offset")
        return 1
    print("BOOST-ABSENCE PASS" if not problems else "BOOST-ABSENCE FAIL")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
