"""Canonical ROM identity with fail-closed verification.

The single rule this module exists to enforce: NEVER silently continue with an
unverified ROM. A wrong revision, a wrong region, a truncated file or a single
flipped byte must stop the pipeline with a report that says exactly what was
expected and exactly what was found.

Two independent checks are applied, in this order:

1. Whole-file digests (SHA-1, SHA-256, MD5, CRC-32). SHA-1 is the canonical
   identifier for this project; the others are recorded so that a mismatch can
   be matched against the identities other repositories use (LOG1-REMAKE
   identifies the same image by CRC-32).
2. The GBA cartridge header fields at 0x00A0..0x00BD, including the header
   checksum. This is what turns "this ROM is not the one you asked for" into
   "this ROM is a different revision, here is the title and game code".

Check 2 is not redundant: it diagnoses, where check 1 only refuses.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import zlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "config"

#: File offsets of the GBA cartridge header fields (see config/rom.json).
TITLE_OFFSET = 0x00A0
GAME_CODE_OFFSET = 0x00AC
MAKER_CODE_OFFSET = 0x00B0
FIXED_VALUE_OFFSET = 0x00B2
MAIN_UNIT_CODE_OFFSET = 0x00B3
DEVICE_TYPE_OFFSET = 0x00B4
SOFTWARE_VERSION_OFFSET = 0x00BC
HEADER_CHECKSUM_OFFSET = 0x00BD
#: The header checksum covers 0x00A0..0x00BC inclusive.
HEADER_CHECKSUM_FIRST = 0x00A0
HEADER_CHECKSUM_LAST = 0x00BC
HEADER_CHECKSUM_SEED = 0x19


class IdentityError(RuntimeError):
    """Raised when a ROM does not match the configured canonical identity."""

    def __init__(self, path: Path, mismatches: list[str]) -> None:
        self.path = path
        self.mismatches = mismatches
        body = "\n".join(f"  - {m}" for m in mismatches)
        super().__init__(
            f"ROM identity check FAILED for {path}\n{body}\n"
            "Refusing to continue with an unverified ROM."
        )


class RomNotFoundError(RuntimeError):
    """Raised when the configured baserom does not exist."""


@dataclasses.dataclass(frozen=True)
class HeaderFields:
    """The meaningful bytes of the GBA cartridge header."""

    title: str
    game_code: str
    maker_code: str
    fixed_value: int
    main_unit_code: int
    device_type: int
    software_version: int
    stored_header_checksum: int
    #: Recomputed from 0x00A0..0x00BC; differs from stored iff the header was edited.
    computed_header_checksum: int


@dataclasses.dataclass(frozen=True)
class RomIdentity:
    """Everything measured about one ROM file."""

    path: Path
    size: int
    sha1: str
    sha256: str
    md5: str
    crc32: str
    header: HeaderFields | None

    def header_checksum_ok(self) -> bool:
        if self.header is None:
            return False
        return self.header.stored_header_checksum == self.header.computed_header_checksum

    def as_dict(self) -> dict:
        data = {
            "path": str(self.path),
            "size": self.size,
            "sha1": self.sha1,
            "sha256": self.sha256,
            "md5": self.md5,
            "crc32": self.crc32,
        }
        if self.header is not None:
            data["gba_header"] = {
                "title": self.header.title,
                "game_code": self.header.game_code,
                "maker_code": self.header.maker_code,
                "fixed_value": self.header.fixed_value,
                "main_unit_code": self.header.main_unit_code,
                "device_type": self.header.device_type,
                "software_version": self.header.software_version,
                "stored_header_checksum": self.header.stored_header_checksum,
                "computed_header_checksum": self.header.computed_header_checksum,
            }
        return data


def load_canonical(path: Path | None = None) -> dict:
    """Load config/rom.json, the single source of truth for ROM identity."""
    config_path = path or (CONFIG_DIR / "rom.json")
    return json.loads(config_path.read_text(encoding="utf-8"))


def _decode_ascii(raw: bytes) -> str:
    return raw.split(b"\x00", 1)[0].decode("ascii", errors="replace")


def _read_header(data: bytes) -> HeaderFields | None:
    if len(data) < 0x00C0:
        return None
    total = sum(data[HEADER_CHECKSUM_FIRST : HEADER_CHECKSUM_LAST + 1])
    computed = (-(HEADER_CHECKSUM_SEED + total)) & 0xFF
    return HeaderFields(
        title=_decode_ascii(data[TITLE_OFFSET:GAME_CODE_OFFSET]),
        game_code=_decode_ascii(data[GAME_CODE_OFFSET:MAKER_CODE_OFFSET]),
        maker_code=_decode_ascii(data[MAKER_CODE_OFFSET:FIXED_VALUE_OFFSET]),
        fixed_value=data[FIXED_VALUE_OFFSET],
        main_unit_code=data[MAIN_UNIT_CODE_OFFSET],
        device_type=data[DEVICE_TYPE_OFFSET],
        software_version=data[SOFTWARE_VERSION_OFFSET],
        stored_header_checksum=data[HEADER_CHECKSUM_OFFSET],
        computed_header_checksum=computed,
    )


def identify(path: str | Path) -> RomIdentity:
    """Measure a ROM file. Does not compare anything; see verify()."""
    p = Path(path)
    if not p.is_file():
        raise RomNotFoundError(f"ROM not found: {p}")

    data = p.read_bytes()
    return RomIdentity(
        path=p,
        size=len(data),
        sha1=hashlib.sha1(data).hexdigest(),
        sha256=hashlib.sha256(data).hexdigest(),
        md5=hashlib.md5(data).hexdigest(),
        crc32=f"{zlib.crc32(data) & 0xFFFFFFFF:08x}",
        header=_read_header(data),
    )


def compare(actual: RomIdentity, config: dict) -> list[str]:
    """Return a list of human-readable mismatches. Empty means verified."""
    problems: list[str] = []

    expected_size = int(config["size_bytes"])
    if actual.size != expected_size:
        problems.append(
            f"size: expected {expected_size} bytes, found {actual.size} bytes"
        )

    for key in ("sha1", "sha256", "md5", "crc32"):
        expected = config["hashes"][key].lower()
        found = getattr(actual, key).lower()
        if expected != found:
            problems.append(f"{key}: expected {expected}, found {found}")

    expected_header = config.get("gba_header")
    if expected_header:
        if actual.header is None:
            problems.append(
                "GBA header: file is too small to contain a cartridge header "
                f"(need at least 0x00C0 bytes, found {actual.size})"
            )
        else:
            h = actual.header
            for field, expected_value in (
                ("title", expected_header["title"]),
                ("game_code", expected_header["game_code"]),
                ("maker_code", expected_header["maker_code"]),
                ("fixed_value", expected_header["fixed_value"]),
                ("main_unit_code", expected_header["main_unit_code"]),
                ("device_type", expected_header["device_type"]),
                ("software_version", expected_header["software_version"]),
                ("stored_header_checksum", expected_header["header_checksum"]),
            ):
                found = getattr(h, field)
                if found != expected_value:
                    problems.append(
                        f"header {field}: expected {expected_value!r}, found {found!r}"
                    )
            if not actual.header_checksum_ok():
                problems.append(
                    "header checksum does not validate: "
                    f"stored 0x{h.stored_header_checksum:02X}, "
                    f"computed 0x{h.computed_header_checksum:02X} "
                    "(the header has been modified)"
                )

    return problems


def verify(path: str | Path, config: dict | None = None) -> RomIdentity:
    """Identify a ROM and refuse to continue unless it is the canonical image.

    Raises IdentityError with every mismatch listed at once, so a wrong dump is
    diagnosed in a single run rather than one problem per attempt.
    """
    cfg = config if config is not None else load_canonical()
    actual = identify(path)
    problems = compare(actual, cfg)
    if problems:
        raise IdentityError(actual.path, problems)
    return actual


def default_baserom_candidates(repo_root: Path | None = None) -> list[Path]:
    """Where scripts look for the baserom, in priority order.

    1. $BUUSFURY_ROM   - explicit, wins over everything
    2. <repo>/baserom.gba
    3. <repo>/roms/baserom.gba
    """
    import os

    root = repo_root or REPO_ROOT
    candidates: list[Path] = []
    env = os.environ.get("BUUSFURY_ROM", "").strip()
    if env:
        candidates.append(Path(env))
    candidates.append(root / "baserom.gba")
    candidates.append(root / "roms" / "baserom.gba")
    return candidates


def resolve_baserom(explicit: str | Path | None = None, repo_root: Path | None = None) -> Path:
    """Resolve the baserom path, preferring an explicit argument.

    Never invents a path: if nothing exists, raises RomNotFoundError naming every
    location that was tried.
    """
    if explicit is not None:
        p = Path(explicit)
        if not p.is_file():
            raise RomNotFoundError(f"ROM not found at the requested path: {p}")
        return p

    tried = default_baserom_candidates(repo_root)
    for candidate in tried:
        if candidate.is_file():
            return candidate
    locations = "\n".join(f"  - {c}" for c in tried)
    raise RomNotFoundError(
        "No baserom found. A legally dumped copy of the canonical ROM is required "
        "and is never tracked by Git. Looked in:\n" + locations + "\n"
        "Place it at <repo>/baserom.gba, or set BUUSFURY_ROM, or pass --rom."
    )
