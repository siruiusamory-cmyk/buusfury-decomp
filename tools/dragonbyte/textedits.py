"""The authored string table, as one reversible journal payload.

The Scripts & Text destination edits `text/strings.toml`, which the project model
already owns: `webfoot.build.extract_project` writes it and
`webfoot.project.read_project` reads it back. This module is the journal's adapter
for it and is deliberately thin, because there is exactly one authored
representation of the string table and it belongs to `webfoot.project`:

* `read` snapshots the project's own `strings` mapping;
* `install` puts a snapshot back, so undo and redo are the two operations the
  dialogue adapter already uses;
* `write` calls the SDK's one project writer with the argument shape
  `webfoot.build.extract_project` passes it for text.

**One target, and it is NOT the dialogue target.** The project holds two authored
text documents reaching two independent systems in the image:
`text/strings.toml` (menu, quest, item, bio and map-name text, identified by
pointer-table slot) and `dialogue/replacements.toml` (spoken dialogue, identified
by packed handle). They are registered under separate targets because the journal
writes one payload per target on Save: sharing one target would let a string edit
overwrite a spoken-dialogue replacement in the same save.

No Qt is imported: the adapter is drivable from a headless test.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Mapping

from tools.webfoot.formats import stat_tables as st
from tools.webfoot.formats import text_tables as tt
from tools.webfoot.project import ProjectMeta, StatProject, write_project

from .dataedits import _character_records, _enemy_records, _map_records

#: The journal target the authored string table is committed under. One target
#: for the one document, and never the dialogue target.
TEXT_TARGET = "textstrings"


class TextEditError(ValueError):
    """A string edit was refused; the message says which slot and why."""


@dataclass(frozen=True, slots=True)
class AuthoredStrings:
    """The project's authored string table, as one value.

    The mapping is held as it is read: a slot identity to the text the project
    authors for it. No address, offset or stride is stored, because all three are
    facts about today's image rather than about the record.

    The four other authored documents are carried because the SDK's one project
    writer writes the whole tree. They are passed through untouched, which is what
    keeps a string edit from dropping a dialogue replacement or a stat record.
    """

    meta: ProjectMeta
    strings: Mapping[tt.TextIdentity, str]
    enemies: Mapping[st.StatIdentity, Mapping[str, Any]]
    characters: Mapping[st.StatIdentity, Mapping[str, Any]]
    maps: Mapping[int, Mapping[str, Any]]
    dialogues: Mapping[str, str]

    @property
    def record_count(self) -> int:
        return len(self.strings)


def read(project: StatProject) -> AuthoredStrings:
    """Snapshot the string document a project holds, with the tables it carries."""
    return AuthoredStrings(
        meta=project.meta,
        strings=dict(project.strings),
        enemies=dict(project.enemies),
        characters=dict(project.characters),
        maps=dict(project.maps),
        dialogues=dict(project.dialogues),
    )


def install(project: StatProject, payload: object) -> StatProject:
    """The project with `payload`'s string table, and every other document kept."""
    authored = _require_payload(payload)
    return replace(project, strings=dict(authored.strings))


def validate(project: StatProject, payload: object) -> None:
    """Refuse a payload that is not this project's own string document.

    The identity check is the load-bearing one: `install` replaces `meta`, so a
    payload carrying another project's meta would move the session's own authority
    half way through an edit. Whether a given string is encodable depends on the
    image, which only the surface holds, so that check stays there.
    """
    authored = _require_payload(payload)
    if authored.meta != project.meta:
        raise TextEditError(
            "a string edit must carry the project's own identity; this payload names "
            f"{authored.meta.name!r} against {project.meta.name!r}"
        )
    for identity in authored.strings:
        if not isinstance(identity, tt.TextIdentity):
            raise TextEditError(
                "a string edit is keyed by the pointer-table slot it names; "
                f"{identity!r} is not a text identity"
            )


def write(directory: object, payload: object) -> None:
    """Persist the string table through the SDK's one project writer.

    The whole authored tree is passed, exactly as the data adapter passes it,
    because `write_project` writes every document it is handed and a second
    caller writing this project must not drop a document another adapter writes.
    """
    authored = _require_payload(payload)
    write_project(
        Path(directory),
        authored.meta,
        enemies=_enemy_records(authored.enemies),
        characters=_character_records(authored.characters),
        maps=_map_records(authored.maps),
        strings=_string_records(authored.strings),
        dialogues=dict(authored.dialogues),
    )


def _require_payload(payload: object) -> AuthoredStrings:
    if not isinstance(payload, AuthoredStrings):
        raise TextEditError("a string edit carries the project's authored string table.")
    return payload


def _string_records(
    strings: Mapping[tt.TextIdentity, str],
) -> list[tuple[tt.TextIdentity, str]]:
    """The writer's own `strings` argument, ordered by durable identity."""
    return [
        (identity, strings[identity])
        for identity in sorted(strings, key=lambda item: item.index)
    ]


__all__ = [
    "TEXT_TARGET",
    "AuthoredStrings",
    "TextEditError",
    "install",
    "read",
    "validate",
    "write",
]
