"""The run manifest and the optional spoiler log.

Both are deterministic, machine-readable JSON. The manifest is the record a run
is reproduced from; the spoiler log is the same information presented for a
stream or a debugging session, and it is the only place the two differ.

Determinism
===========

Every document is built from plain data and serialized with ``sort_keys=True``,
so the same seed, image and configuration produce byte-identical text. No
absolute path is ever written - only the output's basename - so two runs of the
same image and seed in different folders agree, and a published manifest can be
compared with a locally produced one.

No ROM addresses in the primary presentation
============================================

The manifest names maps and placements by their durable identities
(``map:0040/placement:0000``, ``enemy:434``) and never by ROM offset or GBA
address, because the ticket requires that a user not need to know an offset to
read a run. Byte offsets stay out of both documents entirely: the writer's own
:class:`~tools.webfoot.write.WriteManifest` already carries the byte-level
provenance for anyone who needs it, and duplicating offsets here would create a
second place for them to drift.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Mapping

from .seeds import MASTER_DOMAIN, MODULE_DOMAIN, derive_all_module_seeds

#: The manifest schema this pack writes. Bumped when the document's shape
#: changes, so a reader can tell an old manifest from a new one rather than
#: guessing from missing keys.
SCHEMA_VERSION = 1

#: The ticket this pack exists for. Recorded so a manifest names the work that
#: produced it.
TICKET = "RANDOMIZER-ENEMY-PACK-001"


def canonical_json(document: Mapping) -> str:
    """Serialize a document deterministically, with a trailing newline.

    ``sort_keys=True`` and a fixed indent are the whole determinism story: two
    runs that produced the same data produce the same bytes, so a manifest can be
    hashed and compared.
    """
    return json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def digest_of(document: Mapping) -> str:
    """The SHA-256 of a document's canonical text, for the manifest's own id."""
    return hashlib.sha256(canonical_json(document).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class RunManifest:
    """Everything needed to reproduce and audit one randomized run.

    ``sdk_commit`` is supplied by the caller rather than read from git here: this
    module performs no I/O, and a component that shelled out to ``git`` would be
    untestable without a repository.
    """

    master_seed: str
    module_seeds: dict[str, str]
    profile_id: str
    profile_sha256: str
    sdk_commit: str | None
    preset: str
    configuration: dict
    slot_summary: dict
    module_summaries: dict
    exclusions: dict
    source_rom_sha256: str
    output_rom_sha256: str
    output_rom_size: int
    changed_byte_count: int

    def to_json(self) -> dict:
        return {
            "schema_version": SCHEMA_VERSION,
            "ticket": TICKET,
            "seed": {
                "master": self.master_seed,
                "master_domain": MASTER_DOMAIN.decode("ascii"),
                "module_domain": MODULE_DOMAIN.decode("ascii"),
                # The derivation is recorded, not just its result: a reader can
                # re-derive every module seed from the master seed and check it.
                "derivation": "sha256(master_domain | seed | module_id)",
                "module_seeds": dict(sorted(self.module_seeds.items())),
            },
            "rom": {
                "profile": self.profile_id,
                "profile_sha256": self.profile_sha256,
                "source_sha256": self.source_rom_sha256,
            },
            "tool": {
                "name": "webfoot randomize",
                "sdk_commit": self.sdk_commit,
            },
            "preset": self.preset,
            "configuration": self.configuration,
            "output": {
                "sha256": self.output_rom_sha256,
                "size": self.output_rom_size,
                "changed_byte_count": self.changed_byte_count,
            },
            "eligibility": self.slot_summary,
            "modules": self.module_summaries,
            "exclusions": self.exclusions,
        }

    @property
    def document_id(self) -> str:
        return digest_of(self.to_json())


@dataclass(frozen=True, slots=True)
class SpoilerLog:
    """Per-slot detail, for a stream, a bug report, or a debugging session.

    Kept separate from the manifest because it is large: one row per randomized
    slot rather than a summary. It is written only when asked for.
    """

    master_seed: str
    module_seeds: dict[str, str]
    profile_id: str
    slots: tuple[dict, ...]
    stats: tuple[dict, ...]
    #: What each module did, so the log cannot imply by omission that a module ran
    #: or changed something. Carries the same `delivers_ticket_module_c` statement
    #: the manifest does.
    module_summaries: dict = field(default_factory=dict)

    def to_json(self) -> dict:
        return {
            "schema_version": SCHEMA_VERSION,
            "ticket": TICKET,
            "seed": {
                "master": self.master_seed,
                "module_seeds": dict(sorted(self.module_seeds.items())),
            },
            "profile": self.profile_id,
            # Stated up front, because a reader opening only this file would
            # otherwise see per-slot rows and reasonably assume enemy types moved.
            "enemy_type_randomization": {
                "delivered": False,
                "note": (
                    "Enemy-TYPE randomization is not delivered on current evidence. "
                    "If the enemy-type module ran, it exchanged identity only between "
                    "slots whose flags, behavior descriptor and children already "
                    "matched, which cannot turn an ordinary enemy into a different "
                    "kind of enemy. See section 5.2 of "
                    "docs/research/ENEMY_RANDOMIZER_VERIFICATION.md."
                ),
            },
            "modules": self.module_summaries,
            "slots": list(self.slots),
            "stats": list(self.stats),
        }
