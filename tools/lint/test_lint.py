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
ASM_CONSTANT = "unk_03003014    EQU     0x03003014\n\tEXPORT  unk_03003014\n"
README_SYMBOL_LINE = MEASURED_PROGRESS + " 6,739 of the 6,740 symbols"


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


def test_the_ratchet_refuses_a_count_above_the_baseline():
    assert lints.ratchet_findings(10, 9)


def test_the_ratchet_refuses_a_count_below_an_unlowered_baseline():
    assert lints.ratchet_findings(8, 9)


def test_the_ratchet_accepts_the_count_the_baseline_holds():
    assert not lints.ratchet_findings(9, 9)


def test_an_exported_ram_constant_is_not_counted_as_a_symbol():
    assert lints.symbol_counts(exported(ASM_CONSTANT), {"unk_03003014"}) == (0, 0)


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
    test_the_ratchet_refuses_a_count_above_the_baseline()
    test_the_ratchet_refuses_a_count_below_an_unlowered_baseline()
    test_the_ratchet_accepts_the_count_the_baseline_holds()
    test_an_exported_ram_constant_is_not_counted_as_a_symbol()
    test_the_readme_symbol_figure_that_disagrees_is_caught()
    test_the_readme_symbol_figure_that_agrees_is_not_caught()
    test_a_pair_named_in_the_allowlist_is_cleared()
    test_a_multiline_c_comment_keeps_the_reported_line_numbers()
    test_a_line_comment_marker_inside_a_string_is_not_a_comment()
    test_a_block_comment_marker_inside_a_string_hides_nothing()
    test_an_inline_block_comment_leaves_the_code_on_both_sides()
    test_a_char_literal_holding_a_slash_is_not_a_comment()
    print("PASS test_lint")
