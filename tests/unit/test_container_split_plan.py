"""The container-split planner's own arithmetic, on synthetic input.

The planner's load-bearing decision is a boundary: a padded record whose trimmed bytes
nobody else reads is repaired in place, and one whose trimmed bytes another record reads is
moved to a new container. That decision is measured against a real image and reported in
`docs/research/FRIEND_V3_WT_SPLIT_CONTAINER.md`; what is checkable without a ROM is the pad
comparison it rests on and the two field ceilings it refuses against.
"""

from __future__ import annotations

from tools.research.plan_friend_v3_container_split import FIRST_FREE_SELECTOR, target_text
from tools.webfoot.handles import (HANDLE_LENGTH_MAX_BYTES, HANDLE_START_MAX_BYTES,
                                   DialogueHandle)


def test_handle_ceilings_are_the_documented_field_widths() -> None:
    assert HANDLE_START_MAX_BYTES == 0x7FFF * 2 == 65534
    assert HANDLE_LENGTH_MAX_BYTES == 0x7FF * 2 == 4094
    packed = DialogueHandle(7, 65534, 4094).encode()
    assert packed >> 21 == 0x7FF
    assert (packed >> 6) & 0x7FFF == 0x7FFF
    assert packed & 0x3F == 7
    assert FIRST_FREE_SELECTOR == 7


def test_target_text_without_a_reference_changes_nothing() -> None:
    assert target_text("Uub    and", None) == "Uub    and"


def test_target_text_reduces_a_pad_run_the_reference_does_not_share() -> None:
    # The measured pad pair from the World Tournament scene: the four-unit pad inside
    # "Uub    and" is the rename's displacement, and the text after the run is what aligns.
    padded = "#Get him, Uub!    You make that boy sorry he ever met you!"
    retail = "#Get him, Trunks! You make that boy sorry he ever met you!"
    assert target_text(padded, retail) == \
        "#Get him, Uub! You make that boy sorry he ever met you!"
    # Where retail has a run of its own, the larger end wins and the run is retail's.
    assert target_text("a  b", "a   b") == "a   b"
