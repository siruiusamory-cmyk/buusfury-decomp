"""Unit tests for the shared authored-image transaction and provenance verifier.

Synthetic only: no ROM, no extracted assets, no private input. The transaction and
the verifier are functions of bytes, a manifest document and one domain hook, so
every generic rule is pinned here in CI - which has no canonical ROM. The real
DragonByte Z accept/reject behaviour is pinned against an emitted ROM in
``tests/integration/test_map_layout_editor_rom.py``.

The toy domain below is deliberately trivial (`field:NNNN` owners over a
synthetic base) so that a failure here is a failure of the shared layer and not of
any one editor's rules.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

from tools.webfoot import authored_image as ai
from tools.webfoot import write as write_sdk
from tools.webfoot.authored_image import (
    AuthoredImageError,
    manifest_path_for,
    normalize_changes,
    save_authored_image,
    staging_path,
    verify_authored_image,
    verify_emitted_image,
)

#: A synthetic 2 KiB base image; its hash plays the canonical image's role.
BASE = bytes(range(256)) * 8
CANONICAL_SHA256 = hashlib.sha256(BASE).hexdigest()
FIELD_BYTES = 4
REASON = "synthetic field replacement"
PROFILE = "toy_rom_profile"


def _change(offset: int, old: bytes, new: bytes, owner: str = "field:0001") -> write_sdk.ByteChange:
    return write_sdk.ByteChange(offset=offset, old=old, new=new, owner=owner, reason=REASON)


def _change_at(offset: int, new: bytes, *, owner: str = "field:0001") -> write_sdk.ByteChange:
    """One bounded write of the synthetic base's own bytes at `offset`."""
    return _change(offset, BASE[offset : offset + FIELD_BYTES], new, owner)


def _check_fields(declared, canonical_image, data):
    """The toy domain's half: an owner names a field number, nothing more."""
    targets = []
    for change in declared:
        if not change.owner.startswith("field:"):
            raise AuthoredImageError(f"foreign owner: {change.owner!r}")
        targets.append(int(change.owner.split(":")[1]))
    return tuple(targets)


def _verify_hook(data, changes):
    """A toy `verify`: the emitted offsets the domain cares about."""
    return tuple(change.offset for change in changes)


VERIFY = _verify_hook


def _source(tmp_path: Path, name: str = "source.gba") -> Path:
    path = tmp_path / name
    path.write_bytes(BASE)
    return path


def _save(tmp_path: Path, changes, *, base: bytes = BASE, **overrides) -> ai.AuthoredImageSave:
    arguments = dict(
        source_path=_source(tmp_path),
        output_path=tmp_path / "out.gba",
        profile_id=PROFILE,
        changes=changes,
        canonical_sha256=CANONICAL_SHA256,
        verify=VERIFY,
    )
    arguments.update(overrides)
    return save_authored_image(base, **arguments)


# --- path conventions --------------------------------------------------------


def test_path_conventions_are_siblings_of_the_image(tmp_path: Path) -> None:
    image = tmp_path / "Dragon Ball Z - Buu's Fury (U) - Edited.gba"
    assert manifest_path_for(image) == image.with_name(
        "Dragon Ball Z - Buu's Fury (U) - Edited.gba.dragonbyte.json"
    )
    assert staging_path(image) == image.with_name(
        ".Dragon Ball Z - Buu's Fury (U) - Edited.gba.webfoot-partial"
    )
    assert staging_path(manifest_path_for(image)).name.startswith(".")


# --- the transaction ---------------------------------------------------------


def test_an_empty_plan_writes_a_byte_identical_copy(tmp_path: Path) -> None:
    saved = _save(tmp_path, ())
    assert saved.no_op
    assert saved.changes == ()
    assert saved.changed_offsets == ()
    assert saved.output_path.read_bytes() == BASE
    assert saved.output_sha256 == CANONICAL_SHA256
    assert saved.output_size == len(BASE)
    # The copy is the canonical image, so it needs no provenance to be trusted;
    # the document is still published, because the save that made it did.
    assert saved.manifest_path.is_file()
    assert not staging_path(saved.output_path).exists()
    assert not staging_path(saved.manifest_path).exists()


def test_an_ordinary_bounded_write_changes_only_its_field(tmp_path: Path) -> None:
    replacement = b"\xDE\xAD\xBE\xEF"
    saved = _save(tmp_path, [_change_at(16, replacement)])
    data = saved.output_path.read_bytes()
    assert not saved.no_op
    assert data[16:20] == replacement
    assert data[:16] == BASE[:16] and data[20:] == BASE[20:]
    assert saved.changed_offsets == (16, 17, 18, 19)
    assert saved.verified == (16,)
    assert len(saved.changes) == 1


