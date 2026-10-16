"""ROM-gated proofs for the warp randomizer *application* boundary.

WARPRAND-APP-001. The randomizer's own policy is proved against the canonical
image in ``tests/integration/test_warp_randomizer_rom.py``; this file proves what
the application layer adds on top of it, and only what needs a real ROM:

* the canonical image is accepted, and the counts the window will display are the
  counts the run returned;
* the **Goku golden output** - the accepted v0.1.0 release hash - is reproduced,
  so a change to the core, the boundary or the seed handling cannot silently
  re-lay a published seed;
* the manifest is created, carries the product identity and the policy, and is
  **byte-identical** for the same image, seed and output name in two different
  directories - no absolute path and no machine detail reaches it;
* the selected source ROM is byte-identical afterwards, and its SHA-256 is still
  the canonical one;
* a second run of the same seed produces a byte-identical ROM;
* a different seed produces a different ROM, so the seed really is the input;
* an existing output is refused until an overwrite is confirmed, and confirming
  one replaces it;
* the progress reports name every real phase, in order.

Skips cleanly when the private canonical image is not configured.
``LOGX_CANONICAL_ROM`` overrides the default ``roms/`` path, so a review worktree
can point at the main checkout's copy and run the whole file read-only.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

from tools.webfoot.warprand import service as warprand

LOCAL_ROM = Path(
    os.environ.get("LOGX_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba")
)

#: The canonical image, as the ticket states it.
CANONICAL_SIZE = 8_388_608
CANONICAL_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)

#: The accepted **v0.1.0 golden output** for the launch seed ``Goku``, recorded
#: from the packaged executable's own smoke run of the released build.
GOKU_GOLDEN_SHA256 = (
    "ed167ca17944e4782cf19bf31245f772e5b7b9f5c66af317ddbedc8906c5abdc"
)

#: The counts the accepted run reports for ``Goku``. Pinned so a policy change
#: cannot pass as an ordinary refactor - the ticket's own numbers.
SUPPORTED = 735
RANDOMIZED = 496
SKIPPED = 239
DESTINATIONS_MOVED = 492

#: A second seed, proved to differ from the golden one.
OTHER_SEED = "cale-2"


pytestmark = pytest.mark.skipif(
    not LOCAL_ROM.is_file(),
    reason=(
        f"the canonical Buu's Fury image is not configured; set "
        f"LOGX_CANONICAL_ROM or place it at {LOCAL_ROM}"
    ),
)


@pytest.fixture(scope="module")
def service() -> warprand.WarpRandomizerService:
    return warprand.WarpRandomizerService()


@pytest.fixture(scope="module")
def canonical_before() -> str:
    """The source ROM's digest, read once before any test writes anything."""
    return hashlib.sha256(LOCAL_ROM.read_bytes()).hexdigest()


# --- the input image ---------------------------------------------------------


def test_the_canonical_image_is_the_supported_one(service, canonical_before):
    assert canonical_before == CANONICAL_SHA256
    verification = service.verify_rom(LOCAL_ROM)

    assert verification.ok
    assert verification.size == CANONICAL_SIZE
    assert verification.sha256 == CANONICAL_SHA256


def test_a_wrong_hash_at_the_canonical_size_is_refused(service, tmp_path):
    """The size alone is not the gate: a same-size file with other bytes fails."""
    forged = tmp_path / "forged.gba"
    image = bytearray(LOCAL_ROM.read_bytes())
    image[0x100] ^= 0xFF
    forged.write_bytes(bytes(image))

    verification = service.verify_rom(forged)

    assert not verification.ok
    assert verification.size == CANONICAL_SIZE
    assert "Expected SHA-256" in verification.problem


