"""WORKBENCH-001 T0.5: the `atlas text` CLI output is unchanged by Wave 0a.

Wave 0a extracted the handle- and text-search logic out of ``cli.py`` into
``atlas.search_text`` / ``handles.recover_handle``. The hard requirement is that
the CLI's rendered output is byte-for-byte identical to before. One flagged
behaviour change needs proving: ``search_text`` now formats ALL hit rows and the
CLI applies ``[:limit]`` afterwards (see ``cli.py`` ``_run_atlas`` ``text``
branch, ``result["runs"] = result["runs"][:args.limit]``), rather than slicing
before formatting.

There is no pre-extraction binary to diff against here (the base ROM commit is
already post-extraction), so a golden capture is committed and asserted against.
The ``--limit 3`` case on a phrase with far more than three hits is the proof: if
the slice order ever regresses, either the retained rows change (breaking the
golden equality) or the reported totals diverge from the sliced list lengths.

ROM-gated: text search needs the assembled atlas artefacts, which are derived
from the canonical ROM, so the test skips cleanly when the fixture is absent,
matching ``tests/integration/test_text_rom.py``.
"""

from __future__ import annotations

import contextlib
import glob
import hashlib
import io
import json
import os
from pathlib import Path

import pytest

from tools.webfoot.cli import main

CANONICAL_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)

#: Fixed search phrase with many more than a small `--limit`'s worth of hits
#: (25 raw + 65 decoded = 90 against the canonical atlas), so the limit-slice is
#: genuinely exercised.
PHRASE = "Goku"
SMALL_LIMIT = 3

GOLDEN = Path(__file__).parent / "goldens" / "atlas_text_goku_limit3.json"


def _atlas_is_present() -> bool:
    return (Path("build") / "atlas" / "atlas.jsonl").is_file()


def _canonical_rom_present() -> bool:
    matches = glob.glob(os.path.join("roms", "*Buu*.gba"))
    if not matches:
        return False
    return (
        hashlib.sha256(open(matches[0], "rb").read()).hexdigest()
        == CANONICAL_SHA256
    )


@pytest.fixture
def fixtures_present() -> None:
    # The atlas is the direct input; the canonical ROM is what it was derived
    # from. Require both, so a stray/mismatched atlas cannot pass silently.
    if not _atlas_is_present():
        pytest.skip("assembled atlas (build/atlas/atlas.jsonl) not present locally")
    if not _canonical_rom_present():
        pytest.skip("canonical Buu's Fury ROM not present locally")


def _run(args: list[str]) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(args)
    return code, buf.getvalue()


def test_atlas_text_output_matches_the_committed_golden(fixtures_present):
    """SC1: `atlas text` for a fixed phrase produces stable, asserted output."""
    code, out = _run(["atlas", "text", PHRASE, "--limit", str(SMALL_LIMIT)])
    assert code == 0
    assert out == GOLDEN.read_text(encoding="utf-8"), (
        "CLI `atlas text` output drifted from the committed golden. If the "
        "extraction changed the output this is a real regression - do not "
        "regenerate the golden to hide it."
    )


def test_the_output_is_deterministic(fixtures_present):
    """A golden is only meaningful if the command is reproducible."""
    _, first = _run(["atlas", "text", PHRASE, "--limit", str(SMALL_LIMIT)])
    _, second = _run(["atlas", "text", PHRASE, "--limit", str(SMALL_LIMIT)])
    assert first == second


def test_limit_slices_after_formatting_not_before(fixtures_present):
    """SC2: the format-then-slice change preserved output.

    The proof that the slice order is right: with a `--limit` far below the hit
    count, the reported `matched` total is the FULL count (formatting/counting
    happened over every hit), while `runs`/`decoded` are exactly the first
    `limit` of those fully-formatted rows. A regression that sliced before
    formatting would collapse `matched` to the limit, or retain different rows.
    """
    _, limited_raw = _run(["atlas", "text", PHRASE, "--limit", str(SMALL_LIMIT)])
    _, full_raw = _run(["atlas", "text", PHRASE, "--limit", "100000"])
    limited = json.loads(limited_raw)
    full = json.loads(full_raw)

    # More hits exist than the small limit, so the slice is actually exercised.
    assert full["matched"] > SMALL_LIMIT
    assert full["raw_matched"] > SMALL_LIMIT
    assert full["decoded_matched"] > SMALL_LIMIT

    # Counts survive the slice unchanged: they are over all hits, not the page.
    assert limited["matched"] == full["matched"]
    assert limited["raw_matched"] == full["raw_matched"]
    assert limited["decoded_matched"] == full["decoded_matched"]

    # The retained rows are the FIRST `limit` of the fully-formatted rows.
    assert len(limited["runs"]) == SMALL_LIMIT
    assert len(limited["decoded"]) == SMALL_LIMIT
    assert limited["runs"] == full["runs"][:SMALL_LIMIT]
    assert limited["decoded"] == full["decoded"][:SMALL_LIMIT]
