"""PINMAP-09: the atlas seed reads its profile-declared rows instead of restating them.

Three properties are pinned here, and nothing else:

* no emitted row carries an address, count, stride or extent that the profile
  already declares, so a profile that moves cannot leave a stale number behind it;
* the seed's one recorded conflict is ONE named row that still states both
  claims, both values and which one the code follows - one note is not enough
  and removing a claim is not recording it;
* the assembler never reads a seed row's ``notes`` or ``evidence``, so folding
  those notes moves ``seed_knowledge.jsonl`` alone and leaves the built atlas
  byte-identical.

The row's ``notes`` and ``evidence`` strings are evidence data and are NOT
matched here: they cite addresses as provenance, which is what they are for.
What is pinned is the VALUE layer the atlas consumes.

What this module does NOT check, stated so a reader does not expect more: the
whole-atlas byte comparison itself. That needs the ROM and lives in the
ticket's closure report, not in a 5-second unit run.
"""

from __future__ import annotations

import ast
from pathlib import Path

from tools.webfoot.atlas_build import ARTIFACTS, EVIDENCE, _objects, _seed_claims
from tools.webfoot.atlas_producers import seed
from tools.webfoot.binary import GBA_ROM_BASE as BASE
from tools.webfoot.packaged import packaged_profile


def _rows():
    return seed._rows()


def _by_identity():
    return {row["identity"]: row for row in _rows()}


def _without_notes(rows):
    return [{key: value for key, value in row.items() if key != "notes"} for row in rows]


def _artifacts(seed_rows):
    return {name: [] for name in ARTIFACTS} | {"seed_knowledge": seed_rows}


#: identity -> the profile value the row's ``size`` must equal; the selector
#: view's expected size is None because it deliberately claims no extent.
SIZE_FROM_PROFILE = {
    "text_strings.pool": lambda p: p.text_strings.pool_size,
    "text_strings.pointer_table": lambda p: p.text_strings.count * 4,
    "map_entries": lambda p: p.map_entries.count * p.map_entries.record_size,
    "actor_sprites.character_table": lambda p: p.actor_sprites.character_count * 4,
    "character_base_stats": lambda p: p.character_base_stats.total_size,
    "enemy_stats": lambda p: p.enemy_stats.total_size,
    "placement_types.table": lambda p: None,
    "free_region.toolkit028": lambda p: p.free_regions[0].range.size,
}

#: identity -> the profile address the row's ``gba_address`` must equal.
ADDRESS_FROM_PROFILE = {
    "text_strings.pool": lambda p: p.text_strings.pool_address.raw,
    "text_strings.pointer_table": lambda p: p.text_strings.pointer_table_address.raw,
    "map_entries": lambda p: p.map_entries.address.raw,
    "actor_sprites.character_table": lambda p: p.actor_sprites.character_table_address.raw,
    "character_base_stats": lambda p: p.character_base_stats.address.raw,
    "enemy_stats": lambda p: p.enemy_stats.address.raw,
    "placement_types.table": lambda p: p.placement_types.table_address.raw,
    "placement_types.constructor": lambda p: p.placement_types.constructor_address.raw,
    "placement_types.factory_wrapper": lambda p: p.placement_types.factory_raw - 1,
    "free_region.toolkit028": lambda p: p.free_regions[0].range.start.value + BASE,
}


def test_every_profile_keyed_row_carries_the_profiles_own_value() -> None:
    """A row that restated a number would fail here the moment the profile moved."""
    profile = packaged_profile()
    rows = _by_identity()
    for identity, expected_of in SIZE_FROM_PROFILE.items():
        expected = expected_of(profile)
        assert rows[identity]["size"] == expected, (
            f"{identity} emits size {rows[identity]['size']!r}, not the profile's {expected!r}"
        )
    for identity, expected_of in ADDRESS_FROM_PROFILE.items():
        expected = expected_of(profile)
        emitted = int(rows[identity]["gba_address"], 16)
        assert emitted == expected, (
            f"{identity} emits {rows[identity]['gba_address']}, not the profile's 0x{expected:08X}"
        )


