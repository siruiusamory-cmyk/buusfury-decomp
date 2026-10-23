from __future__ import annotations

import os
import shutil
import sys
import tempfile

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import lints

SHIM = "c" "md"
BARE = SHIM + " /c extract.cmd\n"
NAMED = "@echo off\n" + SHIM + ".exe /c extract.cmd\ncall rebuild.cmd\n"
POOL = "\n".join(["import multiprocessing", "", "def run():",
                  "    return multiprocessing.Pool(2)"])
POOL_GUARDED = POOL + '\n\nif __name__ == "__main__":\n    run()\n'
DRIVE = "C" + ":"
OUTSIDE = 'import sys\nsys.path.insert(0, r"%s\\\\temp\\\\clone\\\\tools\\\\formats")\n' % DRIVE
INSIDE = 'import sys, os\nsys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n'
MARKED = "/* NONMATCHING-REFERENCE: reconstructed, not linked. */\nvoid Unit_DoIt(void) {\n}\n"
UNMARKED = "void Unit_DoIt(void) {\n}\n"
LOWERCASE_VERB = "void Unit_doit(void) {\n}\n"
CONVENTION_NAMES = ("void Unit_DoIt(void) {\n}\nvoid sub_080143F2(void) {\n}\n"
                    "void sub_0801C62C(void) {\n}\n")
MEASURED = (6274068, 8388608, "74.7927", 8518)
STALE_PROGRESS = ("The source-built surface is 2,004,828 of 8,388,608 bytes (23.8994 %): "
                  "1,395 ledger rows in `work/ledger.csv`.")
MEASURED_PROGRESS = ("74.7927 % of the ROM (6,274,068 of 8,388,608 bytes) is built from this "
                     "repository's sources; `python tools\\gate\\gate.py` prints it.")
BYTES_FIRST = ("6,274,068 of 8,388,608 bytes (74.7927 %) is built from this repository's "
               "sources; `python tools\\gate\\gate.py` prints it.")
IDENTIFIED = ("3.9375", 330306)
IDENTIFIED_LINE = (MEASURED_PROGRESS + " 3.9375 % is identified binary (330,306 B whose region is "
                                       "mapped and no format beats its null)")
BLOCK = ("def %s():\n"
         "    first = 1\n"
         "    second = first + 1\n"
         "    third = second * 2\n"
         "    fourth = third - 3\n"
         "    fifth = fourth / 4\n"
         "    sixth = fifth + 6\n"
         "    seventh = sixth - 7\n"
         "    return seventh\n")
PLANTED_DUPLICATE = BLOCK % "left" + "\n" + BLOCK % "right"
ONE_COPY = BLOCK % "left"
SILENT_RETURN = ("import os\n"
                 "\n"
                 "\n"
                 "def test_the_image_is_there():\n"
                 "    if not os.path.exists('baserom.gba'):\n"
                 "        return\n"
                 "    assert True\n")
SKIPPED = ("import os\n"
           "import pytest\n"
           "\n"
           "\n"
           "def test_the_image_is_there():\n"
           "    if not os.path.exists('baserom.gba'):\n"
           "        pytest.skip('baserom.gba is absent, so this test cannot run')\n"
           "    assert True\n")
NESTED_HELPER = ("def test_the_helper_may_return():\n"
                 "    def check():\n"
                 "        return 1\n"
                 "    assert check() == 1\n")
EARLY_RETURN_AFTER_ASSERT = ("def test_the_population_is_measured():\n"
                             "    rows = read()\n"
                             "    assert rows\n"
                             "    if len(rows) < 2:\n"
                             "        return\n"
                             "    assert rows[1]\n")
ASSERT_IN_ONE_BRANCH = ("def test_the_image_is_there():\n"
                        "    if present():\n"
                        "        assert True\n"
                        "        return\n"
                        "    return\n")
MATCH_RETURN = ("def test_the_fixture_is_there():\n"
                "    match read():\n"
                "        case None:\n"
                "            return\n"
                "        case _:\n"
                "            assert True\n")
FOREIGN_SKIP = ("def test_the_image_is_there():\n"
                "    reporter.skip()\n"
                "    return\n")
