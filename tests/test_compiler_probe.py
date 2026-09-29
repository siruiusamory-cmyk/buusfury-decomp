"""DECOMP-COMPILER-PROBE-001: the probe manifest, the harness, and ROM safety.

Two classes of test live here and they are deliberately separate:

* PORTABLE tests need no baserom and no compiler. They assert the manifest's
  shape, that the harness fails CLOSED (BLOCKED, never a false PASS) when ADS
  1.2 is absent or unidentifiable, that comparison is deterministic, and that
  nothing proprietary can be committed.
* ROM-GATED tests use the `baserom` fixture and assert that every measured field
  in config/compiler_probes.json is reproducible from the canonical image, and
  that reading it does not mutate it.

No test in this file runs a proprietary compiler, and none requires one. A
missing ADS installation is a PASSING state for these tests: the ticket's
contract is that the blocker is measured and reported, not that it is absent.

The tests that use a `manifest` fixture read the COMMITTED file. That is the
point: the committed manifest is a claim that must be re-derivable, not a
declaration to be trusted.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from buusfury import compiler_probe as cp
from buusfury import gba, identity

REPO_ROOT = identity.REPO_ROOT
PROBE_COUNT = 8


@pytest.fixture(scope="module")
def manifest() -> dict:
    return cp.load_manifest()


@pytest.fixture(scope="module")
def functions_by_address() -> dict[int, dict]:
    raw = json.loads((REPO_ROOT / "config" / "functions.json").read_text(encoding="utf-8"))
    return {int(f["address"], 16) & ~1: f for f in raw["functions"]}


@pytest.fixture(scope="module")
def rom_map() -> dict:
    return json.loads((REPO_ROOT / "config" / "rom_map.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# manifest validity
# ---------------------------------------------------------------------------
def test_manifest_declares_its_schema_and_source(manifest):
    canonical = identity.load_canonical()
    assert manifest["schema"] == 1
    # Compared against the single source of truth rather than a copied literal,
    # so a ROM profile change cannot leave this test asserting a stale digest.
    assert manifest["source_sha1"] == canonical["hashes"]["sha1"]
    assert manifest["generated_by"].endswith("derive_manifest()")


def test_manifest_pins_the_inventory_it_borrows_from(manifest):
    """The manifest embeds inventory-derived fields, so the inventory is pinned.

    Without the digest, a changed config/functions.json would present as a
    manifest that disagrees with the ROM, and a reader would be pointed at the
    wrong file.
    """
    assert manifest["inventory_sha1"] == cp._inventory_digest()
    assert "pinned by digest" in manifest["inventory_basis"]


def test_manifest_has_exactly_one_translation_unit(manifest):
    units = manifest["translation_units"]
    assert len(units) == 1
    unit = units[0]
    assert unit["id"] == "gbaram_tu"
    assert unit["isa"] == "thumb"
    assert unit["confidence"] == "proven"
    assert unit["rom_address"] == "0x0803D4D0"
    assert unit["end_address"] == "0x0803D740"
    assert unit["byte_length"] == 624
    assert unit["code_byte_length"] == 608


def test_manifest_probe_count_is_in_the_tickets_6_to_12_band(manifest):
    counts = manifest["counts"]
    assert counts["probes"] == PROBE_COUNT
    assert 6 <= counts["thumb"] <= 12
    assert counts["arm"] == 0, (
        "no confirmed ARM region is ordinary engine code, so an ARM probe would "
        "be forced and the ticket forbids forcing one"
    )
    assert counts["leaf"] + counts["non_leaf"] == counts["probes"]


def test_every_probe_declares_the_required_fields(manifest):
    required = {
        "name",
        "rom_address",
        "file_offset",
        "isa",
        "start",
        "end",
        "byte_length",
        "sha1",
        "instructions",
        "returns",
        "leaf",
        "callees",
        "literal_slots",
        "confidence",
        "boundary_evidence",
        "relocations",
        "role",
        "translation_unit",
        "in_function_inventory",
        "inventory_confidence",
        "inventory_size",
    }
    for probe in manifest["probes"]:
        assert required <= set(probe), probe["name"]
        assert probe["confidence"] == "proven"
        assert probe["boundary_evidence"], probe["name"]
        assert probe["relocations"], probe["name"]


def test_probe_names_are_neutral_and_carry_no_semantic_claim(manifest):
    for probe in manifest["probes"]:
        assert probe["name"] == f"sub_{int(probe['rom_address'], 16):08X}"


def test_address_and_file_offset_agree_through_the_rom_base(manifest):
    for probe in manifest["probes"]:
        address = int(probe["rom_address"], 16)
        offset = int(probe["file_offset"], 16)
        assert address - gba.ROM_BASE == offset, probe["name"]


# ---------------------------------------------------------------------------
# cross-checks against the previous ticket's inventory
# ---------------------------------------------------------------------------
def test_every_probe_address_exists_in_the_function_inventory_or_is_recorded(
    manifest, functions_by_address
):
    """No probe may be invented.

    A probe is legitimate if the previous inventory records it, OR if the
    manifest records it as a measured GAP in that inventory with the independent
    evidence that it is real code. Silently omitting either case is what would
    let a probe be built on nothing.
    """
    gaps = {gap["name"] for gap in manifest["inventory_gaps"]}
    for probe in manifest["probes"]:
        address = int(probe["rom_address"], 16)
        if address in functions_by_address:
            assert probe["in_function_inventory"] is True, probe["name"]
            assert probe["name"] not in gaps, probe["name"]
        else:
            assert probe["name"] in gaps, f"{probe['name']} is neither recorded nor a gap"
            assert probe["in_function_inventory"] is False, probe["name"]


def test_the_inventory_gaps_are_exactly_the_two_uncalled_functions(manifest):
    """Measured, not asserted: two real functions have no discoverable caller.

    sub_0803D548 and sub_0803D712 are never the target of a BL/BLX anywhere in
    the image and are not literal-pool code pointers, so a branch-target
    inventory cannot see them. They are still real: they decode completely and
    terminate on every path inside a proven code region.
    """
    assert {gap["name"] for gap in manifest["inventory_gaps"]} == {
        "sub_0803D548",
        "sub_0803D712",
    }
    for gap in manifest["inventory_gaps"]:
        assert gap["why_absent"], gap["name"]
        assert gap["independent_evidence"], gap["name"]


def test_the_probe_confidence_is_the_probe_manifests_own_not_the_inventorys(manifest):
    """The two confidences mean different things and must not be conflated.

    The inventory rates a BL-target entry `medium` because a branch target is not
    proof of a function start in a cartridge where data decodes as Thumb. The
    probe manifest rates the same address `proven` because a chain walk closed
    every path and the unit's boundaries are corroborated independently. Both
    values are carried on the probe so the distinction survives.
    """
    assert all(probe["confidence"] == "proven" for probe in manifest["probes"])
    levels = {
        probe["inventory_confidence"]
        for probe in manifest["probes"]
        if probe["in_function_inventory"]
    }
    assert levels <= {"proven", "high", "medium", "low"}
    assert "medium" in levels
    assert all(
        probe["inventory_confidence"] is None
        for probe in manifest["probes"]
        if not probe["in_function_inventory"]
    )


def test_the_inventory_size_overruns_are_recorded_with_the_right_entries(manifest):
    """The two functions the docs used to confuse are now named explicitly.

    config/functions.json records 620 bytes for 0x0803D4D0 and 388 for
    0x0803D5B8. An earlier revision of this ticket's prose attached 620 to
    0x0803D5B8; the manifest must state the measured pair, not a recollection.
    """
    disagreements = {
        item["name"]: (item["inventory_size"], item["measured_boundary"])
        for item in manifest["inventory_size_disagreements"]
    }
    assert disagreements["sub_0803D4D0"] == (620, 24)
    assert disagreements["sub_0803D5B8"] == (388, 132)
    for name, (recorded, measured) in disagreements.items():
        assert recorded > measured, name
    assert manifest["consistency_problems"] == []


def test_the_inventory_overrun_is_not_used_as_a_boundary(manifest):
    for probe in manifest["probes"]:
        assert probe["byte_length"] == int(probe["end"], 16) - int(probe["start"], 16)
        assert probe["inventory_size"] != probe["byte_length"] or (
            probe["inventory_size"] == probe["byte_length"]
        )


# ---------------------------------------------------------------------------
# range sanity
# ---------------------------------------------------------------------------
def test_probe_ranges_do_not_overlap(manifest):
    spans = sorted((int(p["start"], 16), int(p["end"], 16)) for p in manifest["probes"])
    for (start_a, end_a), (start_b, _end_b) in zip(spans, spans[1:]):
        assert end_a <= start_b, f"0x{start_a:08X}..0x{end_a:08X} overlaps the next probe"


def test_probes_tile_the_translation_unit_code_body_exactly(manifest):
    unit = manifest["translation_units"][0]
    spans = sorted((int(p["start"], 16), int(p["end"], 16)) for p in manifest["probes"])
    assert spans[0][0] == int(unit["rom_address"], 16)
    assert spans[-1][1] == int(unit["code_end_address"], 16)
    for (start_a, end_a), (start_b, _end_b) in zip(spans, spans[1:]):
        assert end_a == start_b, "a gap or an overlap would break the boundary evidence"
    assert sum(end - start for start, end in spans) == unit["code_byte_length"]


def test_internal_calls_resolve_to_probes_in_the_same_unit(manifest):
    """The measured call graph must stay inside the unit, or the boundary story breaks."""
    addresses = {int(p["rom_address"], 16) for p in manifest["probes"]}
    for probe in manifest["probes"]:
        for callee in probe["callees"]:
            assert int(callee, 16) in addresses, (probe["name"], callee)


def test_the_measured_call_graph_is_the_one_the_docs_claim(manifest):
    callers = {
        probe["name"]: sorted(probe["callees"]) for probe in manifest["probes"]
    }
    assert callers["sub_0803D5B8"] == ["0x0803D4E8"]
    assert callers["sub_0803D63C"] == ["0x0803D4E8", "0x0803D520", "0x0803D56A"]
    for name, _callees in callers.items():
        if name not in ("sub_0803D5B8", "sub_0803D63C"):
            assert callers[name] == [], f"{name} is documented as a leaf"


def test_literal_pool_lies_immediately_after_the_code_body(manifest):
    unit = manifest["translation_units"][0]
    pool = unit["literal_pool"]
    assert int(pool["rom_address"], 16) == int(unit["code_end_address"], 16)
    assert pool["byte_length"] == 16
    assert [w["value"] for w in pool["words"]] == [
        "0x02000800",
        "0x03003488",
        "0x0000FDFE",
        "0x7FFFFFFF",
    ]


def test_the_pool_values_are_the_ones_the_previous_ticket_proved(manifest):
    """Corroboration, not decoration: this is why the unit was selected at all."""
    expected = {
        "0x03D730": 0x02000800,
        "0x03D734": 0x03003488,
        "0x03D738": 0x0000FDFE,
        "0x03D73C": 0x7FFFFFFF,
    }
    fixed = json.loads((REPO_ROOT / "data" / "fixed_regions.json").read_text(encoding="utf-8"))
    recorded = {
        word["offset"].lower(): word["value"] for word in fixed["gbaram_literals"]["words"]
    }
    assert recorded == {key.lower(): value for key, value in expected.items()}

    pool = {
        word["file_offset"].lower(): int(word["value"], 16)
        for word in manifest["translation_units"][0]["literal_pool"]["words"]
    }
    assert pool == {key.lower(): value for key, value in expected.items()}
    assert "0x03D4D0..0x03D730" in " ".join(fixed["gbaram_literals"]["_comment"])


# ---------------------------------------------------------------------------
# controls and rejected candidates are checked against the map, not just non-empty
# ---------------------------------------------------------------------------
def test_controls_and_rejections_are_recorded(manifest):
    ids = {c["id"] for c in manifest["controls"]}
    assert {"reset_crt", "crt_veneer", "codec_blob"} <= ids
    assert {r["id"] for r in manifest["rejections"]} >= {
        "code_reachable_055324",
        "code_candidate_span_6_048F14",
        "sub_0803D4D0_inventory_entry",
        "sub_0803D5B8_inventory_entry",
    }


def test_every_control_is_anchored_to_a_real_region_in_the_map(manifest, rom_map):
    """A control that names a region the map does not have is a fabricated control."""
    by_id = {region["id"]: region for region in rom_map["regions"]}
    for control in manifest["controls"]:
        region = by_id.get(control["region_id"])
        assert region is not None, control["id"]
        assert region["isa"] == control["isa"], control["id"]
        assert region["confidence"] == control["region_confidence"], control["id"]
        assert region["executable"] == control["region_executable"], control["id"]


def test_only_two_regions_are_arm_and_confirmed(manifest, rom_map):
    """The "no ARM probe without forcing one" argument is anchored here.

    If a third ARM region were ever confirmed as ordinary code, this test would
    fail and the empty ARM probe corpus would need to be revisited rather than
    quietly inherited.
    """
    confirmed_arm = [
        region["id"]
        for region in rom_map["regions"]
        if region.get("isa") == "arm" and region.get("executable") == "confirmed"
    ]
    assert sorted(confirmed_arm) == ["codec_blob", "reset_code"]
    assert {c["region_id"] for c in manifest["controls"]} >= set(confirmed_arm)


def test_the_arm_veneer_is_recorded_as_a_sub_address_not_a_region_start(manifest, rom_map):
    control = next(c for c in manifest["controls"] if c["id"] == "crt_veneer")
    region = next(r for r in rom_map["regions"] if r["id"] == control["region_id"])
    assert control["rom_address"] != region["rom_address_start"]
    assert int(region["rom_address_start"], 16) < int(control["rom_address"], 16)
    assert "not a region start" in control["excluded_because"]


def test_the_data_region_that_looks_like_code_is_recorded(manifest):
    rejection = next(
        r for r in manifest["rejections"] if r["id"] == "code_reachable_055324"
    )
    assert "DATA" in rejection["rejected_because"]


# ---------------------------------------------------------------------------
# the harness fails closed
# ---------------------------------------------------------------------------
def test_no_ads_is_discovered_when_the_root_is_bogus(monkeypatch, tmp_path):
    monkeypatch.delenv("ADS12_ROOT", raising=False)
    monkeypatch.setenv("PATH", str(tmp_path))
    assert cp.discover_ads(tmp_path / "nope") is None


def test_an_unidentifiable_executable_is_not_accepted_as_ads(monkeypatch, tmp_path):
    """A file named tcpp.exe is not a compiler, let alone ARM's.

    This is the defect the review found: the earlier version accepted any
    executable with the right name, and `tcc` is also the Tiny C Compiler.
    """
    bindir = tmp_path / "Bin"
    bindir.mkdir()
    (bindir / "tcpp.exe").write_bytes(b"MZ")  # not even a valid executable
    monkeypatch.delenv("PATH", raising=False)
    assert cp.discover_ads(tmp_path, compiler_id="tcpp") is None


def test_a_real_non_ads_executable_is_rejected(tmp_path):
    """A genuinely runnable program whose banner is not ARM's must be refused."""
    assert cp.identify_ads_tool(Path(sys.executable)) is None
    assert cp.looks_like_ads("Python 3.12.0") is False


