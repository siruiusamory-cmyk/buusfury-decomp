"""ROM-gated proof that the multi-module application composes headlessly.

ENEMY-RANDOMIZER-EXE-001's addendum calls this "the most important future-proofing
acceptance test", and the reason is concrete: the eventual product is ONE
application with several independently selectable randomizer modules writing ONE
ROM, and that only works if the three proven modules can share a request, a
context, a plan and a writer today. If they cannot, no amount of GUI work later
will make it true.

What is proved, against the canonical image:

* ``map-warp`` + ``enemy-placement`` + ``enemy-stat`` run in one request and
  produce one accepted ROM;
* the composition is **deterministic** - two runs of the same seed are
  byte-identical;
* it is **additive** - the combined run's changed-byte count is exactly the sum of
  the three modules' own runs, which is a proof that no module's writes were
  dropped or double-counted *and* a proof that none of them collide;
* every module's manifest section is present, enabled and versioned;
* each module's derived seed is unchanged by enabling or disabling its siblings;
* the source image is an input on every path and an output on none.

This is not a second product. It is a headless proof that the module architecture
composes; the combined executable is deliberately not built here.

Skips cleanly when the private canonical image is not configured.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

from tools.webfoot.randomizer.registry import derive_module_seeds, progress_steps
from tools.webfoot.randomizer.service import RandomizerRequest, RandomizerService

LOCAL_ROM = Path(
    os.environ.get("LOGX_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba")
)

CANONICAL_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)

#: One seed drives every module, which is the whole point of the derivation.
SEED = "StreamBlind-0001"

ALL_MODULES = frozenset({"map-warp", "enemy-placement", "enemy-stat"})

pytestmark = pytest.mark.skipif(
    not LOCAL_ROM.is_file(),
    reason=(
        "the canonical Buu's Fury image is not configured; set "
        f"LOGX_CANONICAL_ROM or place it at {LOCAL_ROM}"
    ),
)


def _request(service: RandomizerService, tmp_path: Path, name: str, enabled, seed=SEED):
    return RandomizerRequest(
        source_rom=LOCAL_ROM,
        output_rom=tmp_path / f"{name}.gba",
        master_seed=seed,
        enabled=frozenset(enabled),
        tool_name="Combined composition proof",
        tool_version="0.0.0",
        progression="composed modules",
        spoiler=True,
    )


@pytest.fixture(scope="module")
def workdir(tmp_path_factory) -> Path:
    return tmp_path_factory.mktemp("combined")


@pytest.fixture(scope="module")
def source_sha256() -> str:
    return hashlib.sha256(LOCAL_ROM.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def service() -> RandomizerService:
    return RandomizerService()


@pytest.fixture(scope="module")
def runs(workdir, service):
    """Every run this file needs, made once against one loaded image."""
    results = {}
    for name, enabled in (
        ("warp", {"map-warp"}),
        ("placement", {"enemy-placement"}),
        ("stat", {"enemy-stat"}),
        ("enemy-both", {"enemy-placement", "enemy-stat"}),
        ("combined", ALL_MODULES),
        ("combined-again", ALL_MODULES),
    ):
        results[name] = service.run(_request(service, workdir, name, enabled))
    return results


def test_the_canonical_image_is_the_supported_one(source_sha256):
    assert source_sha256 == CANONICAL_SHA256


def test_the_three_modules_compose_in_one_request(runs):
    combined = runs["combined"]

    assert combined.enabled == ("map-warp", "enemy-placement", "enemy-stat")
    assert combined.output_path.is_file()
    assert combined.changed_byte_count > 0
    assert combined.source_unchanged is True


def test_the_composition_is_deterministic(runs):
    assert runs["combined"].output_sha256 == runs["combined-again"].output_sha256
    assert (
        runs["combined"].output_path.read_bytes()
        == runs["combined-again"].output_path.read_bytes()
    )


def test_the_combined_manifest_is_byte_identical_across_directories(
    service, workdir
):
    """The same seed, modules and output *name* produce the same document.

    The output contributes its basename only, so no absolute path and no machine
    detail reaches the record of a combined run - which is what would let a
    published combined manifest be compared with a locally produced one.
    """
    left = workdir / "one"
    right = workdir / "two"
    left.mkdir(exist_ok=True)
    right.mkdir(exist_ok=True)
    name = "combined.gba"

    first = service.run(_request(service, left, "combined", ALL_MODULES)).manifest_path
    second = service.run(_request(service, right, "combined", ALL_MODULES)).manifest_path

    assert first.read_bytes() == second.read_bytes()
    assert str(workdir).encode() not in first.read_bytes()


def _changed_offsets(left: bytes, right: bytes) -> set[int]:
    """Every byte position at which two images differ."""
    if len(left) != len(right):
        raise AssertionError("the images are different lengths")
    return {index for index, (a, b) in enumerate(zip(left, right)) if a != b}


@pytest.fixture(scope="module")
def base_bytes() -> bytes:
    return LOCAL_ROM.read_bytes()


@pytest.fixture(scope="module")
def offsets(runs, base_bytes):
    """The byte positions each module owns, measured rather than declared."""
    return {
        name: _changed_offsets(base_bytes, runs[name].output_path.read_bytes())
        for name in ("warp", "placement", "stat", "enemy-both", "combined")
    }


def test_the_composition_is_additive_and_therefore_collision_free(offsets):
    """The strongest available proof that no module's bytes were lost or shared.

    ``plan_changes`` refuses overlapping writes outright, so a collision cannot
    reach this assertion - but a *silently dropped* change could, and a "last
    module wins" resolution could hide one. Counting changed bytes catches both,
    which is what an earlier version of this test did; comparing the byte
    POSITIONS catches more, because two modules could move the same number of
    bytes in the same total and still not be additive.

    An independent review pointed out that the count-only form would pass a run in
    which one module's result had drifted while its byte count stayed the same.
    """
    assert offsets["combined"] == (
        offsets["warp"] | offsets["placement"] | offsets["stat"]
    )
    assert offsets["enemy-both"] == offsets["placement"] | offsets["stat"]
    # And the three are genuinely disjoint, which is what makes the union above a
    # composition rather than an overlap that failed to be detected.
    assert not (offsets["warp"] & offsets["placement"])
    assert not (offsets["warp"] & offsets["stat"])
    assert not (offsets["placement"] & offsets["stat"])


def test_every_module_writes_exactly_its_own_bytes_and_nothing_else(
    runs, base_bytes, offsets
):
    """Per position: the combined image is each module's own image, or the base.

    This is the end-to-end independence claim. It says that enabling the stat
    module does not move a placement, that enabling placement does not change a
    stat, and that the warp shuffle is unaffected by either - measured on the
    emitted bytes rather than inferred from the seed derivation.
    """
    combined = runs["combined"].output_path.read_bytes()
    owned = offsets["warp"] | offsets["placement"] | offsets["stat"]

    for name in ("warp", "placement", "stat"):
        single = runs[name].output_path.read_bytes()
        for offset in offsets[name]:
            assert combined[offset] == single[offset], (
                f"{name} byte 0x{offset:06X} differs between its own run and the "
                "combined one"
            )

    stray = [
        offset
        for offset in range(len(base_bytes))
        if offset not in owned and combined[offset] != base_bytes[offset]
    ]
    assert stray == [], (
        "the combined image changed bytes no module claims: "
        f"{[hex(offset) for offset in stray[:8]]}"
    )


def test_the_combined_output_is_not_any_single_modules_output(runs):
    hashes = {
        name: runs[name].output_sha256
        for name in ("warp", "placement", "stat", "enemy-both", "combined")
    }

    assert len(set(hashes.values())) == len(hashes), hashes


def test_every_module_contributes_an_enabled_versioned_manifest_section(runs):
    document = json.loads(runs["combined"].manifest_path.read_text(encoding="utf-8"))

    assert document["module_order"] == ["map-warp", "enemy-placement", "enemy-stat"]
    for module_id in ("map-warp", "enemy-placement", "enemy-stat"):
        section = document["modules"][module_id]
        assert section["enabled"] is True, module_id
        assert section["module_version"] == 1, module_id
        assert section["seed_namespace"], module_id
        assert section["derived_seed"], module_id


def test_a_disabled_module_is_still_described_in_the_combined_manifest(runs):
    document = json.loads(runs["combined"].manifest_path.read_text(encoding="utf-8"))
    placement_only = json.loads(
        runs["placement"].manifest_path.read_text(encoding="utf-8")
    )

    assert document["modules"]["enemy-placement"]["enabled"] is True
    assert placement_only["modules"]["map-warp"]["enabled"] is False
    assert placement_only["modules"]["enemy-stat"]["enabled"] is False


def test_each_modules_seed_is_unmoved_by_its_siblings(runs):
    """Enabling or disabling a module must not perturb another module's result.

    Two halves, and the difference matters. The *derivation* half is structural:
    :func:`derive_module_seeds` takes the master seed and computes each entry
    independently, so there is no enabled set in scope for it to depend on - and an
    earlier version of this test asserted that by comparing the function with
    itself, which could not fail. The half that can fail is the *effect*, and it is
    measured on the emitted bytes by
    :func:`test_every_module_writes_exactly_its_own_bytes_and_nothing_else` and
    :func:`test_the_composition_is_additive_and_therefore_collision_free`.
    """
    all_three = derive_module_seeds(SEED)

    assert all_three["map-warp"] == SEED, "the legacy namespace consumes the master seed"
    assert all_three["enemy-placement"] != all_three["enemy-stat"]
    # Each module's seed differs from the master seed, so no two modules share a
    # stream even though they share a master seed.
    for module_id in ("enemy-placement", "enemy-stat"):
        assert all_three[module_id] != SEED
    # The seeds a run records are the seeds the runs above consumed.
    for name in ("warp", "placement", "stat", "combined"):
        assert runs[name].module_seeds == all_three


def test_the_progress_plan_names_every_enabled_module_once():
    phases = progress_steps(ALL_MODULES)

    assert len(phases) == 6
    assert len(set(phases)) == 6
    assert phases[0] == "Verifying the ROM"
    assert phases[-1] == "Verifying the source ROM and writing the manifest"


def test_the_combined_run_writes_a_spoiler_with_a_section_per_module(runs):
    document = json.loads(runs["combined"].spoiler_path.read_text(encoding="utf-8"))

    # map-warp has nothing to hide *in the spoiler*: its per-transition mapping is
    # provenance and has lived in its manifest since v0.1.0, which is stated in the
    # spoiler module's own docstring. The two enemy modules are the ones that keep
    # their decisions out of the manifest.
    assert set(document["modules"]) == {"enemy-placement", "enemy-stat"}
    assert document["master_seed"] == SEED
    assert document["output"]["sha256"] == runs["combined"].output_sha256


def test_a_run_with_nothing_to_hide_writes_no_spoiler_and_does_not_fail(runs, workdir):
    """Asking for a spoiler is a request, not a promise about its contents.

    A warp-only run has no secret to record, so it produces no spoiler file - and
    the run still succeeds, with the manifest saying so. Failing here would abort
    a *combined* run after its ROM was already written, which is worse than either
    alternative.
    """
    document = json.loads(runs["warp"].manifest_path.read_text(encoding="utf-8"))

    assert runs["warp"].spoiler_path is None
    assert document["spoiler"] is None
    assert not (workdir / "warp.spoiler.json").exists()
    assert runs["warp"].output_path.is_file()


def test_the_source_image_is_an_input_on_every_path(runs, source_sha256):
    assert hashlib.sha256(LOCAL_ROM.read_bytes()).hexdigest() == CANONICAL_SHA256
    for name, result in runs.items():
        assert result.source_sha256 == source_sha256, name
        assert result.source_unchanged is True, name
        assert result.output_path != LOCAL_ROM, name