C_COMMENTED_DUPLICATE = ("/* the header\n"
                         "   spans three\n"
                         "   physical lines */\n"
                         "static void unit_left(void) {\n"
                         "    unsigned first = 1;\n"
                         "    unsigned second = first + 1;\n"
                         "    unsigned third = second * 2;\n"
                         "    unsigned fourth = third - 3;\n"
                         "    unsigned fifth = fourth / 4;\n"
                         "    unsigned sixth = fifth + 6;\n"
                         "    unsigned seventh = sixth - 7;\n"
                         "}\n"
                         "\n"
                         "static void unit_right(void) {\n"
                         "    unsigned first = 1;\n"
                         "    unsigned second = first + 1;\n"
                         "    unsigned third = second * 2;\n"
                         "    unsigned fourth = third - 3;\n"
                         "    unsigned fifth = fourth / 4;\n"
                         "    unsigned sixth = fifth + 6;\n"
                         "    unsigned seventh = sixth - 7;\n"
                         "}\n")


CALL = "call tools\\incbin.bat baserom.gba 0x158 0x143f2\n"
ASM_GOOD = "\tEXPORT |sub_08000158|\n\tEXPORT |Module_DoIt|\n\tEXPORT |loc_0800016A|\n" \
           "\tEXPORT |inc_0x071c90_0x3715c0|\n\tEXPORT |unk_03003014|\n"
ASM_BAD_NAME = "\tEXPORT |lowercase_verb|\n"
ASM_BAD_DIGITS = "\tEXPORT |sub_08001|\n"
ASM_LIBRARY = "\tEXPORT |strlen|\n"
CRAFTED_BOUNDS = ("address,kind,limb,parent\n"
                  "0x08000158,start,prologue,\n"
                  "0x0800016A,unreferenced,,\n"
                  "0x08000170,block,,0x08000158\n")
CRAFTED_LEDGER = ("address,old,new,evidence_class,evidence\n"
                  "0x08046B28,sub_08046B28,strlen,toolchain-library,armlib/c_t__un.l\n"
                  "0x08046B84,sub_08046B84,memcpy,caller-role,page\n")
ASM_CONSTANT = "unk_03003014    EQU     0x03003014\n\tEXPORT  unk_03003014\n"
README_SYMBOL_LINE = MEASURED_PROGRESS + " 6,739 of the 6,740 functions"


def refused(text, name, check):
    scratch = tempfile.mkdtemp(prefix="lint-test-")
    try:
        path = os.path.join(scratch, name)
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        return [detail for found, detail in lints.run([path]) if found == check]
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


PROLOGUE = ("from __future__ import annotations\nimport hashlib\nimport io\nimport os\n"
            "import re\nimport struct\nimport sys\nimport tokenize\n")

ANSWER_CASES = (
    pytest.param(BARE, "step.cmd", "P-159-bare-interpreter", True,
                 id="a_bare_interpreter_launch_in_a_step_script_is_caught"),
    pytest.param(NAMED, "step.cmd", "P-159-bare-interpreter", False,
                 id="the_executable_name_and_a_sibling_script_are_not_caught"),
    pytest.param(POOL, "probe.py", "P-167-pool-guard", True,
                 id="a_pool_in_a_module_with_no_main_guard_is_caught"),
    pytest.param(POOL_GUARDED, "probe.py", "P-167-pool-guard", False,
                 id="the_same_pool_under_a_main_guard_is_not_caught"),
    pytest.param(OUTSIDE, "tool.py", "P-148-repo-module-path", True,
                 id="a_search_path_leaving_the_repository_is_caught"),
    pytest.param(INSIDE, "tool.py", "P-148-repo-module-path", False,
                 id="a_search_path_inside_the_repository_is_not_caught"),
    pytest.param(ONE_COPY, "tool.py", "DUP-block", False,
                 id="a_block_written_once_is_not_caught"),
    pytest.param(PROLOGUE + PROLOGUE, "tool.py", "DUP-block", False,
                 id="a_repeated_import_prologue_is_not_a_duplicate"),
    pytest.param(SKIPPED, "test_image.py", "TEST-silent-return", False,
                 id="a_test_that_skips_with_a_reason_is_not_caught"),
    pytest.param(NESTED_HELPER, "test_image.py", "TEST-silent-return", False,
                 id="a_helper_defined_inside_a_test_may_return"),
    pytest.param(EARLY_RETURN_AFTER_ASSERT, "test_image.py", "TEST-silent-return", False,
                 id="a_return_after_an_assert_is_not_caught"),
)


