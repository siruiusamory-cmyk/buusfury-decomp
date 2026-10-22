from __future__ import annotations

import csv
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import testkit

import export_labels
import written

LABELS = os.path.join(export_labels.ROOT, export_labels.OUT)
INPUTS = os.path.join(export_labels.ROOT, export_labels.INPUTS)
NAMES = os.path.join(export_labels.ROOT, export_labels.NAMES)


def a_tree(root, csv_text, inputs_text=None, runtime_text="address,mode,provenance\n"):
    os.makedirs(os.path.join(root, "docs", "research"), exist_ok=True)
    text = inputs_text if inputs_text is not None else (
        "[counts]\nfunctions = 2\n\n"
        "[[code]]\naddr = 0x08000100\nmode = \"thumb\"\nsize = 8\n\n"
        "[[entry]]\naddr = 0x08000200\nmode = \"arm\"\n")
    for path, body in ((os.path.join(root, export_labels.INPUTS), text),
                       (os.path.join(root, export_labels.NAMES), csv_text),
                       (os.path.join(root, "docs", "research", "RUNTIME_ENTRIES.csv"), runtime_text),
                       (os.path.join(root, "docs", "research", "PAGE.md"), "0x08000100\n")):
        with open(path, "w", encoding="ascii", newline="\n") as handle:
            handle.write(body)


def test_a_named_root_keeps_its_name_and_an_unnamed_root_gets_the_house_name(tmp_path):
    a_tree(str(tmp_path), "address,name,evidence_doc\n0x08000100,MapEntry_Root,docs/research/PAGE.md\n")
    assert export_labels.label_set(str(tmp_path)) == [
        (0x08000100, "thumb", 0x08000108, "MapEntry_Root"),
        (0x08000200, "arm", None, "sub_08000200")]


def test_a_runtime_row_the_export_lacks_reaches_the_label_file(tmp_path):
    a_tree(str(tmp_path), "address,name,evidence_doc\n0x08000100,MapEntry_Root,docs/research/PAGE.md\n",
           runtime_text="address,mode,provenance\n0x08000300,thumb,runtime-recorded\n")
    assert export_labels.label_set(str(tmp_path)) == [
        (0x08000100, "thumb", 0x08000108, "MapEntry_Root"),
        (0x08000200, "arm", None, "sub_08000200"),
        (0x08000300, "thumb", None, "sub_08000300")]
    image = os.path.join(str(tmp_path), "image.bin")
    with open(image, "wb") as handle:
        handle.write(b"\0" * 16)
    text = export_labels.render(str(tmp_path), image)
    assert 'name = "sub_08000300"\naddress = 0x08000300\nmode = "thumb"\n' in text


def test_a_missing_runtime_file_is_refused_rather_than_shrinking_the_label_file(tmp_path):
    a_tree(str(tmp_path), "address,name,evidence_doc\n0x08000100,MapEntry_Root,docs/research/PAGE.md\n")
    os.remove(os.path.join(str(tmp_path), "docs", "research", "RUNTIME_ENTRIES.csv"))
    with pytest.raises(SystemExit) as refused:
        export_labels.label_set(str(tmp_path))
    assert "RUNTIME_ENTRIES.csv" in str(refused.value)


def test_a_runtime_row_of_another_provenance_is_refused(tmp_path):
    a_tree(str(tmp_path), "address,name,evidence_doc\n0x08000100,MapEntry_Root,docs/research/PAGE.md\n",
           runtime_text="address,mode,provenance\n0x08000300,thumb,static-guess\n")
    with pytest.raises(SystemExit) as refused:
        export_labels.label_set(str(tmp_path))
    assert "provenance" in str(refused.value)


def test_a_name_the_export_carries_no_entry_for_is_refused(tmp_path):
    a_tree(str(tmp_path), "address,name,evidence_doc\n0x08000300,MapEntry_Root,docs/research/PAGE.md\n")
    with pytest.raises(SystemExit) as refused:
        export_labels.label_set(str(tmp_path))
    assert "no export entry carries" in str(refused.value)


def test_a_name_whose_doc_is_absent_is_refused(tmp_path):
    a_tree(str(tmp_path), "address,name,evidence_doc\n0x08000100,MapEntry_Root,docs/research/NONE.md\n")
    with pytest.raises(SystemExit) as refused:
        export_labels.label_set(str(tmp_path))
    assert "not in the tree" in str(refused.value)


def test_two_rows_with_one_name_are_refused(tmp_path):
    a_tree(str(tmp_path), "address,name,evidence_doc\n"
                          "0x08000100,MapEntry_Root,docs/research/PAGE.md\n"
                          "0x08000200,MapEntry_Root,docs/research/PAGE.md\n")
    with pytest.raises(SystemExit) as refused:
        export_labels.label_set(str(tmp_path))
    assert "same name" in str(refused.value)


