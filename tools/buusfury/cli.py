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
# fixed   (Workstream 2: generate, don't copy)
# --------------------------------------------------------------------------
def cmd_fixed(args) -> int:
    from . import fixed as _fixed

    try:
        rom = _resolve_rom(args)
        identity = _identity.verify(rom)
    except (_identity.IdentityError, _identity.RomNotFoundError) as exc:
        print(f"FAIL: {exc}")
        return EXIT_FAIL

    data = identity.path.read_bytes()
    results = _fixed.verify_all(data)
    if args.json:
        print(json.dumps([r.as_dict() for r in results], indent=2))
    else:
        print(f"{'region':<20} {'result':<8} {'bytes':>7}  detail")
        for result in results:
            state = "OK" if result.matches_rom else "FAIL"
            print(
                f"{result.region_id:<20} {state:<8} {result.generated_length:>7}  {result.detail}"
            )
    good = sum(1 for r in results if r.matches_rom)
    print(f"\n{good}/{len(results)} fixed regions generate byte-identically")
    return EXIT_OK if good == len(results) else EXIT_FAIL


# --------------------------------------------------------------------------
# rommap   (Workstreams 1, 3, 4, 5, 6, 7)
# --------------------------------------------------------------------------
def cmd_rommap(args) -> int:
    from . import analysis as _analysis
    from . import mapbuild as _mapbuild
    from . import rommap as _rm

    try:
        rom = _resolve_rom(args)
        identity = _identity.verify(rom)
    except (_identity.IdentityError, _identity.RomNotFoundError) as exc:
        print(f"FAIL: {exc}")
        return EXIT_FAIL

    data = identity.path.read_bytes()
    tooling = {
        "disassembler": f"capstone {__import__('capstone').__version__} (ARM + Thumb)",
        "array_math": f"numpy {__import__('numpy').__version__}",
        "ghidra": "not used and not installed; import metadata is left to a later ticket",
    }

    print("analysing...")
    reset = _analysis.trace_reset(data)
    if args.show_reset:
        for line in reset.evidence:
            print(f"  - {line}")

    rom_map = _mapbuild.build_rom_map(data, identity.sha1, tooling=tooling)
    coverage = rom_map.coverage()

    print(f"\nROM map: {len(rom_map.regions)} regions tile {rom_map.rom_size:,} bytes exactly")
    print(f"\n{'classification':<20} {'bytes':>12} {'share':>9} {'regions':>8}  bytes by confidence")
    for name, slot in coverage.items():
        breakdown = ", ".join(f"{lvl} {n:,}" for lvl, n in slot["confidence"].items())
        print(
            f"{name:<20} {slot['bytes']:>12,} {100.0*slot['bytes']/rom_map.rom_size:>8.3f}% "
            f"{slot['regions']:>8}  {breakdown}"
        )
    print(f"{'total':<20} {rom_map.rom_size:>12,} {100.0:>8.3f}% {len(rom_map.regions):>8}")

    print("\nexecutable byte coverage:")
    for state, count in rom_map.executable_coverage().items():
        print(f"  {state:<10} {count:>12,}  {100.0*count/rom_map.rom_size:>7.3f}%")

    # --- function discovery
    seeds = [
        (reset.entry_address, reset.entry_isa, "cartridge header entry branch"),
        (reset.handoff_address, "arm", "reset path tail branch (C runtime entry veneer)"),
        (reset.game_entry, "thumb", "lr value the reset path sets before the tail branch"),
    ]
    if reset.library_entry:
        seeds.append((reset.library_entry, "thumb", "code pointer the C runtime veneer BXes"))
    for region in rom_map.regions:
        if region.classification == "code" and region.confidence in ("proven", "high") and region.isa:
            seeds.append((region.address_start, region.isa, f"entry of proven code region {region.id}"))

    print(f"\ndiscovering functions from {len(seeds)} seeds...")
    discovery = _analysis.discover_functions(data, rom_map, seeds)
    inventory = _rm.FunctionInventory(
        functions=list(discovery.functions.values()),
        source_sha1=identity.sha1,
        method=(
            "linear sweep of every code-classified region in its own instruction set, "
            "harvesting BL/BLX immediate targets and literal-pool code pointers, iterated "
            "to a fixpoint and then validated by disassembling from each candidate"
        ),
        notes="No semantic name is assigned to any function. Names are sub_<address>.",
    )
    counts = inventory.counts()
    print(f"\n{'ARM (confirmed)':<20} {counts['confirmed_arm']:>6}")
    print(f"{'ARM (probable)':<20} {counts['probable_arm']:>6}")
    print(f"{'Thumb (confirmed)':<20} {counts['confirmed_thumb']:>6}")
    print(f"{'Thumb (probable)':<20} {counts['probable_thumb']:>6}")
    print(f"{'ISA uncertain':<20} {counts['uncertain_isa']:>6}")
    print(f"{'total candidates':<20} {counts['total']:>6}")

    if args.write:
        target = Path(args.write)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(rom_map.to_json())
        print(f"\nwrote {target}")
    if args.functions:
        target = Path(args.functions)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(inventory.to_json())
        print(f"wrote {target}")
    if args.docs:
        target = Path(args.docs)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(_rm.render_rom_map_markdown(rom_map, tooling))
        print(f"wrote {target}")
    return EXIT_OK


