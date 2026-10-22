from __future__ import annotations

import os
import random
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "gate"))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "mapcontainer"))

import gate  # noqa: E402
import raw_remainder  # noqa: E402
import unknown_census  # noqa: E402


def test_a_flat_tile_buffer_reads_one_and_a_counting_buffer_does_not():
    flat = bytes(32 * 8)
    assert unknown_census.tile_repeat(flat, 4) == 1.0
    counting = bytes(range(32)) * 8
    assert unknown_census.tile_repeat(counting, 4) < 0.5


def test_palette_words_take_bit_15_clear_on_every_halfword():
    good = bytes(range(0, 32, 2)) + bytes(16)
    assert unknown_census.palette_row(good) is True
    bad = bytearray(good)
    bad[1] = 0x80
    assert unknown_census.palette_row(bytes(bad)) is False
    assert unknown_census.palette_row(good[:-1]) is False


def test_a_smooth_stream_beats_its_own_shuffle_null_and_random_bytes_do_not():
    smooth = bytes((value * 7) % 256 for value in range(512))
    real, null = unknown_census.coherence(smooth, 0x1000)
    assert real - null > unknown_census.MARGIN
    rng = random.Random(7)
    noise = bytes(rng.randrange(256) for _ in range(512))
    real, null = unknown_census.coherence(noise, 0x2000)
    assert real - null <= unknown_census.MARGIN


def test_a_null_reading_above_below_or_equal_to_retail_is_named_that_way():
    assert unknown_census.null_relation(263, 383) == "above"
    assert unknown_census.null_relation(147, 85) == "below"
    assert unknown_census.null_relation(2, 2) == "equal to"


def test_the_generated_report_has_no_broken_pipe_table_row():
    path = os.path.join(os.path.dirname(os.path.dirname(HERE)), "docs", "research", "UNKNOWN_CENSUS.md")
    with open(path, encoding="utf-8") as handle:
        assert unknown_census.table_faults(handle.read()) == []
    broken = "| a | b |\n|---|---|\n| 1 |\n  2 |\n"
    assert unknown_census.table_faults(broken)


def test_a_committed_file_that_differs_from_the_generated_text_is_reported_by_line(tmp_path):
    generated = "a\nb\nc\n"
    path = tmp_path / "doc.md"
    path.write_bytes(generated.encode())
    assert unknown_census.file_difference(path, generated) is None
    assert unknown_census.check_files([(path, generated)]) is True
    path.write_bytes(generated.replace("b", "B", 1).encode())
    assert unknown_census.file_difference(path, generated) == 2
    assert unknown_census.check_files([(path, generated)]) is False
    path.write_bytes(generated.encode() + b"tail\n")
    assert unknown_census.file_difference(path, generated) == 4


def test_the_sample_fire_rule_is_one_helper_with_the_margin_and_positivity():
    assert unknown_census.sample_fires(0.60, 0.00) is True
    assert unknown_census.sample_fires(0.20, 0.10) is True
    assert unknown_census.sample_fires(0.05, 0.00) is False
    assert unknown_census.sample_fires(0.20, 0.16) is False
    assert unknown_census.sample_fires(-0.10, -0.20) is False


def test_the_webfoot_probe_requires_the_container_to_end_inside_the_row(monkeypatch):
    image = unknown_census.Image(bytes(range(0x40)))
    monkeypatch.setattr(raw_remainder, "webfoot_extent", lambda _rom, _start: (1, 0x30))
    assert unknown_census.measure_row(image, 0, 16)["webfoot"] is False
    monkeypatch.setattr(raw_remainder, "webfoot_extent", lambda _rom, _start: (1, 8))
    assert unknown_census.measure_row(image, 0, 16)["webfoot"] is True


def test_the_modal_share_comparison_is_byte_weighted_on_both_sides():
    assert unknown_census.byte_weighted_share([(1.0, 1), (0.0, 3)]) == 0.25
    assert unknown_census.byte_weighted_share([(0.5, 2), (0.25, 6)]) == 0.3125
    assert unknown_census.byte_weighted_share([]) == 0.0
    assert unknown_census.byte_weighted_share(
        pair for pair in [(1.0, 1), (0.0, 3)]) == 0.25


def test_the_population_sentence_names_the_tables_that_really_sum():
    text = ("## U1. The regions\n\n| region | id | rows | bytes |\n|---|---|---|---|\n"
            "| a | `R01` | 3 | 30 |\n| b | `R02` | 2 | 20 |\n"
            "| **total** | | **5** | **50** |\n\n"
            "## U2. Every instrument\n\n| region | rows | bytes | `sample` |\n|---|---|---|---|\n"
            "| a | 3 | 30 | x |\n| b | 2 | 20 | x |\n\n## U4. The readers\n")
    assert unknown_census.summed_tables(text) == {"## U1.": (5, 50), "## U2.": (5, 50)}