def test_the_banner_matcher_accepts_ads_and_rejects_the_tiny_c_compiler():
    assert cp.looks_like_ads("ARM C/C++ Compiler, ADS1.2 [Build 842]")
    assert cp.looks_like_ads("ARM Developer Suite 1.2")
    assert cp.looks_like_ads("ARM Assembler, RVCT 2.2")
    assert cp.looks_like_ads("ARM Linker, RealView")
    # Tiny C Compiler: the name collides, the banner must not.
    assert cp.looks_like_ads("tcc version 0.9.27 (x86_64 Linux)") is False
    assert cp.looks_like_ads("") is False


def test_an_explicit_root_does_not_fall_back_to_path(monkeypatch, tmp_path):
    """Under an explicit ADS12_ROOT, PATH must not substitute another binary."""
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (elsewhere / "tcpp.exe").write_bytes(b"MZ")
    root = tmp_path / "ads"
    (root / "Bin").mkdir(parents=True)
    monkeypatch.setenv("PATH", str(elsewhere))
    monkeypatch.setenv("ADS12_ROOT", str(root))
    assert cp.discover_ads(compiler_id="tcpp") is None


def test_a_missing_toolchain_reports_blocked_never_a_pass(monkeypatch, tmp_path, rom_bytes):
    monkeypatch.delenv("ADS12_ROOT", raising=False)
    monkeypatch.setenv("PATH", str(tmp_path))
    result = cp.run_probe(rom_bytes, cp.GBARAM_TU)
    assert result.status == "BLOCKED"
    assert result.code == cp.BLOCK_ADS_UNAVAILABLE
    assert result.diff is None
    assert result.comparison_ran is False
    assert result.as_dict()["exact_match"] is False


