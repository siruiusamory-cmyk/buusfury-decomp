"""Mutable ROM fixtures, and the identity check that keeps them safe.

OWNER R3, 2026-10-09, after a test wrote through the canonical ROM's path and
changed every worktree that hard-links or junctions to it. The rule this module
enforces: a test may READ the canonical image, and every test that MUTATES ROM
bytes mutates an independently created copy whose file identity is proved distinct
from every protected repository input before it is handed over.

The distinction matters and is worth stating in the tests' own vocabulary.
:func:`assert_distinct_file_identity` is a PREVENTIVE check - it stops a test
before the write. The digest verifications in the ROM-gated tests are DETECTIVE -
they notice corruption after it exists. The incident was invisible to the second
kind and would have been stopped by the first.
"""

from __future__ import annotations

from hashlib import sha256
import os
from pathlib import Path

import pytest

from tests.gates import REPOSITORY_ROOT

#: The canonical Buu's Fury image every ROM-gated family reads, in the two
#: spellings the suite accepts, plus the default location under the repo root.
ROM_ENVIRONMENT_VARIABLES = ("WEBFOOT_BUU_ROM", "LOGX_CANONICAL_ROM")
ROM_DEFAULT = Path("roms") / "Dragon Ball Z - Buu's Fury (U).gba"
CANONICAL_ROM_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)

#: The directories `tools.webfoot.destination` treats as protected ROM inputs.
PROTECTED_INPUT_DIRECTORIES = ("roms", "extracted", "dump", "stock", "exports")


def canonical_rom_path() -> Path | None:
    """The canonical image this suite may read, or None when it is absent."""
    for variable in ROM_ENVIRONMENT_VARIABLES:
        value = os.environ.get(variable)
        if value and Path(value).is_file():
            return Path(value)
    candidate = REPOSITORY_ROOT / ROM_DEFAULT
    return candidate if candidate.is_file() else None


def canonical_rom_bytes() -> bytes:
    """Read the canonical image, or skip the test that needs it.

    Reading is the only thing this helper does. Every write path in this suite
    goes through :func:`mutable_rom_copy` instead.
    """
    path = canonical_rom_path()
    if path is None:
        pytest.skip("canonical Buu's Fury ROM not present locally")
    data = path.read_bytes()
    digest = sha256(data).hexdigest()
    if digest != CANONICAL_ROM_SHA256:
        pytest.skip(
            "local ROM is not the canonical profile these offsets target "
            f"(sha256 {digest})"
        )
    return data


def canonical_rom_sha256() -> str:
    """The canonical image's digest as it stands now, or a skip when absent."""
    return sha256(canonical_rom_bytes()).hexdigest()


def protected_input_identity() -> set[tuple[int, int]]:
    """The file identity of every protected repository ROM input.

    A file's identity is what the operating system uses to say "these two names
    are one file": volume serial and file index on Windows, device and inode on
    POSIX. Two names that share one identity cannot be written independently,
    which is how one test's write reached every worktree linked to the input.
    """
    identities: set[tuple[int, int]] = set()
    for name in PROTECTED_INPUT_DIRECTORIES:
        directory = REPOSITORY_ROOT / name
        if not directory.is_dir():
            continue
        for walked, _, names in os.walk(directory):
            for entry in names:
                try:
                    info = (Path(walked) / entry).stat()
                except OSError:
                    continue
                identities.add((info.st_dev, info.st_ino))
    return identities


def assert_distinct_file_identity(path: Path) -> None:
    """Refuse to proceed when `path` IS a protected input, or shares its file.

    The required regression: a fixture that computes the identity of the bytes it
    is about to mutate and finds a protected input behind them stops the test
    instead of mutating a repository input.
    """
    info = Path(path).stat()
    if (info.st_dev, info.st_ino) in protected_input_identity():
        raise AssertionError(
            f"{path} is the same file as a protected repository ROM input - "
            f"identity ({info.st_dev}, {info.st_ino}) - so it is not a mutable "
            "fixture; copy it into a temporary directory first"
        )


def mutable_rom_copy(directory: Path, name: str = "mutable-base.gba") -> Path:
    """An independently created, mutable copy of the canonical image.

    The copy is written into `directory` (a pytest temporary directory), its
    identity is proved distinct from every protected input before it is handed
    back, and the canonical image itself is only ever read.
    """
    data = canonical_rom_bytes()
    path = Path(directory) / name
    path.write_bytes(data)
    assert_distinct_file_identity(path)
    return path


def assert_canonical_unchanged() -> None:
    """Prove the repository's canonical image is still the canonical image.

    The detective half: run after a ROM-touching test, it fails the test that
    damaged the input rather than failing the next one to read it.
    """
    path = canonical_rom_path()
    if path is None:
        pytest.skip("canonical Buu's Fury ROM not present locally")
    digest = sha256(path.read_bytes()).hexdigest()
    assert digest == CANONICAL_ROM_SHA256, (
        f"the canonical ROM at {path} is no longer the canonical image "
        f"(sha256 {digest}); a test in this run wrote to it"
    )
