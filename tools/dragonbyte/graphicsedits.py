"""The authored object-palette overrides, as one reversible journal payload.

The Graphics destination edits `graphics/overrides.toml`, the one graphics
document the project model already authors: a palette index to an RGB triple.
This module is the journal's adapter for it and is deliberately thin, because
there is exactly one authored representation of a palette recolour and it belongs
to `webfoot.project`:

* `read` snapshots the project's own `graphics_overrides.palette`;
* `install` puts a snapshot back, so undo and redo are the two operations the
  dialogue, data, maps and text adapters already use;
* `write` calls the SDK's own narrow writer, `write_graphics_overrides`, which is
  the one place this document reaches disk. An emptied palette removes the file
  rather than writing a table the reader would refuse.

**Why the payload is the palette and not the pixels.** The document carries only
palette overrides. The pixel half of `GraphicsOverrides` is DERIVED, from the
project's own PNGs against the baseline the extracted manifest recorded
(`webfoot.project.model.GraphicsOverrides`), so it is not a document any adapter
could write back: `webfoot.graphics_authoring.resolve_pixel_overrides` re-derives
it on every validate and every build. A payload that claimed to author pixels
would be a second statement of something the PNG already says.

Building a palette-only project is safe for that reason rather than by luck:
`webfoot.build` re-derives the pixel half itself from the project directory, so
dropping the in-memory derived field changes nothing about what a build emits.

No Qt is imported: the adapter is drivable from a headless test.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Mapping

from tools.webfoot.project import (
    GraphicsOverrides,
    ProjectMeta,
    StatProject,
    write_graphics_overrides,
)

#: The journal target the authored object-palette overrides are committed under.
#: One target for the one graphics document, and never the "graphics_authoring"
#: allocation domain name, which is a build concept rather than a document.
GRAPHICS_TARGET = "graphics"

#: The object palette's extent. Stated here as the authored document's own bound,
#: and checked against the SDK's own document reader, which refuses an index
#: outside it.
PALETTE_ENTRIES = 256


class GraphicsEditError(ValueError):
    """A palette edit was refused; the message says which entry and why."""


@dataclass(frozen=True, slots=True)
class AuthoredPalette:
    """The project's authored palette overrides, as one value.

    The mapping is held as it is read: a palette index to an RGB triple, each
    channel 0..255. No packed GBA word and no address is stored, because the
    SDK owns the RGB-to-word packing and an address is a fact about today's
    image rather than about the entry.
    """

    meta: ProjectMeta
    palette: Mapping[int, tuple[int, int, int]]

    @property
    def entry_count(self) -> int:
        return len(self.palette)


def read(project: StatProject) -> AuthoredPalette:
    """Snapshot the palette document a project holds."""
    return AuthoredPalette(
        meta=project.meta,
        palette=dict(project.graphics_overrides.palette),
    )


def install(project: StatProject, payload: object) -> StatProject:
    """The project with `payload`'s palette, and every other document kept.

    The derived pixel half is carried through untouched rather than rebuilt: it
    is not this payload's to change, and rebuilding it here would drop what the
    project directory says.
    """
    authored = _require_payload(payload)
    return replace(
        project,
        graphics_overrides=replace(
            project.graphics_overrides, palette=dict(authored.palette)
        ),
    )


def validate(project: StatProject, payload: object) -> None:
    """Refuse a payload that is not this project's own palette document.

    The identity check is the load-bearing one: `install` replaces the project's
    graphics document, so a payload carrying another project's meta would move
    the session's own authority half way through an edit. The entry checks are
    the SDK document reader's own, so an entry that this would write is one
    `read_project` will read back.
    """
    authored = _require_payload(payload)
    if authored.meta != project.meta:
        raise GraphicsEditError(
            "a palette edit must carry the project's own identity; this payload "
            f"names {authored.meta.name!r} against {project.meta.name!r}"
        )
    for index, rgb in authored.palette.items():
        if type(index) is not int or not 0 <= index < PALETTE_ENTRIES:
            raise GraphicsEditError(
                f"palette index {index!r} is outside 0..{PALETTE_ENTRIES - 1}"
            )
        if not isinstance(rgb, tuple) or len(rgb) != 3:
            raise GraphicsEditError(
                f"palette entry {index:03d} carries {rgb!r}, not three channels"
            )
        for channel in rgb:
            if type(channel) is not int or not 0 <= channel <= 255:
                raise GraphicsEditError(
                    f"palette entry {index:03d} has channel {channel!r}, which is "
                    "outside 0..255"
                )


def write(directory: object, payload: object) -> None:
    """Persist the palette overrides through the SDK's own narrow writer."""
    authored = _require_payload(payload)
    write_graphics_overrides(Path(directory), authored.palette)


def _require_payload(payload: object) -> AuthoredPalette:
    if not isinstance(payload, AuthoredPalette):
        raise GraphicsEditError(
            "a palette edit carries the project's authored graphics overrides."
        )
    return payload


__all__ = [
    "GRAPHICS_TARGET",
    "PALETTE_ENTRIES",
    "AuthoredPalette",
    "GraphicsEditError",
    "install",
    "read",
    "validate",
    "write",
]
