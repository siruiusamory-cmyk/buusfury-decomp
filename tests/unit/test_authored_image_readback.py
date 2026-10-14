from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from tools.webfoot import authored_image as ai
from tools.webfoot import write as write_sdk
from tools.webfoot.authored_image import AuthoredImageError

BASE = bytes(range(256)) * 8
CANONICAL_SHA256 = hashlib.sha256(BASE).hexdigest()
PROFILE = "toy_rom_profile"
FIELD = 0x40
FIELD_BYTES = 4
NEW_FIELD = b"\xEE\xEE\xEE\xEE"


def edit(offset: int = FIELD, new: bytes = NEW_FIELD) -> write_sdk.ByteChange:
    return write_sdk.ByteChange(
        offset=offset,
        old=BASE[offset : offset + len(new)],
        new=new,
        owner="field:0001",
        reason="readback fixture",
    )


def source(tmp_path: Path, name: str = "source.gba") -> Path:
    path = tmp_path / name
    path.write_bytes(BASE)
    return path


def keep(data: bytes, declared: tuple[write_sdk.ByteChange, ...]) -> None:
    return None


def save(tmp_path: Path, *, changes=(), decoder=None, destination: str = "out.gba", **overrides):
    arguments = dict(
        source_path=source(tmp_path),
        output_path=tmp_path / destination,
        profile_id=PROFILE,
        changes=changes,
        canonical_sha256=CANONICAL_SHA256,
        verify=keep,
        decode=decoder,
    )
    arguments.update(overrides)
    return ai.save_authored_image(BASE, **arguments)


def manifest_for(saved: ai.AuthoredImageSave) -> write_sdk.WriteManifest:
    return write_sdk.WriteManifest(
        base_profile_id=PROFILE,
        base_sha256=CANONICAL_SHA256,
        output_sha256=saved.output_sha256,
        output_size=saved.output_size,
        changes=saved.changes,
    )


def test_readback_re_parses_the_published_image_and_matches_its_manifest(tmp_path):
    saved = save(
        tmp_path,
        changes=(edit(),),
        decoder=lambda data: data[FIELD : FIELD + FIELD_BYTES],
    )
    published = tmp_path / "out.gba"
    assert published.is_file()
    assert published.stat().st_size == saved.output_size
    assert saved.readback.decoded == NEW_FIELD
    assert saved.readback.sha256 == saved.output_sha256
    assert saved.readback.size == saved.output_size
    assert saved.readback.changed == tuple(range(FIELD, FIELD + FIELD_BYTES))

    report = ai.readback(
        published,
        manifest=manifest_for(saved),
        decode=lambda data: data[FIELD : FIELD + FIELD_BYTES],
    )
    assert report.decoded == NEW_FIELD
    assert report.changed == saved.readback.changed
    assert report.sha256 == hashlib.sha256(published.read_bytes()).hexdigest()


def test_readback_names_the_first_offset_that_disagrees_with_the_manifest(tmp_path):
    saved = save(tmp_path, changes=(edit(),))
    published = tmp_path / "out.gba"
    tampered = bytearray(published.read_bytes())
    tampered[FIELD + 2] ^= 0xFF
    published.write_bytes(bytes(tampered))

    with pytest.raises(AuthoredImageError) as error:
        ai.readback(published, manifest=manifest_for(saved))

    assert f"0x{FIELD + 2:08X}" in str(error.value)
    assert "0xEE" in str(error.value)


def test_readback_refuses_a_byte_changed_outside_the_declared_fields(tmp_path):
    saved = save(tmp_path, changes=(edit(),))
    published = tmp_path / "out.gba"
    tampered = bytearray(published.read_bytes())
    tampered[-1] ^= 0xFF
    published.write_bytes(bytes(tampered))

    with pytest.raises(AuthoredImageError) as error:
        ai.readback(published, manifest=manifest_for(saved))

    assert "hashes to" in str(error.value)
    assert saved.output_sha256 in str(error.value)


def test_an_empty_plan_reports_a_byte_identical_output_and_publishes_it(tmp_path):
    saved = save(tmp_path, changes=(), decoder=lambda data: len(data))
    published = tmp_path / "out.gba"

    assert saved.no_op is True
    assert saved.readback.changed == ()
    assert saved.readback.decoded == len(BASE)
    assert published.read_bytes() == BASE
    assert saved.manifest_path.is_file()
    assert not ai.staging_path(published).exists()
    assert not ai.staging_path(saved.manifest_path).exists()


def test_the_emitter_refuses_an_existing_destination_and_names_it(tmp_path):
    destination = tmp_path / "out.gba"
    destination.write_bytes(b"occupied")
    plan = write_sdk.plan_changes(
        BASE, (), profile_id=PROFILE, base_sha256=CANONICAL_SHA256
    )

    with pytest.raises(write_sdk.OutputPathError) as error:
        write_sdk.emit_image(source(tmp_path), destination, plan)

    assert str(destination) in str(error.value)
    assert destination.read_bytes() == b"occupied"


def test_the_save_refuses_every_alias_of_the_source_before_the_emitter_runs(
    tmp_path, monkeypatch
):
    source_path = source(tmp_path)
    aliases: list[tuple[str, Path]] = [
        ("the source itself", source_path),
        ("a relative spelling", Path(os.path.relpath(source_path, Path.cwd()))),
    ]
    linked = tmp_path / "linked.gba"
    os.link(source_path, linked)
    aliases.append(("a hard link", linked))
    if os.name == "nt":
        aliases.append(("a different case", Path(str(source_path).upper())))

    emitted: list[object] = []
    monkeypatch.setattr(ai.write_sdk, "emit_image", lambda *a, **k: emitted.append(a))
    for label, destination in aliases:
        with pytest.raises((AuthoredImageError, write_sdk.WriteError)):
            ai.save_authored_image(
                BASE,
                source_path=source_path,
                output_path=destination,
                profile_id=PROFILE,
                changes=(edit(),),
                canonical_sha256=CANONICAL_SHA256,
                verify=keep,
            )
        assert emitted == [], label


def test_the_emitter_refuses_an_alias_of_the_source_and_names_both_paths(tmp_path):
    source_path = source(tmp_path)
    linked = tmp_path / "linked.gba"
    os.link(source_path, linked)
    plan = write_sdk.plan_changes(
        BASE, (), profile_id=PROFILE, base_sha256=CANONICAL_SHA256
    )

    with pytest.raises(write_sdk.OutputPathError) as error:
        write_sdk.emit_image(source_path, linked, plan)

    assert str(source_path) in str(error.value)


def test_a_crash_before_the_publish_leaves_no_destination_and_the_base_unchanged(
    tmp_path, monkeypatch
):
    source_path = source(tmp_path)
    destination = tmp_path / "out.gba"
    before = source_path.read_bytes()

    def crash(*args, **kwargs):
        raise OSError("injected between the staged write and the publish")

    monkeypatch.setattr(ai.os, "replace", crash)

    with pytest.raises(OSError):
        save(tmp_path, changes=(edit(),), source_path=source_path)

    assert not destination.exists()
    assert not ai.manifest_path_for(destination).exists()
    assert not ai.staging_path(destination).exists()
    assert source_path.read_bytes() == before
