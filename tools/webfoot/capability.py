
from __future__ import annotations

from enum import Enum
from functools import cache
from importlib import resources

from .profile import RomProfile, RomProfileCatalog, VerificationStatus
from .rom import RomIdentification


class Capability(str, Enum):
    """Each value names the profile field that declares it, so a capability cannot drift from the data that backs it."""

    MAP_ENTRIES = "map_entries"
    ENEMY_STATS = "enemy_stats"
    CHARACTER_BASE_STATS = "character_base_stats"
    TEXT_STRINGS = "text_strings"
    SCRIPTS = "scripts"
    PLACEMENT_TYPES = "placement_types"
    ACTOR_SPRITES = "actor_sprites"
    APPEARANCES = "appearances"


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
    match = identification.profile_match
    if match.status is not VerificationStatus.VERIFIED or match.profile is None:
        raise error_type(f"{subsystem} requires an exactly verified ROM")
    profile = match.profile

    if not declared(profile, capability):
        raise error_type(
            f"profile {profile.id!r} does not declare {capability.value}; "
            f"{subsystem} is unavailable for this ROM"
        )

    # A supplied profile's extents are trusted only after the packaged catalog's entry for the same id agrees, because identity verification authenticates the ROM and not the metadata describing it.
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
