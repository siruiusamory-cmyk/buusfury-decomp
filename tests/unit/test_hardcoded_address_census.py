"""Hard-coded address census guard: the surface is measured and it cannot grow.

Every node here re-measures the tracked tree through
``tests.unit.address_literal_census``; nothing is read from a stored result, so
a pinned number that stops being true fails with the file and the count that
moved.

The guard covers:

* the whole tracked ``tools/`` tree, as the ``HEX5`` token census, both as it
  measures today and as the single line by which it differs from
  ``INVENTORY.md`` section 4's published pair;
* what an address looks like when you write it: an uppercase prefix and a digit
  separator are counted, a Java suffix does not break the count, and an
  identifier that merely ends in something hex-shaped is not a literal;
* the enforcement set (that tree minus the four instrument directories) for
  conventional hex, complete ROM-space hex, and decimal ROM-range literals. The
  decimal unit is the one a hex-only guard cannot see, and it is 404 lines in a
  single file;
* one row per enforced file that carries a ROM-space or decimal literal, with
  three counts and a reason written for that file.

The guard does NOT cover, and no node here should be read as covering:

* a swap of one address for another at constant count. A row pins counts, so it
  catches growth, shrinkage and a file that stops carrying literals; the
  ``ponytail:`` note in the census module names the digest upgrade that would
  catch a swap;
* anything outside ``tools/``. A ROM-space literal in a test, a document or a
  site file is not counted, and this guard does not certify it;
* the four instrument directories, which the migration order keeps out of scope
  on purpose;
* the disk. The set is ``git ls-files``, so a path that exists only on disk is
  invisible: the guard governs the committed tree and never fires on a bytecode
  cache, an editor backup or generated output;
* ``0o`` and ``0b`` spellings, and any other exotic form of the same integer.
  The token patterns are hexadecimal and decimal, and no such spelling is in the
  tracked tree today.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import tests.unit.address_literal_census as census
from tools.quality.architecture import REPOSITORY_ROOT, tracked_files

ROOT = Path(__file__).resolve().parents[2]


def test_a_run_that_reads_no_path_fails_closed() -> None:
    """A census of nothing is an error, never a count of zero lines."""
    with pytest.raises(census.CensusError):
        census.scan([])


def test_a_file_that_cannot_be_read_fails_closed_with_its_path() -> None:
    with pytest.raises(census.CensusError, match="tools/webfoot/absent_from_the_tree.py"):
        census.scan(["tools/webfoot/absent_from_the_tree.py"])


def test_the_census_set_is_the_tracked_index_and_not_the_disk() -> None:
    """The set is ``git ls-files``, so a path that exists only on disk is invisible.

    That is the point of the guard: it governs committed state. The set is
    therefore proved equal to the index slice, and a path found on disk but not
    in the index is proved absent from the measurement. Nothing in the scan
    walks the disk, which is what keeps the guard from firing on a bytecode
    cache, an editor backup or generated output.
    """
    every_tracked = set(tracked_files())
    measured = set(census.census_paths())
    assert every_tracked, "the index listed no file at all; the scan cannot run"
    assert measured, "the index listed no file under tools/; the scan cannot run"
    assert measured == {path for path in every_tracked if path.startswith("tools/")}

    on_disk = {
        item.relative_to(REPOSITORY_ROOT).as_posix()
        for item in (ROOT / "tools").rglob("*")
        if item.is_file()
    }
    untracked_on_disk = sorted(on_disk - every_tracked)
    leaked = sorted(set(untracked_on_disk) & measured)
    assert not leaked, (
        f"the scan measured {len(leaked)} path(s) that are not in the index: {leaked}"
    )


def test_the_tools_hex5_census_matches_the_widened_measurement() -> None:
    measured = census.totals(census.scan(census.census_paths()))[0]
    pinned = census.CENSUS_HEX5
    assert measured == pinned, (
        f"HEX5 census: {measured[0]} lines / {measured[1]} files, pinned "
        f"{pinned[0]} lines / {pinned[1]} files"
    )


def test_the_widened_census_is_the_publication_plus_every_declared_move() -> None:
    """The publication is quoted, and each ticket's move of it is declared.

    Section 4 stays quoted as published. A ticket that moves the measured pair adds a
    ledger entry naming every ``path:line`` that left or arrived, so the tree pair is
    the publication plus the declared moves and nothing else. An undeclared move fails
    here by value, with every entry printed, instead of being absorbed into a rewritten
    quotation - which is what would make the published number false.
    """
    measured = census.totals(census.scan(census.census_paths()))[0]
    published = census.CENSUS_INVENTORY_S4
    expected = census.expected_census_hex5()
    assert measured == census.CENSUS_HEX5, (
        f"HEX5 census: {measured[0]} lines / {measured[1]} files, pinned "
        f"{census.CENSUS_HEX5[0]} lines / {census.CENSUS_HEX5[1]} files"
    )
    entries = "\n".join(
        f"  {entry.ticket}: {entry.lines:+d} lines / {entry.files:+d} files, "
        f"naming {', '.join(entry.named)}: {entry.reason}"
        for entry in census.RECONCILIATION_LEDGER
    )
    difference = (measured[0] - published[0], measured[1] - published[1])
    assert measured == expected, (
        f"the census moved {difference} against INVENTORY.md section 4's published "
        f"{published[0]} lines / {published[1]} files; the declared ledger expects "
        f"{expected[0]} lines / {expected[1]} files and the tree measures "
        f"{measured[0]} lines / {measured[1]} files. Every declared entry:\n{entries}"
    )


def test_every_ledger_entry_names_a_tracked_line_and_declares_a_reason() -> None:
    """A ``path:line`` typo cannot sit in the ledger, and every entry says why.

    The ledger is the evidence a reader re-measures, so its pointers are checked against
    the index the scan itself uses rather than trusted, and the line number has to be a
    real line of that file. An entry that names nothing, or names a path or a line that
    does not exist, fails here by name.
    """
    tracked = set(tracked_files())
    for entry in census.RECONCILIATION_LEDGER:
        assert entry.ticket.strip(), entry
        assert entry.reason.strip(), entry.ticket
        assert entry.named, f"{entry.ticket} declares a move and names no line"
        for named in entry.named:
            path, _, number = named.rpartition(":")
            assert path in tracked, f"{entry.ticket} names {named}, which is not tracked"
            assert number.isdigit(), f"{entry.ticket} names {named} without a line number"
            lines = (REPOSITORY_ROOT / path).read_text(encoding="utf-8").splitlines()
            assert 0 < int(number) <= len(lines), (
                f"{entry.ticket} names {named}, but that file holds {len(lines)} lines"
            )


def test_the_uppercase_prefix_and_the_digit_separator_are_both_counted(
    tmp_path: Path,
) -> None:
    """Two spellings of the same integer used to evade every unit.

    Driven through ``scan`` and not through a pattern, so what is tested is the
    file-reading path. ``scan`` joins a path onto the repository root, and an
    absolute operand passes that join unchanged, which is what lets the probe
    live in the temporary directory.
    """
    probe = tmp_path / "hex_spellings.py"
    probe.write_text("A = 0X0879B704\nA = 0x0879_B704\n", encoding="utf-8")
    measured = census.scan([str(probe)])
    assert measured == {str(probe): (2, 2, 0)}, (
        f"both lines must count in hex5 and in rom_hex, measured {measured}"
    )


def test_an_identifier_that_ends_in_something_hex_shaped_is_not_a_literal(
    tmp_path: Path,
) -> None:
    probe = tmp_path / "identifier.py"
    probe.write_text('    "byte_at_0x10_census": {\n', encoding="utf-8")
    measured = census.scan([str(probe)])
    assert measured == {}, f"a name is not a literal; measured {measured}"


def test_the_historical_coverage_survives_the_widened_token(tmp_path: Path) -> None:
    probe = tmp_path / "suffixes.py"
    probe.write_text("A = 0x080126D4L\nA = 0x1_234\n", encoding="utf-8")
    measured = census.scan([str(probe)])
    assert measured == {str(probe): (1, 1, 0)}, (
        f"a Java L suffix must not stop the count, and four digits are not five: "
        f"{measured}"
    )


def test_the_enforcement_set_totals_match_the_pinned_counts() -> None:
    hex5, rom_hex, decimal = census.totals(census.scan(census.enforcement_paths()))
    for measured, pinned, unit in (
        (hex5, census.ENFORCEMENT_HEX5, "HEX5"),
        (rom_hex, census.ENFORCEMENT_ROM_HEX, "ROM-space hex"),
        (decimal, census.ENFORCEMENT_DECIMAL, "decimal ROM-range"),
    ):
        assert measured == pinned, (
            f"{unit}: {measured[0]} lines / {measured[1]} files, pinned "
            f"{pinned[0]} lines / {pinned[1]} files"
        )


def test_the_instrument_exclusion_is_four_named_directories_each_with_a_reason() -> None:
    assert len(census.INSTRUMENT_DIRECTORIES) == 4, (
        "the exclusion list no longer names four directories; a fifth exclusion "
        "is a scan-set change and must be stated as one"
    )
    tracked = set(census.census_paths())
    for directory, reason in census.INSTRUMENT_DIRECTORIES:
        assert reason.strip(), f"{directory}: excluded from the scan with no reason"
        assert any(path.startswith(directory) for path in tracked), (
            f"{directory}: named as an instrument directory but holds no tracked file"
        )
    excluded = tuple(directory for directory, _ in census.INSTRUMENT_DIRECTORIES)
    assert census.enforcement_paths() == sorted(
        path for path in census.census_paths() if not path.startswith(excluded)
    )
    assert census.enforcement_paths(), (
        "the enforcement set is empty; every literal would go unguarded"
    )


def test_the_exemption_table_is_exactly_the_files_that_carry_a_literal() -> None:
    per_file = census.scan(census.enforcement_paths())
    measured = set(census.carrying_paths(per_file))
    rows = [row.path for row in census.EXEMPTIONS]
    assert len(rows) == len(set(rows)), "the exemption table names a path twice"
    assert rows == sorted(rows), "the exemption table is not in path order"

    unrowed = sorted(measured - set(rows))
    assert not unrowed, (
        f"{len(unrowed)} enforced file(s) carry a ROM-space or decimal literal with "
        f"no exemption row: {unrowed}"
    )
    stale = sorted(set(rows) - measured)
    assert not stale, (
        f"{len(stale)} exemption row(s) name a file that carries no ROM-space or "
        f"decimal literal now: {stale}"
    )

    not_tracked = sorted(set(rows) - set(tracked_files()))
    assert not not_tracked, (
        f"exemption row(s) name a file that is not tracked: {not_tracked}"
    )
    without_reason = sorted(
        row.path for row in census.EXEMPTIONS if not row.reason.strip()
    )
    assert not without_reason, (
        f"exemption row(s) carry no reason: {without_reason}"
    )
    excluded = tuple(directory for directory, _ in census.INSTRUMENT_DIRECTORIES)
    instrument_rows = sorted(path for path in rows if path.startswith(excluded))
    assert not instrument_rows, (
        f"exemption row(s) name an excluded instrument directory: {instrument_rows}"
    )


def test_every_exemption_row_count_matches_the_measurement_exactly() -> None:
    per_file = census.scan(census.enforcement_paths())
    moved: list[str] = []
    for row in census.EXEMPTIONS:
        measured = per_file.get(row.path)
        if measured is None:
            continue  # a stale row, reported by name by the structural node
        for unit, pinned, actual in (
            ("hex5", row.hex5, measured[0]),
            ("rom_hex", row.rom_hex, measured[1]),
            ("decimal", row.decimal, measured[2]),
        ):
            if actual != pinned:
                direction = "grew" if actual > pinned else "shrank"
                moved.append(
                    f"{row.path}: {unit} {actual} measured against {pinned} pinned "
                    f"({direction})"
                )
    assert not moved, "exemption counts moved:\n" + "\n".join(moved)