@pytest.mark.parametrize("text,name,check,caught", ANSWER_CASES)
def test_the_lint_answer_to_one_input(text, name, check, caught):
    found = refused(text, name, check)
    assert bool(found) == caught


CAUGHT_CASES = (
    pytest.param(PLANTED_DUPLICATE, "tool.py", "DUP-block",
                 ("tool.py:2 and", "tool.py:12: 8 identical lines"),
                 id="a_block_written_twice_in_one_file_is_caught"),
    pytest.param(SILENT_RETURN, "test_image.py", "TEST-silent-return",
                 (":6: test_the_image_is_there",),
                 id="a_test_that_returns_when_its_fixture_is_missing_is_caught"),
    pytest.param(ASSERT_IN_ONE_BRANCH, "test_image.py", "TEST-silent-return",
                 (":5: test_the_image_is_there",),
                 id="an_assert_inside_one_branch_does_not_clear_a_return_in_another"),
    pytest.param(MATCH_RETURN, "test_image.py", "TEST-silent-return",
                 (":4: test_the_fixture_is_there",),
                 id="a_return_inside_a_match_case_is_caught"),
    pytest.param(FOREIGN_SKIP, "test_image.py", "TEST-silent-return",
                 (":3: test_the_image_is_there",),
                 id="a_skip_on_an_unrelated_object_does_not_clear_a_return"),
)


@pytest.mark.parametrize("text,name,check,fragments", CAUGHT_CASES)
def test_a_refused_run_names_the_lines_it_refused(text, name, check, fragments):
    found = refused(text, name, check)
    assert len(found) == 1, found
    assert [fragment for fragment in fragments if fragment not in found[0]] == [], found


def test_a_function_name_outside_the_convention_is_caught():
    assert lints.function_name_findings("src/Unit.c", LOWERCASE_VERB)


def test_module_verb_and_sub_08xxxxxx_names_are_not_caught():
    assert not lints.function_name_findings("src/Unit.c", CONVENTION_NAMES)


def test_a_c_source_the_build_skips_and_does_not_mark_is_caught():
    assert lints.c_status_findings("src/Unit.c", UNMARKED, compiled=set())


def test_a_c_source_the_build_skips_and_marks_is_not_caught():
    assert not lints.c_status_findings("src/Unit.c", MARKED, compiled=set())


def test_a_c_source_the_build_compiles_and_marks_is_caught():
    assert lints.c_status_findings("src/sub_0801C62C.c", MARKED, compiled={"src/sub_0801C62C.c"})


def test_a_c_source_the_build_compiles_and_does_not_mark_is_not_caught():
    assert not lints.c_status_findings("src/sub_0801C62C.c", UNMARKED,
                                       compiled={"src/sub_0801C62C.c"})


def test_a_marker_below_the_header_does_not_satisfy_the_check():
    body_marker = "void Unit_DoIt(void) {\n    /* NONMATCHING-REFERENCE */\n}\n"
    assert lints.c_status_findings("src/Unit.c", body_marker, compiled=set())


def test_a_tracked_rom_path_is_caught():
    assert lints.tracked_image_name("baserom.gba")


def test_a_tracked_source_path_is_not_caught():
    assert not lints.tracked_image_name("src/GBARam.c")


def test_the_tracked_retail_hash_file_is_not_caught():
    assert not lints.tracked_image_name("baserom.sha1")


def test_a_tracked_file_over_a_megabyte_outside_assets_is_caught():
    assert lints.oversize_tracked("tools/big.bin", 2 * 1024 * 1024)


def test_a_tracked_file_over_a_megabyte_under_assets_is_not_caught():
    assert not lints.oversize_tracked("assets/big.bin", 2 * 1024 * 1024)


def test_the_stale_readme_progress_line_is_caught():
    assert lints.readme_numbers_findings(STALE_PROGRESS, *MEASURED)


def test_a_one_digit_percentage_change_is_caught():
    assert lints.readme_numbers_findings(MEASURED_PROGRESS.replace("74.7927", "74.7928"),
                                         *MEASURED)