def test_the_output_does_not_depend_on_the_order_edits_are_reported_in(
    tmp_path: Path,
) -> None:
    first = _change_at(16, b"\x01\x02\x03\x04", owner="field:0001")
    second = _change_at(32, b"\x05\x06\x07\x08", owner="field:0002")
    forwards = _save(tmp_path, [first, second], output_path=tmp_path / "a.gba")
    backwards = _save(tmp_path, [second, first], output_path=tmp_path / "b.gba")
    assert forwards.output_path.read_bytes() == backwards.output_path.read_bytes()
    assert [change.offset for change in forwards.changes] == [16, 32]
    assert [change.offset for change in backwards.changes] == [16, 32]
    assert (
        forwards.manifest_path.read_bytes() == backwards.manifest_path.read_bytes()
    )


def test_a_duplicate_physical_write_is_collapsed(tmp_path: Path) -> None:
    change = _change_at(16, b"\x11\x22\x33\x44")
    twin = _change(16, change.old, change.new, owner="field:0002")
    assert normalize_changes([twin, change]) == (change,)
    saved = _save(tmp_path, [change, twin])
    assert len(saved.changes) == 1
    assert saved.output_path.read_bytes()[16:20] == change.new
    document = json.loads(saved.manifest_path.read_text(encoding="utf-8"))
    assert len(document["changes"]) == 1
    assert document["changes"][0]["owner"] == "field:0001"


def test_conflicting_physical_writes_fail_closed_before_publication(
    tmp_path: Path,
) -> None:
    first = _change_at(16, b"\x11\x22\x33\x44", owner="field:0001")
    # Same field, different replacement: a contradiction, not a plan.
    conflicting = _change(16, first.old, b"\x55\x66\x77\x88", owner="field:0002")
    with pytest.raises(AuthoredImageError) as excinfo:
        normalize_changes([first, conflicting])
    assert "same field" in str(excinfo.value)

    destination = tmp_path / "out.gba"
    destination.write_bytes(b"the user's previous build")
    with pytest.raises(AuthoredImageError):
        _save(tmp_path, [first, conflicting], output_path=destination)
    # Nothing was published, and nothing was left staged.
    assert destination.read_bytes() == b"the user's previous build"
    assert not staging_path(destination).exists()
    assert list(tmp_path.glob("*webfoot-partial")) == []


@pytest.mark.parametrize("label", ["requested output", "manifest", "staging image", "staging manifest"])
def test_the_source_may_not_be_any_path_the_save_touches(
    tmp_path: Path, label: str
) -> None:
    """The output, the derived manifest and both staging names are all refused."""
    destination = tmp_path / "weird.gba"
    collided = {
        "requested output": destination,
        "manifest": manifest_path_for(destination),
        "staging image": staging_path(destination),
        "staging manifest": staging_path(manifest_path_for(destination)),
    }[label]
    collided.write_bytes(BASE)
    with pytest.raises(AuthoredImageError) as excinfo:
        _save(tmp_path, [_change_at(16, b"\x01\x02\x03\x04")], source_path=collided,
              output_path=destination)
    assert "is the source ROM" in str(excinfo.value)
    # The refusal is total: the source is untouched, and the save created nothing.
    assert collided.read_bytes() == BASE, "the refused save touched the source"
    if collided != staging_path(destination):
        assert not staging_path(destination).exists()
    if collided != staging_path(manifest_path_for(destination)):
        assert not staging_path(manifest_path_for(destination)).exists()
    if collided != destination:
        assert not destination.exists()


def test_an_existing_destination_that_is_the_canonical_image_is_refused(
    tmp_path: Path,
) -> None:
    """A destination that already holds the canonical image is a ROM, not an output.

    The destination is a separate file from the source, so nothing here is an
    alias refusal: only the canonical-copy guard can refuse this save, and it has
    to refuse it before the destination is replaced.
    """
    destination = tmp_path / "out.gba"
    destination.write_bytes(BASE)
    source = tmp_path / "source.gba"
    with pytest.raises(AuthoredImageError) as excinfo:
        _save(tmp_path, [_change_at(16, b"\x01\x02\x03\x04")])
    assert "copy of the canonical ROM" in str(excinfo.value)
    assert destination.read_bytes() == BASE
    assert source.read_bytes() == BASE
    # The refusal is total: no provenance document and no staging artefact.
    assert sorted(p.name for p in tmp_path.iterdir()) == ["out.gba", "source.gba"]


