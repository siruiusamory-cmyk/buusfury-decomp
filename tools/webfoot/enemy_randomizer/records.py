"""The placement record mutation authority for the enemy randomizer pack.

One component decides how an intended semantic edit to a placement record becomes
an attributed :class:`~tools.webfoot.write.ByteChange`. The placement shuffle and
the type shuffle both express their intent as *field values* and hand them here,
so neither module encodes bytes and the record codec stays in one place.

Why edits are merged before encoding
====================================

A placement record is a single object, and both shuffles can touch the same
record: the type shuffle rewrites ``+0x08``/``+0x10`` and the placement shuffle
rewrites ``+0x0C``. Two independent full-record overwrites of the same bytes would
be reported as an overlap by :func:`tools.webfoot.write.plan_changes`, and
correctly so - it cannot tell that the two writers were describing different
fields of one object. The fix is not to relax the overlap check; it is to merge
the intended fields first and encode the record exactly once, which also makes the
manifest carry one attributed change per record instead of two overlapping ones.

Every edit is applied to the record's **own original bytes**, and only the decoded
span is overwritten. The variable-length child-pointer array at ``+0x1C`` and the
flags at ``+0x04`` therefore ride through untouched, which is what makes an
unedited record re-serialize byte-identically.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from ..maps import PlacementEntry, PlacementIdentity
from ..write import ByteChange

#: The placement fields this pack is allowed to rewrite, by record offset.
#:
#: ``+0x04`` (flags) and ``+0x14`` (the behavior-descriptor pointer) are editable
#: ONLY as part of the retype typing mode, where an identity is installed together
#: with everything the engine reads alongside it. In the default proven-pair mode
#: neither is written: an identity goes only onto a slot that already matches, so
#: neither changes. See :mod:`tools.webfoot.enemy_randomizer.enemy_type` for why
#: the two modes exist.
#:
#: ``+0x18``/``+0x1C`` (the child count and child pointers) are written by neither
#: mode. They describe attached structure rather than the actor's own
#: configuration, and this pack has no evidence about what may share one, so a
#: record whose children differ from a peer's is simply not a retype donor.
EDITABLE_FIELDS: frozenset[str] = frozenset(
    {"type_raw", "position_raw", "id_raw", "flags_raw", "descriptor_pointer_raw"}
)

#: The fields the type shuffle owns, by mode. The coupled pair joins only when the
#: mode retypes, because installing an identity onto a slot with different coupled
#: fields is exactly the hybrid the default mode refuses.
TYPE_FIELDS: tuple[str, ...] = ("type_raw", "id_raw")
TYPE_FIELDS_WITH_COUPLING: tuple[str, ...] = (
    "type_raw", "id_raw", "flags_raw", "descriptor_pointer_raw",
)

#: The fields the placement shuffle owns.
PLACEMENT_FIELDS: tuple[str, ...] = ("position_raw",)


class RecordEditError(ValueError):
    """An edit this authority will not perform."""


@dataclass(frozen=True, slots=True)
class RecordEdits:
    """Intended field values, accumulated per placement, keyed by owner module.

    ``edits[identity][module]`` is the dict of field values that module wants.
    Keeping the module as a key rather than merging immediately is what lets the
    manifest attribute a change to the module that caused it and lets a test
    assert that one module's choices cannot depend on another's.
    """

    edits: dict[PlacementIdentity, dict[str, dict[str, int]]]

    @classmethod
    def empty(cls) -> "RecordEdits":
        return cls(edits={})

    def set(self, identity: PlacementIdentity, module_id: str, **values: int) -> None:
        unknown = set(values) - EDITABLE_FIELDS
        if unknown:
            raise RecordEditError(
                f"{identity}: {', '.join(sorted(unknown))} is not editable by this "
                f"pack; editable: {', '.join(sorted(EDITABLE_FIELDS))}"
            )
        self.edits.setdefault(identity, {})[module_id] = dict(values)

    def fields_for(self, identity: PlacementIdentity) -> dict[str, int]:
        """Every intended field for one placement, merged across modules."""
        merged: dict[str, int] = {}
        for values in self.edits.get(identity, {}).values():
            merged.update(values)
        return merged

    def modules_for(self, identity: PlacementIdentity) -> tuple[str, ...]:
        return tuple(sorted(self.edits.get(identity, {})))

    def is_empty(self) -> bool:
        return not self.edits


def _apply(entry: PlacementEntry, fields: dict[str, int]):
    """The record with ``fields`` installed, validated by the codec on encode."""
    return replace(entry.record, **fields)


def changes_for(
    entries: dict[PlacementIdentity, PlacementEntry],
    edits: RecordEdits,
) -> tuple[ByteChange, ...]:
    """Encode each edited placement once, as an attributed change.

    The ``owner`` is the placement's semantic identity - never a ROM address -
    and the ``reason`` names the modules that produced the value, so a manifest
    answers "which edit changed these bytes" rather than only "these bytes
    differ".
    """
    changes: list[ByteChange] = []
    for identity in sorted(edits.edits):
        entry = entries.get(identity)
        if entry is None:
            raise RecordEditError(f"{identity}: no such placement in this image")
        fields = edits.fields_for(identity)
        if not fields:
            continue
        record = _apply(entry, fields)
        encoded = record.to_bytes()
        if len(encoded) != len(entry.original_bytes):
            raise RecordEditError(
                f"{identity}: encoding changed the record's length "
                f"({len(entry.original_bytes)} -> {len(encoded)}); the placement "
                "family is variable-length and this pack only rewrites fixed-width "
                "fields inside the existing extent"
            )
        if encoded == entry.original_bytes:
            # A module may legitimately draw the identity a slot already had.
            # Emitting a no-op change would put a row in the manifest claiming a
            # rewrite that did not happen.
            continue
        modules = ", ".join(edits.modules_for(identity))
        fields_named = ", ".join(sorted(fields))
        changes.append(
            ByteChange(
                offset=entry.file_offset,
                old=entry.original_bytes,
                new=encoded,
                owner=str(identity),
                reason=f"enemy randomizer [{modules}]: {fields_named}",
            )
        )
    return tuple(changes)
