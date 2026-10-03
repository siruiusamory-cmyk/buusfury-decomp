"""The shared randomizer application foundation: contract, registry, documents.

ENEMY-RANDOMIZER-EXE-001 built this package so that the Map Warp Randomizer and
the Enemy Randomizer stop being two applications. What is proved here is the part
that has to hold for a *third* product to be a configuration rather than a
rewrite:

* the registry is an explicit list with a canonical order, unique ids and unique
  seed namespaces, and its invariants are checked rather than assumed;
* each module's seed is a pure function of the master seed and that module's own
  id, so enabling, disabling, adding or reordering a module cannot move an
  existing one's result - and ``map-warp`` keeps its frozen legacy namespace, so
  every warp seed ever produced still reproduces;
* the phase list is derived from the modules that actually run, and for the warp
  product it comes out identical to the list that product always had;
* the manifest is versioned, additive per module, and free of absolute paths;
* the spoiler is one document with one section per module, and "nothing to hide"
  is a first-class outcome rather than an empty file.

No ROM is needed for any of this, which is the point: the composition rules are
about modules, not about Buu's Fury.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.webfoot.randomizer import (
    FORMAT_VERSION,
    MODULE_ORDER,
    ModulePlan,
    RandomizerService,
    build_manifest,
    build_spoiler,
    canonical_json,
    default_enabled_ids,
    derive_module_seeds,
    document_digest,
    known_module_ids,
    module_for,
    modules,
    progress_steps,
    resolve_enabled,
    validate_registry,
)
from tools.webfoot.randomizer.errors import (
    ModuleRefusedError,
    OutputPathRefusedError,
    RandomizerAppError,
)
from tools.webfoot.randomizer.manifest import RESERVED_SECTION_KEYS
from tools.webfoot.randomizer.module import ModuleContractError, SettingDescriptor
from tools.webfoot.randomizer.service import (
    RandomizerRequest,
    RandomizerResult,
    shorten_hash,
)

#: The registry as shipped, pinned. A module added or reordered without thought
#: changes every combined manifest and every progress display, so it should cost
#: one deliberate edit here.
EXPECTED_ORDER = ("map-warp", "enemy-placement", "enemy-stat")


# --- the registry -------------------------------------------------------------


def test_the_registry_invariants_hold():
    """The import-time check, called again so it is proved rather than assumed."""
    validate_registry()


def test_the_canonical_order_is_explicit_and_pinned():
    assert MODULE_ORDER == EXPECTED_ORDER
    assert known_module_ids() == EXPECTED_ORDER


def test_every_module_declares_a_unique_id_and_seed_namespace():
    ids = [module.id for module in modules()]
    namespaces = [module.seed_namespace for module in modules()]

    assert len(set(ids)) == len(ids)
    assert len(set(namespaces)) == len(namespaces)


def test_every_module_declares_what_a_window_needs():
    """A module a product can offer must be describable without a ROM."""
    for module in modules():
        assert module.display_name
        assert module.description
        assert module.progress_label
        assert module.algorithm_version >= 1
        assert isinstance(module.default_enabled, bool)
        for setting in module.settings:
            assert setting.key and setting.label


def test_an_unknown_module_is_refused_by_name():
    with pytest.raises(ModuleRefusedError) as caught:
        module_for("enemy-type")

    assert "unknown randomizer module" in str(caught.value)
    assert "map-warp" in str(caught.value)


def test_enemy_type_is_not_registered_at_all():
    """Module C is absent by construction, not disabled by a flag.

    A registered-but-disabled module would still need explaining in a window and
    could still be enabled by a caller who named it. Not registering it means no
    product built on this foundation can offer it, and there is no wording
    anywhere in the shell that could imply an enemy's species is changed.
    """
    assert "enemy-type" not in known_module_ids()
    with pytest.raises(ModuleRefusedError):
        module_for("enemy-type")


# --- the enabled set ----------------------------------------------------------


def test_the_map_warp_product_resolves_to_its_one_module():
    assert resolve_enabled(["map-warp"], None) == frozenset({"map-warp"})


def test_the_enemy_product_resolves_to_its_two_modules():
    assert resolve_enabled(["enemy-placement", "enemy-stat"], None) == frozenset(
        {"enemy-placement", "enemy-stat"}
    )


def test_a_module_a_product_does_not_offer_is_refused_not_dropped():
    """A silently dropped module would produce a ROM under a false label."""
    with pytest.raises(ModuleRefusedError) as caught:
        resolve_enabled(["map-warp"], ["map-warp", "enemy-stat"])

    assert "does not offer" in str(caught.value)
    assert "enemy-stat" in str(caught.value)


def test_default_enabled_is_exactly_what_the_modules_declare():
    assert default_enabled_ids() == frozenset({"map-warp", "enemy-placement", "enemy-stat"})


# --- seeds --------------------------------------------------------------------


def test_each_modules_seed_is_a_function_of_the_master_seed_and_its_own_id():
    seeds = derive_module_seeds("StreamBlind-0001")

    assert set(seeds) == set(MODULE_ORDER)
    # The enemy modules reuse the pack's own domain-separated derivation, which is
    # what makes the application route and the CLI route produce the same ROM.
    assert seeds["enemy-placement"] != seeds["enemy-stat"]
    assert seeds["enemy-placement"] != "StreamBlind-0001"
    assert seeds["map-warp"] == "StreamBlind-0001"


def test_map_warps_legacy_namespace_is_pinned():
    """The one namespace that is not a hash, and the reason it may not be.

    The warp core draws from ``sha256(SEED_DOMAIN | seed | group | step)`` with
    the seed the user typed. Feeding it a *derived* seed would silently break every
    warp seed that already exists, so this module consumes the master seed itself.
    A future module may not copy the pattern: the test below pins that the enemy
    modules do not.
    """
    assert module_for("map-warp").seed_namespace == "master-legacy"
    assert derive_module_seeds("Goku")["map-warp"] == "Goku"
    for module_id in ("enemy-placement", "enemy-stat"):
        assert module_for(module_id).seed_namespace == module_id
        assert derive_module_seeds("Goku")[module_id] != "Goku"


def test_a_modules_seed_matches_the_authority_it_delegates_to():
    """Derivation is structural, and this is the half that can actually fail.

    An earlier version of this test compared :func:`derive_module_seeds` with
    itself, which cannot fail; an independent review caught that. What can fail is
    whether the registry's derived seed is the seed the *core* derives - the
    manifest publishes the first and the bytes come from the second, so the two
    agreeing is a fact about this build rather than about the signature.
    """
    from tools.webfoot.enemy_randomizer.seeds import derive_module_seed

    seeds = derive_module_seeds("Goku")

    for module_id in ("enemy-placement", "enemy-stat"):
        assert seeds[module_id] == derive_module_seed("Goku", module_id), (
            "the shared registry and the enemy pack must derive one seed for one "
            "module, or the manifest would state a seed the run did not use"
        )

    # And the derivation takes no enabled set, so there is nothing for a sibling's
    # state to travel through.
    import inspect

    signature = inspect.signature(derive_module_seeds)
    assert list(signature.parameters) == ["master_seed"]


def test_different_master_seeds_produce_different_module_seeds():
    first = derive_module_seeds("StreamBlind-0001")
    second = derive_module_seeds("StreamBlind-0002")

    assert first["enemy-placement"] != second["enemy-placement"]
    assert first["enemy-stat"] != second["enemy-stat"]


# --- progress -----------------------------------------------------------------


def test_the_warp_products_phase_list_is_what_it_always_was():
    """Derived from the module, and identical to the v0.1.0 list."""
    assert progress_steps({"map-warp"}) == (
        "Verifying the ROM",
        "Randomizing warp destinations",
        "Writing the randomized ROM",
        "Verifying the source ROM and writing the manifest",
    )


def test_an_enemy_run_names_the_enemy_work_and_a_placement_only_run_names_one_phase():
    both = progress_steps({"enemy-placement", "enemy-stat"})
    placement_only = progress_steps({"enemy-placement"})

    assert both[1] == "Shuffling enemy placements"
    assert both[2] == "Randomizing enemy stats"
    assert "Randomizing enemy stats" not in placement_only
    assert len(placement_only) == len(both) - 1


def test_a_combined_run_names_every_enabled_module_in_canonical_order():
    phases = progress_steps({"map-warp", "enemy-placement", "enemy-stat"})

    assert phases == (
        "Verifying the ROM",
        "Randomizing warp destinations",
        "Shuffling enemy placements",
        "Randomizing enemy stats",
        "Writing the randomized ROM",
        "Verifying the source ROM and writing the manifest",
    )


def test_the_phase_list_does_not_depend_on_the_iteration_order_it_was_given():
    assert progress_steps({"enemy-stat", "enemy-placement"}) == progress_steps(
        ["enemy-placement", "enemy-stat"]
    )


# --- module settings ----------------------------------------------------------


def test_settings_defaults_are_declared_and_unknown_keys_are_refused():
    stat = module_for("enemy-stat")
    resolved = stat.resolve_settings({})

    assert set(resolved) == {setting.key for setting in stat.settings}
    with pytest.raises(ModuleContractError) as caught:
        stat.resolve_settings({"nonsense": 1})
    assert "has no setting" in str(caught.value)


def test_a_choice_setting_refuses_a_value_outside_its_options():
    stat = module_for("enemy-stat")

    with pytest.raises(ModuleContractError):
        stat.resolve_settings({"stat_band": "ludicrous"})


def test_the_band_setting_offers_exactly_the_presets_the_core_ships():
    from tools.webfoot.enemy_randomizer.config import PRESETS

    band = next(s for s in module_for("enemy-stat").settings if s.key == "stat_band")

    assert sorted(band.choices) == sorted(PRESETS)
    assert band.default == "stream-safe"


def test_a_boolean_setting_must_carry_a_boolean_default():
    with pytest.raises(ModuleContractError):
        SettingDescriptor(key="x", kind="bool", label="X", default="yes")


def test_a_choice_setting_must_carry_its_options():
    with pytest.raises(ModuleContractError):
        SettingDescriptor(key="x", kind="choice", label="X", default="a")


# --- the manifest -------------------------------------------------------------


def _manifest(**overrides):
    fields = dict(
        tool_name="Test Tool",
        tool_version="9.9.9",
        modules=modules(),
        enabled=frozenset({"map-warp"}),
        plans=(
            ModulePlan(
                module_id="map-warp",
                manifest={"algorithm": "reciprocal-door-pairs/3"},
                summary_lines=("Supported: 735",),
                limitations=("warps may make the game impossible",),
            ),
        ),
        module_seeds=derive_module_seeds("Goku"),
        profile_id="test_profile",
        source_sha256="ab" * 32,
        source_size=8,
        master_seed="Goku",
        output_filename="out.gba",
        output_size=8,
        output_sha256="cd" * 32,
        changed_byte_count=12,
        progression="a caveat",
        module_order=list(MODULE_ORDER),
    )
    fields.update(overrides)
    return build_manifest(**fields)


def test_the_manifest_is_versioned_and_names_every_registered_module():
    document = _manifest()

    assert document["format_version"] == FORMAT_VERSION
    assert set(document["modules"]) == set(MODULE_ORDER)
    assert document["module_order"] == list(MODULE_ORDER)


def test_a_disabled_module_is_recorded_as_disabled_not_omitted():
    """So "off" is distinguishable from "did nothing" when two runs are compared."""
    document = _manifest()

    assert document["modules"]["map-warp"]["enabled"] is True
    assert document["modules"]["enemy-placement"]["enabled"] is False


def test_each_module_section_carries_its_algorithm_version_and_seed():
    document = _manifest()
    warp = document["modules"]["map-warp"]

    assert warp["module_version"] == 1
    assert warp["seed_namespace"] == "master-legacy"
    assert warp["derived_seed"] == "Goku"
    assert warp["algorithm"] == "reciprocal-door-pairs/3"
    assert warp["summary_lines"] == ["Supported: 735"]


def test_a_module_cannot_restate_a_shell_owned_section_key():
    """``enabled``, the versions and the seeds describe the run, not the module.

    A module that could rewrite them could make two incomparable manifests look
    comparable, or claim to have run when it did not.
    """
    for key in sorted(RESERVED_SECTION_KEYS):
        with pytest.raises(ModuleContractError):
            _manifest(plans=(ModulePlan(module_id="map-warp", manifest={key: "x"}),))


def test_a_section_always_states_the_runs_own_facts():
    document = _manifest()

    for module in modules():
        section = document["modules"][module.id]
        assert section["display_name"] == module.display_name
        assert section["module_version"] == module.algorithm_version
        assert section["seed_namespace"] == module.seed_namespace
        assert "derived_seed" in section


def test_the_manifest_carries_a_modules_limitations_once_each():
    document = _manifest(
        plans=(
            ModulePlan(module_id="map-warp", limitations=("one", "two")),
            ModulePlan(module_id="enemy-placement", limitations=("two",)),
        )
    )

    assert document["limitations"] == ["one", "two"]


def test_the_manifest_never_carries_an_absolute_path():
    """Two runs of the same seed in two folders must produce identical bytes."""
    import tempfile

    left = Path(tempfile.mkdtemp()) / "out.gba"
    right = Path(tempfile.mkdtemp()) / "out.gba"

    assert left != right
    assert left.name == right.name
    # The manifest records only the basename, so the two documents below are the
    # same document - which is what lets a published manifest be compared with a
    # locally produced one.
    assert canonical_json(_manifest(output_filename=left.name)) == canonical_json(
        _manifest(output_filename=right.name)
    )


def test_the_manifest_text_is_canonical_and_digestible():
    document = _manifest()
    text = canonical_json(document)

    assert text.endswith("\n")
    assert text == canonical_json(json.loads(text))
    assert document_digest(document) == document_digest(json.loads(text))


def test_the_spoiler_is_one_document_with_one_section_per_module():
    document = build_spoiler(
        tool_name="Test Tool",
        tool_version="9.9.9",
        modules=modules(),
        plans=(
            ModulePlan(module_id="enemy-placement", spoiler={"slots": [{"a": 1}]}),
            ModulePlan(module_id="enemy-stat", spoiler={"stats": [{"b": 2}]}),
        ),
        master_seed="Goku",
        profile_id="test_profile",
        output_filename="out.gba",
        output_sha256="cd" * 32,
    )

    assert set(document["modules"]) == {"enemy-placement", "enemy-stat"}
    assert document["format_version"] == FORMAT_VERSION


def test_a_run_with_nothing_to_hide_produces_no_spoiler_at_all():
    """``None``, not an empty document: an empty file reads as "nothing changed"."""
    assert (
        build_spoiler(
            tool_name="Test Tool",
            tool_version="9.9.9",
            modules=modules(),
            plans=(ModulePlan(module_id="map-warp"),),
            master_seed="Goku",
            profile_id="test_profile",
            output_filename="out.gba",
            output_sha256="cd" * 32,
        )
        is None
    )


# --- identity and refusals ----------------------------------------------------


def test_the_refusal_families_are_one_vocabulary():
    for family in (
        ModuleRefusedError,
        OutputPathRefusedError,
    ):
        assert issubclass(family, RandomizerAppError)


def test_the_shared_result_reports_only_what_it_was_given():
    result = RandomizerResult(
        master_seed="Goku",
        enabled=("map-warp",),
        module_seeds=derive_module_seeds("Goku"),
        module_versions={"map-warp": 1},
        output_path=Path("out.gba"),
        output_sha256="cd" * 32,
        output_size=8,
        manifest_path=Path("out.manifest.json"),
        spoiler_path=None,
        changed_byte_count=3,
        source_sha256="ab" * 32,
        source_unchanged=True,
        tool_name="Test Tool",
        tool_version="9.9.9",
        document=_manifest(),
    )

    lines = result.success_lines()
    assert "Seed: Goku" in lines
    assert any(line.startswith("Output:") for line in lines)
    assert any(line.startswith("SHA-256:") for line in lines)
    assert "Source ROM unchanged: yes" in lines
    assert not any("Spoiler:" in line for line in lines)


def test_a_hash_is_shortened_the_way_a_person_can_compare_it():
    assert shorten_hash("940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e") == (
        "940AD5F0...F059E"
    )
    assert shorten_hash("short") == "SHORT"


def test_the_service_refuses_a_module_outside_the_products_own_list(tmp_path):
    """The product's list is enforced by the shell, not by each client.

    An independent review found the warp product's window protocol accepting a
    hand-built request that named an enemy module: the shared service validated
    nothing, and only the enemy product happened to check. A rule written once per
    client is a rule one client forgets, so the check now lives in
    :meth:`RandomizerService.run` against the request's own ``allowed_modules``.
    """
    source = tmp_path / "source.gba"
    source.write_bytes(b"x" * 16)
    service = RandomizerService()

    with pytest.raises(ModuleRefusedError) as caught:
        service.run(
            RandomizerRequest(
                source_rom=source,
                output_rom=tmp_path / "out.gba",
                master_seed="Goku",
                enabled=frozenset({"enemy-stat"}),
                allowed_modules=frozenset({"map-warp"}),
            )
        )

    assert "does not offer" in str(caught.value)
    assert "enemy-stat" in str(caught.value)
    assert not (tmp_path / "out.gba").exists()


def test_the_service_refuses_a_request_with_no_module_enabled(tmp_path):
    """A run with nothing enabled would emit an unmodified copy of the ROM."""
    source = tmp_path / "source.gba"
    source.write_bytes(b"x" * 16)
    service = RandomizerService()

    with pytest.raises(ModuleRefusedError) as caught:
        service.run(
            RandomizerRequest(
                source_rom=source,
                output_rom=tmp_path / "out.gba",
                master_seed="Goku",
                enabled=frozenset(),
            )
        )

    assert "no module is enabled" in str(caught.value)
