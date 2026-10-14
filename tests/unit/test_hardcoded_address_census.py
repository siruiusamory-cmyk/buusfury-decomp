"""Hard-coded address census guard: the surface is measured and it cannot grow.

Every node here re-measures the tracked tree through
``tests.unit.address_literal_census``; nothing is read from a stored result, so
a pinned number that stops being true fails with the file and the count that
moved.

The guard covers:

* the whole tracked ``tools/`` tree, as the ``HEX5`` census whose parent pair
  ``INVENTORY.md`` section 4 reports;
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
  cache, an editor backup or generated output.
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


def test_the_tools_hex5_census_reproduces_the_inventory_parent_pair() -> None:
    measured = census.totals(census.scan(census.census_paths()))[0]
    pinned = census.CENSUS_INVENTORY_S4
    assert measured == pinned, (
        f"HEX5 census: {measured[0]} lines / {measured[1]} files, pinned "
        f"{pinned[0]} lines / {pinned[1]} files"
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