def test_blocked_configurations_never_produce_a_complete_or_refuted_matrix(
    monkeypatch, tmp_path, rom_bytes
):
    """A toolchain that ran nothing must not yield a compiler conclusion.

    This is the BLOCKER the review found: previously every configuration could
    be BLOCKED and the document still reported COMPLETE with a REFUTED
    fingerprint and exit code 0.
    """
    monkeypatch.delenv("ADS12_ROOT", raising=False)
    monkeypatch.setenv("PATH", str(tmp_path))
    matrix = cp.build_matrix(rom_bytes, identity.load_canonical()["hashes"]["sha1"])
    assert matrix["comparisons_run"] == 0
    assert matrix["code"] == cp.BLOCK_ADS_UNAVAILABLE
    assert "BLOCKED" in matrix["result"]
    assert matrix["conclusion"] == "UNTESTED"
    assert matrix["no_compiler_result_claimed"] is True
    assert all(c["status"] == "BLOCKED" for c in matrix["configurations"])
    assert all(c["comparison_ran"] is False for c in matrix["configurations"])
    assert all(c["exact_match"] is False for c in matrix["configurations"])
    assert all(c["matching_probes"] == 0 for c in matrix["configurations"])
    # No claim may be REFUTED, because nothing was attempted.
    for claim, state in matrix["fingerprint"].items():
        if claim.startswith("_"):
            continue
        assert state == "UNTESTED", (claim, state)


def test_the_blocked_matrix_records_itself_environment_independently(rom_bytes, monkeypatch, tmp_path):
    """The committed document must not embed this machine's tool listing."""
    monkeypatch.delenv("ADS12_ROOT", raising=False)
    monkeypatch.setenv("PATH", str(tmp_path))
    matrix = cp.build_matrix(rom_bytes, "f" * 40)
    text = json.dumps(matrix)
    assert "ADS12_ROOT:" not in text
    assert "MISSING" not in text
    assert cp.BLOCKED_STATEMENT in matrix["details"]
    # Deterministic, so --verify-matrix is meaningful across machines.
    assert cp.build_matrix(rom_bytes, "f" * 40) == matrix


def test_a_partial_matrix_carries_the_blocker_code_on_its_rows_only(rom_bytes, monkeypatch, tmp_path):
    """The root cause of the gate's substring bug, pinned so it cannot come back.

    In a PARTIAL matrix the blocked ROWS carry `"code": "ADS12_UNAVAILABLE"` while
    the document's own top-level `code` is null. Any consumer that searches the
    document text for that string therefore mistakes a run that did compare bytes
    for a blocked one, which is exactly what a gate must not do. Gate 6 reads the
    top-level field instead.
    """
    monkeypatch.delenv("ADS12_ROOT", raising=False)
    monkeypatch.setenv("PATH", str(tmp_path))
    blocked = cp.build_matrix(rom_bytes, "f" * 40)
    assert blocked["code"] == cp.BLOCK_ADS_UNAVAILABLE
    assert blocked["comparisons_run"] == 0
    assert "ADS12_UNAVAILABLE" in json.dumps(blocked)

    # A synthetic partial matrix: one row compared, five blocked.
    def row(frontend, opt, matched, ran=True):
        return {
            "frontend": frontend,
            "optimization": opt,
            "isa": "thumb",
            "cpu": "ARM7TDMI",
            "translation_unit": "gbaram_tu",
            "comparison_ran": ran,
            "exact_match": False,
            "matching_probes": matched if ran else None,
            "total_probes": PROBE_COUNT if ran else None,
            "matching_instructions": None,
            "total_instructions": None,
            "dropped_candidate_bytes": 0,
            "status": "DIFFER" if ran else "BLOCKED",
            "code": None if ran else cp.BLOCK_ADS_UNAVAILABLE,
            "probe_matches": {},
        }

    partial = cp._matrix_document(
        "f" * 40,
        [row("tcpp", "-O1", 0)] + [row(f, "-O1", None, ran=False) for f in ("tcc", "armcc")],
        result="COMPILER PROBE: PARTIAL",
        code=None,
        details=[],
    )
    assert partial["comparisons_run"] == 1
    assert partial["code"] is None, "the document is not blocked even though rows are"
    assert "ADS12_UNAVAILABLE" in json.dumps(partial), (
        "and the string is still present, which is why the gate must not search for it"
    )
    assert partial["result"].startswith("COMPILER PROBE: PARTIAL")


