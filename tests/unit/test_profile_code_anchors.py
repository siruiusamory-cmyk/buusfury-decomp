"""The per-profile ``code_anchors`` declaration and each of its refusals.

One node per acceptance drive in PINMAP-03-SCHEMA-V2-CODE-ANCHORS-001. Every
refusal node asserts ``ProfileConfigError`` and matches the reason that refusal
is named for, so a node cannot pass on an unrelated failure. The two falsifiers
the migration order names are here as well: an existing version-1 profile must
still load, and no evidence class outside the five may be admitted.
"""

from pathlib import Path

import pytest
import yaml

from tests.helpers import make_synthetic_rom, profile_for
from tools.webfoot.binary import GbaRomAddress
from tools.webfoot.packaged import packaged_profile
from tools.webfoot.profile import (
    CodeAnchor,
    ProfileConfigError,
    RomProfileCatalog,
)

#: The shipped catalogue's pre-existing scalar fields, read from
#: `config/roms.yaml` at the baseline and pinned here so a loader change that
#: moved one is caught by this module rather than by a downstream codec.
SHIPPED_PROFILES = [
    ("buus_fury_usa_rev0_01c1707f", "buus_fury", "USA", 0, "BG3E", 8388608,
     "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"),
    ("buus_fury_usa_rev0_dcf23468", "buus_fury", "USA", 0, "BG3E", 8388608,
     "15df2fbbe072cc5d28a699ae9af9c56657e290cdb47c92e57d6ce14a01be4b64"),
    ("legacy_of_goku_usa_a3c8c767", "legacy_of_goku", "USA", None, "ALGE", 8388608,
     "3ba9919e26704b0f5fdc2bfabc7f7a0404c71413761d38abcd94224c3bd4b1b9"),
    ("legacy_of_goku_ii_usa_rev0_204142e1", "legacy_of_goku_ii", "USA", 0, "ALFE",
     8388608, "6e6c370c339ec9171cb1956adf837a0d342a197f78964882ef46c3086656ff75"),
]

#: PINMAP-07a. The shipped Buu profile's ten declared anchors, in declaration
#: order, each with the address, state and evidence class a lookup must return.
DECLARED_ANCHORS = (
    CodeAnchor("factory_raw", GbaRomAddress(0x0800FD55), "thumb", "declared"),
    CodeAnchor("script_dispatch_handler", GbaRomAddress(0x0800421F), "thumb", "declared"),
    CodeAnchor("handler_0800421d", GbaRomAddress(0x0800421D), "thumb", "declared"),
    CodeAnchor("handler_0800424f", GbaRomAddress(0x0800424F), "thumb", "declared"),
    CodeAnchor("sibling_factory_08017da3", GbaRomAddress(0x08017DA3), "thumb", "declared"),
    CodeAnchor("sibling_factory_080111a9", GbaRomAddress(0x080111A9), "thumb", "declared"),
    CodeAnchor("dominant_layer_handler", GbaRomAddress(0x08008087), "thumb", "declared"),
    CodeAnchor("absent_layer_handler", GbaRomAddress(0x08007A41), "thumb", "declared"),
    CodeAnchor("terrain_field_layer_handler", GbaRomAddress(0x080088BD), "thumb", "declared"),
    CodeAnchor("entry_class_0800a7a1", GbaRomAddress(0x0800A7A1), "thumb", "declared"),
)


def anchor(**overrides):
    """One well-formed anchor mapping, with any single field replaced."""
    entry = {
        "name": "handler",
        "address": 0x08001234,
        "kind": "thumb",
        "evidence": "ghidra",
    }
    entry.update(overrides)
    return entry


def declared(*entries):
    """A synthetic profile whose mapping carries ``code_anchors``."""
    return profile_for(make_synthetic_rom(), code_anchors=list(entries))


def document(**overrides):
    """A whole version-1 catalogue text around one minimal synthetic profile."""
    mapping = {
        "id": "synthetic_code_anchors",
        "game": "synthetic",
        "region": "test",
        "game_code": "TEST",
        "size": 0x100,
        "sha256": "0" * 64,
    }
    mapping.update(overrides)
    return yaml.safe_dump({"schema_version": 1, "profiles": [mapping]})


