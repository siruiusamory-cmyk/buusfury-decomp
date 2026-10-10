"""The six destinations, and nothing else about them.

A destination is a place in the window, not a document: it names the kind of
content a user is looking at, the group it belongs to in the strip, and the one
honest sentence a foundation page can say about it today. The registry is the
only list; the menus, the strip and the stacked pages all read it, so a
destination cannot exist in one place and not another.

No Qt here: this is a table a test can read with no window open.
"""

from __future__ import annotations

from dataclasses import dataclass

#: A peer destination: identity first, one of the five the strip carries.
SEMANTIC = "semantic"

#: The image as an address space. A destination, but a different kind of surface,
#: which is why the strip separates it with one rule.
ROM = "rom"


@dataclass(frozen=True)
class Destination:
    """One destination: its id, its label, its group and its honest state."""

    id: str
    label: str
    group: str
    #: One sentence naming what is NOT built yet. Product language, no promise.
    foundation_summary: str


DESTINATIONS: tuple[Destination, ...] = (
    Destination(
        id="maps",
        label="Maps",
        group=SEMANTIC,
        foundation_summary=(
            "Map layout, chunks, warps, transitions and map graphics are not "
            "implemented in the foundation build."
        ),
    ),
    Destination(
        id="entities",
        label="Entities",
        group=SEMANTIC,
        foundation_summary=(
            "Placement records, the unmodelled object families, behaviours and "
            "stat records are not implemented in the foundation build."
        ),
    ),
    Destination(
        id="scripts_text",
        label="Scripts & Text",
        group=SEMANTIC,
        foundation_summary=(
            "Script families and roots, the event resource corpus, the seven "
            "spoken-dialogue containers and the 1,534-slot string table, as two "
            "text systems that are never one."
        ),
    ),
    Destination(
        id="graphics",
        label="Graphics",
        group=SEMANTIC,
        foundation_summary=(
            "Actor sprite identities, their shared graphics payloads, the "
            "appearance-definition records and the one global object palette, "
            "whose entries are recoloured through the one journal."
        ),
    ),
    Destination(
        id="data",
        label="Data",
        group=SEMANTIC,
        foundation_summary=(
            "Stat tables, map-entry tables, the item table and the coverage "
            "view are not implemented in the foundation build."
        ),
    ),
    Destination(
        id="rom",
        label="ROM",
        group=ROM,
        foundation_summary=(
            "The ROM destination is the address-first view of the image: its "
            "ranges and the owners the range index reports, its bytes beside their "
            "canonical values, raw byte search, and a confirmed raw write into "
            "bytes no structure owns."
        ),
    ),
)

#: The last entry, and the only one a different kind of surface owns.
ROM_DESTINATION = DESTINATIONS[-1]


def destination(destination_id: str) -> Destination:
    """The destination with this id, or ``KeyError`` naming it."""
    for candidate in DESTINATIONS:
        if candidate.id == destination_id:
            return candidate
    raise KeyError(destination_id)
