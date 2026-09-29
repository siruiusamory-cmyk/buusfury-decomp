"""DECOMP-LIFT-PILOT-001: the semantic lifting loop.

Three groups:

* PORTABLE tests need no toolchain and no ROM. They cover the registry, the
  promoted source layout, the semantic predicate and the comparison primitives.
* TOOLCHAIN-gated tests skip cleanly when no ARM cross toolchain exists.
* ROM-gated tests skip cleanly when no canonical baserom is present.

The ROM is opened READ-ONLY and no test writes to it.
"""

from __future__ import annotations

import hashlib
import json
import re

import pytest

from buusfury import identity, lift


# ---------------------------------------------------------------------------
# the registry
# ---------------------------------------------------------------------------
def test_registry_loads_and_declares_the_pilot_target():
    targets = lift.load_targets()
    assert "gbaram" in [t.id for t in targets]
    target = {t.id: t for t in targets}["gbaram"]
    assert target.probe_translation_unit == "gbaram_tu"
    assert target.cpu == "arm7tdmi"
    assert target.isa == "thumb"
    assert target.ticket == "DECOMP-LIFT-PILOT-001"


def test_every_registry_entry_declares_a_semantic_minimum_and_host_width():
    """Both are per-target: one global number or width would be wrong for one
    of them, and an entry missing either must not silently inherit a default."""
    for target in lift.load_targets():
        assert target.semantic_minimum_checks > 0, target.id
        assert target.host_build_bits in (32, 64), target.id
        assert target.selftest_source.endswith(".c"), target.id
        assert (identity.REPO_ROOT / target.selftest_source).is_file(), target.id


def test_registry_compiler_config_is_a_modern_configuration_not_an_ads_claim():
    target = lift.get_target("gbaram")
    assert target.optimization in ("-O0", "-O1", "-O2", "-O3", "-Os")
    # The modern compiler is NOT the original; the registry must not imply it is.
    registry = lift.load_target_registry()
    assert "ADS" in json.dumps(registry["_comment"])
    assert "not a" in json.dumps(registry["_comment"]).lower()


def test_unknown_target_is_refused():
    with pytest.raises(lift.LiftError):
        lift.get_target("does_not_exist")


def test_every_declared_source_exists():
    for target in lift.load_targets():
        assert (identity.REPO_ROOT / target.decomp_source).is_file(), target.decomp_source
        assert (identity.REPO_ROOT / target.probe_source).is_file(), target.probe_source


# ---------------------------------------------------------------------------
# the promotion into the real source tree
# ---------------------------------------------------------------------------
def test_the_implementation_lives_at_the_path_the_original_build_names():
    """The surviving command line says `src/GBARam.c`; that is where it now is."""
    implementation = identity.REPO_ROOT / "src" / "GBARam.c"
    assert implementation.is_file()
    text = implementation.read_text(encoding="utf-8")
    for name in (
        "sub_0803D4D0", "sub_0803D4E8", "sub_0803D520", "sub_0803D548",
        "sub_0803D56A", "sub_0803D5B8", "sub_0803D63C", "sub_0803D712",
    ):
        assert f"{name}(" in text, name


def test_the_probe_path_is_a_shim_and_not_a_second_copy():
    """One source of truth: the probe entry point must #include, not duplicate."""
    shim = (identity.REPO_ROOT / "src" / "probes" / "GBARam.c").read_text(encoding="utf-8")
    assert "#include" in shim and "../GBARam.c" in shim
    # A duplicated implementation would define the functions; a shim must not.
    assert "sub_0803D5B8(" not in shim
    assert len(shim.splitlines()) < 30, "the shim has grown into a second copy"


