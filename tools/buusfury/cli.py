"""Command-line entry point: `python -m buusfury <command>`.

Exit codes
----------
0   the requested check passed
1   the requested check failed, or a stage is blocked
2   usage error / unexpected exception
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import assets as _assets
from . import build as _build
from . import identity as _identity
from . import regions as _regions
from . import toolchain as _toolchain

EXIT_OK = 0
EXIT_FAIL = 1
EXIT_USAGE = 2


def _resolve_rom(args) -> Path:
    return _identity.resolve_baserom(getattr(args, "rom", None))


# --------------------------------------------------------------------------
# verify
# --------------------------------------------------------------------------
def cmd_verify(args) -> int:
    cfg = _identity.load_canonical()
    try:
        rom = _resolve_rom(args)
    except _identity.RomNotFoundError as exc:
        print(f"FAIL: {exc}")
        return EXIT_FAIL

    try:
        found = _identity.verify(rom, cfg)
    except _identity.IdentityError as exc:
        print(str(exc))
        print()
        _print_expected(cfg)
        return EXIT_FAIL

    print("ROM identity: PASS")
    print(f"  path    : {found.path}")
    print(f"  size    : {found.size} bytes")
    print(f"  sha1    : {found.sha1}")
    print(f"  sha256  : {found.sha256}")
    print(f"  crc32   : {found.crc32}")
    if found.header is not None:
        h = found.header
        print(
            f"  header  : title={h.title!r} game_code={h.game_code!r} "
            f"maker={h.maker_code!r} checksum=0x{h.stored_header_checksum:02X} (valid)"
        )
    return EXIT_OK


def _print_expected(cfg: dict) -> None:
    print("Expected canonical identity:")
    print(f"  profile : {cfg['profile_id']}")
    print(f"  size    : {cfg['size_bytes']} bytes")
    for key in ("sha1", "sha256", "md5", "crc32"):
        print(f"  {key:<7} : {cfg['hashes'][key]}")


# --------------------------------------------------------------------------
# map
# --------------------------------------------------------------------------
def cmd_map(args) -> int:
    region_list = _regions.load_regions()
    rom_size = _regions.load_rom_size()
    try:
        _regions.validate_tiling(region_list, rom_size)
    except _regions.RegionMapError as exc:
        print(f"REGION MAP: FAIL\n{exc}")
        return EXIT_FAIL

    totals = _regions.class_totals(region_list)
    print(f"REGION MAP: PASS ({len(region_list)} regions tile 0x000000-0x{rom_size:06X})")
    print()
    print(f"{'class':<8} {'bytes':>12} {'share':>9}  regions")
    for cls in _regions.VALID_CLASSES:
        members = _regions.regions_by_class(region_list, cls)
        share = 100.0 * totals[cls] / rom_size
        print(f"{cls:<8} {totals[cls]:>12,} {share:>8.3f}%  {len(members)}")
    print(f"{'total':<8} {sum(totals.values()):>12,} {100.0:>8.3f}%  {len(region_list)}")

    if args.write:
        target = Path(args.write)
        target.parent.mkdir(parents=True, exist_ok=True)
        # newline="\n" is load-bearing: Python's text mode translates "\n" to
        # os.linesep on Windows, which would make the generated document differ
        # from its committed form on every regeneration.
        with target.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(_regions.render_markdown(region_list, rom_size))
        print(f"\nwrote {target}")
    return EXIT_OK


# --------------------------------------------------------------------------
# doctor
# --------------------------------------------------------------------------
def cmd_doctor(args) -> int:
    statuses = _toolchain.doctor(args.ads12_root, probe_versions=not args.no_probe)
    root = _toolchain.ads_root(args.ads12_root)

    if args.json:
        print(
            json.dumps(
                {
                    "ads12_root": str(root) if root else None,
                    "tools": [s.as_dict() for s in statuses],
                },
                indent=2,
            )
        )
    else:
        print(f"ADS12_ROOT: {root if root else '(unset)'}")
        print()
        print(f"{'tool':<10} {'family':<8} {'status':<9} path / version")
        for status in statuses:
            state = "available" if status.available else "MISSING"
            where = str(status.path) if status.path else "-"
            version = f"  [{status.version}]" if status.version else ""
            print(f"{status.id:<10} {status.family:<8} {state:<9} {where}{version}")

    blocking = [s for s in statuses if not s.available and s.blocks_full_reproduction]
    if blocking:
        print()
        print("Available, but full source reproduction is blocked by:")
        for status in blocking:
            print(f"  - {status.id}: {status.purpose}")
    return EXIT_OK


# --------------------------------------------------------------------------
# assets
# --------------------------------------------------------------------------
def cmd_assets(args) -> int:
    try:
        rom = _resolve_rom(args)
        identity = _identity.verify(rom)
    except (_identity.IdentityError, _identity.RomNotFoundError) as exc:
        print(f"FAIL: {exc}")
        return EXIT_FAIL

    region_list = _regions.load_regions()
    results = _assets.verify_assets(
        identity.path,
        region_list,
        reference_dir=(
            Path(args.reference) if args.reference else None
        ),
        workdir=Path(args.workdir) if args.workdir else None,
    )

    if args.json:
        print(json.dumps([r.as_dict() for r in results], indent=2))
        return EXIT_OK if all(r.ok for r in results) else EXIT_FAIL

    print(f"{'region':<24} {'result':<10} {'bytes':>8}  detail")
    ok = 0
    for result in results:
        state = "IDENTICAL" if result.ok else "FAIL"
        ok += int(result.ok)
        print(
            f"{result.region_id:<24} {state:<10} {result.rebuilt_length:>8}  "
            f"{result.detail}"
        )
    print()
    print(f"{ok}/{len(results)} asset regions reproduced byte-identically")
    return EXIT_OK if ok == len(results) else EXIT_FAIL


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------
def cmd_build(args) -> int:
    output = args.output or str(_identity.REPO_ROOT / "build" / "buusfury.gba")
    report_path = Path(args.report or (_identity.REPO_ROOT / "build" / "build-report.json"))
    try:
        report = _build.assemble(
            _resolve_rom(args),
            output=output,
            allow_passthrough=args.allow_passthrough,
            reference_dir=Path(args.reference) if args.reference else None,
            ads12_root=args.ads12_root,
        )
    except _build.BuildBlocker as exc:
        print(f"BUILD: BLOCKED [{exc.code}]")
        print(exc.summary)
        print()
        for line in exc.details:
            print(line)
        print()
        print(
            "Re-run with --allow-passthrough to assemble a byte-identical image whose\n"
            "build report labels exactly which bytes were NOT rebuilt."
        )
        return EXIT_FAIL
    except (_build.BuildError, _identity.IdentityError, _regions.RegionMapError) as exc:
        print(f"BUILD: FAIL\n{exc}")
        return EXIT_FAIL

    for line in report.summary_lines():
        print(line)
    _build.write_report(report, report_path)
    print(f"report           : {report_path}")

    print()
    print("per-region provenance:")
    print(f"  {'region':<24} {'class':<8} {'bytes':>10}  provenance")
    for outcome in report.region_outcomes:
        print(
            f"  {outcome.region_id:<24} {outcome.cls:<8} {outcome.length:>10,}  "
            f"{outcome.provenance}"
        )

    return EXIT_OK if report.byte_identical else EXIT_FAIL


# --------------------------------------------------------------------------
# status  (the one-command summary)
# --------------------------------------------------------------------------
def cmd_status(args) -> int:
    cfg = _identity.load_canonical()
    failures: list[str] = []

    print("=" * 72)
    print("Buu's Fury decompilation baseline - status")
    print("=" * 72)

    # 1. baserom identity
    print("\n[1/4] canonical baserom identity")
    try:
        rom = _resolve_rom(args)
        found = _identity.verify(rom, cfg)
        print(f"      PASS  {found.sha1}  ({found.path})")
    except (_identity.IdentityError, _identity.RomNotFoundError) as exc:
        print(f"      FAIL  {exc}")
        failures.append("baserom identity")
        rom = None

    # 2. region map
    print("\n[2/4] region map tiles the ROM exactly")
    try:
        region_list = _regions.load_regions()
        rom_size = _regions.load_rom_size()
        _regions.validate_tiling(region_list, rom_size)
        totals = _regions.class_totals(region_list)
        print(
            f"      PASS  {len(region_list)} regions; "
            f"incbin {totals['incbin']:,} / asset {totals['asset']:,} / "
            f"ads {totals['ads']:,}"
        )
    except _regions.RegionMapError as exc:
        print(f"      FAIL  {exc}")
        failures.append("region map")
        region_list = []
        totals = {}

    # 3. asset reproduction
    print("\n[3/4] asset regions reproduced byte-identically")
    if rom is not None and region_list:
        results = _assets.verify_assets(
            found.path,
            region_list,
            reference_dir=Path(args.reference) if args.reference else None,
        )
        good = sum(1 for r in results if r.ok)
        if good == len(results):
            total = sum(r.expected_length for r in results)
            print(f"      PASS  {good}/{len(results)} regions, {total:,} bytes identical")
        else:
            print(f"      FAIL  {good}/{len(results)} regions identical")
            for result in results:
                if not result.ok:
                    print(f"            {result.region_id}: {result.detail}")
            failures.append("asset reproduction")
    else:
        print("      SKIP  no verified baserom / region map")
        failures.append("asset reproduction")

    # 4. full source reproduction
    print("\n[4/4] full source reproduction (ARM Developer Suite 1.2)")
    if region_list:
        ads_regions = _regions.regions_by_class(region_list, _regions.CLASS_ADS)
        statuses = {s.id: s for s in _toolchain.doctor(args.ads12_root, probe_versions=False)}
        missing = [
            t for t in ("armasm", "armcpp", "armlink", "fromelf")
            if not statuses.get(t) or not statuses[t].available
        ]
        ads_bytes = sum(r.length for r in ads_regions)
        if missing:
            print(
                f"      BLOCKED  {ads_bytes:,} bytes in {len(ads_regions)} region(s) "
                f"need ADS 1.2; missing: {', '.join(missing)}"
            )
        else:
            print(f"      ADS tools present; {ads_bytes:,} bytes still need sources")
        # NOT a failure: a documented blocker is the expected baseline outcome.
    else:
        print("      SKIP")

    print("\n" + "=" * 72)
    if failures:
        print(f"BASELINE: FAIL ({', '.join(failures)})")
        return EXIT_FAIL
    print("BASELINE: PASS (achievable gates); full reproduction blocked on ADS 1.2,")
    print("          documented in docs/DECOMP_BASELINE.md and reported above.")
    print("=" * 72)
    return EXIT_OK


# --------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="buusfury",
        description="Buu's Fury decompilation baseline harness.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def add_rom(p):
        p.add_argument(
            "--rom",
            default=None,
            help="path to the baserom (default: $BUUSFURY_ROM, ./baserom.gba)",
        )

    p = sub.add_parser("verify", help="verify a ROM against the canonical identity")
    add_rom(p)
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("map", help="validate the region map and report coverage")
    p.add_argument("--write", default=None, help="write the markdown map to this path")
    p.set_defaults(func=cmd_map)

    p = sub.add_parser("doctor", help="report toolchain availability")
    p.add_argument("--ads12-root", default=None)
    p.add_argument("--json", action="store_true")
    p.add_argument("--no-probe", action="store_true", help="skip version probing")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser("assets", help="rebuild asset regions and compare to the ROM")
    add_rom(p)
    p.add_argument("--reference", default=None, help="reference checkout root")
    p.add_argument("--workdir", default=None)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_assets)

    p = sub.add_parser("build", help="assemble a ROM from the region map")
    add_rom(p)
    p.add_argument("-o", "--output", default=None)
    p.add_argument("--report", default=None)
    p.add_argument("--reference", default=None)
    p.add_argument("--ads12-root", default=None)
    p.add_argument(
        "--allow-passthrough",
        action="store_true",
        help="permit copying regions the reference build rebuilds, with a labelled report",
    )
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("status", help="run every achievable gate and summarise")
    add_rom(p)
    p.add_argument("--reference", default=None)
    p.add_argument("--ads12-root", default=None)
    p.set_defaults(func=cmd_status)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return EXIT_USAGE
    except Exception as exc:  # noqa: BLE001 - surfaced to the operator
        print(f"unexpected error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_USAGE
