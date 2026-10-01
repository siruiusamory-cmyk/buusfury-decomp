"""Focused tests for the decomp.dev semantic progress integration.

INFRA-DECOMPDEV-001. These tests are deliberately narrow: they cover the new
infrastructure and nothing else. The project's full suite is not part of this
ticket's contract.

The subject is a SEMANTIC reconstruction, so the tests are as much about what the
report must NOT say as about what it says:

  * a unit is credited only when a committed lift report says SEMANTIC = PROVEN;
  * MODERN_BUILD = PASS earns nothing, and ADS_MATCH = BLOCKED costs nothing;
  * the credited size is the function's ORIGINAL byte size, never the modern
    GCC output size;
  * unreconstructed functions stay in the denominator at zero;
  * the denominator cannot shrink as a side effect of proving something;
  * no cartridge bytes, no absolute local path and no non-objdiff field can
    reach the artifact.

Nothing here needs the canonical ROM, a compiler or a build: the report is
derived from committed provenance only.
"""

from __future__ import annotations

import copy
import json
import re

import pytest

from buusfury import decompdev as dd


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def inventory() -> dd.Inventory:
    return dd.build_inventory(dd.load_inputs())


@pytest.fixture(scope="module")
def report(inventory: dd.Inventory) -> dict:
    return dd.objdiff_report(inventory)


@pytest.fixture(scope="module")
def report_text(report: dict) -> str:
    return dd.render_report_json(report)


def _unit(report: dict, name: str) -> dict:
    for unit in report["units"]:
        if unit["name"] == name:
            return unit
    raise AssertionError(f"no unit named {name!r}")


def _credited_unit_name(report: dict) -> str:
    for unit in report["units"]:
        if unit["measures"].get("matched_code"):
            return unit["name"]
    raise AssertionError("no credited unit in the report")


# ---------------------------------------------------------------------------
# 1. valid objdiff report version, and a schema that only holds objdiff fields
# ---------------------------------------------------------------------------
def test_report_is_a_valid_objdiff_report_version_2(report: dict) -> None:
    assert report["version"] == dd.REPORT_VERSION == 2
    assert dd.report_schema_findings(report) == []


def test_the_schema_validator_rejects_an_unsupported_version(report: dict) -> None:
    """A validator that cannot fail is not a validator."""
    broken = copy.deepcopy(report)
    broken["version"] = 3
    assert dd.report_schema_findings(broken)

    broken = copy.deepcopy(report)
    broken["units"][0]["invented_field"] = True
    assert dd.report_schema_findings(broken)

    # objdiff's deserialiser types `size` as uint64, which JSON carries as a
    # string; a bare number is a different document.
    broken = copy.deepcopy(report)
    for unit in broken["units"]:
        if unit.get("functions"):
            unit["functions"][0]["size"] = 64
            break
    assert dd.report_schema_findings(broken)


def test_u64_fields_are_json_strings_and_the_first_byte_is_an_open_brace(report_text: str) -> None:
    """objdiff picks JSON-vs-protobuf from byte 0, so a BOM or leading space breaks it."""
    assert report_text[0] == "{"
    document = json.loads(report_text)
    assert isinstance(document["measures"]["total_code"], str)
    assert isinstance(document["measures"]["matched_code"], str)
    assert isinstance(document["version"], int)
    for unit in document["units"]:
        if unit.get("functions"):
            assert isinstance(unit["functions"][0]["size"], str)


# ---------------------------------------------------------------------------
# 2. deterministic output
# ---------------------------------------------------------------------------
def test_report_generation_is_deterministic(inventory: dd.Inventory) -> None:
    first = dd.render_report_json(dd.objdiff_report(inventory))
    second = dd.render_report_json(dd.objdiff_report(inventory))
    assert first == second
    assert "\r" not in first  # LF only, so a checkout cannot change the bytes


def test_the_committed_report_is_current(inventory: dd.Inventory) -> None:
    committed = dd.REPORT_PATH.read_text(encoding="utf-8")
    assert committed == dd.render_report_json(dd.objdiff_report(inventory))


