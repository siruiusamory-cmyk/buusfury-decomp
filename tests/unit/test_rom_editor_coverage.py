"""The ROM-editor coverage research artifacts stay self-consistent.

These are research-artifact checks, not product tests: the subject is the census
JSON zero and the three documents rendered from it.
"""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from tools.research import rom_editor_coverage_render as render

ROOT = Path(__file__).resolve().parents[2]
JSON_PATH = ROOT / "docs" / "research" / "rom_editor_coverage.json"
CAPABILITIES = ROOT / "src" / "data" / "capabilities.json"
GAMES = ("buus_fury", "logii", "log1")


def load() -> dict:
    with io.open(JSON_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def test_every_row_has_a_unique_id_and_a_known_area():
    doc = load()
    ids = [r["id"] for r in doc["rows"]]
    assert len(ids) == len(set(ids)), "duplicate census id"
    assert doc["denominator"]["accepted_rows"] == len(ids)
    areas = {"MAP/WORLD", "ENTITIES/GAMEPLAY", "SCRIPT/TEXT", "GRAPHICS", "AUDIO", "SYSTEM/ROM"}
    for row in doc["rows"]:
        assert row["area"] in areas, row["id"]
        assert set(row["games"]) == set(GAMES), row["id"]
        for key in ("description", "evidence_authority", "read", "edit", "author", "xref",
                    "raw_range", "validation_rebuild", "ui", "restrictions", "external_tool"):
            assert row[key].strip(), (row["id"], key)
        assert row["open_questions"] and row["evidence_refs"], row["id"]


def test_every_cell_uses_one_of_the_approved_words():
    doc = load()
    vocab = doc["vocabularies"]
    for row in doc["rows"]:
        for game in GAMES:
            cell = row["games"][game]
            assert cell["state"] in vocab["coverage_states"], (row["id"], game, cell["state"])
            assert cell["basis"] in vocab["basis"], (row["id"], game)
            assert cell["engine_knowledge"] in vocab["engine_knowledge"], (row["id"], game)
            assert cell["runtime_evidence"] in vocab["runtime_evidence"], (row["id"], game)
            assert cell["confidence"] in vocab["confidence"], (row["id"], game)
            if cell["state"] == "UNKNOWN_UNMAPPED" and cell["basis"] == "NOT_INVESTIGATED":
                assert cell["engine_knowledge"] == "UNKNOWN", (row["id"], game)


def test_published_counts_equal_the_counts_recomputed_from_the_rows():
    doc = load()
    states = doc["vocabularies"]["coverage_states"]
    totals = doc["totals"]

    by_game = {g: {s: 0 for s in states} for g in GAMES}
    by_area: dict[str, dict[str, int]] = {}
    ek = {g: {k: 0 for k in doc["vocabularies"]["engine_knowledge"]} for g in GAMES}
    for row in doc["rows"]:
        slot = by_area.setdefault(row["area"], {"rows": 0, **{s: 0 for s in states if s != "N_A"}})
        slot["rows"] += 1
        for game in GAMES:
            cell = row["games"][game]
            by_game[game][cell["state"]] += 1
            ek[game][cell["engine_knowledge"]] += 1
            if cell["state"] != "N_A":
                slot[cell["state"]] += 1

    for game in GAMES:
        published = totals["by_game"][game]
        assert published["measured_cells"] == sum(by_game[game][s] for s in states if s != "N_A")
        for state in states:
            assert published[state] == by_game[game][state], (game, state)
        assert totals["engine_knowledge_by_game"][game] == ek[game], game

    family = {s: sum(by_game[g][s] for g in GAMES) for s in states}
    published = totals["family_wide"]
    for state in states:
        assert published[state] == family[state], state
    measured = sum(family[s] for s in states if s != "N_A")
    writable = family["FULLY_EDITABLE"] + family["PARTIALLY_EDITABLE"]
    assert published["measured_cells"] == measured
    assert published["writable_cells"] == writable
    assert published["writable_pct_of_measured"] == round(100.0 * writable / measured, 2)
    assert totals["by_area_buus_fury"] == {a: by_area[a] for a in sorted(by_area)}


def test_the_rom_surface_classes_account_for_the_whole_image():
    doc = load()
    surface = doc["rom_surface"]
    assert sum(c["bytes"] for c in surface["classes"]) == surface["total_bytes"] == surface["rom_size"]
    assert surface["rom_size"] == 8388608
    for c in surface["classes"]:
        assert c["decided_by"].strip() and c["note"].strip()


def test_the_fixed_capability_registry_is_not_touched_by_this_census():
    with io.open(CAPABILITIES, encoding="utf-8") as fh:
        registry = json.load(fh)
    assert registry["track"]["capabilityTotal"] == 24
    assert len(registry["capabilities"]) == 24
    assert {c["state"] for c in registry["capabilities"]} == {"shipped"}
    assert {c["family"] for c in registry["capabilities"]} == {"see", "edit", "author", "deliver"}


def test_every_census_row_appears_in_both_documents():
    doc = load()
    ledger = io.open(render.LEDGER, encoding="utf-8").read()
    census = io.open(render.CENSUS, encoding="utf-8").read()
    for row in doc["rows"]:
        token = "`{}`".format(row["id"])
        assert token in ledger, ("missing from ledger", row["id"])
        assert token in census, ("missing from census", row["id"])


@pytest.mark.parametrize("path,builder", [
    ("ROM_EDITOR_SYSTEM_CENSUS.md", "census"),
    ("ROM_EDITOR_COVERAGE_LEDGER.md", "ledger"),
    ("ROM_EDITOR_COVERAGE_SUMMARY.md", "summary"),
])
def test_each_document_is_exactly_what_the_renderer_produces(path, builder):
    expected = getattr(render, builder)(load())
    actual = io.open(ROOT / "docs" / "research" / path, encoding="utf-8", newline="").read()
    assert actual == expected, "{} has drifted from rom_editor_coverage.json".format(path)
