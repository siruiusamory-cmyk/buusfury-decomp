"""ROM-gated proofs for the standalone *Enemy Randomizer*.

ENEMY-RANDOMIZER-EXE-001. Two things are established here that no portable test
can establish, and both are on the ticket's acceptance list:

**The golden cross-check.** For one fixed image, seed and configuration, the
production core's own programmatic route and the new executable's application
route must produce the *identical* randomized ROM. This file calls
:func:`tools.webfoot.enemy_randomizer.planner.plan_enemy_randomization` - the
already-merged core entry point - and
:meth:`tools.webfoot.enemyrand.service.EnemyRandomizerService.randomize_enemies`,
and compares the bytes. If the executable were a subtly different randomizer
rather than a frontend to the same product, this is where it would show.

**The ``StreamBlind-0001`` regression fixture.** The ticket's seed, and the seed
the randomised ROM merged to master was produced with. Pinned so a change to the
core, the module adapter, the seed derivation or the writer cannot silently
re-lay a seed somebody has already streamed.

Skips cleanly when the private canonical image is not configured.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

from tools.webfoot.cli import load_catalog
from tools.webfoot.enemy_randomizer.config import preset as enemy_preset
from tools.webfoot.enemy_randomizer.planner import plan_enemy_randomization
from tools.webfoot.enemyrand import service as enemyrand
from tools.webfoot.randomizer.errors import (
    OutputAlreadyExistsError,
    UnsupportedRomError,
)
from tools.webfoot.write import apply_plan

LOCAL_ROM = Path(
    os.environ.get("LOGX_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba")
)

CANONICAL_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)

#: The ticket's regression seed, and this product's launch seed.
STREAM_SEED = "StreamBlind-0001"

#: The output the merged RANDOMIZER-ENEMY-PACK-001 corpus recorded for that seed
#: on the canonical image. Reproduced by the application route, and by the core
#: route independently, in this file.
STREAM_BLIND_GOLDEN_SHA256 = (
    "4d4cf624681803a227c26a44bc08b3c6b6cf71539c0a283a03fabd0561e7895f"
)

#: The counts the pack recorded for that seed: 1177 placements moved, 91 stat
#: records changed. Pinned so a policy change cannot pass as a refactor.
PLACEMENTS_MOVED = 1177
STAT_RECORDS_CHANGED = 91

pytestmark = pytest.mark.skipif(
    not LOCAL_ROM.is_file(),
    reason=(
        "the canonical Buu's Fury image is not configured; set "
        f"LOGX_CANONICAL_ROM or place it at {LOCAL_ROM}"
    ),
)


@pytest.fixture(scope="module")
def service() -> enemyrand.EnemyRandomizerService:
    return enemyrand.EnemyRandomizerService()


@pytest.fixture(scope="module")
def source_sha256() -> str:
    return hashlib.sha256(LOCAL_ROM.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def golden(service, tmp_path_factory):
    """The default, launch-seed, both-modules run with a spoiler - made once."""
    work = tmp_path_factory.mktemp("enemy-app")
    return service.randomize_enemies(
        LOCAL_ROM, work / "stream.gba", STREAM_SEED, spoiler=True
    )


# --- the product, end to end --------------------------------------------------


def test_the_canonical_image_is_accepted(service, source_sha256):
    verification = service.verify_rom(LOCAL_ROM)

    assert source_sha256 == CANONICAL_SHA256
    assert verification.ok
    assert verification.sha256 == CANONICAL_SHA256


def test_the_stream_blind_fixture_reproduces_the_recorded_output(golden):
    assert golden.master_seed == STREAM_SEED
    assert golden.output_sha256 == STREAM_BLIND_GOLDEN_SHA256


def test_the_recorded_counts_are_reproduced(golden):
    placement = golden.module_section("enemy-placement")
    stats = golden.module_section("enemy-stat")

    assert placement["summary"]["slots_moved"] == PLACEMENTS_MOVED
    assert stats["summary"]["records_changed"] == STAT_RECORDS_CHANGED
    assert golden.source_unchanged is True


# --- the golden cross-check against the core ----------------------------------


def test_the_application_route_is_the_core_route(golden):
    """Same image, seed and configuration; identical bytes, not merely close.

    The core route here is the one that already merged to master - a fresh context
    built by the pack's own one-shot wrapper, its own plan, applied by the one
    writer. If the executable reimplemented any part of the policy, or derived a
    seed differently, the digests in this test would differ.
    """
    catalog = load_catalog(None)
    config = enemy_preset("stream-safe").config
    core = plan_enemy_randomization(
        LOCAL_ROM, catalog, STREAM_SEED, config, preset_name="stream-safe"
    )
    core_bytes = apply_plan(LOCAL_ROM.read_bytes(), core.plan)

    assert hashlib.sha256(core_bytes).hexdigest() == golden.output_sha256
    assert core_bytes == golden.output_path.read_bytes()


def test_the_derived_module_seeds_are_the_packs_own(golden):
    """The module seeds are the pack's, so the two routes share one derivation."""
    catalog = load_catalog(None)
    config = enemy_preset("stream-safe").config
    core = plan_enemy_randomization(
        LOCAL_ROM, catalog, STREAM_SEED, config, preset_name="stream-safe"
    )

    for module_id in ("enemy-placement", "enemy-stat"):
        assert golden.module_seeds[module_id] == core.module_seeds[module_id]


