"""Data-driven exact ROM profiles and conservative matching."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import re
from typing import Any, Mapping, Sequence

import yaml

from .gba_header import GbaHeader
from .hashing import RomHashes


_HEX_LENGTHS = {"crc32": 8, "md5": 32, "sha1": 40, "sha256": 64}
_ALLOWED_KEYS = {
    "id",
    "game",
    "region",
    "revision",
    "game_code",
    "size",
    "crc32",
    "md5",
    "sha1",
    "sha256",
    "sources",
    "notes",
}


class ProfileConfigError(ValueError):
    """Raised for malformed or duplicate profile configuration."""


class AmbiguousProfileError(ProfileConfigError):
    """Raised when multiple profiles exactly identify one ROM."""


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    UNKNOWN = "UNKNOWN"
    CONFLICT = "CONFLICT"


def _required_string(data: Mapping[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ProfileConfigError(f"profile field {key!r} must be a non-empty string")
    return value.strip()


def _optional_hash(data: Mapping[str, Any], key: str) -> str | None:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ProfileConfigError(f"profile field {key!r} must be a hexadecimal string")
    normalized = value.strip().lower()
    expected_length = _HEX_LENGTHS[key]
    if len(normalized) != expected_length or re.fullmatch(r"[0-9a-f]+", normalized) is None:
        raise ProfileConfigError(
            f"profile field {key!r} must contain {expected_length} hexadecimal characters"
        )
    return normalized


@dataclass(frozen=True, slots=True)
class RomProfile:
    id: str
    game: str
    region: str
    revision: int | None
    game_code: str
    size: int
    crc32: str | None
    md5: str | None
    sha1: str | None
    sha256: str | None
    sources: tuple[str, ...]
    notes: str

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "RomProfile":
        if not isinstance(data, Mapping):
            raise ProfileConfigError("each profile must be a mapping")

        unexpected = set(data) - _ALLOWED_KEYS
        if unexpected:
            joined = ", ".join(sorted(str(key) for key in unexpected))
            raise ProfileConfigError(f"profile contains unexpected fields: {joined}")

        revision = data.get("revision")
        if revision is not None and (
            type(revision) is not int or revision < 0 or revision > 255
        ):
            raise ProfileConfigError("profile revision must be an integer from 0 through 255")

        size = data.get("size")
        if type(size) is not int or size <= 0:
            raise ProfileConfigError("profile size must be a positive integer")

        game_code = _required_string(data, "game_code").upper()
        if len(game_code) != 4 or not game_code.isascii() or not game_code.isalnum():
            raise ProfileConfigError("profile game_code must be four alphanumeric ASCII characters")

        sources_value = data.get("sources", [])
        if not isinstance(sources_value, list) or not all(
            isinstance(source, str) and source.strip() for source in sources_value
        ):
            raise ProfileConfigError("profile sources must be a list of non-empty strings")

        hashes = {key: _optional_hash(data, key) for key in _HEX_LENGTHS}
        if hashes["sha256"] is None:
            raise ProfileConfigError("profile must provide sha256 for exact verification")

        notes = data.get("notes", "")
        if not isinstance(notes, str):
            raise ProfileConfigError("profile notes must be a string")

        return cls(
            id=_required_string(data, "id"),
            game=_required_string(data, "game"),
            region=_required_string(data, "region"),
            revision=revision,
            game_code=game_code,
            size=size,
            crc32=hashes["crc32"],
            md5=hashes["md5"],
            sha1=hashes["sha1"],
            sha256=hashes["sha256"],
            sources=tuple(source.strip() for source in sources_value),
            notes=notes.strip(),
        )


@dataclass(frozen=True, slots=True)
class ProfileMatch:
    status: VerificationStatus
    profile: RomProfile | None
    reason: str
    mismatches: tuple[str, ...] = ()


class RomProfileCatalog:
    def __init__(self, profiles: Sequence[RomProfile]) -> None:
        self.profiles = tuple(profiles)
        self._validate_unique()

    @classmethod
    def load(cls, path: str | Path) -> "RomProfileCatalog":
        config_path = Path(path)
        try:
            text = config_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ProfileConfigError(f"cannot load ROM profiles from {config_path}: {exc}") from exc
        return cls.loads(text, source=str(config_path))

    @classmethod
    def loads(cls, text: str, *, source: str = "<profiles>") -> "RomProfileCatalog":
        try:
            raw = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            raise ProfileConfigError(f"cannot load ROM profiles from {source}: {exc}") from exc

        if not isinstance(raw, Mapping):
            raise ProfileConfigError("ROM profile configuration must be a mapping")
        if raw.get("schema_version") != 1:
            raise ProfileConfigError("ROM profile configuration requires schema_version: 1")
        profile_data = raw.get("profiles")
        if not isinstance(profile_data, list):
            raise ProfileConfigError("ROM profile configuration requires a profiles list")
        return cls([RomProfile.from_mapping(item) for item in profile_data])

    def _validate_unique(self) -> None:
        ids: set[str] = set()
        identities: dict[tuple[str, str], str] = {}
        for profile in self.profiles:
            if profile.sha256 is None:
                raise ProfileConfigError(
                    f"profile {profile.id!r} must provide sha256 for exact verification"
                )
            if profile.id in ids:
                raise ProfileConfigError(f"duplicate profile id: {profile.id}")
            ids.add(profile.id)
            for algorithm in ("sha256", "sha1", "md5"):
                value = getattr(profile, algorithm)
                if value is None:
                    continue
                key = (algorithm, value)
                prior = identities.get(key)
                if prior is not None:
                    raise ProfileConfigError(
                        f"duplicate {algorithm} identity in profiles {prior!r} and {profile.id!r}"
                    )
                identities[key] = profile.id

    def match(
        self,
        *,
        size: int,
        hashes: RomHashes,
        header: GbaHeader,
    ) -> ProfileMatch:
        candidates: list[RomProfile] = []
        conflicts: list[tuple[RomProfile, tuple[str, ...]]] = []

        for profile in self.profiles:
            if hashes.sha256 != profile.sha256:
                continue

            mismatches = self._mismatches(
                profile, size=size, hashes=hashes, header=header
            )
            if mismatches:
                conflicts.append((profile, mismatches))
            else:
                candidates.append(profile)

        if len(candidates) > 1:
            joined = ", ".join(profile.id for profile in candidates)
            raise AmbiguousProfileError(f"ROM matches multiple profiles: {joined}")
        if candidates:
            return ProfileMatch(
                status=VerificationStatus.VERIFIED,
                profile=candidates[0],
                reason="all configured hashes and metadata match exactly",
            )
        if conflicts:
            profile, mismatches = conflicts[0]
            return ProfileMatch(
                status=VerificationStatus.CONFLICT,
                profile=profile,
                reason="a cryptographic identity matched but configured metadata conflicted",
                mismatches=mismatches,
            )
        return ProfileMatch(
            status=VerificationStatus.UNKNOWN,
            profile=None,
            reason="no configured cryptographic identity matched",
        )

    @staticmethod
    def _mismatches(
        profile: RomProfile,
        *,
        size: int,
        hashes: RomHashes,
        header: GbaHeader,
    ) -> tuple[str, ...]:
        mismatches: list[str] = []
        if profile.size != size:
            mismatches.append(f"size: expected {profile.size}, got {size}")
        if profile.game_code != header.game_code:
            mismatches.append(
                f"game_code: expected {profile.game_code}, got {header.game_code}"
            )
        if profile.revision is not None and profile.revision != header.software_version:
            mismatches.append(
                f"revision: expected {profile.revision}, got {header.software_version}"
            )
        for algorithm in ("crc32", "md5", "sha1", "sha256"):
            expected = getattr(profile, algorithm)
            actual = getattr(hashes, algorithm)
            if expected is not None and expected != actual:
                mismatches.append(f"{algorithm}: expected {expected}, got {actual}")
        return tuple(mismatches)
