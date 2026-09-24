"""CQA-03-15-IDENTITY-AND-EXTENTS-001: pre-fix reproduction of the atlas hole.

Drives the real `Session.open_rom` with a verified profile identification and an
atlas whose own declared identity names a different profile and base. No second
commercial ROM is required or read: the identification is stubbed to the
canonical profile, and only the atlas identity is varied.

Run before the fix to record RED, after it to record GREEN:

    python tools/qa/cqa03_atlas_identity_probe.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.webfoot.atlas import Atlas, CoverageMap, Confidence  # noqa: E402
from tools.webfoot.hashing import RomHashes  # noqa: E402
from tools.webfoot.layout import Provenance  # noqa: E402
from tools.webfoot.profile import (  # noqa: E402
    ProfileMatch,
    RomProfileCatalog,
    VerificationStatus,
)
from tools.webfoot.rom import RomIdentification  # noqa: E402
from tools.webfoot.workbench import session as session_mod  # noqa: E402
from tools.webfoot.workbench.session import Session, SessionError  # noqa: E402

BUU = "buus_fury_usa_rev0_01c1707f"
BUU_SHA = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
LOGII = "legacy_of_goku_ii_usa_rev0_204142e1"
LOGII_SHA = "6e6c370c339ec9171cb1956adf837a0d342a197f78964882ef46c3086656ff75"
SIZE = 8_388_608


def _atlas(profile_id: str, base_sha256: str) -> Atlas:
    coverage = CoverageMap.single(
        SIZE, "UNKNOWN", Confidence.OBSERVED, Provenance(profile_id, base_sha256, "probe")
    )
    return Atlas(profile_id, base_sha256, SIZE, coverage)


def _drive(catalog: RomProfileCatalog, *, image_name: str, atlas: Atlas, tmp: Path):
    """Call the real open_rom with a stubbed identification and atlas artifact."""
    profile = next(p for p in catalog.profiles if p.id == BUU)
    rom_path = tmp / image_name
    rom_path.write_bytes(b"\x00" * SIZE)

    real_identify = session_mod.identify_rom

    def fake_identify(path, cat):  # noqa: ANN001
        real = real_identify(path, catalog)
        return RomIdentification(
            path=real.path,
            size=SIZE,
            hashes=RomHashes(
                crc32=profile.crc32,
                md5=profile.md5,
                sha1=profile.sha1,
                sha256=profile.sha256,
            ),
            header=real.header,
            profile_match=ProfileMatch(
                status=VerificationStatus.VERIFIED,
                profile=profile,
                reason="stubbed for the CQA-03 probe",
            ),
        )

    atlas_dir = tmp / "atlas"
    atlas_dir.mkdir(parents=True, exist_ok=True)
    (atlas_dir / "atlas.jsonl").write_text("", encoding="utf-8")

    session = Session()
    saved_identify = session_mod.identify_rom
    saved_dir = session_mod._default_atlas_directory
    saved_load = session_mod.load_atlas
    session_mod.identify_rom = fake_identify
    session_mod._default_atlas_directory = lambda: atlas_dir
    session_mod.load_atlas = lambda path: atlas
    try:
        session.open_rom(rom_path, catalog)
        refused = None
    except SessionError as exc:
        refused = exc
    finally:
        session_mod.identify_rom = saved_identify
        session_mod._default_atlas_directory = saved_dir
        session_mod.load_atlas = saved_load
    return session, refused


def main() -> int:
    catalog = RomProfileCatalog.load(ROOT / "config" / "roms.yaml")
    import tempfile

    failures = 0
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        cases = (
            ("wrong profile id (same image)", _atlas(LOGII, BUU_SHA), False),
            ("correct profile id, wrong base sha", _atlas(BUU, LOGII_SHA), False),
            ("matching identity", _atlas(BUU, BUU_SHA), True),
        )
        for label, atlas, expect_accepted in cases:
            session, refused = _drive(catalog, image_name="probe.gba", atlas=atlas, tmp=tmp)
            accepted = refused is None
            leaked = session.atlas is not None
            print(
                f"{label}: refused = {not accepted}, "
                f"atlas in session state = {leaked}, "
                f"expected accepted = {expect_accepted}"
            )
            if refused is not None:
                print(f"    {refused}")
            if accepted != expect_accepted or (not expect_accepted and leaked):
                failures += 1
    print()
    print("RED" if failures else "GREEN")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
