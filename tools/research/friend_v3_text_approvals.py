"""The owner-approved text-table edits, as tracked constants.

WHY A TRACKED CONSTANT RATHER THAN A MANIFEST FIELD. A verifier that reads the expected text
out of the manifest is checking the artifact against itself: the builder wrote both. The
approved wording therefore lives here, where a verifier and a test can recompute it, and the
manifest's own copy of it is treated as provenance rather than as authority.

Each entry carries the slot, the text the image held before the approval (the guard that the
write lands where the approval says), the approved replacement, and the approval's own
identity so a reader can trace the wording back to the decision it came from.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ApprovedTextSlot:
    """One approved text-table slot: its identity, its old text and its approved text."""

    slot: int
    old: str
    new: str
    label: str
    approval: str


#: Slot 1083, Bulma's scanner biography. Owner decision relayed by the coordinator on
#: 2026-10-10, quoted verbatim; the Adja node that recorded the owner's wording is named in
#: the string so the approval can be found again.
APPROVED_TEXT_SLOTS: tuple[ApprovedTextSlot, ...] = (
    ApprovedTextSlot(
        slot=1083,
        old="Bulma is Yamcha's wife and Krillin and Videl's mother. She is the daughter of "
            "the Ox-King.",
        new="Bulma is Yamcha's wife and Krillin and Videl's mother. A genius inventor, she "
            "is the heiress of Capsule Corporation.",
        label="biography, Bulma",
        approval="FRIEND-V3-WT-SPLIT-CONTAINER-001 release 2.1 owner decision, 2026-10-10",
    ),
)

#: The replacements by slot, for a caller that wants the approved wording alone.
APPROVED_REPLACEMENTS = {edit.slot: edit.new for edit in APPROVED_TEXT_SLOTS}
