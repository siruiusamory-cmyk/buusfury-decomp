"""`webfoot randomize` - the project-first randomizer command.

This is where the enemy pack meets the normal build path. The command composes
the layers that already exist rather than adding a second pipeline::

    canonical ROM (read-only)
        -> semantic model          maps, placements, transitions, stat records
        -> seeded module mutations  type / placement / stat, via their authorities
        -> validated WritePlan      one plan, overlap-checked against the base
        -> emit_image               the one writer
        -> output ROM

Nothing here patches bytes directly. Every write is a
:class:`~tools.webfoot.write.ByteChange` produced by a semantic authority,
validated by :func:`~tools.webfoot.write.plan_changes` and applied by
:func:`~tools.webfoot.write.emit_image`, which is the same path the project build
uses. That is the point of the command: it demonstrates the SDK rather than
bypassing it.

Safety
======

The canonical image is an input on every path and an output on none:

* the output may not be the input, under any spelling, symlink or hard link;
* an existing output is never replaced without ``--overwrite``;
* an existing output that is itself a copy of the canonical image is refused even
  then, because replacing it would destroy a clean ROM;
* the input is re-identified after the write and the run fails closed if its
  SHA-256 moved.

No ROM is ever committed or copied into the repository by this command; the
caller chooses the output path.
"""

from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys

from ..enemy_randomizer.config import (
    DEFAULT_STAT_FIELDS,
    STAT_FIELDS,
    EnemyRandomizerConfig,
    ConfigError,
    PRESETS,
    preset as lookup_preset,
)
from ..enemy_randomizer.manifest import SpoilerLog, canonical_json
from ..enemy_randomizer.planner import EnemyRandomizerError, plan_enemy_randomization
from ..enemy_randomizer.seeds import (
    MODULE_ENEMY_PLACEMENT,
    MODULE_ENEMY_STAT,
    MODULE_ENEMY_TYPE,
    SeedError,
)
from ..rom import identify_rom
from ..write import WriteError, emit_image, paths_are_the_same_file

#: The enemy modules a caller can toggle individually. The warp module is not
#: listed: it is a separate product with its own command and its own output, and
#: offering it here would imply this pack writes two ROMs.
TOGGLEABLE_MODULES = (MODULE_ENEMY_TYPE, MODULE_ENEMY_PLACEMENT, MODULE_ENEMY_STAT)

#: The default output basename. ``{seed}`` receives a filename-safe rendering,
#: never the algorithm seed.
OUTPUT_TEMPLATE = "Buu's Fury - Randomized - {seed}.gba"


class RandomizeError(ValueError):
    """A refused run. The message is user-facing."""


def add_parser(subparsers) -> None:
    """Register the `randomize` surface. Kept here so `cli.py` stays a wiring file."""
    parser = subparsers.add_parser(
        "randomize",
        help=(
            "generate a deterministic randomized ROM from a seed and a preset, "
            "through the normal semantic project/build path"
        ),
    )
    parser.add_argument("rom", type=Path, help="the canonical ROM (opened read-only)")
    parser.add_argument(
        "--seed",
        required=False,
        default=None,
        help=(
            "the master seed. One seed deterministically derives an independent "
            "seed for every module, so enabling one module cannot change another's "
            "result. Any non-empty string or integer."
        ),
    )
    parser.add_argument(
        "--preset",
        default="stream-safe",
        help=f"a named preset: {', '.join(sorted(PRESETS))} (default: stream-safe)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="output ROM path; defaults to a name beside the input",
    )
    parser.add_argument(
        "--spoiler",
        type=Path,
        default=None,
        help="write a spoiler log (per-slot identities, positions and stats) here",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="write the run manifest here (default: beside the output ROM)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace an existing output; a copy of the canonical ROM is still refused",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="plan and validate the run, print the summary, and write nothing",
    )
    parser.add_argument(
        "--list-presets",
        action="store_true",
        help="print the presets and their enabled modules, then exit",
    )
    parser.add_argument(
        "--stat-range",
        default=None,
        help=(
            "override the preset's multiplier band as LOW:HIGH with exact "
            "fractions, e.g. 3/4:27/20"
        ),
    )
    parser.add_argument(
        "--stat-fields",
        default=None,
        help=(
            f"comma-separated stat fields to randomize; default: "
            f"{','.join(DEFAULT_STAT_FIELDS)}"
        ),
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--only",
        default=None,
        help=(
            "run only these modules (comma-separated): "
            f"{', '.join(TOGGLEABLE_MODULES)}"
        ),
    )
    group.add_argument(
        "--without",
        default=None,
        help="run every module except these (comma-separated)",
    )


