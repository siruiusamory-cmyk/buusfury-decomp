"""CQA-03: the atlas/ROM identity contract, and the Workbench refusal it drives.

The defect these cover: `Session.open_rom` identified the ROM, resolved the
profile, loaded whatever `build/atlas/atlas.jsonl` it found and assigned it -
never comparing the atlas's own `profile_id` / `base_sha256` with the identity
just verified. Every offset, coverage class and `VERIFIED_FREE` span then
described bytes that were not there.

Nothing here needs a second commercial ROM. The identification is stubbed to a
verified catalog profile and only the atlas identity is varied, so the matrix
below is portable and runs on any checkout.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from tools.webfoot.atlas import (
    VERIFIED_FREE,
    Atlas,
    Confidence,
    CoverageMap,
    CoverageSpan,
)
from tools.webfoot.hashing import RomHashes
from tools.webfoot.layout import Provenance
from tools.webfoot.profile import (
    AtlasIdentity,
    AtlasIdentityMismatch,
    MapEntryTableProfile,
    ProfileConfigError,
    ProfileMatch,
    RomProfileCatalog,
    VerificationStatus,
)
from tools.webfoot.rom import RomIdentification
from tools.webfoot.workbench import session as session_mod
from tools.webfoot.workbench.session import Session, SessionError

BUU = "buus_fury_usa_rev0_01c1707f"
#: A second catalogued profile. Only its id and hash are used; no image of it is
#: read, which is the point - the mismatch is detectable from identity alone.
LOGII = "legacy_of_goku_ii_usa_rev0_204142e1"
IMAGE_SIZE = 8_388_608


@pytest.fixture
def catalog() -> RomProfileCatalog:
    return RomProfileCatalog.load("config/roms.yaml")


@pytest.fixture
def buu(catalog):
    return next(p for p in catalog.profiles if p.id == BUU)


@pytest.fixture
def logii(catalog):
    return next(p for p in catalog.profiles if p.id == LOGII)


def _atlas(profile_id: str, base_sha256: str) -> Atlas:
    """A minimal but structurally valid atlas declaring one identity."""
    coverage = CoverageMap.single(
        IMAGE_SIZE,
        "UNKNOWN",
        Confidence.OBSERVED,
        Provenance(profile_id, base_sha256, "cqa-03-15 test fixture"),
    )
    return Atlas(profile_id, base_sha256, IMAGE_SIZE, coverage)


def _drive(catalog, tmp_path: Path, *, atlas: Atlas, profile):
    """Call the real `open_rom`, stubbing only identification and the artifact.

    `_default_atlas_directory` and `load_atlas` are replaced so the session
    reads the fixture atlas; `identify_rom` is replaced so a verified profile is
    resolved without a commercial image. Everything else is the production path.
    """
    rom_path = tmp_path / "fixture.gba"
    rom_path.write_bytes(b"\x00" * IMAGE_SIZE)
    atlas_dir = tmp_path / "atlas"
    atlas_dir.mkdir(parents=True, exist_ok=True)
    (atlas_dir / "atlas.jsonl").write_text("", encoding="utf-8")

    real_identify = session_mod.identify_rom

    def fake_identify(path, cat):
        real = real_identify(path, cat)
        return RomIdentification(
            path=real.path,
            size=IMAGE_SIZE,
            hashes=RomHashes(
                crc32=profile.crc32 or "00000000",
                md5=profile.md5 or "0" * 32,
                sha1=profile.sha1 or "0" * 40,
                sha256=profile.sha256,
            ),
            header=real.header,
            profile_match=ProfileMatch(
                status=VerificationStatus.VERIFIED,
                profile=profile,
                reason="stubbed: CQA-03-15 atlas identity test",
            ),
        )

    saved = (
        session_mod.identify_rom,
        session_mod._default_atlas_directory,
        session_mod.load_atlas,
    )
    session_mod.identify_rom = fake_identify
    session_mod._default_atlas_directory = lambda: atlas_dir
    session_mod.load_atlas = lambda path: atlas
    try:
        session = Session()
        session.open_rom(rom_path, catalog)
        return session, None
    except SessionError as exc:
        return Session(), exc
    finally:
        (
            session_mod.identify_rom,
            session_mod._default_atlas_directory,
            session_mod.load_atlas,
        ) = saved


# --- the contract itself: A, B, C, F, G ---------------------------------------


def test_A_matching_profile_and_base_is_accepted(buu):
    atlas = _atlas(buu.id, buu.sha256)
    assert buu.require_identity(atlas) == buu.identity


def test_A_accepts_a_differently_cased_hash(buu):
    """The catalog normalises to lowercase; the comparison must too."""
    atlas = _atlas(buu.id, buu.sha256.upper())
    assert buu.require_identity(atlas).sha256 == buu.sha256


def test_B_wrong_profile_id_is_refused(buu, logii):
    """Two catalogued profiles, the same image bytes: the id alone is decisive."""
    atlas = _atlas(logii.id, buu.sha256)
    with pytest.raises(AtlasIdentityMismatch) as excinfo:
        buu.require_identity(atlas)
    assert buu.id in str(excinfo.value)
    assert logii.id in str(excinfo.value)


def test_C_correct_profile_id_wrong_base_sha_is_refused(buu, logii):
    """The narrower mismatch the ticket names: right profile, wrong base."""
    atlas = _atlas(buu.id, logii.sha256)
    with pytest.raises(AtlasIdentityMismatch) as excinfo:
        buu.require_identity(atlas)
    assert buu.sha256 in str(excinfo.value)
    assert logii.sha256 in str(excinfo.value)


def test_C_wrong_image_size_is_refused(buu):
    """An atlas bounded by another size cannot describe this image."""
    atlas = Atlas(
        buu.id,
        buu.sha256,
        IMAGE_SIZE // 2,
        CoverageMap.single(
            IMAGE_SIZE // 2,
            "UNKNOWN",
            Confidence.OBSERVED,
            Provenance(buu.id, buu.sha256, "half-size fixture"),
        ),
    )
    with pytest.raises(AtlasIdentityMismatch, match="image size"):
        buu.require_identity(atlas)


def test_F_a_derivative_naming_another_base_is_refused(buu, logii):
    """A derivative's canonical base must be the profile it claims to derive from."""
    atlas = _atlas(logii.id, logii.sha256)
    with pytest.raises(AtlasIdentityMismatch):
        buu.require_identity(atlas)


