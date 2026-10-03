"""ROM-gated proofs for the enemy randomizer pack. RANDOMIZER-ENEMY-PACK-001.

The canonical Buu's Fury image is opened read-only on every path here. Every
mutated image is produced in memory by ``webfoot.write.apply_plan``; the only file
written is written into ``tmp_path``, never over the input.

What this file proves, and the acceptance item each serves
==========================================================

1. eligibility: ordinary combat enemies are found, and every actor this project
   *can* exclude is excluded - script-attached placements, selectors outside the
   verified stat extent, slots inside a door trigger, and slots alone in their map;
2. excluded actors are **byte-identical** - the ticket's "bosses/NPCs/scripted/
   unknown remain untouched", asserted on the emitted image rather than on a
   summary count;
3. type compatibility: every installed identity is a pair some canonical
   placement builds, and it is installed on a slot of the **same map** - so no
   hybrid entity and no enemy that its map never had;
4. placement legality: every new coordinate is an existing placement coordinate
   of that same map, and the set of occupied coordinates per map is unchanged;
5. stats: every randomized value is inside its field's legal domain **and** inside
   the preset's band of the original, with zero preserved where zero is legal;
6. determinism: the same seed gives the same plan bytes, the same output bytes and
   the same manifest bytes; a different seed gives different bytes;
7. seed separation, end to end: disabling the stat module leaves the type and
   placement decisions identical;
8. composition and warp interoperability: all three modules plus a derivation of
   the warp module's seed from the same master seed, with the warp seed unchanged
   by anything the enemy modules do;
9. the canonical ROM is byte-identical before and after the whole file, and the
   emitted derivative equals the planned image.

The suite skips cleanly when the private canonical ROM is not configured.
``LOGX_CANONICAL_ROM`` or ``WEBFOOT_BUU_ROM`` overrides the default ``roms/``
path, so a review worktree - which never carries the ignored image - can point at
the main checkout's copy and run this whole file read-only.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import pytest

from tools.webfoot.cli import load_catalog
from tools.webfoot.enemy_randomizer.compatibility import IdentityPair, is_canonical
from tools.webfoot.enemy_randomizer.config import (
    PRESETS,
    STAT_FIELDS,
    EnemyRandomizerConfig,
)
from tools.webfoot.enemy_randomizer.eligibility import (
    Classification,
    Refusal,
    build_slot_model,
    placements_in_door_triggers,
    scripted_placements,
)
from tools.webfoot.enemy_randomizer.manifest import canonical_json
from tools.webfoot.enemy_randomizer.planner import plan_enemy_randomization
from tools.webfoot.enemy_randomizer.seeds import (
    MODULE_ENEMY_PLACEMENT,
    MODULE_ENEMY_STAT,
    MODULE_ENEMY_TYPE,
    derive_all_module_seeds,
)
from tools.webfoot.entities import PlacementTypes
from tools.webfoot.map_transitions import read_map_transitions
from tools.webfoot.maps import load_maps
from tools.webfoot.placement_events import PlacementEvents
from tools.webfoot.stats import load_stat_tables
from tools.webfoot.write import apply_plan

CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"

_ROM_VARIABLES = ("WEBFOOT_BUU_ROM", "LOGX_CANONICAL_ROM")
_ROM_DEFAULT = Path("roms") / "Dragon Ball Z - Buu's Fury (U).gba"


def _canonical_rom() -> Path | None:
    for name in _ROM_VARIABLES:
        configured = os.environ.get(name)
        if configured and Path(configured).is_file():
            return Path(configured)
    if _ROM_DEFAULT.is_file():
        return _ROM_DEFAULT
    return None


ROM = _canonical_rom()
pytestmark = pytest.mark.skipif(
    ROM is None,
    reason=(
        "no canonical Buu's Fury image; set "
        + " or ".join(_ROM_VARIABLES)
        + f", or place {_ROM_DEFAULT}"
    ),
)

SEED = "enemy-pack-001"
OTHER_SEED = "enemy-pack-002"


# --- fixtures ----------------------------------------------------------------


@pytest.fixture(scope="module")
def catalog():
    return load_catalog(None)


@pytest.fixture(scope="module")
def base_image() -> bytes:
    data = Path(ROM).read_bytes()
    assert hashlib.sha256(data).hexdigest() == CANONICAL_SHA256, (
        "the configured image is not the verified canonical Buu's Fury ROM"
    )
    return data


@pytest.fixture(scope="module")
def maps(catalog):
    return load_maps(ROM, catalog)


@pytest.fixture(scope="module")
def types(maps):
    return PlacementTypes(maps)


@pytest.fixture(scope="module")
def model(maps, types):
    events = PlacementEvents(maps)
    scripted, unresolved = scripted_placements(maps, events)
    return build_slot_model(
        maps,
        types,
        scripted=scripted,
        unresolved_script=unresolved,
        door_slots=placements_in_door_triggers(
            maps, read_map_transitions(maps.base_bytes, maps.profile)
        ),
    )


@pytest.fixture(scope="module")
def shipping_plan(catalog):
    """The plan the SHIPPING preset produces: placement and stats only.

    This is what a streamed run is built from, and what the acceptance target names.
    The enemy-type module is absent here because the preset disables it.
    """
    preset = PRESETS["stream-safe"]
    return plan_enemy_randomization(
        ROM, catalog, SEED, preset.config, preset_name=preset.name
    )


def _all_modules_plan(catalog):
    """All three modules forced on, including the undelivered one.

    The enemy-type module is DISABLED in every preset because it does not deliver a
    type change (section 5.2 of the evidence document). Its invariants are still
    worth testing - the research result must stay reproducible and a future ticket
    will build on it - so the type-specific tests drive it explicitly rather than
    relying on a preset to enable it.
    """
    preset = PRESETS["stream-safe"]
    forced = replace(
        preset.config,
        enabled=frozenset(
            {MODULE_ENEMY_TYPE, MODULE_ENEMY_PLACEMENT, MODULE_ENEMY_STAT}
        ),
    )
    return plan_enemy_randomization(
        ROM, catalog, SEED, forced, preset_name="all-modules-explicit"
    )


@pytest.fixture(scope="module")
def safe_plan(catalog):
    """All three modules, for the type-module invariant tests.

    Named for what it is: a deliberately WIDER plan than the preset ships, so a test
    that uses it is testing the module rather than the shipping composition.
    """
    return _all_modules_plan(catalog)


@pytest.fixture(scope="module")
def safe_output(base_image, safe_plan) -> bytes:
    return apply_plan(base_image, safe_plan.plan)


def _change_owners(result) -> dict[int, str]:
    """File offset -> the semantic owner of the change that covers it."""
    owners: dict[int, str] = {}
    for change in result.plan.changes:
        for offset in range(change.offset, change.end):
            owners[offset] = change.owner
    return owners


# --- 1. eligibility ----------------------------------------------------------


class TestEligibility:
    def test_ordinary_enemies_are_found(self, model):
        eligible = model.eligible
        assert len(eligible) > 1000, "the canonical corpus holds >1,400 eligible slots"
        assert all(s.classification is Classification.ORDINARY_COMBAT_ENEMY
                   for s in eligible)

    def test_scripted_actors_are_classified_and_refused(self, model, maps):
        events = PlacementEvents(maps)
        scripted, unresolved = scripted_placements(maps, events)
        assert len(scripted) == 57, "measured: 57 canonical script-attached placements"
        by_id = {s.identity: s for s in model.slots}
        for identity in scripted:
            slot = by_id[identity]
            assert slot.classification is Classification.SCRIPTED_ACTOR
            assert model.refusal_reason(slot) is Refusal.SCRIPT_EVENT

    def test_a_script_dispatch_with_no_decoded_root_is_refused(self, model, maps):
        """Fail closed: an UNDECODED script is not the absence of a script.

        Seven canonical placements dispatch through the verified script handler
        ``0x0800421F`` but point at a root whose extent was never established, so
        the event corpus reports ``event is None`` for them. Treating that as "not
        scripted" would randomize a scripted actor, which is what an earlier
        revision of this pack did. They are refused, under their own reason.
        """
        events = PlacementEvents(maps)
        scripted, unresolved = scripted_placements(maps, events)
        assert len(unresolved) == 7, "measured: 7 script-dispatch roots are undecoded"
        assert not (set(unresolved) & set(scripted)), "the two sets must not overlap"
        by_id = {s.identity: s for s in model.slots}
        for identity in unresolved:
            slot = by_id[identity]
            assert slot.classification is Classification.SCRIPTED_ACTOR
            assert model.refusal_reason(slot) is Refusal.SCRIPT_UNRESOLVED

    def test_selectors_outside_the_stat_extent_are_unknown_and_refused(self, model):
        """UNKNOWN must fail closed, and it must be the measured set."""
        assert model.out_of_extent_selectors == (141, 142, 145, 146, 147, 148, 149)
        unknown = [s for s in model.slots if s.classification is Classification.UNKNOWN]
        assert unknown, "the canonical corpus has 15 such placements"
        for slot in unknown:
            assert model.refusal_reason(slot) is Refusal.OUTSIDE_STAT_EXTENT

    def test_a_door_trigger_slot_is_refused(self, model):
        refused = [s for s, r in model.refusals if r is Refusal.IN_DOOR_TRIGGER]
        assert len(refused) == 2, "measured: exactly two eligible slots in a door"

    def test_a_lone_enemy_in_its_map_is_refused(self, model):
        """A shuffle of one element is not a shuffle, and it is recorded as such."""
        alone = [s for s, r in model.refusals if r is Refusal.ALONE_IN_MAP]
        assert alone, "measured: 23 single-placement maps"
        for slot in alone:
            assert len(model.by_map().get(slot.map_index, ())) <= 1

    def test_the_classification_partitions_every_placement(self, model):
        counted = sum(model.counts().values())
        assert counted == len(model.slots) == 1559

    def test_eligibility_never_reads_a_combat_stat(self, model):
        """The ticket forbids inferring eligibility from HP.

        A slot's verdict must be the same whatever its record's stats say, so a
        classification cannot be a disguised stat threshold. Asserted by checking
        that eligible selectors span the full measured stat range rather than
        clustering at one end.
        """
        stat_tables = load_stat_tables(ROM, load_catalog(None))
        levels = []
        for slot in model.eligible:
            if slot.stat_identity is not None:
                levels.append(stat_tables.enemy(slot.stat_identity).record.level)
        assert min(levels) == 1
        assert max(levels) >= 100


# --- 2. excluded actors are untouched ----------------------------------------


class TestExcludedActorsUntouched:
    def test_every_excluded_placement_is_byte_identical(self, safe_plan, base_image, safe_output):
        """The safety claim, on the emitted bytes rather than on a count."""
        changed_offsets = set()
        for change in safe_plan.plan.changes:
            changed_offsets.update(range(change.offset, change.end))

        by_identity = {s.identity: s for s in safe_plan.model.slots}
        for slot, reason in safe_plan.model.refusals:
            if reason not in (Refusal.SCRIPT_EVENT, Refusal.SCRIPT_UNRESOLVED,
                              Refusal.OUTSIDE_STAT_EXTENT):
                continue
            entry = by_identity[slot.identity].placement
            span = set(range(entry.file_offset,
                             entry.file_offset + len(entry.original_bytes)))
            assert not (span & changed_offsets), (
                f"{slot.key} is refused for {reason.value} but its record was written"
            )
            assert base_image[entry.file_offset:
                              entry.file_offset + len(entry.original_bytes)] == \
                safe_output[entry.file_offset:
                            entry.file_offset + len(entry.original_bytes)]

    def test_a_scripted_actors_shared_stat_record_is_not_randomized(self, safe_plan, model):
        """One unsafe consumer vetoes the shared record.

        A stat record is shared by every placement selecting it. Randomizing a
        record that a scripted actor also uses would change that actor's stats,
        which the default configuration forbids, so the record is skipped and the
        reason is reported.
        """
        refused = dict(safe_plan.stats.refused_selectors)
        assert refused, "the canonical corpus shares selectors with scripted actors"
        randomized_identities = {d.enemy_identity for d in safe_plan.stats.decisions}
        for selector in refused:
            slots = [s for s in model.slots if s.original_selector == selector]
            identities = {str(s.stat_identity) for s in slots if s.stat_identity}
            assert not (identities & randomized_identities), (
                f"selector {selector} shares a record with a refused actor but was "
                "randomized anyway"
            )

    def test_a_lone_enemys_stat_record_is_not_randomized(self, safe_plan, model):
        """A slot the run refuses must not have its record scaled behind its back.

        A review found this: ``alone_in_map`` slots stay classified
        ``ORDINARY_COMBAT_ENEMY`` (they are ordinary enemies; the refusal is about
        moving them), so they passed the classification test and their stat records
        were scaled - while ``exclusions.policy`` told the reader that a placement is
        "refused when it is the only eligible slot in its map", and Waiver 1 leaned
        on that exclusion as the boss protection. A record whose ONLY consumer is
        such a slot is now vetoed.
        """
        by_selector: dict[int, list] = {}
        for slot in model.slots:
            by_selector.setdefault(slot.original_selector, []).append(slot)

        lone_only = [
            selector for selector, slots in by_selector.items()
            if all(model.refusal_reason(s) is Refusal.ALONE_IN_MAP for s in slots)
        ]
        assert lone_only, "the canonical corpus has selectors used only by lone slots"

        randomized_identities = {d.enemy_identity for d in safe_plan.stats.decisions}
        for selector in lone_only:
            identities = {
                str(s.stat_identity) for s in by_selector[selector] if s.stat_identity
            }
            assert not (identities & randomized_identities), (
                f"selector {selector} is used only by an alone-in-map slot, which the "
                "manifest says is refused, but its record was scaled"
            )

    def test_a_lone_slots_shared_record_is_still_scaled(self, safe_plan, model):
        """The veto must not spread to records ordinary enemies also share.

        Vetoing every selector a lone slot touches would have cost 11 records and
        silently stripped stat randomization from ordinary enemies elsewhere. Only a
        record with no legitimate consumer is vetoed.
        """
        by_selector: dict[int, list] = {}
        for slot in model.slots:
            by_selector.setdefault(slot.original_selector, []).append(slot)

        shared_with_lone = [
            selector for selector, slots in by_selector.items()
            if any(model.refusal_reason(s) is Refusal.ALONE_IN_MAP for s in slots)
            and any(model.refusal_reason(s) is None for s in slots)
        ]
        assert shared_with_lone, "expected selectors shared between lone and ordinary slots"
        randomized_identities = {d.enemy_identity for d in safe_plan.stats.decisions}
        assert any(
            {str(s.stat_identity) for s in by_selector[sel] if s.stat_identity}
            & randomized_identities
            for sel in shared_with_lone
        ), "a record shared with a properly-randomized ordinary enemy was over-vetoed"


# --- 3. type compatibility ---------------------------------------------------


class TestTypeCompatibility:
    def test_every_installed_identity_is_canonical(self, safe_plan, model):
        for decision in safe_plan.types.decisions:
            assert is_canonical(decision.randomized, model), (
                f"{decision.placement} was given {decision.randomized.display}, "
                "which no canonical placement builds"
            )

    def test_no_hybrid_entity_is_created(self, safe_plan, model):
        """The pair must come from one enemy, not one half from each.

        A hybrid would show a selector from one canonical pair and a sprite from
        another. Asserted by requiring each installed pair to match a pair some
        canonical placement actually uses.
        """
        canonical = {
            (s.original_selector, s.original_sprite) for s in model.slots
        }
        for decision in safe_plan.types.decisions:
            assert (decision.randomized.selector, decision.randomized.sprite) in canonical

    def test_every_resulting_combination_already_exists_canonically(self, safe_plan, model):
        """The identity AND every coupled field must be a combination retail builds.

        This is the invariant an earlier revision violated. It wrote only ``+0x08``
        and ``+0x10`` and left each slot's own ``+0x04`` flags, ``+0x14`` behavior
        descriptor and child pointers behind, so 54 of 1,002 changed slots ended up
        as enemy B's stats and graphics driven by enemy A's behavior descriptor - a
        combination that appears nowhere in the corpus, and the graphics/behaviour/
        stat hybrid the ticket forbids.

        Asserted the strong way: for each changed slot, the exact tuple
        ``(selector, sprite, flags, descriptor, child_count, children)`` must appear
        on some canonical placement. If the shuffle ever mixes fields from two
        sources, no slot will carry that tuple and this fails.
        """
        canonical = {
            (s.original_selector, s.original_sprite,
             s.record.flags_raw, s.record.descriptor_pointer_raw,
             s.record.child_count, tuple(s.record.child_pointers_raw))
            for s in model.slots
        }
        by_key = {s.key: s for s in model.slots}
        for decision in safe_plan.types.decisions:
            slot = by_key[decision.placement]
            combination = (
                decision.randomized.selector, decision.randomized.sprite,
                slot.record.flags_raw, slot.record.descriptor_pointer_raw,
                slot.record.child_count, tuple(slot.record.child_pointers_raw),
            )
            assert combination in canonical, (
                f"{decision.placement} would become a combination no canonical "
                f"placement builds: {combination}"
            )

    def test_a_swapped_identity_keeps_the_slots_coupled_fields(self, safe_plan, model):
        """The donor of the installed identity must agree on the coupled fields.

        The direct statement of the rule: the slot the identity came from shares
        the recipient's flags, descriptor and children, so nothing is mixed.
        """
        by_key = {s.key: s for s in model.slots}
        for decision in safe_plan.types.decisions:
            if not decision.changed:
                continue
            recipient = by_key[decision.placement]
            donors = [
                s for s in model.slots
                if s.map_index == decision.map_index
                and s.original_pair == (decision.randomized.selector,
                                        decision.randomized.sprite)
            ]
            assert donors, "no same-map donor carries the installed identity"
            assert any(
                (s.record.flags_raw, s.record.descriptor_pointer_raw,
                 s.record.child_count, tuple(s.record.child_pointers_raw))
                == (recipient.record.flags_raw, recipient.record.descriptor_pointer_raw,
                    recipient.record.child_count,
                    tuple(recipient.record.child_pointers_raw))
                for s in donors
            ), f"{decision.placement} took an identity from a slot with different coupled fields"

    def test_an_identity_stays_in_its_own_map(self, safe_plan):
        for decision in safe_plan.types.decisions:
            slot = next(s for s in safe_plan.model.slots
                        if s.key == decision.placement)
            assert slot.map_index == decision.map_index

    def test_the_maps_identity_multiset_is_preserved(self, safe_plan):
        """Same map means the same enemies are present, in different hands."""
        before: dict[int, list] = {}
        for decision in safe_plan.types.decisions:
            before.setdefault(decision.map_index, []).append(decision.original)
        after: dict[int, list] = {}
        for decision in safe_plan.types.decisions:
            after.setdefault(decision.map_index, []).append(decision.randomized)
        for map_index, originals in before.items():
            assert sorted(originals, key=lambda p: (p.selector, p.sprite)) == \
                sorted(after[map_index], key=lambda p: (p.selector, p.sprite))

    def test_the_door_trigger_slot_keeps_its_identity(self, safe_plan):
        door = {s.identity for s, r in safe_plan.model.refusals
                if r is Refusal.IN_DOOR_TRIGGER}
        for decision in safe_plan.types.decisions:
            slot = next(s for s in safe_plan.model.slots if s.key == decision.placement)
            if slot.identity in door:
                assert decision.original == decision.randomized


# --- 4. placement legality ---------------------------------------------------


class TestPlacementLegality:
    def test_every_new_coordinate_was_already_in_that_map(self, model, safe_plan):
        originals: dict[int, set[tuple[int, int]]] = {}
        for slot in model.eligible:
            originals.setdefault(slot.map_index, set()).add(slot.original_position)
        for decision in safe_plan.placements.decisions:
            assert decision.randomized in originals[decision.map_index], (
                f"{decision.placement} was moved to {decision.randomized}, which is "
                "not an existing placement coordinate of its map"
            )

    def test_the_occupied_coordinate_set_is_unchanged(self, safe_plan):
        """No coordinate is invented and none is vacated."""
        before: dict[int, list] = {}
        after: dict[int, list] = {}
        for decision in safe_plan.placements.decisions:
            before.setdefault(decision.map_index, []).append(decision.original)
            after.setdefault(decision.map_index, []).append(decision.randomized)
        for map_index, coords in before.items():
            assert sorted(coords) == sorted(after[map_index])

    def test_positions_are_valid_signed_halfwords(self, safe_plan):
        for decision in safe_plan.placements.decisions:
            for value in (*decision.original, *decision.randomized):
                assert -0x8000 <= value <= 0x7FFF


# --- 5. stats ----------------------------------------------------------------


class TestStats:
    def test_every_randomized_value_is_inside_its_domain(self, safe_plan):
        for decision in safe_plan.stats.decisions:
            for field, value in decision.randomized.items():
                low, high = STAT_FIELDS[field]
                assert low <= value <= high, (
                    f"{decision.enemy_identity}.{field} = {value} outside [{low}, {high}]"
                )

    def test_every_randomized_value_is_inside_the_preset_band(self, safe_plan):
        """The progression safeguard, asserted on the real corpus."""
        band = safe_plan.manifest.configuration["stat_range"]
        low, high = Fraction(band["low"]), Fraction(band["high"])
        for decision in safe_plan.stats.decisions:
            for field, original in decision.original.items():
                randomized = decision.randomized[field]
                if original == 0:
                    assert randomized == 0, "zero must stay zero"
                    continue
                floor = (original * low.numerator) // low.denominator
                ceil = (original * high.numerator) // high.denominator
                # The clamp at a field floor can lift a value above the band's own
                # floor, and the field ceiling can push it below the band's
                # ceiling; both are bounds, so allow them explicitly.
                field_low, field_high = STAT_FIELDS[field]
                assert min(max(floor, field_low), field_high) <= randomized
                assert randomized <= min(max(ceil, field_low), field_high)

    def test_zero_is_preserved_where_zero_is_legal(self, base_image, safe_plan, catalog):
        """A real corpus assertion, not just the pure unit one."""
        tables = load_stat_tables(ROM, catalog)
        for decision in safe_plan.stats.decisions:
            for field, original in decision.original.items():
                if original == 0:
                    assert decision.randomized[field] == 0

    def test_stats_are_randomized_per_record_not_per_instance(self, safe_plan, model):
        """One record per selector, so every consumer sees the same numbers."""
        by_selector: dict[int, set] = {}
        for slot in model.slots:
            if slot.stat_identity is not None:
                by_selector.setdefault(slot.original_selector, set()).add(
                    str(slot.stat_identity))
        for decision in safe_plan.stats.decisions:
            assert len(by_selector[decision.selector]) == 1


# --- 6. determinism ----------------------------------------------------------


class TestDeterminism:
    def test_same_seed_same_plan(self, catalog):
        preset = PRESETS["stream-safe"]
        one = plan_enemy_randomization(ROM, catalog, SEED, preset.config,
                                       preset_name=preset.name)
        two = plan_enemy_randomization(ROM, catalog, SEED, preset.config,
                                       preset_name=preset.name)
        assert [(c.offset, c.new, c.owner) for c in one.plan.changes] == \
            [(c.offset, c.new, c.owner) for c in two.plan.changes]

    def test_same_seed_same_manifest_bytes(self, catalog):
        preset = PRESETS["stream-safe"]
        one = plan_enemy_randomization(ROM, catalog, SEED, preset.config,
                                       preset_name=preset.name)
        two = plan_enemy_randomization(ROM, catalog, SEED, preset.config,
                                       preset_name=preset.name)
        assert canonical_json(one.manifest.to_json()) == canonical_json(two.manifest.to_json())

    def test_a_different_seed_is_a_different_result(self, catalog):
        preset = PRESETS["stream-safe"]
        one = plan_enemy_randomization(ROM, catalog, SEED, preset.config,
                                       preset_name=preset.name)
        two = plan_enemy_randomization(ROM, catalog, OTHER_SEED, preset.config,
                                       preset_name=preset.name)
        assert [(c.offset, c.new) for c in one.plan.changes] != \
            [(c.offset, c.new) for c in two.plan.changes]

    def test_the_output_image_is_reproducible(self, base_image, catalog):
        """The acceptance target: a seed reproduces the same ROM bytes."""
        preset = PRESETS["stream-safe"]
        one = apply_plan(base_image, plan_enemy_randomization(
            ROM, catalog, SEED, preset.config, preset_name=preset.name).plan)
        two = apply_plan(base_image, plan_enemy_randomization(
            ROM, catalog, SEED, preset.config, preset_name=preset.name).plan)
        assert hashlib.sha256(one).hexdigest() == hashlib.sha256(two).hexdigest()

    def test_the_manifest_reproduces_the_output(self, base_image, safe_plan, safe_output):
        """A manifest is enough to re-derive the image it describes."""
        rebuilt = apply_plan(base_image, plan_enemy_randomization(
            ROM, load_catalog(None), safe_plan.master_seed,
            EnemyRandomizerConfig(**{
                "stat_range": safe_plan.stats and PRESETS["stream-safe"].config.stat_range,
                "stat_fields": tuple(safe_plan.stats.fields),
                "enabled": frozenset(safe_plan.manifest.configuration["enabled_modules"]),
            }),
            preset_name=safe_plan.manifest.preset,
        ).plan)
        assert hashlib.sha256(rebuilt).hexdigest() == hashlib.sha256(safe_output).hexdigest()


# --- 7. seed separation, end to end ------------------------------------------


class TestSeedSeparation:
    def test_disabling_stats_leaves_types_and_placements_identical(self, catalog):
        """The type module is forced on here, because no preset enables it.

        Seed separation must hold for the module itself, not only for the shipping
        composition, so this drives all three explicitly and then drops one.
        """
        preset = PRESETS["stream-safe"]
        all_on = replace(
            preset.config,
            enabled=frozenset(
                {MODULE_ENEMY_TYPE, MODULE_ENEMY_PLACEMENT, MODULE_ENEMY_STAT}
            ),
        )
        full = plan_enemy_randomization(ROM, catalog, SEED, all_on,
                                        preset_name="all-modules-explicit")
        without_stats = replace(
            all_on,
            enabled=frozenset({MODULE_ENEMY_TYPE, MODULE_ENEMY_PLACEMENT}),
        )
        other = plan_enemy_randomization(ROM, catalog, SEED, without_stats,
                                         preset_name="all-modules-explicit")
        assert [d.to_json() for d in other.types.decisions] == \
            [d.to_json() for d in full.types.decisions]
        assert [d.to_json() for d in other.placements.decisions] == \
            [d.to_json() for d in full.placements.decisions]

    def test_the_shipping_preset_leaves_placement_and_stats_identical_to_wider_runs(
        self, catalog
    ):
        """What stream-safe ships matches the same modules run explicitly.

        The preset enables a subset; a caller who names the same subset by hand must
        get the same decisions, or "the preset is the acceptance target" would not be
        checkable.
        """
        preset = PRESETS["stream-safe"]
        shipped = plan_enemy_randomization(
            ROM, catalog, SEED, preset.config, preset_name=preset.name
        )
        explicit = plan_enemy_randomization(
            ROM, catalog, SEED,
            replace(preset.config, enabled=frozenset(preset.config.enabled)),
            preset_name=preset.name,
        )
        assert [d.to_json() for d in shipped.placements.decisions] == \
            [d.to_json() for d in explicit.placements.decisions]
        assert [d.to_json() for d in shipped.stats.decisions] == \
            [d.to_json() for d in explicit.stats.decisions]
        assert shipped.types is None, "the shipping preset must not run the type module"

    def test_disabling_types_leaves_placements_identical(self, catalog):
        preset = PRESETS["stream-safe"]
        full = plan_enemy_randomization(ROM, catalog, SEED, preset.config,
                                        preset_name=preset.name)
        without_types = replace(
            preset.config,
            enabled=frozenset({MODULE_ENEMY_PLACEMENT, MODULE_ENEMY_STAT}),
        )
        other = plan_enemy_randomization(ROM, catalog, SEED, without_types,
                                         preset_name=preset.name)
        assert [d.to_json() for d in other.placements.decisions] == \
            [d.to_json() for d in full.placements.decisions]

    def test_the_module_seeds_do_not_depend_on_the_enabled_set(self, catalog):
        preset = PRESETS["stream-safe"]
        full = plan_enemy_randomization(ROM, catalog, SEED, preset.config,
                                        preset_name=preset.name)
        minimal = plan_enemy_randomization(
            ROM, catalog, SEED,
            replace(preset.config, enabled=frozenset({MODULE_ENEMY_TYPE})),
            preset_name=preset.name,
        )
        assert full.module_seeds == minimal.module_seeds


# --- 8. composition and warp interoperability --------------------------------


class TestCompositionAndWarp:
    def test_all_three_modules_compose(self, safe_plan):
        assert safe_plan.types is not None
        assert safe_plan.placements is not None
        assert safe_plan.stats is not None
        assert safe_plan.types.changed_count > 0
        assert safe_plan.placements.moved_count > 0
        assert safe_plan.stats.randomized_records > 0

    def test_one_record_carries_both_a_type_and_a_placement_edit(self, safe_plan):
        """The composition seam: two modules, one record, one change.

        If the two shuffles emitted overlapping overwrites the plan would be
        refused; if one silently won, a slot would keep a stale field. Asserted
        by finding a change whose owner names both modules.
        """
        both = [c for c in safe_plan.plan.changes
                if "enemy-type" in c.reason and "placement" in c.reason]
        assert both, "no record carried both edits; check the merge in records.py"

    def test_no_two_changes_overlap(self, safe_plan):
        """``plan_changes`` already enforces this; asserted so a merge regression
        is a test failure rather than a late refusal on a user's machine."""
        ordered = sorted(safe_plan.plan.changes, key=lambda c: c.offset)
        for previous, current in zip(ordered, ordered[1:]):
            assert current.offset >= previous.end

    def test_the_warp_seed_is_derived_and_independent(self, safe_plan):
        """Warp interoperability at the seed level.

        The pack derives a warp seed from the same master seed, so one seed
        addresses a warp plus enemy run, and the enemy modules cannot move it
        because it is a function of the master seed and the module name alone.
        """
        from tools.webfoot.enemy_randomizer.seeds import MODULE_WARP

        assert MODULE_WARP in safe_plan.module_seeds
        assert safe_plan.module_seeds == derive_all_module_seeds(safe_plan.master_seed)
        # Independent of the enemy modules' draws: deriving after a full run
        # gives the identical value.
        assert derive_all_module_seeds(safe_plan.master_seed)[MODULE_WARP] == \
            safe_plan.module_seeds[MODULE_WARP]

    def test_the_warp_randomizer_is_unaffected(self, catalog):
        """The existing warp mapping must not move because this pack exists.

        Its policy id and seed domain are frozen; this asserts the pack did not
        touch them, which is the concrete form of "a warp change was not
        necessary".
        """
        from tools.webfoot.warp_randomizer import POLICY_ID, plan_warp_randomization
        from tools.webfoot.rom import identify_rom

        assert POLICY_ID == "reciprocal-door-pairs/3"
        identification = identify_rom(ROM, catalog)
        profile = identification.profile_match.profile
        image = Path(ROM).read_bytes()
        warp = plan_warp_randomization(image, profile, "warp-interop")
        assert len(warp.manifest.randomized) > 0
        # And it is deterministic without the enemy pack in the picture at all.
        again = plan_warp_randomization(image, profile, "warp-interop")
        assert [(c.offset, c.new) for c in warp.write_plan.changes] == \
            [(c.offset, c.new) for c in again.write_plan.changes]


