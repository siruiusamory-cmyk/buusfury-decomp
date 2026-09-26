"""ROM-gated proofs for the warp randomizer. ROMHACK-WARP-RANDOMIZER-001.

The canonical Buu's Fury image is opened read-only on every path here. Every
mutated image is produced in memory by ``webfoot.write.apply_plan``; the one file
that is written is written into ``tmp_path`` by ``emit_image``, never over the
input.

What this file proves, and the ticket that asks for each:

* the canonical supported records enumerate; the eligible class and the two skip
  reasons account for exactly the records the authority loads;
* the same seed is the same mapping, the same manifest bytes and the same output
  bytes; a different seed is a different mapping and different bytes;
* the source trigger region of every record survives - the class and invariant
  words, both ordered intervals, the unresolved ``+0x13`` and the door-gate bits;
* a randomized bundle is internally consistent: its destination resolves through
  the engine's key table, its arrival lies inside the destination's own walkable
  extent, and its facing is the direction the manifest states;
* unrelated bytes are untouched: every differing byte is one of the declared
  randomized offsets of a randomized record, and a skipped record is
  byte-identical to the canonical image;
* skipped records are deterministic across runs with the same seed and every one
  of them carries a reason;
* the canonical ROM is byte-identical before and after the whole file;
* the emitted derivative ROM equals the planned image and its manifest's
  ``output_sha256`` is the file that was written.

The suite skips cleanly when the private canonical ROM is not configured.
``LOGX_CANONICAL_ROM`` overrides the default ``roms/`` path, so a review worktree -
which never carries the ignored image - can point at the main checkout's copy and
run the whole file read-only.
"""

from __future__ import annotations

import glob
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from tools.webfoot.map_transitions import (
    TransitionIdentity,
    load_map_transitions,
    read_map_transitions,
)
from tools.webfoot.maps import MapIdentity
from tools.webfoot.profile import RomProfile, RomProfileCatalog
from tools.webfoot.rom import identify_rom
from tools.webfoot.warp_randomizer import (
    PRESERVED_RECORD_OFFSETS,
    RANDOMIZED,
    RANDOMIZED_RECORD_OFFSETS,
    REASON_NO_RECIPROCAL_PAIR,
    REASON_SCENE_RELATIVE_ARRIVAL,
    SKIPPED,
    WarpRandomization,
    WarpRandomizerError,
    emit_randomized_rom,
    plan_warp_randomization,
)
from tools.webfoot.write import OutputPathError, apply_plan, emit_image

LOCAL_ROM = Path(
    os.environ.get("LOGX_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba")
)
CATALOG = "config/roms.yaml"

#: Measured from the canonical image. The first four are the transition family's
#: own census (LOGX-CONNECTOR-001); the rest are policy /2's arithmetic over it,
#: pinned so a change to the pairing rule cannot pass silently.
TRANSITION_COUNT = 735
CLASS_A_COUNT = 566
CLASS_B_COUNT = 169
MAP_COUNT = 452
PAIR_COUNT = 248
RANDOMIZED_COUNT = 496
SKIPPED_COUNT = 239
SKIPPED_NO_PAIR = 70

#: Two seeds whose mappings are proved to differ. Named rather than random so a
#: failure reproduces exactly.
SEED_A = "cale-1"
SEED_B = "cale-2"


def _canonical_rom() -> Path:
    if LOCAL_ROM.is_file():
        return LOCAL_ROM
    matches = sorted(glob.glob(os.path.join("roms", "*Buu*.gba")))
    if matches:
        return Path(matches[0])
    pytest.skip("no local canonical Buu's Fury image is configured")


@pytest.fixture(scope="module")
def environment() -> dict:
    """The canonical image, its profile and the two seeded randomizations."""
    path = _canonical_rom()
    catalog = RomProfileCatalog.load(Path(CATALOG))
    image = path.read_bytes()
    identification = identify_rom(path, catalog)
    profile: RomProfile = identification.profile_match.profile
    assert profile is not None, identification.profile_match.reason
    a = plan_warp_randomization(image, profile, SEED_A)
    b = plan_warp_randomization(image, profile, SEED_B)
    return {
        "path": path,
        "catalog": catalog,
        "profile": profile,
        "image": image,
        "sha256": hashlib.sha256(image).hexdigest(),
        "a": a,
        "b": b,
        "out_a": apply_plan(image, a.write_plan),
        "out_b": apply_plan(image, b.write_plan),
    }