def test_the_promoted_source_still_carries_the_semantic_fixes():
    """The four defects the host run found must not be undone by the move."""
    text = (identity.REPO_ROOT / "src" / "GBARam.c").read_text(encoding="utf-8")
    # Signedness: the ROM emits `asrs`, so the locals must be signed.
    assert "int want" in text and "int best_size" in text
    assert "u32 want" not in text
    # The loop terminator tests the WORD before converting it.
    assert "block->prev == 0" in text
    # The sentinel is the search's initial best size, not a size guard.
    assert "0x7FFFFFFF" in text
    assert "sentinel" in text
    # No invented out-of-memory path.
    assert "NO out-of-memory path" in text


def test_the_manifest_still_points_at_the_probe_entry_point():
    """The probe manifest must keep naming a file that exists.

    The manifest records the translation unit's source CANDIDATE; if the
    promotion had deleted that path, the ADS probe leg would break silently.
    """
    manifest = json.loads((identity.CONFIG_DIR / "compiler_probes.json").read_text("utf-8"))
    units = {u["id"]: u for u in manifest["translation_units"]}
    candidate = units["gbaram_tu"]["source_candidate"]
    assert (identity.REPO_ROOT / candidate).is_file(), candidate


# ---------------------------------------------------------------------------
# the semantic predicate (pure, so no compiler is needed)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "returncode,checks,failures,expected",
    [
        (0, 230, 0, "PROVEN"),
        (0, 300, 0, "PROVEN"),
        (0, 229, 0, "PARTIAL"),   # checks were lost: never a pass
        (0, 0, 0, "PARTIAL"),
        (0, 230, 1, "FAILED"),
        (1, 230, 0, "FAILED"),
    ],
)
def test_semantic_verdict_requires_positive_evidence(returncode, checks, failures, expected):
    status, detail = lift.semantic_verdict(returncode, checks, failures)
    assert status == expected
    assert detail


def test_the_semantic_minimum_is_the_one_the_ticket_names():
    assert lift.MIN_SEMANTIC_CHECKS == 230


def test_the_verdict_vocabularies_are_separate():
    """Three questions, three vocabularies. Collapsing them is the defect class."""
    assert "PROVEN" in lift.SEMANTIC_STATES
    assert "PASS" in lift.MODERN_BUILD_STATES
    assert "BLOCKED" in lift.ADS_MATCH_STATES
    assert "PROVEN" not in lift.MODERN_BUILD_STATES
    assert "PASS" not in lift.ADS_MATCH_STATES


# ---------------------------------------------------------------------------
# toolchain discovery (portable: absence must be clean, not an exception)
# ---------------------------------------------------------------------------
def test_toolchain_discovery_returns_none_for_a_bogus_root(tmp_path):
    assert lift.discover_modern_toolchain(tmp_path / "nope") is None


def test_toolchain_discovery_is_all_or_nothing(tmp_path):
    """A partial installation must be reported absent rather than half-used."""
    (tmp_path / "bin").mkdir()
    (tmp_path / "bin" / "arm-none-eabi-gcc.exe").write_bytes(b"MZ")
    # gcc present, ld/objcopy/nm absent -> not a usable toolchain.
    assert lift.discover_modern_toolchain(tmp_path) is None


def test_root_relabelling_removes_machine_specific_paths(tmp_path):
    toolchain = lift.discover_modern_toolchain()
    if toolchain is None:
        pytest.skip("no modern toolchain available")
    assert "C:" not in toolchain.relabel(str(toolchain.gcc))
    assert toolchain.root_label in toolchain.relabel(str(toolchain.gcc))


# ---------------------------------------------------------------------------
# comparison primitives (portable)
# ---------------------------------------------------------------------------
def test_pool_runs_group_contiguous_slots():
    assert lift._pool_runs([0x100, 0x104, 0x108]) == [[0x100, 0x10C]]
    assert lift._pool_runs([0x100, 0x108]) == [[0x100, 0x104], [0x108, 0x10C]]
    assert lift._pool_runs([]) == []


