"""Drive a real startup and report what opened, so a packaged build is provable.

This is the product half of the packaging acceptance: a frozen executable that is
never asked to do its job is not evidence that it can. The randomizers answer this
with a ``--smoke`` entry that runs the real worker through the real window, and
this is the same answer for an editor - a real ``Session``, the real project
reader, the real ROM identification, reporting what opened as JSON.

Why JSON and not stdout: the frozen build is windowed, so it has no console to
print to. A file the caller named is the channel that survives, and it is the one
:mod:`tests.unit.test_dragonbyte_release` reads.
"""

from __future__ import annotations

import json
from pathlib import Path

from tools.webfoot.release_identity import identity_document

from .session import Session, SessionError

#: The report schema. Bumped when a reader would have to notice a change.
SMOKE_SCHEMA = 1


def run_smoke(project: Path, rom: Path | None, report: Path) -> int:
    """Open a project (and an image, when one is named) and write what opened.

    Returns 0 only when the report was written. A refusal is written into the
    report as well as returned, because a caller reading the exit code cannot see
    which of the three opens failed, and a smoke run that reports "it did not work"
    without saying what it asked is not worth the run.
    """
    session = Session()
    document: dict = {
        "schema_version": SMOKE_SCHEMA,
        "identity": identity_document(),
        "project": {"path": str(project), "opened": False, "name": None},
        "rom": {"path": None if rom is None else str(rom), "opened": False},
        "error": None,
    }
    status = 0
    try:
        session.open_project(Path(project))
        document["project"]["opened"] = True
        document["project"]["name"] = session.project.meta.name
        if rom is not None:
            session.open_rom(Path(rom))
            document["rom"]["opened"] = True
            document["rom"]["sha256"] = session.identification.hashes.sha256
    except SessionError as exc:
        document["error"] = str(exc)
        status = 1
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return status
