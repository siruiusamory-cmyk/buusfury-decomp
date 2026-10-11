"""The dialogue portrait operand's thresholds, pinned.

These three branches are the whole meaning of the census: they decide how thousands of lines are
grouped, so a silent edit of a boundary would change the text tool's speaker grouping without any
record changing.
"""

from __future__ import annotations

from tools.research.dialogue_portrait_census import classify_operand


def test_the_operand_classes_are_the_consumers_branches() -> None:
    assert classify_operand(0) == "none", "0 takes the r1 = 0 branch: no portrait at all"
    assert classify_operand(7) == "none", "7 takes the same branch as 0"
    for value in range(1, 7):
        assert classify_operand(value) == "party", "1..6 go through the save/party byte"
    for value in (8, 79, 137, 162):
        assert classify_operand(value) == "array", "8 and above index the portrait array"
