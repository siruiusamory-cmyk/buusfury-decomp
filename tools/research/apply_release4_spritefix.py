"""Restore the 28 canonical bytes that the shipped release 3.1 wrote over sprite data.

THE DEFECT THIS REPAIRS. Release 3.1's rename builder found record words by shape
alone and rewrote every hit. Nine of those words lie outside the event-resource
pool, in sprite graphics and in unclassified data, so the release silently
corrupted them. Found by the coordinator review of RELEASE4-SPACES-001 (B1), whose
engine now refuses to write outside the pool; the corruption itself is already in
the shipped chain, and Release 4A and the Release 4 image both carry it.

WHAT IS RESTORED. Nine four-byte words, taken byte for byte from the canonical
image. Six sit inside compressed character-sprite animation frames, two in
uncompressed 8bpp tile data, one in unclassified low-entropy data with no consumer
identified. The frame identities below are the review's measured mapping
(container offsets re-checked here by decoding each container).

WHAT IS PROVEN BEFORE ANYTHING IS PUBLISHED. Every frame container named here is
decoded from the built bytes and compared with the canonical image's own decode;
the two tile regions and the unclassified word are compared byte for byte. A
disagreement refuses the build. The write itself goes through
`tools/webfoot/write.py` `emit_image`, so the destination guards, the staged
publish and the provenance manifest are the project's, not this file's.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.webfoot.formats import webfoot_lz  # noqa: E402
from tools.webfoot.write import ByteChange, WritePlan, emit_image  # noqa: E402

#: The sprite files carry one of these profile ids; the value is provenance only.
BASE_PROFILE_ID = "friend-v3-derived"

#: offset, container (None when the word is not inside one), what it is, and how it
#: is proven. A `frame` is proven by decoding its container; a `tiles` site by
#: comparing `tile_window` bytes at `tile_window_start`; a `data` site by comparing
#: the four bytes themselves.
SITES: tuple[dict, ...] = (
    {"offset": 0x316A18, "container": None, "kind": "data",
     "owner": "data@0x316A18",
     "what": "unclassified low-entropy data, consumer unknown"},
    {"offset": 0x40E178, "container": 0x40E0DC, "kind": "frame",
     "owner": "graphics.container.0584:character-033-animation-005-frame-000",
     "what": "compressed frame, character 033"},
    {"offset": 0x4567CC, "container": 0x4565CC, "kind": "frame",
     "owner": "graphics.container.1016:character-042-animation-003-frame-003",
     "what": "compressed frame, character 042"},
    {"offset": 0x46C29C, "container": 0x46C1D8, "kind": "frame",
     "owner": "graphics.container.1119:character-042-animation-007-frame-002",
     "what": "compressed frame, character 042"},
    {"offset": 0x4D99A8, "container": 0x4D995C, "kind": "frame",
     "owner": "graphics.container.2162:character-099-animation-002-frame-003",
     "what": "compressed frame, character 099"},
    {"offset": 0x545A04, "container": 0x5459C4, "kind": "frame",
     "owner": "graphics.container.3614:character-114-animation-015-frame-003",
     "what": "compressed frame, character 114"},
    {"offset": 0x5C6FB4, "container": 0x5C6DF0, "kind": "frame",
     "owner": "graphics.container.4909:character-123-animation-002-frame-003",
     "what": "compressed frame, character 123"},
    {"offset": 0x725474, "container": None, "kind": "tiles",
     "owner": "graphics.tiles@0x7253DC+0x98:oam-0x72A5F0",
     "tile_window_start": 0x7253DC + 0x98, "tile_window": 512,
     "what": "uncompressed 8bpp tile block, 32x16 frame"},
    {"offset": 0x726074, "container": None, "kind": "tiles",
     "owner": "graphics.tiles@0x725FDC+0x98:oam-0x72A620",
     "tile_window_start": 0x725FDC + 0x98, "tile_window": 512,
     "what": "uncompressed 8bpp tile block, duplicate of the same frame"},
)

#: How many bytes differ between the canonical image and the release-31 values.
EXPECTED_DIFFERING_BYTES = 28


class SpriteFixError(ValueError):
    """The restore refused rather than writing a byte it could not verify."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def prove(built: bytes, canonical: bytes) -> list[dict]:
    """Decode and compare everything each site claims, in memory, before writing."""
    rows = []
    for site in SITES:
        offset = site["offset"]
        restored = built[offset:offset + 4]
        expected = canonical[offset:offset + 4]
        if restored != expected:
            raise SpriteFixError(
                f"REFUSED: {site['owner']} at {offset:#x} reads {restored.hex()}, "
                f"canonical is {expected.hex()}")
        row = {"owner": site["owner"], "offset": f"0x{offset:08X}", "kind": site["kind"],
               "canonical_word": expected.hex()}
        if site["kind"] == "frame":
            container = site["container"]
            want = webfoot_lz.unpack(canonical, container)
            got = webfoot_lz.unpack(built, container)
            if bytes(got.data) != bytes(want.data):
                differing = sum(1 for a, b in zip(got.data, want.data) if a != b)
                raise SpriteFixError(
                    f"REFUSED: {site['owner']} container {container:#x} decodes with "
                    f"{differing} byte(s) different from canonical")
            row["container"] = f"0x{container:08X}"
            row["decoded_bytes"] = len(got.data)
            row["decoded_matches_canonical"] = True
        elif site["kind"] == "tiles":
            start = site["tile_window_start"]
            size = site["tile_window"]
            if built[start:start + size] != canonical[start:start + size]:
                raise SpriteFixError(
                    f"REFUSED: {site['owner']} tile window {start:#x}+{size} does not "
                    "match canonical")
            row["tile_window"] = f"0x{start:08X}+{size}"
            row["tile_window_matches_canonical"] = True
        rows.append(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--canonical", required=True)
    parser.add_argument("--canonical-sha256", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    source = Path(args.image)
    image = source.read_bytes()
    digest = sha256_bytes(image)
    if digest != args.expect_sha256.lower():
        raise SpriteFixError(f"REFUSED: {source} is {digest}, expected "
                             f"{args.expect_sha256.lower()}")
    canonical = Path(args.canonical).read_bytes()
    # The restore's authority is the canonical image, so its identity is pinned
    # here and recorded in every change's reason. A reference image that is not the
    # one this ticket measured would restore the wrong bytes, and the 28-count check
    # alone would not catch a different build of the same game.
    canonical_digest = sha256_bytes(canonical)
    if canonical_digest != args.canonical_sha256.lower():
        raise SpriteFixError(f"REFUSED: {args.canonical} is {canonical_digest}, expected "
                             f"{args.canonical_sha256.lower()}")

    changes = []
    already = 0
    for site in SITES:
        offset = site["offset"]
        old = image[offset:offset + 4]
        new = canonical[offset:offset + 4]
        if old == new:
            already += 1
            continue
        changes.append(ByteChange(
            offset=offset, old=old, new=new, owner=site["owner"],
            reason=f"restore the canonical bytes release 3.1 wrote over {site['what']}; "
                   f"canonical image sha256 {canonical_digest}"))
    if already == len(SITES):
        raise SpriteFixError("REFUSED: every site already holds the canonical bytes")
    site_difference = sum(
        1 for site in SITES for index in range(4)
        if image[site["offset"] + index:site["offset"] + index + 1]
        != canonical[site["offset"] + index:site["offset"] + index + 1])
    if site_difference != EXPECTED_DIFFERING_BYTES:
        raise SpriteFixError(
            f"REFUSED: the nine sites differ from canonical at {site_difference} byte(s), "
            f"expected the {EXPECTED_DIFFERING_BYTES} this ticket names")

    plan = WritePlan(base_profile_id=BASE_PROFILE_ID, base_sha256=digest,
                     base_size=len(image), changes=tuple(changes))
    built = bytearray(image)
    for change in plan.effective_changes:
        if built[change.offset:change.offset + change.size] != change.old:
            raise SpriteFixError(
                f"REFUSED: {change.owner} at {change.offset:#x} does not hold the bytes "
                "this change replaces")
        built[change.offset:change.offset + change.size] = change.new
    rows = prove(bytes(built), canonical)

    manifest = emit_image(source, Path(args.out), plan, manifest_path=Path(args.manifest))
    print(f"  sites restored: {len(plan.effective_changes)} of {len(SITES)} "
          f"({already} already canonical)")
    print(f"  differing bytes against canonical at the nine sites: {site_difference}")
    for row in rows:
        print(f"  {row['offset']} {row['kind']:6} {row['owner']}")
    print(f"# wrote {args.out} {manifest.output_size} bytes sha256 {manifest.output_sha256}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
