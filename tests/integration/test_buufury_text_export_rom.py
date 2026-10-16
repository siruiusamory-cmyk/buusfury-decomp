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


def key_parts(key: str) -> tuple[int, int, int]:
    selector, start, length = (int(part) for part in key.split(":"))
    return selector, start, length


def a_retail_matching_word(session) -> tuple[str, str, int] | None:
    """A word in a spoken line that the retail reference attributes to the actor.

    The row is a LINE, so the offset the rename needs is the one inside that line,
    while `rename_hits` reports offsets inside the RECORD that carries it. The swap
    is therefore accepted only where the retail test itself decides to rename that
    occurrence, rather than where this test guesses it should. The line has to read
    as prose, or the swap lands on one of the short fragments these containers also
    carry and proves the mechanics without proving the workflow.
    """
    for line in session.lines:
        if line.kind != "record" or not line.proven or len(line.text) < 30:
            continue
        if line.text.count(" ") < 3:
            continue
        holder = session.model.record(*key_parts(line.target))
        if holder is None or holder.start > line.position[1]:
            continue
        offset = (line.position[1] - holder.start) // 2
        # A capitalised word, so the swap is a name swap of the release-3.1 kind
        # rather than any word that happens to match.
        for match in re.finditer(r"[A-Z][a-z]{3,}", line.text):
            word = match.group(0)
            wanted = offset + match.start()
            if any(hit.key == line.target and hit.at == wanted
                   and hit.decision == textedit.RENAME
                   for hit in session.rename_hits(word)):
                return line.key, word, match.start()
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
    # A name strictly longer than the one it replaces, which is the shape of the
    # release-3.1 rename: the line no longer fits its span and has to move.
    swapped = "Kakarotto" if len(old) < 9 else old + "!"
    assert len(swapped) > len(old)
    renamed = session.rename_text(key, old, swapped, frozenset({at}))
    assert renamed != session.line(key).text
    session.set_edit(key, renamed)

    # One dialogue line grown past its span, which is the route the window calls
    # the mover. It must be a line in a DIFFERENT record, or the second edit would
    # replace the first: an edit list is one entry per record, not per row.
    grower = next(line for line in session.lines
                  if line.kind == "record" and line.key != key
                  and line.target != session.line(key).target
                  and len(line.text) > 20)
    session.set_edit(grower.key, grower.text + " and friends")

    assert session.state(key) is app_session.State.WILL_MOVE
    assert session.state(grower.key) is app_session.State.WILL_MOVE
    assert session.refusals() == ()
    assert len(session.edited_keys()) == 2

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
