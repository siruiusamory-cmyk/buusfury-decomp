"""Atomic replacement of a project document.

N-08. A project document is replaced as a whole or not at all: the new text is
written to a sibling temporary file, flushed and synced, and only then moved
over the destination with ``os.replace``. An interrupted or failed write leaves
the previous document byte-identical instead of truncated, and ``os.replace``
never removes the destination first, so the file is never absent.

The text is encoded as UTF-8 and written in binary. Every project writer passes
``newline="\\n"``, under which CPython translates nothing, so this is
byte-identical to the ``write_text`` call it replaces - and it cannot acquire
the platform's CRLF translation on the way out.
"""

import os
import tempfile
from pathlib import Path


def _document_mode(destination: Path) -> int:
    """The mode a plain ``write_text`` would have given the destination."""
    try:
        return destination.stat().st_mode & 0o777
    except OSError:
        umask = os.umask(0)
        os.umask(umask)
        return 0o666 & ~umask


def replace_document(path: str | Path, text: str) -> Path:
    """Write ``text`` to ``path``, atomically replacing any existing file."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    # A process that dies between the temp write and the replace leaves one
    # .webfoot-partial sibling behind. read_project loads exact names, so the
    # orphan is ignored; sweep them only if such files ever accumulate.
    handle, temporary = tempfile.mkstemp(
        dir=destination.parent,
        prefix=f".{destination.name}.",
        suffix=".webfoot-partial",
    )
    try:
        # mkstemp creates 0600; a project document keeps the mode a plain write
        # would have given it, so a shareable 0644 file does not become private.
        os.chmod(temporary, _document_mode(destination))
        with os.fdopen(handle, "wb") as stream:
            stream.write(text.encode("utf-8"))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return destination