def corpus_of(environment: dict):
    return read_map_transitions(environment["image"], environment["profile"])


def decisions_by_identity(randomization: WarpRandomization) -> dict:
    return {item.identity: item for item in randomization.manifest.decisions}


# --- the census --------------------------------------------------------------


def test_the_canonical_corpus_enumerates_the_measured_family(environment: dict) -> None:
    """All 735 records enumerate, split into the two measured classes."""
    corpus = corpus_of(environment)
    entries = list(corpus.entries())
    assert corpus.map_count == MAP_COUNT
    assert len(entries) == TRANSITION_COUNT
    class_a = [e for e in entries if e.record.has_raw_arrival_pair]
    assert len(class_a) == CLASS_A_COUNT
    assert len(entries) - len(class_a) == CLASS_B_COUNT

    manifest = environment["a"].manifest
    assert manifest.supported == TRANSITION_COUNT
    assert manifest.class_counts == {"A": CLASS_A_COUNT, "B": CLASS_B_COUNT}
    assert manifest.randomized and len(manifest.randomized) == RANDOMIZED_COUNT
    assert len(manifest.skipped) == SKIPPED_COUNT
    assert len(manifest.groups) == 1, "policy /2 has one compatibility class"
    assert manifest.groups[0].pairs == PAIR_COUNT
    assert manifest.groups[0].members == 2 * PAIR_COUNT
    assert [d.identity for d in manifest.decisions] == [
        e.identity.key for e in entries
    ], "the manifest must list every record in the corpus's own order"


def test_the_two_skip_reasons_account_for_every_skipped_record(
    environment: dict,
) -> None:
    manifest = environment["a"].manifest
    reasons = manifest.skipped_by_reason()
    assert reasons == {
        REASON_SCENE_RELATIVE_ARRIVAL: CLASS_B_COUNT,
        REASON_NO_RECIPROCAL_PAIR: SKIPPED_NO_PAIR,
    }
    assert sum(reasons.values()) == SKIPPED_COUNT
    assert all(item.skip_reason for item in manifest.skipped)
    assert all(item.randomized_destination is None for item in manifest.skipped)


def mutual_pairs(canonical) -> set[frozenset[str]]:
    """Every clean reciprocal door pair, recomputed here rather than imported.

    The eligibility claim is then checked against the corpus instead of against the
    policy that produced it: exactly one door back, mutual, and both halves
    arrival-authorable.
    """
    dest = {e.identity.key: canonical.destination(e.identity) for e in canonical.entries()}
    entries = {e.identity.key: e for e in canonical.entries()}
    eligible = {
        key for key, entry in entries.items() if entry.record.has_raw_arrival_pair
    }

    def doors_back(key):
        entry = entries[key]
        return [
            other.identity.key for other in canonical.for_map(dest[key])
            if dest[other.identity.key] == entry.identity.source
        ]

    pairs = set()
    for key in sorted(eligible):
        back = doors_back(key)
        if len(back) != 1:
            continue
        other = back[0]
        if other == key or other not in eligible:
            continue
        if doors_back(other) != [key]:
            continue
        pairs.add(frozenset({key, other}))
    return pairs


def test_a_record_is_randomized_exactly_when_it_is_half_of_a_clean_pair(
    environment: dict,
) -> None:
    """The eligible set is stated positively, and recomputed from the corpus."""
    canonical = corpus_of(environment)
    pairs = mutual_pairs(canonical)
    assert len(pairs) == PAIR_COUNT
    members = {key for pair in pairs for key in pair}
    assert len(members) == RANDOMIZED_COUNT

    decisions = decisions_by_identity(environment["a"])
    for entry in canonical.entries():
        row = decisions[entry.identity.key]
        if entry.identity.key in members:
            assert row.disposition == RANDOMIZED, entry.identity
        elif entry.record.has_raw_arrival_pair:
            assert row.disposition == SKIPPED
            assert row.skip_reason == REASON_NO_RECIPROCAL_PAIR, entry.identity
        else:
            assert row.disposition == SKIPPED
            assert row.skip_reason == REASON_SCENE_RELATIVE_ARRIVAL
        # A randomized row names its NEW return door - the record its arrival sits
        # on, which after the permutation is a different record from the canonical
        # pair - and the two rows name each other. That is what makes the manifest
        # checkable without the policy.
        if row.disposition == RANDOMIZED:
            assert row.pair is not None and row.counterpart is not None
            partner_row = decisions[row.counterpart]
            assert partner_row.disposition == RANDOMIZED
            assert partner_row.pair == row.pair
            assert partner_row.counterpart == row.identity
            assert partner_row.source_map_index == int(
                row.randomized_destination.split(":")[1]
            ), (row.identity, row.randomized_destination, row.counterpart)


