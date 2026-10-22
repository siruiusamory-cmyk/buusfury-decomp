from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import library_match


def archive(name, body):
    header = (name.ljust(16) + "0".ljust(12) + "0".ljust(6) + "0".ljust(6)
              + "100644".ljust(8) + str(len(body)).ljust(10) + "`\n")
    return b"!<arch>\n" + header.encode("latin-1") + body


def test_an_archive_yields_its_members():
    assert library_match.members(archive("x.o/", b"0123456789abcdef")) == [
        ("x.o/", b"0123456789abcdef")]


def test_a_branch_relocation_masks_the_three_offset_bytes():
    assert library_match.fields([(0, 1)]) == {1, 2, 3}


def test_a_word_relocation_masks_the_whole_word():
    assert library_match.fields([(4, 2)]) == {4, 5, 6, 7}


def test_a_thumb_call_relocation_masks_the_call_pair():
    assert library_match.fields([(0, 10)]) == {0, 1, 2, 3}


def test_a_different_branch_offset_still_matches():
    assert library_match.same(b"\x00\xf0\x00\xf8", b"\x00\xf0\x04\xf8", {0, 1, 2})


def test_a_different_opcode_byte_does_not_match():
    assert not library_match.same(b"\x00\xf0\x00\xf8", b"\x00\xf0\x04\xf9", {0, 1, 2})


def test_a_relocated_word_carries_any_address():
    assert library_match.same(b"\x01\x02\x03\x04", b"\xf8\xd0\x7f\x08", {0, 1, 2, 3})


def test_a_member_is_found_at_an_emitted_entry_only():
    text = b"\x0a\x20\x01\x02\x03\x04\x70\x47"
    rom = b"\x00" * 0x100 + text + b"\x00" * 4
    assert library_match.matches(text, set(), rom, [0x08000100], 0x08000000) == [0x08000100]
    assert library_match.matches(text, set(), rom, [0x08000102], 0x08000000) == []


def test_entries_read_the_export_and_the_ledger(tmp_path):
    asm = tmp_path / "asm"
    asm.mkdir()
    (asm / "slice.s").write_text("\tEXPORT |sub_08000158|\n\tEXPORT |loc_08000160|\n"
                                 "\tEXPORT |Promoted_Name|\n\tEXPORT |unk_08000170|\n",
                                 encoding="ascii")
    ledger = tmp_path / "docs" / "NAMING_LEDGER.csv"
    ledger.parent.mkdir()
    ledger.write_text("address,old,new,evidence_class,evidence\n"
                      "0x08000200,sub_08000200,Promoted_Name,caller-role,page\n",
                      encoding="utf-8")
    assert library_match.entries(str(tmp_path)) == {0x08000158: "sub_08000158",
                                                    0x08000200: "Promoted_Name"}


def test_a_rename_rewrites_the_export_and_the_label_line():
    text = "\tEXPORT |sub_08000158|\n|sub_08000158|\n\tnop\n"
    assert library_match.renamed(text, "sub_08000158", "strlen") == (
        "\tEXPORT |strlen|\n|strlen|\n\tnop\n")


if __name__ == "__main__":
    test_an_archive_yields_its_members()
    test_a_branch_relocation_masks_the_three_offset_bytes()
    test_a_word_relocation_masks_the_whole_word()
    test_a_thumb_call_relocation_masks_the_call_pair()
    test_a_different_branch_offset_still_matches()
    test_a_different_opcode_byte_does_not_match()
    test_a_relocated_word_carries_any_address()
    test_a_member_is_found_at_an_emitted_entry_only()
    print("PASS test_library_match")