# --------------------------------------------------------------------------
# compiler-probe   (DECOMP-COMPILER-PROBE-001)
# --------------------------------------------------------------------------
def cmd_compiler_probe(args) -> int:
    from . import compiler_probe as _cp

    if args.write_manifest:
        target = _cp.write_manifest(
            Path(args.write_manifest) if isinstance(args.write_manifest, str) else None
        )
        print(f"wrote {target}")
        return EXIT_OK

    if args.write_matrix:
        target = _cp.write_matrix(
            Path(args.write_matrix) if isinstance(args.write_matrix, str) else None
        )
        print(f"wrote {target}")
        return EXIT_OK

    try:
        rom = _resolve_rom(args)
        found = _identity.verify(rom)
    except (_identity.IdentityError, _identity.RomNotFoundError) as exc:
        print(f"FAIL: {exc}")
        return EXIT_FAIL

    data = found.path.read_bytes()

    if args.verify_manifest:
        problems = _cp.verify_manifest(data)
        if problems:
            print("PROBE MANIFEST: FAIL")
            for problem in problems:
                print(f"  - {problem}")
            return EXIT_FAIL
        manifest = _cp.load_manifest()
        print(
            f"PROBE MANIFEST: PASS ({manifest['counts']['probes']} probes, "
            f"{manifest['counts']['thumb']} thumb / {manifest['counts']['arm']} arm, "
            f"{manifest['counts']['leaf']} leaf / {manifest['counts']['non_leaf']} non-leaf)"
        )
        return EXIT_OK

    if args.verify_matrix:
        problems = _cp.verify_matrix(data, found.sha1)
        if problems:
            print("PROBE MATRIX: FAIL")
            for problem in problems:
                print(f"  - {problem}")
            return EXIT_FAIL
        print("PROBE MATRIX: PASS (config/compiler_matrix.json reproduces)")
        return EXIT_OK

    if args.plan:
        tools = _cp.discover_ads(args.ads12_root, compiler_id=args.frontend)
        unit = _cp.GBARAM_TU
        workdir = _cp.PROBE_WORKSPACE / unit.id
        print(f"probe plan for {unit.id} ({unit.source})")
        print(f"compiler: {args.frontend}  cpu: {args.cpu}  opt: {args.opt}")
        print()
        if tools is None:
            print(f"BLOCKED [{_cp.BLOCK_ADS_UNAVAILABLE}] no identified ADS 1.2 installation")
            print()
            for detail in _cp.ads_blocked_details(args.ads12_root):
                print(f"  {detail}")
            print()
        else:
            print(f"identified toolchain: {tools.banner}")
            print()
        print("exact command sequence once ADS 1.2 is supplied:")
        planning = tools or _cp.planning_tools(args.frontend)
        commands = _cp.plan_commands(
            planning,
            Path("<repo>") / unit.source,
            workdir,
            (args.frontend, args.cpu, args.opt),
        )
        for command in commands:
            print("  " + " ".join(command))
        print()
        print("linker layout (probe.scatter):")
        for line in _cp.render_scatter(unit).splitlines():
            print(f"  {line}")
        print()
        print("relocation methodology:")
        print(f"  {_cp.ORIGIN_ASSUMPTION}")
        print()
        print("toolchain identification:")
        print(f"  {_cp.BANNER_ASSUMPTION}")
        print()
        print("--plan executes nothing and therefore always exits 0.")
        return EXIT_OK

    if args.matrix:
        matrix = run_matrix(args, data, found.sha1)
        if args.json:
            print(json.dumps(matrix, indent=2))
        else:
            print(_cp.render_matrix_markdown(matrix).rstrip())
            print()
            print(f"result: {matrix['result']}")
            print(
                f"configurations compared: {matrix['comparisons_run']} of "
                f"{len(matrix['configurations'])}"
            )
            for line in matrix.get("details", []):
                print(f"  {line}")
            if not matrix["comparisons_run"]:
                print()
                print("live toolchain state on this machine:")
                for line in _cp.ads_blocked_details(args.ads12_root):
                    print(f"  {line}")
        # Exit 0 only when at least one configuration actually compared bytes.
        # A blocked matrix is a failure to obtain a verdict, not a pass.
        return EXIT_OK if matrix["comparisons_run"] else EXIT_FAIL

    if args.diagnostic_control:
        return _run_diagnostic_control(args, data)

    # default: report the prepared probe corpus and its blocked/tooled state.
    # A blocked toolchain makes this a NON-ZERO exit even under --json, because
    # no verdict was obtained and the documented contract says so.
    manifest = _cp.derive_manifest(data)
    tools = _cp.discover_ads(args.ads12_root, compiler_id=args.frontend)
    # An identified toolchain is not a usable one. Ask it to compile something
    # trivial before calling the probe ready: "a toolchain was found" is a proxy
    # for "a verdict is obtainable", and a licence refusal makes them differ.
    licensed: bool | None = None
    licence_evidence: str | None = None
    if tools is not None:
        licensed, licence_evidence = _cp.licence_status(
            tools, _cp.PROBE_WORKSPACE / "licence-check"
        )
    usable = tools is not None and licensed
    if tools is None:
        result = _cp.blocked_result(args.ads12_root)["result"]
    elif not licensed:
        result = f"COMPILER PROBE: BLOCKED - {_cp.BLOCK_LICENSE}"
    else:
        result = "COMPILER PROBE: READY - run with --matrix to test configurations"

    report = {
        "canonical_rom_sha1": found.sha1,
        "ads12_available": tools is not None,
        "ads12_banner": tools.banner if tools else None,
        "ads12_licensed": licensed,
        "ads12_licence_evidence": licence_evidence,
        "probe_corpus": manifest["counts"],
        "result": result,
        "no_compiler_result_claimed": not usable,
        "translation_units": manifest["translation_units"],
        "probes": manifest["probes"],
        "controls": manifest["controls"],
        "rejections": manifest["rejections"],
        "consistency_problems": manifest["consistency_problems"],
    }

    if args.json:
        print(json.dumps(report, indent=2))
        if report["consistency_problems"]:
            return EXIT_FAIL
        return EXIT_OK if usable else EXIT_FAIL

    print("=" * 72)
    print("COMPILER PROBE - DECOMP-COMPILER-PROBE-001")
    print("=" * 72)
    print(f"canonical ROM : {found.sha1}")
    if tools is None:
        print("ADS 1.2       : ABSENT")
    else:
        print(f"ADS 1.2       : {tools.banner}")
        print(f"  installed at: {tools.root}")
        print(f"  licensed    : {'yes' if licensed else 'NO - ' + str(licence_evidence)}")
    print()
    counts = manifest["counts"]
    print(
        f"probe corpus  : {counts['probes']} functions in {counts['translation_units']} "
        f"translation unit ({counts['thumb']} Thumb / {counts['arm']} ARM, "
        f"{counts['leaf']} leaf / {counts['non_leaf']} non-leaf)"
    )
    print()
    print(f"{'probe':<14} {'rom address':<12} {'bytes':>6} {'insn':>5} {'leaf':<5} {'lits':>5}  role")
    for probe in manifest["probes"]:
        print(
            f"{probe['name']:<14} {probe['rom_address']:<12} {probe['byte_length']:>6} "
            f"{probe['instructions']:>5} {str(probe['leaf']):<5} "
            f"{len(probe['literal_slots']):>5}  {probe['role']}"
        )
    if manifest["consistency_problems"]:
        print()
        print("CONSISTENCY PROBLEMS:")
        for problem in manifest["consistency_problems"]:
            print(f"  - {problem}")
        return EXIT_FAIL

    print()
    print(f"controls (NOT evidence)  : {len(manifest['controls'])} regions excluded by role")
    for control in manifest["controls"]:
        print(f"  {control['id']:<14} {control['rom_address']}  {control['excluded_because'][:64]}...")
    print(f"rejected candidates      : {len(manifest['rejections'])}")

    print()
    print("=" * 72)
    if tools is None:
        blocked = _cp.blocked_result(args.ads12_root)
        print(blocked["result"])
        print("=" * 72)
        print()
        print("Preparation is complete; NO compiler result is claimed.")
        print("exact command required once ADS 1.2 is supplied:")
        print(f"  {blocked['exact_command_required']}")
        print()
        for detail in blocked["details"]:
            print(f"  {detail}")
        return EXIT_FAIL
    print(f"COMPILER PROBE: READY - identified {tools.banner}")
    print("  run with --matrix to test configurations")
    print("=" * 72)
    return EXIT_OK


