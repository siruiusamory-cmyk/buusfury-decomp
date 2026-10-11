"""The text-edit engine's public surface: open, plan, apply, rename_positions.

A caller never touches a byte:

    from tools.webfoot import textedit

    model = textedit.open(rom, canonical=canonical_rom)
    built = textedit.plan(model, [textedit.RecordEdit(1, 38856, 252, "Great Soy Man",
                                                      "Great Soyman")])
    report = textedit.apply(built, out)

`open` is the ticket's name for :func:`open_rom`; the alias exists so a caller
can write the API the ticket specifies, and `open_rom` stays available where
shadowing the builtin would be confusing.
"""

from __future__ import annotations

from .engine import (
    AMBIGUOUS_PORTRAIT,
    IN_PLACE,
    KEEP,
    MOVE,
    NAMED_PORTRAIT,
    NO_PORTRAIT,
    PARTY_PORTRAIT,
    REFUSED,
    RENAME,
    UNCLEAR,
    UNKNOWN_PORTRAIT,
    Change,
    Control,
    Decision,
    Layout,
    MapRow,
    MapTable,
    Model,
    Occurrence,
    Plan,
    Portrait,
    Record,
    RecordEdit,
    RenameEdit,
    Slot,
    SlotEdit,
    SpokenLine,
    Text,
    TextEditError,
    TitleProfile,
    apply,
    detect,
    lines,
    line_maps,
    locked_tokens,
    maps,
    open_rom,
    plan,
    portraits,
    readback,
    record_maps,
    record_operand,
    rename_occurrences,
    rename_positions,
    shown_text,
    speakers,
    units,
    validate,
)

open = open_rom  # noqa: A001 - the public name the ticket's API specifies

__all__ = [
    "AMBIGUOUS_PORTRAIT",
    "IN_PLACE",
    "KEEP",
    "MOVE",
    "NAMED_PORTRAIT",
    "NO_PORTRAIT",
    "PARTY_PORTRAIT",
    "REFUSED",
    "RENAME",
    "UNCLEAR",
    "UNKNOWN_PORTRAIT",
    "Change",
    "Control",
    "Decision",
    "Layout",
    "MapRow",
    "MapTable",
    "Model",
    "Occurrence",
    "Plan",
    "Portrait",
    "Record",
    "RecordEdit",
    "RenameEdit",
    "Slot",
    "SlotEdit",
    "SpokenLine",
    "Text",
    "TextEditError",
    "TitleProfile",
    "apply",
    "detect",
    "lines",
    "line_maps",
    "locked_tokens",
    "maps",
    "open",
    "open_rom",
    "plan",
    "portraits",
    "readback",
    "record_maps",
    "record_operand",
    "rename_occurrences",
    "rename_positions",
    "shown_text",
    "speakers",
    "units",
    "validate",
]
