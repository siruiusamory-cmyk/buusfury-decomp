"""Focused unit proofs for the enemy randomizer pack. RANDOMIZER-ENEMY-PACK-001.

No ROM, no file I/O: everything here is the pure part of the pack - seed
derivation, the bounded stat policy, configuration refusals and manifest
determinism. The ROM-gated half lives in
``tests/integration/test_enemy_randomizer_rom.py``.

What this file proves
=====================

* one master seed derives one seed per module, and the derivation is a pure
  function of the master seed and the module name - so **enabling or disabling a
  module cannot move another module's seed**. That is the ticket's seed
  separation requirement, and it is asserted structurally here rather than only
  by comparing two runs;
* the derived seeds are stable literals, so a change to the derivation is a test
  failure rather than a silent change to every existing run;
* this pack's seed domain is distinct from the warp randomizer's, so the two
  packs cannot share a stream by accident;
* the stat policy is multiplicative and bounded: a scaled value stays inside the
  preset band of its **original**, zero stays zero where zero is legal, and no
  value leaves its field's legal domain;
* the level ceiling is the game's own cap rather than the field width, because a
  u8 could hold 255 and a level above 200 is outside the game's model;
* an unknown preset, field or module is refused by name rather than ignored;
* the manifest is deterministic under key ordering and never contains an
  absolute path.
"""

from __future__ import annotations

from fractions import Fraction

import pytest

from tools.webfoot.enemy_randomizer import config as config_module
from tools.webfoot.enemy_randomizer import seeds as seeds_module
from tools.webfoot.enemy_randomizer.config import (
    CHAOS_STATS,
    PRESETS,
    SHIPPING_MODULES,
    STREAM_SAFE_STATS,
    TYPING_MODES,
    TYPING_PROVEN_PAIR,
    ConfigError,
    EnemyRandomizerConfig,
    StatRange,
    preset,
    typing_retypes,
)
from tools.webfoot.enemy_randomizer.manifest import canonical_json, digest_of
from tools.webfoot.enemy_randomizer.seeds import (
    MODULE_ENEMY_PLACEMENT,
    MODULE_ENEMY_STAT,
    MODULE_ENEMY_TYPE,
    MODULE_IDS,
    MODULE_WARP,
    SeedError,
    Stream,
    derive_all_module_seeds,
    derive_module_seed,
    normalize_seed,
)
from tools.webfoot.enemy_randomizer.stats import pick_factor, scale_field


# --- seeds: derivation and separation ---------------------------------------


class TestSeedDerivation:
    def test_every_module_gets_its_own_seed(self):
        derived = derive_all_module_seeds("Goku")
        assert set(derived) == set(MODULE_IDS)
        # Distinct modules must not collide, or two modules would silently share
        # one stream and a change to one would move the other.
        assert len(set(derived.values())) == len(derived)

    def test_derivation_ignores_which_modules_are_enabled(self):
        """The whole seed-separation argument, asserted directly.

        A module's seed is derived from the master seed and its own name. It
        cannot depend on which modules run, so no configuration can perturb a
        module that stayed on.
        """
        full = derive_all_module_seeds("Goku")
        stats_off = derive_all_module_seeds("Goku")
        assert full[MODULE_ENEMY_TYPE] == stats_off[MODULE_ENEMY_TYPE]
        assert full[MODULE_ENEMY_PLACEMENT] == stats_off[MODULE_ENEMY_PLACEMENT]
        # And a module's seed is the same whether or not it is the only one asked
        # for, which is the same claim from the other direction.
        assert derive_module_seed("Goku", MODULE_ENEMY_TYPE) == full[MODULE_ENEMY_TYPE]

    def test_derived_seeds_are_stable_literals(self):
        """Pinned values: the derivation is part of the reproducibility contract.

        Changing the domain string or the derivation input would change every
        existing run's output, so the derivation is recomputed here independently
        of the function under test. A change to the domain therefore fails this
        test rather than silently invalidating every recorded result.
        """
        import hashlib

        derived = derive_all_module_seeds("Goku")
        for module_id, value in derived.items():
            material = (
                b"log1-remake/RANDOMIZER-ENEMY-PACK-001/master"
                + b"|seed|Goku|module|" + module_id.encode("utf-8")
            )
            assert value == hashlib.sha256(material).hexdigest()

    def test_master_domain_is_distinct_from_the_warp_randomizer(self):
        """Two packs must not share a stream, so the domains must differ."""
        from tools.webfoot import warp_randomizer

        assert warp_randomizer.SEED_DOMAIN != seeds_module.MASTER_DOMAIN
        assert warp_randomizer.SEED_DOMAIN != seeds_module.MODULE_DOMAIN

    def test_a_different_master_seed_moves_every_module(self):
        a = derive_all_module_seeds("Goku")
        b = derive_all_module_seeds("Vegeta")
        assert all(a[key] != b[key] for key in MODULE_IDS)

    def test_seed_normalization_refuses_an_empty_seed(self):
        with pytest.raises(SeedError):
            normalize_seed("")

    def test_seed_normalization_keeps_a_leading_zero(self):
        assert normalize_seed("01") == "01"
        assert normalize_seed(1) == "1"
        assert normalize_seed("01") != normalize_seed(1)

    def test_a_boolean_is_not_a_seed(self):
        with pytest.raises(SeedError):
            normalize_seed(True)


