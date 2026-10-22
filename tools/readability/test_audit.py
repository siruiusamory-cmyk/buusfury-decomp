from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import audit


def test_band_classifies_the_io_page_and_not_its_neighbour():
    assert audit.band(0x04000000, audit.IO_START, audit.IO_END)
    assert audit.band(0x040003FE, audit.IO_START, audit.IO_END)
    assert not audit.band(0x04000400, audit.IO_START, audit.IO_END)
    assert not audit.band(0x05000000, audit.IO_START, audit.IO_END)


def test_address_name_takes_five_prefixes_and_eight_digits():
    for name in ("sub_08000158", "loc_0800016A", "dat_0801440C", "unk_03001BAC", "g_03005294"):
        assert audit.ADDRESS_NAME.match(name)
    for name in ("Blend_WriteControl1", "unk_03001BA", "g_0300529"):
        assert not audit.ADDRESS_NAME.match(name)


def test_main_reports_every_class(capsys=None):
    collected = []
    original = sys.stdout

    class Sink:
        def write(self, text):
            collected.append(text)

        def flush(self):
            pass

    sys.stdout = Sink()
    try:
        assert audit.main() == 0
    finally:
        sys.stdout = original
    text = "".join(collected)
    for label in ("layout", "hardware", "ram", "tables", "magic", "docs", "tools", "tests",
                  "symbols"):
        assert label in text