def test_a_one_digit_byte_count_change_is_caught():
    assert lints.readme_numbers_findings(MEASURED_PROGRESS.replace("6,274,068", "6,274,069"),
                                         *MEASURED)


def test_a_row_count_that_disagrees_with_the_ledger_is_caught():
    assert lints.readme_numbers_findings(MEASURED_PROGRESS + " 1,395 ledger rows", *MEASURED)


def test_the_measured_readme_progress_line_is_not_caught():
    assert not lints.readme_numbers_findings(MEASURED_PROGRESS, *MEASURED)


def test_a_readme_with_no_row_count_and_the_bytes_first_is_not_caught():
    assert not lints.readme_numbers_findings(BYTES_FIRST, *MEASURED)


def test_the_ledger_identified_binary_figure_is_allowed_and_a_third_percentage_is_not():
    assert not lints.readme_numbers_findings(IDENTIFIED_LINE, *MEASURED, identified=IDENTIFIED)
    assert lints.readme_numbers_findings(IDENTIFIED_LINE + " 1.0000 % extra", *MEASURED,
                                         identified=IDENTIFIED)


README_REFUSED = (
    pytest.param(MEASURED_PROGRESS + " 74.7927 %", id="two_copies_of_the_source_percentage"),
    pytest.param(MEASURED_PROGRESS, id="a_missing_identified_binary_percentage"),
    pytest.param(IDENTIFIED_LINE.replace("330,306", "330,307"),
                 id="a_drifted_identified_binary_byte_count"),
)


@pytest.mark.parametrize("text", README_REFUSED)
def test_the_readme_two_number_guard_refuses(text):
    assert lints.readme_numbers_findings(text, *MEASURED, identified=IDENTIFIED)


def test_a_progress_line_without_its_command_is_caught():
    assert lints.readme_numbers_findings(
        MEASURED_PROGRESS.replace("`python tools\\gate\\gate.py` ", ""), *MEASURED)


def test_an_incbin_call_naming_a_slice_no_source_incbins_is_caught():
    assert lints.stale_call_findings(CALL, set())


def test_an_incbin_call_naming_a_slice_the_source_incbins_is_not_caught():
    assert not lints.stale_call_findings(CALL, {(0x158, 0x143f2 - 0x158)})


def test_the_repository_has_no_lint_finding():
    assert lints.run() == []


def exported(text):
    return [(name, "asm/unit.s", line) for line, name in lints.asm_exports(text)[0]]


def test_an_asm_export_outside_the_convention_is_caught():
    for text in (ASM_BAD_NAME, ASM_BAD_DIGITS):
        assert lints.asm_symbol_findings(exported(text), {})


def test_module_verb_address_and_slice_exports_are_not_caught():
    assert not lints.asm_symbol_findings(exported(ASM_GOOD), {})


def test_an_address_form_whose_digits_are_not_its_own_address_is_caught():
    assert lints.asm_symbol_findings(exported(ASM_GOOD), {"sub_08000158": 0x0800015A})
    assert not lints.asm_symbol_findings(exported(ASM_GOOD), {"sub_08000158": 0x08000158})


def test_a_library_symbol_is_caught_without_its_toolchain_library_row():
    assert lints.asm_symbol_findings(exported(ASM_LIBRARY), {}, library=())
    assert not lints.asm_symbol_findings(exported(ASM_LIBRARY), {}, library={"strlen"})


def test_a_sub_name_on_an_interior_block_is_caught():
    assert lints.block_findings(exported("\tEXPORT |sub_08001000|\n"), {}, {0x08001000})
    assert not lints.block_findings(exported("\tEXPORT |sub_08001000|\n"), {}, {0x08001002})


def test_a_module_verb_name_on_an_interior_block_is_caught():
    assert lints.block_findings(exported("\tEXPORT |Unit_DoIt|\n"),
                                {"Unit_DoIt": 0x08001000}, {0x08001000})


def test_a_loc_name_on_an_interior_block_is_not_caught():
    assert not lints.block_findings(exported("\tEXPORT |loc_08001000|\n"), {}, {0x08001000})


def test_a_sub_name_on_a_function_start_is_not_caught():
    assert not lints.block_findings(exported("\tEXPORT |sub_08001000|\n"), {}, set())


