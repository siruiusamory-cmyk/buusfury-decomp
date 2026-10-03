"""One verified image, loaded once, shared by every module in a run.

The performance requirement this answers was measured, not assumed. The enemy
ticket's own profile found 5.65 s of an 11.8 s five-seed loop inside ``load_maps``
alone, of which 2.3 s was SHA-256 over the whole 8 MiB image, and the fix that
took that loop from ~1.2 s per seed to **164 ms per seed** was to load the
invariant data once and plan many times. The same rule applies one level up: a
combined run must not re-open, re-hash, re-parse or re-index the image once per
module.

So this context is the run's single door to the image:

* it identifies the image once (one hash pass) and keeps the identification;
* it reads the bytes once, and only if a module asks for them;
* it builds the enemy pack's own loaded context once, on first use, and hands the
  same object to every enemy module in the run.

What is deliberately NOT here: per-run state. A slot model, a stat table carrying
edits, a module's own accumulator - all of that is built per plan by the module
that owns it, so two runs against one context cannot contaminate each other. The
context is immutable ROM data and nothing else.

Source-ROM safety is inherited, not re-implemented: every loader here opens the
image read-only, and :meth:`RandomizerContext.assert_source_unchanged` re-checks
the filesystem identity tuple cheaply so an image edited mid-session is refused
rather than planned against.
"""

from __future__ import annotations

from pathlib import Path

from ..capability import Capability, require
from ..profile import RomProfile, RomProfileCatalog
from ..rom import RomIdentification, identify_rom
from .errors import ModuleRefusedError

#: The capability an image must expose for either product to read it at all. The
#: warp randomizer's own driver gates on this, so gating here means a wrong ROM
#: fails for the same reason in every product rather than for a second, app-local
#: reason that could drift.
REQUIRED_CAPABILITY = Capability.MAP_ENTRIES


class RandomizerContext:
    """A verified image and the immutable data read from it.

    Construction verifies the image. It is the caller's job to refuse an
    unsupported file *before* reaching here with a sentence for a person; this
    raises :class:`~tools.webfoot.randomizer.errors.ModuleRefusedError` because a
    context built on an unverified image would let a module plan against bytes
    nobody checked.
    """

    def __init__(
        self,
        source_rom: str | Path,
        catalog: RomProfileCatalog,
        *,
        identification: RomIdentification | None = None,
    ) -> None:
        self.path = Path(source_rom)
        self.catalog = catalog
        # An already-verified identification is accepted rather than recomputed:
        # the application service has just hashed this file to decide whether it
        # is supported, and hashing 8 MiB a second time to ask the same question
        # is exactly the repeated work the context exists to prevent.
        self.identification: RomIdentification = (
            identification
            if identification is not None
            else identify_rom(self.path, catalog)
        )
        profile: RomProfile | None = self.identification.profile_match.profile
        if profile is None:
            raise ModuleRefusedError(
                self.identification.profile_match.reason
                or "the selected image does not match a verified ROM profile"
            )
        # The one capability gate. Resolved against the *packaged* catalog, which
        # is the authority: a profile a caller injected for a synthetic image
        # cannot exempt itself from the declaration the toolkit actually ships.
        require(
            self.identification,
            REQUIRED_CAPABILITY,
            subsystem="randomization",
            error_type=ModuleRefusedError,
            check_header=True,
        )
        self.profile: RomProfile = profile
        self._image: bytes | None = None
        self._enemy: object | None = None
        self._source_stat = self.path.stat()

    # --- lazily loaded, cached for the whole run -------------------------

    def image(self) -> bytes:
        """The base image. Read once, on first use, and kept."""
        if self._image is None:
            self._image = self.path.read_bytes()
        return self._image

    def enemy_context(self):
        """The enemy pack's loaded context, built once and shared.

        Imported here rather than at module scope so the foundation stays
        importable without the enemy pack's loader stack, and so a product that
        never enables an enemy module never pays for one. The object is the pack's
        own :class:`~tools.webfoot.enemy_randomizer.planner.EnemyRandomizerContext`
        - not a copy, not a second parse - and it is reused by every enemy module
        in this run, which is what keeps a two-module enemy run at one map load
        instead of two.
        """
        if self._enemy is None:
            from ..enemy_randomizer.planner import EnemyRandomizerContext

            self._enemy = EnemyRandomizerContext(self.path, self.catalog)
        return self._enemy

    @property
    def plans(self) -> int:
        """How many plans every loaded sub-context has produced between them."""
        enemy = self._enemy
        return int(getattr(enemy, "plans", 0)) if enemy is not None else 0

    # --- safety ----------------------------------------------------------

    def assert_source_unchanged(self) -> None:
        """Refuse if the image moved on disk since it was loaded.

        A full re-hash per call would defeat the point of caching, so this
        compares the filesystem identity tuple - device, inode, size and mtime -
        which catches a rewrite, a truncation and a replacement. The digest was
        already proved once at load time.
        """
        current = self.path.stat()
        before = self._source_stat
        if (current.st_dev, current.st_ino, current.st_size, current.st_mtime_ns) != (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
        ):
            raise ModuleRefusedError(
                f"the source image changed after it was loaded: {self.path}. "
                "Select it again so every plan is made against the image that was "
                "verified."
            )

    # --- what a module may read ------------------------------------------

    @property
    def source_sha256(self) -> str:
        return self.identification.hashes.sha256

    @property
    def size(self) -> int:
        return self.identification.size

    def __repr__(self) -> str:  # pragma: no cover - diagnostics only
        return f"RandomizerContext({self.path.name!r}, profile={self.profile.id!r})"
