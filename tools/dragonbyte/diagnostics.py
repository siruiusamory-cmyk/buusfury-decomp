"""What to tell a user, or a bug report, about the state of this window.

One line per fact, in a fixed order, so the same session always produces the
same text and two reports can be compared. The release identity comes from its
one authority; nothing here restates a version, a path convention or a support
rule.

No Qt: the About surface formats this text, it does not own it.
"""

from __future__ import annotations

from tools.webfoot.release_identity import release_identity

from .destination import Destination
from .session import Session


def release_line() -> str:
    """The product and version, from the identity authority."""
    return f"Release: {release_identity().display}"


def diagnostics_text(
    session: Session,
    destination: Destination | None,
    status: str = "",
) -> str:
    """The window's state as one ``Label: value`` line per fact.

    ``destination`` is the active destination, or None before one is chosen.
    ``status`` is the last message the window showed - a refusal's reason, or a
    result - or empty for "this session has nothing to report".
    """
    if destination is None:
        active = "none"
    else:
        active = f"{destination.label} ({destination.id})"
    rom = "open" if session.has_rom else "not open"
    project = "open" if session.has_project else "not open"
    return "\n".join(
        (
            release_line(),
            f"ROM identity: {session.rom_identity}",
            f"Project identity: {session.project_identity}",
            f"Active destination: {active}",
            f"Session state: ROM {rom}, project {project}",
            f"Support: {status or 'none'}",
        )
    )