def test_the_committed_inventory_reproduces(inventory: dd.Inventory) -> None:
    assert dd.compare_inventory(inventory) == []


# ---------------------------------------------------------------------------
# 3 and 4. the aggregates are exactly the sums of the units
# ---------------------------------------------------------------------------
def test_aggregate_byte_totals_equal_the_unit_sums(report: dict) -> None:
    total = sum(int(u["measures"].get("total_code", 0)) for u in report["units"])
    matched = sum(int(u["measures"].get("matched_code", 0)) for u in report["units"])
    assert int(report["measures"]["total_code"]) == total
    assert int(report["measures"]["matched_code"]) == matched


def test_aggregate_function_totals_equal_the_unit_sums(report: dict) -> None:
    total = sum(int(u["measures"].get("total_functions", 0)) for u in report["units"])
    matched = sum(int(u["measures"].get("matched_functions", 0)) for u in report["units"])
    assert report["measures"]["total_functions"] == total
    assert report["measures"]["matched_functions"] == matched
    # A unit that is not a function must not be counted as one.
    remainder = [u for u in report["units"] if not u.get("functions")]
    assert remainder, "the inventory should have unattributed remainder units"
    assert all("total_functions" not in u["measures"] for u in remainder)


# ---------------------------------------------------------------------------
# 5. what semantic-complete means
# ---------------------------------------------------------------------------
def test_semantic_complete_units_are_exactly_the_proven_ones(
    inventory: dd.Inventory, report: dict
) -> None:
    credited = [u for u in inventory.units if u.credited]
    assert credited, "the project has committed SEMANTIC PROVEN work"
    for unit in credited:
        assert unit.status == dd.STATUS_COMPLETE
        assert unit.evidence and unit.lift_target and unit.source
        assert unit.instructions
        assert unit.extent == dd.EXTENT_MEASURED
    # and every credited function's own report says PROVEN
    proven = {
        function.address
        for target in inventory.inputs.lift_reports
        if target.semantic == dd.CREDIT_VERDICT
        for function in target.functions
    }
    assert len(credited) == len(proven)
    assert report["measures"]["matched_functions"] == len(credited)
    assert all(u["measures"].get("matched_code") for u in report["units"] if u.get("functions") and u["measures"].get("matched_functions"))


def test_a_credited_unit_cannot_lose_its_evidence(inventory: dd.Inventory) -> None:
    broken = dd.build_inventory(dd.load_inputs())
    unit = next(u for u in broken.units if u.credited)
    unit.evidence = None
    problems = broken.validate()
    assert any("no evidence" in p for p in problems)


# ---------------------------------------------------------------------------
# 6. unresolved functions remain, at zero
# ---------------------------------------------------------------------------
def test_unreconstructed_functions_remain_in_the_denominator_at_zero(
    inventory: dd.Inventory, report: dict
) -> None:
    pending = [u for u in inventory.function_units if not u.credited]
    assert pending, "the project is nowhere near finished"
    for unit in pending[:25]:
        rendered = _unit(report, unit.unit_name)
        assert "matched_code" not in rendered["measures"]
        assert "matched_functions" not in rendered["measures"]
        # ...but its bytes ARE in the denominator
        assert int(rendered["measures"]["total_code"]) == unit.size > 0


# ---------------------------------------------------------------------------
# 7. MODERN_BUILD alone earns nothing
# ---------------------------------------------------------------------------
def test_modern_build_only_function_is_not_semantic_complete() -> None:
    inputs = dd.load_inputs()
    target = next(r for r in inputs.lift_reports if r.credited)
    assert target.modern_build == "PASS"
    before = dd.build_inventory(inputs)
    evidence_before = {
        u.unit_name: u.evidence for u in before.units if u.credited
    }

    # Same measurements, same MODERN_BUILD, but the behavioural verdict is not
    # PROVEN. Credit must vanish for exactly that target's functions.
    target.semantic = "PARTIAL"
    after = dd.build_inventory(inputs)
    evidence_after = {u.unit_name: u.evidence for u in after.units if u.credited}

    removed = set(evidence_before) - set(evidence_after)
    assert removed, "losing a PROVEN verdict must withdraw credit"
    assert all(
        evidence_before[name] == f"config/{target.path.name}" for name in removed
    )
    assert len(removed) == len(target.functions)


