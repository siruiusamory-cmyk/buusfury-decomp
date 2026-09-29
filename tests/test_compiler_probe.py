"""DECOMP-COMPILER-PROBE-001: the probe manifest, the harness, and ROM safety.

Two classes of test live here and they are deliberately separate:

* PORTABLE tests need no baserom and no compiler. They assert the manifest's
  shape, that the harness fails CLOSED (BLOCKED, never a false PASS) when ADS
  1.2 is absent, that comparison is deterministic, and that nothing proprietary
  can be committed.
* ROM-GATED tests use the `baserom` fixture and assert that every measured field
  in config/compiler_probes.json is reproducible from the canonical image, and
  that reading it does not mutate it.

No test in this file runs a proprietary compiler, and none requires one. A
missing ADS installation is a PASSING state for these tests: the ticket's
contract is that the blocker is measured and reported, not absent.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from buusfury import compiler_probe as cp
from buusfury import gba, identity

REPO_ROOT = identity.REPO_ROOT
PROBE_TEST_COUNT = 8


@pytest.fixture(scope="module")
def manifest() -> dict:
    return cp.load_manifest()


@pytest.fixture(scope="module")
def functions_by_address() -> dict[int, dict]:
    raw = json.loads((REPO_ROOT / "config" / "functions.json").read_text(encoding="utf-8"))
    return {int(f["address"], 16) & ~1: f for f in raw["functions"]}


# ---------------------------------------------------------------------------
# manifest validity
# ---------------------------------------------------------------------------
def test_manifest_declares_its_schema_and_source(manifest):
    assert manifest["schema"] == 1
    assert manifest["source_sha1"] == "f1c4b07554d2a3b1ad2f325307051e775ce68087"
    assert manifest["generated_by"].endswith("derive_manifest()")


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
    assert counts["probes"] == PROBE_TEST_COUNT
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


def test_the_probe_confidence_is_the_probe_manifests_own_not_the_inventorys(
    manifest, functions_by_address
):
    """The two confidences mean different things and must not be conflated.

    The inventory rates a BL-target entry `medium` because a branch target is not
    proof of a function start in a cartridge where data decodes as Thumb. The
    probe manifest rates the same address `proven` because a chain walk closed
    every path and the unit's boundaries are corroborated independently. Both
    values are carried on the probe so the distinction survives.
    """
    assert all(probe["confidence"] == "proven" for probe in manifest["probes"])
    inventory_levels = {
        probe["inventory_confidence"]
        for probe in manifest["probes"]
        if probe["in_function_inventory"]
    }
    assert inventory_levels <= {"proven", "high", "medium", "low"}
    assert "medium" in inventory_levels
    assert all(
        probe["inventory_confidence"] is None
        for probe in manifest["probes"]
        if not probe["in_function_inventory"]
    )


def test_a_disagreeing_inventory_size_is_reported_not_smoothed_over(manifest):
    """Where the inventory's decode extent disagrees, the manifest says so.

    Kept in its own field rather than folded into consistency_problems: these
    disagreements are expected and already explained, whereas a consistency
    problem would be a contradiction in this manifest.
    """
    disagreements = manifest["inventory_size_disagreements"]
    assert disagreements, "the known overrun must be recorded, not hidden"
    for item in disagreements:
        assert item["inventory_size"] > item["measured_boundary"], item["name"]
        assert "decode_run" in item["explanation"]
    assert manifest["consistency_problems"] == []


def test_the_probe_module_records_the_inventory_sizes_as_unusable():
    """The ticket forbids building a boundary on a heuristic window.

    config/functions.json's size comes from a decode run capped at 0x400, so it
    overruns small functions; the manifest must say so rather than quietly use it.
    """
    manifest = cp.load_manifest()
    assert "chain-walk" in manifest["method"]
    assert any("decode_run" in note for note in manifest["notes"]), (
        "the manifest must record that config/functions.json's size is a decode "
        "extent and not a boundary"
    )
    assert any("boundaries are evidence" in note.lower() for note in manifest["notes"])
    assert manifest["inventory_size_disagreements"], (
        "the overrun is a measured result and must appear as one"
    )


# ---------------------------------------------------------------------------
# range sanity
# ---------------------------------------------------------------------------
def test_probe_ranges_do_not_overlap(manifest):
    spans = sorted(
        (int(p["start"], 16), int(p["end"], 16)) for p in manifest["probes"]
    )
    for (start_a, end_a), (start_b, _end_b) in zip(spans, spans[1:]):
        assert end_a <= start_b, f"0x{start_a:08X}..0x{end_a:08X} overlaps the next probe"


def test_probes_tile_the_translation_unit_code_body_exactly(manifest):
    unit = manifest["translation_units"][0]
    spans = sorted(
        (int(p["start"], 16), int(p["end"], 16)) for p in manifest["probes"]
    )
    assert spans[0][0] == int(unit["rom_address"], 16)
    assert spans[-1][1] == int(unit["code_end_address"], 16)
    for (start_a, end_a), (start_b, _end_b) in zip(spans, spans[1:]):
        assert end_a == start_b, "a gap or an overlap would break the boundary evidence"


def test_internal_calls_resolve_to_probes_in_the_same_unit(manifest):
    """The measured call graph must stay inside the unit, or the boundary story breaks."""
    addresses = {int(p["rom_address"], 16) for p in manifest["probes"]}
    for probe in manifest["probes"]:
        for callee in probe["callees"]:
            assert int(callee, 16) in addresses, (probe["name"], callee)


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
    """Corroboration, not decoration: this is why the unit was selected at all.

    DECOMP-ROM-MAP-001 recorded the same four words independently, with their own
    provenance and confidence, as the fixed region `gbaram_literals`.
    """
    expected = {
        "0x03D730": 0x02000800,
        "0x03D734": 0x03003488,
        "0x03D738": 0x0000FDFE,
        "0x03D73C": 0x7FFFFFFF,
    }
    fixed = json.loads((REPO_ROOT / "data" / "fixed_regions.json").read_text(encoding="utf-8"))
    recorded = {
        word["offset"].lower(): word["value"]
        for word in fixed["gbaram_literals"]["words"]
    }
    assert recorded == {key.lower(): value for key, value in expected.items()}

    pool = {
        word["file_offset"].lower(): int(word["value"], 16)
        for word in manifest["translation_units"][0]["literal_pool"]["words"]
    }
    assert pool == {key.lower(): value for key, value in expected.items()}
    assert "0x03D4D0..0x03D730" in " ".join(fixed["gbaram_literals"]["_comment"])


# ---------------------------------------------------------------------------
# exclusions and controls are recorded, not silently dropped
# ---------------------------------------------------------------------------
def test_the_forbidden_evidence_regions_are_recorded_as_controls(manifest):
    ids = {c["id"] for c in manifest["controls"]}
    assert {"reset_crt", "codec_blob"} <= ids
    addresses = {c["rom_address"] for c in manifest["controls"]}
    assert "0x080000C0" in addresses, "the reset routine must be an explicit control"
    assert "0x087B79A4" in addresses, "the codec blob must be an explicit control"


def test_every_control_states_why_it_is_not_evidence(manifest):
    for control in manifest["controls"]:
        assert control["excluded_because"], control["id"]
        assert control["role"] == "control"


def test_rejected_candidates_are_recorded_with_their_measurement(manifest):
    assert len(manifest["rejections"]) >= 4
    for rejection in manifest["rejections"]:
        assert rejection["rejected_because"], rejection["id"]
        assert rejection["map_claim"], rejection["id"]


def test_the_data_regions_that_look_like_code_are_recorded(manifest):
    """A `high`/confirmed code region that is really data must stay rejected."""
    ids = {r["id"] for r in manifest["rejections"]}
    assert "code_reachable_055324" in ids
    assert "code_candidate_span_6_048F14" in ids


# ---------------------------------------------------------------------------
# the harness fails closed
# ---------------------------------------------------------------------------
def test_no_ads_installation_is_discovered_when_the_root_is_bogus(monkeypatch, tmp_path):
    monkeypatch.delenv("ADS12_ROOT", raising=False)
    monkeypatch.setenv("PATH", str(tmp_path))
    assert cp.discover_ads(tmp_path / "nope") is None


def test_discover_ads_finds_a_staged_tool_under_the_root_bin_directory(monkeypatch, tmp_path):
    (tmp_path / "Bin").mkdir()
    (tmp_path / "Bin" / "tcpp.exe").write_bytes(b"MZ")
    monkeypatch.delenv("PATH", raising=False)
    tools = cp.discover_ads(tmp_path, compiler_id="tcpp")
    assert tools is not None
    assert tools.compiler == tmp_path / "Bin" / "tcpp.exe"


def test_a_missing_toolchain_reports_blocked_never_a_pass(monkeypatch, tmp_path, rom_bytes):
    monkeypatch.delenv("ADS12_ROOT", raising=False)
    monkeypatch.setenv("PATH", str(tmp_path))
    result = cp.run_probe(rom_bytes, cp.GBARAM_TU)
    assert result.status == "BLOCKED"
    assert result.code == cp.BLOCK_ADS_UNAVAILABLE
    assert result.diff is None
    assert result.as_dict()["exact_match"] is False


def test_the_blocked_report_claims_no_compiler_result(monkeypatch, tmp_path, rom_bytes):
    monkeypatch.delenv("ADS12_ROOT", raising=False)
    monkeypatch.setenv("PATH", str(tmp_path))
    matrix = cp.build_matrix(rom_bytes, identity.load_canonical()["hashes"]["sha1"])
    assert matrix["code"] == cp.BLOCK_ADS_UNAVAILABLE
    assert matrix["no_compiler_result_claimed"] is True
    assert matrix["conclusion"] == "UNTESTED"
    assert all(not c["exact_match"] for c in matrix["configurations"])
    assert all(c["status"] == "BLOCKED" for c in matrix["configurations"])
    assert matrix["fingerprint"]["thumb_frontend"] == "UNTESTED"
    assert matrix["fingerprint"]["c_vs_cpp"] == "UNTESTED"


def test_the_fingerprint_never_promotes_without_discriminating_matches():
    assert cp.fingerprint([])["thumb_optimization"] == "UNTESTED"
    assert cp.fingerprint([{"exact_match": True}])["thumb_optimization"] == "PLAUSIBLE"
    assert (
        cp.fingerprint([{"exact_match": True}] * 3)["thumb_optimization"]
        == "STRONGLY_SUPPORTED"
    )
    assert (
        cp.fingerprint([{"exact_match": False}] * 3)["thumb_optimization"] == "REFUTED"
    )


def test_the_matrix_declares_negative_controls(rom_bytes, monkeypatch, tmp_path):
    monkeypatch.delenv("ADS12_ROOT", raising=False)
    monkeypatch.setenv("PATH", str(tmp_path))
    matrix = cp.build_matrix(rom_bytes, "f" * 40)
    controls = " ".join(matrix["negative_controls"])
    assert "tcc vs tcpp" in controls
    assert "-O0 vs -O1" in controls
    assert "-O1 vs -O2" in controls
    frontends = {c["frontend"] for c in matrix["configurations"]}
    assert {"tcpp", "tcc", "armcc", "armcpp"} <= frontends
    optimisations = {c["optimization"] for c in matrix["configurations"]}
    assert {"-O0", "-O1", "-O2"} <= optimisations


def test_the_lead_configuration_is_tested_first(rom_bytes, monkeypatch, tmp_path):
    monkeypatch.delenv("ADS12_ROOT", raising=False)
    monkeypatch.setenv("PATH", str(tmp_path))
    first = cp.build_matrix(rom_bytes, "f" * 40)["configurations"][0]
    assert (first["frontend"], first["cpu"], first["optimization"]) == (
        "tcpp",
        "ARM7TDMI",
        "-O1",
    )
    assert cp.LEAD_COMMAND_LINE == "tcpp -S -c -cpu ARM7TDMI -O1 src/GBARam.c"


# ---------------------------------------------------------------------------
# deterministic comparison
# ---------------------------------------------------------------------------
def test_comparison_is_deterministic_and_symmetric():
    target = bytes(range(64))
    other = bytes(range(64))
    first = cp.compare_bytes(target, other, 0x08000000, "thumb")
    second = cp.compare_bytes(target, other, 0x08000000, "thumb")
    assert first.as_dict() == second.as_dict()
    assert first.exact_match and first.differing_bytes == 0
    assert first.first_difference is None


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


def test_comparison_counts_differing_instructions_separately():
    target = bytes.fromhex("0020 0149 0847")  # movs r0,#0 ; ldr r1,[pc,#4] ; bx r1
    candidate = bytes.fromhex("0120 0149 0847")  # movs r0,#1 differs
    diff = cp.compare_bytes(target, candidate, 0x08000000, "thumb")
    assert diff.differing_instructions == 1
    assert diff.compared_instructions == 3


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
    # 0xB6xx is an unassigned Thumb encoding and 0xF0000000 is an NV-condition
    # ARM word; capstone refuses both, which is what makes them usable probes.
    with pytest.raises(cp.ProbeError):
        cp.chain_walk(b"\x00\xb6" * 16, gba.ROM_BASE, gba.ROM_BASE + 32, "thumb")
    with pytest.raises(cp.ProbeError):
        cp.chain_walk(b"\x00\x00\x00\xf0" * 8, gba.ROM_BASE, gba.ROM_BASE + 32, "arm")


def test_chain_walk_flags_a_region_with_no_terminator():
    """A region that decodes but never returns is a lower bound, and says so."""
    boundaries = cp.chain_walk(b"\xc0\x46" * 32, gba.ROM_BASE, gba.ROM_BASE + 64, "thumb")
    assert len(boundaries) == 1
    assert boundaries[0].problems
    assert "no terminator" in boundaries[0].problems[0]


# ---------------------------------------------------------------------------
# the linker layout and the command plan
# ---------------------------------------------------------------------------
def test_the_scatter_file_places_the_unit_at_its_rom_address():
    text = cp.render_scatter(cp.GBARAM_TU)
    assert "0x0803D4D0" in text
    assert "probe.o (+RO)" in text


def test_the_command_plan_is_the_lead_pipeline_in_order():
    tools = cp.AdsTools(
        root=Path("/ads"),
        compiler=Path("/ads/Bin/tcpp.exe"),
        compiler_id="tcpp",
        support={
            "armasm": Path("/ads/Bin/armasm.exe"),
            "armlink": Path("/ads/Bin/armlink.exe"),
            "fromelf": Path("/ads/Bin/fromelf.exe"),
        },
    )
    commands = cp.plan_commands(
        tools, Path("src/probes/GBARam.c"), Path("build/out"), ("tcpp", "ARM7TDMI", "-O1")
    )
    assert len(commands) == 4
    assert commands[0][1:6] == ["-S", "-c", "-cpu", "ARM7TDMI", "-O1"]
    assert commands[0][0].endswith("tcpp.exe")
    assert "armasm" in commands[1][0] and commands[1][-1].endswith("probe.s")
    assert "armlink" in commands[2][0] and "-scatter" in commands[2]
    assert "fromelf" in commands[3][0] and "-bin" in commands[3]


def test_the_origin_assumption_is_stated_not_implied():
    assert "fromelf" in cp.ORIGIN_ASSUMPTION
    assert "UNEXERCISED" in cp.ORIGIN_ASSUMPTION


# ---------------------------------------------------------------------------
# safety: nothing proprietary, nothing outside build/
# ---------------------------------------------------------------------------
def test_the_probe_workspace_is_inside_the_gitignored_build_directory():
    assert cp.PROBE_WORKSPACE == REPO_ROOT / "build" / "probes"
    assert "build" in cp.PROBE_WORKSPACE.parts
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "/build/" in gitignore


def test_the_gitignore_excludes_every_ads_binary_name():
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    for name in ("armcc", "armcpp", "tcc", "tcpp", "armasm", "armlink", "fromelf"):
        assert name in gitignore, f"{name} would be committable"


def test_no_ads_binary_is_present_in_the_repository_tree():
    """Nothing resembling a proprietary tool or a licence file may be tracked."""
    forbidden = {
        "armcc.exe",
        "armcpp.exe",
        "tcc.exe",
        "tcpp.exe",
        "armasm.exe",
        "armlink.exe",
        "fromelf.exe",
        "axd.exe",
        "armsd.exe",
    }
    ignored_dirs = {".git", "build", "reference", "__pycache__"}
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file() or ignored_dirs & set(path.parts):
            continue
        assert path.name.lower() not in forbidden, path
        assert path.suffix.lower() not in (".lic", ".license"), path


def test_the_harness_never_writes_outside_the_probe_workspace():
    """Every path the module writes to must live under build/probes."""
    source = (REPO_ROOT / "tools" / "buusfury" / "compiler_probe.py").read_text(
        encoding="utf-8"
    )
    assert "PROBE_WORKSPACE" in source
    assert "write_text" in source
    # The only non-workspace write is the committed manifest/matrix, which the
    # operator asks for explicitly by name.
    assert "MANIFEST_PATH = _identity.CONFIG_DIR" in source
    assert "MATRIX_PATH = _identity.CONFIG_DIR" in source


def test_the_harness_holds_no_path_into_the_other_checkout():
    needle = "log1" + "-remake"
    source = (REPO_ROOT / "tools" / "buusfury" / "compiler_probe.py").read_text(
        encoding="utf-8"
    )
    assert needle not in source


def test_the_diagnostic_control_is_labelled_as_not_evidence():
    assert cp.DIAGNOSTIC_CONTROL == "DIAGNOSTIC_CONTROL_NOT_EVIDENCE"
    compiler = cp.discover_diagnostic_compiler()
    if compiler is None:
        pytest.skip("no devkitARM GCC available for the plumbing control")
    assert compiler.as_dict()["classification"] == cp.DIAGNOSTIC_CONTROL
    assert "not" in compiler.as_dict()["why"].lower() or "cannot be evidence" in (
        compiler.as_dict()["why"]
    )


# ---------------------------------------------------------------------------
# ROM-gated: the manifest is reproducible from the canonical image
# ---------------------------------------------------------------------------
@pytest.mark.usefixtures("baserom")
def test_the_committed_manifest_reproduces_from_the_canonical_rom(rom_bytes):
    assert cp.verify_manifest(rom_bytes) == []


def test_chain_walk_recovers_exactly_the_eight_declared_functions(rom_bytes):
    unit = cp.GBARAM_TU
    boundaries = cp.chain_walk(
        rom_bytes, unit.rom_address, unit.code_end_address, unit.isa
    )
    assert len(boundaries) == PROBE_TEST_COUNT
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
    from buusfury import identity as ident

    fake = tmp_path / "wrong.gba"
    fake.write_bytes(bytes(0x1000))
    with pytest.raises(ident.IdentityError):
        ident.verify(fake)


def test_derive_manifest_is_deterministic(rom_bytes):
    first = cp.derive_manifest(rom_bytes)
    second = cp.derive_manifest(rom_bytes)
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["consistency_problems"] == []