def test_a_missing_source_or_an_unknown_profile_is_refused(tmp_path: Path) -> None:
    change = _change_at(16, b"\x01\x02\x03\x04")
    with pytest.raises(AuthoredImageError):
        _save(tmp_path, [change], source_path=tmp_path / "absent.gba")
    with pytest.raises(AuthoredImageError):
        _save(tmp_path, [change], profile_id="  ")
    with pytest.raises(AuthoredImageError):
        _save(tmp_path, [change], canonical_sha256="ab" * 32)
    # A base that is not the canonical image cannot be the image this plan
    # describes, even when the source file is the real one.
    with pytest.raises(AuthoredImageError) as excinfo:
        _save(tmp_path, [change], base=bytes(len(BASE)))
    assert "base image" in str(excinfo.value)


def test_a_failed_emit_preserves_an_existing_destination(tmp_path: Path, monkeypatch) -> None:
    destination = tmp_path / "out.gba"
    destination.write_bytes(b"the user's previous build")
    manifest = manifest_path_for(destination)
    manifest.write_bytes(b"the user's previous provenance")

    def failing_emit(*args, **kwargs):
        raise write_sdk.WriteError("emit refused")

    monkeypatch.setattr(write_sdk, "emit_image", failing_emit)
    with pytest.raises(write_sdk.WriteError):
        _save(tmp_path, [_change_at(16, b"\x01\x02\x03\x04")], output_path=destination)
    assert destination.read_bytes() == b"the user's previous build"
    assert manifest.read_bytes() == b"the user's previous provenance"
    assert list(tmp_path.glob("*webfoot-partial")) == []


def test_a_failed_verification_preserves_an_existing_destination(tmp_path: Path) -> None:
    destination = tmp_path / "out.gba"
    destination.write_bytes(b"the user's previous build")
    manifest = manifest_path_for(destination)
    manifest.write_bytes(b"the user's previous provenance")

    def failing_verify(data, changes):
        raise AuthoredImageError("verification refused")

    with pytest.raises(AuthoredImageError):
        _save(
            tmp_path,
            [_change_at(16, b"\x01\x02\x03\x04")],
            output_path=destination,
            verify=failing_verify,
        )
    assert destination.read_bytes() == b"the user's previous build"
    assert manifest.read_bytes() == b"the user's previous provenance"
    assert list(tmp_path.glob("*webfoot-partial")) == []


def test_a_failed_publish_leaves_no_temporary_file(tmp_path: Path) -> None:
    destination = tmp_path / "blocked.gba"
    destination.mkdir()  # a directory at the destination makes the final replace fail
    with pytest.raises(OSError):
        _save(tmp_path, [_change_at(16, b"\x01\x02\x03\x04")], output_path=destination)
    assert destination.is_dir()
    assert list(tmp_path.glob("*webfoot-partial")) == []


def test_a_failed_manifest_publish_reports_an_image_without_provenance(
    tmp_path: Path, monkeypatch
) -> None:
    """The image is published first; a provenance publish that then fails says so."""
    real_replace = os.replace
    published: list[Path] = []

    def failing_manifest_publish(source, target):
        published.append(Path(target))
        if len(published) == 2:
            raise OSError("manifest destination refused")
        return real_replace(source, target)

    monkeypatch.setattr(os, "replace", failing_manifest_publish)
    with pytest.raises(AuthoredImageError) as excinfo:
        _save(tmp_path, [_change_at(16, b"\x01\x02\x03\x04")])
    # The failure is reported for what it is: an image on disk without the
    # provenance that would let it reopen, and no staging file left behind.
    assert "provenance could not be published" in str(excinfo.value)
    assert published[1].name.endswith(".dragonbyte.json")
    assert published[0].read_bytes()[16:20] == b"\x01\x02\x03\x04"
    assert not published[1].exists()
    assert list(tmp_path.glob("*webfoot-partial")) == []