def test_G_missing_identity_fails_rather_than_defaulting(buu):
    """A value without the identity triple is refused, never silently accepted."""

    class Anonymous:
        pass

    with pytest.raises(AtlasIdentityMismatch, match="does not declare"):
        buu.require_identity(Anonymous())


def test_G_a_malformed_image_size_is_refused_at_construction():
    with pytest.raises(ProfileConfigError, match="image_size"):
        AtlasIdentity("buus_fury_usa_rev0_01c1707f", "ab" * 32, 0)


def test_G_an_empty_identity_field_is_refused_at_construction():
    with pytest.raises(ProfileConfigError, match="non-empty"):
        AtlasIdentity("", "ab" * 32, IMAGE_SIZE)


# --- refusal through the real session path: A, B, C ---------------------------


def test_session_refuses_a_wrong_profile_atlas(catalog, buu, logii, tmp_path):
    session, refused = _drive(
        catalog, tmp_path, atlas=_atlas(logii.id, buu.sha256), profile=buu
    )
    assert refused is not None
    assert isinstance(refused, SessionError)
    assert buu.id in str(refused) and logii.id in str(refused)
    # Nothing atlas-backed is reachable on the refused session.
    assert session.atlas is None
    assert session.profile is None
    assert session.rom_image is None


def test_session_refuses_a_wrong_base_atlas(catalog, buu, logii, tmp_path):
    session, refused = _drive(
        catalog, tmp_path, atlas=_atlas(buu.id, logii.sha256), profile=buu
    )
    assert refused is not None
    assert session.atlas is None
    assert buu.sha256 in str(refused)
    assert logii.sha256 in str(refused)


def test_session_accepts_a_matching_atlas(catalog, buu, tmp_path):
    session, refused = _drive(
        catalog, tmp_path, atlas=_atlas(buu.id, buu.sha256), profile=buu
    )
    assert refused is None, refused
    assert session.atlas is not None
    assert session.profile is not None
    assert session.profile.id == buu.id
    assert session.atlas.base_sha256 == buu.sha256


