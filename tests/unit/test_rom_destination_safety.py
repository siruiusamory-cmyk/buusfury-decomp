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

OWNER R3 second half, 2026-10-10: a declared protected name is protected before
anything creates it. The policy kept a listed name only when the directory already
existed, and the writers create a destination's parent directory, so a ROM write
could create `exports/` - or `dumps/`, `dump/`, `stock/`, `extracted/` - and publish
inside it. `roms/` refused correctly only because it exists in every checkout.
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
from tools.webfoot.character_swap import write_staged
from tools.webfoot.write import ByteChange, WriteError, emit_image, plan_changes

IGNORE_TEXT = "\n".join(
    (
        "# Commercial ROM images",
        "roms/",
        "roms",
        "*.gba",
        "# Extracted/generated game data",
        "extracted/",
        "dump/",
        "dumps/",
        "stock/",
        "exports/",
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

#: The declared names `checkout` does not create. `roms` is the one it does, which
#: is why the defect was invisible: the only protected name with a directory was
#: the only one that refused.
MISSING_NAMES = tuple(
    name for name in destination_sdk.PROTECTED_INPUT_DIRECTORIES if name != "roms"
)

#: Case-insensitivity is a property of the filesystem, not of the host's name, so
#: the case-variation tests state what they need instead of assuming Windows.
CASE_INSENSITIVE = pytest.mark.skipif(
    os.path.normcase("A") != os.path.normcase("a"),
    reason="this filesystem is case-sensitive, so a case variation is another directory",
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


def test_emit_image_refuses_a_manifest_destination_in_the_protected_directory(
    checkout: Path, tmp_path: Path
):
    """The policy is about the path, so it covers the provenance document too.

    Measured before this was closed: `emit_image` guarded the image destination but
    not the manifest destination, so an explicitly redirected manifest was created
    inside a protected ROM input directory. No ROM could be destroyed through it -
    an existing file there is refused by the overwrite rule - but the rule this
    module states was not true of that path.
    """
    base = _rom(checkout).read_bytes()
    plan = _plan_for(base)
    refused_manifest = checkout / "roms" / "provenance.json"

    with pytest.raises(WriteError, match="protected ROM input directory"):
        emit_image(
            _rom(checkout),
            tmp_path / "derivative.gba",
            plan,
            manifest_path=refused_manifest,
        )

    assert not refused_manifest.exists()


def test_emit_image_still_writes_a_legitimate_derivative(checkout: Path, tmp_path: Path):
    base = _rom(checkout).read_bytes()
    plan = _plan_for(base)
    output = tmp_path / "derivative.gba"
    manifest_path = tmp_path / "derivative.json"

    manifest = emit_image(_rom(checkout), output, plan, manifest_path=manifest_path)

    assert output.exists()
    assert output.read_bytes()[4] == base[4] ^ 0xFF
    assert manifest.output_sha256 == _digest(output.read_bytes())
    # The legitimate companion is still published where the caller asked.
    assert manifest_path.exists()


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


# --- a declared name is protected before anything creates it, OWNER R3 2026-10-10 ---


def _directory_link(target: Path, link: Path) -> None:
    """A directory link at `link`, or a skip where this host refuses to make one.

    `target` may be absent: the link is then dangling, and resolution still follows
    the target text the link carries.
    """
    try:
        os.symlink(target, link, target_is_directory=True)
    except (OSError, NotImplementedError) as exc:  # pragma: no cover - host policy
        pytest.skip(f"this host cannot create a directory link: {exc}")
    if not link.is_symlink():  # pragma: no cover - defensive
        pytest.skip("the host accepted the call but created no directory link")


@pytest.mark.parametrize("name", MISSING_NAMES)
def test_an_existing_protected_directory_is_refused(checkout: Path, name: str):
    """Case 1: the directory is there, so the walk found it before this change too."""
    protected = checkout / name
    protected.mkdir()
    before = _digest(_rom(checkout).read_bytes())

    with pytest.raises(WriteError, match="protected ROM input directory"):
        destination_sdk.refuse_rom_destination(_rom(checkout), protected / "derivative.gba")

    assert list(protected.iterdir()) == []
    assert _digest(_rom(checkout).read_bytes()) == before


@pytest.mark.parametrize("name", MISSING_NAMES)
def test_a_protected_directory_that_does_not_exist_yet_is_refused(checkout: Path, name: str):
    """Case 2, the measured defect: nothing created the directory, so nothing protected it.

    The refusal must name the resolved destination and the protected component, must
    not create the directory, and must leave the source ROM byte-for-byte.
    """
    protected = checkout / name
    destination = protected / "derivative.gba"
    before = _digest(_rom(checkout).read_bytes())

    with pytest.raises(WriteError, match="protected ROM input directory") as refusal:
        destination_sdk.refuse_rom_destination(_rom(checkout), destination)

    message = str(refusal.value)
    assert str(destination.resolve()) in message
    assert str(protected.resolve()) in message
    assert not protected.exists()
    assert _digest(_rom(checkout).read_bytes()) == before


@pytest.mark.parametrize("name", MISSING_NAMES)
def test_a_nested_destination_in_a_missing_protected_directory_is_refused(
    checkout: Path, name: str
):
    """Case 3: the nearest existing ancestor is the repository root, and the rest is read."""
    protected = checkout / name
    destination = protected / "deeper" / "still" / "derivative.gba"

    with pytest.raises(WriteError, match="protected ROM input directory"):
        destination_sdk.refuse_rom_destination(_rom(checkout), destination)

    assert not protected.exists()


def test_a_junction_alias_into_missing_protected_storage_is_refused(checkout: Path):
    """Case 4: an unprotected alias name, resolved onto a protected component that is absent.

    The link is dangling because the protected directory was never created; the
    destination is refused by what the alias points AT, never by the name it was
    reached under.
    """
    protected = checkout / "exports"
    alias = checkout / "route-into-exports"
    _directory_link(protected, alias)

    with pytest.raises(WriteError, match="protected ROM input directory") as refusal:
        destination_sdk.refuse_rom_destination(_rom(checkout), alias / "derivative.gba")

    assert str(protected.resolve()) in str(refusal.value)
    assert not protected.exists()


def test_an_external_alias_resolving_into_protected_storage_is_refused(
    checkout: Path, tmp_path: Path
):
    """Case 4 from outside the checkout: the chosen path leaves, the resolution does not."""
    protected = checkout / "dumps"
    protected.mkdir()
    alias = tmp_path / "a-friendly-output-folder"
    _directory_link(protected, alias)

    with pytest.raises(WriteError, match="protected ROM input directory") as refusal:
        destination_sdk.refuse_rom_destination(_rom(checkout), alias / "derivative.gba")

    assert str(protected.resolve()) in str(refusal.value)
    assert list(protected.iterdir()) == []


@CASE_INSENSITIVE
@pytest.mark.parametrize("spelling", (str.upper, str.title), ids=("upper", "title"))
@pytest.mark.parametrize("name", MISSING_NAMES)
def test_a_case_variation_of_a_missing_name_is_refused(
    checkout: Path, name: str, spelling
):
    """Case 5: a Windows path component is case-insensitive, and the directory is absent."""
    destination = checkout / spelling(name) / "derivative.gba"

    with pytest.raises(WriteError, match="protected ROM input directory"):
        destination_sdk.refuse_rom_destination(_rom(checkout), destination)

    assert not (checkout / name).exists()


@pytest.mark.parametrize("name", MISSING_NAMES)
def test_authorized_build_output_is_allowed_whatever_the_directory_is_called(
    checkout: Path, name: str
):
    """Case 6: `build/` is the authorized derivative location, so the word is not banned."""
    destination = checkout / "build" / name / "derivative.gba"

    destination_sdk.refuse_rom_destination(_rom(checkout), destination)

    assert not destination.exists()


@pytest.mark.parametrize("name", MISSING_NAMES)
def test_an_external_derivative_under_a_protected_name_is_allowed(
    checkout: Path, tmp_path: Path, name: str
):
    """Case 7: the policy is the repository's, not the word's."""
    outside = tmp_path / name / "derivative.gba"

    destination_sdk.refuse_rom_destination(_rom(checkout), outside)

    assert not outside.exists()


def test_emit_image_refuses_a_missing_protected_directory(checkout: Path):
    """The production write path, not a standalone check: the directory is never created.

    `emit_image` refuses both destinations it writes before `publish_new_files`
    reaches its `mkdir(parents=True)`.
    """
    base = _rom(checkout).read_bytes()
    plan = _plan_for(base)
    destination = checkout / "dumps" / "brand-new.gba"
    before = _digest(base)

    with pytest.raises(WriteError, match="protected ROM input directory"):
        emit_image(_rom(checkout), destination, plan)

    assert not (checkout / "dumps").exists()
    assert _digest(_rom(checkout).read_bytes()) == before


def test_emit_image_refuses_a_manifest_in_a_missing_protected_directory(
    checkout: Path, tmp_path: Path
):
    """The provenance document answers the same policy, and nothing is published."""
    plan = _plan_for(_rom(checkout).read_bytes())
    derivative = tmp_path / "derivative.gba"

    with pytest.raises(WriteError, match="protected ROM input directory"):
        emit_image(
            _rom(checkout),
            derivative,
            plan,
            manifest_path=checkout / "exports" / "provenance.json",
        )

    assert not (checkout / "exports").exists()
    assert not derivative.exists()


def test_write_staged_refuses_a_missing_protected_directory(checkout: Path):
    """The publication boundary that calls `mkdir`, reached with the protected name absent."""
    destination = checkout / "stock" / "out.bin"
    before = _digest(_rom(checkout).read_bytes())

    with pytest.raises(WriteError, match="protected ROM input directory"):
        write_staged(destination, b"x", _rom(checkout))

    assert not (checkout / "stock").exists()
    assert _digest(_rom(checkout).read_bytes()) == before


def test_a_refusal_leaves_the_source_the_destination_and_a_neighbour_unchanged(
    checkout: Path,
):
    """Case 8: source ROM, refused destination and a pre-existing neighbour, all unchanged."""
    protected = checkout / "exports"
    protected.mkdir()
    neighbour = protected / "kept.bin"
    neighbour.write_bytes(b"an existing file in a protected directory")
    destination = protected / "brand-new.gba"
    base = _rom(checkout).read_bytes()
    plan = _plan_for(base)
    before_rom = _digest(base)
    before_neighbour = _digest(neighbour.read_bytes())

    with pytest.raises(WriteError, match="protected ROM input directory"):
        emit_image(_rom(checkout), destination, plan)

    assert not destination.exists()
    assert [entry.name for entry in protected.iterdir()] == ["kept.bin"]
    assert _digest(_rom(checkout).read_bytes()) == before_rom
    assert _digest(neighbour.read_bytes()) == before_neighbour