# --- determinism and the modules ----------------------------------------------


def test_the_same_seed_and_settings_produce_the_same_rom(service, golden, tmp_path):
    again = service.randomize_enemies(LOCAL_ROM, tmp_path / "again.gba", STREAM_SEED)

    assert again.output_sha256 == golden.output_sha256
    assert again.output_path.read_bytes() == golden.output_path.read_bytes()


def test_a_different_seed_produces_a_different_rom(service, golden, tmp_path):
    other = service.randomize_enemies(LOCAL_ROM, tmp_path / "other.gba", "StreamBlind-0002")

    assert other.output_sha256 != golden.output_sha256


def test_placement_only_changes_the_image_and_leaves_stats_alone(service, tmp_path):
    result = service.randomize_enemies(
        LOCAL_ROM, tmp_path / "placement.gba", STREAM_SEED, enabled={"enemy-placement"}
    )
    document = json.loads(result.manifest_path.read_text(encoding="utf-8"))

    assert result.enabled == ("enemy-placement",)
    assert document["modules"]["enemy-placement"]["enabled"] is True
    assert document["modules"]["enemy-stat"]["enabled"] is False
    assert document["modules"]["map-warp"]["enabled"] is False
    assert result.changed_byte_count > 0
    # The stat module did not run, so no stat record may be claimed.
    assert "configuration" not in document["modules"]["enemy-stat"]


def test_stats_only_changes_the_image_and_leaves_placements_alone(service, tmp_path):
    result = service.randomize_enemies(
        LOCAL_ROM, tmp_path / "stats.gba", STREAM_SEED, enabled={"enemy-stat"}
    )
    document = json.loads(result.manifest_path.read_text(encoding="utf-8"))

    assert result.enabled == ("enemy-stat",)
    assert document["modules"]["enemy-stat"]["enabled"] is True
    assert document["modules"]["enemy-placement"]["enabled"] is False
    assert result.changed_byte_count > 0
    # No placement decision may be claimed by a run that shuffled no placement.
    assert "eligibility" not in document["modules"]["enemy-placement"]


def test_the_three_enabled_sets_produce_three_different_roms(service, golden, tmp_path):
    placement = service.randomize_enemies(
        LOCAL_ROM, tmp_path / "p.gba", STREAM_SEED, enabled={"enemy-placement"}
    )
    stats = service.randomize_enemies(
        LOCAL_ROM, tmp_path / "s.gba", STREAM_SEED, enabled={"enemy-stat"}
    )

    assert len(
        {placement.output_sha256, stats.output_sha256, golden.output_sha256}
    ) == 3


# --- the manifest and the spoiler ---------------------------------------------


def test_every_manifest_records_that_module_c_is_not_delivered(golden):
    document = json.loads(golden.manifest_path.read_text(encoding="utf-8"))

    for module_id in ("enemy-placement", "enemy-stat"):
        section = document["modules"][module_id]
        assert section["delivers_ticket_module_c"] is False
        assert "module_version" in section
    # The pack's own configuration block, which carries the band, the field list
    # and the effect statement, travels whole.
    configuration = document["modules"]["enemy-stat"]["configuration"]
    assert configuration["delivers_ticket_module_c"] is False
    assert configuration["enabled_modules"] == ["enemy-placement", "enemy-stat"]


def test_the_manifest_carries_the_products_own_identity_and_caveat(golden):
    document = json.loads(golden.manifest_path.read_text(encoding="utf-8"))

    assert document["tool"] == {"name": "Enemy Randomizer", "version": "0.1.0"}
    assert document["master_seed"] == STREAM_SEED
    assert document["source"]["sha256"] == CANONICAL_SHA256
    assert document["output"]["sha256"] == STREAM_BLIND_GOLDEN_SHA256
    assert "NOT changed" in document["progression"]
    assert document["limitations"], "the run's exclusions must travel with it"


def test_the_spoiler_is_written_when_asked_for_and_carries_the_decisions(golden):
    assert golden.spoiler_path is not None
    document = json.loads(golden.spoiler_path.read_text(encoding="utf-8"))

    assert set(document["modules"]) == {"enemy-placement", "enemy-stat"}
    assert document["modules"]["enemy-placement"]["slots"]
    assert document["modules"]["enemy-stat"]["stats"]
    assert document["output"]["sha256"] == STREAM_BLIND_GOLDEN_SHA256