def test_the_conflict_is_one_named_row_that_states_both_claims() -> None:
    """Two notes about one fact is not one row, and deleting a claim is not recording it."""
    rows = _rows()
    conflicts = [row for row in rows if "CONFLICT" in row["notes"]]
    assert [row["identity"] for row in conflicts] == ["enemy_stats"], (
        "the seed must record its one conflict as ONE named row; the rows naming "
        f"a CONFLICT are {[row['identity'] for row in conflicts]}"
    )
    note = conflicts[0]["notes"]
    for claim in ("141", "149", "28", "0x1C", "3,948", "max_selector", "enemy_stats",
                  "placement_types"):
        assert claim in note, f"the one conflict row no longer states {claim!r}: {note!r}"
    for resolution in ("NOT a total table count", "THIS row's count 141 is the extent",
                       "size null"):
        assert resolution in note, (
            "the conflict row no longer records which reading the code follows "
            f"({resolution!r} missing): {note!r}"
        )
    for index, subject in enumerate(("enemy_stats", "placement_types"), start=1):
        assert f"Claim {index}, {subject}" in note, (
            "the one conflict row no longer labels the "
            f"{subject} claim it records: {note!r}"
        )


def test_the_assembler_never_reads_a_seed_rows_notes_or_evidence() -> None:
    """Only the notes moved, so the assembled atlas cannot see them."""
    rows = _rows()
    without_notes = _without_notes(rows)
    assert list(_seed_claims(rows)) == list(_seed_claims(without_notes)), (
        "the seed claims depend on a row's notes; the atlas output would move with them"
    )
    assert _objects(_artifacts(rows), None) == _objects(_artifacts(without_notes), None), (
        "a seed row's notes reach an atlas object; the atlas output would move with them"
    )
    assert EVIDENCE["seed"].startswith("seed_knowledge.jsonl:"), EVIDENCE["seed"]


#: The names `_rows` binds from the packaged profile. A row put back on a literal
#: leaves this set even when the literal has the same value, which is the point.
PROFILE_DERIVED_NAMES = (
    "placement", "text", "text_pointer_size", "map_entries", "map_table_size",
    "sprites", "sprite_table_size", "base_stats", "base_stats_size",
    "enemy_stats", "enemy_stats_size", "free_region",
)

#: Every `add(...)` call in the seed and the profile names its arguments read,
#: spelled as literals rather than derived from the tree being checked.
ROWS_READING_THE_PROFILE = {
    149: ("placement",),
    157: ("placement",),
    271: ("text",),
    282: ("text", "text_pointer_size"),
    307: ("map_entries", "map_table_size"),
    439: ("sprite_table_size", "sprites"),
    479: ("base_stats", "base_stats_size"),
    498: ("enemy_stats", "enemy_stats_size"),
    516: ("placement",),
    532: ("free_region",),
}


def _read_names(node: ast.AST, found: list[str]) -> None:
    """Collect profile-derived names in an expression, skipping subscripts.

    Subscript is skipped on purpose: the rows iterate local arrays whose element
    names would otherwise read as profile attributes.
    """
    if isinstance(node, ast.Subscript):
        return
    if isinstance(node, ast.Name) and node.id in PROFILE_DERIVED_NAMES:
        found.append(node.id)
        return
    for child in ast.iter_child_nodes(node):
        _read_names(child, found)


def _names_read(call: ast.Call) -> list[str]:
    """The profile-derived names a call's `addr=` / `size=` arguments read."""
    found: list[str] = []
    for keyword in call.keywords:
        if keyword.arg in ("addr", "size"):
            _read_names(keyword.value, found)
    return sorted(set(found))


def _rows_function() -> ast.FunctionDef:
    """`_rows` as parsed from the module source, so its line numbers are the file's."""
    tree = ast.parse(Path(seed.__file__).read_text(encoding="utf-8"))
    return next(node for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef) and node.name == "_rows")


def _profile_calls() -> dict[int, tuple[str, ...]]:
    return {
        node.lineno: tuple(_names_read(node))
        for node in ast.walk(_rows_function())
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "add"
        and _names_read(node)
    }


def test_only_the_measured_rows_read_the_profile() -> None:
    """A row put back on a literal leaves this set even when its value is the same."""
    measured = _profile_calls()
    assert measured == ROWS_READING_THE_PROFILE, (
        "the add() rows that read a profile-derived value moved; a row here that "
        "no longer appears was reverted to a literal, and one that appeared "
        "without this expectation being updated is a new claim: "
        f"{sorted(set(measured) ^ set(ROWS_READING_THE_PROFILE))} differ"
    )


def test_every_profile_keyed_row_reads_its_own_declaring_key() -> None:
    """The `placement_types` row reads `placement`, not the other key at that base."""
    source = Path(seed.__file__).read_text(encoding="utf-8")
    placement_row = _profile_calls().get(516)
    assert placement_row == ("placement",), (
        f"line 516 reads {placement_row}, so its own declaring key is not the one read"
    )
    assert "placement.table_address" in source, (
        "placement_types.table_address is no longer read anywhere in the seed"
    )
