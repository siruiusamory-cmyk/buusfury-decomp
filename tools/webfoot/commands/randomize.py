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
    TYPING_MODES,
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
from ..randomizer.service import (
    default_manifest_path,
    default_spoiler_path,
    repository_commit,
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
        "--typing-mode",
        default=None,
        choices=sorted(TYPING_MODES),
        help=(
            "how the enemy-type module installs an identity. One mode exists: an "
            "identity is installed only onto a slot whose flags, behavior descriptor "
            "and children already match the donor's, so every resulting object is one "
            "a canonical placement holds. It does NOT change an enemy's TYPE and does "
            "not deliver ticket Module C. Every manifest records "
            "delivers_ticket_module_c: false, and the module's exact effect is stated "
            "in configuration.typing_mode_effect. See section 5.2 of "
            "docs/research/ENEMY_RANDOMIZER_VERIFICATION.md."
        ),
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
    typing_mode = base.typing_mode
    if getattr(args, "typing_mode", None) is not None:
        typing_mode = args.typing_mode
    return replace(
        base,
        enabled=frozenset(enabled),
        stat_fields=fields,
        stat_range=stat_range,
        typing_mode=typing_mode,
    )


def _filename_safe(seed: str) -> str:
    """A filename-safe rendering of the seed; the algorithm seed is untouched."""
    text = "".join(c if (c.isalnum() or c in " _-") else " " for c in str(seed))
    text = " ".join(text.split()).rstrip(". ")
    return (text[:64].strip().rstrip(". ")) or "seed"


def default_output(rom: Path, seed: str) -> Path:
    return rom.parent / OUTPUT_TEMPLATE.format(seed=_filename_safe(seed))


def _remove_existing(paths: list[Path], *, overwrite: bool) -> None:
    """Unlink the artefacts a confirmed overwrite replaces.

    Every refusal has already run over the whole set and the plan is built, so
    this is the point of no return. The image goes last, so a failure unlinking a
    companion cannot cost the caller the ROM it was replacing.

    The removal is duplicated from RandomizerService._remove_existing
    (randomizer/service.py:964) because the CLI cannot route through that service
    while the enemy-type registry gap stands; consolidate when it closes.
    """
    if not overwrite:
        return
    for path in reversed(paths):
        if not path.exists():
            continue
        try:
            path.unlink()
        except OSError as exc:
            raise RandomizeError(
                f"the existing {path} could not be replaced: {exc}"
            ) from exc


def _git_commit() -> str | None:
    """The commit this run came from, read from the one authority that owns it.

    RELEASE-ARTEFACT-001 removed a second ``git rev-parse`` that lived here: it
    answered the same question with its own process, from its own working
    directory, and with no baked-record fallback, so a frozen build would have
    reported a null commit through this path.
    """
    return repository_commit()


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
    # Refused rather than ignored. A dry run writes nothing by design, so asking
    # for a spoiler log during one is a request this command cannot honour; saying
    # so is better than exiting 0 with no spoiler log and no explanation.
    if args.dry_run and args.spoiler:
        raise RandomizeError(
            "--dry-run writes nothing, so --spoiler cannot be produced. Drop "
            "--dry-run to write the spoiler log, or drop --spoiler."
        )
    if args.dry_run and args.overwrite:
        raise RandomizeError("--overwrite has no meaning with --dry-run.")

    config = build_config(args)
    catalog = load_catalog_for(args)
    source = Path(args.rom)
    output = Path(args.output) if args.output else default_output(source, args.seed)

    if paths_are_the_same_file(source, output):
        raise RandomizeError(
            "the output is the input ROM; this command never writes to the ROM it "
            "reads. Choose a different --output."
        )

    # EVERY path this command will write is checked against the input and against
    # the output, not just the manifest. The spoiler log is the one that makes this
    # more than tidiness: it is written after the post-write source check, so a
    # spoiler aimed at the input would destroy the verified image with nothing
    # noticing. ROM_SAFETY.md forbids any write path reaching the input, and a
    # check covering some of them is not that rule.
    manifest_path = Path(args.manifest) if args.manifest else default_manifest_path(output)
    spoiler_path = Path(args.spoiler) if args.spoiler else None
    companion_spoiler = (
        spoiler_path if spoiler_path is not None else default_spoiler_path(output)
    )
    write_targets: list[tuple[Path, str]] = [
        (output, "output ROM"),
        (manifest_path, "manifest"),
        (companion_spoiler, "spoiler log"),
    ]

    for target, label in write_targets:
        if paths_are_the_same_file(target, source):
            raise RandomizeError(
                f"the {label} path is the input ROM, which this command never "
                f"writes: {target}"
            )
    # Two destinations that are the same file would silently destroy one result;
    # the manifest and the spoiler are separate documents and must stay separate.
    for index, (target, label) in enumerate(write_targets):
        for other, other_label in write_targets[index + 1:]:
            if paths_are_the_same_file(target, other):
                raise RandomizeError(
                    f"the {label} and the {other_label} are the same file "
                    f"({target}); choose different paths so neither result is lost."
                )

    if not args.dry_run:
        if output.exists() and not args.overwrite:
            raise RandomizeError(
                f"{output} already exists. Pass --overwrite to replace it, or choose "
                "another --output."
            )
        # Refused even with --overwrite: replacing a copy of the canonical image
        # would destroy a clean ROM, the one file this command exists to protect.
        #
        # This covers EVERY destination, not just the output. The manifest and the
        # spoiler take the same flag and are written by the same run, so a
        # destination aimed at a second clean copy of the canonical image would
        # have been replaced by JSON - the same loss the output guard exists to
        # prevent, through a different flag.
        for target, label in write_targets:
            if target.exists() and _is_canonical_copy(target, catalog):
                raise RandomizeError(
                    f"the {label} {target} is a copy of the canonical ROM, so it is "
                    f"not replaced. Choose another {label} path."
                )
        # The manifest and the spoiler follow the same policy as the image they
        # describe. Writing them over an existing file without confirmation while
        # the ROM itself needed --overwrite would let a run replace the recorded
        # provenance of a previous randomized ROM - the artefact that makes that
        # ROM reproducible.
        for target, label in write_targets[1:]:
            if target.exists() and not args.overwrite:
                raise RandomizeError(
                    f"the {label} {target} already exists. Pass --overwrite to "
                    f"replace it, or choose another {label} path."
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

    _remove_existing([path for path, _ in write_targets], overwrite=args.overwrite)

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

    if spoiler_path is not None:
        spoiler = result.spoiler
        # Reuse the result's own log rather than rebuilding it. An earlier revision
        # reconstructed the dataclass and dropped module_summaries on the floor, so
        # the file on disk always carried an empty "modules": {} block - and the test
        # that checks the spoiler agrees with the manifest was reading the in-memory
        # object, not the file, so it never caught it.
        document_spoiler = spoiler.to_json()
        document_spoiler["output_sha256"] = write_manifest.output_sha256
        spoiler_path.parent.mkdir(parents=True, exist_ok=True)
        spoiler_path.write_text(canonical_json(document_spoiler), encoding="utf-8")

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
        print(f"  identity swaps: {types.changed_count} slot(s) relocated within "
              f"identical-field groups in {types.groups_shuffled} map(s); "
              f"pool {types.pool_size} canonical pairs. This does NOT change enemy "
              f"types - Module C is undelivered.")
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