# ---------------------------------------------------------------------------
# 8. ADS_MATCH is irrelevant to semantic credit
# ---------------------------------------------------------------------------
def test_ads_blocked_does_not_affect_semantic_credit(inventory: dd.Inventory) -> None:
    assert all(r.ads_match == "BLOCKED" for r in inventory.inputs.lift_reports)
    assert all(
        r.document["verdicts"]["ads_match"]["not_inferable_from_modern_build"] is True
        for r in inventory.inputs.lift_reports
    )
    inputs = dd.load_inputs()
    baseline = dd.build_inventory(inputs)
    for target in inputs.lift_reports:
        target.ads_match = "UNTESTED"
        target.ads_code = ""
    after = dd.build_inventory(inputs)
    assert after.complete_functions == baseline.complete_functions
    assert after.complete_bytes == baseline.complete_bytes
    assert after.tracked_executable_bytes == baseline.tracked_executable_bytes


# ---------------------------------------------------------------------------
# 9. the size is the ORIGINAL size, never the modern output size
# ---------------------------------------------------------------------------
def test_original_size_is_used_and_not_the_modern_output_size(inventory: dd.Inventory) -> None:
    discrepancies = []
    for target in inventory.inputs.lift_reports:
        rows = {int(f["original"]["start"], 0): f for f in target.document["functions"]}
        for function in target.functions:
            row = rows[function.address]
            modern = row.get("modern")
            if modern and modern["size"] != function.size:
                discrepancies.append((function.address, function.size, modern["size"]))
    assert discrepancies, "at least one function has a modern size that differs"

    by_address = {
        (u.rom_address if u.rom_address is not None else u.address): u
        for u in inventory.units
    }
    for address, original, modern in discrepancies:
        unit = by_address[address]
        assert unit.size == original
        assert unit.size != modern


# ---------------------------------------------------------------------------
# 10. IWRAM overlay accounting
# ---------------------------------------------------------------------------
def test_iwram_overlay_units_account_for_their_copied_code(inventory: dd.Inventory) -> None:
    overlay = {r["id"]: r for r in inventory.regions}["iwram_overlay"]
    members = [u for u in inventory.units if u.region == "iwram_overlay"]
    functions = [u for u in members if u.is_function]

    assert overlay["length"] == inventory.inputs.overlay_code_bytes
    assert sum(u.size for u in members) == overlay["length"]
    assert len(functions) == 18  # 16 reachable + 2 complete unreachable
    assert sum(u.size for u in functions) + sum(
        u.size for u in members if not u.is_function
    ) == overlay["length"]

    # every overlay function is measured (the block derivation is an exact walk)
    assert {u.extent for u in functions} == {dd.EXTENT_MEASURED}
    # the runtime address and the ROM source address are both carried, and the
    # ROM source lies inside the region the map classified as the copied block
    for unit in functions:
        assert dd.IWRAM_BASE <= unit.address < 0x03001004
        assert unit.rom_address is not None
        assert (
            int(inventory.inputs.overlay["block"]["rom_source"], 0)
            <= unit.rom_address
            < int(inventory.inputs.overlay["block"]["rom_source"], 0)
            + int(inventory.inputs.overlay["block"]["bytes"])
        )

    # the overlay's source bytes are NOT also tracked as cartridge functions
    overlay_start = int(inventory.inputs.overlay["block"]["rom_source"], 0)
    overlay_end = overlay_start + int(inventory.inputs.overlay["block"]["bytes"])
    assert not [
        u for u in inventory.units
        if u.address is not None and overlay_start <= u.address < overlay_end
    ]