def test_document_diff_detects_a_changed_leaf():
    """verify_report must not be vacuous: a changed key has to be reported."""
    assert lift._diff_documents({"a": 1}, {"a": 1}, "") == []
    assert lift._diff_documents({"a": 1}, {"a": 2}, "")
    assert lift._diff_documents({"a": 1}, {"b": 1}, "")
    assert lift._diff_documents({"a": [1, 2]}, {"a": [1, 2, 3]}, "")


def test_document_diff_reaches_nested_keys():
    """A subset comparison would let whole sections say anything."""
    expected = {"verdicts": {"ads_match": {"status": "BLOCKED"}}}
    actual = {"verdicts": {"ads_match": {"status": "PROVEN"}}}
    problems = lift._diff_documents(expected, actual, "")
    assert problems and "ads_match" in problems[0]


# ---------------------------------------------------------------------------
# the report, ROM- and toolchain-gated
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def lifted(request):
    """Run the loop once per session; the host self-check costs seconds."""
    toolchain = lift.discover_modern_toolchain()
    if toolchain is None:
        pytest.skip("no modern ARM toolchain available")
    try:
        from buusfury import identity as ident

        rom = ident.resolve_baserom()
        ident.verify(rom)
    except Exception as exc:  # noqa: BLE001 - the fixture's whole job is to skip
        pytest.skip(f"no canonical baserom available: {exc}")
    data = rom.read_bytes()
    return data, lift.run_lift("gbaram", data, toolchain)


def test_all_three_verdicts_are_present_and_in_their_own_vocabulary(lifted):
    _, document = lifted
    verdicts = document["verdicts"]
    assert set(verdicts) == {"semantic", "modern_build", "ads_match"}
    assert verdicts["semantic"]["status"] in lift.SEMANTIC_STATES
    assert verdicts["modern_build"]["status"] in lift.MODERN_BUILD_STATES
    assert verdicts["ads_match"]["status"] in lift.ADS_MATCH_STATES


def test_semantic_is_proven_with_the_required_check_count(lifted):
    _, document = lifted
    semantic = document["verdicts"]["semantic"]
    assert semantic["status"] == "PROVEN", semantic["detail"]
    assert semantic["checks"] >= lift.MIN_SEMANTIC_CHECKS
    assert semantic["failures"] == 0


def test_modern_build_passes_and_the_toolchain_is_identified(lifted):
    _, document = lifted
    build = document["modern_build"]
    assert build["status"] == "PASS", build["detail"]
    assert build["identity"]["gcc_version"]
    assert build["identity"]["target_triple"] == "arm-none-eabi"
    assert build["identity"]["is_the_original_compiler"] is False
    assert build["target_support"]["supported"] is True


def test_ads_match_is_blocked_and_never_promoted(lifted):
    _, document = lifted
    ads = document["verdicts"]["ads_match"]
    assert ads["status"] == "BLOCKED"
    assert ads["code"] == "ADS12_LICENSE_UNAVAILABLE"
    assert ads["not_inferable_from_modern_build"] is True


def test_the_modern_build_is_never_reported_as_a_match(lifted):
    """The one claim this ticket must not make."""
    _, document = lifted
    comparison = document["comparison"]
    assert comparison["is_a_match_claim"] is False
    assert "MEASUREMENT ONLY" in comparison["match_claim_note"]
    assert document["literal_pools"]["is_a_match_claim"] is False
    assert document["verdicts"]["ads_match"]["not_inferable_from_modern_build"] is True
    # And the measurement itself must not read as identity.
    assert comparison["byte_identical"] is False
    assert comparison["differing_bytes_in_overlap"] > 0