# --- D and E: canonical and trusted-derivative identity -----------------------


def test_D_canonical_identity_is_the_profiles_declaration(buu):
    """The canonical case: the profile's own identity is what an atlas must match."""
    assert buu.identity == AtlasIdentity(buu.id, buu.sha256, buu.size)
    assert buu.require_identity(_atlas(buu.id, buu.sha256)) == buu.identity


def test_E_a_derivative_is_checked_against_its_canonical_base(catalog, buu, tmp_path):
    """A derivative's atlas must describe the CANONICAL base, not the output file.

    This is the distinction the ticket calls out: a derivative's own bytes hash
    differently, but the atlas still describes the canonical image the readers
    actually run against (`Session.map_image`). So the accepted comparison is
    the reconstructed canonical identity, which is what the session already
    proved the manifest names.
    """
    derivative_output_sha = "ff" * 32
    assert derivative_output_sha != buu.sha256
    # The atlas describing the canonical base is accepted by that base's profile.
    assert buu.require_identity(_atlas(buu.id, buu.sha256)).sha256 == buu.sha256
    # An atlas describing the derivative's own output digest is NOT this base.
    with pytest.raises(AtlasIdentityMismatch, match="base sha256"):
        buu.require_identity(_atlas(buu.id, derivative_output_sha))


# --- the reason this gates the capacity ticket --------------------------------


def test_verified_free_evidence_cannot_reach_a_mismatched_base(catalog, buu, logii, tmp_path):
    """VERIFIED_FREE spans from the wrong image must not become session facts.

    `VERIFIED_FREE` is the atlas classification the capacity work would read for
    free space. Proven here: an atlas carrying such a span, built for another
    profile, is refused before it becomes session state, so no consumer of
    `session.atlas` can read a free span describing bytes that are not present.
    """
    coverage = CoverageMap.single(
        IMAGE_SIZE,
        VERIFIED_FREE,
        Confidence.CONFIRMED,
        Provenance(logii.id, buu.sha256, "TOOLKIT-028-style free declaration"),
    )
    # The span is a real VERIFIED_FREE claim and the atlas is self-consistent.
    assert coverage.spans[0].classification == VERIFIED_FREE
    foreign = Atlas(logii.id, buu.sha256, IMAGE_SIZE, coverage)
    foreign.validate()

    session, refused = _drive(catalog, tmp_path, atlas=foreign, profile=buu)
    assert refused is not None, "a VERIFIED_FREE atlas from another profile was accepted"
    assert session.atlas is None

    # And the same span from the RIGHT profile is accepted, so the refusal is
    # about identity and not about the classification.
    honest = Atlas(
        buu.id,
        buu.sha256,
        IMAGE_SIZE,
        CoverageMap(
            (
                CoverageSpan(
                    coverage.spans[0].range,
                    VERIFIED_FREE,
                    Confidence.CONFIRMED,
                    Provenance(buu.id, buu.sha256, "own free declaration"),
                ),
            ),
            IMAGE_SIZE,
        ),
    )
    session2, refused2 = _drive(catalog, tmp_path, atlas=honest, profile=buu)
    assert refused2 is None, refused2
    assert session2.atlas is not None


# --- the contract must not be enforceable only by the session -----------------


def test_the_same_rule_serves_a_modified_profile(buu):
    """A profile whose declared extents moved still gets one comparison.

    Cheap parameterization proof for the contract itself: a replacing profile is
    held to its own identity, so a synthetic profile cannot be satisfied by the
    canonical hash.
    """
    synthetic = replace(buu, id="synthetic_profile", sha256="ab" * 32)
    with pytest.raises(AtlasIdentityMismatch, match="base sha256"):
        synthetic.require_identity(_atlas(buu.id, buu.sha256))
    assert synthetic.require_identity(_atlas("synthetic_profile", "ab" * 32))


def test_map_entry_profile_is_part_of_the_declaration(buu):
    """The map table the renderer indexes is the profile's, not a module's."""
    table = buu.map_entries
    assert isinstance(table, MapEntryTableProfile)
    assert table.count > 0
    assert table.record_size > 0