def test_iwram_and_cartridge_units_do_not_share_an_address_space(inventory: dd.Inventory) -> None:
    iwram = [u for u in inventory.units if u.region == "iwram_overlay" and u.address is not None]
    rom = [u for u in inventory.units if u.region != "iwram_overlay" and u.address is not None]
    assert all(u.address >= dd.IWRAM_BASE for u in iwram)
    assert all(u.address >= 0x08000000 for u in rom)


# ---------------------------------------------------------------------------
# 11. categories
# ---------------------------------------------------------------------------
def test_category_measures_equal_their_member_units(report: dict) -> None:
    assert dd.category_totals(report) == []
    category_bytes = sum(int(c["measures"].get("total_code", 0)) for c in report["categories"])
    category_functions = sum(int(c["measures"].get("total_functions", 0)) for c in report["categories"])
    assert category_bytes == int(report["measures"]["total_code"])
    assert category_functions == report["measures"]["total_functions"]


def test_every_unit_belongs_to_exactly_one_declared_category(report: dict) -> None:
    for unit in report["units"]:
        categories = unit["metadata"]["progress_categories"]
        assert len(categories) == 1
        assert categories[0] in dd.CATEGORY_NAMES
    # and the category display names say what this actually is
    for category in report["categories"]:
        assert category["name"] == dd.CATEGORY_NAMES[category["id"]]
    reconstructed = [
        c for c in report["categories"] if c["measures"].get("matched_code")
    ]
    assert reconstructed, "some categories hold reconstructed work"
    assert all("semantic" in c["name"] for c in reconstructed)


# ---------------------------------------------------------------------------
# 12. duplicate addresses are rejected
# ---------------------------------------------------------------------------
def test_duplicate_function_addresses_are_rejected(inventory: dd.Inventory) -> None:
    broken = dd.build_inventory(dd.load_inputs())
    placed = [u for u in broken.units if u.address is not None]
    clone = copy.deepcopy(placed[1])
    clone.unit_name = "rom/sub_DEADBEEF"
    clone.neutral_name = "sub_DEADBEEF"
    broken.units.append(clone)
    problems = broken.validate()
    assert any("duplicate unit address" in p for p in problems)


# ---------------------------------------------------------------------------
# 13. overlap / inventory corruption is rejected
# ---------------------------------------------------------------------------
def test_overlapping_units_are_rejected(inventory: dd.Inventory) -> None:
    broken = dd.build_inventory(dd.load_inputs())
    placed = sorted(
        (u for u in broken.units if u.address is not None and u.address >= 0x08000000),
        key=lambda u: u.address,
    )
    placed[0].size = placed[1].address - placed[0].address + 4
    problems = broken.validate()
    assert any("overlapping" in p for p in problems)
    assert any("units total" in p for p in problems)


def test_region_bytes_are_conserved(inventory: dd.Inventory) -> None:
    """Every tracked byte belongs to exactly one unit, function or remainder."""
    broken = dd.build_inventory(dd.load_inputs())
    placed = [u for u in broken.units if u.address is not None]
    placed[0].size -= 4
    problems = broken.validate()
    assert any("units total" in p for p in problems)


# ---------------------------------------------------------------------------
# 14. denominator regression protection
# ---------------------------------------------------------------------------
def test_denominator_shrink_is_detected(inventory: dd.Inventory) -> None:
    baseline = {
        "tracked_functions": inventory.tracked_functions,
        "tracked_executable_bytes": inventory.tracked_executable_bytes,
    }
    changes, problems = dd.denominator_changes(inventory, baseline)
    assert changes == [] and problems == []

    shrunk = dict(baseline, tracked_functions=baseline["tracked_functions"] + 1)
    _, problems = dd.denominator_changes(inventory, shrunk)
    assert any("DENOMINATOR SHRANK" in p for p in problems)

    shrunk = dict(baseline, tracked_executable_bytes=baseline["tracked_executable_bytes"] + 4096)
    _, problems = dd.denominator_changes(inventory, shrunk)
    assert any("DENOMINATOR SHRANK" in p for p in problems)


