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

**CQA-04: the resolution itself now lives in the SDK.** `webfoot.packaged` carries
`PACKAGED_PROFILE_ID`, `packaged_profile` and `packaged_profile_identity`, because
the SDK's own map/graphics reader and the map-layout writer need exactly the same
lookup and must not resolve a different profile from the exporter. What remains
here is the export-facing spelling of it, kept so exporter call sites and their
provenance labels do not move. The dependency points SDK authority -> export
consumer and never the reverse.

Why the packaged catalog rather than a caller-supplied one: these readers are
addressed by fixed offsets that were verified against one image, so letting the
identity come from an arbitrary `--profiles` file would move the very extents the
readers were proven on. `webfoot.capability` makes the same choice, for the same
reason.
"""

from __future__ import annotations

from tools.webfoot.packaged import (
    PACKAGED_PROFILE_ID as CANONICAL_EXPORT_PROFILE_ID,
    packaged_profile,
    packaged_profile_identity,
)
from tools.webfoot.profile import AtlasIdentity, RomProfile

__all__ = [
    "CANONICAL_EXPORT_PROFILE_ID",
    "canonical_export_profile",
    "canonical_export_identity",
]


def canonical_export_profile() -> RomProfile:
    """The packaged profile describing the image these readers accept."""
    return packaged_profile()


def canonical_export_identity() -> AtlasIdentity:
    """That profile's identity triple, for callers that only need to compare."""
    return packaged_profile_identity()
