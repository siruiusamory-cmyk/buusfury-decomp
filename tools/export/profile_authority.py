"""The export-side readers' single profile authority.

ASSET-EXPORT-001 and the LOGX/DragonByte Z readers under `tools.export` were
written against one verified image and carried that image's identity and table
extents as module constants in `canonical.py` and `map_browser.py`. CQA-15 found
those to be a second, independent owner of facts the profile catalog already
declares, and one of them - `canonical.TEXT_POINTER_COUNT` - was a live index
bound.

This module is the one place those readers ask for that data. It is deliberately
thin: it resolves a profile from the *packaged* catalog - the same file
`webfoot.capability` treats as the trusted, in-repo authority - so the exported
identity is the catalog's declaration and not a literal beside it. Nothing here
stores a copy of any address, count or hash; every value is read through the
resolved `RomProfile` at the point of use.

Why the packaged catalog rather than a caller-supplied one: these readers are
addressed by fixed offsets that were verified against one image, so letting the
identity come from an arbitrary `--profiles` file would move the very extents the
readers were proven on. `webfoot.capability` makes the same choice, for the same
reason.
"""

from __future__ import annotations

from tools.webfoot.profile import AtlasIdentity, RomProfile

#: The canonical profile this export stack was verified against. It is a
#: provenance label - the identity values themselves come from the catalog
#: entry it names, never from a literal here.
CANONICAL_EXPORT_PROFILE_ID = "buus_fury_usa_rev0_01c1707f"


def canonical_export_profile() -> RomProfile:
    """The packaged profile describing the image these readers accept."""
    from tools.webfoot.capability import Capability, packaged_contract

    return packaged_contract(CANONICAL_EXPORT_PROFILE_ID, Capability.MAP_ENTRIES)


def canonical_export_identity() -> AtlasIdentity:
    """That profile's identity triple, for callers that only need to compare."""
    return canonical_export_profile().identity