def test_unit_diagnostics_report_both_directions() -> None:
    """Diagnostics compare the committed record against freshly derived reality.

    A unit that reality LOST is the dangerous direction - unresolved work leaving
    the denominator - and must say so; a unit reality GAINED only means the record
    is stale.
    """
    committed = dd.INVENTORY_PATH

    missing = dd.build_inventory(dd.load_inputs())
    dropped = missing.units[0].unit_name
    missing.units = [u for u in missing.units if u.unit_name != dropped]
    problems = dd.compare_inventory(missing, committed)
    assert any(f"unit removed: {dropped}" in p for p in problems)

    extra = dd.build_inventory(dd.load_inputs())
    clone = copy.deepcopy(extra.units[0])
    clone.unit_name = "rom/sub_00000001"
    extra.units = extra.units + [clone]
    problems = dd.compare_inventory(extra, committed)
    assert any("unit added: rom/sub_00000001" in p for p in problems)


def test_lift_report_diagnostics_are_keyed_by_path(inventory: dd.Inventory, tmp_path) -> None:
    """A report list that gained or lost an entry must not be compared one-off.

    Comparing by position made a newly added report report itself as an unchanged
    neighbour ("PROVEN -> PROVEN") while hiding the report that actually moved.
    """
    path = tmp_path / "decompdev_inventory.json"
    document = inventory.as_dict()
    reports = document["inputs"]["lift_reports"]
    dropped, altered = reports[0]["path"], reports[1]["path"]
    reports[1] = dict(reports[1], semantic="PARTIAL")
    document["inputs"]["lift_reports"] = reports[1:]
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8", newline="\n")

    problems = dd.compare_inventory(inventory, path)
    assert any(f"lift report added: {dropped}" in p for p in problems)
    assert any("lift report changed" in p and altered in p for p in problems)
    assert any("'PARTIAL' -> 'PROVEN'" in p for p in problems)


def test_proving_a_function_cannot_move_the_denominator() -> None:
    """Withdrawing credit grows the remainder; it never shrinks the total.

    A function's measured extent is smaller than the bound the inventory gives an
    unproven unit, so removing credit moves bytes from `measured` into
    `upper-bound` and `unattributed` while the tracked total stays put. That is the
    property that stops a ticket from raising its percentage by deleting work.
    """
    inputs = dd.load_inputs()
    before = dd.build_inventory(inputs)
    target = next(r for r in inputs.lift_reports if r.credited)
    credit_removed = sum(f.size for f in target.functions)
    assert credit_removed > 0

    target.semantic = "UNTESTED"
    after = dd.build_inventory(inputs)

    assert after.tracked_executable_bytes == before.tracked_executable_bytes
    assert after.tracked_functions == before.tracked_functions
    assert before.complete_bytes - after.complete_bytes == credit_removed
    assert before.measured_bytes - after.measured_bytes == credit_removed
    assert (
        after.unattributed_bytes + after.upper_bound_bytes
    ) - (before.unattributed_bytes + before.upper_bound_bytes) == credit_removed
    # the three classes still partition the total
    for state in (before, after):
        assert (
            state.measured_bytes + state.upper_bound_bytes + state.unattributed_bytes
            == state.tracked_executable_bytes
        )


# ---------------------------------------------------------------------------
# 15. no canonical ROM is required
# ---------------------------------------------------------------------------
def test_report_generation_never_touches_a_rom(inventory: dd.Inventory, monkeypatch) -> None:
    def forbidden(*args, **kwargs):  # pragma: no cover - must never be called
        raise AssertionError("the progress report must not read a cartridge image")

    monkeypatch.setattr(dd._identity, "resolve_baserom", forbidden)
    monkeypatch.setattr(dd._identity, "verify", forbidden)
    rebuilt = dd.build_inventory(dd.load_inputs())
    assert rebuilt.tracked_executable_bytes == inventory.tracked_executable_bytes
    assert dd.render_report_json(dd.objdiff_report(rebuilt)) == dd.render_report_json(
        dd.objdiff_report(inventory)
    )


