"""The packaged profile the ROM-addressed readers were verified against.

Every ROM-addressed reader in this project resolves table addresses that are a
*declaration*, not a literal: `RomProfile` owns them and the packaged catalog in
``tools.webfoot.data/roms.yaml`` is the trusted authority `webfoot.capability`
gates on. What is left is the one question those readers still have to answer for
themselves - *which* catalog entry is the image they were proven against - and
that answer is a provenance label.

This module is that label's single owner. It lives outside `webfoot.profile`
deliberately: `tools/webfoot/profile.py` is one of the core modules
`tests/unit/test_capability.py` holds to "no game name in executable code", and a
profile id is a game name wherever it is spelled. Putting the label here keeps
the rule intact - a shape is documented in a docstring, a *selection* lives in a
provenance module - and keeps every reader that needs the default from restating
the string.

**Nothing here holds an extent.** The id selects a catalog entry; the address,
count, stride and hash all come from that entry through `RomProfile`. That is the
property CQA-03/CQA-15 established and CQA-04 preserved.
"""

from __future__ import annotations

from .profile import AtlasIdentity, RomProfile

#: The packaged profile the ROM-addressed readers were verified against.
PACKAGED_PROFILE_ID = "buus_fury_usa_rev0_01c1707f"


def packaged_profile(profile_id: str = PACKAGED_PROFILE_ID) -> RomProfile:
    """One profile from the *packaged* catalog, or a refusal naming what is missing.

    A caller that has resolved a profile of its own must pass that one instead;
    this is only the default for a reader whose addresses were verified against
    the packaged image. The import is deferred because `capability` imports
    `profile`.
    """
    from .capability import Capability, packaged_contract

    return packaged_contract(profile_id, Capability.MAP_ENTRIES)


def packaged_profile_identity(profile_id: str = PACKAGED_PROFILE_ID) -> AtlasIdentity:
    """That profile's identity triple, for callers that only need to compare."""
    return packaged_profile(profile_id).identity