def test_a_plan_that_is_not_applicable_is_refused_before_publication(
    tmp_path: Path,
) -> None:
    """An unsupported declaration never reaches an output image."""
    destination = tmp_path / "out.gba"
    destination.write_bytes(b"the user's previous build")
    # 1. The change claims bytes the base does not hold - the plan is not this
    #    image's plan.
    wrong_old = _change(16, b"\xFF\xFF\xFF\xFF", b"\x01\x02\x03\x04")
    with pytest.raises(AuthoredImageError) as excinfo:
        _save(tmp_path, [wrong_old], output_path=destination)
    assert "not applicable" in str(excinfo.value)
    # 2. Overlapping writes to one another.
    overlapping = [
        _change(16, BASE[16:20], b"\x01\x02\x03\x04", owner="field:0001"),
        _change(18, BASE[18:22], b"\x05\x06\x07\x08", owner="field:0002"),
    ]
    with pytest.raises(AuthoredImageError) as excinfo:
        _save(tmp_path, overlapping, output_path=destination)
    assert "not applicable" in str(excinfo.value)
    # 3. A write whose span runs past the end of the image.
    past_end = write_sdk.ByteChange(
        offset=len(BASE) - 2,
        old=b"\x00\x00\x00\x00",
        new=b"\x01\x02\x03\x04",
        owner="field:0003",
        reason=REASON,
    )
    with pytest.raises(AuthoredImageError):
        _save(tmp_path, [past_end], output_path=destination)
    assert destination.read_bytes() == b"the user's previous build"
    assert list(tmp_path.glob("*webfoot-partial")) == []


def test_the_published_manifest_records_the_emitted_digest_and_byte_count(
    tmp_path: Path,
) -> None:
    saved = _save(tmp_path, [_change_at(16, b"\x01\x02\x03\x04")])
    document = json.loads(saved.manifest_path.read_text(encoding="utf-8"))
    data = saved.output_path.read_bytes()
    assert document["schema_version"] == ai.SUPPORTED_SCHEMA_VERSION
    assert document["base"] == {"profile_id": PROFILE, "sha256": CANONICAL_SHA256}
    assert document["output"] == {
        "sha256": hashlib.sha256(data).hexdigest(),
        "size": len(data),
    }
    assert document["output"]["sha256"] == saved.output_sha256
    assert document["changed_byte_count"] == 4


def test_the_byte_level_verification_refuses_a_wrong_size_digest_or_extra_byte(
    tmp_path: Path,
) -> None:
    """The three questions every emitted image must answer, asked directly."""
    saved = _save(tmp_path, [_change_at(16, b"\x01\x02\x03\x04")])
    data = saved.output_path.read_bytes()
    manifest = write_sdk.WriteManifest(
        base_profile_id=PROFILE,
        base_sha256=CANONICAL_SHA256,
        output_sha256=hashlib.sha256(data).hexdigest(),
        output_size=len(data),
        changes=(_change_at(16, b"\x01\x02\x03\x04"),),
    )
    changes = (_change_at(16, b"\x01\x02\x03\x04"),)
    assert verify_emitted_image(BASE, data, changes, manifest) == (16, 17, 18, 19)
    with pytest.raises(AuthoredImageError):
        verify_emitted_image(BASE, data + b"\x00", changes, manifest)
    # A byte that differs outside every requested field, with the manifest's own
    # digest recomputed so that only this rule can refuse it.
    tampered = bytearray(data)
    tampered[0] ^= 0xFF
    tampered_manifest = write_sdk.WriteManifest(
        base_profile_id=PROFILE,
        base_sha256=CANONICAL_SHA256,
        output_sha256=hashlib.sha256(bytes(tampered)).hexdigest(),
        output_size=len(tampered),
        changes=changes,
    )
    with pytest.raises(AuthoredImageError) as excinfo:
        verify_emitted_image(BASE, bytes(tampered), changes, tampered_manifest)
    assert "outside the requested fields" in str(excinfo.value)
    # A manifest whose recorded size is not the image's.
    wrong_size = write_sdk.WriteManifest(
        base_profile_id=PROFILE,
        base_sha256=CANONICAL_SHA256,
        output_sha256=hashlib.sha256(data).hexdigest(),
        output_size=len(data) + 1,
        changes=(),
    )
    with pytest.raises(AuthoredImageError):
        verify_emitted_image(BASE, data, changes, wrong_size)
    # A manifest whose digest is not the image's.
    wrong_digest = write_sdk.WriteManifest(
        base_profile_id=PROFILE,
        base_sha256=CANONICAL_SHA256,
        output_sha256="ab" * 32,
        output_size=len(data),
        changes=(),
    )
    with pytest.raises(AuthoredImageError) as excinfo:
        verify_emitted_image(BASE, data, changes, wrong_digest)
    assert "own digest" in str(excinfo.value)


# --- provenance verification -------------------------------------------------


