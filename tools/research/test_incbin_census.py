import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))

import incbin_census  # noqa: E402


def test_rows_sum_to_the_gate_incbin_total():
    text, rows, total, _ = incbin_census.render()
    assert sum(size for _, size, _, _, _ in rows) == total
    assert incbin_census.gate.incbin_ranges() and total > 0
    assert "| census bytes | **%d B** |" % total in text


def test_every_byte_has_one_status():
    _, rows, total, _ = incbin_census.render()
    assert len(rows) == len(incbin_census.gate.incbin_ranges())
    for start, size, status, name, _ in rows:
        assert size > 0 and status in incbin_census.STATUSES and name
        assert start + size <= 0x800000


def test_the_three_classes_account_for_every_byte():
    text, rows, total, _ = incbin_census.render()
    cited = sum(size for _, size, status, _, _ in rows if status == "raw-labeled")
    unreferenced = sum(size for _, size, status, _, _ in rows if status == "unreferenced")
    assert cited + unreferenced == total
    raw, gate_cited, runtime, gate_unreferenced = incbin_census.gate.raw_classes()
    assert raw == total
    assert gate_cited + runtime + gate_unreferenced == raw
    assert "| **accounted** | **%d** | **100.0000 %%** |" % incbin_census.gate.ROM_SIZE in text
    assert "| source - built from tracked source or a byte-exact generator | %d |" \
        % (incbin_census.gate.ROM_SIZE - total) in text


def test_the_recon_reconciliation_sums_to_the_ticket_numbers():
    rows = incbin_census.recon_reconciliation()
    assert sum(union for _, union, _, _, _, _ in rows) == 110733
    assert sum(total for _, _, total, _, _, _ in rows) == 110892


def test_the_text_is_a_pure_function_of_the_tree():
    first = incbin_census.render()[0]
    second = incbin_census.render()[0]
    assert hashlib.sha256(first.encode()).hexdigest() == hashlib.sha256(second.encode()).hexdigest()


def test_the_promoted_families_are_not_still_incbin():
    mask = incbin_census.inbin_mask(incbin_census.gate.incbin_ranges())
    band = next(region.ranges for region in incbin_census.REGIONS
                if region.name == "first-MiB code band")
    for family, ticket, extents in incbin_census.promoted_families():
        for offset, length in extents:
            if any(low <= offset and offset + length <= high for low, high in band):
                continue
            assert not any(mask[offset:offset + length]), (family, ticket, hex(offset))


def test_the_raw_labeled_runs_are_carried_as_cited_slices():
    import rawlabeled

    _, rows, _, _ = incbin_census.render()
    mask = incbin_census.inbin_mask(incbin_census.gate.incbin_ranges())
    for run in rawlabeled.RUNS:
        assert all(mask[run.start:run.end]), hex(run.start)
        cited = sum(size for start, size, status, _, _ in rows
                    if status == "raw-labeled" and start < run.end and start + size > run.start)
        assert cited == run.end - run.start, hex(run.start)
        assert incbin_census.raw_labeled_rows(incbin_census.read_rom())