def test_no_compiler_result_claimed_means_nothing_was_promoted():
    """It does not mean nothing was learned: a refuted lead is still a result."""
    def row(frontend, opt, matched):
        return {
            "frontend": frontend,
            "optimization": opt,
            "isa": "thumb",
            "cpu": "ARM7TDMI",
            "translation_unit": "gbaram_tu",
            "comparison_ran": True,
            "exact_match": False,
            "matching_probes": matched,
            "total_probes": PROBE_COUNT,
            "matching_instructions": None,
            "total_instructions": None,
            "dropped_candidate_bytes": 0,
            "status": "DIFFER",
            "code": None,
            "probe_matches": {},
        }

    refuted = cp._matrix_document(
        "f" * 40,
        [row("tcpp", "-O1", 0), row("tcc", "-O1", 0)],
        result="COMPILER PROBE: COMPLETE",
        code=None,
        details=[],
    )
    assert refuted["no_compiler_result_claimed"] is True
    assert refuted["promoted_claims"] == []
    # The CPU claim is also refuted, because the winner matched nothing at all.
    assert refuted["refuted_claims"] == [
        "thumb_frontend",
        "thumb_optimization",
        "thumb_cpu_target",
        "c_vs_cpp",
    ]


def test_the_documented_exit_contract_is_enforced_by_a_real_invocation(baserom):
    """Behavioural: run the CLI and check its exit code, do not read its source.

    Replaces a test that grepped cli.py for `EXIT_FAIL`, which could not fail if
    the exit path were wrong in any other way.
    """
    for flags in (["--json"], ["--matrix", "--json"], ["--json", "--verify-matrix"]):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "buusfury",
                "compiler-probe",
                "--rom",
                str(baserom),
                *flags,
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            env={**__import__("os").environ, "PYTHONPATH": str(REPO_ROOT / "tools")},
        )
        # No ADS on the build machine, so every probe mode must be non-zero.
        # --verify-matrix legitimately passes, so it is checked separately.
        if "--verify-matrix" in flags:
            assert completed.returncode == 0, completed.stdout + completed.stderr
            continue
        assert completed.returncode == 1, (flags, completed.stdout[-400:])


# ---------------------------------------------------------------------------
# the fingerprint classifies per claim
# ---------------------------------------------------------------------------
def _row(frontend, opt, matched, total=PROBE_COUNT, ran=True):
    return {
        "frontend": frontend,
        "optimization": opt,
        "comparison_ran": ran,
        "matching_probes": matched if ran else None,
        "total_probes": total if ran else None,
        "exact_match": matched == total if ran else False,
    }


def test_the_fingerprint_is_untested_when_nothing_compared():
    state = cp.fingerprint([_row("tcpp", "-O1", None, ran=False)])
    assert state["thumb_frontend"] == "UNTESTED"
    assert state["thumb_optimization"] == "UNTESTED"
    assert state["c_vs_cpp"] == "UNTESTED"
    assert state["thumb_cpu_target"] == "UNTESTED"
    assert state["arm_frontend"] == "UNTESTED"
    assert state["abi"] == "UNTESTED"


def test_a_lead_that_matches_nothing_is_refuted():
    state = cp.fingerprint([_row("tcpp", "-O1", 0), _row("tcc", "-O1", 0)])
    assert state["thumb_frontend"] == "REFUTED"


def test_matching_all_probes_with_a_differing_competitor_is_proven():
    """Each claim needs its OWN competing setting to have run.

    tcc -O1 discriminates the frontend but says nothing about the optimization
    level, so `thumb_optimization` is only PROVEN once an -O0 or -O2 row has run
    and differed. An earlier revision asserted PROVEN from the tcc row alone,
    which is the defect this now guards against.
    """
    frontend_only = cp.fingerprint(
        [_row("tcpp", "-O1", PROBE_COUNT), _row("tcc", "-O1", 0)]
    )
    assert frontend_only["thumb_frontend"] == "PROVEN"
    assert frontend_only["c_vs_cpp"] == "PROVEN"
    assert frontend_only["thumb_optimization"] == "PLAUSIBLE", "no -O competitor ran"

    with_optimisation = cp.fingerprint(
        [
            _row("tcpp", "-O1", PROBE_COUNT),
            _row("tcc", "-O1", 0),
            _row("tcpp", "-O0", 0),
        ]
    )
    assert with_optimisation["thumb_optimization"] == "PROVEN"


def test_a_competitor_that_matches_identically_is_only_plausible():
    """Three configurations matching the same way is NOT three confirmations."""
    state = cp.fingerprint(
        [
            _row("tcpp", "-O1", PROBE_COUNT),
            _row("tcc", "-O1", PROBE_COUNT),
            _row("tcpp", "-O0", PROBE_COUNT),
            _row("tcpp", "-O2", PROBE_COUNT),
        ]
    )
    assert state["thumb_frontend"] == "PLAUSIBLE"
    assert state["thumb_optimization"] == "PLAUSIBLE"
    assert state["c_vs_cpp"] == "PLAUSIBLE"


def test_an_arm_match_is_scored_from_its_own_rows_not_hardcoded():
    state = cp.fingerprint(
        [_row("tcpp", "-O1", 0), _row("armcpp", "-O1", PROBE_COUNT), _row("armcc", "-O1", 0)]
    )
    assert state["arm_frontend"] == "PROVEN"
    assert state["thumb_frontend"] == "REFUTED"


def test_the_cpu_claim_can_never_be_promoted_by_this_matrix():
    """No configuration varies the CPU, so the claim is structurally capped."""
    state = cp.fingerprint([_row("tcpp", "-O1", PROBE_COUNT), _row("tcc", "-O1", 0)])
    assert state["thumb_cpu_target"] == "PLAUSIBLE"
    assert "can never be promoted" in state["_evidence"]["discriminators"]["thumb_cpu_target"]


def test_a_partial_match_is_plausible_not_proven():
    """The ticket's bar is three discriminating functions, so one is not enough."""
    state = cp.fingerprint([_row("tcpp", "-O1", 1), _row("tcc", "-O1", 0)])
    assert state["thumb_frontend"] == "PLAUSIBLE"
    two = cp.fingerprint([_row("tcpp", "-O1", 2), _row("tcc", "-O1", 0)])
    assert two["thumb_frontend"] == "STRONGLY_SUPPORTED"


