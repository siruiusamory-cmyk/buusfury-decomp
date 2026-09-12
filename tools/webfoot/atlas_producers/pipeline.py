"""ROM-ATLAS-001 canonical regeneration: every artifact, one deterministic order.

This is the only chain claimed to be reproducible. Run it against an EMPTY output
directory; no stage reads an artifact it did not itself produce in this run, and
none reads its own previous output.

The order below is fixed by real data dependencies, not by chasing the historical
run's timestamps:

1. `seed`               — reads documents only, writes `seed_knowledge.jsonl`.
2. `graphics_extents`   — needs only the ROM and the profile catalog.
3. `scan`               — needs the seed rows (for `in_claimed_region`); runs all
                          six passes.
4. `code_functions.build_wave2` — needs the seed rows.
5. `code_functions.build_wave4` — needs wave 2's function set for its delta rule.
6. `regions`            — needs both traversals' reach records.
7. `code_coverage_wave4.json` — needs both traversals.

`atlas_build.build_atlas` then assembles the result; `run` does that last unless
`assemble=False`.

Steps 2 and 3 are independent of each other, as are 1 and 2 apart from step 3's
seed dependency; the order here is the documented canonical one, chosen so each
stage's inputs exist when it starts and nothing else.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from . import code_functions, graphics_extents, regions, scan, seed

#: Relative to the repository root, for the default config catalog.
DEFAULT_CONFIG = Path("config") / "roms.yaml"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def run(rom_path: Path, out_dir: Path, *, config_path: Path | None = None,
        assemble: bool = True, atlas_path: Path | None = None) -> dict:
    """Regenerate every atlas input from `rom_path` into `out_dir`.

    Returns a summary dict. The ROM is opened read-only and its SHA-256 is
    checked before and after the whole run.
    """
    rom_path = Path(rom_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    config_path = Path(config_path) if config_path else repo_root() / DEFAULT_CONFIG

    sha_before = hashlib.sha256(rom_path.read_bytes()).hexdigest()
    written: list[str] = []

    written.append(seed.build(out_dir).name)
    written.append(graphics_extents.build(rom_path, out_dir, config_path).name)

    scan_summary = scan.build(rom_path, out_dir)
    written.extend(f"{name}.jsonl" for name in
                   ("scan_text", "scan_pointers", "scan_pointer_tables",
                    "scan_entropy", "scan_compression", "scan_code_shape"))

    wave2_path, wave2 = code_functions.build_wave2(rom_path, out_dir)
    written.append(wave2_path.name)
    wave4_path, wave4 = code_functions.build_wave4(rom_path, out_dir, wave2)
    written.append(wave4_path.name)
    written.append(regions.build(out_dir, wave2, wave4).name)
    written.append(code_functions.write_coverage(out_dir, rom_path, wave2, wave4).name)

    sha_after = hashlib.sha256(rom_path.read_bytes()).hexdigest()
    if sha_after != sha_before:
        raise RuntimeError("the canonical ROM changed during the run")

    summary = {
        "rom": str(rom_path), "rom_sha256": sha_after,
        "out_dir": str(out_dir), "artifacts": sorted(written),
        "functions_wave2": len(wave2.functions),
        "functions_wave4_delta": len(set(wave4.functions) - set(wave2.functions)),
        "scan": scan_summary,
    }

    if assemble:
        from ..atlas_build import build_atlas, coverage_statistics, write_atlas

        report = build_atlas(out_dir)
        target = Path(atlas_path) if atlas_path else out_dir / "atlas.jsonl"
        write_atlas(report, target)
        summary["atlas"] = str(target)
        summary["atlas_sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
        summary["conflicts"] = len(report.conflicts)
        summary["coverage"] = coverage_statistics(report.atlas)
    return summary
