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
    IN_PLACE,
    KEEP,
    MOVE,
    RENAME,
    REFUSED,
    UNCLEAR,
    Change,
    Control,
    Decision,
    Layout,
    Model,
    Occurrence,
    Plan,
    Record,
    RecordEdit,
    RenameEdit,
    Slot,
    SlotEdit,
    Text,
    TextEditError,
    TitleProfile,
    apply,
    detect,
    locked_tokens,
    open_rom,
    plan,
    rename_occurrences,
    rename_positions,
    readback,
    units,
    validate,
)

open = open_rom  # noqa: A001 - the public name the ticket's API specifies

__all__ = [
    "IN_PLACE",
    "KEEP",
    "MOVE",
    "RENAME",
    "REFUSED",
    "Change",
    "Control",
    "Decision",
    "Layout",
    "Model",
    "Occurrence",
    "Plan",
    "Record",
    "RecordEdit",
    "RenameEdit",
    "Slot",
    "SlotEdit",
    "Text",
    "TextEditError",
    "TitleProfile",
    "apply",
    "detect",
    "locked_tokens",
    "open",
    "open_rom",
    "plan",
    "rename_occurrences",
    "rename_positions",
    "readback",
    "units",
    "validate",
]