def test_the_inventory_records_where_every_number_came_from(inventory: dd.Inventory) -> None:
    document = inventory.as_dict()
    digests = document["inputs"]["digests"]
    assert set(digests) == {"functions.json", "rom_map.json", "lift_targets.json"}
    assert all(len(value) == 40 for value in digests.values())
    assert document["source_sha1"] == "f1c4b07554d2a3b1ad2f325307051e775ce68087"
    for entry in document["inputs"]["lift_reports"]:
        assert len(entry["sha1"]) == 40
        assert entry["semantic"] in ("PROVEN", "PARTIAL", "FAILED", "UNTESTED")


# ---------------------------------------------------------------------------
# 16. no absolute local path
# ---------------------------------------------------------------------------
def test_no_absolute_local_path_is_emitted(inventory: dd.Inventory, report_text: str) -> None:
    assert not dd._contains_absolute_path(report_text)
    assert not re.search(r"[A-Za-z]:[\\/]", report_text)
    assert "\\\\" not in report_text
    problems = dd.proprietary_payload_findings(json.loads(report_text), inventory)
    assert problems == []


def test_an_absolute_source_path_is_rejected(inventory: dd.Inventory, report: dict) -> None:
    broken = copy.deepcopy(report)
    for unit in broken["units"]:
        if unit.get("metadata", {}).get("source_path"):
            unit["metadata"]["source_path"] = "C:/Dev/buusfury-decomp/src/GBARam.c"
            break
    assert dd.proprietary_payload_findings(broken, inventory)


# ---------------------------------------------------------------------------
# 17. no copyrighted bytes
# ---------------------------------------------------------------------------
def test_no_cartridge_content_can_be_emitted(inventory: dd.Inventory, report: dict) -> None:
    assert dd.proprietary_payload_findings(report, inventory) == []

    # There is no field in the objdiff schema that holds bytes, and nothing in
    # our document smuggles one through a string field.
    def keys(payload) -> set:
        found = set()
        if isinstance(payload, dict):
            for key, value in payload.items():
                found.add(key)
                found |= keys(value)
        elif isinstance(payload, list):
            for entry in payload:
                found |= keys(entry)
        return found

    assert not {"bytes", "data", "hex", "blob", "rom_bytes"} & keys(report)

    # A binary-safe encoding carried in a name, and a machine-code-looking
    # constant, are both refused.
    broken = copy.deepcopy(report)
    broken["units"][0]["name"] = "rom/QUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVphYmNkZWZnaGk"
    assert dd.proprietary_payload_findings(broken, inventory)


def test_an_undeclared_category_cannot_appear(inventory: dd.Inventory, report: dict) -> None:
    broken = copy.deepcopy(report)
    broken["categories"].append(
        {"id": "byte_matched", "name": "Byte-matched", "measures": {"total_code": "1"}}
    )
    assert dd.proprietary_payload_findings(broken, inventory)


# ---------------------------------------------------------------------------
# decomp.dev's own ingestion contract
# ---------------------------------------------------------------------------
def test_artifact_name_and_report_shape_match_the_ingestion_contract() -> None:
    # decomp.dev: ^(?P<version>[A-z0-9_.\-]+)[_-]report(?:[_-].*)?$
    pattern = re.compile(r"^(?P<version>[A-z0-9_.\-]+)[_-]report(?:[_-].*)?$")
    match = pattern.match(dd.ARTIFACT_NAME)
    assert match and match.group("version") == dd.VERSION_NAME == "semantic"
    # the archive entry must be a file whose stem is `report`
    assert dd.ARTIFACT_FILE_NAME == "report.json"
    assert dd.ARTIFACT_FILE_NAME.rsplit(".", 1)[0] == "report"


def test_the_report_does_not_claim_to_be_fully_linked(report: dict) -> None:
    """`metadata.complete` drives decomp.dev's separate "fully linked" figure.

    Semantic reconstruction is not linking, so leaving it false keeps the second
    number at zero instead of restating the same claim in different words.
    """
    assert all(u["metadata"]["complete"] is False for u in report["units"])
    assert "complete_code" not in report["measures"]
    assert "complete_units" not in report["measures"]