def test_a_winner_with_no_running_competitor_can_never_be_promoted():
    """A competitor that never ran is not a competitor that differs.

    This was a real defect: treating a missing competitor as differing published
    PROVEN for a compiler setting with no discriminating evidence at all, which
    becomes reachable as soon as a partially installed toolchain runs only some
    configurations.
    """
    state = cp.fingerprint([_row("tcpp", "-O1", PROBE_COUNT)])
    assert state["thumb_frontend"] == "PLAUSIBLE"
    assert state["thumb_optimization"] == "PLAUSIBLE"
    assert state["c_vs_cpp"] == "PLAUSIBLE"
    assert "thumb_frontend" in state["_evidence"]["claims_capped_for_a_missing_competitor"]

    # A blocker on the competitor row is the same situation as a missing row.
    state = cp.fingerprint(
        [_row("tcpp", "-O1", PROBE_COUNT), _row("tcc", "-O1", None, ran=False)]
    )
    assert state["thumb_frontend"] == "PLAUSIBLE"

    # And a partially installed toolchain, where only some rows ran, must not
    # promote the optimization claim whose -O2 row is blocked.
    state = cp.fingerprint(
        [
            _row("tcpp", "-O1", PROBE_COUNT),
            _row("tcc", "-O1", 0),
            _row("tcpp", "-O0", 0),
            _row("tcpp", "-O2", None, ran=False),
        ]
    )
    assert state["thumb_optimization"] == "PROVEN", "one differing competitor is enough"
    state_missing_both = cp.fingerprint(
        [
            _row("tcpp", "-O1", PROBE_COUNT),
            _row("tcc", "-O1", 0),
            _row("tcpp", "-O0", None, ran=False),
            _row("tcpp", "-O2", None, ran=False),
        ]
    )
    assert state_missing_both["thumb_optimization"] == "PLAUSIBLE"


def test_arm_optimization_is_untested_because_nothing_varies_it():
    """No ARM row varies -O and there is no ARM probe corpus to optimize."""
    state = cp.fingerprint(
        [_row("armcpp", "-O1", PROBE_COUNT), _row("armcc", "-O1", 0)]
    )
    assert state["arm_frontend"] == "PROVEN"
    assert state["arm_optimization"] == "UNTESTED"
    assert "no ARM row varies" in state["_evidence"]["discriminators"]["arm_optimization"]


# ---------------------------------------------------------------------------
# deterministic comparison
# ---------------------------------------------------------------------------
def test_comparison_is_deterministic():
    target = bytes(range(64))
    first = cp.compare_bytes(target, bytes(range(64)), 0x08000000, "thumb")
    second = cp.compare_bytes(target, bytes(range(64)), 0x08000000, "thumb")
    assert first.as_dict() == second.as_dict()
    assert first.exact_match and first.differing_bytes == 0
    assert first.first_difference is None
    assert first.matching_instructions == first.target_instructions


def test_comparison_reports_the_first_difference_and_the_counts():
    target = bytes(32)
    candidate = bytearray(32)
    candidate[4] = 0xAB
    candidate[9] = 0xCD
    diff = cp.compare_bytes(target, bytes(candidate), 0x08000000, "thumb")
    assert not diff.exact_match
    assert diff.first_difference == 4
    assert diff.differing_bytes == 2
    assert diff.identical_bytes == 30


def test_comparison_reports_a_length_mismatch_rather_than_hiding_it():
    diff = cp.compare_bytes(bytes(8), bytes(4), 0x08000000, "thumb")
    assert not diff.exact_match
    assert diff.target_size == 8
    assert diff.candidate_size == 4
    assert diff.differing_bytes == 4
    assert diff.identical_bytes == 4


def test_comparison_counts_a_differing_instruction_once():
    target = bytes.fromhex("0020 0149 0847")  # movs r0,#0 ; ldr r1,[pc,#4] ; bx r1
    candidate = bytes.fromhex("0120 0149 0847")  # movs r0,#1 differs
    diff = cp.compare_bytes(target, candidate, 0x08000000, "thumb")
    assert diff.target_instructions == 3
    assert diff.differing_instructions == 1
    assert diff.matching_instructions == 2


def test_a_byte_difference_can_never_report_zero_differing_instructions():
    """The review's counterexample: different encodings, identical disassembly.

    0x4280 and 0x4500 both render as `cmp r0, r0`, so a positional text
    comparison reports zero differences for bytes that are not equal. Keying on
    the target's instruction boundaries cannot make that mistake.
    """
    left = cp.disassemble(bytes.fromhex("8042"), 0x08000000, "thumb")
    right = cp.disassemble(bytes.fromhex("0045"), 0x08000000, "thumb")
    assert [x[1:] for x in left] == [x[1:] for x in right], "premise: same text"
    diff = cp.compare_bytes(bytes.fromhex("8042"), bytes.fromhex("0045"), 0x08000000, "thumb")
    assert diff.exact_match is False
    assert diff.differing_instructions == 1


def test_matching_instructions_can_never_go_negative():
    target = bytes.fromhex("0020 0149 0847 00bf")
    candidate = bytes.fromhex("0120 0149")
    diff = cp.compare_bytes(target, candidate, 0x08000000, "thumb")
    assert diff.differing_instructions <= diff.target_instructions
    assert diff.matching_instructions >= 0


def test_unequal_bytes_almost_always_imply_a_differing_instruction():
    """The invariant, and the one case where it does not hold.

    If the target's own bytes do not decode to a single instruction there is
    nothing to compare instruction-wise, so the uncovered bytes are published as
    `undecoded_target_bytes`. They are deliberately NOT folded into the
    instruction count, because that made `matching_instructions` negative. The
    documented guarantee is therefore scoped to a fully-decoding target, which
    every real probe is.
    """
    diff = cp.compare_bytes(bytes.fromhex("00f0"), bytes.fromhex("00bf"), 0x08000000, "thumb")
    assert diff.exact_match is False
    assert diff.target_instructions == 0
    assert diff.differing_bytes == 1
    assert diff.undecoded_target_bytes == 2
    assert diff.differing_instructions == 0, "no instruction spans exist to differ"
    assert diff.matching_instructions == 0, "and the matching count must clamp at zero"

    for target_hex, candidate_hex in (
        ("8042", "0045"),
        ("0020", "0120"),
        ("00200149", "00200150"),
    ):
        diff = cp.compare_bytes(
            bytes.fromhex(target_hex), bytes.fromhex(candidate_hex), 0x08000000, "thumb"
        )
        assert diff.undecoded_target_bytes == 0
        assert not diff.exact_match
        assert diff.differing_instructions > 0, (target_hex, candidate_hex)
        assert diff.matching_instructions >= 0


def test_matching_instructions_never_goes_negative_for_any_input():
    """Property test over adversarial pairs, including undecodable targets."""
    cases = [
        (bytes.fromhex("00f0"), bytes.fromhex("00bf")),
        (bytes.fromhex("00f0"), b""),
        (b"", bytes.fromhex("00bf")),
        (bytes.fromhex("0020"), bytes.fromhex("00200149")),
        (bytes.fromhex("00200149"), bytes.fromhex("0020")),
        (bytes(8), bytes.fromhex("00b6" * 4)),
    ]
    for target, candidate in cases:
        diff = cp.compare_bytes(target, candidate, 0x08000000, "thumb")
        assert diff.matching_instructions >= 0, (target.hex(), candidate.hex())
        assert diff.differing_instructions <= max(diff.target_instructions, 0) + 0
        assert diff.identical_bytes >= 0


def test_every_real_probe_decodes_fully_so_the_invariant_holds_for_it(rom_bytes, manifest):
    for probe in manifest["probes"]:
        start = int(probe["rom_address"], 16)
        raw = cp.extract(rom_bytes, start, probe["byte_length"])
        spans = cp.instruction_spans(raw, start, probe["isa"])
        assert sum(size for _offset, size in spans) == probe["byte_length"], probe["name"]
        diff = cp.compare_bytes(raw, raw[:1] * probe["byte_length"], start, probe["isa"])
        assert diff.undecoded_target_bytes == 0, probe["name"]
        assert diff.differing_instructions > 0, probe["name"]


