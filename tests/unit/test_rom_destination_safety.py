"""Fail-closed ROM destination safety. OWNER R3, 2026-10-09.

The incident this closes: a write aimed at a protected ROM through the ordinary
`Path.write_bytes` was not refused by anything in the SDK, because every existing
guard compared the destination's *content* or its *name* with the source's, and a
hardlink - or a path reached through a junction - has neither in common.

Two layers are tested, because they refuse different things and both must hold:

* `destination.refuse_rom_destination` is the new guard. It refuses by FILE
  IDENTITY (a hardlink, or the protected path itself) and by RESOLVED PATH (a
  protected input directory, reached however it was reached).
* `write.emit_image` and `authored_image.save_authored_image` must refuse a
  protected destination themselves, because the caller cannot be the guard: the
  incident was a direct write that no caller checked. The older source-alias rule
  fires first for the destination-that-is-the-source, so these tests accept either
  refusal - both name a rule and both leave the ROM untouched - and one test
  asserts the new rule's identity message for a destination that is a hardlink
  rather than the source itself.

The checkout under test is a private temporary one: the protected-input policy is
read from a `.gitignore` this file writes, so nothing here reads, writes or even
needs the real repository's ROM inputs.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from tools.webfoot import destination as destination_sdk
from tools.webfoot.authored_image import (
    AuthoredImageError,
    refuse_canonical_destination,
    save_authored_image,
)
from tools.webfoot.write import ByteChange, WriteError, emit_image, plan_changes

IGNORE_TEXT = "\n".join(
    (
        "# Commercial ROM images",
        "roms/",
        "roms",
        "*.gba",
        "build/",
        "",
    )
)

ROM_NAME = "Dragon Ball Z - Buu's Fury (U).gba"
ROM_BYTES = b"protected canonical rom bytes" * 4

#: Either refusal is correct for a destination that IS the source: the older
#: source-alias rule and the new destination rule both name a rule and both refuse
#: before anything is written.
_ANY_REFUSAL = (
    r"protected ROM input|refusing to write the output over the input"
    r"|the requested output path is the source ROM"
)


@pytest.fixture(autouse=True)
def _isolate_destination_policy_cache():
    """Keep one test's protected-input index out of another's.

    `destination` caches the protected-input index per checkout root, which keeps
    the check cheap on every emitted image. These tests point the policy at
    temporary roots, so that cache is cleared around every test in this file rather
    than left for a later test to read.
    """
    destination_sdk._PROTECTED_CACHE.clear()
    yield
    destination_sdk._PROTECTED_CACHE.clear()


@pytest.fixture
def checkout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A private checkout whose `roms/` directory holds one protected ROM."""
    root = tmp_path / "checkout"
    roms = root / "roms"
    roms.mkdir(parents=True)
    (root / ".gitignore").write_text(IGNORE_TEXT, encoding="utf-8")
    (roms / ROM_NAME).write_bytes(ROM_BYTES)
    # One protected-input index per root is cached per process; this root is
    # per-test, so nothing else in the suite sees this checkout.
    monkeypatch.setattr(destination_sdk, "repository_root", lambda: root)
    return root


def _rom(checkout: Path) -> Path:
    return checkout / "roms" / ROM_NAME


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# --- the new guard: identity and resolved path --------------------------------


def test_the_protected_pathname_itself_is_refused(checkout: Path):
    with pytest.raises(WriteError, match="protected ROM input"):
        destination_sdk.refuse_rom_destination(_rom(checkout), _rom(checkout))


def test_a_new_file_in_the_protected_directory_is_refused(checkout: Path):
    """A protected input directory is read-only for new names too.

    The rule the owner stated is scoped to the REPOSITORY's protected input
    directories - the ones the tracked ignore rules designate. A stray output in
    them would be an unversioned ROM-derived artifact beside the immutable input,
    which is what the designation exists to prevent, so the refusal is deliberate
    and its message names the rule.
    """
    new_name = checkout / "roms" / "brand-new.gba"

    with pytest.raises(WriteError, match="protected ROM input directory"):
        destination_sdk.refuse_rom_destination(_rom(checkout), new_name)


def test_a_hardlink_under_another_name_is_refused(checkout: Path, tmp_path: Path):
    """The incident's shape: a different name, a different directory, one file."""
    alias = tmp_path / "alias.gba"
    os.link(_rom(checkout), alias)

    assert alias.name != ROM_NAME
    assert alias.parent != _rom(checkout).parent
    assert os.path.samefile(alias, _rom(checkout))
    with pytest.raises(WriteError, match="same file under a different name"):
        destination_sdk.refuse_rom_destination(_rom(checkout), alias)


def test_a_hardlink_to_another_protected_input_is_refused(checkout: Path, tmp_path: Path):
    """A hardlink to a ROM that is not the caller's own input is protected too.

    This is the case the source-identity rule cannot see: the destination is
    neither the source's path nor a derivative of it, but writing it would still
    truncate a protected ROM the repository holds.
    """
    other = checkout / "roms" / "other-revision.gba"
    other.write_bytes(b"a different protected rom" * 3)
    alias = tmp_path / "other-alias.gba"
    os.link(other, alias)
    source = tmp_path / "unrelated-source.gba"
    source.write_bytes(b"not a protected input at all")

    with pytest.raises(WriteError, match="same file under a different name"):
        destination_sdk.refuse_rom_destination(source, alias)


