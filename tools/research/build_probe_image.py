"""Build a probe image that applies the OAM bank-select patch, for runtime testing of the detour.

Why it exists: the question "does appended code reached from a pulled-in jump actually run in this engine"
is answered only in the emulator, and it needs an image with the patch applied and the stub layout printed.
`--body none` writes a zero-byte stub body, which is the control that separates "the detour works" from
"the stub body works".

Invoke:
  python -m tools.research.build_probe_image --image BASE.gba --out OUT.gba --body stub
  python -m tools.research.build_probe_image --image BASE.gba --out OUT.gba --body none

Then launch it with tools/runtime/start_toolkit031_session.ps1 and a frame callback probe, and read the
frame log: a run whose frames advance past a few hundred has proved the detour.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools.research import oam_bank_patch as patch  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--body", choices=["stub", "none"], default="stub")
    parser.add_argument("--padding", type=int, default=0)
    args = parser.parse_args()

    base = args.image.read_bytes()
    image = bytearray(base)
    body = b"" if args.body == "none" else None
    stub_address, replaced = patch.patch(image, body=body, padding=args.padding)
    args.out.write_bytes(bytes(image))
    print(f"base  {args.image} {len(base)} byte(s) sha256 {hashlib.sha256(base).hexdigest()}")
    print(f"out   {args.out} {len(image)} byte(s) sha256 {hashlib.sha256(bytes(image)).hexdigest()}")
    print(f"stub  0x{stub_address + patch.ROM_BASE:08X} (file 0x{stub_address:06X}), body {args.body}")
    print(f"replaced at 0x{patch.BLOCK_SITE:08X}: {replaced.hex(' ')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