def _declared(offset: int, old: bytes, new: bytes, owner: str = "field:0001") -> dict:
    return {
        "offset": offset,
        "offset_hex": f"0x{offset:08X}",
        "size": FIELD_BYTES,
        "old": old.hex(),
        "new": new.hex(),
        "owner": owner,
        "reason": REASON,
    }


def _document(
    changes: list[dict],
    *,
    output: bytes,
    base_sha256: str = CANONICAL_SHA256,
    profile_id: str = PROFILE,
    **overrides,
) -> dict:
    document = {
        "schema_version": ai.SUPPORTED_SCHEMA_VERSION,
        "base": {"profile_id": profile_id, "sha256": base_sha256},
        "output": {
            "sha256": hashlib.sha256(output).hexdigest(),
            "size": len(output),
        },
        "changed_byte_count": sum(
            sum(1 for before, after in zip(bytes.fromhex(c["old"]), bytes.fromhex(c["new"]))
                if before != after)
            for c in changes
        ),
        "changes": changes,
    }
    document.update(overrides)
    return document


def _derivative(offset: int = 16, new: bytes = b"\xA1\xA2\xA3\xA4") -> tuple[bytes, dict]:
    """The synthetic canonical image plus one declared four-byte change."""
    data = bytearray(BASE)
    old = bytes(data[offset : offset + FIELD_BYTES])
    data[offset : offset + FIELD_BYTES] = new
    return bytes(data), _declared(offset, old, new)


def _verify(
    tmp_path: Path, data: bytes, document: dict, *, canonical_size: int = len(BASE)
):
    image = tmp_path / "derived.gba"
    image.write_bytes(data)
    manifest_path_for(image).write_text(json.dumps(document), encoding="utf-8")
    return verify_authored_image(
        image,
        canonical_sha256=CANONICAL_SHA256,
        canonical_size=canonical_size,
        field_bytes=FIELD_BYTES,
        expected_reason=REASON,
        check_changes=_check_fields,
    )


def _expanded_derivative(
    *, offset: int = 16, new: bytes = b"\xA1\xA2\xA3\xA4", extra: int = 4096
) -> tuple[bytes, dict]:
    """The canonical image plus one declared change, then generated expansion.

    This is the shape a build emits once authored content no longer fits below
    canonical EOF: `base` bytes first, then generated bytes the canonical image
    never had. Reconstructing the canonical image therefore has to undo the
    declared changes *and* drop the expansion; hashing the whole buffer can only
    ever produce the digest of an image with the expansion still attached.
    """
    data, change = _derivative(offset=offset, new=new)
    expanded = data + bytes([0x5A]) * extra
    return expanded, _document([change], output=expanded)


def test_a_valid_expanded_derivative_verifies(tmp_path: Path) -> None:
    """A 16 MiB-style derivative of an 8 MiB-style base must reopen.

    The declared change is entirely inside the canonical span, the expansion is
    generated padding, and the manifest's output identity matches the file, so
    nothing but the canonical reconstruction can refuse this image.
    """
    data, document = _expanded_derivative()
    assert len(data) > len(BASE), "the fixture really is expanded"

    verified = _verify(tmp_path, data, document, canonical_size=len(BASE))

    assert verified.canonical_image == BASE
    assert len(verified.canonical_image) == len(BASE)


def test_an_expanded_derivative_refuses_an_undeclared_base_mutation(
    tmp_path: Path,
) -> None:
    """Truncating to the canonical span must not hide a real base-region edit.

    The mutation is inside the canonical span and is not declared, and the
    manifest still describes the file it was built for, so reconstruction is the
    only rule that can refuse it. Without the truncation this would be refused
    for the wrong reason (the expansion), which is why the positive control above
    has to pass for this negative to mean anything.
    """
    data, document = _expanded_derivative()
    mutated = bytearray(data)
    mutated[32] ^= 0xFF  # a canonical-span byte, not the declared field at 16
    document["output"]["sha256"] = hashlib.sha256(bytes(mutated)).hexdigest()

    with pytest.raises(AuthoredImageError, match="canonical ROM plus the changes"):
        _verify(tmp_path, bytes(mutated), document, canonical_size=len(BASE))


def test_a_canonical_size_beyond_the_image_is_refused(tmp_path: Path) -> None:
    """A malformed size relationship fails closed rather than silently truncating."""
    data, document = _expanded_derivative()
    with pytest.raises(AuthoredImageError, match="canonical size"):
        _verify(tmp_path, data, document, canonical_size=len(data) + 1)