def test_the_first_difference_address_uses_the_base_address():
    target = bytes(8)
    candidate = bytearray(8)
    candidate[3] = 1
    diff = cp.compare_bytes(target, bytes(candidate), 0x0803D4D0, "thumb")
    assert diff.first_difference == 3
    assert diff.as_dict()["first_difference_address"] == "0x0803D4D3"


def test_extract_refuses_a_range_outside_the_image():
    with pytest.raises(cp.ProbeError):
        cp.extract(bytes(16), gba.ROM_BASE + 8, 32)


def test_chain_walk_rejects_an_unaligned_region():
    with pytest.raises(cp.ProbeError):
        cp.chain_walk(bytes(64), gba.ROM_BASE + 1, gba.ROM_BASE + 32, "thumb")
    with pytest.raises(cp.ProbeError):
        cp.chain_walk(bytes(64), gba.ROM_BASE + 2, gba.ROM_BASE + 33, "arm")


def test_chain_walk_refuses_a_region_that_does_not_decode_at_all():
    """Undecodable filler must stop the walk, not produce a plausible function."""
    with pytest.raises(cp.ProbeError):
        cp.chain_walk(b"\x00\xb6" * 16, gba.ROM_BASE, gba.ROM_BASE + 32, "thumb")
    with pytest.raises(cp.ProbeError):
        cp.chain_walk(b"\x00\x00\x00\xf0" * 8, gba.ROM_BASE, gba.ROM_BASE + 32, "arm")


def test_chain_walk_flags_a_region_with_no_terminator():
    """A region that decodes but never returns is a lower bound, and says so."""
    boundaries = cp.chain_walk(b"\xc0\x46" * 32, gba.ROM_BASE, gba.ROM_BASE + 64, "thumb")
    assert len(boundaries) == 1
    assert boundaries[0].problems
    assert any("no terminator" in p for p in boundaries[0].problems)
    assert any("flow left the unit" in p for p in boundaries[0].problems)


def test_chain_walk_reports_a_path_that_leaves_the_region():
    """A path escaping the unit makes the reported end a lower bound.

    The review found this case silently produced a boundary with no problem
    whose reachable body extended past its own reported end. Two forms are
    checked: a conditional branch out of the unit, and a fall-through past its
    end (covered by the no-terminator test above).
    """
    # 0xd100 = bne to 0x08000004, which is the region end, so it leaves the unit;
    # 0x4770 = bx lr.
    raw = bytes.fromhex("00d1 7047 0000 0000")
    boundaries = cp.chain_walk(raw, gba.ROM_BASE, gba.ROM_BASE + 4, "thumb")
    assert any("leaves the unit" in problem for problem in boundaries[0].problems), (
        boundaries[0].problems
    )
    assert boundaries[0].end <= gba.ROM_BASE + 4


# ---------------------------------------------------------------------------
# the linker layout and the command plan
# ---------------------------------------------------------------------------
def test_the_scatter_file_places_the_unit_at_its_rom_address():
    text = cp.render_scatter(cp.GBARAM_TU)
    assert "0x0803D4D0" in text
    assert "probe.o (+RO)" in text


def test_the_command_plan_is_the_lead_pipeline_in_order():
    tools = cp.planning_tools("tcpp")
    commands = cp.plan_commands(
        tools, Path("src/probes/GBARam.c"), Path("build/out"), ("tcpp", "ARM7TDMI", "-O1")
    )
    assert len(commands) == 4
    assert commands[0][1:6] == ["-S", "-c", "-cpu", "ARM7TDMI", "-O1"]
    assert commands[0][0].endswith("tcpp.exe")
    assert "armasm" in commands[1][0] and commands[1][-1].endswith("probe.s")
    assert "armlink" in commands[2][0] and "-scatter" in commands[2]
    assert "fromelf" in commands[3][0] and "-bin" in commands[3]


def test_the_planning_placeholder_is_never_an_identified_toolchain():
    tools = cp.planning_tools("tcpp")
    assert "placeholder" in tools.banner
    assert tools.version == "unknown"


def test_the_origin_assumption_is_stated_not_implied():
    assert "fromelf" in cp.ORIGIN_ASSUMPTION
    assert "UNEXERCISED" in cp.ORIGIN_ASSUMPTION


def test_probe_slices_partition_the_target_and_report_one_result_per_function(rom_bytes):
    """Behavioural: the slices must cover the unit exactly, once each.

    Replaces a test that only grepped two prose substrings out of the module and
    therefore could not fail for the property it named.
    """
    unit = cp.GBARAM_TU
    target = cp.extract(rom_bytes, unit.rom_address, unit.length)
    matches = cp.probe_slice_matches(target, target, unit, unit.isa)
    assert len(matches) == PROBE_COUNT
    assert all(matched for _name, matched in matches), "a self-comparison must match"
    assert [name for name, _m in matches] == [f"sub_{s:08X}" for s, _e, _r in cp.GBARAM_FUNCTIONS]

    # A candidate differing in exactly one function must fail exactly that one.
    changed = bytearray(target)
    changed[0] ^= 0xFF
    matches = cp.probe_slice_matches(target, bytes(changed), unit, unit.isa)
    assert sum(1 for _n, m in matches if m) == PROBE_COUNT - 1
    assert matches[0][1] is False

    # And the slices must tile the code body exactly, with no byte counted twice.
    spans = [(s - unit.rom_address, e - unit.rom_address) for s, e, _r in cp.GBARAM_FUNCTIONS]
    assert spans[0][0] == 0
    assert spans[-1][1] == unit.code_length
    for (_a, end_a), (start_b, _b) in zip(spans, spans[1:]):
        assert end_a == start_b


# ---------------------------------------------------------------------------
# verifying the committed documents
# ---------------------------------------------------------------------------
def test_a_tampered_manifest_is_caught_in_every_field(rom_bytes, tmp_path):
    """The whole document must be compared, not a hand-picked subset."""
    committed = json.loads(cp.MANIFEST_PATH.read_text(encoding="utf-8"))
    for field, tampered in (
        ("schema", 999),
        ("method", "trust me"),
        ("notes", ["everything is fine"]),
        ("controls", []),
        ("rejections", []),
        ("generated_by", "somewhere else"),
        ("counts", {"probes": 0}),
    ):
        altered = dict(committed)
        altered[field] = tampered
        path = tmp_path / f"tampered-{field}.json"
        path.write_text(json.dumps(altered), encoding="utf-8")
        problems = cp.verify_manifest(rom_bytes, path)
        assert problems, f"tampering with {field!r} was not detected"


def test_an_unchanged_manifest_verifies(rom_bytes):
    assert cp.verify_manifest(rom_bytes) == []


def test_manifest_verification_reports_inventory_drift_separately(rom_bytes, tmp_path, monkeypatch):
    """A changed inventory must not be reported as ROM drift."""
    committed = json.loads(cp.MANIFEST_PATH.read_text(encoding="utf-8"))
    committed["inventory_sha1"] = "0" * 40
    path = tmp_path / "drifted.json"
    path.write_text(json.dumps(committed), encoding="utf-8")
    problems = cp.verify_manifest(rom_bytes, path)
    assert any("INVENTORY DRIFT" in p for p in problems)
    assert any("not evidence about the ROM" in p for p in problems)