# --- determinism -------------------------------------------------------------


def test_the_same_seed_is_the_same_mapping_manifest_and_bytes(
    environment: dict,
) -> None:
    image = environment["image"]
    profile = environment["profile"]
    first = plan_warp_randomization(image, profile, SEED_A)
    assert first.write_plan == environment["a"].write_plan
    assert first.manifest.decisions == environment["a"].manifest.decisions
    assert first.manifest.groups == environment["a"].manifest.groups
    json_a = environment["a"].manifest.to_json(output_sha256="x" * 64, output_size=1)
    assert json_a == first.manifest.to_json(output_sha256="x" * 64, output_size=1)
    assert apply_plan(image, first.write_plan) == environment["out_a"]


def test_a_different_seed_is_a_different_mapping_and_different_bytes(
    environment: dict,
) -> None:
    a = decisions_by_identity(environment["a"])
    b = decisions_by_identity(environment["b"])
    assert a.keys() == b.keys()
    differing = [
        key for key in a
        if a[key].randomized_destination != b[key].randomized_destination
    ]
    assert differing, "two seeds produced the same destination mapping"
    assert environment["out_a"] != environment["out_b"]
    assert environment["a"].write_plan != environment["b"].write_plan
    # The skipped set is policy, not seed: both seeds leave exactly the same
    # records alone.
    assert {k for k, v in a.items() if v.disposition == SKIPPED} == {
        k for k, v in b.items() if v.disposition == SKIPPED
    }


# --- the source trigger ------------------------------------------------------


def test_the_source_trigger_region_of_every_record_is_untouched(
    environment: dict,
) -> None:
    """The class and invariant words, both intervals, +0x13 and the door gate."""
    corpus = corpus_of(environment)
    image = environment["image"]
    output = environment["out_a"]
    for entry in corpus.entries():
        before = image[entry.file_offset : entry.file_offset + 24]
        after = output[entry.file_offset : entry.file_offset + 24]
        for offset in PRESERVED_RECORD_OFFSETS:
            assert after[offset] == before[offset], (entry.identity, hex(offset))
        assert after[0x10] & 0x03 == before[0x10] & 0x03, entry.identity


def test_the_pointer_structure_that_reaches_the_records_is_untouched(
    environment: dict,
) -> None:
    """No count, no array element and no array pointer moved: the records did."""
    corpus = corpus_of(environment)
    image = environment["image"]
    output = environment["out_a"]
    for entry in corpus.entries():
        element = entry.element_address - 0x08000000
        assert output[element : element + 4] == image[element : element + 4]


# --- the randomized bundle ---------------------------------------------------


def test_every_randomized_bundle_is_internally_consistent(environment: dict) -> None:
    """Resolve, land on the map, face the stated way, and keep the class."""
    output = environment["out_a"]
    profile = environment["profile"]
    out_corpus = read_map_transitions(output, profile)
    canonical = corpus_of(environment)
    decisions = decisions_by_identity(environment["a"])

    for entry in out_corpus.entries():
        row = decisions[entry.identity.key]
        if row.disposition != RANDOMIZED:
            continue
        destination = out_corpus.destination(entry.identity)
        assert destination.key == row.randomized_destination, entry.identity
        assert entry.record.class_raw == row.class_raw, entry.identity
        assert entry.record.has_raw_arrival_pair, entry.identity

        arrival = entry.record.arrival
        assert arrival is not None, entry.identity
        assert (arrival.x, arrival.y) == row.arrival, entry.identity
        width, height = out_corpus.destination_bounds(destination)
        assert 0 <= arrival.x < width, (entry.identity, arrival, width)
        assert 0 <= arrival.y < height, (entry.identity, arrival, height)
        assert entry.record.facing.arrival_direction == row.arrival_facing
        assert row.arrival_facing is not None, entry.identity
        # The gate half of +0x10 is the canonical record's, not the bundle's.
        before = canonical.entry(entry.identity).record
        assert entry.record.facing.gate_direction == before.facing.gate_direction


