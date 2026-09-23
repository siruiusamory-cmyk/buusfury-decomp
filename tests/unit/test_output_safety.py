"""Portable tests for the SDK's shared output-path safety authority.

CQA-01-OUTPUT-SAFETY-001. One module owns the question "may this destination be
written?", and these tests pin that authority directly: the filesystem-identity
predicate, the two explicit refusal policies, and the fact that the existing
`emit_image` writer is routed through them rather than through a second
comparison of its own.

Everything here is synthetic. Every test writes only inside `tmp_path`, and no
test opens, hashes or writes the canonical ROM.

A note on aliases that the host cannot provide: hard links and directory
symlinks/junctions are real filesystem features that some environments disable
(a Windows account without the create-symlink privilege, a filesystem without
hard links). Each of those tests **skips explicitly, naming what was
unavailable** - it never degrades into a weaker assertion that would pass while
the invariant went untested.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from tools.webfoot import write as sdk_write
from tools.webfoot.write import (
    OutputPathError,
    WriteError,
    ensure_new_destination,
    ensure_not_source_alias,
    paths_are_the_same_file,
)


# --- the predicate: what counts as the same file -----------------------------


def test_the_identical_path_is_the_same_file(tmp_path: Path):
    source = tmp_path / "source.gba"
    source.write_bytes(b"source bytes")
    assert paths_are_the_same_file(source, source)


def test_a_relative_spelling_resolves_to_the_same_file(tmp_path: Path, monkeypatch):
    """`./x`, `dir/../x` and an absolute path are one file, not three."""
    source = tmp_path / "source.gba"
    source.write_bytes(b"source bytes")
    nested = tmp_path / "deep" / "inner"
    nested.mkdir(parents=True)
    monkeypatch.chdir(nested)
    assert paths_are_the_same_file(source, Path("../../source.gba"))
    assert paths_are_the_same_file(source, Path(os.path.join("..", "..", "source.gba")))
    assert paths_are_the_same_file(Path("../../source.gba"), source)


def test_case_and_separator_variation_follow_the_filesystem(tmp_path: Path):
    """On Windows `SOURCE.GBA` is the file; on POSIX it is a different name.

    The rule is the platform's own, so this asserts the platform-correct answer
    rather than a lowercased comparison the toolkit invented.
    """
    source = tmp_path / "source.gba"
    source.write_bytes(b"source bytes")
    shouty = tmp_path / "SOURCE.GBA"
    case_matters = not (os.name == "nt" or shouty.exists())
    if case_matters:
        assert not paths_are_the_same_file(source, shouty)
    else:
        assert paths_are_the_same_file(source, shouty)


def test_distinct_paths_are_not_the_same_file(tmp_path: Path):
    first = tmp_path / "one.png"
    second = tmp_path / "two.png"
    first.write_bytes(b"one")
    assert not paths_are_the_same_file(first, second)


def test_a_destination_that_does_not_exist_is_compared_by_spelling(tmp_path: Path):
    """The ordinary export case: `samefile` cannot compare what is not there."""
    source = tmp_path / "source.gba"
    source.write_bytes(b"source bytes")
    assert paths_are_the_same_file(source, tmp_path / "absent" / ".." / "source.gba")
    assert not paths_are_the_same_file(source, tmp_path / "absent.png")


def test_a_hard_link_alias_is_the_same_file(tmp_path: Path):
    """Two different names, one file: only filesystem identity catches this."""
    source = tmp_path / "source.gba"
    source.write_bytes(b"source bytes" * 64)
    alias = tmp_path / "alias_with_another_name.bin"
    try:
        os.link(source, alias)
    except (OSError, NotImplementedError, AttributeError) as exc:  # pragma: no cover
        pytest.skip(f"hard links unavailable here: {exc}")
    assert paths_are_the_same_file(source, alias)
    assert paths_are_the_same_file(alias, source)


def test_a_symlink_alias_is_the_same_file(tmp_path: Path):
    source = tmp_path / "source.gba"
    source.write_bytes(b"source bytes")
    link = tmp_path / "link.gba"
    try:
        link.symlink_to(source)
    except (OSError, NotImplementedError) as exc:  # pragma: no cover
        pytest.skip(f"file symlinks unavailable here: {exc}")
    assert paths_are_the_same_file(source, link)
    assert paths_are_the_same_file(link, source)


def test_a_directory_symlink_alias_is_the_same_file(tmp_path: Path):
    """A junction/symlinked *directory* in the middle of the path is an alias too."""
    real = tmp_path / "real"
    real.mkdir()
    source = real / "source.gba"
    source.write_bytes(b"source bytes")
    linked = tmp_path / "linked"
    try:
        linked.symlink_to(real, target_is_directory=True)
    except (OSError, NotImplementedError) as exc:  # pragma: no cover
        pytest.skip(f"directory symlinks/junctions unavailable here: {exc}")
    assert paths_are_the_same_file(source, linked / "source.gba")


# --- the policies: what is refused ------------------------------------------


def test_ensure_not_source_alias_refuses_the_identical_path(tmp_path: Path):
    source = tmp_path / "rom.gba"
    source.write_bytes(b"source bytes")
    before = source.read_bytes()
    with pytest.raises(OutputPathError) as excinfo:
        ensure_not_source_alias(source, source)
    assert "source" in str(excinfo.value)
    assert source.read_bytes() == before


def test_ensure_not_source_alias_refuses_a_hard_link_alias(tmp_path: Path):
    source = tmp_path / "rom.gba"
    source.write_bytes(b"source bytes")
    alias = tmp_path / "hardlink.bin"
    try:
        os.link(source, alias)
    except (OSError, NotImplementedError, AttributeError) as exc:  # pragma: no cover
        pytest.skip(f"hard links unavailable here: {exc}")
    with pytest.raises(OutputPathError):
        ensure_not_source_alias(source, alias)


def test_ensure_not_source_alias_refuses_a_symlink_alias(tmp_path: Path):
    source = tmp_path / "rom.gba"
    source.write_bytes(b"source bytes")
    link = tmp_path / "link.gba"
    try:
        link.symlink_to(source)
    except (OSError, NotImplementedError) as exc:  # pragma: no cover
        pytest.skip(f"file symlinks unavailable here: {exc}")
    with pytest.raises(OutputPathError):
        ensure_not_source_alias(source, link)


def test_ensure_not_source_alias_accepts_a_distinct_path(tmp_path: Path):
    source = tmp_path / "rom.gba"
    source.write_bytes(b"source bytes")
    ensure_not_source_alias(source, tmp_path / "export.png")


def test_ensure_not_source_alias_accepts_a_sibling_in_the_same_directory(tmp_path: Path):
    """Same directory, different name: safe, and the guard must not overreach."""
    source = tmp_path / "rom.gba"
    source.write_bytes(b"source bytes")
    ensure_not_source_alias(source, tmp_path / "rom_backup.gba")


def test_ensure_new_destination_refuses_an_existing_file(tmp_path: Path):
    existing = tmp_path / "already-there.bin"
    existing.write_bytes(b"occupied")
    with pytest.raises(OutputPathError) as excinfo:
        ensure_new_destination(existing)
    assert "existing" in str(excinfo.value)
    assert existing.read_bytes() == b"occupied"


def test_ensure_new_destination_accepts_a_free_path(tmp_path: Path):
    ensure_new_destination(tmp_path / "free.bin")


def test_the_two_policies_are_independent(tmp_path: Path):
    """The point of keeping them separate: one can hold while the other does not.

    A caller may replace an existing artefact and still never be allowed to touch
    its own source - which is impossible to express in a single "is safe" boolean.
    """
    existing = tmp_path / "existing-artefact.png"
    existing.write_bytes(b"the previous export")
    # The overwrite policy refuses it...
    with pytest.raises(OutputPathError):
        ensure_new_destination(existing)
    # ...while the source-alias policy, given a different source, is satisfied.
    other_source = tmp_path / "rom.gba"
    other_source.write_bytes(b"source bytes")
    ensure_not_source_alias(other_source, existing)


def test_every_refusal_is_a_write_error(tmp_path: Path):
    """Existing callers catch `WriteError`/`ValueError`; the new family joins it."""
    source = tmp_path / "rom.gba"
    source.write_bytes(b"source bytes")
    with pytest.raises(WriteError):
        ensure_not_source_alias(source, source)
    with pytest.raises(ValueError):
        ensure_new_destination(source)


# --- the writer is routed through the authority ------------------------------


def test_emit_image_refuses_a_hard_link_alias_of_its_input(tmp_path: Path):
    """The guard the write core applies is the shared one, not a local comparison.

    This is the anti-regression pin for "do not add a second, weaker comparison":
    hard links are exactly what a string comparison cannot see, so a future
    edit that reintroduces `resolve() == resolve()` here fails this test.
    """
    import hashlib as _hashlib

    from tools.webfoot.write import WritePlan

    base = bytes(range(256)) * 4
    source = tmp_path / "base.gba"
    source.write_bytes(base)
    alias = tmp_path / "alias.gba"
    try:
        os.link(source, alias)
    except (OSError, NotImplementedError, AttributeError) as exc:  # pragma: no cover
        pytest.skip(f"hard links unavailable here: {exc}")

    plan = WritePlan(
        base_profile_id="synthetic",
        base_sha256=_hashlib.sha256(base).hexdigest(),
        base_size=len(base),
        changes=(),
    )
    with pytest.raises(WriteError):
        sdk_write.emit_image(source, alias, plan)
    assert source.read_bytes() == base
    assert alias.read_bytes() == base