def test_an_unreferenced_census_row_is_a_start_the_naming_rules_cover():
    starts, blocks = lints.census_kinds(CRAFTED_BOUNDS)
    assert starts == {0x08000158, 0x0800016A}
    assert blocks == {0x08000170}
    assert not lints.block_findings(exported("\tEXPORT |Unit_DoIt|\n"),
                                    {"Unit_DoIt": 0x0800016A}, blocks)


def test_the_ratchet_counts_function_starts_rather_than_exports():
    addresses = {"Module_DoIt": 0x08000158}
    assert lints.naming_counts({0x08000158}, addresses, exported(ASM_GOOD)) == (0, 1)
    assert lints.naming_counts({0x0800016A}, addresses, exported(ASM_GOOD)) == (1, 1)
    assert lints.naming_counts(set(), addresses, exported(ASM_GOOD)) == (0, 0)


def test_a_start_named_only_by_a_ledger_row_is_not_address_named():
    assert lints.naming_counts({0x08000158}, {"Unit_Named": 0x08000158},
                               exported("\tEXPORT |sub_08000158|\n")) == (0, 1)
    assert lints.naming_counts({0x08000158}, {}, exported("\tEXPORT |sub_08000158|\n")) == (1, 1)


def test_a_library_name_at_a_start_is_not_an_address_name():
    assert lints.naming_counts({0x08000158}, {"strlen": 0x08000158},
                               exported("\tEXPORT |sub_08000158|\n"),
                               library={"strlen"}) == (0, 1)


def test_only_a_toolchain_library_row_admits_a_library_symbol():
    assert lints.library_symbols(CRAFTED_LEDGER) == {"strlen"}
    assert not lints.asm_symbol_findings(exported(ASM_LIBRARY), {},
                                         library=lints.library_symbols(CRAFTED_LEDGER))
    assert lints.asm_symbol_findings(exported("\tEXPORT |memcpy|\n"), {},
                                     library=lints.library_symbols(CRAFTED_LEDGER))


def test_the_ratchet_refuses_a_count_above_the_baseline():
    assert lints.ratchet_findings(10, 9)


def test_the_ratchet_refuses_a_count_below_an_unlowered_baseline():
    assert lints.ratchet_findings(8, 9)


def test_the_ratchet_accepts_the_count_the_baseline_holds():
    assert not lints.ratchet_findings(9, 9)


def test_the_ratchet_refuses_a_raise_no_retired_row_covers():
    assert lints.ratchet_findings(6690, 6680, 5)
    assert lints.ratchet_findings(6690, 6680, 0)


def test_the_ratchet_accepts_a_raise_the_retired_rows_cover():
    assert not lints.ratchet_findings(6685, 6680, 5)
    assert not lints.ratchet_findings(6680, 6680, 0)


def test_a_retired_row_that_licenses_nothing_must_lower_the_baseline():
    assert lints.ratchet_findings(6680, 6680, 5)
    assert lints.ratchet_findings(6697, 6680, 16)


def test_a_retired_row_must_be_an_address_named_export():
    retired = [{"address": "0x08004DEE", "retired": "Blend_WriteAlpha1", "reason": "page"}]
    assert not lints.retired_findings(retired, exported(ASM_GOOD + "\tEXPORT |sub_08004DEE|\n"),
                                     [])
    assert lints.retired_findings(retired, exported(ASM_GOOD), [])
    assert lints.retired_findings(retired, exported(ASM_GOOD + "\tEXPORT |sub_08004DEE|\n"),
                                  [(0x08004DEE, "Blend_WriteAlpha1")])
    stale = exported(ASM_GOOD + "\tEXPORT |sub_08004DEE|\n\tEXPORT |Blend_WriteAlpha1|\n")
    assert lints.retired_findings(retired, stale, [])
    assert not lints.retired_findings(retired, stale, [(0x0800536A, "Blend_WriteAlpha1")])


def test_an_exported_ram_constant_is_not_a_function_start():
    assert lints.naming_counts({0x08000158}, {}, exported(ASM_CONSTANT)) == (1, 1)
    assert lints.naming_counts(set(), {}, exported(ASM_CONSTANT)) == (0, 0)


def test_the_readme_symbol_figure_that_disagrees_is_caught():
    assert lints.readme_numbers_findings(README_SYMBOL_LINE, *MEASURED, symbols=(6738, 6740))