def test_a_non_positive_canonical_size_is_refused(tmp_path: Path) -> None:
    data, document = _expanded_derivative()
    for bad in (0, -1):
        with pytest.raises(AuthoredImageError, match="canonical size"):
            _verify(tmp_path, data, document, canonical_size=bad)


def test_unexpanded_but_truncated_canonical_size_is_refused(tmp_path: Path) -> None:
    """A size that cuts a canonical image short cannot verify as canonical.

    The image is the real canonical bytes, but the declared span stops before
    EOF, so the digest of that prefix is not the canonical digest. Nothing may
    accept a base span shorter than the base it claims to be.
    """
    data, change = _derivative()
    document = _document([change], output=data)
    with pytest.raises(AuthoredImageError, match="canonical ROM plus the changes"):
        _verify(tmp_path, data, document, canonical_size=len(BASE) - 1)


def test_an_expanded_derivative_with_a_wrong_base_identity_is_refused(
    tmp_path: Path,
) -> None:
    """Expansion must not weaken the base-identity check."""
    data, document = _expanded_derivative()
    document["base"]["sha256"] = "ab" * 32
    with pytest.raises(AuthoredImageError, match="canonical base"):
        _verify(tmp_path, data, document, canonical_size=len(BASE))


def test_an_undeclared_byte_change_is_refused_by_reconstruction(tmp_path: Path) -> None:
    """The decisive rule: undoing the declared changes must reproduce the canonical image.

    Reconstruction is what bounds an accepted derivative without keeping a copy of
    the canonical file, so it needs its own negative control rather than inheriting
    one from a rule that happens to refuse the same file earlier.
    """
    data, change = _derivative()
    # The image carries every declared replacement and the manifest's output
    # identity is recomputed, so no earlier rule can refuse this file: only
    # undoing the declarations can show that it is not canonical plus them.
    payload = bytearray(data)
    payload[64] ^= 0x5A
    undeclared = _document([change], output=bytes(payload))
    with pytest.raises(AuthoredImageError) as excinfo:
        _verify(tmp_path, bytes(payload), undeclared)
    assert "canonical ROM plus the changes" in str(excinfo.value)

    # A declaration whose `old` bytes are valid but are not what the canonical
    # image holds there: restoring them cannot reproduce the canonical image,
    # even though the file does carry the declared replacement.
    stale = _declared(16, b"\x01\x02\x03\x04", bytes.fromhex(change["new"]))
    with pytest.raises(AuthoredImageError) as excinfo:
        _verify(tmp_path, data, _document([stale], output=data))
    assert "canonical ROM plus the changes" in str(excinfo.value)


def test_a_valid_derivative_is_accepted_and_typed_by_the_domain_hook(
    tmp_path: Path,
) -> None:
    data, change = _derivative()
    verified = _verify(tmp_path, data, _document([change], output=data))
    assert verified.profile_id == PROFILE
    assert verified.canonical_sha256 == CANONICAL_SHA256
    assert verified.output_sha256 == hashlib.sha256(data).hexdigest()
    assert verified.canonical_image == BASE
    assert len(verified.changes) == 1
    assert verified.changes[0].target == 1
    assert verified.changes[0].offset == 16
    assert verified.changes[0].new == b"\xA1\xA2\xA3\xA4"


def test_a_tampered_image_is_refused(tmp_path: Path) -> None:
    data, change = _derivative()
    document = _document([change], output=data)
    # A byte changed outside the declared field: the image no longer matches the
    # digest its own provenance states.
    tampered = bytearray(data)
    tampered[0] ^= 0xFF
    with pytest.raises(AuthoredImageError) as excinfo:
        _verify(tmp_path, bytes(tampered), document)
    assert "does not match its provenance" in str(excinfo.value)
    # A byte changed *inside* the declared field, with the manifest re-hashed to
    # match: reconstruction still reaches the canonical image, so only the rule
    # that the field must carry the declared replacement refuses it.
    inside = bytearray(data)
    inside[19] ^= 0x40
    document = _document([change], output=bytes(inside))
    with pytest.raises(AuthoredImageError) as excinfo:
        _verify(tmp_path, bytes(inside), document)
    assert "does not carry the declared value" in str(excinfo.value)
    # And a field that still holds the *old* value while its manifest declares a
    # change is not a derivative either.
    document = _document([change], output=BASE)
    with pytest.raises(AuthoredImageError) as excinfo:
        _verify(tmp_path, BASE, document)
    assert "does not carry the declared value" in str(excinfo.value)


