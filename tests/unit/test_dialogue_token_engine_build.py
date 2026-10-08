"""The token engine builder may never write its own source image.

DIALOGUE-TOKEN-PRODUCTIZATION-001. The first candidate's guard compared resolved
paths, which cannot see a hard-link alias; the second staged through a predictable
`<destination>.partial` name, which an alias could also occupy. Both are
regression cases here.

The guard runs before the source is read or parsed, so these tests need no image:
any file will do, and the refusal is asserted on the message the repository's own
alias rule produces.
"""

from __future__ import annotations

import os

import pytest

from tools.research.build_dialogue_token_engine import patch


def test_refuses_a_destination_that_is_the_source(tmp_path) -> None:
    source = tmp_path / "image.gba"
    source.write_bytes(b"an image")
    with pytest.raises(SystemExit, match="input image"):
        patch(source, source, "unused")
    assert source.read_bytes() == b"an image"


def test_refuses_a_hard_link_alias_of_the_source(tmp_path) -> None:
    source = tmp_path / "image.gba"
    source.write_bytes(b"an image")
    alias = tmp_path / "alias.gba"
    try:
        os.link(source, alias)
    except OSError:
        pytest.skip("this filesystem cannot make a hard link")
    with pytest.raises(SystemExit, match="input image"):
        patch(source, alias, "unused")
    assert source.read_bytes() == b"an image"


def test_refuses_a_destination_reached_through_a_relative_spelling(tmp_path) -> None:
    source = tmp_path / "image.gba"
    source.write_bytes(b"an image")
    spelled = tmp_path / "." / "image.gba"
    with pytest.raises(SystemExit, match="input image"):
        patch(source, spelled, "unused")
    assert source.read_bytes() == b"an image"
