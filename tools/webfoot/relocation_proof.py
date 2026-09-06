"""Portable infrastructure demonstration, containing only constructed bytes."""

from hashlib import sha256

from .binary import FileOffset
from .document import RomDocument
from .layout import (Anchor, AnchorId, Provenance, Reference, ReferenceClass,
                     ReferenceEncoding, RomRange)
from .profile import RomProfile
from .relocation import RelocationRequest, RelocationResult, plan_relocation


def synthetic_relocation_proof() -> RelocationResult:
    image = bytearray(1024)
    image[0xA0:0xAC] = b"SYNTHETIC   "
    image[0xAC:0xB0] = b"TEST"
    image[0xB0:0xB2] = b"00"
    image[0xB2] = 0x96
    image[0xBD] = (-(sum(image[0xA0:0xBD]) + 0x19)) & 255
    image[0x100:0x108] = b"old-data"
    image[0xC0:0xC4] = (0x08000100).to_bytes(4, "little")
    image[0xC4:0xC8] = (0x104 - 0xC4).to_bytes(4, "little", signed=True)
    profile = RomProfile.from_mapping({
        "id": "synthetic-proof-v1", "game": "synthetic", "region": "test",
        "revision": 0, "game_code": "TEST", "size": 1024,
        "sha256": sha256(image).hexdigest(),
        "free_regions": [{"file_offset": 0x201, "size": 0xFF, "status": "CONFIRMED",
                          "evidence": "constructed synthetic fixture; no game claim"}],
    })
    provenance = Provenance(profile.id, profile.sha256, "constructed synthetic layout contract")
    identity = AnchorId("fixture:payload")
    anchor = Anchor(identity, RomRange(FileOffset(0x100), 8), "opaque-test",
                    "fixture:owner", 8, True, provenance)
    references = (
        Reference(FileOffset(0xC0), identity, 0, ReferenceEncoding.ABSOLUTE_ROM_U32_LE,
                  ReferenceClass.DECLARED_REFERENCE, provenance),
        Reference(FileOffset(0xC4), identity, 4, ReferenceEncoding.RELATIVE_I32_LE,
                  ReferenceClass.CONFIRMED_REFERENCE, provenance),
    )
    document = RomDocument.from_bytes(bytes(image), profile, anchors=(anchor,), references=references)
    return plan_relocation(document, [RelocationRequest(identity, b"synthetic payload grew from eight bytes")])
