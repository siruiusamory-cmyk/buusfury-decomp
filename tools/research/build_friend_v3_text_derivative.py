"""Build the consolidated V3 mainline friend derivative from the pre-BOOST foundation.

ONE CUMULATIVE CHAIN, WITHOUT THE SPEEDRUN IMAGE. The base is the pre-BOOST
Tulma-complete foundation `a4c12a95`, which carries every accepted modification except the
artificial level and stats. The BOOST image `acd98c2a` is a separate testing derivative and
is NOT an ancestor of anything this builds; the owner's lineage correction says so, and the
check below is what holds it.

  0. the foundation itself, carried as the base and checked by digest;
  1. the owner-approved text batch: seven biographies in place, the slot 1065 grammar
     repair by append and repoint;
  2. the trailing-pad repair: 32 records whose last units are padding spaces, repaired by
     reducing their handle's decoded length, which moves no container byte.

WHAT IT DELIBERATELY DOES NOT DO. No interior-padding repair, no `Great Soyman`, no
`Kakarot` to `Bandit` and no World Tournament wording: all of those need the handle-format
work and are recorded for the successor engine ticket. `plan_group` is not called here and
must not be wired into a write path.

Usage:
  python build/fv3text001/build_derivative.py --out DIR [--stage-dir DIR]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

BASELINE_SHA = "a4c12a95818cab2781165658d25f2463bc6fe0f87040620a7c89f0034c5b49db"
BOOST_SHA = "acd98c2ac90907ae0d83e78019c19b9b26001a49bc28e8bd436da7be9b4bb48c"
FOUNDATION_SHA = "a4c12a95818cab2781165658d25f2463bc6fe0f87040620a7c89f0034c5b49db"
NAME = "v3-mainline-text-dialogue-pass"

#: WHAT THE LINEAGE IS, AND WHY IT CHANGED. The owner's 2026-10-10 correction separates the
#: distribution image from the speedrun one: the BOOST image `acd98c2a` holds artificial
#: level 200 and maximum STR/POW/END/SPD for the five party records, and must not be an
#: ancestor of a mainline release. Measured, the BOOST differs from the pre-BOOST
#: foundation `a4c12a95` in exactly 25 bytes, every one inside the base-stat table at file
#: 0x6FDA4C, which is the same 25 offsets the boost builder's own manifest declares. So
#: the foundation carries every other accepted modification and nothing of the boost.
BOOST_ONLY_OFFSETS = (
    0x6FDA4C, 0x6FDA52, 0x6FDA53, 0x6FDA54, 0x6FDA55, 0x6FDA5E, 0x6FDA64, 0x6FDA65,
    0x6FDA66, 0x6FDA67, 0x6FDA70, 0x6FDA76, 0x6FDA77, 0x6FDA78, 0x6FDA79, 0x6FDA82,
    0x6FDA88, 0x6FDA89, 0x6FDA8A, 0x6FDA8B, 0x6FDA94, 0x6FDA9A, 0x6FDA9B, 0x6FDA9C,
    0x6FDA9D,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str], cwd: Path = REPO) -> str:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(f"REFUSED: {' '.join(command)}\n{result.stdout}\n{result.stderr}")
    return result.stdout


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--stage-dir", default=str(REPO / "build" / "fv3text001" / "stage"))
    args = parser.parse_args()

    stage = Path(args.stage_dir)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    foundation = stage / "foundation-a4c12a95.gba"
    if sha256(foundation) != FOUNDATION_SHA:
        raise SystemExit("REFUSED: the foundation digest is not the verified one")

    # THE FOUNDATION IS THE BASE, NOT THE BOOST IMAGE. Checking it here is what keeps this
    # builder from silently starting on the speedrun derivative, which carries 25 bytes of
    # artificial stats that must never reach a mainline release.
    boost = stage / "boost-repro.gba"
    if boost.exists():
        boost_bytes, base_bytes = boost.read_bytes(), foundation.read_bytes()
        differing = [offset for offset in range(len(base_bytes))
                     if base_bytes[offset] != boost_bytes[offset]]
        if differing != list(BOOST_ONLY_OFFSETS):
            raise SystemExit(
                "REFUSED: the boost image and the foundation differ somewhere other than "
                f"the base-stat table: {[hex(o) for o in differing if o not in BOOST_ONLY_OFFSETS]}"
            )
        print(f"# lineage check: the boost differs from the foundation in exactly "
              f"{len(differing)} byte(s), all inside the base-stat table")

    baseline = foundation
    got = sha256(baseline)
    print(f"# base {baseline.name} {got} (pre-BOOST; no artificial stats)")
    print(f"# the BOOST image {BOOST_SHA[:16]} is preserved as a separate testing derivative")

    print("STAGE 1 the approved text batch")
    batch = out / "stage2-text-batch.gba"
    run([sys.executable, "tools/research/apply_friend_v3_text_batch.py",
         "--image", str(baseline), "--expect-sha256", BASELINE_SHA,
         "--out", str(batch), "--manifest", str(out / "stage2-text-batch.manifest.json")])
    print(f"  {batch.name} {sha256(batch)}")

    print("STAGE 2 the trailing-pad repair")
    final = out / f"{NAME}.gba"
    captured = run([sys.executable, "-m", "tools.research.trim_dialogue_padding",
                    "--image", str(batch), "--expect-sha256", sha256(batch),
                    "--out", str(final),
                    "--manifest", str(out / f"{NAME}.manifest.json")])
    print("  " + captured.strip().replace("\n", "\n  "))

    # THE POST-CHECK THE FIRST REVIEW ASKED FOR. Pinning the foundation digest keeps BOOST
    # stats out on the way in, but nothing until now proved they were still out on the way
    # out. These 25 bytes are the whole of the BOOST modification, so an equality test
    # against the foundation on the finished image is the cheap closing check.
    boost_offsets = sorted(BOOST_ONLY_OFFSETS)
    foundation_bytes = foundation.read_bytes()
    final_bytes = final.read_bytes()
    differing = [offset for offset in boost_offsets
                 if final_bytes[offset] != foundation_bytes[offset]]
    if differing:
        raise SystemExit("REFUSED: the derivative's base-stat bytes differ from the "
                         f"pre-BOOST foundation at {[hex(o) for o in differing]}")
    print(f"# post-check: all {len(boost_offsets)} base-stat bytes still equal the "
          "pre-BOOST foundation, so no BOOST-only value reached this image")

    changelog = {
        "name": NAME,
        "foundation": {"file": foundation.name, "sha256": FOUNDATION_SHA,
                       "bytes": len(foundation_bytes),
                       "role": "base of this derivative: the pre-BOOST Tulma-complete image"},
        "boost_artifact_preserved_not_an_ancestor": {
            "file": "v3-playtest-boost.gba", "sha256": BOOST_SHA,
            "why_excluded": "carries artificial level 200 and maximum STR/POW/END/SPD for "
                            "the five party records, which must never reach a mainline "
                            "release; the owner's lineage correction separates the two",
            "measured_isolation": "the BOOST differs from the foundation in exactly 25 "
                                  "bytes, all inside the base-stat table at 0x6FDA4C, and "
                                  "the derivative's bytes there equal the foundation's",
        },
        "output": {"file": final.name, "sha256": sha256(final),
                   "bytes": final.stat().st_size},
        "growth_bytes": final.stat().st_size - len(foundation_bytes),
        "stages": [
            {"stage": 0, "what": "pre-BOOST foundation, the base; no stage regenerates it",
             "file": foundation.name, "sha256": FOUNDATION_SHA},
            {"stage": 1, "what": "approved text batch: seven biographies in place, slot 1065 "
                                 "grammar repair by append and repoint",
             "file": batch.name, "sha256": sha256(batch)},
            {"stage": 2, "what": "trailing-pad repair: 32 records, 70 pad units, handle "
                                 "length only, no container byte moved",
             "file": final.name, "sha256": sha256(final)},
        ],
        "included": [
            "every modification carried by the pre-BOOST foundation a4c12a95, which is the "
            "Tulma-complete chain through MR !165",
            "seven owner-approved biographies (slots 1059, 1069, 1187, 1189, 1191, 1193, 1195)",
            "owner-approved slot 1065 grammar repair",
            "trailing-pad repair for 32 dialogue records",
        ],
        "boost_modifications_absent": [
            "level 200 on the five party records",
            "maximum STR/POW/END/SPD on the five party records",
        ],
        "not_included_deferred_to_engine_ticket": [
            "interior dialogue padding (321 runs, 653 units) in the dialogue containers",
            "the single spoken Great Soy Man to Great Soyman rename",
            "Kakarot to Bandit in the punctuated occurrences",
            "the owner-authored World Tournament lines, which need the same container work",
        ],
        "excluded_on_purpose": [
            "tools/webfoot/dialogue_repack.py::plan_group is not called by any stage here",
        ],
        "save_compatibility": {
            "battery_save": "compatible: no stage touches the save layout, the game code or "
                            "the base-stat table, and the baseline's own save compatibility "
                            "is unchanged",
            "savestate": "NOT compatible with states written on acd98c2a: stage 2 moves one "
                         "string and repoints one table word, so a state whose EWRAM holds "
                         "the decoded text may show the old wording. Start from a battery "
                         "save, or expect stale text from a restored state.",
        },
    }
    (out / "changelog.json").write_text(json.dumps(changelog, indent=2) + "\n",
                                        encoding="utf-8")
    print(f"\nFINAL {final.name} {changelog['output']['sha256']} "
          f"{changelog['output']['bytes']} bytes (growth {changelog['growth_bytes']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
