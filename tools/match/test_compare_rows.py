from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import compare_rows


def scratch_ledger(text):
    path = os.path.join(tempfile.mkdtemp(prefix="match-test-"), "ledger.csv")
    with open(path, "w", encoding="ascii") as handle:
        handle.write(text)
    return path


def run(a, b, ledger):
    out = io.StringIO()
    argv = sys.argv
    sys.argv = ["compare_rows.py", a, b, "--ledger", ledger]
    try:
        with contextlib.redirect_stdout(out):
            code = compare_rows.main()
    finally:
        sys.argv = argv
    return code, out.getvalue()


def test_a_clean_pair_is_match_and_a_run_inside_a_row_names_it():
    shape = os.path.join(tempfile.mkdtemp(prefix="match-test-"), "a.bin")
    first = bytes(64)
    image = bytearray(first)
    image[9] ^= 0xFF
    with open(shape, "wb") as handle:
        handle.write(first)
    other = shape + ".b"
    with open(other, "wb") as handle:
        handle.write(bytes(image))
    ledger = scratch_ledger("0x0,8,thumb,first_row,asm/x.s,transcription,byte-proven,8\n"
                            "0x8,8,thumb,second_row,asm/x.s,transcription,byte-proven,8\n")
    code, printed = run(shape, shape, ledger)
    assert code == 0 and printed.rstrip().endswith("MATCH")
    code, printed = run(shape, other, ledger)
    assert code == 1
    assert "+0x000009" in printed and "second_row" in printed
    assert "rows with a differing run: second_row" in printed


def test_a_run_outside_every_row_is_unattributed():
    shape = os.path.join(tempfile.mkdtemp(prefix="match-test-"), "a.bin")
    with open(shape, "wb") as handle:
        handle.write(bytes(64))
    other = shape + ".b"
    image = bytearray(64)
    image[40] ^= 0xFF
    with open(other, "wb") as handle:
        handle.write(bytes(image))
    ledger = scratch_ledger("0x0,8,thumb,first_row,asm/x.s,transcription,byte-proven,8\n")
    code, printed = run(shape, other, ledger)
    assert code == 1 and "NOT IN ANY ROW" in printed


def test_a_size_mismatch_is_refused_not_diffed():
    shape = os.path.join(tempfile.mkdtemp(prefix="match-test-"), "a.bin")
    with open(shape, "wb") as handle:
        handle.write(bytes(64))
    other = shape + ".b"
    with open(other, "wb") as handle:
        handle.write(bytes(32))
    code, printed = run(shape, other, scratch_ledger("0x0,8,thumb,r,asm/x.s,transcription,byte-proven,8\n"))
    assert code == 1 and printed.startswith("SIZE MISMATCH")


def test_a_run_that_does_not_start_at_zero_prints_the_true_second_image_bytes():
    shape = os.path.join(tempfile.mkdtemp(prefix="match-test-"), "a.bin")
    with open(shape, "wb") as handle:
        handle.write(bytes(64))
    other = shape + ".b"
    image = bytearray(64)
    image[9] = 0xF8
    with open(other, "wb") as handle:
        handle.write(bytes(image))
    ledger = scratch_ledger("0x0,8,thumb,first_row,asm/x.s,transcription,byte-proven,8\n"
                            "0x8,8,thumb,second_row,asm/x.s,transcription,byte-proven,8\n")
    code, printed = run(shape, other, ledger)
    assert code == 1
    assert "+0x000009" in printed and "second_row" in printed
    assert "A=00  B=f8" in printed


if __name__ == "__main__":
    test_a_clean_pair_is_match_and_a_run_inside_a_row_names_it()
    test_a_run_outside_every_row_is_unattributed()
    test_a_size_mismatch_is_refused_not_diffed()
    test_a_run_that_does_not_start_at_zero_prints_the_true_second_image_bytes()
    print("PASS test_compare_rows")