def run_matrix(args, data: bytes, sha1: str) -> dict:
    """Run every candidate configuration, or report the whole matrix as blocked."""
    from . import compiler_probe as _cp

    return _cp.build_matrix(data, sha1, ads12_root=args.ads12_root)


def _run_diagnostic_control(args, data: bytes) -> int:
    """Exercise the compile/compare plumbing with a modern compiler.

    Explicitly NOT evidence about the original build: the result is tagged
    DIAGNOSTIC_CONTROL_NOT_EVIDENCE and is only here so that the harness's
    extraction, compilation, byte comparison and reporting paths are known to
    work on a machine that has no ADS 1.2.
    """
    from . import compiler_probe as _cp

    compiler = _cp.discover_diagnostic_compiler()
    if compiler is None:
        print(f"DIAGNOSTIC CONTROL: unavailable (no arm-none-eabi-gcc on this machine)")
        return EXIT_FAIL

    unit = _cp.GBARAM_TU
    source = _identity.REPO_ROOT / unit.source
    workdir = _cp.PROBE_WORKSPACE / unit.id / "diagnostic_control"
    target = _cp.extract(data, unit.rom_address, unit.end_address - unit.rom_address)

    print("=" * 72)
    print("DIAGNOSTIC CONTROL - NOT EVIDENCE ABOUT THE ORIGINAL COMPILER")
    print("=" * 72)
    print(json.dumps(compiler.as_dict(), indent=2))
    print()

    try:
        candidate, commands = _cp.compile_diagnostic_control(
            compiler, source, workdir, cpu="arm7tdmi", opt="-O1", thumb=True
        )
    except _cp.ProbeError as exc:
        print(f"DIAGNOSTIC CONTROL: FAILED\n{exc}")
        return EXIT_FAIL

    for command in commands:
        print("  " + " ".join(command))
    print()
    diff = _cp.compare_bytes(
        target,
        candidate,
        unit.rom_address,
        unit.isa,
        notes=(_cp.DIAGNOSTIC_CONTROL, "plumbing self-test only"),
    )
    payload = {
        "classification": _cp.DIAGNOSTIC_CONTROL,
        "target_size": diff.target_size,
        "candidate_size": diff.candidate_size,
        "identical_bytes": diff.identical_bytes,
        "first_difference": diff.as_dict()["first_difference"],
        "first_difference_address": diff.as_dict()["first_difference_address"],
        "differing_bytes": diff.differing_bytes,
        "target_instructions": diff.target_instructions,
        "differing_instructions": diff.differing_instructions,
        "matching_instructions": diff.matching_instructions,
        "exact_match": diff.exact_match,
        "is_evidence_about_the_original_compiler": False,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for key in (
            "target_size",
            "candidate_size",
            "identical_bytes",
            "first_difference",
            "first_difference_address",
            "differing_bytes",
            "target_instructions",
            "differing_instructions",
            "matching_instructions",
            "exact_match",
        ):
            print(f"  {key:<26} {payload[key]}")
        print()
        print("  This run exercises the harness. It is NOT a compiler finding:")
        print("  a modern GCC cannot be evidence about the original Webfoot build.")
    return EXIT_OK


# --------------------------------------------------------------------------
# lift   (DECOMP-LIFT-PILOT-001)
# --------------------------------------------------------------------------
def cmd_lift(args) -> int:
    from . import lift as _lift

    if args.list_targets:
        print(f"{'id':<14} {'translation unit':<18} {'source':<22} {'cpu':<12} isa    opt")
        for target in _lift.load_targets():
            print(
                f"{target.id:<14} {target.probe_translation_unit:<18} "
                f"{target.decomp_source:<22} {target.cpu:<12} {target.isa:<6} "
                f"{target.optimization}"
            )
        return EXIT_OK

    toolchain = _lift.discover_modern_toolchain(args.toolchain_root)
    if toolchain is None:
        print("LIFT: BLOCKED [MODERN_TOOLCHAIN_UNAVAILABLE]")
        print(
            "  No ARM cross toolchain was found. Looked at --toolchain-root, then "
            f"${_lift.DEVKITARM_ENV}, then {_lift.DEFAULT_DEVKITARM}."
        )
        print("  This ticket requires an EXISTING toolchain; it installs nothing.")
        return EXIT_FAIL

    try:
        rom = _resolve_rom(args)
        found = _identity.verify(rom)
    except (_identity.IdentityError, _identity.RomNotFoundError) as exc:
        print(f"FAIL: {exc}")
        return EXIT_FAIL

    data = found.path.read_bytes()
    target_ids = (
        [t.id for t in _lift.load_targets()] if args.target == "all" else [args.target]
    )

    exit_code = EXIT_OK
    for target_id in target_ids:
        try:
            document = _lift.run_lift(
                target_id,
                data,
                toolchain,
                run_semantic=not args.no_semantic,
            )
        except (_lift.LiftError, _cp_free_exception()) as exc:  # pragma: no cover
            print(f"LIFT {target_id}: FAIL\n  {exc}")
            exit_code = EXIT_FAIL
            continue

        verdicts = document["verdicts"]
        if args.json:
            print(json.dumps(document, indent=2))
        elif args.verify:
            verification = _lift.verify_report(data, target_id)
            if verification["ok"]:
                print(f"LIFT {target_id} REPORT: PASS ({verification['detail']})")
            else:
                print(f"LIFT {target_id} REPORT: FAIL ({verification['detail']})")
                for problem in verification["problems"][:40]:
                    print(f"  - {problem}")
                if len(verification["problems"]) > 40:
                    print(f"  ... {len(verification['problems']) - 40} more")
                exit_code = EXIT_FAIL
            for note in verification["exempted"]:
                print(f"  exempted: {note}")
        else:
            print(f"=== lift {target_id}: {document['target']['name']} ===")
            print(f"  source        : {document['target']['decomp_source']}")
            print(
                f"  ROM extent    : file {document['target']['file_offset']}"
                f"..0x{int(document['target']['file_offset'], 16) + document['target']['byte_length']:06X}"
                f"   address {document['target']['rom_address']}"
                f"..{document['target']['end_address']}"
                f"   ({document['target']['byte_length']} bytes,"
                f" {document['target']['code_byte_length']} code)"
            )
            print(
                f"  toolchain     : {document['modern_build']['identity']['gcc_banner']}"
            )
            print(f"  config        : {document['modern_build']['compiler_configuration']}")
            print()
            for name in ("semantic", "modern_build", "ads_match"):
                verdict = verdicts[name]
                print(f"  {name.upper():<14} {verdict['status']}")
                print(f"                 {verdict['detail']}")
            print()
            if document.get("comparison", {}).get("original_byte_length"):
                comparison = document["comparison"]
                print("  modern vs original (MEASUREMENT ONLY, not a match claim):")
                for key in (
                    "original_byte_length",
                    "modern_byte_length",
                    "differing_bytes_in_overlap",
                    "matching_instruction_spans",
                    "differing_instruction_spans",
                    "byte_identical",
                ):
                    print(f"    {key:<42} {comparison[key]}")
            print()
            print(f"  {'function':<16} {'orig B':>7} {'mod B':>7} {'orig i':>7} {'mod i':>7} {'calls':>7} {'lits':>5}")
            for row in document["functions"]:
                original = row["original"]
                modern = row["modern"]
                print(
                    f"  {row['name']:<16} {original['size']:>7} "
                    f"{(modern['size'] if modern else 0):>7} "
                    f"{original['instructions']:>7} "
                    f"{(modern['instructions'] if modern else 0):>7} "
                    f"{len(original['calls']):>7} "
                    f"{len(original['literal_slots']):>5}"
                )

        target_path = Path(args.write) if args.write else _lift.report_path_for(target_id)
        _lift.write_report(document, target_path)
        print(f"  report        : {target_path}")

        if verdicts["semantic"]["status"] not in ("PROVEN", "UNTESTED"):
            exit_code = EXIT_FAIL
        if verdicts["modern_build"]["status"] != "PASS":
            exit_code = EXIT_FAIL

    return exit_code


def _cp_free_exception():
    """The compiler-probe exception type, imported lazily to avoid a cycle."""
    from . import compiler_probe as _cp

    return _cp.ProbeError


# --------------------------------------------------------------------------
# decompdev-inventory   (INFRA-DECOMPDEV-001)
# --------------------------------------------------------------------------
def cmd_decompdev_inventory(args) -> int:
    from . import decompdev as _dd

    try:
        inventory = _dd.build_inventory(_dd.load_inputs())
    except (_dd.DecompDevError, OSError, KeyError, ValueError) as exc:
        print(f"DECOMPDEV INVENTORY: FAIL\n  {exc}")
        return EXIT_FAIL

    if isinstance(args.write, str):
        path = Path(args.write)
    elif args.write:
        path = _dd.INVENTORY_PATH
    else:
        path = _dd.INVENTORY_PATH
    problems = list(inventory.problems)

    # The inventory is derived from committed provenance only, so a refresh never
    # needs the ROM. What it must never do silently is SHRINK: unresolved work has
    # to stay in the denominator, or a ticket could raise its own percentage by
    # deleting work it could not reconstruct.
    previous = _dd.previous_inventory_totals(path)
    changes, shrink = _dd.denominator_changes(inventory, previous)
    if shrink and not args.allow_denominator_decrease:
        problems.extend(shrink)
    elif shrink:
        for problem in shrink:
            print(f"  ALLOWED (denominator decrease): {problem}")

    if problems:
        print("DECOMPDEV INVENTORY: FAIL")
        for problem in problems:
            print(f"  - {problem}")
        return EXIT_FAIL

    if args.check:
        stale = _dd.compare_inventory(inventory, path)
        if stale:
            print("DECOMPDEV INVENTORY: STALE")
            for problem in stale[:40]:
                print(f"  - {problem}")
            if len(stale) > 40:
                print(f"  ... {len(stale) - 40} more")
            return EXIT_FAIL
        print(
            f"DECOMPDEV INVENTORY: PASS ({inventory.tracked_functions} tracked "
            f"functions, {inventory.tracked_executable_bytes:,} tracked executable "
            f"bytes, committed snapshot reproduces)"
        )
        return EXIT_OK

    if not args.write:
        print(
            f"DECOMPDEV INVENTORY: derived ({inventory.tracked_functions} tracked "
            f"functions, {inventory.tracked_executable_bytes:,} tracked executable "
            f"bytes); pass --write to commit it or --check to compare"
        )
        for change in changes:
            print(f"  {change}")
        return EXIT_OK

    path.parent.mkdir(parents=True, exist_ok=True)
    # newline="\n" is load-bearing: Python's text mode would emit CRLF on Windows
    # and the committed snapshot would differ from its regenerated form.
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(inventory.to_json())
    print(
        f"DECOMPDEV INVENTORY: WROTE {path} ({inventory.tracked_functions} tracked "
        f"functions, {inventory.tracked_executable_bytes:,} tracked executable bytes)"
    )
    for change in changes:
        print(f"  {change}")
    return EXIT_OK


# --------------------------------------------------------------------------
# decompdev-report   (INFRA-DECOMPDEV-001)
# --------------------------------------------------------------------------
def cmd_decompdev_report(args) -> int:
    from . import decompdev as _dd

    try:
        inventory = _dd.build_inventory(_dd.load_inputs())
    except (_dd.DecompDevError, OSError, KeyError, ValueError) as exc:
        print(f"DECOMPDEV REPORT: FAIL\n  {exc}")
        return EXIT_FAIL

    report = _dd.objdiff_report(inventory)
    text = _dd.render_report_json(report)
    percent = report["measures"].get("matched_code_percent", 0.0)

    # Capture the committed report's measures BEFORE --out can overwrite it, so
    # the change line the ticket quotes reports real movement rather than
    # comparing the fresh document against itself.
    previous = _dd.committed_report_measures()

    if args.out:
        target = Path(args.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        print(
            f"DECOMPDEV REPORT: wrote {target} ({len(text):,} bytes, "
            f"{len(report['units'])} units)"
        )

    if args.summary or not (args.check or args.json):
        for line in inventory.summary_lines():
            print(line)
        print()
        print(f"artifact      : {_dd.ARTIFACT_NAME} containing {_dd.ARTIFACT_FILE_NAME}")
        print(
            f"report version: {_dd.VERSION_NAME} "
            f"(objdiff Report version {_dd.REPORT_VERSION})"
        )
        print("local command : python -m buusfury decompdev-report --out report.json")

    if args.json:
        print(text, end="")

    if not args.check:
        return EXIT_OK

    problems, line = _dd.check(inventory, previous_measures=previous)
    if problems:
        print("DECOMPDEV REPORT: FAIL")
        for problem in problems:
            print(f"  - {problem}")
        print(f"decomp.dev: semantic code {percent:.3f}% (report check FAIL)")
        return EXIT_FAIL

    print(
        "DECOMPDEV REPORT: PASS "
        f"({len(report['units'])} units, {inventory.complete_functions} "
        "semantic-complete functions, deterministic, committed report current)"
    )
    print(line)
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

    p = sub.add_parser(
        "fixed", help="generate the zero-toolchain fixed regions and compare to the ROM"
    )
    add_rom(p)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_fixed)

    p = sub.add_parser(
        "rommap", help="build the independent ROM map and the candidate function inventory"
    )
    add_rom(p)
    p.add_argument("--write", default=None, help="write config/rom_map.json here")
    p.add_argument("--functions", default=None, help="write config/functions.json here")
    p.add_argument("--docs", default=None, help="write docs/ROM_MAP.md here")
    p.add_argument("--show-reset", action="store_true", help="print the reset-path evidence")
    p.set_defaults(func=cmd_rommap)

    p = sub.add_parser(
        "compiler-probe",
        help="establish the ADS 1.2 compiler recipe by compiling probes and diffing bytes",
    )
    add_rom(p)
    p.add_argument("--ads12-root", default=None, help="ARM Developer Suite 1.2 root")
    p.add_argument("--frontend", default="tcpp", help="compiler frontend (tcpp/tcc/armcpp/armcc)")
    p.add_argument("--cpu", default="ARM7TDMI")
    p.add_argument("--opt", default="-O1")
    # The modes are mutually exclusive on purpose: previously a combined
    # invocation silently ran only one of them, which is how a flag can appear
    # to have had an effect it never had.
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--matrix", action="store_true", help="run every candidate configuration")
    mode.add_argument("--plan", action="store_true", help="print the exact commands, execute nothing")
    mode.add_argument(
        "--write-manifest",
        nargs="?",
        const=True,
        default=None,
        help="regenerate config/compiler_probes.json from the canonical ROM",
    )
    mode.add_argument(
        "--write-matrix",
        nargs="?",
        const=True,
        default=None,
        help="regenerate config/compiler_matrix.json",
    )
    mode.add_argument("--verify-manifest", action="store_true", help="re-derive and compare the manifest")
    mode.add_argument("--verify-matrix", action="store_true", help="re-derive and compare the matrix")
    mode.add_argument(
        "--diagnostic-control",
        action="store_true",
        help="exercise the harness with devkitARM GCC; NEVER evidence about the original compiler",
    )
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_compiler_probe)

    p = sub.add_parser(
        "lift",
        help="semantic lifting loop: decompiled source -> modern build -> comparison",
    )
    add_rom(p)
    p.add_argument("--target", default="gbaram", help="target id, or 'all'")
    p.add_argument("--list-targets", action="store_true", help="list the registry and exit")
    p.add_argument("--toolchain-root", default=None, help="ARM cross toolchain root")
    p.add_argument("--write", default=None, help="report path (default config/lift_<id>.json)")
    p.add_argument("--verify", action="store_true", help="regenerate and compare the whole report")
    p.add_argument("--no-semantic", action="store_true", help="skip the host self-check")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_lift)

    p = sub.add_parser(
        "decompdev-inventory",
        help=(
            "derive the decomp.dev progress inventory (the denominator) from committed "
            "project provenance; needs no ROM and no toolchain"
        ),
    )
    p.add_argument(
        "--write",
        nargs="?",
        const=True,
        default=None,
        help="write the snapshot (default config/decompdev_inventory.json)",
    )
    p.add_argument("--check", action="store_true", help="verify the committed snapshot reproduces from the inputs")
    p.add_argument(
        "--allow-denominator-decrease",
        action="store_true",
        help=(
            "permit a tracked-function or tracked-byte DECREASE. Requires review: "
            "removing unresolved work raises the percentage without doing any."
        ),
    )
    p.set_defaults(func=cmd_decompdev_inventory)

    p = sub.add_parser(
        "decompdev-report",
        help=(
            "generate the objdiff Report version 2 that decomp.dev ingests "
            "(semantic coverage, not byte matching)"
        ),
    )
    p.add_argument("--out", default=None, help="write the report JSON here")
    p.add_argument("--check", action="store_true", help="verify determinism, invariants and the committed report")
    p.add_argument("--summary", action="store_true", help="print the human-readable summary")
    p.add_argument("--json", action="store_true", help="print the report itself")
    p.set_defaults(func=cmd_decompdev_report)

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