def test_the_change_line_is_computed_not_typed(report: dict) -> None:
    """The line must be derived from the measures, not from a written-down value.

    Pinning today's percentage here would make the test fail on every legitimate
    progress change and would tempt a future ticket into "fixing" the number
    instead of regenerating it, so the expected text is derived from the report.
    """
    current = report["measures"]["matched_code_percent"]
    assert dd.describe_change(None, report) == (
        f"decomp.dev: semantic code {current:.3f}% (report check PASS)"
    )
    assert dd.describe_change(report["measures"], report) == (
        "decomp.dev: unchanged (report check PASS)"
    )
    previous = dict(report["measures"], matched_code_percent=0.5)
    assert dd.describe_change(previous, report) == (
        f"decomp.dev: semantic code 0.500% -> {current:.3f}% (report check PASS)"
    )


def test_overwriting_the_committed_report_still_reports_the_movement(
    inventory: dd.Inventory, tmp_path
) -> None:
    """`--out <the committed report> --check` must not compare a file with itself.

    This is how a closeout regeneration runs, and it is the one invocation in
    which the movement would otherwise always read as "unchanged".
    """
    path = tmp_path / "decompdev_report.json"
    report = dd.objdiff_report(inventory)
    path.write_text(dd.render_report_json(report), encoding="utf-8", newline="\n")
    current = report["measures"]["matched_code_percent"]

    captured = dict(report["measures"], matched_code_percent=0.9)
    problems, line = dd.check(inventory, report_path=path, previous_measures=captured)
    assert problems == []
    assert line == f"decomp.dev: semantic code 0.900% -> {current:.3f}% (report check PASS)"

    # Without the captured measures the same call can only see the fresh file,
    # which is exactly the blind spot the parameter exists to close.
    _, blind = dd.check(inventory, report_path=path)
    assert blind == "decomp.dev: unchanged (report check PASS)"


def test_the_summary_reports_the_mechanical_denominator(inventory: dd.Inventory) -> None:
    text = "\n".join(inventory.summary_lines())
    assert f"Functions: {inventory.complete_functions} / {inventory.tracked_functions}" in text
    assert f"{inventory.complete_bytes:,} / {inventory.tracked_executable_bytes:,}" in text
    assert "ROM" in text and "IWRAM" in text
    assert "NOT a byte-identical compiler-match percentage" in text
    assert "C:\\" not in text


def test_check_passes_on_the_committed_tree(inventory: dd.Inventory) -> None:
    problems, line = dd.check(inventory)
    assert problems == []
    assert line == "decomp.dev: unchanged (report check PASS)"


def test_the_readme_quotes_the_generated_figures(inventory: dd.Inventory) -> None:
    """Prose is not allowed to drift from the committed config.

    The same discipline `tests/test_regions.py` applies to the coverage tables.
    """
    readme = (dd._identity.REPO_ROOT / "README.md").read_text(encoding="utf-8")
    section = readme.split("### Semantic reconstruction progress", 1)
    assert len(section) == 2, "the README must carry the semantic progress section"
    section = section[1].split("### Build coverage", 1)[0]

    assert f"{inventory.tracked_functions}" in section
    assert f"{inventory.tracked_executable_bytes:,}" in section
    assert (
        f"{inventory.complete_functions} ({_percent(inventory.complete_functions, inventory.tracked_functions)}%)"
        in section
    )
    assert (
        f"{inventory.complete_bytes:,} ({_percent(inventory.complete_bytes, inventory.tracked_executable_bytes)}%)"
        in section
    )
    assert f"{inventory.measured_bytes:,}" in section
    assert f"{inventory.upper_bound_bytes:,}" in section
    assert f"{inventory.unattributed_bytes:,}" in section
    for label, iwram in (("ROM", False), ("runtime-copied IWRAM overlay", True)):
        members = inventory.scoped(iwram=iwram)
        functions = [u for u in members if u.is_function]
        credited = [u for u in functions if u.credited]
        assert f"{len(credited)} / {len(functions)}" in section, label


def _percent(part: int, whole: int) -> str:
    return f"{dd._pct(part, whole, 3):.3f}"
