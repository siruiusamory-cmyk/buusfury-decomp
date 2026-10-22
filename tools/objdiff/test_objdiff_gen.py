from __future__ import annotations

import importlib.util
import json
import os
import struct

HERE = os.path.dirname(os.path.abspath(__file__))


def module():
    spec = importlib.util.spec_from_file_location("_objdiff_gen", os.path.join(HERE, "objdiff_gen.py"))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def tree(tmp_path):
    (tmp_path / "work").mkdir()
    (tmp_path / "asm").mkdir()
    (tmp_path / "build" / "output").mkdir(parents=True)
    (tmp_path / "work" / "ledger.csv").write_text(
        "0x158,120,t,code_158_143F2,b,t,p,120\n"
        "0x1d0,8,t,sub_0801C62C,src/sub_0801C62C.c,c,m,8\n"
        "0x1d8,16,d,data_1D8,G,t,p,0\n"
        "0x1e8,24,d,structured_run_0001E8,r,g,p,0\n"
        "0x1f0,8,t,thumb_body_0001F0,s,t,p,8\n", encoding="ascii")
    (tmp_path / "asm" / "buu.s").write_text(
        "    INCBIN  baserom.gba_0x00300_0x00400.extracted\n", encoding="ascii")
    (tmp_path / "asm" / "slice_000158.s").write_text("", encoding="ascii")
    (tmp_path / "rebuild.cmd").write_text(
        "tcpp -c -cpu ARM7TDMI -Iinclude -O2 -Otime -apcs /nointerwork "
        "src/sub_0801C62C.c -o build/sub_0801C62C.o\n", encoding="ascii")
    (tmp_path / "build" / "sub_0801C62C.o").write_bytes(
        module().elf([(".text", 0x6, bytes(8), [("sub_0801C62C", 0, 8, "t")])]))
    (tmp_path / "build" / "output" / "symbols.json").write_text(json.dumps({"symbols": [
        {"name": "sub_0801C62C", "address": "0x0801c62c", "size": 8, "kind": "thumb"}]}),
        encoding="ascii")


def test_units_follow_the_ledger_and_need_no_image(tmp_path):
    tree(tmp_path)
    config, units = module().build(root=str(tmp_path))
    names = [unit["name"] for unit in config["units"]]
    assert names == sorted(names)
    assert "src/sub_0801C62C" in names
    assert "asm/buu/code_158_143F2" in names
    assert "asm/GBARam/data_1D8" in names
    assert "asm/slices/thumb_body_0001F0" in names
    assert "data/generated/structured_run_0001E8" in names
    assert "data/incbin/000300_000400" in names
    by_name = {unit["name"]: unit for unit in config["units"]}
    assert by_name["src/sub_0801C62C"]["base_path"] == "build/sub_0801C62C.o"
    assert by_name["src/sub_0801C62C"]["metadata"]["complete"] is True
    assert by_name["src/sub_0801C62C"]["metadata"]["source_path"] == "src/sub_0801C62C.c"
    assert by_name["src/sub_0801C62C"]["metadata"]["progress_categories"] == ["code"]
    assert by_name["asm/buu/code_158_143F2"].get("base_path") is None
    assert by_name["asm/buu/code_158_143F2"]["metadata"]["complete"] is False
    assert by_name["asm/buu/code_158_143F2"]["metadata"]["source_path"] == "asm/buu.s"
    assert by_name["asm/buu/code_158_143F2"]["metadata"]["progress_categories"] == ["code"]
    assert by_name["asm/GBARam/data_1D8"]["metadata"]["progress_categories"] == ["data"]
    assert by_name["asm/slices/thumb_body_0001F0"]["metadata"]["source_path"] == \
        "asm/slice_000158.s"
    assert by_name["data/generated/structured_run_0001E8"]["metadata"]["progress_categories"] \
        == ["data"]
    assert by_name["data/generated/structured_run_0001E8"]["metadata"]["source_path"] == \
        "asm/rest_of_the_game.s"
    assert by_name["data/incbin/000300_000400"]["metadata"]["source_path"] == "asm/buu.s"
    assert by_name["data/incbin/000300_000400"]["options"] == {"arm_arch_version": "v4t"}
    for unit in config["units"]:
        assert unit["target_path"].startswith("build/objdiff/target/")
    assert [category["id"] for category in config["progress_categories"]] == ["code", "data"]
    assert len(units) == len(config["units"])


def test_target_object_is_a_relocatable_arm_elf(tmp_path):
    gen = module()
    blob = gen.elf([
        (".text", 0x6, bytes(range(8)), [("one", 0, 4, "t"), ("two", 4, 4, "t")]),
        (".constdata", 0x2, bytes(range(8)), [("lut", 0, 8, "d")]),
    ])
    assert blob[:4] == b"\x7fELF"
    assert struct.unpack_from("<H", blob, 18)[0] == 40
    shoff = struct.unpack_from("<I", blob, 32)[0]
    assert struct.unpack_from("<H", blob, 48)[0] == 6
    assert struct.unpack_from("<H", blob, 50)[0] == 5
    symtab = shoff + 3 * 40
    assert struct.unpack_from("<I", blob, symtab + 4)[0] == 2
    assert struct.unpack_from("<I", blob, symtab + 28)[0] == 4
    path = tmp_path / "unit.o"
    path.write_bytes(blob)
    assert gen.headers(str(path))[1:] == [(".text", 0x6, 1), (".constdata", 0x2, 1),
                                          (".symtab", 0, 2), (".strtab", 0, 3),
                                          (".shstrtab", 0, 3)]
    assert gen.defined(str(path)) == [("one", 1, 0, 4), ("two", 1, 4, 4), ("lut", 2, 0, 8)]


def test_functions_read_back_the_base_symbols(tmp_path):
    gen = module()
    path = tmp_path / "unit.o"
    path.write_bytes(gen.elf([(".text", 0x6, bytes(16), [("b", 8, 8, "t"), ("a", 0, 8, "t")])]))
    assert gen.defined(str(path)) == [("a", 1, 0, 8), ("b", 1, 8, 8)]


def test_the_same_tree_gives_the_same_configuration(tmp_path):
    tree(tmp_path)
    gen = module()
    first = json.dumps(gen.build(root=str(tmp_path))[0], indent=2)
    second = json.dumps(gen.build(root=str(tmp_path))[0], indent=2)
    assert first == second