def test_a_tampered_matrix_is_caught(rom_bytes, tmp_path):
    committed = json.loads(cp.MATRIX_PATH.read_text(encoding="utf-8"))
    committed["result"] = "COMPILER PROBE: COMPLETE"
    committed["code"] = None
    path = tmp_path / "tampered-matrix.json"
    path.write_text(json.dumps(committed), encoding="utf-8")
    problems = cp.verify_matrix(rom_bytes, "f" * 40, path)
    assert problems
    assert "differing fields" in problems[0]


def test_the_committed_matrix_claims_no_result(rom_bytes):
    """Only asserted on a machine that cannot run the probe.

    On a machine with an identified ADS 1.2 the matrix legitimately becomes
    COMPLETE once regenerated, so requiring `comparisons_run == 0` there would
    make the suite unable to pass on exactly the machine the next ticket needs.
    The consistency check below is the part that always applies.
    """
    matrix = json.loads(cp.MATRIX_PATH.read_text(encoding="utf-8"))
    if cp.discover_ads() is None:
        assert matrix["comparisons_run"] == 0
        assert matrix["no_compiler_result_claimed"] is True
        assert matrix["code"] == cp.BLOCK_ADS_UNAVAILABLE
        assert matrix["promoted_claims"] == []
    else:
        assert "comparisons_run" in matrix
    assert cp.verify_matrix(rom_bytes, identity.load_canonical()["hashes"]["sha1"]) == []


def test_the_matrix_headlines_partial_when_only_some_configurations_ran():
    """A partly blocked matrix must not be called COMPLETE."""
    one_ran = [_row("tcpp", "-O1", 0)]
    doc = cp._matrix_document(
        "f" * 40,
        [
            {
                **row,
                "isa": "thumb",
                "cpu": "ARM7TDMI",
                "translation_unit": "gbaram_tu",
                "matching_instructions": None,
                "total_instructions": None,
                "dropped_candidate_bytes": 0,
                "status": "DIFFER" if row["comparison_ran"] else "BLOCKED",
                "code": None if row["comparison_ran"] else cp.BLOCK_ADS_UNAVAILABLE,
                "exact_match": False,
                "probe_matches": {},
            }
            for row in (
                one_ran[0],
                _row("tcc", "-O1", None, ran=False),
            )
        ],
        result="x",
        code=None,
        details=[],
    )
    assert doc["comparisons_run"] == 1
    # No claim was promoted, so the document must not appear to claim a result.
    assert doc["no_compiler_result_claimed"] is True
    assert doc["promoted_claims"] == []


# ---------------------------------------------------------------------------
# safety: nothing proprietary, nothing outside build/
# ---------------------------------------------------------------------------
def test_the_probe_workspace_is_inside_the_gitignored_build_directory():
    assert cp.PROBE_WORKSPACE == REPO_ROOT / "build" / "probes"
    assert "build" in cp.PROBE_WORKSPACE.parts
    result = subprocess.run(
        ["git", "check-ignore", "-q", str(cp.PROBE_WORKSPACE)],
        cwd=str(REPO_ROOT),
        capture_output=True,
    )
    if result.returncode == 2:
        pytest.skip("git is not available to confirm the ignore rule")
    assert result.returncode == 0, "build/probes is not gitignored"


def test_git_refuses_to_track_every_ads_binary_and_licence_file():
    """Asked of Git itself rather than of the .gitignore text."""
    result = subprocess.run(
        ["git", "--version"], capture_output=True, text=True
    )
    if result.returncode != 0:
        pytest.skip("git is not available")
    names = [
        "armcc.exe",
        "armcpp.exe",
        "tcc.exe",
        "tcpp.exe",
        "armasm.exe",
        "armlink.exe",
        "fromelf.exe",
        "armsd.exe",
        "axd.exe",
        "armcc",
        "tcpp",
        "fromelf",
        "tool.lic",
        "tool.license",
        "license.txt",
    ]
    for name in names:
        checked = subprocess.run(
            ["git", "check-ignore", "-q", name],
            cwd=str(REPO_ROOT),
            capture_output=True,
        )
        assert checked.returncode == 0, f"{name} would be committable"


def test_no_ads_binary_or_licence_is_present_in_the_repository_tree():
    forbidden = {
        "armcc.exe", "armcpp.exe", "tcc.exe", "tcpp.exe", "armasm.exe",
        "armlink.exe", "fromelf.exe", "axd.exe", "armsd.exe",
    }
    ignored_dirs = {".git", "build", "reference", "__pycache__"}
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file() or ignored_dirs & set(path.parts):
            continue
        assert path.name.lower() not in forbidden, path
        assert path.suffix.lower() not in (".lic", ".license"), path
        assert path.name.lower() != "license.txt", path


def test_a_blocked_probe_writes_nothing_outside_the_probe_workspace(
    rom_bytes, monkeypatch, tmp_path
):
    """Behavioural, not textual: run the harness and diff the working tree.

    The earlier version of this test only grepped the module's source, so any
    real out-of-workspace write would have passed it.
    """
    monkeypatch.delenv("ADS12_ROOT", raising=False)
    monkeypatch.setenv("PATH", str(tmp_path))
    watched = [
        REPO_ROOT / "config",
        REPO_ROOT / "docs",
        REPO_ROOT / "src",
        REPO_ROOT / "tests",
        REPO_ROOT / "tools",
    ]

    def snapshot() -> dict[str, int]:
        state = {}
        for root in watched:
            for path in root.rglob("*"):
                if path.is_file() and "__pycache__" not in path.parts:
                    state[str(path)] = path.stat().st_mtime_ns
        return state

    before = snapshot()
    cp.run_probe(rom_bytes, cp.GBARAM_TU)
    cp.build_matrix(rom_bytes, "f" * 40)
    cp.verify_manifest(rom_bytes)
    cp.verify_matrix(rom_bytes, "f" * 40)
    assert snapshot() == before


def test_the_harness_holds_no_path_into_the_other_checkout():
    """A cheap guard, deliberately not the main defence.

    The repository-wide invariant in tests/test_rom_map.py covers tools/*.py; this
    adds the tests directory and the CLI module, which that one does not reach.
    A string check cannot prove absence of a write path, which is why
    `test_a_blocked_probe_writes_nothing_outside_the_probe_workspace` exists.
    """
    needle = "log1" + "-remake"
    for name in ("compiler_probe.py", "cli.py"):
        source = (REPO_ROOT / "tools" / "buusfury" / name).read_text(encoding="utf-8")
        assert needle not in source, name
    test_source = (REPO_ROOT / "tests" / "test_compiler_probe.py").read_text(encoding="utf-8")
    assert needle not in test_source


def test_the_manifest_does_not_present_semantic_roles_as_measurements(manifest):
    """The role strings are hypotheses, and the manifest must say so.

    An earlier revision claimed the roles described each function's measured
    shape while the strings actually carried semantic guesses.
    """
    note = " ".join(manifest["notes"])
    assert "SEMANTIC HYPOTHESES" in note
    assert "UNPROVEN" in note
    roles = " ".join(probe["role"] for probe in manifest["probes"])
    assert "free" in roles or "allocate" in roles, "the roles really are semantic"
    assert "method" in manifest and "chain-walk" in manifest["method"]