def _parse_modules(raw: str | None, *, default) -> frozenset[str]:
    if raw is None:
        return default
    names = [name.strip() for name in raw.split(",") if name.strip()]
    unknown = set(names) - set(TOGGLEABLE_MODULES)
    if unknown:
        raise RandomizeError(
            f"unknown module(s): {', '.join(sorted(unknown))}; "
            f"known: {', '.join(TOGGLEABLE_MODULES)}"
        )
    return frozenset(names)


def parse_stat_range(text: str):
    """``LOW:HIGH`` with exact fractions, refused rather than approximated."""
    from fractions import Fraction

    from ..enemy_randomizer.config import StatRange

    low_text, separator, high_text = text.partition(":")
    if not separator:
        raise RandomizeError(
            f"--stat-range needs LOW:HIGH, got {text!r} (e.g. 3/4:27/20)"
        )
    try:
        low = Fraction(low_text.strip())
        high = Fraction(high_text.strip())
    except (ValueError, ZeroDivisionError) as exc:
        raise RandomizeError(
            f"--stat-range values must be exact fractions or integers: {exc}"
        ) from exc
    return StatRange(low, high, f"custom {low}:{high}")


def build_config(args) -> EnemyRandomizerConfig:
    """The configuration this invocation describes, or a refusal.

    The preset supplies the defaults and every flag is an explicit override on top
    of it, so a caller who passes nothing gets exactly the named preset.
    """
    base = lookup_preset(args.preset).config
    enabled = base.enabled
    if args.only is not None:
        enabled = _parse_modules(args.only, default=enabled)
    elif args.without is not None:
        enabled = enabled - _parse_modules(args.without, default=frozenset())
    fields = base.stat_fields
    if args.stat_fields is not None:
        fields = tuple(f.strip() for f in args.stat_fields.split(",") if f.strip())
        unknown = set(fields) - set(STAT_FIELDS)
        if unknown:
            raise RandomizeError(
                f"unknown stat field(s): {', '.join(sorted(unknown))}; "
                f"known: {', '.join(sorted(STAT_FIELDS))}"
            )
    stat_range = base.stat_range
    if args.stat_range is not None:
        stat_range = parse_stat_range(args.stat_range)
    return replace(base, enabled=frozenset(enabled), stat_fields=fields, stat_range=stat_range)


def _filename_safe(seed: str) -> str:
    """A filename-safe rendering of the seed; the algorithm seed is untouched."""
    text = "".join(c if (c.isalnum() or c in " _-") else " " for c in str(seed))
    text = " ".join(text.split()).rstrip(". ")
    return (text[:64].strip().rstrip(". ")) or "seed"


def default_output(rom: Path, seed: str) -> Path:
    return rom.parent / OUTPUT_TEMPLATE.format(seed=_filename_safe(seed))


def default_manifest(output: Path) -> Path:
    return output.with_suffix(".manifest.json")


def _git_commit() -> str | None:
    """The SDK commit, for the manifest. Best-effort: a non-checkout has none.

    Read through ``git rev-parse`` rather than a library so the command works in
    an installed layout, and return ``None`` rather than failing when there is no
    repository, because a missing commit is a provenance gap and not a reason to
    refuse an otherwise reproducible run.
    """
    import subprocess

    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(__file__).resolve().parent,
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    text = result.stdout.strip()
    return text if result.returncode == 0 and text else None


def _print_presets() -> int:
    for name in sorted(PRESETS):
        entry = PRESETS[name]
        print(f"{name}: {entry.description}")
        print(f"    modules: {', '.join(sorted(entry.config.enabled))}")
        band = entry.config.stat_range
        print(f"    stats: {band.label} " + (f"[{band.low} .. {band.high}]" if band else "(off)"))
    return 0