def test_the_readme_symbol_figure_that_agrees_is_not_caught():
    assert not lints.readme_numbers_findings(README_SYMBOL_LINE, *MEASURED, symbols=(6739, 6740))


def test_a_pair_named_in_the_allowlist_is_cleared():
    scratch = tempfile.mkdtemp(prefix="lint-test-")
    try:
        path = os.path.join(scratch, "tool.py")
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(PLANTED_DUPLICATE)
        first, second, _ = lints.duplicate_blocks([path])[0]
        saved = lints.DUP_ALLOWLIST
        lints.DUP_ALLOWLIST = ((first[0], first[1], second[0], second[1], "measured"),)
        try:
            assert not [detail for found, detail in lints.run([path]) if found == "DUP-block"]
        finally:
            lints.DUP_ALLOWLIST = saved
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def test_a_multiline_c_comment_keeps_the_reported_line_numbers():
    found = refused(C_COMMENTED_DUPLICATE, "unit.c", "DUP-block")
    assert len(found) == 1, found
    assert "unit.c:5 and" in found[0], found
    assert "unit.c:15: 8 identical lines" in found[0], found


def test_a_line_comment_marker_inside_a_string_is_not_a_comment():
    assert lints.c_lines('printf("http://x");\n') == [(1, 'printf("http://x");')]


def test_a_block_comment_marker_inside_a_string_hides_nothing():
    text = 'puts("/*");\nint kept = 1;\n/* real */\nint tail = 2;\n'
    assert lints.c_lines(text) == [(1, 'puts("/*");'), (2, "int kept = 1;"), (3, ""),
                                   (4, "int tail = 2;")]


def test_an_inline_block_comment_leaves_the_code_on_both_sides():
    assert lints.c_lines("a /* c */ b\n") == [(1, "a b")]


def test_a_char_literal_holding_a_slash_is_not_a_comment():
    assert lints.c_lines("if (c == '/') { n++; }\n") == [(1, "if (c == '/') { n++; }")]


def test_a_behaviour_test_row_must_cite_a_test_the_tree_has():
    row = {"address": "0x0801191A", "new": "List_Append",
           "evidence_class": "behaviour-test",
           "evidence": "tools/behaviour/test_names.py::test_list_append_stores"}
    assert not lints.behaviour_findings(
        [row], names_of=lambda path: {"test_list_append_stores"})
    assert lints.behaviour_findings(
        [row], names_of=lambda path: {"test_something_else"})
    assert lints.behaviour_findings([row], names_of=lambda path: None)
    assert lints.behaviour_findings(
        [dict(row, evidence="the function appends")],
        names_of=lambda path: {"test_list_append_stores"})


def test_a_row_of_another_class_cites_no_test():
    row = {"address": "0x0800536A", "new": "Blend_WriteControl1",
           "evidence_class": "hardware-register",
           "evidence": "writes BLDCNT 0x04000050"}
    assert not lints.behaviour_findings([row], names_of=lambda path: set())


def test_a_raw_hardware_literal_the_baseline_does_not_admit_is_caught():
    documents = [("asm/probe.s", "\tDCD     0x04000040\n")]
    findings = lints.hardware_literal_findings(documents, "")
    assert [finding[0] for finding in findings] == ["ASM-hardware-literal"]
    assert "0x04000040" in findings[0][1]
    assert not lints.hardware_literal_findings(documents, "0x04000040 1\n")
    stale = lints.hardware_literal_findings(documents, "0x04000040 2\n")
    assert stale and "must be lowered" in stale[0][1]
    named = [("asm/probe.s", "REG_BLDCNT\tEQU\t0x04000050\n\tDCD     REG_BLDCNT\n")]
    assert not lints.hardware_literal_findings(named, "")


def test_a_raw_ram_literal_above_the_baseline_is_caught():
    documents = [("asm/probe.s", "\tDCD     0x03004000\n")]
    high = lints.ram_ratchet_findings(documents, "0\n")
    assert [finding[0] for finding in high] == ["ASM-ram-ratchet"]
    assert not lints.ram_ratchet_findings(documents, "1\n")
    low = lints.ram_ratchet_findings(documents, "2\n")
    assert low and "must be lowered" in low[0][1]


