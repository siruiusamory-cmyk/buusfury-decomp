"""The verifier's oracle: what a record must hold, built from the substitution regions.

DIALOGUE-TOKEN-PRODUCTIZATION-001. `expected_text` is the piece of the verifier that
has been wrong twice - first by skipping a region whose substituted name ran past the
record's end instead of clipping it, then by applying the same substitution twice when
two overlapping records described it - and neither mistake needed an image to make or
to catch. These tests are pure string arithmetic.

The unit/byte mix-up that reported 66 correct records as changed lived in `main`,
where a container offset is divided by two, and is NOT covered here: it needs an image
to exercise. These tests cover the arithmetic only.

The strings here are STORED text, not visible text: a replacement is exactly as many
units as the region it replaces, which is the property the whole rename method rests
on, so every replacement below is the same length as its region.
"""

from __future__ import annotations

from tools.research.verify_token_splice import expected_text


def test_a_region_inside_the_span_replaces_exactly_that_much() -> None:
    # Four units in, four units out: the stored form of a rename that keeps the span.
    assert expected_text("Goku went home", 0, [(0, 4, "Yamc")]) == "Yamc went home"


def test_a_region_is_placed_by_its_absolute_position() -> None:
    # The span starts at unit 100 of the container, so a region at 105 is at unit 5.
    assert expected_text("Goku went home", 100, [(105, 4, "Yamc")]) == "Goku Yamc home"


def test_a_region_running_past_the_end_is_clipped_not_skipped() -> None:
    """The span ends inside the substituted name, so it keeps the part that fits.

    Skipping instead reported three correct records as changed. The replacement is six
    units for a six-unit region; the span holds four of them.
    """
    assert expected_text("Goku", 0, [(0, 6, "Yamcha")]) == "Yamc"


def test_a_region_starting_before_the_span_is_clipped_at_the_front() -> None:
    # A six-unit region at absolute 4 covers 4..10. The span starts at 6, so it takes
    # replacement[2:6] = "mcha" over its own units 0..4, which hold "ku w".
    assert expected_text("ku went home", 6, [(4, 6, "Yamcha")]) == "mchaent home"


def test_a_region_outside_the_span_changes_nothing() -> None:
    assert expected_text("Goku", 500, [(0, 4, "Yamc")]) == "Goku"
    assert expected_text("Goku", 0, [(20, 4, "Yamc")]) == "Goku"


def test_the_same_region_twice_is_applied_once() -> None:
    """Overlapping retail records describe the same bytes, so one arrives twice."""
    assert expected_text("Goku went home", 0, [(0, 4, "Yamc"), (0, 4, "Yamc")]) == \
        "Yamc went home"


def test_regions_apply_in_position_order_to_a_longer_text() -> None:
    text = "Goku met Gohan by the river"
    regions = [(0, 4, "Yamc"), (9, 5, "Krill")]
    assert expected_text(text, 0, regions) == "Yamc met Krill by the river"
