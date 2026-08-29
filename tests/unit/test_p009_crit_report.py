from __future__ import annotations

import io

from tools.runtime.mgba_capture import CAPTURE_MAGIC, write_capture_record
from tools.runtime.p009_crit_report import (
    RECORD_DAMAGE,
    RECORD_SPECIAL_FLAG,
    build_rows,
    displayed,
    load_dumps,
    summarize,
)


def test_displayed_matches_the_rounding_in_the_number_refresh_path():
    """The display path at 0x0800AB9A adds 1023 then arithmetic-shifts by 10,
    which is a ceiling divide, not a truncating one."""
    assert displayed(0) == 0
    assert displayed(1) == 1
    assert displayed(1024) == 1
    assert displayed(1025) == 2


def test_displayed_reproduces_the_p006b_runtime_capture():
    """P-006B captured a single punch as raw 51338 against raw HP 141884.
    Those must read as ordinary gameplay numbers, not five-figure ones."""
    assert displayed(51338) == 51
    assert displayed(141884) == 139


def test_p008_damage_band_lands_in_the_expected_gameplay_range():
    """Every P-008 non-outlier hit should convert into the high forties or
    low fifties, which is what a wolf dying in about three hits requires."""
    for raw in (47956, 49476, 49884, 50358, 51018, 51148, 51528, 52440):
        assert 47 <= displayed(raw) <= 52


def _record(flag: int, damage: int) -> bytes:
    blob = bytearray(0x40)
    blob[RECORD_SPECIAL_FLAG : RECORD_SPECIAL_FLAG + 4] = flag.to_bytes(4, "little")
    blob[RECORD_DAMAGE : RECORD_DAMAGE + 4] = damage.to_bytes(4, "little")
    return bytes(blob)


def _write_run(tmp_path, rows):
    events = tmp_path / "events.csv"
    lines = ["stop,gameplay_tick,lr"]
    stream = io.BytesIO()
    stream.write(CAPTURE_MAGIC)
    for index, (lr, flag, damage) in enumerate(rows, start=1):
        lines.append(f"{index},{100 + index},{lr}")
        write_capture_record(stream, index, 0x03007D44, _record(flag, damage))
    events.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (tmp_path / "dumps.wfcap").write_bytes(stream.getvalue())
    return tmp_path


def test_build_rows_decodes_the_flag_and_damage_from_the_record_dump(tmp_path):
    run = _write_run(tmp_path, [("0x0800FA78", 0, 51338), ("0x0800FA78", 1, 102676)])
    rows = build_rows(run)

    assert [row["flag"] for row in rows] == [0, 1]
    assert [row["damage_raw"] for row in rows] == [51338, 102676]
    assert [row["damage_shown"] for row in rows] == [51, 101]


def test_summary_reports_the_ratio_between_flagged_and_plain_hits(tmp_path):
    run = _write_run(tmp_path, [("0x0800FA78", 0, 50000), ("0x0800FA78", 1, 100000)])
    text = "\n".join(summarize(build_rows(run)))

    assert "ratio 2.000" in text
    assert "0x0800FA78  x2" in text


def test_summary_refuses_to_conclude_when_no_flagged_hit_was_seen(tmp_path):
    """A run with no flag=1 event must not be reported as evidence about the
    flag's meaning; silence is the honest result."""
    run = _write_run(tmp_path, [("0x0800FA78", 0, 50000)])
    text = "\n".join(summarize(build_rows(run)))

    assert "stays UNKNOWN" in text
    assert "ratio" not in text


def test_missing_dump_file_yields_no_records(tmp_path):
    (tmp_path / "events.csv").write_text("stop,gameplay_tick,lr\n1,100,0x0800FA78\n",
                                         encoding="utf-8")
    rows = build_rows(tmp_path)

    assert load_dumps(tmp_path / "dumps.wfcap") == {}
    assert rows[0]["damage_raw"] is None
    assert "nothing can be concluded" in "\n".join(summarize(rows))
