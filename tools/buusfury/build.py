"""Assemble a ROM from the region map, with explicit per-region provenance.

The one thing this module refuses to do is report "byte-identical" without
saying which bytes were actually rebuilt. Every region carries a provenance
label, and the build report records it:

    rebuilt-asset   regenerated from a source asset with grit / JCALG1
    rebuilt-ads     regenerated from source with ARM Developer Suite 1.2
    passthrough     copied out of the baserom, exactly as the reference build
                    does for its INCBIN ranges

A ROM assembled with -AllowPassthrough will hash to the canonical SHA-1. That
proves the REGION MAP is right. It does NOT prove the passthrough bytes were
rebuilt, and the report says so.

Strict mode (the default) refuses to passthrough anything that the reference
project itself rebuilds, and fails closed with the exact commands that would be
needed - see docs/DECOMP_BASELINE.md for why those commands cannot be run here.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
from pathlib import Path

from . import assets as _assets
from . import identity as _identity
from . import regions as _regions
from . import toolchain as _toolchain

PROVENANCE_PASSTHROUGH = "passthrough"
PROVENANCE_ASSET = "rebuilt-asset"
PROVENANCE_ADS = "rebuilt-ads"


class BuildError(RuntimeError):
    """Raised when the build cannot proceed."""


class BuildBlocker(BuildError):
    """Raised when a stage is blocked by a missing prerequisite.

    Carries structured context so the report can name the exact commands, the
    exact licence problem and the exact missing sources rather than a shrug.
    """

    def __init__(self, code: str, summary: str, details: list[str]) -> None:
        self.code = code
        self.summary = summary
        self.details = details
        body = "\n".join(f"  - {d}" for d in details)
        super().__init__(f"[{code}] {summary}\n{body}")


#: The reference build's own ARM Developer Suite commands, per region.
#:
#: Recorded here so that a blocked build can state precisely what it would have
#: run. These are the exact invocations from 2genkidev/buusfury build.bat.
ADS_COMMANDS: dict[str, list[str]] = {
    "crt0": [
        "armasm asm/buu.s -o build/buu.o",
        "# asm/buu.s line 10 does INCLUDE crt0.s, which INCLUDEs rom_header.s",
    ],
    "gbaram_text": ["armasm asm/GBARam.s -o build/GBARam.o"],
    "afterlibs_thunk": [
        "armasm asm/buu.s -o build/buu.o",
        "# AREA AfterLibs: LDR r12,|FUN_08046aec_PTR| / BX r12 / DCD 0x08046AED",
    ],
    "color_transforms": [
        "armcpp -c src/color_transforms.cpp -o build/color_transforms.o",
        "# note: NO optimisation flag is passed",
    ],
    "strings": ["armcpp -c src/strings.cpp -o build/strings.o"],
}

#: The linker/convert steps, run once for the whole image.
ADS_LINK_COMMANDS: list[str] = [
    "armasm asm/ewram.s -o build/ewram.o",
    "armasm asm/iwram.s -o build/iwram.o",
    "armasm asm/rest_of_the_game.s -o build/rest_of_the_game.o",
    (
        "armlink build/GBARam.o build/color_transforms.o build/strings.o "
        "build/buu.o build/rest_of_the_game.o build/ewram.o build/iwram.o "
        "-noremove -scatter scatter.ld -o build/buu.axf"
    ),
    "fromelf build/buu.axf -bin -o build/output",
]


@dataclasses.dataclass
class RegionOutcome:
    region_id: str
    start: int
    end: int
    length: int
    cls: str
    provenance: str
    detail: str = ""

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class BuildReport:
    baserom: str
    baserom_sha1: str
    output: str | None
    output_sha1: str
    expected_sha1: str
    byte_identical: bool
    strict: bool
    region_outcomes: list[RegionOutcome]
    rebuilt_bytes: int
    passthrough_bytes: int
    blockers: list[dict]

    def as_dict(self) -> dict:
        data = dataclasses.asdict(self)
        data["region_outcomes"] = [o.as_dict() for o in self.region_outcomes]
        return data

    def summary_lines(self) -> list[str]:
        lines: list[str] = []
        lines.append(f"baserom          : {self.baserom}")
        lines.append(f"baserom SHA-1    : {self.baserom_sha1}")
        lines.append(f"output           : {self.output}")
        lines.append(f"output SHA-1     : {self.output_sha1 or '(not produced)'}")
        lines.append(f"expected SHA-1   : {self.expected_sha1}")
        verdict = "PASS" if self.byte_identical else "FAIL"
        lines.append(f"byte-identical   : {verdict}")
        total = self.rebuilt_bytes + self.passthrough_bytes
        share = (100.0 * self.rebuilt_bytes / total) if total else 0.0
        lines.append(
            f"provenance       : {self.rebuilt_bytes:,} bytes rebuilt "
            f"({share:.3f}%), {self.passthrough_bytes:,} bytes passthrough"
        )
        for blocker in self.blockers:
            lines.append(f"blocker [{blocker['code']}]: {blocker['summary']}")
        return lines


def region_bytes_from_baserom(data: bytes, region: _regions.Region) -> bytes:
    return data[region.start : region.end]


def assemble(
    baserom: str | Path,
    output: str | Path | None = None,
    allow_passthrough: bool = False,
    reference_dir: Path | None = None,
    ads12_root: str | Path | None = None,
    workdir: Path | None = None,
    config: dict | None = None,
) -> BuildReport:
    """Assemble the ROM from the region map.

    Raises BuildBlocker in strict mode when a region requires the ADS toolchain,
    or when an asset region cannot be rebuilt and passthrough is not allowed.
    """
    cfg = config if config is not None else _identity.load_canonical()
    identity = _identity.verify(baserom, cfg)

    region_list = _regions.load_regions()
    rom_size = _regions.load_rom_size()
    _regions.validate_tiling(region_list, rom_size)

    data = identity.path.read_bytes()
    outcomes: list[RegionOutcome] = []
    chunks: list[bytes] = []
    blockers: list[dict] = []
    rebuilt = 0
    passed = 0

    ref = reference_dir or _assets.default_reference_dir()
    work = workdir or (_identity.REPO_ROOT / "build" / "assets")
    grit = _toolchain.find_grit()
    compress = _assets.default_compress_exe()

    ads_regions = [r for r in region_list if r.cls == _regions.CLASS_ADS]
    ads_status = {s.id: s for s in _toolchain.doctor(ads12_root, probe_versions=False)}

    # ---- ADS regions ----------------------------------------------------
    if ads_regions:
        details: list[str] = []
        details.append(
            "Requirement 1 - a licensed ARM Developer Suite 1.2 installation."
        )
        for tool_id in ("armasm", "armcpp", "armlink", "fromelf"):
            status = ads_status.get(tool_id)
            state = f"found at {status.path}" if status and status.available else "NOT FOUND"
            details.append(f"  {tool_id}: {state}")
        details.append(
            "Requirement 2 - independently authored sources for those regions."
        )
        details.append(
            "  No ADS input source for these regions exists in this repository, and"
        )
        details.append(
            "  none may be imported from the only public copy: 2genkidev/buusfury"
        )
        details.append(
            "  carries no licence (GitHub reports \"license\": null), so its source"
        )
        details.append("  is all-rights-reserved and cannot be copied here.")
        details.append("Commands the reference build runs for these regions:")
        for tool_cmds in ADS_COMMANDS.values():
            details.extend(f"  {c}" for c in tool_cmds)
        details.append("Link and convert steps:")
        details.extend(f"  {c}" for c in ADS_LINK_COMMANDS)

        blockers.append(
            {
                "code": "ADS12_UNAVAILABLE",
                "summary": (
                    f"{len(ads_regions)} region(s), "
                    f"{sum(r.length for r in ads_regions):,} bytes, can only be "
                    "rebuilt with ARM Developer Suite 1.2, which is not installed "
                    "and whose source inputs are not available to this repository."
                ),
                "regions": [r.id for r in ads_regions],
                "details": details,
            }
        )

        if not allow_passthrough:
            raise BuildBlocker(
                "ADS12_UNAVAILABLE",
                blockers[0]["summary"],
                details,
            )

    # ---- build every region --------------------------------------------
    for region in region_list:
        if region.cls == _regions.CLASS_INCBIN:
            chunk = region_bytes_from_baserom(data, region)
            outcomes.append(
                RegionOutcome(
                    region.id, region.start, region.end, region.length, region.cls,
                    PROVENANCE_PASSTHROUGH,
                    "opaque range; the reference build INCBINs this same range",
                )
            )
            passed += len(chunk)
            chunks.append(chunk)
            continue

        if region.cls == _regions.CLASS_ADS:
            chunk = region_bytes_from_baserom(data, region)
            outcomes.append(
                RegionOutcome(
                    region.id, region.start, region.end, region.length, region.cls,
                    PROVENANCE_PASSTHROUGH,
                    "PASSTHROUGH: strict build not possible - see blocker ADS12_UNAVAILABLE",
                )
            )
            passed += len(chunk)
            chunks.append(chunk)
            continue

        # class == asset
        spec = _assets.SPECS_BY_REGION.get(region.id)
        if spec is None:
            if not allow_passthrough:
                raise BuildBlocker(
                    "ASSET_SPEC_MISSING",
                    f"region {region.id} is class=asset but has no rebuild spec",
                    [
                        "Add an AssetSpec for it in tools/buusfury/assets.py, or",
                        "reclassify the region in config/regions.json.",
                    ],
                )
            chunk = region_bytes_from_baserom(data, region)
            outcomes.append(
                RegionOutcome(
                    region.id, region.start, region.end, region.length, region.cls,
                    PROVENANCE_PASSTHROUGH, "no rebuild spec",
                )
            )
            passed += len(chunk)
            chunks.append(chunk)
            continue

        expected = region_bytes_from_baserom(data, region)
        rebuilt_bytes: bytes | None = None
        failure = ""
        if ref is None:
            failure = (
                "no reference checkout; run scripts/fetch-reference.ps1 or set "
                "BUUSFURY_REFERENCE"
            )
        else:
            try:
                rebuilt_bytes = _assets.rebuild_one(
                    region, spec, ref, work, grit, compress
                )
            except _assets.AssetError as exc:
                failure = str(exc)

        if rebuilt_bytes is not None and rebuilt_bytes == expected:
            outcomes.append(
                RegionOutcome(
                    region.id, region.start, region.end, region.length, region.cls,
                    PROVENANCE_ASSET, f"rebuilt from {spec.source}; byte-identical",
                )
            )
            rebuilt += len(rebuilt_bytes)
            chunks.append(rebuilt_bytes)
            continue

        if rebuilt_bytes is not None:
            failure = (
                f"rebuilt {len(rebuilt_bytes)} bytes from {spec.source} but they are "
                f"NOT byte-identical to the canonical ROM"
            )

        if not allow_passthrough:
            raise BuildBlocker(
                "ASSET_REBUILD_FAILED",
                f"region {region.id} could not be rebuilt byte-identically",
                [failure, "Refusing to fall back to a passthrough silently."],
            )

        outcomes.append(
            RegionOutcome(
                region.id, region.start, region.end, region.length, region.cls,
                PROVENANCE_PASSTHROUGH, f"PASSTHROUGH: {failure}",
            )
        )
        passed += len(expected)
        chunks.append(expected)

    image = b"".join(chunks)
    if len(image) != rom_size:
        raise BuildError(
            f"assembled {len(image)} bytes but the ROM is {rom_size} bytes"
        )

    output_sha1 = hashlib.sha1(image).hexdigest()
    expected_sha1 = cfg["hashes"]["sha1"].lower()

    out_path: Path | None = None
    if output is not None:
        out_path = Path(output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(image)

    return BuildReport(
        baserom=str(identity.path),
        baserom_sha1=identity.sha1,
        output=str(out_path) if out_path else None,
        output_sha1=output_sha1,
        expected_sha1=expected_sha1,
        byte_identical=(output_sha1 == expected_sha1),
        strict=not allow_passthrough,
        region_outcomes=outcomes,
        rebuilt_bytes=rebuilt,
        passthrough_bytes=passed,
        blockers=blockers,
    )


def write_report(report: BuildReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # newline="\n" keeps the report byte-stable across platforms.
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(report.as_dict(), indent=2) + "\n")


def _which(name: str) -> Path | None:
    import shutil

    found = shutil.which(name)
    return Path(found) if found else None