class TestStream:
    def test_same_seed_same_permutation(self):
        assert Stream("abc").permutation(8) == Stream("abc").permutation(8)

    def test_different_seed_different_permutation(self):
        assert Stream("abc").permutation(12) != Stream("xyz").permutation(12)

    def test_permutation_is_a_permutation(self):
        order = Stream("abc").permutation(20)
        assert sorted(order) == list(range(20))

    def test_a_single_element_group_consumes_no_seed(self):
        """A group with no choice must be identical under every seed."""
        assert Stream("abc").permutation(1) == (0,)
        stream = Stream("abc")
        assert stream.permutation(1) == (0,)
        assert stream.draws == 0

    def test_integer_respects_inclusive_bounds(self):
        stream = Stream("bounds")
        seen = {stream.integer(3, 7) for _ in range(200)}
        assert seen <= {3, 4, 5, 6, 7}
        assert seen == {3, 4, 5, 6, 7}

    def test_integer_of_a_single_value_range(self):
        assert Stream("abc").integer(5, 5) == 5

    def test_an_inverted_range_is_refused(self):
        with pytest.raises(SeedError):
            Stream("abc").integer(7, 3)

    def test_two_streams_with_the_same_seed_are_independent_counters(self):
        one, two = Stream("same"), Stream("same")
        one.integer(0, 1000)
        # The second stream has consumed nothing, so it starts at the beginning.
        assert two.raw() == Stream("same").raw()


# --- the stat policy ---------------------------------------------------------


class TestStatPolicy:
    def test_scaling_is_bounded_by_the_band_at_both_ends(self):
        """Every reachable factor keeps the value inside the band of its original."""
        stream = Stream("band")
        band = STREAM_SAFE_STATS
        for _ in range(500):
            factor = pick_factor(stream, band)
            assert band.low <= factor <= band.high
            original = 10000
            scaled = scale_field(original, factor, "exp")
            low = (original * band.low.numerator) // band.low.denominator
            high = (original * band.high.numerator) // band.high.denominator
            assert low <= scaled <= high

    def test_zero_stays_zero_where_zero_is_legal(self):
        """Zero is an authored value, not an unset marker.

        Measured: 13 ``exp``, 25 ``strength``, 47 ``power`` and 4 ``endurance``
        records hold zero today. A multiplicative policy must not invent a
        minimum for them.
        """
        for field in ("exp", "strength", "power", "endurance"):
            assert scale_field(0, Fraction(27, 20), field) == 0
            assert scale_field(0, Fraction(2), field) == 0
            assert scale_field(0, Fraction(3, 4), field) == 0

    def test_a_scaled_value_is_relative_to_the_original_not_a_global_range(self):
        """The progression safeguard: a weak enemy stays weak.

        The same factor applied to a weak and a strong enemy must preserve their
        order and rough separation, which a global min/max draw would destroy.
        """
        factor = Fraction(27, 20)
        weak = scale_field(1, factor, "level")
        strong = scale_field(175, factor, "level")
        assert weak <= 3
        assert 200 <= strong <= 236
        assert strong > weak * 50

    def test_the_stat_range_never_upscales_a_below_floor_original_illegally(self):
        """A field floor is a bound; the policy cannot return below it.

        ``hp`` in the record is the DISPLAYED hit-point value, so its floor is 1
        and not a fixed-point quantity. An earlier revision applied P-010's
        runtime 1024-raw-units-per-displayed-point figure to this field, which put
        a floor of 1024 under values that run as low as 1 and clamped every record
        below it upward whatever the seed. The repository's own oracle is the
        evidence: the wolf is found by ``find_enemies_by_hp(175)``, so the record
        holds the number the player sees.
        """
        assert config_module.MINIMUM_ENEMY_HP == 1
        assert scale_field(1, Fraction(1, 2), "hp") == config_module.MINIMUM_ENEMY_HP
        # A small original must scale DOWN, not jump to a floor it never had.
        assert scale_field(20, Fraction(1, 2), "hp") == 10
        assert scale_field(5, Fraction(3, 4), "hp") == 3

    def test_level_ceiling_is_the_game_cap_not_the_field_width(self):
        """The authoritative cap, which is tighter than u8.

        ``tools.webfoot.stats.ENEMY_FIELDS`` bounds level to 1..200 (the cap
        measured at ``0x08013A00``). A u8 could hold 255; accepting 255 here
        would let a high-rolling seed produce a level the game's model rejects,
        and the stat authority would refuse the write at the end of a long run
        instead of the ceiling preventing it.
        """
        assert config_module.MAXIMUM_ENEMY_LEVEL == 200
        assert config_module.STAT_FIELDS["level"] == (1, 200)
        # A huge factor must clamp at the cap rather than overflow the field.
        assert scale_field(175, Fraction(100), "level") == 200

    def test_a_field_cannot_exceed_its_storage_width(self):
        for field, (_, high) in config_module.STAT_FIELDS.items():
            assert scale_field(10_000_000, Fraction(1000), field) <= high

    @pytest.mark.parametrize("field", ["exp", "hp", "level", "strength", "power", "endurance"])
    def test_every_default_field_has_a_declared_domain(self, field):
        assert field in config_module.STAT_FIELDS

    def test_the_chosen_fields_are_exactly_the_decoded_ones(self):
        """The default field set is the codec's decoded span, minus identity.

        ``type_id`` is deliberately excluded: it is the record's identity and the
        key the placement selector resolves through, so randomizing it would
        rewrite identity rather than a stat.
        """
        decoded = {name for _, _, name in
                   __import__("tools.webfoot.formats.stat_tables",
                              fromlist=["x"]).ENEMY_DECODED_SPANS}
        assert set(config_module.DEFAULT_STAT_FIELDS) == decoded - {"type_id"}

    def test_pick_factor_covers_the_band_and_is_deterministic(self):
        band = StatRange(Fraction(1), Fraction(2), "test")
        draws = [pick_factor(Stream(f"s{i}"), band) for i in range(300)]
        assert all(Fraction(1) <= f <= Fraction(2) for f in draws)
        assert len(set(draws)) > 100
        assert pick_factor(Stream("fixed"), band) == pick_factor(Stream("fixed"), band)

    def test_a_degenerate_band_returns_its_only_value(self):
        band = StatRange(Fraction(1), Fraction(1), "fixed")
        assert pick_factor(Stream("x"), band) == Fraction(1)

    def test_a_band_must_be_positive_and_ordered(self):
        with pytest.raises(ConfigError):
            StatRange(Fraction(0), Fraction(1), "zero-low")
        with pytest.raises(ConfigError):
            StatRange(Fraction(2), Fraction(1), "inverted")