def test_a_row_that_only_repeats_the_house_name_is_refused(tmp_path):
    a_tree(str(tmp_path), "address,name,evidence_doc\n0x08000200,sub_08000200,docs/research/PAGE.md\n")
    with pytest.raises(SystemExit) as refused:
        export_labels.label_set(str(tmp_path))
    assert "house name" in str(refused.value)


def test_the_house_name_is_the_retail_address_in_eight_uppercase_digits():
    assert export_labels.house(0x08001234) == "sub_08001234"
    assert export_labels.house(0x030000f0) == "sub_030000F0"


def test_a_committed_file_that_differs_is_reported_by_line(tmp_path):
    path = os.path.join(str(tmp_path), "file.txt")
    with open(path, "w", encoding="ascii", newline="\n") as handle:
        handle.write("one\ntwo\nthree\n")
    assert written.difference(path, "one\ntwo\nthree\n") is None
    assert "line 2" in written.difference(path, "one\nTWO\nthree\n")


def committed_labels():
    with open(LABELS, encoding="ascii", newline="") as handle:
        return handle.read()


def export_roots():
    with open(INPUTS, encoding="ascii", newline="") as handle:
        text = handle.read()
    out = {}
    for block in text.split("[[code]]")[1:]:
        addr = int(re.search(r'addr = 0x([0-9a-f]+)', block).group(1), 16)
        out[addr] = addr + int(re.search(r'size = (\d+)', block).group(1))
    for block in text.split("[[entry]]")[1:]:
        addr = int(re.search(r'addr = 0x([0-9a-f]+)', block).group(1), 16)
        out.setdefault(addr, None)
    return out


def runtime_addresses():
    path = os.path.join(export_labels.ROOT, "docs", "research", "RUNTIME_ENTRIES.csv")
    with open(path, newline="", encoding="ascii") as handle:
        return {int(row["address"], 16) for row in csv.DictReader(handle)}


def test_every_tracked_runtime_row_is_in_the_label_file():
    runtime = runtime_addresses()
    assert runtime
    carried = {int(addr, 16) for addr in re.findall(
        r'\[\[functions\]\]\nname = "[^"]*"\naddress = 0x([0-9a-f]+)', committed_labels())}
    assert runtime <= carried


def test_every_runtime_class_entry_the_export_tags_is_in_the_label_file():
    with open(INPUTS, encoding="ascii", newline="") as handle:
        text = handle.read()
    tagged = {int(addr, 16) for addr in re.findall(
        r'\[\[entry\]\]\naddr = 0x([0-9a-f]+)\nmode = "\w+"\nclass = "runtime"', text)}
    assert tagged
    carried = {int(addr, 16) for addr in re.findall(
        r'\[\[functions\]\]\nname = "[^"]*"\naddress = 0x([0-9a-f]+)', committed_labels())}
    assert tagged <= carried


def test_the_tracked_label_file_is_the_one_the_tree_derives():
    testkit.require(export_labels.ROM, "no image, so the label file cannot pin itself")
    assert export_labels.main(["--check"]) == 0


def test_the_label_file_carries_every_export_entry_and_no_other_address():
    text = committed_labels()
    carried = [int(addr, 16) for addr in re.findall(
        r'\[\[functions\]\]\nname = "[^"]*"\naddress = 0x([0-9a-f]+)', text)]
    assert carried
    assert len(carried) == len(set(carried))
    assert set(carried) == set(export_roots()) | runtime_addresses()


def test_the_file_pins_the_image_and_every_function_has_a_mode_and_its_export_end():
    testkit.require(export_labels.ROM, "no image, so the pin cannot be compared")
    text = committed_labels()
    assert text.startswith('format = "gba-labels"\nversion = 2\n\n[image]\n')
    pin = re.search(r'\[image\]\nsha256 = "([0-9a-f]{64})"', text).group(1)
    assert pin == export_labels.image_sha256()
    ends = export_roots()
    runtime = runtime_addresses()
    rows = re.findall(r'\[\[functions\]\]\nname = "([^"]*)"\naddress = 0x([0-9a-f]+)\n'
                      r'(?:end = 0x([0-9a-f]+)\n)?mode = "(\w+)"\n', text)
    assert len(rows) == len(ends) + len(runtime)
    for name, addr, end, mode in rows:
        assert mode in ("arm", "thumb")
        assert name
        if int(addr, 16) in ends:
            want = ends[int(addr, 16)]
            assert (int(end, 16) if end else None) == want
            continue
        assert int(addr, 16) in runtime
        assert end == ""


def test_every_name_row_cites_a_tracked_page_that_carries_its_address():
    rows = [line.strip().split(",") for line in open(NAMES, encoding="ascii")
            if line.strip() and not line.startswith("address")]
    assert rows
    for addr, name, doc in rows:
        path = os.path.join(export_labels.ROOT, *doc.split("/"))
        assert os.path.exists(path), doc
        assert doc.startswith("docs/research/"), doc
        page = open(path, encoding="utf-8", errors="replace").read().lower()
        seek = addr[2:].lower()
        assert seek in page, (addr, doc)