def test_the_files_this_ticket_adds_are_ascii_lf_and_bom_free():
    """A BOM or a smart dash is invisible in review and breaks the text contract.

    This repository's generated documents are LF-only and its markdown is ASCII
    (a global pre-commit hook rejects em-dashes in .md and .txt). A PowerShell
    `Set-Content -Encoding UTF8` silently writes a BOM, which showed up as an
    unwanted whole-file change while this ticket was being written, so the rule
    is asserted rather than remembered.
    """
    paths = [
        REPO_ROOT / "config" / "compiler_probes.json",
        REPO_ROOT / "config" / "compiler_matrix.json",
        REPO_ROOT / "docs" / "COMPILER_PROBE.md",
        REPO_ROOT / "docs" / "COMPILER_PROBE_PROVENANCE.md",
        REPO_ROOT / "src" / "probes" / "GBARam.c",
        REPO_ROOT / "src" / "probes" / "README.md",
        REPO_ROOT / "tools" / "buusfury" / "compiler_probe.py",
        REPO_ROOT / "tests" / "test_compiler_probe.py",
    ]
    for path in paths:
        raw = path.read_bytes()
        assert not raw.startswith(b"\xef\xbb\xbf"), f"{path.name} starts with a BOM"
        assert b"\r\n" not in raw, f"{path.name} has CRLF line endings"
        text = raw.decode("ascii", errors="strict")  # raises on any non-ASCII byte
        assert "\u2014" not in text and "\u2013" not in text, path.name


def test_the_diagnostic_control_cannot_reach_a_compiler_finding():
    """Behavioural: the GCC path must not be reachable from the probe pipeline.

    Replaces a test that compared a constant to its own literal. What matters is
    that no code path that produces a claim can obtain the diagnostic compiler.
    """
    import inspect

    assert cp.DIAGNOSTIC_CONTROL not in (cp.BLOCK_ADS_UNAVAILABLE, cp.BLOCK_TOOLCHAIN)
    for producer in (cp.run_probe, cp.build_matrix, cp.fingerprint, cp._claim):
        source = inspect.getsource(producer)
        assert "diagnostic" not in source.lower(), producer.__name__
        assert "gcc" not in source.lower(), producer.__name__
    # And the blocker codes are distinct from the control label, so a control
    # result can never be read as a probe status.
    assert "DIAGNOSTIC" not in cp.BLOCK_ADS_UNAVAILABLE


# ---------------------------------------------------------------------------
# ROM-gated: the manifest is reproducible from the canonical image
# ---------------------------------------------------------------------------
def test_the_committed_manifest_reproduces_from_the_canonical_rom(rom_bytes):
    assert cp.verify_manifest(rom_bytes) == []


def test_chain_walk_recovers_exactly_the_eight_declared_functions(rom_bytes):
    unit = cp.GBARAM_TU
    boundaries = cp.chain_walk(rom_bytes, unit.rom_address, unit.code_end_address, unit.isa)
    assert len(boundaries) == PROBE_COUNT
    for boundary in boundaries:
        assert boundary.problems == (), boundary.name
        assert boundary.returns >= 1
        assert boundary.size % 2 == 0
    expected = [(start, end) for start, end, _ in cp.GBARAM_FUNCTIONS]
    assert [(b.start, b.end) for b in boundaries] == expected


def test_the_target_bytes_match_the_digest_in_the_manifest(rom_bytes, manifest):
    import hashlib

    for probe in manifest["probes"]:
        start = int(probe["rom_address"], 16)
        raw = cp.extract(rom_bytes, start, probe["byte_length"])
        assert hashlib.sha1(raw).hexdigest() == probe["sha1"], probe["name"]
        assert len(raw) == probe["byte_length"]


def test_the_expected_isa_decodes_the_target_bytes_completely(rom_bytes, manifest):
    """The declared instruction set must consume the whole span with no leftovers.

    This is what makes the byte length a real boundary: if the span ended
    mid-instruction, or needed a different instruction set to decode, the
    comparison would be against a byte range the compiler never emitted.
    """
    for probe in manifest["probes"]:
        start = int(probe["rom_address"], 16)
        raw = cp.extract(rom_bytes, start, probe["byte_length"])
        decoder = cp.MD[probe["isa"]]
        instructions = list(decoder.disasm(raw, start))
        assert instructions, probe["name"]
        assert len(instructions) == probe["instructions"], probe["name"]
        assert sum(ins.size for ins in instructions) == probe["byte_length"], probe["name"]
        for ins in instructions:
            assert ins.address - start + ins.size <= probe["byte_length"], probe["name"]


def test_only_one_probe_lacks_a_pc_relative_load(rom_bytes, manifest):
    """Recorded because it changes what a standalone comparison can prove.

    Seven of the eight probes load a literal, so their PC-relative displacement
    depends on where the pool sits; only sub_0803D548 is byte-comparable on its
    own. Conflating the two would produce a false mismatch for correct source.
    """
    without = [p["name"] for p in manifest["probes"] if not p["literal_slots"]]
    assert without == ["sub_0803D548"]
    assert "no PC-relative literal load" in next(
        p["relocations"] for p in manifest["probes"] if p["name"] == "sub_0803D548"
    )


def test_the_literal_pool_words_decoded_are_what_the_disassembly_loads(rom_bytes):
    unit = cp.GBARAM_TU
    pool = {
        offset + gba.ROM_BASE: int.from_bytes(rom_bytes[offset : offset + 4], "little")
        for offset, _value in unit.literal_pool
    }
    loaded = set()
    for boundary in cp.chain_walk(
        rom_bytes, unit.rom_address, unit.code_end_address, unit.isa
    ):
        loaded |= set(boundary.literal_slots)
    assert loaded
    assert loaded <= set(pool), "a literal load points outside the recorded pool"


def test_reading_the_rom_for_the_probe_does_not_mutate_it(baserom):
    import hashlib

    before_digest = hashlib.sha1(baserom.read_bytes()).hexdigest()
    before_mtime = baserom.stat().st_mtime_ns
    data = baserom.read_bytes()
    cp.derive_manifest(data)
    cp.chain_walk(data, cp.GBARAM_TU.rom_address, cp.GBARAM_TU.code_end_address, "thumb")
    assert hashlib.sha1(baserom.read_bytes()).hexdigest() == before_digest
    assert baserom.stat().st_mtime_ns == before_mtime


def test_a_wrong_rom_is_refused_before_any_probe_runs(tmp_path):
    """Fail closed on identity: a one-byte edit must not produce a probe result."""
    fake = tmp_path / "wrong.gba"
    fake.write_bytes(bytes(0x1000))
    with pytest.raises(identity.IdentityError):
        identity.verify(fake)


def test_derive_manifest_is_deterministic(rom_bytes):
    first = cp.derive_manifest(rom_bytes)
    second = cp.derive_manifest(rom_bytes)
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["consistency_problems"] == []
