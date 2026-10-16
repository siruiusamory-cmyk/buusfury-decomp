"""The F3 guard on the DragonByte acceptance loader seam.

TEST-SPEED-003. `dragonbyte_acceptance_support` replaces five destination
loaders with one module decode, so a read of a second image would otherwise
silently receive the first one's surfaces. These cases drive the replacement
loader the page really calls, and prove it refuses a read of any other image
while answering a read of the one it was decoded from.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from tests.unit.dragonbyte_acceptance_support import check_image, replacement_loader

CANONICAL = b"the canonical image"
SECOND = b"a second image"


def _surfaces(image: bytes) -> SimpleNamespace:
    return SimpleNamespace(image=image, graphics="the graphics surfaces")


def test_check_image_accepts_the_image_the_surfaces_came_from():
    check_image(_surfaces(CANONICAL), CANONICAL)


def test_check_image_refuses_a_different_image():
    with pytest.raises(AssertionError, match="different image"):
        check_image(_surfaces(CANONICAL), SECOND)


def test_check_image_refuses_a_call_that_names_no_image():
    with pytest.raises(AssertionError, match="different image"):
        check_image(_surfaces(CANONICAL), None)


def test_the_graphics_loader_answers_the_image_it_was_installed_for():
    """Graphics takes three arguments and holds the image in the third."""
    loader = replacement_loader(_surfaces(CANONICAL), "graphics", 2)

    assert loader("identification", "profile", CANONICAL) == "the graphics surfaces"


def test_the_graphics_loader_refuses_a_second_image():
    loader = replacement_loader(_surfaces(CANONICAL), "graphics", 2)

    with pytest.raises(AssertionError, match="different image"):
        loader("identification", "profile", SECOND)


def test_a_five_argument_loader_refuses_a_second_image():
    """The other four loaders hold the image in the fifth argument."""
    surfaces = SimpleNamespace(image=CANONICAL, data="the data surfaces")
    loader = replacement_loader(surfaces, "data", 4)

    assert loader("rom", "catalog", "id", "profile", CANONICAL) == "the data surfaces"
    with pytest.raises(AssertionError, match="different image"):
        loader("rom", "catalog", "id", "profile", SECOND)