def run(args) -> int:
    if args.list_presets:
        return _print_presets()
    if args.seed is None:
        raise RandomizeError(
            "--seed is required. One master seed controls every module; omit it "
            "only with --list-presets."
        )

    config = build_config(args)
    catalog = load_catalog_for(args)
    source = Path(args.rom)
    output = Path(args.output) if args.output else default_output(source, args.seed)

    if paths_are_the_same_file(source, output):
        raise RandomizeError(
            "the output is the input ROM; this command never writes to the ROM it "
            "reads. Choose a different --output."
        )

    manifest_path = Path(args.manifest) if args.manifest else default_manifest(output)
    for candidate, label in ((manifest_path, "the manifest path"),):
        if paths_are_the_same_file(candidate, source):
            raise RandomizeError(f"{label} is the input ROM: {candidate}")

    if not args.dry_run:
        if output.exists() and not args.overwrite:
            raise RandomizeError(
                f"{output} already exists. Pass --overwrite to replace it, or choose "
                "another --output."
            )
        # Refused even with --overwrite: replacing a copy of the canonical image
        # would destroy a clean ROM, the one file this command exists to protect.
        if output.exists() and _is_canonical_copy(output, catalog):
            raise RandomizeError(
                f"{output} is a copy of the canonical ROM, so it is not replaced. "
                "Choose a different --output."
            )

    before = identify_rom(source, catalog)
    result = plan_enemy_randomization(
        source, catalog, args.seed, config,
        preset_name=args.preset, sdk_commit=_git_commit(),
    )

    if args.dry_run:
        print(json.dumps(result.manifest.to_json(), indent=2, sort_keys=True))
        print("\n# dry run: nothing was written", file=sys.stderr)
        return 0

    write_manifest = emit_image(source, output, result.plan)

    # Fail closed if the input moved under us: a run whose base changed mid-flight
    # is not reproducible, so its artefacts must not be presented as a result.
    after = identify_rom(source, catalog)
    if after.hashes.sha256 != before.hashes.sha256:
        raise RandomizeError(
            "the source ROM changed while it was being randomized, so the output "
            f"was not accepted. Delete {output} and retry with a ROM that is not "
            "being modified."
        )

    document = result.manifest.to_json()
    document["output"] = {
        "filename": output.name,
        "size": write_manifest.output_size,
        "sha256": write_manifest.output_sha256,
        "changed_byte_count": write_manifest.to_json()["changed_byte_count"],
    }
    document["rom"]["source_sha256"] = before.hashes.sha256
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(canonical_json(document), encoding="utf-8")

    if args.spoiler:
        spoiler = result.spoiler
        document_spoiler = SpoilerLog(
            master_seed=spoiler.master_seed,
            module_seeds=spoiler.module_seeds,
            profile_id=spoiler.profile_id,
            slots=spoiler.slots,
            stats=spoiler.stats,
        ).to_json()
        document_spoiler["output_sha256"] = write_manifest.output_sha256
        Path(args.spoiler).parent.mkdir(parents=True, exist_ok=True)
        Path(args.spoiler).write_text(canonical_json(document_spoiler), encoding="utf-8")

    _report(result, output, manifest_path, write_manifest)
    return 0


def _is_canonical_copy(path: Path, catalog) -> bool:
    """Whether ``path`` hashes to any canonical image in the catalog."""
    try:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return False
    for profile in catalog.profiles:
        if profile.sha256 and profile.sha256.lower() == digest:
            return True
    return False


def load_catalog_for(args):
    """The profile catalog this invocation should use.

    Imported here rather than at module scope: :mod:`tools.webfoot.cli` imports
    this module to register the subcommand, so a module-level import back into it
    would be circular.
    """
    from ..cli import load_catalog

    return load_catalog(getattr(args, "profiles", None))


def _report(result, output: Path, manifest_path: Path, write_manifest) -> None:
    types = result.types
    placement = result.placements
    stats = result.stats
    print(f"Randomized {output}")
    print(f"  seed          : {result.master_seed}")
    print(f"  output sha256 : {write_manifest.output_sha256}")
    print(f"  manifest      : {manifest_path}")
    if types:
        print(f"  enemy types   : {types.changed_count} slot(s) changed in "
              f"{types.groups_shuffled} map(s); pool {types.pool_size} canonical pairs")
    if placement:
        print(f"  placements    : {placement.moved_count} slot(s) moved in "
              f"{placement.groups_shuffled} map(s)")
    if stats:
        print(f"  stats         : {stats.randomized_records} enemy record(s) changed")
    summary = result.model.summary()
    print(f"  eligibility   : {summary['eligible']} of {summary['placements']} placements")
    print(f"  excluded      : {summary['refusal_counts']}")


def dispatch(args) -> int:
    """Run the command and translate every expected refusal into exit code 2.

    The CLI's other commands report a refusal as ``error: <message>`` on stderr
    and a non-zero status rather than a traceback, and this command follows that
    contract. Only the exception families a caller can actually trigger are
    caught; a genuine programmer error still escapes to the crash surface.
    """
    try:
        return run(args)
    except (RandomizeError, ConfigError, SeedError, EnemyRandomizerError,
            WriteError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def main(argv: list[str] | None = None) -> int:
    """Standalone entry point, so the command is testable without the full CLI."""
    parser = argparse.ArgumentParser(prog="webfoot randomize")
    subparsers = parser.add_subparsers(dest="command", required=True)
    add_parser(subparsers)
    args = parser.parse_args(["randomize", *(argv or [])])
    return dispatch(args)
