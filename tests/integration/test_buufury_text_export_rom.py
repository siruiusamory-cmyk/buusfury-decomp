"""The app's export path on release 3.1: a name swap and a grown line.

ROM-gated. It drives the same `Session` the window drives, so what it proves is the
path a user takes and not a private route: open the release, find a name swap the
retail reference permits, grow one dialogue line, export, and let the engine's own
readback and staged write decide whether it worked.

Skipped, never failed, when the release or the canonical image is not staged.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

from tests.gates import REPOSITORY_ROOT
from tests.rom_support import canonical_rom_path
from tools.buufury_text import session as app_session
from tools.webfoot import textedit

#: The published release 3.1 image. Its digest is pinned so a different file that
#: happens to share the name cannot stand in for it.
RELEASE31 = "f5c9648bbf7a9b448d801866cc775eb76abd270f7c16fb93d4e01630ef236201"
RELEASE31_NAME = "v3-release31.gba"


def staged(name: str) -> Path:
    path = Path(REPOSITORY_ROOT) / "roms" / name
    if not path.is_file():
        pytest.skip(f"{name} is not staged under roms/")
    return path


def a_retail_matching_word(session) -> tuple[str, str, int] | None:
    """A word the release and the original game both say at the same offset.

    That is exactly the condition the per-occurrence rule tests, so the swap this
    finds is one the retail reference attributes to the actor rather than one this
    test guessed at. The line has to read as prose, or the swap lands on one of the
    short fragments these containers also carry and proves the mechanics without
    proving the workflow.
    """
    for line in session.lines:
        if line.kind != "record" or line.retail is None:
            continue
        if len(line.text) != len(line.retail) or len(line.text) < 30:
            continue
        if line.text.count(" ") < 3:
            continue
        for match in re.finditer(r"[A-Za-z]{4,}", line.text):
            at, end = match.span()
            if line.retail[at:end] == line.text[at:end]:
                return line.key, line.text[at:end], at
    return None


def test_a_name_swap_and_a_grown_line_export_and_read_back(tmp_path: Path) -> None:
    release = staged(RELEASE31_NAME)
    if hashlib.sha256(release.read_bytes()).hexdigest() != RELEASE31:
        pytest.skip("the staged release 3.1 is not the published one")
    canonical = canonical_rom_path()
    if canonical is None:
        pytest.skip("canonical Buu's Fury ROM not present locally")

    session = app_session.open_image(release, canonical=canonical)
    assert session.model.retail_streams

    # A name swap of the release-3.1 kind: the retail reference decides, per
    # occurrence, whether the actor at that offset is the one being renamed.
    found = a_retail_matching_word(session)
    assert found is not None, "release 3.1 has no retail-attributable word to swap"
    key, old, at = found
    hit = next(item for item in session.rename_hits(old)
               if item.key == key and item.at == at)
    assert hit.decision == textedit.RENAME
    # A name strictly longer than the one it replaces, which is the shape of the
    # release-3.1 rename: the line no longer fits its span and has to move.
    swapped = "Kakarotto" if len(old) < 9 else old + "!"
    assert len(swapped) > len(old)
    renamed = session.rename_text(key, old, swapped, frozenset({at}))
    assert renamed != session.line(key).text
    session.set_edit(key, renamed)

    # One dialogue line grown past its span, which is the route the window calls
    # the mover.
    grower = next(line for line in session.lines
                  if line.kind == "record" and line.key != key and len(line.text) > 20)
    session.set_edit(grower.key, grower.text + " and friends")

    assert session.state(key) is app_session.State.WILL_MOVE
    assert session.state(grower.key) is app_session.State.WILL_MOVE
    assert session.refusals() == ()

    plan = session.plan()
    assert plan is not None
    assert textedit.readback(plan) == ()

    target = tmp_path / "release31-edited.gba"
    report = session.export(target)
    written = target.read_bytes()
    assert len(written) > len(release.read_bytes())
    assert hashlib.sha256(written).hexdigest() == report["output_sha256"]
    assert report["moved"] == 2
    assert report["refused"] == 0
    assert release.read_bytes() != written
    # The input is untouched: same digest after the export as the pinned one.
    assert hashlib.sha256(release.read_bytes()).hexdigest() == RELEASE31

    print(f"exported {report['moved']} moved, {report['in_place']} in place, "
          f"sha256 {report['output_sha256']}")