def test_class_shares_measures_the_sample_statistic_through_coherence(monkeypatch):
    calls = []

    def fake(blob, start, draws=unknown_census.DRAWS):
        calls.append((len(blob), start, draws))
        return 0.60, 0.0

    monkeypatch.setattr(unknown_census, "coherence", fake)
    rows = [{"start": 0, "end": 8, "bytes": 8, "class": "unknown"}]
    got = unknown_census.class_shares(bytes(16), rows)
    assert calls == [(8, 0, unknown_census.DRAWS)]
    assert got["unknown"][2] == 1


def image_or_skip():
    path = os.path.join(os.path.dirname(os.path.dirname(HERE)), "baserom.gba")
    if not os.path.exists(path):
        pytest.skip("the image is not in this worktree")
    return raw_remainder.read_rom()


def winning_class(rom, row, instruments):
    found = [kind for kind, _text in raw_remainder.matches(rom, row, instruments)]
    assert found == sorted(found, key=raw_remainder.PRIORITY.index), found
    return found[0] if found else "unknown"


def layout_faults(spans):
    faults = []
    for prev, cur in zip(spans, spans[1:]):
        if cur[2] == prev[2] + 1:
            if cur[0] > prev[1]:
                faults.append(("gap", prev, cur))
            elif cur[0] < prev[1]:
                faults.append(("overlap", prev, cur))
        elif cur[2] == 0:
            if cur[0] < prev[1]:
                faults.append(("cross-block overlap", prev, cur))
        else:
            faults.append(("index does not restart", prev, cur))
    return faults


def test_span_layout_faults_catch_a_gap_an_overlap_and_a_cross_block_overlap():
    good = [(0, 10, 0), (10, 20, 1), (30, 40, 0), (40, 50, 1)]
    assert layout_faults(good) == []
    assert layout_faults([(0, 10, 0), (12, 20, 1)])[0][0] == "gap"
    assert layout_faults([(0, 10, 0), (8, 20, 1)])[0][0] == "overlap"
    assert layout_faults([(0, 10, 0), (10, 20, 1), (15, 40, 0)])[0][0] == "cross-block overlap"


def test_the_143_named_spans_tile_the_two_directory_blocks_and_no_raw_row_lies_inside_one():
    rom = image_or_skip()
    spans = raw_remainder.audio_spans(rom)
    assert len(spans) == 143
    assert spans[0][0] == 0x2B9BB0
    assert spans[-1][1] == 0x36D18A
    assert sum(high - low for low, high, _index in spans) == 733911
    blocks = []
    for span in spans:
        if not blocks or span[2] != blocks[-1][-1][2] + 1:
            blocks.append([])
        blocks[-1].append(span)
    assert [len(block) for block in blocks] == [64, 79]
    assert layout_faults(spans) == []
    assert blocks[1][0][0] - blocks[0][-1][1] == 771
    for start, length in gate.incbin_ranges():
        for low, high, _index in spans:
            assert not (low <= start and start + length <= high), \
                "row 0x%06X lies inside the sample span 0x%06X..0x%06X" % (start, low, high)


def test_the_audio_predicate_fires_inside_a_named_span_and_not_outside_it():
    rom = bytes(0x40)
    instruments = {"jcalg1": [], "transcribed": {}, "graphics": (), "code": {},
                   "audio": [(0, 0x20, 0)]}
    assert "audio" in [kind for kind, _text in raw_remainder.matches(rom, (0, 16), instruments)]
    outside = winning_class(rom, (0x30, 16), instruments)
    assert outside != "audio"


def test_a_higher_priority_predicate_wins_while_audio_remains_a_rival():
    rom = bytes(0x40)
    instruments = {"jcalg1": [], "transcribed": {}, "graphics": (), "code": {},
                   "audio": [(0, 0x20, 0)]}
    found = [kind for kind, _text in raw_remainder.matches(rom, (0, 16), instruments)]
    assert found == ["fill/padding", "audio"]
    assert winning_class(rom, (0, 16), instruments) == "fill/padding"


def test_a_row_inside_a_named_span_is_classified_audio():
    rom = image_or_skip()
    spans = raw_remainder.audio_spans(rom)
    instruments = {"jcalg1": [], "transcribed": {}, "graphics": (), "code": {}, "audio": spans}
    second = next(span for prev, span in zip(spans, spans[1:]) if span[2] != prev[2] + 1)
    for low, _high, _index in (spans[0], second):
        assert winning_class(rom, (low, 16), instruments) == "audio"