def test_a_truncated_image_is_refused(service, tmp_path):
    short = tmp_path / "short.gba"
    short.write_bytes(LOCAL_ROM.read_bytes()[: CANONICAL_SIZE // 2])

    verification = service.verify_rom(short)

    assert not verification.ok
    assert f"{CANONICAL_SIZE // 2:,} bytes" in verification.problem


# --- the Goku golden run -----------------------------------------------------


def test_the_golden_goku_output_is_reproduced(service, tmp_path, canonical_before):
    """The accepted v0.1.0 release hash, re-derived through the boundary."""
    output = tmp_path / "Buu's Fury - Warp Randomized - Goku.gba"

    outcome = service.randomize_warps(LOCAL_ROM, output, "Goku")

    assert outcome.seed == "Goku"
    assert outcome.policy_id == "reciprocal-door-pairs/3"
    assert outcome.supported == SUPPORTED
    assert outcome.randomized == RANDOMIZED
    assert outcome.skipped == SKIPPED
    assert outcome.destinations_moved == DESTINATIONS_MOVED
    assert outcome.output_sha256 == GOKU_GOLDEN_SHA256
    assert hashlib.sha256(output.read_bytes()).hexdigest() == GOKU_GOLDEN_SHA256


def test_the_displayed_summary_is_the_run_s_own_numbers(service, tmp_path):
    """The window renders these; a stale hard-coded count cannot creep in."""
    output = tmp_path / "summary.gba"

    outcome = service.randomize_warps(LOCAL_ROM, output, "Goku")
    lines = outcome.status_lines()
    text = "\n".join(lines)

    assert lines[0] == "Success"
    assert f"Seed: {outcome.seed}" in text
    assert f"Randomized: {outcome.randomized}" in text
    assert f"Skipped: {outcome.skipped}" in text
    assert f"Output: {outcome.output_path}" in text
    assert f"SHA-256: {outcome.output_sha256}" in text
    # The skip reasons travel with the result, at the core's own wording.
    assert sum(outcome.skipped_reasons.values()) == outcome.skipped
    assert outcome.skipped_reasons


def test_the_same_seed_is_the_same_bytes(service, tmp_path):
    first = tmp_path / "a.gba"
    second = tmp_path / "b.gba"

    one = service.randomize_warps(LOCAL_ROM, first, "Goku")
    two = service.randomize_warps(LOCAL_ROM, second, "Goku")

    assert one.output_sha256 == two.output_sha256 == GOKU_GOLDEN_SHA256


def test_a_different_seed_is_a_different_layout(service, tmp_path):
    output = tmp_path / "other.gba"

    outcome = service.randomize_warps(LOCAL_ROM, output, OTHER_SEED)

    assert outcome.output_sha256 != GOKU_GOLDEN_SHA256
    # The policy is unchanged: the same records are supported and the same
    # number of them move. Only the permutation differs.
    assert outcome.supported == SUPPORTED
    assert outcome.randomized == RANDOMIZED
    assert outcome.skipped == SKIPPED


def test_a_punctuated_seed_is_used_verbatim_but_named_safely(service, tmp_path):
    """The file name is sanitised; the seed the algorithm sees is not."""
    output = tmp_path / "punctuated.gba"

    outcome = service.randomize_warps(LOCAL_ROM, output, "Goku: SSJ3?!")

    assert outcome.seed == "Goku: SSJ3?!"
    assert outcome.output_sha256 not in ("", GOKU_GOLDEN_SHA256)
    assert (
        warprand.sanitize_seed_for_filename(outcome.seed) == "Goku SSJ3"
    )
    assert outcome.randomizer_manifest["seed"]["given"] == "Goku: SSJ3?!"


def test_the_source_rom_is_never_written(service, tmp_path, canonical_before):
    """The permanent rule: the canonical image is an input on every path."""
    assert canonical_before == CANONICAL_SHA256

    outcome = service.randomize_warps(LOCAL_ROM, tmp_path / "immutable.gba", "Goku")

    assert outcome.source_sha256 == CANONICAL_SHA256
    assert outcome.source_unchanged is True
    assert hashlib.sha256(LOCAL_ROM.read_bytes()).hexdigest() == CANONICAL_SHA256


def test_the_output_may_not_be_the_canonical_image(service, canonical_before):
    with pytest.raises(warprand.OutputPathRefusedError):
        service.randomize_warps(LOCAL_ROM, LOCAL_ROM, "Goku")

    assert hashlib.sha256(LOCAL_ROM.read_bytes()).hexdigest() == canonical_before


# --- the manifest ------------------------------------------------------------


def test_the_manifest_is_created_beside_the_output(service, tmp_path):
    output = tmp_path / "Buu's Fury - Warp Randomized - Goku.gba"

    outcome = service.randomize_warps(LOCAL_ROM, output, "Goku")

    assert outcome.manifest_path.exists()
    assert outcome.manifest_path.name == (
        "Buu's Fury - Warp Randomized - Goku.manifest.json"
    )
    document = json.loads(outcome.manifest_path.read_text(encoding="utf-8"))

    # ENEMY-RANDOMIZER-EXE-001 moved this product onto the shared, versioned
    # randomizer manifest, because a combined run has one output and therefore
    # needs one document describing it. The warp-specific facts did not leave the
    # document, only moved under the module that owns them.
    assert document["format_version"] == warprand.MANIFEST_SCHEMA_VERSION
    assert document["tool"] == {
        "name": "Buu's Fury Warp Randomizer",
        "version": "0.1.0",
    }
    assert document["master_seed"] == "Goku"
    assert document["module_order"] == ["map-warp", "enemy-placement", "enemy-stat"]
    assert document["source"]["size"] == CANONICAL_SIZE
    assert document["source"]["sha256"] == CANONICAL_SHA256
    assert document["output"]["filename"] == output.name
    assert document["output"]["sha256"] == GOKU_GOLDEN_SHA256

    warp = document["modules"]["map-warp"]
    assert warp["enabled"] is True
    assert warp["algorithm"] == "reciprocal-door-pairs/3"
    # The launch seed is the master seed verbatim for this one module: its seed
    # semantics predate the shared framework and every warp seed ever produced
    # depends on them, so the namespace says so out loud.
    assert warp["seed_namespace"] == "master-legacy"
    assert warp["derived_seed"] == "Goku"
    assert warp["module_version"] == 1
    assert warp["counts"] == {
        "supported": SUPPORTED,
        "randomized": RANDOMIZED,
        "destinations_moved": DESTINATIONS_MOVED,
        "destinations_unchanged": RANDOMIZED - DESTINATIONS_MOVED,
        "skipped": SKIPPED,
    }
    assert sum(warp["skipped_reasons"].values()) == SKIPPED
    # Every registered module is described, including the ones this product does
    # not offer, so two manifests are comparable without knowing which product
    # wrote them - and "off" is distinguishable from "did nothing".
    assert document["modules"]["enemy-placement"]["enabled"] is False
    assert document["modules"]["enemy-stat"]["enabled"] is False
    assert document["spoiler"] is None
    # The limitation travels with the artefact, not only with the window that
    # made it. The reviewer noted this was asserted nowhere.
    assert document["progression"] == warprand.PROGRESSION_DISCLAIMER
    assert "impossible to complete" in document["progression"]


def test_the_manifest_carries_the_per_transition_mapping(service, tmp_path):
    """Enough to audit a decision without the tool: the ticket's minimum."""
    output = tmp_path / "mapping.gba"

    outcome = service.randomize_warps(LOCAL_ROM, output, "Goku")
    records = outcome.randomizer_manifest["records"]

    assert len(records) == SUPPORTED
    randomized = [row for row in records if row["disposition"] == "randomized"]
    skipped = [row for row in records if row["disposition"] == "skipped"]
    assert len(randomized) == RANDOMIZED
    assert len(skipped) == SKIPPED

    for row in randomized:
        # Source identity, both destinations, the arrival bundle, the
        # compatibility grouping and the pairing are all present.
        assert row["transition"]
        assert row["source_map"] is not None
        assert row["retail_destination"]
        assert row["randomized_destination"]
        assert row["arrival"]
        assert row["arrival_facing"] is not None
        assert row["gate_direction"] is not None
        assert row["pair"]
        assert row["counterpart"]
        assert row["skip_reason"] == ""

    for row in skipped:
        assert row["skip_reason"], "a skipped record must say why"
        assert row["randomized_destination"] is None

    # The two skip families the ticket names, each with its own wording: the
    # 169-class scene-relative arrivals and the records with no clean pair.
    assert sorted(outcome.skipped_reasons.values()) == [70, 169]


def test_the_embedded_core_record_states_no_empty_output_digest(service, tmp_path):
    """A plan has no output yet, so the record it carries must not pretend it does.

    An independent review found the warp module embedding the core's record with
    ``output_rom.sha256: ""`` and ``counts.output_sha256: ""`` while its own comment
    claimed the field was absent. An empty digest is an invalid value a reader can
    mistake for a real one, so the fields are removed and the two facts are stated
    once, by the application, at the top level of the manifest.
    """
    outcome = service.randomize_warps(LOCAL_ROM, tmp_path / "core-record.gba", "Goku")
    core = outcome.randomizer_manifest

    assert "output_rom" not in core
    assert "output_sha256" not in core["counts"]
    # The facts are not lost: they are on the document itself, with real values.
    document = json.loads(outcome.manifest_path.read_text(encoding="utf-8"))
    assert document["output"]["sha256"] == GOKU_GOLDEN_SHA256
    assert document["output"]["size"] == CANONICAL_SIZE


def test_the_manifest_is_byte_identical_across_directories(service, tmp_path):
    """No absolute path and no machine detail may reach the manifest.

    The output *basename* is deliberately the same in both runs, because the
    ticket requires the manifest to name the output file; everything else about
    where the run happened must be absent.
    """
    first_dir = tmp_path / "one"
    second_dir = tmp_path / "two"
    first_dir.mkdir()
    second_dir.mkdir()
    name = "Buu's Fury - Warp Randomized - Goku.gba"

    one = service.randomize_warps(LOCAL_ROM, first_dir / name, "Goku")
    two = service.randomize_warps(LOCAL_ROM, second_dir / name, "Goku")

    first_bytes = one.manifest_path.read_bytes()
    second_bytes = two.manifest_path.read_bytes()

    assert first_bytes == second_bytes
    assert str(tmp_path).encode() not in first_bytes
    assert str(LOCAL_ROM.parent).encode() not in first_bytes


# --- collisions --------------------------------------------------------------


def test_an_existing_output_is_refused_until_overwrite_is_confirmed(service, tmp_path):
    output = tmp_path / "collision.gba"
    original = service.randomize_warps(LOCAL_ROM, output, "Goku")
    preserved = output.read_bytes()

    with pytest.raises(warprand.OutputAlreadyExistsError):
        service.randomize_warps(LOCAL_ROM, output, "Goku")

    assert output.read_bytes() == preserved
    assert (
        hashlib.sha256(output.read_bytes()).hexdigest() == original.output_sha256
    )


def test_a_confirmed_overwrite_replaces_the_previous_output(service, tmp_path):
    output = tmp_path / "replace.gba"
    service.randomize_warps(LOCAL_ROM, output, "Goku")

    outcome = service.randomize_warps(LOCAL_ROM, output, OTHER_SEED, overwrite=True)

    assert outcome.seed == OTHER_SEED
    assert hashlib.sha256(output.read_bytes()).hexdigest() == outcome.output_sha256
    assert outcome.output_sha256 != GOKU_GOLDEN_SHA256


# --- progress ----------------------------------------------------------------


def test_progress_reports_every_real_phase_in_order(service, tmp_path):
    output = tmp_path / "progress.gba"
    seen: list[tuple[int, int, str]] = []

    service.randomize_warps(
        LOCAL_ROM, output, "Goku", on_progress=lambda *a: seen.append(a)
    )

    assert [step for step, _total, _label in seen] == [1, 2, 3, 4]
    assert {total for _step, total, _label in seen} == {4}
    assert [label for _step, _total, label in seen] == list(warprand.PROGRESS_STEPS)