def test_well_formed_code_anchors_load_with_every_field():
    profile = declared(
        anchor(name="handler", address=0x08001234, kind="thumb",
               evidence="runtime-proven", role="map handler"),
        anchor(name="factory", address=0x09FFFFFF, kind="arm", evidence="ghidra"),
    )

    assert profile.code_anchors == (
        CodeAnchor("handler", GbaRomAddress(0x08001234), "thumb", "runtime-proven",
                   "map handler"),
        CodeAnchor("factory", GbaRomAddress(0x09FFFFFF), "arm", "ghidra", None),
    )
    assert [entry.name for entry in profile.code_anchors] == ["handler", "factory"]
    assert [entry.address.raw for entry in profile.code_anchors] == [0x08001234, 0x09FFFFFF]
    assert [entry.kind for entry in profile.code_anchors] == ["thumb", "arm"]
    assert [entry.evidence for entry in profile.code_anchors] == ["runtime-proven", "ghidra"]
    assert [entry.role for entry in profile.code_anchors] == ["map handler", None]


def test_absent_code_anchors_key_yields_an_empty_tuple():
    assert profile_for(make_synthetic_rom()).code_anchors == ()


@pytest.mark.parametrize("value", [{"handler": 1}, "handler"], ids=["mapping", "scalar"])
def test_non_list_code_anchors_refuses_naming_the_key(value):
    with pytest.raises(ProfileConfigError, match="code_anchors must be a list"):
        RomProfileCatalog.loads(document(code_anchors=value))


def test_non_mapping_entry_refuses_naming_the_index():
    with pytest.raises(ProfileConfigError, match="code_anchors entry 1 must be a mapping"):
        RomProfileCatalog.loads(document(code_anchors=[anchor(), "handler"]))


def test_unknown_entry_key_refuses_naming_the_key():
    with pytest.raises(ProfileConfigError, match="code_anchors entry 0 contains unexpected fields: capture"):
        RomProfileCatalog.loads(document(code_anchors=[anchor(capture="run.yaml")]))


@pytest.mark.parametrize(
    "entry",
    [
        {"address": 0x08001234, "kind": "arm", "evidence": "declared"},
        anchor(name="   "),
    ],
    ids=["missing-name", "empty-name"],
)
def test_missing_or_empty_name_refuses_naming_the_field(entry):
    with pytest.raises(
        ProfileConfigError,
        match="code_anchors entry 0 name must be a non-empty string",
    ):
        RomProfileCatalog.loads(document(code_anchors=[entry]))


def test_duplicate_anchor_name_refuses_quoting_the_name(tmp_path):
    path = tmp_path / "roms.yaml"
    path.write_text(
        document(code_anchors=[anchor(name="handler"), anchor(name="handler", kind="arm")]),
        encoding="utf-8",
    )

    with pytest.raises(ProfileConfigError, match="duplicate anchor name: 'handler'"):
        RomProfileCatalog.load(path)


@pytest.mark.parametrize("address", ["0x08001234", True], ids=["hex-string", "boolean-true"])
def test_non_integer_address_refuses_naming_the_field(address):
    with pytest.raises(
        ProfileConfigError,
        match="code_anchors anchor 'handler' address must be an integer GBA address",
    ):
        RomProfileCatalog.loads(document(code_anchors=[anchor(address=address)]))


@pytest.mark.parametrize("address", [0x07FFFFFF, 0x0A000000], ids=["below-base", "at-end"])
def test_out_of_window_address_refuses_naming_the_value(address):
    with pytest.raises(
        ProfileConfigError,
        match=f"code_anchors anchor 'handler' address {address} is outside the GBA ROM window",
    ):
        RomProfileCatalog.loads(document(code_anchors=[anchor(address=address)]))


def test_window_boundary_addresses_load():
    profile = declared(
        anchor(name="first_byte", address=0x08000000),
        anchor(name="last_byte", address=0x09FFFFFF),
    )

    assert [entry.address.raw for entry in profile.code_anchors] == [0x08000000, 0x09FFFFFF]