def test_a_junction_to_the_protected_directory_is_refused(checkout: Path):
    """A directory alias is not a way around the rule; the path is resolved."""
    junction = checkout / "link-to-roms"
    try:
        os.symlink(checkout / "roms", junction, target_is_directory=True)
    except (OSError, NotImplementedError) as exc:  # pragma: no cover - host policy
        pytest.skip(f"this host cannot create a directory link: {exc}")
    if not junction.is_dir():  # pragma: no cover - defensive
        pytest.skip("the host accepted the call but created no directory link")

    with pytest.raises(WriteError, match="protected ROM input directory"):
        destination_sdk.refuse_rom_destination(
            _rom(checkout), junction / "anything.gba"
        )


# --- allowed: the caveat the owner stated -------------------------------------


def test_a_derivative_whose_unprotected_directory_holds_a_rom_is_allowed(
    tmp_path: Path,
):
    """A directory containing a ROM is not itself protected.

    The owner's caveat, as a test: an output directory outside the repository's
    protected inputs is the user's to choose, and a ROM sitting in it must not
    turn every write beside it into a refusal. Nothing here is a repository
    protected input, so no policy applies and no refusal may fire.
    """
    elsewhere = tmp_path / "user-chosen"
    elsewhere.mkdir()
    their_rom = elsewhere / "some rom.gba"
    their_rom.write_bytes(b"a rom in a user directory")

    # The new rule has no opinion, and the older content rule fires only when the
    # destination already IS a canonical copy.
    destination_sdk.refuse_rom_destination(their_rom, elsewhere / "some rom_modified.gba")
    refuse_canonical_destination(elsewhere / "some rom_modified.gba", _digest(ROM_BYTES))


def test_a_distinct_derivative_in_an_unprotected_directory_is_allowed(
    checkout: Path, tmp_path: Path
):
    destination_sdk.refuse_rom_destination(_rom(checkout), tmp_path / "out" / "out.gba")


def test_a_destination_that_does_not_exist_in_an_unprotected_directory_is_allowed(
    checkout: Path, tmp_path: Path
):
    """A nonexistent output is validated by its resolved directory, which is not
    protected here, so it is allowed and is not created by the check."""
    missing = tmp_path / "not-created-yet" / "derivative.gba"

    destination_sdk.refuse_rom_destination(_rom(checkout), missing)

    assert not missing.exists()


# --- the existing digest rule still works -------------------------------------


def test_the_existing_canonical_digest_refusal_still_fires(tmp_path: Path):
    """A clean copy of the canonical ROM is refused by content, as it always was."""
    copy = tmp_path / "second-clean-copy.gba"
    copy.write_bytes(ROM_BYTES)

    with pytest.raises(AuthoredImageError, match="copy of the canonical ROM"):
        refuse_canonical_destination(copy, _digest(ROM_BYTES))


# --- enforced inside the writer, not only by the caller -----------------------


def _plan_for(base: bytes):
    change = ByteChange(
        offset=4,
        old=base[4:6],
        new=bytes([base[4] ^ 0xFF, base[5]]),
        owner="test:change",
        reason="owner R3 destination test",
    )
    return plan_changes(
        base,
        [change],
        profile_id="test_profile",
        base_sha256=_digest(base),
    )


def test_emit_image_refuses_the_protected_pathname(checkout: Path):
    base = _rom(checkout).read_bytes()
    plan = _plan_for(base)
    before = _digest(_rom(checkout).read_bytes())

    with pytest.raises(WriteError, match=_ANY_REFUSAL):
        emit_image(_rom(checkout), _rom(checkout), plan)

    assert _digest(_rom(checkout).read_bytes()) == before


def test_emit_image_refuses_a_new_name_in_the_protected_directory(checkout: Path):
    """The destination does not exist, so only the directory rule can refuse it."""
    base = _rom(checkout).read_bytes()
    plan = _plan_for(base)

    with pytest.raises(WriteError, match="protected ROM input directory"):
        emit_image(_rom(checkout), checkout / "roms" / "brand-new.gba", plan)

    assert not (checkout / "roms" / "brand-new.gba").exists()


def test_emit_image_refuses_a_hardlink_of_a_protected_rom(checkout: Path, tmp_path: Path):
    """The new rule's own message, on a destination the alias rule cannot see."""
    base = _rom(checkout).read_bytes()
    plan = _plan_for(base)
    other = checkout / "roms" / "other-revision.gba"
    other.write_bytes(base)
    alias = tmp_path / "alias.gba"
    os.link(other, alias)
    before = _digest(other.read_bytes())

    with pytest.raises(WriteError, match="same file under a different name"):
        emit_image(_rom(checkout), alias, plan)

    assert _digest(other.read_bytes()) == before
    assert alias.read_bytes() == base


def test_emit_image_still_writes_a_legitimate_derivative(checkout: Path, tmp_path: Path):
    base = _rom(checkout).read_bytes()
    plan = _plan_for(base)
    output = tmp_path / "derivative.gba"

    manifest = emit_image(_rom(checkout), output, plan)

    assert output.exists()
    assert output.read_bytes()[4] == base[4] ^ 0xFF
    assert manifest.output_sha256 == _digest(output.read_bytes())


def test_save_authored_image_refuses_the_protected_pathname(checkout: Path):
    base = _rom(checkout).read_bytes()
    before = _digest(_rom(checkout).read_bytes())

    with pytest.raises((WriteError, AuthoredImageError), match=_ANY_REFUSAL):
        save_authored_image(
            base,
            source_path=_rom(checkout),
            output_path=_rom(checkout),
            profile_id="test_profile",
            changes=[
                ByteChange(
                    offset=4,
                    old=base[4:6],
                    new=bytes([base[4] ^ 0xFF, base[5]]),
                    owner="test:change",
                    reason="owner R3 destination test",
                )
            ],
            canonical_sha256=_digest(base),
            verify=lambda data, changes: None,
        )

    assert _digest(_rom(checkout).read_bytes()) == before