def test_a_slice_file_and_a_misnamed_function_file_are_caught():
    census = "address,kind,limb,parent\n0x08000158,start,,\n0x08000159,start,,\n"
    index = ("address,kind,symbol,file\n"
             "0x08000158,start,sub_08000158,asm/sub_08000158.s\n"
             "0x08000159,start,sub_08000159,asm/sub_08000159.s\n")
    good = [("asm/sub_08000158.s", "|sub_08000158|\n\tBX lr\n"),
            ("asm/sub_08000159.s", "|sub_08000159|\n\tBX lr\n")]
    assert not lints.layout_findings(good, census, index)
    sliced = lints.layout_findings(good + [("asm/slice_000158.s", "")], census, index)
    assert [finding[0] for finding in sliced] == ["ASM-layout"]
    misnamed = lints.layout_findings([("asm/sub_08000158.s", "|sub_08000159|\n")], census, index)
    assert any("does not carry the label of its own address" in finding[1]
               for finding in misnamed)


def test_a_ledger_row_without_its_label_at_its_address_is_caught():
    ledger = ("address,old,new,evidence_class,evidence\n"
              "0x0800536A,sub_0800536A,Blend_WriteControl1,hardware-register,cited\n")
    unnamed = ("address,kind,symbol,file\n"
               "0x0800536A,start,,asm/loc_08005228.s\n")
    documents = [("asm/loc_08005228.s", "|loc_08005228|\n\tBX lr\n")]
    findings = lints.ledger_label_findings(ledger, unnamed, documents)
    assert [finding[0] for finding in findings] == ["NAMING-ledger-label"]
    assert "carries no asm label" in findings[0][1]
    named = ("address,kind,symbol,file\n"
             "0x0800536A,start,Blend_WriteControl1,asm/Blend_WriteControl1.s\n")
    carried = [("asm/Blend_WriteControl1.s", "|Blend_WriteControl1|\n\tBX lr\n")]
    assert not lints.ledger_label_findings(ledger, named, carried)
    elsewhere = lints.ledger_label_findings(ledger, named, documents)
    assert any("carries no such label" in finding[1] for finding in elsewhere)
    other = ("address,kind,symbol,file\n"
             "0x0800536A,start,unk_0800536A,asm/unk_0800536A.s\n")
    wrong = lints.ledger_label_findings(ledger, other, [("asm/unk_0800536A.s", "|unk_0800536A|\n")])
    assert any("is labelled unk_0800536A" in finding[1] for finding in wrong)


def test_an_entry_allow_row_the_census_does_not_carry_is_caught():
    census = "address,kind,limb,parent\n0x08000158,unreferenced,,\n"
    allow = ("address,kind,limb,flags,entry,reason\n"
             "0x08000158,unreferenced,,data,0x0800015a,prefix\n")
    assert not lints.entry_allow_findings(census, allow)
    stale = lints.entry_allow_findings("address,kind,limb,parent\n", allow)
    assert [finding[0] for finding in stale] == ["BOUNDS-entry-allow"]
    assert "carries kind" in stale[0][1]
    missing = lints.entry_allow_findings(census, "")
    assert missing and "no entry allow-list" in missing[0][1]


def test_an_entry_allow_row_without_a_flag_or_a_reason_is_caught():
    census = "address,kind,limb,parent\n0x08000158,unreferenced,,\n"
    head = "address,kind,limb,flags,entry,reason\n"
    bare = head + "0x08000158,unreferenced,,,0x0800015a,\n"
    caught = [finding[1] for finding in lints.entry_allow_findings(census, bare)]
    assert any("carries flags" in detail for detail in caught)
    assert any("kept with reason none" in detail for detail in caught)
    wrong = head + "0x08000158,unreferenced,,data,-,prefix\n"
    assert any("not an address after it" in finding[1]
               for finding in lints.entry_allow_findings(census, wrong))
    carried = head + "0x08000158,unreferenced,,shape,0x0800015a,split\n"
    assert any("no prologue to name" in finding[1]
               for finding in lints.entry_allow_findings(census, carried))
    twice = head + "0x08000158,unreferenced,,data,0x0800015a,prefix\n" * 2
    assert any("carried twice" in finding[1]
               for finding in lints.entry_allow_findings(census, twice))


