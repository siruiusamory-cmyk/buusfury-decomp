"""ROM-ATLAS-001 graphics extents: `graphics_extents.jsonl`.

Ported from the earlier exploratory script `gen_graphics_extents.py`, recovered
separately from the other five producers.

Records where the existing walker already goes: `graphics.load_actor_sprites`
(graphics.py:612) is called and one row is written per distinct container file
offset. No new parsing — `file_offset` is `Graphic.file_offset` (graphics.py:122)
and `size` is `Graphic.packed_size` (graphics.py:128), which comes from
`Container.packed_end` (webfoot_lz.py:99).

Changes from the original: the hardcoded repository root, ROM path and output
path (gen_graphics_extents.py:15-25) became parameters, and the `os.chdir` the
original used to resolve `config/roms.yaml` became an explicit `config_path`.
The before/after ROM SHA assertions (gen_graphics_extents.py:28,127) are kept.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from .. import graphics
from ..binary import GBA_ROM_BASE as GBA_BASE
from ..profile import RomProfileCatalog, VerificationStatus
from ..rom import identify_rom
from ._io import write_jsonl

#: `GBA_BASE` is `binary.GBA_ROM_BASE`, the one owner of address-window
#: semantics, rather than a second literal of it.
#:
#: The image identity this pass requires is NOT restated here: it is read from
#: the profile the catalog matches, which is the one authority for it (CQA-15).
#: A second literal would be free to drift from the catalog the pass itself
#: loads, so the check below compares the bytes against the matched profile.


def build(rom_path: Path, out_dir: Path, config_path: Path) -> Path:
    """Write `graphics_extents.jsonl` into `out_dir`. Opens the ROM read-only."""
    rom_path = Path(rom_path)
    image = rom_path.read_bytes()
    before = hashlib.sha256(image).hexdigest()

    catalog = RomProfileCatalog.load(Path(config_path))
    identification = identify_rom(rom_path, catalog)
    match = identification.profile_match
    if match.status is not VerificationStatus.VERIFIED or match.profile is None:
        raise ValueError(
            f"{rom_path} is not an exactly verified profile image: {match.reason}"
        )
    expected = match.profile.identity
    assert before == expected.sha256, (
        f"ROM identity mismatch before: {before} is not {expected.describe()}"
    )
    sprites = graphics.load_actor_sprites(image, identification)

    rows = []
    for graphic in sprites.graphics():
        first = graphic.consumers[0]
        notes = []
        if len(graphic.consumers) > 1:
            notes.append(f"referenced by {len(graphic.consumers)} frames")
        if len(graphic.characters) > 1:
            notes.append(f"used by {len(graphic.characters)} characters")
        rows.append({
            "file_offset": graphic.file_offset,
            "size": graphic.packed_size,
            "gba_address": f"0x{GBA_BASE + graphic.file_offset:08X}",
            "kind": "compressed_stream",
            "identity": f"graphics.container.{graphic.identity.index:04d}",
            "confidence": "CONFIRMED",
            "decoded_size": len(graphic.pixels),
            "reachable_from": (
                f"character:{first.character_index:03d}"
                f"/animation:{first.animation_index:03d}"
                f"/frame:{first.frame_index:03d}"
                f"/direction:{first.direction}"
                f"@frame_offset:0x{first.frame_offset:X}"
            ),
            "source": "tools/webfoot/graphics.py:612",
            "evidence": (
                "reached by load_actor_sprites walk (graphics.py:612); packed extent is "
                "Graphic.packed_size (graphics.py:128) from Container.packed_end "
                "(webfoot_lz.py:99) measured by running the decoder; decoded length "
                "equals the width*height the referring piece record independently declares"
            ),
            "notes": "; ".join(notes),
        })

    rows.sort(key=lambda r: r["file_offset"])
    assert len({r["file_offset"] for r in rows}) == len(rows), "duplicate offsets"

    # Overlap detection on the sorted extents.
    for earlier, later in zip(rows, rows[1:]):
        if earlier["file_offset"] + earlier["size"] > later["file_offset"]:
            for this, other in ((earlier, later), (later, earlier)):
                tag = (f"OVERLAP: {other['identity']} at 0x{other['file_offset']:X}"
                       f"..0x{other['file_offset'] + other['size']:X}")
                this["notes"] = f"{this['notes']}; {tag}" if this["notes"] else tag

    path = Path(out_dir) / "graphics_extents.jsonl"
    write_jsonl(path, rows)

    after = hashlib.sha256(rom_path.read_bytes()).hexdigest()
    assert after == expected.sha256, (
        f"ROM changed during the run: {after} is not {expected.describe()}"
    )
    return path
