"""Profile-declared capabilities and the fail-closed gate that checks them.

Why this module exists
----------------------
TOOLKIT-001 through TOOLKIT-004 each shipped a subsystem that opened with the
same three lines: the ROM must be exactly verified, the profile must declare the
table, and the profile's id must equal one hard-coded constant naming Buu's
Fury. That third line is the one TOOLKIT-005 had to remove. It is not a safety
check - the two around it already are - it is the toolkit asking *which game is
this* and refusing every answer but one, which is exactly the coupling
ARCH-TOOL-001 forbids.

What replaces it keeps every guarantee the constant provided:

* **Verified identity.** Unchanged: the ROM must match a profile exactly.
* **Declared capability.** A profile supports a subsystem when, and only when,
  it declares that subsystem's data. A missing declaration is refused by name
  rather than falling through to a default or an inferred offset.
* **Packaged contract.** The supplied profile's metadata is compared against the
  packaged catalog's entry *for that same profile id*. Previously the contract
  was fetched by constant, so it could only ever authorise one game; fetching it
  by identified id generalises the check without weakening it. Identity
  verification authenticates the ROM, not the metadata describing it, so
  without this a hand-edited ``--profiles`` YAML could keep the hashes intact
  while moving the declared extents and the toolkit would dutifully read or
  write against whatever region that file named.

The cost is deliberate and unchanged from TOOLKIT-001: adding a game means
adding it to the *packaged* catalog, not only to a local file. A verified extent
is a project fact, not a user setting.

Note what is *not* here. There is no capability-to-codec mapping and no
dispatch. Choosing a codec is the calling subsystem's job, made from profile
data it reads itself; this module only answers whether the profile is authorised
to be asked. Putting dispatch here would rebuild the same coupling one layer up.
"""

from __future__ import annotations

from enum import Enum
from functools import cache
from importlib import resources

from .profile import RomProfile, RomProfileCatalog, VerificationStatus
from .rom import RomIdentification


class Capability(str, Enum):
    """A subsystem a profile can declare support for.

    The value is the profile field that declares it, so a capability cannot
    drift from the data that backs it: `_declared` reads exactly this attribute
    and a profile that does not populate it does not have the capability.
    """

    MAP_ENTRIES = "map_entries"
    ENEMY_STATS = "enemy_stats"
    CHARACTER_BASE_STATS = "character_base_stats"
    TEXT_STRINGS = "text_strings"
    SCRIPTS = "scripts"
    PLACEMENT_TYPES = "placement_types"


class CapabilityError(ValueError):
    """Raised when a profile is not authorised for a requested capability.

    One class rather than a hierarchy: every caller here either proceeds or
    refuses, and no code path branches on *why* a profile was unauthorised. The
    message carries that distinction, which is where a human reads it. A
    subsystem that later needs to tell "not declared" apart from "metadata does
    not match" should subclass then, on evidence of a caller that acts on it.
    """


def declared(profile: RomProfile, capability: Capability) -> bool:
    """Whether ``profile`` declares ``capability``."""
    return getattr(profile, capability.value) is not None


def capabilities(profile: RomProfile) -> tuple[Capability, ...]:
    """Every capability ``profile`` declares, in a stable order."""
    return tuple(item for item in Capability if declared(profile, item))


@cache
def _packaged_catalog() -> RomProfileCatalog:
    """The in-repo catalog, read from the package rather than from user input.

    Cached because it is immutable for the life of the process and is consulted
    once per subsystem call.
    """
    packaged = resources.files("tools.webfoot.data").joinpath("roms.yaml")
    return RomProfileCatalog.loads(
        packaged.read_text(encoding="utf-8"),
        source="packaged tools.webfoot.data/roms.yaml",
    )


def packaged_contract(
    profile_id: str,
    capability: Capability,
    *,
    error_type: type[CapabilityError] = CapabilityError,
) -> RomProfile:
    """The packaged catalog's entry for ``profile_id``, declaring ``capability``."""
    try:
        profile = next(
            item for item in _packaged_catalog().profiles if item.id == profile_id
        )
    except StopIteration as exc:
        raise error_type(f"packaged catalog has no {profile_id!r} profile") from exc
    if not declared(profile, capability):
        raise error_type(
            f"packaged profile {profile_id!r} does not declare {capability.value}"
        )
    return profile


def require(
    identification: RomIdentification,
    capability: Capability,
    *,
    subsystem: str,
    error_type: type[CapabilityError] = CapabilityError,
    check_header: bool = False,
) -> RomProfile:
    """Return the verified profile authorised for ``capability``, or raise.

    ``subsystem`` names the caller in error messages, so a refusal says which
    access was refused rather than only which capability was missing.

    ``check_header`` additionally compares the ROM header's game code and
    software version against the contract. It is off by default because the
    SHA-256 comparison already implies both for an intact image; the map-entry
    reader has asserted it since ROM-002 as a cheap, independent statement of
    *which* game the bytes claim to be, and keeping the option preserves that
    guarantee rather than quietly dropping it during this refactor.

    ``error_type`` lets a subsystem keep raising its own established error class
    while sharing this logic, so existing callers that catch `StatProfileError`
    or `TextProfileError` are unaffected by the move. It must derive from
    `CapabilityError`, which those subsystem errors do.

    The checks run in order of how much they assume: identity first, because
    nothing below is meaningful without it; then the declaration, because it is
    the cheap and expected reason a second game says no; then the contract
    comparison, which is the check that survives a doctored profile file.
    """
    match = identification.profile_match
    if match.status is not VerificationStatus.VERIFIED or match.profile is None:
        raise error_type(f"{subsystem} requires an exactly verified ROM")
    profile = match.profile

    if not declared(profile, capability):
        raise error_type(
            f"profile {profile.id!r} does not declare {capability.value}; "
            f"{subsystem} is unavailable for this ROM"
        )

    contract = packaged_contract(profile.id, capability, error_type=error_type)
    if getattr(profile, capability.value) != getattr(contract, capability.value):
        raise error_type(
            f"supplied profile {capability.value} metadata conflicts with the "
            f"packaged contract; refusing {subsystem} against unverified extents"
        )
    if (
        identification.hashes.sha256 != contract.sha256
        or identification.size != contract.size
    ):
        raise error_type(
            f"{subsystem} requires the exact verified identity for "
            f"profile {profile.id!r}"
        )
    if check_header and (
        identification.header.game_code != contract.game_code
        or identification.header.software_version != contract.revision
    ):
        raise error_type(
            f"{subsystem} requires the ROM header to match profile "
            f"{profile.id!r}"
        )
    return profile
