"""The mutable-fixture isolation rule, tested against itself. OWNER R3.

The incident this file exists for: a test wrote ROM bytes through the path its
`rom` fixture named, that path was a hard link shared with 17 worktrees, and one
in-place write changed every tree at once. No digest check saw it, because every
worktree's digest changed together.

`tests/rom_support.assert_distinct_file_identity` is the PREVENTIVE check that
catches it, and this file proves the check itself fires:

* it accepts a copy made in pytest's temporary root;
* it REFUSES a path that shares a file with a protected repository input;
* the fixture every ROM-gated test uses passes that check;
* the canonical repository image is left byte-identical by reading it;
* the protected-name mirror this helper scans equals the policy tuple, so the
  guard cannot silently narrow to fewer names than the policy protects.

The refusal is driven with a genuine hard link to a genuine protected input,
created in a temporary directory, so the rule is proved against the filesystem's
own identity rather than against a mock of it.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from tests import rom_support
from tests.rom_support import (
    CANONICAL_ROM_SHA256,
    assert_canonical_unchanged,
    assert_distinct_file_identity,
    canonical_rom_bytes,
    canonical_rom_path,
    mutable_rom_copy,
    protected_input_identity,
)
from tools.webfoot.destination import PROTECTED_INPUT_DIRECTORIES


def test_a_copy_in_a_temporary_root_is_accepted(tmp_path: Path):
    copy = mutable_rom_copy(tmp_path)

    assert_distinct_file_identity(copy)
    assert copy.read_bytes()[:4] == canonical_rom_bytes()[:4]


def test_a_hard_link_to_a_protected_input_is_refused(tmp_path: Path):
    """The incident's own shape, refused by the identity check."""
    protected = canonical_rom_path()
    if protected is None:  # pragma: no cover - no ROM on this machine
        pytest.skip("canonical ROM not present locally")
    alias = tmp_path / "hardlink-to-the-input.gba"
    try:
        os.link(protected, alias)
    except OSError as exc:  # pragma: no cover - cross-volume temporary root
        pytest.skip(f"this host cannot hard-link across these directories: {exc}")

    # It IS the protected input, whatever its name and directory say.
    assert os.path.samefile(alias, protected)
    with pytest.raises(AssertionError, match="same file as a protected repository"):
        assert_distinct_file_identity(alias)


def test_the_identity_check_agrees_with_the_scan(tmp_path: Path):
    """A fresh copy's identity is in no protected input's identity."""
    copy = mutable_rom_copy(tmp_path, name="another-copy.gba")
    info = copy.stat()

    assert (info.st_dev, info.st_ino) not in protected_input_identity()


def test_the_rom_gated_mutable_fixture_is_isolated(mutable_rom: Path):
    """The fixture every ROM-gated test uses passes the same check."""
    assert_distinct_file_identity(mutable_rom)
    assert mutable_rom.read_bytes() == canonical_rom_bytes()


def test_reading_the_canonical_image_leaves_it_unchanged():
    """The DETECTIVE half: reading is safe, and the digest is what says so."""
    before = hashlib.sha256(canonical_rom_bytes()).hexdigest()
    canonical_rom_bytes()  # a second read

    assert before == CANONICAL_ROM_SHA256
    assert_canonical_unchanged()
    assert rom_support.canonical_rom_sha256() == CANONICAL_ROM_SHA256


def test_the_protected_input_mirror_matches_the_policy_tuple():
    """The guard scans a copy of the policy list, so a drift between the two narrows it.

    Measured before this was closed: the mirror omitted `dumps`, so
    `protected_input_identity` scanned every protected directory except that one
    and a fixture hard-linked to a ROM under `dumps/` would have passed the
    preventive check. The check is now that the two lists are one list.
    """
    mirror = rom_support.PROTECTED_INPUT_DIRECTORIES

    assert mirror == PROTECTED_INPUT_DIRECTORIES, (
        f"tests/rom_support.PROTECTED_INPUT_DIRECTORIES is {mirror}, but "
        f"tools.webfoot.destination.PROTECTED_INPUT_DIRECTORIES is "
        f"{PROTECTED_INPUT_DIRECTORIES}; make the mirror equal the policy tuple, or "
        "the fixture-identity guard is absent for the names it omits"
    )