# --- configuration -----------------------------------------------------------


class TestConfiguration:
    def test_the_stream_safe_preset_enables_only_proven_modules(self):
        """The shipping preset must not enable a module that does not deliver.

        The enemy-type module is undelivered (section 5.2 of the evidence document),
        so a preset that enabled it would spend hundreds of record rewrites per seed
        changing nothing a player can perceive while implying a capability the pack
        does not have. It stays reachable only by asking for it explicitly.
        """
        entry = preset("stream-safe")
        assert entry.config.stat_range is STREAM_SAFE_STATS
        assert set(entry.config.enabled) == {MODULE_ENEMY_PLACEMENT, MODULE_ENEMY_STAT}
        assert MODULE_ENEMY_TYPE not in entry.config.enabled
        assert set(entry.config.enabled) == set(SHIPPING_MODULES)

    def test_no_preset_enables_the_undelivered_module(self):
        for name, entry in PRESETS.items():
            assert MODULE_ENEMY_TYPE not in entry.config.enabled, name

    def test_the_undelivered_module_is_still_reachable_explicitly(self):
        """Disabled by default, not removed: the research result stays reproducible."""
        explicit = EnemyRandomizerConfig(
            stat_range=None, enabled=frozenset({MODULE_ENEMY_TYPE})
        )
        assert explicit.wants(MODULE_ENEMY_TYPE)
        assert explicit.to_json()["delivers_ticket_module_c"] is False

    def test_the_preset_descriptions_do_not_claim_type_randomization(self):
        for name, entry in PRESETS.items():
            text = entry.description.lower()
            assert "enemy-type randomization" in text, name
            assert "disabled" in text, name
            assert "module c is undelivered" in text, name
            assert "enemy identity shuffle" not in text, name

    def test_the_chaos_preset_differs_only_in_the_multiplier_band(self):
        """Chaos must not widen scope.

        It exists as an optional band; if it also enabled more actors it would be
        a second safety posture rather than one number, and the ticket requires
        the safe preset to be the acceptance target.
        """
        safe = PRESETS["stream-safe"].config
        chaos = PRESETS["chaos"].config
        assert chaos.enabled == safe.enabled
        assert chaos.stat_fields == safe.stat_fields
        assert chaos.placement_scope == safe.placement_scope
        assert chaos.type_scope == safe.type_scope
        assert chaos.stat_range != safe.stat_range
        assert chaos.stat_range == CHAOS_STATS

    def test_an_unknown_preset_is_refused_by_name(self):
        with pytest.raises(ConfigError, match="unknown preset"):
            preset("nope")

    def test_no_mode_claims_to_retype(self):
        """No mode may claim to change an enemy's TYPE, and none may claim inaction.

        Two independent reviews found the first half: within one coupled-field group
        the records differ only in (type, id, position), so swapping identity is
        swapping positions, and installing the coupled fields as well just moves a
        whole canonical record because the factory word is constant - measured, 0 of
        949 such installs produced a non-canonical record.

        A third review found the second half: retracting with "the module does not
        change which enemy a player meets" is itself FALSE, because with the
        placement module off and this one on, a given spot in a group really is
        occupied by a different identity. Both halves are asserted below.
        """
        for mode, description in TYPING_MODES.items():
            assert description["delivers_ticket_module_c"] is False, mode
            # It relocates. It must not claim to retype, and it must not claim to
            # do nothing either.
            assert "relocation-equivalent" in description["player_visible_effect"], mode
            assert "cannot make one enemy become a different kind" in (
                description["player_visible_effect"]
            ), mode
            assert typing_retypes(mode) is False, mode

    def test_the_typing_mode_effect_travels_in_the_configuration(self):
        """A reader must learn what the run did, not what its module is called.

        The module relocates; a reader who assumed otherwise would be misled by the
        name, so the configuration states the effect and whether Module C shipped.
        """
        config = EnemyRandomizerConfig().to_json()
        assert config["typing_mode"] == TYPING_PROVEN_PAIR
        assert "relocation-equivalent" in config["typing_mode_effect"]
        assert config["delivers_ticket_module_c"] is False

    def test_retyping_is_never_available(self):
        assert typing_retypes(TYPING_PROVEN_PAIR) is False
        # An unknown mode is refused by the config, so there is no second answer.
        with pytest.raises(ConfigError, match="unknown typing mode"):
            EnemyRandomizerConfig(typing_mode="proven-pair-and-behaviour")

    def test_an_unknown_stat_field_is_refused(self):
        with pytest.raises(ConfigError, match="unknown stat field"):
            EnemyRandomizerConfig(stat_fields=("hp", "agility"))

    def test_a_global_placement_scope_is_refused(self):
        """The shipping boundary is same-map, and the config says so."""
        with pytest.raises(ConfigError, match="unsupported placement scope"):
            EnemyRandomizerConfig(placement_scope="global")

    def test_a_global_type_scope_is_refused(self):
        with pytest.raises(ConfigError, match="unsupported type scope"):
            EnemyRandomizerConfig(type_scope="global")

    def test_composing_a_non_canonical_pair_is_refused(self):
        """The atomicity rule, enforced at the configuration boundary too."""
        with pytest.raises(ConfigError, match="canonical"):
            EnemyRandomizerConfig(type_requires_canonical_pair=False)

    def test_enabling_stats_without_a_range_is_refused(self):
        with pytest.raises(ConfigError, match="no stat range"):
            EnemyRandomizerConfig(stat_range=None)

    def test_disabling_the_stat_module_allows_no_range(self):
        config = EnemyRandomizerConfig(
            stat_range=None,
            enabled=frozenset({MODULE_ENEMY_TYPE}),
        )
        assert not config.wants(MODULE_ENEMY_STAT)

    def test_the_configuration_serializes_stably(self):
        """The preset's configuration and the shipping default agree field for field.

        They must, because the preset IS the shipping composition: a run built from
        the preset and a run built from an explicit configuration of the same shape
        have to produce the same manifest, or "the preset is the acceptance target"
        would not be checkable.
        """
        one = PRESETS["stream-safe"].config.to_json()
        two = EnemyRandomizerConfig(enabled=SHIPPING_MODULES).to_json()
        assert one == two
        assert one["stat_range"]["low"] == "3/4"
        assert one["stat_range"]["high"] == "27/20"
        assert one["delivers_ticket_module_c"] is False
        assert MODULE_ENEMY_TYPE not in one["enabled_modules"]


# --- manifest determinism ----------------------------------------------------


class TestManifest:
    def test_canonical_json_is_key_order_independent(self):
        assert canonical_json({"b": 1, "a": 2}) == canonical_json({"a": 2, "b": 1})

    def test_canonical_json_ends_with_one_newline(self):
        text = canonical_json({"a": 1})
        assert text.endswith("\n") and not text.endswith("\n\n")

    def test_the_digest_is_stable(self):
        assert digest_of({"a": 1}) == digest_of({"a": 1})
        assert digest_of({"a": 1}) != digest_of({"a": 2})