def test_comparison_counts_are_clamped_and_add_up(lifted):
    _, document = lifted
    comparison = document["comparison"]
    for key in (
        "original_byte_length", "modern_byte_length", "overlap_byte_length",
        "differing_bytes_in_overlap", "matching_bytes_in_overlap",
        "original_only_bytes", "modern_only_bytes",
        "original_instruction_spans", "matching_instruction_spans",
        "differing_instruction_spans", "bytes_not_covered_by_an_original_instruction",
    ):
        assert comparison[key] >= 0, key
    assert (
        comparison["matching_bytes_in_overlap"] + comparison["differing_bytes_in_overlap"]
        == comparison["overlap_byte_length"]
    )
    assert (
        comparison["matching_instruction_spans"] + comparison["differing_instruction_spans"]
        <= comparison["original_instruction_spans"]
    )
    # The instruction spans must be keyed on the ORIGINAL's boundaries and must
    # cover the code body, not the literal pool.
    assert comparison["original_instruction_spans"] > 0
    assert comparison["bytes_not_covered_by_an_original_instruction"] >= 0


def test_every_function_is_paired_by_name(lifted):
    _, document = lifted
    rows = document["functions"]
    assert len(rows) == 8
    assert [r["name"] for r in rows] == [f"sub_{a:08X}" for a, _e, _r in __import__(
        "buusfury.compiler_probe", fromlist=["x"]
    ).GBARAM_FUNCTIONS]
    for row in rows:
        assert row["modern_symbol_present"] is True, row["name"]
        assert row["original"]["size"] > 0
        assert row["modern"]["size"] > 0


def test_the_original_pool_is_shared_and_the_modern_one_is_not(lifted):
    """The structural divergence the loop exists to make visible."""
    _, document = lifted
    pools = document["literal_pools"]
    assert pools["original"]["shared_pool"] is True
    assert pools["original"]["run_count"] == 1
    assert pools["original"]["functions_reaching_it"] == 7
    assert pools["original"]["contiguous_runs"] == [["0x0803D730", "0x0803D740"]]
    assert pools["modern"]["shared_pool"] is False
    assert pools["modern"]["run_count"] > 1


def test_abi_facts_are_recorded_for_every_function(lifted):
    _, document = lifted
    for row in document["functions"]:
        for side in ("original", "modern"):
            abi = row[side]["abi"]
            assert isinstance(abi["callee_saved_pushed"], list)
            assert abi["frame_size_bytes"] >= 0
            assert isinstance(abi["written_registers"], list)
        assert "leaf" in row["original"] and "returns" in row["original"]


def test_the_committed_report_matches_a_fresh_run(lifted):
    toolchain = lift.discover_modern_toolchain()
    data, _ = lifted
    result = lift.verify_report(data, "gbaram")
    # recorded with the reason when the host compiler is missing
    if result["exempted"]:
        assert "no host C compiler" in result["exempted"][0]
    assert result["ok"], result["problems"][:10]


def test_the_committed_report_is_environment_independent():
    """A committed report must not carry a machine-specific path."""
    path = lift.report_path_for("gbaram")
    raw = path.read_bytes()
    assert b"\r\n" not in raw, "the report must be LF-only"
    text = raw.decode("utf-8")
    assert "devkitPro" not in text
    assert not re.search(r"[A-Za-z]:\\\\", text), "an absolute Windows path leaked"
    assert lift.ModernToolchain.__name__
    document = json.loads(text)
    assert document["modern_build"]["toolchain"]["root"] == "<DEVKITARM>"


def test_the_report_names_the_canonical_rom(lifted):
    data, document = lifted
    assert document["source_sha1"] == hashlib.sha1(data).hexdigest()
    assert document["target"]["rom_address"] == "0x0803D4D0"
    assert document["target"]["byte_length"] == 624
    assert document["target"]["code_byte_length"] == 608


def test_a_report_cannot_be_verified_without_a_toolchain(monkeypatch):
    monkeypatch.setattr(lift, "discover_modern_toolchain", lambda root=None: None)
    result = lift.verify_report(b"\x00" * 16, "gbaram")
    assert result["ok"] is False
    assert "no modern toolchain" in result["problems"][0]