def test_unknown_kind_refuses_quoting_the_value_and_listing_the_supported_set():
    with pytest.raises(
        ProfileConfigError,
        match="kind 'arm7' is not supported; supported: arm, thumb",
    ):
        RomProfileCatalog.loads(document(code_anchors=[anchor(kind="arm7")]))


def test_unknown_evidence_class_refuses_quoting_the_value_and_listing_five():
    with pytest.raises(
        ProfileConfigError,
        match="evidence 'maybe' is not a supported class",
    ) as raised:
        RomProfileCatalog.loads(document(code_anchors=[anchor(evidence="maybe")]))

    message = str(raised.value)
    for supported in ("byte-proven", "ghidra", "runtime-proven", "declared", "inferred"):
        assert supported in message


@pytest.mark.parametrize(
    "evidence",
    ["byte-proven", "ghidra", "runtime-proven", "declared", "inferred"],
)
def test_each_evidence_class_loads(evidence):
    profile = declared(anchor(evidence=evidence))

    assert [entry.evidence for entry in profile.code_anchors] == [evidence]


def test_empty_role_refuses_naming_the_field():
    with pytest.raises(ProfileConfigError, match="role must be a non-empty string"):
        RomProfileCatalog.loads(document(code_anchors=[anchor(role="   ")]))


@pytest.mark.parametrize(
    "path",
    ["config/roms.yaml", "tools/webfoot/data/roms.yaml"],
    ids=["development", "packaged"],
)
def test_each_shipped_catalogue_copy_declares_every_anchor(path):
    text = Path(path).read_text(encoding="utf-8")
    catalog = RomProfileCatalog.loads(text)

    assert [
        (profile.id, profile.game, profile.region, profile.revision,
         profile.game_code, profile.size, profile.sha256)
        for profile in catalog.profiles
    ] == SHIPPED_PROFILES
    assert [profile.code_anchors for profile in catalog.profiles] == [
        DECLARED_ANCHORS, (), (), ()
    ]


@pytest.mark.parametrize(
    "anchor", DECLARED_ANCHORS, ids=[anchor.name for anchor in DECLARED_ANCHORS]
)
def test_a_declared_anchor_resolves_to_its_address_kind_and_evidence(anchor):
    resolved = packaged_profile().require_code_anchor(anchor.name)

    assert isinstance(resolved, CodeAnchor)
    assert resolved == anchor
    assert (resolved.address.raw, resolved.kind, resolved.evidence) == (
        anchor.address.raw, anchor.kind, anchor.evidence
    )


def test_the_factory_raw_anchor_agrees_with_the_declared_placement_type():
    profile = packaged_profile()

    assert profile.require_code_anchor("factory_raw").address.raw == (
        profile.placement_types.factory_raw
    )


def test_the_lookup_carries_the_state_and_evidence_class_unchanged():
    profile = declared(
        anchor(name="factory", address=0x08001234, kind="arm", evidence="runtime-proven")
    )

    resolved = profile.require_code_anchor("factory")
    assert (resolved.kind, resolved.evidence) == ("arm", "runtime-proven")


def test_an_absent_anchor_refuses_naming_the_anchor_and_the_profile():
    profile = packaged_profile()

    with pytest.raises(ProfileConfigError) as raised:
        profile.require_code_anchor("no_such_anchor")
    message = str(raised.value)
    assert "no_such_anchor" in message
    assert profile.id in message


def test_a_profile_declaring_no_anchors_refuses_rather_than_returning_nothing():
    profile = profile_for(make_synthetic_rom())

    assert profile.code_anchors == ()
    with pytest.raises(ProfileConfigError, match="declares no code anchor 'handler'"):
        profile.require_code_anchor("handler")


def test_schema_version_2_document_is_still_refused():
    with pytest.raises(ProfileConfigError, match="requires schema_version: 1"):
        RomProfileCatalog.loads(yaml.safe_dump({"schema_version": 2, "profiles": []}))