def test_no_spoiler_file_appears_when_the_option_is_off(service, tmp_path):
    result = service.randomize_enemies(
        LOCAL_ROM, tmp_path / "blind.gba", STREAM_SEED, spoiler=False
    )
    document = json.loads(result.manifest_path.read_text(encoding="utf-8"))

    assert result.spoiler_path is None
    assert document["spoiler"] is None
    assert not enemyrand.default_service().spoiler_path_for(result.output_path).exists()
    # The manifest is still written - it is provenance, not answers.
    assert result.manifest_path.exists()


# --- source-ROM safety --------------------------------------------------------


def test_the_source_rom_is_untouched_by_every_run(source_sha256):
    assert hashlib.sha256(LOCAL_ROM.read_bytes()).hexdigest() == CANONICAL_SHA256


def test_an_existing_output_is_refused_until_an_overwrite_is_confirmed(service, tmp_path):
    output = tmp_path / "collision.gba"
    first = service.randomize_enemies(LOCAL_ROM, output, STREAM_SEED)
    preserved = output.read_bytes()

    with pytest.raises(OutputAlreadyExistsError):
        service.randomize_enemies(LOCAL_ROM, output, STREAM_SEED)

    assert output.read_bytes() == preserved

    replaced = service.randomize_enemies(LOCAL_ROM, output, STREAM_SEED, overwrite=True)
    assert replaced.output_sha256 == first.output_sha256


def test_a_copy_of_the_canonical_image_is_never_replaced(service, tmp_path):
    """Confirming an overwrite must not be enough to destroy a clean ROM."""
    output = tmp_path / "looks-clean.gba"
    output.write_bytes(LOCAL_ROM.read_bytes())

    from tools.webfoot.randomizer.errors import OutputPathRefusedError

    with pytest.raises(OutputPathRefusedError) as caught:
        service.randomize_enemies(LOCAL_ROM, output, STREAM_SEED, overwrite=True)

    assert "copy of the verified ROM" in str(caught.value)
    assert hashlib.sha256(output.read_bytes()).hexdigest() == CANONICAL_SHA256


def test_the_output_may_not_be_the_input(service):
    from tools.webfoot.randomizer.errors import OutputPathRefusedError

    with pytest.raises(OutputPathRefusedError) as caught:
        service.randomize_enemies(LOCAL_ROM, LOCAL_ROM, STREAM_SEED)

    assert "never writes to the ROM you selected" in str(caught.value)
    assert hashlib.sha256(LOCAL_ROM.read_bytes()).hexdigest() == CANONICAL_SHA256


def test_an_unsupported_image_is_refused_with_a_sentence(service, tmp_path):
    forged = tmp_path / "forged.gba"
    image = bytearray(LOCAL_ROM.read_bytes())
    image[0x100] ^= 0xFF
    forged.write_bytes(bytes(image))

    verification = service.verify_rom(forged)
    assert not verification.ok
    assert "Expected SHA-256" in verification.problem

    with pytest.raises(UnsupportedRomError):
        service.randomize_enemies(forged, tmp_path / "out.gba", STREAM_SEED)

    assert not (tmp_path / "out.gba").exists()


def test_a_failed_run_leaves_the_source_and_the_destination_alone(service, tmp_path):
    """A refusal must be total: nothing written, nothing destroyed."""
    bad = tmp_path / "not-a-rom.bin"
    bad.write_bytes(b"definitely not a Game Boy Advance image")
    existing = tmp_path / "previous.gba"
    existing.write_bytes(b"a previous randomized ROM")
    manifest = service.manifest_path_for(existing)
    manifest.write_text("{}", encoding="utf-8")

    with pytest.raises(UnsupportedRomError):
        service.randomize_enemies(bad, existing, STREAM_SEED, overwrite=True)

    assert existing.read_bytes() == b"a previous randomized ROM"
    assert manifest.read_text(encoding="utf-8") == "{}"
    assert hashlib.sha256(LOCAL_ROM.read_bytes()).hexdigest() == CANONICAL_SHA256


# --- what the product refuses to offer ----------------------------------------


def test_a_module_outside_the_product_cannot_be_smuggled_into_a_request(service, tmp_path):
    from tools.webfoot.randomizer.errors import RandomizerAppError

    with pytest.raises(RandomizerAppError) as caught:
        service.randomize_enemies(
            LOCAL_ROM,
            tmp_path / "x.gba",
            STREAM_SEED,
            enabled={"enemy-placement", "enemy-type"},
        )

    assert "does not offer" in str(caught.value)
    assert not (tmp_path / "x.gba").exists()


def test_every_module_the_product_offers_is_registered_and_named(service):
    """No "randomize everything" escape, and no type module to reach for."""
    from tools.webfoot.randomizer.registry import known_module_ids

    assert set(service.allowed_modules) <= set(known_module_ids())
    assert "enemy-type" not in service.allowed_modules
