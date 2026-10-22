from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import name


def test_a_house_label_is_replaced_whatever_case_the_reference_uses():
    text = "INCLUDE loc_08009220.s\n    BL |loc_08009220|\n|LOC_08009220|\n"
    assert name.rename_text(text, "loc_08009220", "Object_RebuildSlots1") == \
        "INCLUDE Object_RebuildSlots1.s\n    BL |Object_RebuildSlots1|\n|Object_RebuildSlots1|\n"


def test_a_name_that_shares_a_prefix_is_not_replaced():
    text = "|sub_08000158| and |sub_080001580|\n"
    assert name.rename_text(text, "sub_08000158", "List_Append") == \
        "|List_Append| and |sub_080001580|\n"


def test_only_house_forms_are_promoted_and_a_module_verb_matches():
    assert name.HOUSE.match("sub_0803E5AC")
    assert name.HOUSE.match("loc_0803E5AC")
    assert not name.HOUSE.match("Object_AdvanceTimer1")
    assert name.lints.FUNCTION_NAME.match("Object_AdvanceTimer1")
