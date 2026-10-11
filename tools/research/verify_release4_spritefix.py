"""Verify the release-4 sprite restore from the two images alone.

INDEPENDENT BY CONSTRUCTION. This file imports neither the builder nor the text
engine: it reads the base image, the restored image and the canonical image with
`tools.webfoot.formats.webfoot_lz` and compares bytes.

WHAT IT PROVES.

1. The restored image differs from the base image at exactly the declared sites,
   and nowhere else. Any other changed byte fails.
2. At every site the restored bytes equal the canonical image's own bytes.
3. Every compressed frame container named by a site decodes from the restored
   image and its decoded bytes equal the canonical image's decode of the same
   container. The base image's copy of that container is measured too, so the
   report shows the defect that was repaired (a failed decode, or a count of
   differing decoded bytes).
4. Both uncompressed tile windows equal canonical over the whole window (512
   bytes), and the OAM descriptor each site names really points at that block.
5. Every other byte of the image is identical to the base.
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

ROM_BASE = 0x08000000

#: offset, container, OAM descriptor that names the block (tiles only), window.
SITES = (
    (0x316A18, None, None, 4),
    (0x40E178, 0x40E0DC, None, 4),
    (0x4567CC, 0x4565CC, None, 4),
    (0x46C29C, 0x46C1D8, None, 4),
    (0x4D99A8, 0x4D995C, None, 4),
    (0x545A04, 0x5459C4, None, 4),
    (0x5C6FB4, 0x5C6DF0, None, 4),
    (0x725474, None, (0x72A5F0, 0x7253DC), 512),
    (0x726074, None, (0x72A620, 0x725FDC), 512),
)
EXPECTED_DIFFERING_BYTES = 28


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def decode_or_note(image: bytes, container: int) -> tuple[bytes | None, str]:
    try:
        return bytes(webfoot_lz.unpack(image, container).data), ""
    except webfoot_lz.ContainerError as error:
        return None, str(error)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--canonical", required=True)
    parser.add_argument("--canonical-sha256", required=True)
    args = parser.parse_args()

    base = Path(args.base).read_bytes()
    built = Path(args.out).read_bytes()
    canonical = Path(args.canonical).read_bytes()
    problems: list[str] = []
    notes: list[str] = []

    digest = sha256_bytes(built)
    if digest != args.expect_sha256.lower():
        problems.append(f"the restored image is {digest}, expected {args.expect_sha256.lower()}")
    # The canonical image is the authority every restored word is taken from, so it
    # is identified before it is used.
    canonical_digest = sha256_bytes(canonical)
    if canonical_digest != args.canonical_sha256.lower():
        problems.append(f"the canonical image is {canonical_digest}, expected "
                        f"{args.canonical_sha256.lower()}")

    digest = sha256_bytes(built)
    if digest != args.expect_sha256.lower():
        problems.append(f"the restored image is {digest}, expected {args.expect_sha256.lower()}")
    if len(base) != len(built):
        problems.append(f"base and restored sizes differ: {len(base)} vs {len(built)}")
    if len(canonical) < 0x800000:
        problems.append(f"the canonical image is only {len(canonical)} bytes; the sites this "
                        "ticket names live below 8 MiB")
    for offset, _container, _oam, _window in SITES:
        if offset + 4 > len(canonical):
            problems.append(f"site {offset:#x} lies beyond the canonical image")

    # 1 and 2. exactly the declared bytes changed, and they now equal canonical
    declared = {offset + index for offset, _c, _o, _w in SITES for index in range(4)}
    changed = {index for index in range(len(base)) if base[index] != built[index]}
    stray = sorted(changed - declared)
    missed = sorted({index for index in declared if base[index] == built[index]})
    notes.append(f"changed bytes: {len(changed)}, of the declared {len(declared)} "
                 f"site bytes")
    if stray:
        problems.append(f"{len(stray)} byte(s) changed outside the declared sites, "
                        f"first at {stray[0]:#x}")
    if len(changed) != EXPECTED_DIFFERING_BYTES:
        problems.append(f"{len(changed)} byte(s) changed, expected "
                        f"{EXPECTED_DIFFERING_BYTES}")
    # A site byte that the base already matched is not a failure, only a note.
    already = [f"{index:#x}" for index in missed]
    notes.append(f"declared bytes that already matched canonical in the base: "
                 f"{len(already)} {already[:4]}")

    for offset, container, oam, window in SITES:
        if built[offset:offset + 4] != canonical[offset:offset + 4]:
            problems.append(f"{offset:#x} reads {built[offset:offset + 4].hex()}, canonical is "
                            f"{canonical[offset:offset + 4].hex()}")

        # 3. compressed frames: the restored container must decode and match canonical
        if container is not None:
            want, want_why = decode_or_note(canonical, container)
            got, got_why = decode_or_note(built, container)
            before, before_why = decode_or_note(base, container)
            if want_why or want is None:
                problems.append(f"canonical container {container:#x} does not decode: {want_why}")
            elif got_why or got is None:
                problems.append(f"restored container {container:#x} does not decode: {got_why}")
            elif got != want:
                differing = sum(1 for a, b in zip(got, want) if a != b)
                problems.append(f"restored container {container:#x} decodes with {differing} "
                                "byte(s) different from canonical")
            if before_why:
                notes.append(f"container {container:#x}: the base did not decode ({before_why})")
            elif before is not None and want is not None and before != want:
                differing = sum(1 for a, b in zip(before, want) if a != b)
                notes.append(f"container {container:#x}: the base decoded with {differing} "
                             "byte(s) different from canonical")
            else:
                notes.append(f"container {container:#x}: the base already matched canonical")

        # 4. uncompressed tiles: the whole window and the OAM descriptor
        if oam is not None:
            descriptor_offset, block = oam
            pointer = int.from_bytes(canonical[descriptor_offset:descriptor_offset + 4], "little")
            if pointer != ROM_BASE + block:
                problems.append(f"OAM descriptor {descriptor_offset:#x} names {pointer:#010x}, "
                                f"not the block {ROM_BASE + block:#010x}")
            if built[offset:offset + window] != canonical[offset:offset + window]:
                problems.append(f"tile window at {offset:#x}+{window} does not match canonical")

    # 5. everything else identical to the base
    notes.append("every byte outside the declared sites is identical to the base"
                 if not stray else "see the stray-byte problem above")

    for note in notes:
        print(f"  {note}")
    if problems:
        print(f"VERIFY FAIL: {len(problems)} problem(s)")
        for problem in problems[:20]:
            print(f"  {problem}")
        return 1
    print(f"VERIFY PASS: {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