def test_every_randomized_destination_keeps_its_return_door(environment: dict) -> None:
    """The invariant policy /2 exists for: the mapping stays bidirectional.

    For every randomized record, the destination image must hold a record leading
    back to the source map, and the arrival must sit inside THAT door's trigger
    rectangle - the door the player will use to return, which is where retail puts
    them. The check runs on the OUTPUT image, so it cannot be satisfied by the
    policy's own intent; a single record whose door back was left pointing
    elsewhere fails here.
    """
    canonical = corpus_of(environment)
    output = environment["out_a"]
    out_corpus = read_map_transitions(output, environment["profile"])
    effective = {
        entry.identity.key: out_corpus.destination(entry.identity)
        for entry in out_corpus.entries()
    }
    decisions = decisions_by_identity(environment["a"])
    randomized = [e for e in canonical.entries()
                  if decisions[e.identity.key].disposition == RANDOMIZED]
    assert len(randomized) == RANDOMIZED_COUNT
    by_key = {e.identity.key: e for e in canonical.entries()}

    for entry in randomized:
        source = entry.identity.source
        destination = effective[entry.identity.key]
        doors = [
            other for other in out_corpus.for_map(destination)
            if effective[other.identity.key] == source
        ]
        assert doors, (
            f"{entry.identity} now leads to {destination}, which has no record "
            "leading back to its source map"
        )
        arrival = out_corpus.entry(entry.identity).record.arrival
        assert arrival is not None, entry.identity

        # The exact claim, from the manifest: the named counterpart IS the door
        # back, and the arrival sits inside its trigger rectangle.
        row = decisions[entry.identity.key]
        partner = by_key[row.counterpart]
        assert effective[row.counterpart] == source, (row.identity, row.counterpart)
        (low_x, high_x), (low_y, high_y) = (
            partner.record.region.first, partner.record.region.second
        )
        assert low_x <= arrival.x <= high_x, (row.identity, arrival, row.counterpart)
        assert low_y <= arrival.y <= high_y, (row.identity, arrival, row.counterpart)


def test_no_randomized_arrival_lands_on_a_door_that_leads_elsewhere(
    environment: dict,
) -> None:
    """The defect of policy /1, asserted gone on the output image.

    A player who arrives inside a trigger rectangle never crosses its edge, so a
    door they are standing in does not fire. Under /1, 168 of 559 arrivals landed
    inside a door the permutation had pointed somewhere else - the loop a human
    playthrough was trapped in. Under /2 an arrival may only be inside the door
    that leads back.
    """
    canonical = corpus_of(environment)
    out_corpus = read_map_transitions(environment["out_a"], environment["profile"])
    effective = {
        entry.identity.key: out_corpus.destination(entry.identity)
        for entry in out_corpus.entries()
    }
    decisions = decisions_by_identity(environment["a"])
    offenders = []
    for entry in canonical.entries():
        if decisions[entry.identity.key].disposition != RANDOMIZED:
            continue
        source = entry.identity.source
        arrival = out_corpus.entry(entry.identity).record.arrival
        destination = effective[entry.identity.key]
        for other in out_corpus.for_map(destination):
            if effective[other.identity.key] == source:
                continue  # the door back: benign, and where retail puts the player
            (low_x, high_x), (low_y, high_y) = (
                other.record.region.first, other.record.region.second
            )
            if low_x <= arrival.x <= high_x and low_y <= arrival.y <= high_y:
                offenders.append((entry.identity.key, other.identity.key))
    assert offenders == [], offenders[:8]


# --- byte safety -------------------------------------------------------------


def test_unrelated_bytes_are_untouched(environment: dict) -> None:
    """Every differing byte belongs to a randomized record's declared offsets."""
    image = environment["image"]
    output = environment["out_a"]
    corpus = corpus_of(environment)
    decisions = decisions_by_identity(environment["a"])

    allowed: set[int] = set()
    for entry in corpus.entries():
        if decisions[entry.identity.key].disposition != RANDOMIZED:
            continue
        allowed.update(
            entry.file_offset + offset for offset in RANDOMIZED_RECORD_OFFSETS
        )

    differing = {index for index, (a, b) in enumerate(zip(image, output)) if a != b}
    assert differing <= allowed, sorted(differing - allowed)[:8]
    assert differing, "the randomization changed nothing at all"
    assert len(output) == len(image)

    # And the complement, stated on the records themselves: a skipped record is
    # byte-identical, and so is every byte of every record outside the declared
    # randomized offsets - which the set inclusion above already implies.
    for entry in corpus.entries():
        row = decisions[entry.identity.key]
        before = image[entry.file_offset : entry.file_offset + 24]
        after = output[entry.file_offset : entry.file_offset + 24]
        if row.disposition == SKIPPED:
            assert after == before, entry.identity
        else:
            assert after[0x00:0x10] == before[0x00:0x10]
            assert after[0x13] == before[0x13]
            assert after[0x10] & 0x03 == before[0x10] & 0x03

    # Everything outside the 735 record extents is byte-identical, which is the
    # strongest form of "unrelated ROM bytes remain unchanged".
    extents = sorted(
        (entry.file_offset, entry.file_offset + 24) for entry in corpus.entries()
    )
    cursor = 0
    for start, end in extents:
        assert output[cursor:start] == image[cursor:start]
        cursor = end