def test_a_newcomer_page_without_the_gate_step_is_caught():
    findings = lints.doc_path_findings("git clone x\n")
    assert [finding[0] for finding in findings] == ["DOC-newcomer-path"] * len(findings)
    assert any("gate" in finding[1] for finding in findings)
    complete = " ".join(needle for _label, needle in lints.NEWCOMER_STEPS)
    assert not lints.doc_path_findings(complete)


if __name__ == "__main__":
    for answer in ANSWER_CASES:
        test_the_lint_answer_to_one_input(*answer.values)
    for caught in CAUGHT_CASES:
        test_a_refused_run_names_the_lines_it_refused(*caught.values)
    test_a_function_name_outside_the_convention_is_caught()
    test_module_verb_and_sub_08xxxxxx_names_are_not_caught()
    test_a_c_source_the_build_skips_and_does_not_mark_is_caught()
    test_a_c_source_the_build_skips_and_marks_is_not_caught()
    test_a_c_source_the_build_compiles_and_marks_is_caught()
    test_a_c_source_the_build_compiles_and_does_not_mark_is_not_caught()
    test_a_marker_below_the_header_does_not_satisfy_the_check()
    test_a_tracked_rom_path_is_caught()
    test_a_tracked_source_path_is_not_caught()
    test_the_tracked_retail_hash_file_is_not_caught()
    test_a_tracked_file_over_a_megabyte_outside_assets_is_caught()
    test_a_tracked_file_over_a_megabyte_under_assets_is_not_caught()
    test_the_stale_readme_progress_line_is_caught()
    test_a_one_digit_percentage_change_is_caught()
    test_a_one_digit_byte_count_change_is_caught()
    test_a_row_count_that_disagrees_with_the_ledger_is_caught()
    test_the_measured_readme_progress_line_is_not_caught()
    test_a_readme_with_no_row_count_and_the_bytes_first_is_not_caught()
    test_the_ledger_identified_binary_figure_is_allowed_and_a_third_percentage_is_not()
    for refused_text in README_REFUSED:
        test_the_readme_two_number_guard_refuses(refused_text.values[0])
    test_a_progress_line_without_its_command_is_caught()
    test_an_incbin_call_naming_a_slice_no_source_incbins_is_caught()
    test_an_incbin_call_naming_a_slice_the_source_incbins_is_not_caught()
    test_the_repository_has_no_lint_finding()
    test_an_asm_export_outside_the_convention_is_caught()
    test_module_verb_address_and_slice_exports_are_not_caught()
    test_an_address_form_whose_digits_are_not_its_own_address_is_caught()
    test_a_library_symbol_is_caught_without_its_toolchain_library_row()
    test_only_a_toolchain_library_row_admits_a_library_symbol()
    test_the_ratchet_refuses_a_count_above_the_baseline()
    test_the_ratchet_refuses_a_count_below_an_unlowered_baseline()
    test_the_ratchet_accepts_the_count_the_baseline_holds()
    test_the_ratchet_refuses_a_raise_no_retired_row_covers()
    test_the_ratchet_accepts_a_raise_the_retired_rows_cover()
    test_a_retired_row_that_licenses_nothing_must_lower_the_baseline()
    test_a_retired_row_must_be_an_address_named_export()
    test_an_exported_ram_constant_is_not_counted_as_a_symbol()
    test_the_readme_symbol_figure_that_disagrees_is_caught()
    test_the_readme_symbol_figure_that_agrees_is_not_caught()
    test_a_pair_named_in_the_allowlist_is_cleared()
    test_a_multiline_c_comment_keeps_the_reported_line_numbers()
    test_a_line_comment_marker_inside_a_string_is_not_a_comment()
    test_a_block_comment_marker_inside_a_string_hides_nothing()
    test_an_inline_block_comment_leaves_the_code_on_both_sides()
    test_a_char_literal_holding_a_slash_is_not_a_comment()
    test_a_behaviour_test_row_must_cite_a_test_the_tree_has()
    test_a_row_of_another_class_cites_no_test()
    test_an_entry_allow_row_the_census_does_not_carry_is_caught()
    test_an_entry_allow_row_without_a_flag_or_a_reason_is_caught()
    print("PASS test_lint")
