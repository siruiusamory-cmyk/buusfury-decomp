"""The authored data documents, as one reversible journal payload.

The Data destination edits three tables that the project model already authors:
`enemies/enemies.toml`, `characters/characters.toml` and `maps/maps.toml`. This
module is the journal's adapter for them, and it is deliberately thin, because
there is exactly one authored representation of these records and it belongs to
`webfoot.project`. Nothing here parses, encodes or defines a document:

* `read` snapshots the project's own three mappings;
* `install` puts a snapshot back, so undo and redo are the same two operations
  the dialogues adapter uses;
* `write` calls the SDK's one project writer with the argument shapes
  `webfoot.build.extract_project` itself passes it. `_map_records` adds the two
  keys the project keeps as its outer mapping's key, and reconstructs nothing
  else;
* the field vocabularies come from `webfoot.stats` and `webfoot.maps`, which are
  the modules that own the names, so a rename there cannot drift from here.

No Qt is imported: the adapter is drivable from a headless test.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Mapping

from tools.webfoot import stats as stats_mod
from tools.webfoot.formats import stat_tables as st
from tools.webfoot.project import (
    ProjectMeta,
    StatProject,
    write_project,
)

#: The journal target the data documents are committed under. One target for the
#: three tables: they are one authored subsystem and one file set, and a second
#: target would give a user two undos for one gesture.
DATA_TARGET = "data"


class DataEditError(ValueError):
    """A data edit was refused; the message says which document and why."""


@dataclass(frozen=True, slots=True)
class AuthoredData:
    """The project's authored data documents, as one value.

    The mappings are held as they are read: the record dicts use exactly the
    field names `webfoot.project` reads and writes, and no address, offset or
    stride is stored, because all three are facts about today's image rather
    than about the record.
    """

    meta: ProjectMeta
    enemies: Mapping[st.StatIdentity, Mapping[str, Any]]
    characters: Mapping[st.StatIdentity, Mapping[str, Any]]
    maps: Mapping[int, Mapping[str, Any]]

    @property
    def record_count(self) -> int:
        return len(self.enemies) + len(self.characters) + len(self.maps)


def read(project: StatProject) -> AuthoredData:
    """Snapshot the data documents a project holds."""
    return AuthoredData(
        meta=project.meta,
        enemies=dict(project.enemies),
        characters=dict(project.characters),
        maps=dict(project.maps),
    )


def install(project: StatProject, payload: object) -> StatProject:
    """The project with `payload`'s data documents, and every other document kept."""
    data = _require_payload(payload)
    return replace(
        project,
        enemies=dict(data.enemies),
        characters=dict(data.characters),
        maps=dict(data.maps),
    )


def validate(project: StatProject, payload: object) -> None:
    """Refuse a payload that is not this project's own data documents.

    The identity check is the load-bearing one: `install` replaces `meta`, so a
    payload carrying another project's meta would move the session's own
    authority half way through an edit.
    """
    data = _require_payload(payload)
    if data.meta != project.meta:
        raise DataEditError(
            "a data edit must carry the project's own identity; this payload names "
            f"{data.meta.name!r} against {project.meta.name!r}"
        )
    for label, table in (
        ("enemies", data.enemies),
        ("characters", data.characters),
        ("maps", data.maps),
    ):
        if not isinstance(table, Mapping):
            raise DataEditError(f"the authored {label} document must be a mapping")


def write(directory: object, payload: object) -> None:
    """Persist the data documents through the SDK's one project writer."""
    data = _require_payload(payload)
    write_project(
        Path(directory),
        data.meta,
        enemies=_enemy_records(data.enemies),
        characters=_character_records(data.characters),
        maps=_map_records(data.maps),
    )


def _require_payload(payload: object) -> AuthoredData:
    if not isinstance(payload, AuthoredData):
        raise DataEditError(
            "a data edit carries the project's authored data documents."
        )
    return payload


def _enemy_records(
    enemies: Mapping[st.StatIdentity, Mapping[str, Any]],
) -> list[tuple[st.StatIdentity, st.EnemyRecord, bytes, str | None]]:
    """The writer's own enemy argument, from the authored documents.

    `EnemyRecord.offset` is the provenance of a *decoded* record; a record
    authored from a project has no image address, and `write_project` reads
    every field of the record except this one.
    """
    return [
        (
            identity,
            st.EnemyRecord(
                offset=0,
                type_id=int(values["type_id"]),
                **{name: int(values[name]) for name in stats_mod.ENEMY_FIELDS},
            ),
            bytes(values["raw"]),
            values.get("alias"),
        )
        for identity, values in sorted(enemies.items(), key=lambda item: item[0].key)
    ]


def _character_records(
    characters: Mapping[st.StatIdentity, Mapping[str, Any]],
) -> list[tuple[st.StatIdentity, st.BaseStatRecord, bytes, str]]:
    return [
        (
            identity,
            st.BaseStatRecord(
                offset=0,
                person=int(values["person"]),
                technique_count=int(values["technique_count"]),
                **{name: int(values[name]) for name in stats_mod.CHARACTER_FIELDS},
            ),
            bytes(values["raw"]),
            str(values["alias"]),
        )
        for identity, values in sorted(characters.items(), key=lambda item: item[0].key)
    ]


def _map_records(maps: Mapping[int, Mapping[str, Any]]) -> list[dict[str, Any]]:
    """The writer's own map argument.

    A project keys its map documents by the table index, because that is the
    identity; the writer's argument carries that index and the identity key
    inside the record. This adds back the two keys the outer mapping already
    holds and copies nothing else.
    """
    return [
        {"index": index, "key": f"map:{index:04d}", **dict(values)}
        for index, values in sorted(maps.items())
    ]
