"""The patch service: the source gate, the path policy, and the provenance record.

The happy path of `export_patch` needs a real image and a real project build, so it
is proved in `tests/integration/test_patch_export_rom.py`. What is proved here is
everything that must hold *before* a build runs and everything that must hold when
it does not: which source is acceptable, where an output may go, that a refused
export cannot damage what is already there, and that the provenance record and the
patch footer cannot disagree about the two images.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

import pytest

from tests.helpers import make_synthetic_rom, profile_for
from tools.webfoot.formats.bps import encode, inspect
from tools.webfoot.patch import (
    PATCH_METADATA_SCHEMA,
    PatchSourceError,
    PatchVerificationError,
    export_patch,
    patch_metadata,
    read_patch_metadata,
    require_verified_source,
    verify_patch,
)
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.release_identity import PRODUCT_NAME, PRODUCT_VERSION
from tools.webfoot.rom import identify_rom
from tools.webfoot.write import OutputPathError, publish_new_files


@pytest.fixture
def synthetic(tmp_path):
    """A catalogued synthetic image, and a project directory that does not exist.

    The project is never reached by the tests here, which is the point: every
    refusal below happens before a build would start.
    """
    data = make_synthetic_rom()
    rom = tmp_path / "synthetic.gba"
    rom.write_bytes(data)
    catalog = RomProfileCatalog([profile_for(data)])
    return rom, catalog, tmp_path / "project"


# --- the source gate --------------------------------------------------------


def test_an_uncatalogued_image_is_refused(tmp_path):
    rom = tmp_path / "unknown.gba"
    rom.write_bytes(make_synthetic_rom())
    with pytest.raises(PatchSourceError, match="UNKNOWN"):
        require_verified_source(rom, RomProfileCatalog([]))


def test_a_verifying_catalog_is_accepted(synthetic):
    rom, catalog, _ = synthetic
    identification = require_verified_source(rom, catalog)
    assert identification.profile_match.profile.id == "synthetic_exact"


def test_export_refuses_an_uncatalogued_source_before_building_anything(synthetic):
    rom, _catalog, project = synthetic
    output = rom.parent / "mod.bps"
    with pytest.raises(PatchSourceError, match="no patch was produced"):
        export_patch(project, rom, output, RomProfileCatalog([]))
    assert not output.exists()
    assert not project.exists()


# --- the output path policy runs first --------------------------------------


def test_an_output_that_is_the_source_is_refused(tmp_path):
    """Refused before the source is even opened: the policy is total."""
    missing = tmp_path / "not-there.gba"
    with pytest.raises(OutputPathError, match="can never be an output destination"):
        export_patch(tmp_path / "project", missing, missing, RomProfileCatalog([]))


def test_an_existing_output_is_refused_and_left_untouched(synthetic):
    rom, catalog, project = synthetic
    output = rom.parent / "mod.bps"
    previous = b"a patch that was already here"
    output.write_bytes(previous)

    with pytest.raises(OutputPathError, match="refusing to overwrite"):
        export_patch(project, rom, output, catalog)
    assert output.read_bytes() == previous


def test_an_existing_output_is_refused_by_the_source_alias_rule_first(synthetic):
    """The alias rule is asked first, so a refusal names the source, not an overwrite."""
    rom, catalog, project = synthetic
    with pytest.raises(OutputPathError, match="input image"):
        export_patch(project, rom, rom, catalog)


# --- verification -----------------------------------------------------------


def test_a_truncated_patch_is_refused_before_the_source_is_read(tmp_path):
    """The patch is parsed first, so a broken file is reported as a broken file."""
    truncated = tmp_path / "broken.bps"
    truncated.write_bytes(b"BPS1" + b"\x00" * 4)
    with pytest.raises(ValueError, match="at least"):
        verify_patch(truncated, tmp_path / "missing.gba", RomProfileCatalog([]))


def test_a_patch_without_a_provenance_record_is_refused():
    patch = encode(b"source", b"target")
    with pytest.raises(PatchVerificationError, match="no readable provenance"):
        read_patch_metadata(patch)


def test_a_provenance_record_that_is_not_json_is_refused():
    patch = encode(b"source", b"target", b"not a record")
    with pytest.raises(PatchVerificationError, match="no readable provenance"):
        read_patch_metadata(patch)


def test_a_provenance_record_with_no_schema_is_refused():
    patch = encode(b"source", b"target", b'{"project": "authored"}')
    with pytest.raises(PatchVerificationError, match="no integer schema version"):
        read_patch_metadata(patch)


def test_a_provenance_record_whose_schema_is_not_a_number_is_refused():
    """A string or a null schema must be a refusal, not a comparison error."""
    for schema in ('"2"', "null", "true", "[]"):
        patch = encode(
            b"source", b"target", f'{{"schema_version": {schema}}}'.encode("utf-8")
        )
        with pytest.raises(PatchVerificationError, match="no integer schema version"):
            read_patch_metadata(patch)


def test_a_newer_provenance_schema_is_refused():
    patch = encode(
        b"source",
        b"target",
        json.dumps({"schema_version": PATCH_METADATA_SCHEMA + 1}).encode("utf-8"),
    )
    with pytest.raises(PatchVerificationError, match="newer than this toolkit"):
        read_patch_metadata(patch)


def test_a_verified_source_that_changed_under_the_read_is_refused(synthetic):
    rom, catalog, _ = synthetic
    identification = identify_rom(rom, catalog)
    rom.write_bytes(make_synthetic_rom(title="CHANGED"))
    with pytest.raises(PatchSourceError, match="changed while it was being read"):
        from tools.webfoot.patch import _read_verified_source

        _read_verified_source(rom, identification)


# --- the provenance record --------------------------------------------------


def _metadata_for(rom, catalog, source: bytes, target: bytes) -> bytes:
    identification = identify_rom(rom, catalog)
    from tools.webfoot.formats.bps import crc32
    from tools.webfoot.patch import _digest

    return patch_metadata(
        project_name="authored",
        project_format_version=1,
        identification=identification,
        base_bytes=source,
        target_sha256=_digest(target),
        target_size=len(target),
        target_crc32=crc32(target),
    )


def test_the_provenance_record_is_deterministic(synthetic):
    rom, catalog, _ = synthetic
    source = rom.read_bytes()
    target = source[:100] + b"changed" + source[107:]
    assert _metadata_for(rom, catalog, source, target) == _metadata_for(
        rom, catalog, source, target
    )


def test_the_provenance_record_names_the_product_the_project_and_both_images(
    synthetic,
):
    rom, catalog, _ = synthetic
    source = rom.read_bytes()
    target = source[:100] + b"changed" + source[107:]
    document = json.loads(_metadata_for(rom, catalog, source, target))

    assert document["schema_version"] == PATCH_METADATA_SCHEMA
    assert document["patch_format"] == "bps"
    assert document["product"] == {"name": PRODUCT_NAME, "version": PRODUCT_VERSION}
    assert document["project"] == {"name": "authored", "format_version": 1}
    assert document["base"]["profile_id"] == "synthetic_exact"
    assert document["base"]["sha256"] == hashlib.sha256(source).hexdigest()
    assert document["base"]["size"] == len(source)
    assert document["target"]["sha256"] == hashlib.sha256(target).hexdigest()
    assert document["target"]["size"] == len(target)


def test_verification_refuses_a_record_that_names_another_target(synthetic):
    """A lying provenance record must not be printed as if it were proved.

    The record is the only reason to trust a patch a stranger sent, so a record
    that disagrees with the bytes the patch actually rebuilds is a refusal, not a
    footnote.
    """
    rom, catalog, _ = synthetic
    source = rom.read_bytes()
    target = source[:100] + b"changed" + source[107:]
    document = json.loads(_metadata_for(rom, catalog, source, target))
    document["target"]["sha256"] = "0" * 64
    patch = rom.parent / "lying-target.bps"
    patch.write_bytes(
        encode(
            source,
            target,
            json.dumps(document, sort_keys=True, separators=(",", ":")).encode(),
        )
    )

    with pytest.raises(PatchVerificationError, match="target sha256"):
        verify_patch(patch, rom, catalog)


def test_verification_refuses_a_record_that_names_another_source(synthetic):
    rom, catalog, _ = synthetic
    source = rom.read_bytes()
    target = source[:100] + b"changed" + source[107:]
    document = json.loads(_metadata_for(rom, catalog, source, target))
    document["base"]["sha256"] = "1" * 64
    patch = rom.parent / "lying-base.bps"
    patch.write_bytes(
        encode(
            source,
            target,
            json.dumps(document, sort_keys=True, separators=(",", ":")).encode(),
        )
    )

    with pytest.raises(PatchVerificationError, match="source sha256"):
        verify_patch(patch, rom, catalog)


def test_verification_accepts_a_patch_that_carries_no_record_of_ours(synthetic):
    """A patch made elsewhere has no DragonByte Z record, and is still verifiable."""
    rom, catalog, _ = synthetic
    source = rom.read_bytes()
    target = source[:100] + b"changed" + source[107:]
    patch = rom.parent / "foreign.bps"
    patch.write_bytes(encode(source, target, b"<a foreign metadata block>"))

    verification = verify_patch(patch, rom, catalog)

    assert verification.target_sha256 == hashlib.sha256(target).hexdigest()
    with pytest.raises(PatchVerificationError):
        read_patch_metadata(patch.read_bytes())


def test_the_provenance_record_and_the_patch_footer_agree(synthetic):
    rom, catalog, _ = synthetic
    source = rom.read_bytes()
    target = source[:100] + b"changed" + source[107:]
    metadata = _metadata_for(rom, catalog, source, target)

    header = inspect(encode(source, target, metadata))
    document = json.loads(metadata)
    assert document["base"]["crc32"] == f"{header.source_crc32:08x}"
    assert document["target"]["crc32"] == f"{header.target_crc32:08x}"
    assert document["base"]["size"] == header.source_size
    assert document["target"]["size"] == header.target_size


def test_the_provenance_record_carries_no_path_or_user_name(synthetic):
    rom, catalog, _ = synthetic
    source = rom.read_bytes()
    text = _metadata_for(rom, catalog, source, source[:50] + b"x" * 10).decode("utf-8")
    assert str(rom.parent) not in text
    assert "\\" not in text
    assert not re.search(r"[A-Za-z]:[\\/]", text)
    assert "log1-remake" not in text


# --- publishing -------------------------------------------------------------


def test_publishing_refuses_to_replace_an_existing_file(tmp_path):
    destination = tmp_path / "mod.bps"
    destination.write_bytes(b"previous")
    with pytest.raises(OSError):
        publish_new_files([(destination, b"new")])
    assert destination.read_bytes() == b"previous"
    assert sorted(path.name for path in tmp_path.iterdir()) == ["mod.bps"]


def test_publishing_every_file_or_none_of_them(tmp_path):
    first = tmp_path / "first.bps"
    second = tmp_path / "second.bps"
    second.write_bytes(b"previous")

    with pytest.raises(OSError):
        publish_new_files([(first, b"first bytes"), (second, b"second bytes")])

    assert not first.exists(), "a failed publish must roll back what it published"
    assert second.read_bytes() == b"previous"
    assert sorted(path.name for path in tmp_path.iterdir()) == ["second.bps"]


def test_publishing_creates_a_missing_parent_directory(tmp_path):
    destination = tmp_path / "nested" / "deeper" / "mod.bps"
    publish_new_files([(destination, b"patch bytes")])
    assert destination.read_bytes() == b"patch bytes"


def test_a_derivative_cannot_be_named_as_the_output():
    """The derivative is staged in a directory the caller never names.

    Stated as a test because the ticket asks for it explicitly: there is no
    argument through which a caller could name the derivative, so no output path
    can alias it. If a derivative parameter is ever added, this fails and the
    alias rule has to be written with it.
    """
    import inspect as inspect_module

    from tools.webfoot import patch as patch_module

    parameters = set(inspect_module.signature(patch_module.export_patch).parameters)
    assert parameters == {"project_dir", "rom_path", "output_path", "catalog"}


# --- the command line surface ------------------------------------------------


def test_the_cli_verifies_a_patch_and_prints_its_provenance(tmp_path, capsys):
    """The supported command, over a synthetic ROM the catalog can verify."""
    from tests.helpers import write_catalog
    from tools.webfoot.cli import main as cli_main

    data = make_synthetic_rom()
    rom = tmp_path / "synthetic.gba"
    rom.write_bytes(data)
    catalog_path = tmp_path / "roms.yaml"
    write_catalog(catalog_path, [profile_for(data)])

    target = data[:100] + b"changed" + data[107:]
    catalog = RomProfileCatalog([profile_for(data)])
    metadata = _metadata_for(rom, catalog, data, target)
    patch = tmp_path / "mod.bps"
    patch.write_bytes(encode(data, target, metadata))

    code = cli_main(
        [
            "--profiles", str(catalog_path),
            "patch", "verify", str(patch), "--rom", str(rom),
        ]
    )
    printed = capsys.readouterr().out

    assert code == 0
    assert "COMPLETE" in printed
    assert "synthetic_exact" in printed
    assert hashlib.sha256(target).hexdigest() in printed


def test_the_cli_refuses_a_patch_made_for_another_source(tmp_path, capsys):
    from tests.helpers import write_catalog
    from tools.webfoot.cli import main as cli_main

    data = make_synthetic_rom()
    rom = tmp_path / "synthetic.gba"
    rom.write_bytes(data)
    catalog_path = tmp_path / "roms.yaml"
    write_catalog(catalog_path, [profile_for(data)])

    other = make_synthetic_rom(title="OTHER")
    patch = tmp_path / "foreign.bps"
    patch.write_bytes(encode(other, other[:50] + b"x" * 10))

    code = cli_main(
        [
            "--profiles", str(catalog_path),
            "patch", "verify", str(patch), "--rom", str(rom),
        ]
    )

    assert code == 2
    assert "error:" in capsys.readouterr().err