def test_a_tampered_or_unsupported_provenance_document_is_refused(
    tmp_path: Path,
) -> None:
    data, change = _derivative()
    good = _document([change], output=data)
    assert _verify(tmp_path, data, good).canonical_image == BASE

    def rejected(**overrides) -> None:
        document = _document([change], output=data)
        document.update(overrides)
        with pytest.raises(AuthoredImageError):
            _verify(tmp_path, data, document)

    # A base that is not the canonical image, and one that names no profile.
    rejected(base={"profile_id": PROFILE, "sha256": "ab" * 32})
    rejected(base={"profile_id": "", "sha256": CANONICAL_SHA256})
    rejected(base={"sha256": CANONICAL_SHA256})
    rejected(base="elsewhere")
    rejected(base={})
    # An output identity that contradicts the file, or is absent.
    rejected(output={"sha256": "ab" * 32, "size": len(data)})
    rejected(output={"sha256": hashlib.sha256(data).hexdigest()})
    rejected(output="unstructured")
    # An unsupported schema.
    for schema in (2, "1", True, None):
        rejected(schema_version=schema)
    # A declared byte count that contradicts the declared changes.
    rejected(changed_byte_count=999)
    # No change list at all.
    rejected(changes=None)
    rejected(changes=[])
    rejected(changes="changes")
    # A change that is not an object, names no owner, or claims a reason this tool
    # never writes.
    rejected(changes=["nope"])
    rejected(changes=[{**_declared(16, BASE[16:20], b"\x01\x02\x03\x04"), "owner": None}])
    rejected(changes=[{**_declared(16, BASE[16:20], b"\x01\x02\x03\x04"), "reason": "other"}])
    # A field width the domain does not use, and an unaligned offset.
    rejected(changes=[{**_declared(16, BASE[16:20], b"\x01\x02\x03\x04"), "size": 2}])
    rejected(changes=[{**_declared(16, BASE[16:20], b"\x01\x02\x03\x04"), "offset": 17}])
    rejected(changes=[{**_declared(16, BASE[16:20], b"\x01\x02\x03\x04"), "offset": -4}])
    # A bad old/new field, and a change that changes nothing.
    rejected(changes=[{**_declared(16, BASE[16:20], b"\x01\x02\x03\x04"), "old": "zz"}])
    rejected(changes=[{**_declared(16, BASE[16:20], b"\x01\x02\x03\x04"), "old": "00"}])
    rejected(changes=[_declared(16, BASE[16:20], BASE[16:20])])
    # Two changes writing one field.
    rejected(changes=[change, change])
    # A change whose declared span lies outside the image.
    rejected(changes=[_declared(len(BASE) - 2, BASE[-2:] + b"\x00\x00", b"\x01\x02\x03\x04")])


def test_the_declared_changes_must_be_the_ones_the_domain_authored(
    tmp_path: Path,
) -> None:
    """The domain hook sees every declaration and can refuse the whole document."""
    data, change = _derivative()

    def refusing(declared, canonical_image, emitted):
        raise AuthoredImageError(f"not this domain's change: {declared[0].owner!r}")

    image = tmp_path / "derived.gba"
    image.write_bytes(data)
    manifest_path_for(image).write_text(json.dumps(_document([change], output=data)), encoding="utf-8")
    with pytest.raises(AuthoredImageError) as excinfo:
        verify_authored_image(
            image,
            canonical_sha256=CANONICAL_SHA256,
            canonical_size=len(BASE),
            field_bytes=FIELD_BYTES,
            expected_reason=REASON,
            check_changes=refusing,
        )
    assert "not this domain's change" in str(excinfo.value)

    # A hook that answers for the wrong number of changes cannot silently shorten
    # the declared set either.
    image.write_bytes(data)
    manifest_path_for(image).write_text(json.dumps(_document([change], output=data)), encoding="utf-8")
    with pytest.raises(AuthoredImageError) as excinfo:
        verify_authored_image(
            image,
            canonical_sha256=CANONICAL_SHA256,
            canonical_size=len(BASE),
            field_bytes=FIELD_BYTES,
            expected_reason=REASON,
            check_changes=lambda declared, canonical_image, emitted: (),
        )
    assert "answered for 0 of 1" in str(excinfo.value)


