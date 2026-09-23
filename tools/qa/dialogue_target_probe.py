"""QA probe: find a REAL dialogue record the Inspector can actually author.

The visual-direction capture needs one Inspector state where dialogue authoring
is live (the golden journey's own surface), rather than the "not available for
this record yet" state a random atlas match produces. This walks the real
semantic text corpus of the canonical image and reports which records the public
dialogue-authoring API can resolve, so the capture uses a genuine target.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.webfoot import atlas as atlas_sdk  # noqa: E402
from tools.webfoot import dialogue as dialogue_sdk  # noqa: E402
from tools.webfoot.cli import load_catalog  # noqa: E402
from tools.webfoot.workbench.session import Session  # noqa: E402


def main() -> int:
    rom = _ROOT / "roms" / "Dragon Ball Z - Buu's Fury (U).gba"
    catalog = load_catalog(None)
    session = Session()
    session.open_rom(rom, catalog)
    profile = session.profile
    from tools.webfoot import dialogue as dlg

    registered = getattr(dlg, "AUTHORED_DIALOGUE_TARGETS", {})
    print("registered targets:", len(registered))
    wanted = {f"0x{t.packed_handle:08X}" for t in registered.values()}

    probes = ("Kakarot", "Goku", "Saiyan", "Hello", "Fight", "Dragon Ball", "Buu", "the", "a")
    found = 0
    for phrase in probes:
        result = atlas_sdk.search_text(
            session.atlas, phrase, session.decoded_text, rom_image=session.rom_image
        )
        for decoded in result["decoded"]:
            identity = decoded.get("identity") or {}
            packed = identity.get("packed_handle")
            if packed not in wanted:
                continue
            target = dialogue_sdk.resolve_dialogue_target(decoded, profile)
            if target is None:
                print(f"  packed {packed} matched but did not resolve (profile gate?)")
                continue
            original = dialogue_sdk.get_dialogue_original(
                session.rom_image, profile, target
            )
            print(f"  RESOLVED {target.name!r} handle {packed} from {phrase!r}")
            print(f"    original: {original!r}")
            found += 1
            if found >= 3:
                return 0
    print("resolved targets:", found)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
