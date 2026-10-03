"""The planner: one master seed in, one validated ``WritePlan`` out.
Module composition order
========================

The order is fixed and documented because future modules will depend on it::

    1. discover and classify eligible slots        (the shared model)
    2. shuffle enemy identities (type)             per map, canonical pairs
    3. shuffle placements                          per map, proven coordinates
    4. randomize stats                             per stat record
    5. merge each record's intended fields, encode once
    6. validate the whole semantic change set      one WritePlan, overlap-checked
    7. the normal writer emits the ROM

Steps 2 and 3 both rewrite fields of the *same* placement record, and they are
deliberately independent: step 2 reads only identity pairs and step 3 reads only
coordinates, so neither module's result depends on the other's. Their intents are
merged at step 5 and the record is encoded exactly once, which is what keeps them
from colliding as two overlapping overwrites of one object.

Stats come last because they are keyed by the *original* stat selector. Running
the type shuffle first does not disturb that: the selector recorded on a slot is
the one the retail image had, which is precisely the record whose values the
policy scales. A reader can therefore ask "what did this enemy's HP start at"
and get the pre-randomization number rather than one the type shuffle happened to
install somewhere.

The order is part of the reproducibility contract: the same master seed, image
and configuration must produce the same plan, and reordering the modules would
change every output. The focused determinism tests pin the whole plan's bytes, not
just each module's, so a reordering cannot pass unnoticed.

Seed derivation
===============

Each module draws from its own seed - ``sha256(master | seed | module_id)`` - so
enabling or disabling one module cannot perturb another. The warp module's seed
is derived too, and recorded, so a single master seed addresses a warp plus enemy
run without the two packs sharing a stream.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..entities import PlacementTypes
from ..map_transitions import read_map_transitions
from ..maps import Maps, load_maps
from ..placement_events import PlacementEvents
from ..profile import RomProfile, RomProfileCatalog
from ..rom import identify_rom
from ..stats import load_stat_tables, stat_tables_from_image
from ..write import WritePlan, plan_changes
from .config import EnemyRandomizerConfig
from .eligibility import SlotModel, build_slot_model, placements_in_door_triggers, scripted_placements
from .enemy_type import TypeOutcome, shuffle_enemy_types
from .manifest import RunManifest, SpoilerLog
from .placement import PlacementOutcome, shuffle_placements
from .records import RecordEdits, changes_for
from .seeds import (
    MODULE_ENEMY_PLACEMENT,
    MODULE_ENEMY_STAT,
    MODULE_ENEMY_TYPE,
    MODULE_WARP,
    Stream,
    derive_all_module_seeds,
    normalize_seed,
)
from .stats import StatOutcome, randomize_stats


class EnemyRandomizerError(ValueError):
    """The pack refused this run."""


@dataclass(frozen=True, slots=True)
class EnemyRandomization:
    """A finished plan plus everything a manifest and spoiler log need."""

    plan: WritePlan
    model: SlotModel
    types: TypeOutcome | None
    placements: PlacementOutcome | None
    stats: StatOutcome | None
    manifest: RunManifest
    spoiler: SpoilerLog
    master_seed: str
    module_seeds: dict[str, str]

    @property
    def changed_bytes(self) -> int:
        return sum(change.size for change in self.plan.changes)


def _derive_seeds(master_seed: str) -> dict[str, str]:
    return derive_all_module_seeds(master_seed)


def build_model(
    maps: Maps,
    *,
    with_events: bool = True,
) -> tuple[SlotModel, PlacementTypes]:
    """Classify every placement once, for every module to read.

    Split out from the planner so tests can exercise classification without
    running a full plan, and so the expensive event/transition reads happen in
    exactly one place per run.
    """
    types = PlacementTypes(maps)
    scripted: frozenset[PlacementIdentity] = frozenset()
    unresolved: frozenset[PlacementIdentity] | None = None
    if with_events:
        try:
            scripted, unresolved = scripted_placements(maps, PlacementEvents(maps))
        except Exception as exc:  # noqa: BLE001 - reported, never silently absorbed
            # A profile with no verified placement descriptor contract cannot
            # answer the script question at all. An earlier revision swallowed
            # this and carried on with an EMPTY scripted set, which silently
            # disabled the exclusion for every actor in the game while the
            # manifest still claimed scripted actors were refused.
            #
            # The honest response is neither to abort nor to pretend: the
            # exclusion could not be evaluated, so NO placement can be shown to be
            # free of a script, and every one of them is refused as unresolved
            # until the corpus can answer. That fails closed and names itself.
            unresolved = frozenset(p.identity for p in maps.placements())
            script_evidence_error: str | None = str(exc)
        else:
            script_evidence_error = None
    else:
        script_evidence_error = "event corpus not loaded (with_events=False)"
        unresolved = frozenset()
    door = placements_in_door_triggers(maps, read_map_transitions(maps.base_bytes, maps.profile))
    return build_slot_model(
        maps, types, scripted=scripted, unresolved_script=unresolved,
        door_slots=door, script_evidence_error=script_evidence_error,
    ), types


def plan_enemy_randomization(
    rom_path: str | Path,
    catalog: RomProfileCatalog,
    master_seed: str | int,
    config: EnemyRandomizerConfig,
    *,
    preset_name: str = "custom",
    sdk_commit: str | None = None,
) -> EnemyRandomization:
    """Plan one randomized run. Reads the ROM; writes nothing.

    A convenience wrapper that loads the image and then plans once. A caller that
    plans many seeds against one image should use
    :class:`EnemyRandomizerContext` instead: this function re-reads and re-hashes
    the whole 8 MiB image per call, which is most of its cost and is pure waste
    when the image cannot have changed.

    The canonical image is opened read-only by the loaders this composes, and the
    returned :class:`~tools.webfoot.write.WritePlan` is a pure description a
    caller applies with the one writer.
    """
    return EnemyRandomizerContext(rom_path, catalog).plan(
        master_seed, config, preset_name=preset_name, sdk_commit=sdk_commit
    )


class EnemyRandomizerContext:
    """One verified image, loaded once, planned against many times.

    Why this exists, measured. A single plan over the canonical 8 MiB image costs
    about 1.3 s, and the profile showed 5.65 s of an 11.8 s five-seed loop inside
    ``load_maps`` alone - of which 2.3 s was SHA-256 over the whole image. Every
    seed re-read and re-hashed bytes that could not have changed, because the
    randomizer is defined as read-only over a verified input. On a 1,000-seed
    corpus that is the difference between roughly 22 minutes and a few.

    What is cached and what is not is the whole design of this class:

    * **cached** - the ROM identification and its digests, the parsed map table
      and placement records, the transition corpus, and the scripted-placement
      sets. All of it is immutable data read from one image.
    * **NOT cached** - the stat table object, which carries the edits for a run,
      and the slot model, which is per-run state. Both are rebuilt per call, so
      two seeds cannot contaminate each other.

    Reproducibility is unchanged: :func:`plan_enemy_randomization` now routes
    through this class, so a corpus run and a single run execute the same plan
    body over the same data. The only difference is that the loading happens once.

    Input safety. The loader verifies the digest when it loads, and
    :meth:`_assert_source_unchanged` re-checks the file's identity cheaply on every
    later call, so an image edited mid-corpus is refused rather than silently
    planning against a base that no longer matches the recorded digest.
    """

    def __init__(self, rom_path: str | Path, catalog: RomProfileCatalog) -> None:
        self._path = Path(rom_path)
        self._catalog = catalog
        self._identification = identify_rom(self._path, catalog)
        profile: RomProfile | None = self._identification.profile_match.profile
        if profile is None:
            raise EnemyRandomizerError(
                "the selected image does not match a verified profile, so no "
                "placement or stat table can be trusted"
            )
        self._profile = profile
        self._maps = load_maps(self._path, catalog)
        # The transition corpus and the scripted sets do not depend on the seed or
        # the configuration, so they are read once here rather than per plan.
        self._door_slots = placements_in_door_triggers(
            self._maps, read_map_transitions(self._maps.base_bytes, self._maps.profile)
        )
        self._types = PlacementTypes(self._maps)
        try:
            self._scripted, self._unresolved = scripted_placements(
                self._maps, PlacementEvents(self._maps)
            )
            self._script_error: str | None = None
        except Exception as exc:  # noqa: BLE001 - reported, never silently absorbed
            # Same fail-closed response as build_model: if the script question
            # cannot be answered, no placement can be shown free of a script.
            self._scripted = frozenset()
            self._unresolved = frozenset(p.identity for p in self._maps.placements())
            self._script_error = str(exc)
        self._source_stat = self._path.stat()
        self._plans = 0

    @property
    def profile(self) -> RomProfile:
        return self._profile

    @property
    def maps(self):
        return self._maps

    @property
    def plans(self) -> int:
        """How many plans this context has produced."""
        return self._plans

    def _assert_source_unchanged(self) -> None:
        """Refuse if the image changed under us since it was loaded.

        A full re-hash per call would defeat the point of the cache, so this
        compares the filesystem identity tuple instead: device, inode, size and
        mtime. That catches a rewrite, a truncation and a replacement, which is
        everything that can change the bytes behind a path. ``identify_rom``
        already proved the digest at load time.
        """
        current = self._path.stat()
        before = self._source_stat
        if (current.st_dev, current.st_ino, current.st_size, current.st_mtime_ns) != (
            before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns
        ):
            raise EnemyRandomizerError(
                f"the source image changed after it was loaded: {self._path}. "
                "Build a new context so every plan is made against the image that "
                "was verified."
            )

    def _build_model(self):
        """A fresh slot model for one plan."""
        return build_slot_model(
            self._maps,
            self._types,
            scripted=self._scripted,
            unresolved_script=self._unresolved,
            door_slots=self._door_slots,
            script_evidence_error=self._script_error,
        ), self._types

    def plan(
        self,
        master_seed: str | int,
        config: EnemyRandomizerConfig,
        *,
        preset_name: str = "custom",
        sdk_commit: str | None = None,
    ) -> EnemyRandomization:
        """Plan one seed against the loaded image."""
        self._assert_source_unchanged()
        # The stat table carries per-run edits, so it is rebuilt rather than
        # shared. It is built from the image this context already identified and
        # holds in memory, which avoids a second full read plus a SHA-256 over
        # 8 MiB per plan - the remaining hot spot once the map load was cached.
        stat_tables = stat_tables_from_image(
            self._identification, self._profile, self._maps.base_bytes
        )
        self._plans += 1
        return _plan_with_loaded(
            maps=self._maps,
            stat_tables=stat_tables,
            identification=self._identification,
            profile=self._profile,
            model_factory=self._build_model,
            master_seed=master_seed,
            config=config,
            preset_name=preset_name,
            sdk_commit=sdk_commit,
        )


def _plan_with_loaded(
    *,
    maps,
    stat_tables,
    identification,
    profile,
    model_factory,
    master_seed: str | int,
    config: EnemyRandomizerConfig,
    preset_name: str,
    sdk_commit: str | None,
) -> EnemyRandomization:
    """The plan body, over an already-loaded image. No I/O of its own.

    Kept separate from loading so the expensive part can be done once for many
    seeds. ``model_factory`` builds a fresh slot model per call, because the model
    is per-run state (it carries the caches and the refusal set for THIS run) even
    though the placement records it reads are immutable.
    """
    text_seed = normalize_seed(master_seed)
    module_seeds = _derive_seeds(text_seed)

    model, _types = model_factory()
    edits = RecordEdits.empty()
    entries = {entry.identity: entry for entry in maps.placements()}

    types_outcome: TypeOutcome | None = None
    placement_outcome: PlacementOutcome | None = None
    stats_outcome: StatOutcome | None = None

    # --- step 2: enemy identities, per map, canonical pairs ---
    if config.wants(MODULE_ENEMY_TYPE):
        types_outcome = shuffle_enemy_types(
            model, Stream(module_seeds[MODULE_ENEMY_TYPE]), edits=edits
        )

    # --- step 3: placements, per map, proven coordinates ---
    if config.wants(MODULE_ENEMY_PLACEMENT):
        placement_outcome = shuffle_placements(
            model, Stream(module_seeds[MODULE_ENEMY_PLACEMENT]), entries=entries, edits=edits
        )

    # --- step 4: stats, keyed by the original selector ---
    if config.wants(MODULE_ENEMY_STAT):
        stats_outcome = randomize_stats(
            model, stat_tables, config, Stream(module_seeds[MODULE_ENEMY_STAT])
        )

    # --- step 5: merge intents, encode each edited record once ---
    changes = changes_for(entries, edits) + stat_tables.changes()

    # --- step 6: one plan, validated as a whole ---
    base = maps.base_bytes
    plan = plan_changes(
        base,
        changes,
        profile_id=profile.id,
        base_sha256=identification.hashes.sha256,
    )

    slot_summary = model.summary()
    module_summaries = {
        MODULE_ENEMY_TYPE: types_outcome.summary() if types_outcome else {"enabled": False},
        MODULE_ENEMY_PLACEMENT: (
            placement_outcome.summary() if placement_outcome else {"enabled": False}
        ),
        MODULE_ENEMY_STAT: stats_outcome.summary() if stats_outcome else {"enabled": False},
    }
    exclusions = {
        "policy": (
            "Only ORDINARY_COMBAT_ENEMY placements are randomized. A placement is "
            "refused when it carries a verified script event, when its type "
            "selector falls outside the verified enemy-stat extent, when its "
            "coordinates sit inside a transition trigger, or when it is the only "
            "eligible slot in its map."
        ),
        "actor_refusals": {
            key: value for key, value in model.refusal_counts().items()
            if key != "alone_in_map"
        },
        "scope_note": (
            "No boss, NPC or quest-critical classification exists in this project's "
            "evidence, so none is claimed. See the ticket audit for the residual."
        ),
    }

    spoiler = SpoilerLog(
        master_seed=text_seed,
        module_seeds=module_seeds,
        profile_id=profile.id,
        slots=_spoiler_slots(types_outcome, placement_outcome),
        stats=tuple(
            decision.to_json() for decision in (stats_outcome.decisions if stats_outcome else ())
        ),
    )

    manifest = RunManifest(
        master_seed=text_seed,
        module_seeds=module_seeds,
        profile_id=profile.id,
        profile_sha256=profile.sha256,
        sdk_commit=sdk_commit,
        preset=preset_name,
        configuration=config.to_json(),
        slot_summary=slot_summary,
        module_summaries=module_summaries,
        exclusions=exclusions,
        source_rom_sha256=identification.hashes.sha256,
        # Filled by the writer once the image exists; a plan does not hash its own
        # output because it has not produced one yet.
        output_rom_sha256="",
        output_rom_size=len(base),
        changed_byte_count=sum(change.size for change in plan.changes),
    )

    return EnemyRandomization(
        plan=plan,
        model=model,
        types=types_outcome,
        placements=placement_outcome,
        stats=stats_outcome,
        manifest=manifest,
        spoiler=spoiler,
        master_seed=text_seed,
        module_seeds=module_seeds,
    )


def _spoiler_slots(
    types: TypeOutcome | None, placements: PlacementOutcome | None
) -> tuple[dict, ...]:
    """One spoiler row per slot, joining the identity and placement decisions.

    The join is by placement identity, never by position in either list, so a
    module being disabled produces rows with that half absent rather than
    misaligned rows.
    """
    rows: dict[str, dict] = {}
    if types is not None:
        for decision in types.decisions:
            row = rows.setdefault(decision.placement, {"placement": decision.placement,
                                                       "map": f"map:{decision.map_index:04d}"})
            row["original_enemy"] = decision.original.display
            row["randomized_enemy"] = decision.randomized.display
            row["enemy_changed"] = decision.changed
    if placements is not None:
        for decision in placements.decisions:
            row = rows.setdefault(decision.placement, {"placement": decision.placement,
                                                       "map": f"map:{decision.map_index:04d}"})
            row["original_position"] = {"x": decision.original[0], "y": decision.original[1]}
            row["randomized_position"] = {"x": decision.randomized[0], "y": decision.randomized[1]}
            row["position_changed"] = decision.moved
    return tuple(rows[key] for key in sorted(rows))


#: Re-exported so a caller does not have to guess the warp module id.
WARP_MODULE = MODULE_WARP