def test_a_non_canonical_image_needs_provenance_to_be_accepted(tmp_path: Path) -> None:
    """The canonical image is accepted by identity elsewhere; this path is not it."""
    data, _change = _derivative()
    image = tmp_path / "derived.gba"
    image.write_bytes(data)

    def verify() -> None:
        verify_authored_image(
            image,
            canonical_sha256=CANONICAL_SHA256,
            canonical_size=len(BASE),
            field_bytes=FIELD_BYTES,
            expected_reason=REASON,
            check_changes=_check_fields,
        )

    with pytest.raises(AuthoredImageError) as excinfo:
        verify()
    assert "provenance manifest" in str(excinfo.value)
    assert manifest_path_for(image).name in str(excinfo.value)
    # A document that is not JSON, or not an object, is refused the same way.
    manifest_path_for(image).write_text("not json", encoding="utf-8")
    with pytest.raises(AuthoredImageError) as excinfo:
        verify()
    assert "malformed" in str(excinfo.value)
    manifest_path_for(image).write_text(json.dumps([1, 2]), encoding="utf-8")
    with pytest.raises(AuthoredImageError):
        verify()


def test_an_explicit_manifest_path_is_honoured(tmp_path: Path) -> None:
    data, change = _derivative()
    image = tmp_path / "derived.gba"
    image.write_bytes(data)
    elsewhere = tmp_path / "elsewhere.json"
    elsewhere.write_text(json.dumps(_document([change], output=data)), encoding="utf-8")
    verified = verify_authored_image(
        image,
        manifest_path=elsewhere,
        canonical_sha256=CANONICAL_SHA256,
        canonical_size=len(BASE),
        field_bytes=FIELD_BYTES,
        expected_reason=REASON,
        check_changes=_check_fields,
    )
    assert verified.manifest_path == elsewhere
    assert verified.canonical_image == BASE


# --- a reason string that changed, and the manifests already on disk ---------
#
# MAP-PAINT-ANY-CHUNK-001 widened the layout replacement rule and the map-layout
# editor's reason string changed with it. `expected_reason` therefore takes a
# tuple, so a derivative written by the earlier build keeps verifying instead of
# being refused for naming the older wording. These two tests exist because the
# map-layout suite derives its manifest from the module's own constant, so it
# could not have caught the editor and the verifier disagreeing; these pin both
# spellings explicitly and would fail if either stopped being accepted.


def test_a_manifest_written_with_the_older_reason_still_verifies(tmp_path: Path) -> None:
    data, change = _derivative()
    image = tmp_path / "derived.gba"
    image.write_bytes(data)
    change = {**change, "reason": "existing same-layer chunk replacement"}
    manifest_path_for(image).write_text(
        json.dumps(_document([change], output=data)), encoding="utf-8"
    )

    verified = verify_authored_image(
        image,
        canonical_sha256=CANONICAL_SHA256,
        canonical_size=len(BASE),
        field_bytes=FIELD_BYTES,
        expected_reason=("a newer reason", "existing same-layer chunk replacement"),
        check_changes=_check_fields,
    )

    assert verified.canonical_image == BASE


def test_a_manifest_written_with_the_newer_reason_verifies_too(tmp_path: Path) -> None:
    data, change = _derivative()
    image = tmp_path / "derived.gba"
    image.write_bytes(data)
    change = {**change, "reason": "a newer reason"}
    manifest_path_for(image).write_text(
        json.dumps(_document([change], output=data)), encoding="utf-8"
    )

    verified = verify_authored_image(
        image,
        canonical_sha256=CANONICAL_SHA256,
        canonical_size=len(BASE),
        field_bytes=FIELD_BYTES,
        expected_reason=("a newer reason", "existing same-layer chunk replacement"),
        check_changes=_check_fields,
    )

    assert verified.canonical_image == BASE


def test_a_reason_outside_the_accepted_set_is_still_refused(tmp_path: Path) -> None:
    """Widening the set must not stop refusing a reason this tool never writes."""
    data, change = _derivative()
    image = tmp_path / "derived.gba"
    image.write_bytes(data)
    change = {**change, "reason": "some other tool's reason"}
    manifest_path_for(image).write_text(
        json.dumps(_document([change], output=data)), encoding="utf-8"
    )

    with pytest.raises(AuthoredImageError) as excinfo:
        verify_authored_image(
            image,
            canonical_sha256=CANONICAL_SHA256,
            canonical_size=len(BASE),
            field_bytes=FIELD_BYTES,
            expected_reason=("a newer reason", "existing same-layer chunk replacement"),
            check_changes=_check_fields,
        )

    assert "unsupported change reason" in str(excinfo.value)