def test_no_randomized_link_joins_two_single_door_maps(environment: dict) -> None:
    """Policy /3's guard, asserted on the mapping.

    A map with exactly one door record is a dead end on its own, so linking two of
    them closes an isolated 2-cycle that a player entering from a scripted
    transition cannot leave - the 33 <-> 390 trap the second playthrough hit, where
    the only way on was Broly. Under /2 there were 12 such links; /3 must produce
    none, and must not have relaxed the rule to get there.
    """
    canonical = corpus_of(environment)
    doors_per_map = {
        index: len(canonical.for_map(MapIdentity(index)))
        for index in range(canonical.map_count)
    }
    single = {index for index, count in doors_per_map.items() if count == 1}
    assert len(single) == 86, "the single-door population is a measured fact"

    offenders = []
    for row in environment["a"].manifest.randomized:
        destination = int(row.randomized_destination.split(":")[1])
        if row.source_map_index in single and destination in single:
            offenders.append((row.identity, row.source_map_index, destination))
    assert offenders == [], offenders
    assert environment["a"].manifest.forced_leaf_links == 0


def test_the_randomized_record_set_is_exactly_what_changed(environment: dict) -> None:
    """The changed set is taken from the BYTES, not from the manifest's own flag.

    ``WarpRecordDecision.changed`` is computed by the implementation under test;
    a suite that only asserted it would pass on an implementation that reported
    changes it did not write. So the record set is recovered from the image diff
    and compared with the manifest's randomized set.
    """
    image = environment["image"]
    output = environment["out_a"]
    corpus = corpus_of(environment)
    decisions = decisions_by_identity(environment["a"])

    differing = {index for index, (a, b) in enumerate(zip(image, output)) if a != b}
    observed = {
        entry.identity.key
        for entry in corpus.entries()
        if any(
            offset in differing
            for offset in range(entry.file_offset, entry.file_offset + 24)
        )
    }
    expected = {
        row.identity for row in decisions.values() if row.disposition == RANDOMIZED
    }
    assert observed == expected
    assert len(observed) == RANDOMIZED_COUNT
    # The manifest's flag agrees with the bytes for every row, in both directions.
    for row in decisions.values():
        assert row.changed is (row.identity in observed), row.identity


def test_the_manifest_reports_the_whole_retail_bundle(environment: dict) -> None:
    """Retail destination, arrival and facing byte come from the canonical record."""
    canonical = corpus_of(environment)
    for row in environment["a"].manifest.decisions:
        entry = canonical.entry(
            TransitionIdentity(MapIdentity(row.source_map_index), row.index)
        )
        record = entry.record
        assert row.retail_destination == canonical.destination(entry.identity).key
        assert row.retail_facing_raw == record.byte_0x10_raw
        assert row.gate_direction == record.facing.gate_direction
        assert row.class_raw == record.class_raw
        if record.has_raw_arrival_pair and record.arrival is not None:
            assert row.retail_arrival == (record.arrival.x, record.arrival.y)
        else:
            # The 566 class's sentinel and every 169-class delta are reported as
            # "no arrival", never as a point.
            assert row.retail_arrival is None


# --- the emitted artefact ----------------------------------------------------