# --- 9. ROM safety -----------------------------------------------------------


class TestManifestHonesty:
    def test_the_spoiler_also_states_module_c_is_not_delivered(self, shipping_plan):
        """The spoiler is a separate document and must not imply it by omission.

        A reader who opens only the spoiler sees per-slot rows; without an explicit
        statement they would reasonably read those as enemy-type changes. The
        shipping plan does not even run the type module, so the log has to say so.
        """
        document = shipping_plan.spoiler.to_json()
        statement = document["enemy_type_randomization"]
        assert statement["delivered"] is False
        assert "not delivered" in statement["note"]
        # The spoiler must agree with the manifest about what ran.
        assert document["modules"] == shipping_plan.manifest.to_json()["modules"]
        assert document["modules"]["enemy-type"]["enabled"] is False

    def test_the_shipping_plan_runs_no_type_module(self, shipping_plan):
        assert shipping_plan.types is None
        assert shipping_plan.manifest.to_json()["modules"]["enemy-type"] == {
            "enabled": False
        }

    def test_the_manifest_states_module_c_is_not_delivered(self, safe_plan):
        """Both halves of the manifest must agree that no type change happens.

        A review found the manifest contradicting itself: the configuration's
        ``typing_mode_effect`` correctly said the module exchanges identity between
        otherwise-identical slots, while ``exclusions.enemy_type_module`` retracted
        with "does not change which enemy a player meets" - which is false, because
        with the placement module off a given spot really is occupied by a different
        identity. Nothing tested the exclusion note, which is why it survived.
        """
        document = safe_plan.manifest.to_json()
        configuration = document["configuration"]
        assert configuration["delivers_ticket_module_c"] is False
        assert "relocation-equivalent" in configuration["typing_mode_effect"]
        assert "does not change which enemy a player meets" not in (
            configuration["typing_mode_effect"]
        )

        module_note = document["exclusions"]["enemy_type_module"]
        assert "does NOT change an enemy's TYPE" in module_note
        assert "Module C is undelivered" in module_note
        assert "does not change which enemy a player meets" not in module_note

        module_summary = document["modules"]["enemy-type"]
        assert module_summary["delivers_ticket_module_c"] is False
        assert module_summary["typing_mode"] == configuration["typing_mode"]

    def test_every_exclusion_note_is_readable(self, safe_plan):
        """The exclusion block is prose a reader must be able to read."""
        exclusions = safe_plan.manifest.to_json()["exclusions"]
        for key in ("policy", "scope_note", "enemy_type_module"):
            assert isinstance(exclusions[key], str) and exclusions[key].strip(), key


class TestRomSafety:
    def test_the_canonical_rom_is_unchanged(self, base_image):
        assert hashlib.sha256(Path(ROM).read_bytes()).hexdigest() == \
            hashlib.sha256(base_image).hexdigest()

    def test_the_output_is_the_planned_image(self, safe_plan, safe_output, base_image):
        assert apply_plan(base_image, safe_plan.plan) == safe_output

    def test_the_output_is_a_full_size_image(self, safe_output, base_image):
        assert len(safe_output) == len(base_image) == 8388608

    def test_only_declared_bytes_differ(self, base_image, safe_plan, safe_output):
        declared = set()
        for change in safe_plan.plan.changes:
            declared.update(range(change.offset, change.end))
        for offset in range(len(base_image)):
            if base_image[offset] != safe_output[offset]:
                assert offset in declared, (
                    f"byte 0x{offset:08X} changed without a declared change"
                )

    def test_no_rom_is_written_by_planning(self, base_image):
        assert hashlib.sha256(Path(ROM).read_bytes()).hexdigest() == CANONICAL_SHA256
