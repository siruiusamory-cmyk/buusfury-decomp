from __future__ import annotations

import ast
from dataclasses import replace
from pathlib import Path

import pytest

from tools.webfoot import registry
from tools.webfoot.capability import Capability

REPO_ROOT = Path(__file__).resolve().parents[2]
GRAPHICS_PIECE = "tools/webfoot/graphics.py"


def defined_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }


def unresolved(locator: str) -> str | None:
    path, separator, node = locator.partition("::")
    target = REPO_ROOT / path
    if not target.is_file():
        return f"missing file {path}"
    if not separator or node not in defined_names(target):
        return f"{node or path} is not defined in {path}"
    return None


def formats_imported_by_graphics_piece() -> set[str]:
    tree = ast.parse((REPO_ROOT / GRAPHICS_PIECE).read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level == 1 and node.module == "formats":
            names.update(alias.name for alias in node.names)
    return names


def formats_modules(entries: tuple[registry.Converter, ...]) -> set[str]:
    return {
        callable_.__module__.rsplit(".", 1)[-1]
        for entry in entries
        for callable_ in (entry.decode, entry.encode)
        if callable_ is not None
    }


def test_the_registry_indexes_every_entry_once_by_id():
    assert len(registry.CONVERTERS) == 16
    assert len(registry.CONVERTER_BY_ID) == len(registry.CONVERTERS)
    for entry in registry.CONVERTERS:
        assert registry.converter(entry.id) is entry
        assert entry.family
        assert isinstance(entry.round_trip, registry.RoundTrip)


def test_a_duplicate_id_is_rejected_at_index_time():
    entry = registry.CONVERTERS[0]
    with pytest.raises(registry.RegistryError) as error:
        registry.index_converters((entry, entry))
    assert entry.id in str(error.value)


def test_a_byte_exact_entry_without_an_evidence_locator_is_rejected():
    broken = replace(
        registry.CONVERTERS[0], round_trip=registry.RoundTrip.BYTE_EXACT, evidence="  "
    )
    with pytest.raises(registry.RegistryError) as error:
        registry.index_converters((broken,))
    assert broken.id in str(error.value)


def test_every_entry_evidence_locator_resolves_in_the_working_tree():
    broken = [entry.id for entry in registry.CONVERTERS if unresolved(entry.evidence)]
    assert broken == []


def test_every_byte_exact_row_carries_a_locator_that_resolves():
    exact = [
        entry for entry in registry.CONVERTERS if entry.round_trip is registry.RoundTrip.BYTE_EXACT
    ]
    assert exact
    assert [entry.id for entry in exact if unresolved(entry.evidence)] == []


def test_an_unknown_id_fails_closed_and_names_the_known_ids():
    with pytest.raises(registry.RegistryError) as error:
        registry.converter("no-such-format")
    message = str(error.value)
    assert "no-such-format" in message
    assert "script-vm" in message


def test_the_actor_sprite_entries_are_exactly_the_formats_the_graphics_piece_calls():
    entries = registry.converter_for(Capability.ACTOR_SPRITES)
    assert formats_modules(entries) == formats_imported_by_graphics_piece()
    assert formats_imported_by_graphics_piece() == {"indexed_png", "sprite_graphics", "webfoot_lz"}


def test_converter_for_returns_every_entry_that_carries_the_capability():
    assert {entry.id for entry in registry.converter_for(Capability.SCRIPTS)} == {
        "placement-links",
        "script-vm",
        "webfoot-lz",
    }
    assert registry.converter_for(Capability.APPEARANCES) == ()


def test_the_round_trip_report_states_the_status_of_every_entry():
    rows = registry.round_trip_report()
    assert [row.id for row in rows] == [entry.id for entry in registry.CONVERTERS]
    counts: dict[str, int] = {}
    for row in rows:
        counts[row.round_trip] = counts.get(row.round_trip, 0) + 1
    assert counts == {
        "byte_exact": 9,
        "self_consistent": 4,
        "decode_only": 2,
        "unproven": 1,
    }