def test_the_emitted_rom_is_the_planned_image_with_its_manifest(
    environment: dict, tmp_path: Path
) -> None:
    path = environment["path"]
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    output = tmp_path / "randomized.gba"
    manifest = tmp_path / "randomized.manifest.json"

    randomization, output_sha256 = emit_randomized_rom(
        path,
        output,
        SEED_A,
        catalog=environment["catalog"],
        manifest_path=manifest,
    )

    text = manifest.read_text(encoding="utf-8")
    assert text.endswith("\n") and "\r\n" not in text
    payload = json.loads(text)
    assert payload["seed"]["given"] == SEED_A
    assert payload["output_rom"]["sha256"] == output_sha256
    assert payload["base_rom"]["sha256"] == environment["sha256"]
    assert payload["counts"]["randomized"] == RANDOMIZED_COUNT

    written = output.read_bytes()
    assert hashlib.sha256(written).hexdigest() == output_sha256
    assert written == environment["out_a"]
    assert randomization.write_plan == environment["a"].write_plan
    assert len(payload["records"]) == TRANSITION_COUNT

    # The canonical image is still the canonical image.
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before


def test_an_existing_output_is_refused(environment: dict, tmp_path: Path) -> None:
    output = tmp_path / "already-there.gba"
    output.write_bytes(b"not a rom")
    with pytest.raises(OutputPathError):
        emit_image(
            environment["path"],
            output,
            environment["a"].write_plan,
        )


def test_paths_that_would_overwrite_each_other_are_refused(
    environment: dict, tmp_path: Path
) -> None:
    """The manifest must not be able to replace the image it describes.

    The randomizer writes its own manifest after ``emit_image`` has written the
    ROM, so without an explicit guard a ``manifest_path`` equal to the output
    would replace the freshly emitted image with JSON while the call still
    reported success - the manifest claiming an output hash the file no longer
    had.
    """
    output = tmp_path / "collide.gba"
    with pytest.raises(WarpRandomizerError):
        emit_randomized_rom(
            environment["path"],
            output,
            SEED_A,
            catalog=environment["catalog"],
            manifest_path=output,
        )
    assert not output.exists()

    provenance = tmp_path / "provenance.json"
    with pytest.raises(WarpRandomizerError):
        emit_randomized_rom(
            environment["path"],
            tmp_path / "other.gba",
            SEED_A,
            catalog=environment["catalog"],
            manifest_path=provenance,
            provenance_path=provenance,
        )
    assert not provenance.exists()


def test_the_manifest_is_the_same_in_a_fresh_interpreter(
    environment: dict, tmp_path: Path
) -> None:
    """Determinism across processes, where dict and set order can differ.

    The in-process test cannot see a hash-seed-dependent iteration order, and this
    mapping is built from sorted lists on purpose. Two interpreters with different
    ``PYTHONHASHSEED`` values are the cheapest way to assert that stays true.
    """
    script = (
        "import hashlib, sys\n"
        "from pathlib import Path\n"
        "from tools.webfoot.profile import RomProfileCatalog\n"
        "from tools.webfoot.rom import identify_rom\n"
        "from tools.webfoot.warp_randomizer import plan_warp_randomization\n"
        "rom = Path(sys.argv[1]); seed = sys.argv[2]\n"
        "catalog = RomProfileCatalog.load(Path('config/roms.yaml'))\n"
        "profile = identify_rom(rom, catalog).profile_match.profile\n"
        "plan = plan_warp_randomization(rom.read_bytes(), profile, seed)\n"
        "text = plan.manifest.to_json(output_sha256='x' * 64, output_size=1)\n"
        "print(hashlib.sha256(text.encode('utf-8')).hexdigest())\n"
    )
    digests = []
    for hash_seed in ("1", "2"):
        env = dict(os.environ, PYTHONHASHSEED=hash_seed)
        completed = subprocess.run(
            [sys.executable, "-c", script, str(environment["path"]), SEED_A],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).resolve().parents[2]),
            env=env,
            check=True,
        )
        digests.append(completed.stdout.strip().splitlines()[-1])
    assert digests[0] == digests[1]
    local = environment["a"].manifest.to_json(output_sha256="x" * 64, output_size=1)
    assert digests[0] == hashlib.sha256(local.encode("utf-8")).hexdigest()


# --- the canonical image -----------------------------------------------------


def test_the_canonical_rom_is_never_written(environment: dict) -> None:
    """Read at the end of the module and compared with the identity it started as."""
    path = environment["path"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == environment["sha256"]
    assert environment["sha256"] == environment["profile"].sha256
    # The identity the authority itself re-checks on every load.
    corpus = load_map_transitions(path, environment["catalog"])
    assert corpus.base_sha256 == environment["sha256"]
    assert corpus.record_count == TRANSITION_COUNT
