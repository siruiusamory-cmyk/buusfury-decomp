"""WARPRAND-APP-001 - the application boundary for the warp randomizer, retrofitted.

This module is the **product boundary** of the standalone *Buu's Fury Warp
Randomizer*, and since ENEMY-RANDOMIZER-EXE-001 it is a facade rather than an
implementation. It still contains no randomization logic of its own - every
destination, arrival, facing, permutation and refusal is decided by
:mod:`tools.webfoot.warp_randomizer` - and it now also contains no *application*
logic of its own: the ROM check, the path safety, the source-ROM re-verification,
the manifest, the spoiler machinery and the refusal vocabulary live in
:mod:`tools.webfoot.randomizer`, shared with the enemy executable and with every
randomizer that follows.

Why the retrofit happened, and what it had to preserve
=====================================================

The long-term product is one application with several independently selectable
randomizer modules. Standing the enemy tool up beside this one as a second
application would have made that eventual tool a rewrite, so the shared
foundation was built first and both products became thin compositions over it::

    RandomizerApp(allowed_modules=["map-warp"])
    RandomizerApp(allowed_modules=["enemy-placement", "enemy-stat"])

Three things had to survive the move, and each is pinned by a test:

* **the public surface of this module.** ``verify_rom``, ``randomize_warps``,
  ``RandomizationOutcome`` and the six refusal classes are what the shipped
  window, the focused tests and the packaged smoke all call, so they are still
  here, with the same shapes. :meth:`WarpRandomizerService.randomize_warps`
  translates its arguments into a
  :class:`~tools.webfoot.randomizer.service.RandomizerRequest` and translates the
  result back.
* **the launch seed's output.** A seed is only reproducible alongside the
  algorithm that consumed it. ``map-warp`` therefore consumes the master seed
  verbatim - see :mod:`tools.webfoot.randomizer.modules.map_warp` - so ``Goku``
  still produces the v0.1.0 golden image byte for byte.
* **the phase list.** ``PROGRESS_STEPS`` is derived from the module that runs
  rather than restated, and for this product the derivation reproduces the list
  this product always had, down to the wording.

The product manifest gained a format
====================================

The manifest is now the shared, versioned document
(:mod:`tools.webfoot.randomizer.manifest`) rather than a warp-only shape, because
a combined run has one output and therefore needs one document describing it. The
warp-specific facts did not disappear: the policy, the counts, the skip reasons,
the class counts, the forced dead-end links and the core randomizer's full
per-transition record all live under ``modules["map-warp"]``. What moved is *where
they are stated*, not *what is stated*.

Determinism
===========

A seed is the *exact* string the user typed; nothing here normalizes, trims or
case-folds it on its way to the core, and the core re-derives its permutation from
SHA-256 rather than from a process-randomized hash. The manifest records the seed
verbatim and never an absolute path - only the output's own basename - so the same
input image, tool version, seed and output name produce byte-identical manifest
text anywhere. :func:`sanitize_seed_for_filename` changes only the *file name*,
never the seed the algorithm sees; the two are separate arguments on purpose and
the tests pin the separation.

Source-ROM safety
=================

The selected image is an input on every path and an output on none. The rules, and
the ordering that makes them safe, are
:meth:`tools.webfoot.randomizer.service.RandomizerService.run`'s; this module adds
nothing to them and could not weaken them if it wanted to, because every write goes
through that one method.

Nothing here touches the capability registry. This is a side utility: it ships an
offline artefact and moves no DragonByte Z capability count.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping

from ..randomizer.errors import (
    ManifestWriteError,
    ModuleConflictError,
    ModuleRefusedError,
    OutputAlreadyExistsError,
    OutputPathRefusedError,
    RandomizerAppError,
    SeedRefusedError,
    SourceChangedError,
    UnsupportedRomError,
)
from ..randomizer.registry import progress_steps
from ..randomizer.service import (
    FALLBACK_SEED_FILENAME,
    MANIFEST_SUFFIX,
    MAX_SEED_FILENAME_CHARACTERS,
    SEED_WORDS,
    SPOILER_SUFFIX,
    RandomizerRequest,
    RandomizerResult,
    RandomizerService,
    RomVerification,
    default_manifest_path,
    random_seed,
    sanitize_seed_for_filename,
    shorten_hash,
)
from ..randomizer.service import default_output_path as _shared_default_output_path
from ..randomizer.spoiler import FORMAT_VERSION
from ..warp_randomizer import POLICY_ID

# --- product identity --------------------------------------------------------

#: The shipped product name. The window title, the manifest and the release notes
#: all read this one string; a second spelling would be a second product.
TOOL_NAME = "Buu's Fury Warp Randomizer"

#: The product version. It belongs in the manifest beside the module's algorithm
#: version, because a seed alone does not identify a mapping: the same seed under a
#: new algorithm version may legitimately produce a different layout, and only the
#: version pair makes that visible rather than silent.
TOOL_VERSION = "0.1.0"

#: The v0.1.0 launch seed. Named as a constant so the window's initial text and the
#: focused tests read the same value instead of agreeing by coincidence.
DEFAULT_SEED = "Goku"

#: The default output name, beside the selected image. ``{seed}`` receives the
#: *filename-safe* seed, never the algorithm seed.
OUTPUT_TEMPLATE = "Buu's Fury - Warp Randomized - {seed}.gba"

#: The module this product runs. Named rather than repeated as a literal, because
#: the registry is the authority for what a module is called.
MODULE_ID = "map-warp"

#: The limitation this product does not hide. It is shown in the window and
#: recorded in the manifest, because a shared artifact should carry the caveat even
#: when the window that made it is long gone.
PROGRESSION_DISCLAIMER = (
    "Randomized warps may make the game impossible to complete. Progression, "
    "reachability and beatability are not guaranteed."
)

#: The manifest schema this build writes. It is the shared randomizer format now;
#: the older name is kept because the released product documents it.
MANIFEST_SCHEMA_VERSION = FORMAT_VERSION

#: The real phases of one run, in order, for a progress display.
#:
#: Derived from the module that actually runs rather than restated, and for this
#: product the derivation reproduces the v0.1.0 list exactly. Each entry is
#: reported immediately *before* the work it names begins, so a bar built on them
#: can only ever understate progress, never claim work that has not happened.
PROGRESS_STEPS: tuple[str, ...] = progress_steps({MODULE_ID})

#: ``on_progress(step, total, label)``, step being 1-based.
ProgressCallback = Callable[[int, int, str], None]

#: The randomization policies this product ships. Exactly one, and the boundary
#: **refuses** anything else rather than ignoring it: a policy argument that was
#: silently dropped would produce a ``/3`` mapping under a caller's ``/4`` label.
SUPPORTED_POLICIES: tuple[str, ...] = (POLICY_ID,)

#: The user-facing refusal for an image this version cannot randomize.
UNSUPPORTED_ROM_HEADLINE = (
    "This version currently supports the verified US Buu's Fury ROM only."
)

#: The two states a selected file can be in.
VERIFIED = "verified"
UNSUPPORTED = "unsupported"

#: The refusal classes, re-exported under the names this product has always used.
#: They are the shared families now rather than a warp-private set, so a window
#: written against one product cannot mistake another product's refusal for a
#: crash - and the enemy executable refuses in exactly the same vocabulary.
WarpRandomizerAppError = RandomizerAppError

__all__ = [
    "DEFAULT_SEED",
    "FALLBACK_SEED_FILENAME",
    "MANIFEST_SCHEMA_VERSION",
    "MANIFEST_SUFFIX",
    "MAX_SEED_FILENAME_CHARACTERS",
    "MODULE_ID",
    "ManifestWriteError",
    "ModuleConflictError",
    "ModuleRefusedError",
    "OUTPUT_TEMPLATE",
    "OutputAlreadyExistsError",
    "OutputPathRefusedError",
    "POLICY_ID",
    "PROGRESSION_DISCLAIMER",
    "PROGRESS_STEPS",
    "ProgressCallback",
    "RandomizationOutcome",
    "RandomizerRequest",
    "RandomizerResult",
    "RandomizerService",
    "RomVerification",
    "SEED_WORDS",
    "SPOILER_SUFFIX",
    "SUPPORTED_POLICIES",
    "SeedRefusedError",
    "SourceChangedError",
    "TOOL_NAME",
    "TOOL_VERSION",
    "UNSUPPORTED",
    "UNSUPPORTED_ROM_HEADLINE",
    "UnsupportedRomError",
    "VERIFIED",
    "WarpRandomizerAppError",
    "WarpRandomizerService",
    "default_manifest_path",
    "default_output_path",
    "default_service",
    "random_seed",
    "randomize_warps",
    "sanitize_seed_for_filename",
    "shorten_hash",
    "verify_rom",
]


# --- the result --------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class RandomizationOutcome:
    """One finished run, in the shape this product has always reported.

    Every count is the core's own reported value, carried through untouched. The
    window displays these and never a hard-coded expectation, which is what stops
    a policy change from leaving a stale number on screen.
    """

    seed: str
    policy_id: str
    tool_version: str
    supported: int
    randomized: int
    destinations_moved: int
    skipped: int
    skipped_reasons: Mapping[str, int]
    class_counts: Mapping[str, int]
    output_path: Path
    output_sha256: str
    output_size: int
    manifest_path: Path
    changed_byte_count: int
    source_sha256: str
    source_unchanged: bool
    randomizer_manifest: Mapping
    #: Added by the retrofit. This product offers no spoiler control, so it is
    #: ``None`` on every run this boundary can start - it exists so the field is
    #: part of the outcome shape rather than a product-specific special case.
    spoiler_path: Path | None = None

    def short_output_sha256(self) -> str:
        return shorten_hash(self.output_sha256)

    def status_lines(self) -> list[str]:
        """The success text, in the order the ticket specifies."""
        return [
            "Success",
            f"Seed: {self.seed}",
            f"Randomized: {self.randomized}",
            f"Skipped: {self.skipped}",
            f"Output: {self.output_path}",
            f"SHA-256: {self.output_sha256}",
        ]


# --- naming ------------------------------------------------------------------


def default_output_path(rom_path: str | Path, seed: str) -> Path:
    """``<ROM folder>/Buu's Fury - Warp Randomized - <safe seed>.gba``.

    Beside the selected image, which is where a user who just picked a ROM expects
    the result, and never a repository-internal build directory: the app is shipped
    to people who have no checkout.
    """
    return _shared_default_output_path(rom_path, seed, OUTPUT_TEMPLATE)


# --- the boundary ------------------------------------------------------------


class WarpRandomizerService:
    """The application boundary. GUI-free, so it is testable without Qt.

    One instance owns one shared service, which owns one ROM profile catalog,
    loaded once. The catalog is the authority for *which* image is supported: the
    expected size and SHA-256 in every refusal come out of the verified profile
    rather than from a literal in this file, so a profile change cannot leave the
    app checking yesterday's image.
    """

    def __init__(
        self,
        *,
        catalog=None,
        supported_profile=None,
        policy_id: str = POLICY_ID,
        tool_version: str = TOOL_VERSION,
        service: RandomizerService | None = None,
    ) -> None:
        self.policy_id = policy_id
        self.tool_version = tool_version
        self._shared = (
            service
            if service is not None
            else RandomizerService(catalog=catalog, supported_profile=supported_profile)
        )

    # --- the shared service, exposed for a composer ----------------------

    @property
    def shared(self) -> RandomizerService:
        """The foundation this product sits on.

        Public because the window protocol is the shared one and a caller may want
        the raw result; it is not an escape hatch around the refusals, which all
        live there.
        """
        return self._shared

    @property
    def catalog(self):
        return self._shared.catalog

    # --- supported image -------------------------------------------------

    def supported_profile(self):
        """The one profile this product randomizes.

        Resolved from the catalog by the packaged profile id - the same authority
        the ROM-addressed readers use - so every "expected" value in a refusal is
        read from verified profile data rather than restated here. It is injectable
        so the boundary's own tests can drive a synthetic image without a private
        ROM, exactly as the profile contract intends.
        """
        return self._shared.supported_profile()

    # --- seed ------------------------------------------------------------

    def normalize_seed(self, seed: str | int) -> str:
        """The exact seed string, or a friendly refusal.

        Delegated to the shared boundary so there is one definition of "a usable
        seed" across every product, and so the enemy executable refuses an empty
        seed with the same sentence.
        """
        return self._shared.normalize_seed(seed)

    def generate_seed(self) -> str:
        return self._shared.generate_seed()

    # --- verification ----------------------------------------------------

    def verify_rom(self, path: str | Path) -> RomVerification:
        """Check a selected file against the supported image. Never raises."""
        return self._shared.verify_rom(path)

    # --- naming ----------------------------------------------------------

    def default_output_path(self, rom_path: str | Path, seed: str) -> Path:
        return default_output_path(rom_path, seed)

    def manifest_path_for(self, output_rom: str | Path) -> Path:
        return default_manifest_path(output_rom)

    def spoiler_path_for(self, output_rom: str | Path) -> Path:
        return self._shared.spoiler_path_for(output_rom)

    def output_is_the_input(self, source_rom: str | Path, output_rom: str | Path) -> bool:
        """Whether the requested output *is* the input, by filesystem identity.

        Exposed for the window, which blocks the run before it starts rather than
        after a refusal comes back from a worker thread. It is the same predicate
        the refusal uses - ``webfoot.write`` documents this exact use ("a GUI
        enabling a button, a report") - so the button and the refusal cannot
        disagree.
        """
        return self._shared.output_is_the_input(source_rom, output_rom)

    # --- the run ---------------------------------------------------------

    def build_request(
        self,
        source_rom: str | Path,
        output_rom: str | Path,
        seed: str | int = DEFAULT_SEED,
        *,
        overwrite: bool = False,
        on_progress: ProgressCallback | None = None,
    ) -> RandomizerRequest:
        """The shared request this product's run describes."""
        return RandomizerRequest(
            source_rom=Path(source_rom),
            output_rom=Path(output_rom),
            master_seed=str(seed),
            enabled=frozenset({MODULE_ID}),
            tool_name=TOOL_NAME,
            tool_version=self.tool_version,
            progression=PROGRESSION_DISCLAIMER,
            overwrite=overwrite,
            on_progress=on_progress,
        )

    def randomize(self, request: RandomizerRequest) -> RandomizationOutcome:
        """The shared window protocol: run exactly the request it was handed.

        This product offers one module, so a request naming anything else is
        refused by the registry rather than silently narrowed - and the result is
        translated back into this product's own outcome shape, because the window
        is the *product's* window and reports with this product's vocabulary. The
        enemy sibling returns the shared result instead and presents its own
        block; both are the same protocol, which is why the window treats a result
        opaquely and only ever reads ``output_path``, ``output_sha256`` and
        ``manifest_path`` from it.
        """
        return self._outcome(self._shared.run(request))

    def randomize_warps(
        self,
        source_rom: str | Path,
        output_rom: str | Path,
        seed: str | int = DEFAULT_SEED,
        *,
        policy: str = POLICY_ID,
        overwrite: bool = False,
        on_progress: ProgressCallback | None = None,
    ) -> RandomizationOutcome:
        """Randomize ``source_rom`` into ``output_rom`` and record the run.

        The signature the WARPRAND-APP-001 ticket names, and the whole surface the
        released scripts use. It is a thin translation now: the ordering, the path
        rules, the merge, the write and the manifest belong to
        :meth:`tools.webfoot.randomizer.service.RandomizerService.run`, which is
        also what the enemy executable calls.

        ``policy`` is validated and refused when unknown - it is not a knob. Only
        :data:`SUPPORTED_POLICIES` may be passed, and the window offers no control
        for it.
        """
        if policy not in SUPPORTED_POLICIES:
            raise RandomizerAppError(
                f"unsupported randomization policy {policy!r}; this version "
                f"supports only {', '.join(SUPPORTED_POLICIES)}"
            )
        result = self._shared.run(
            self.build_request(
                source_rom,
                output_rom,
                seed,
                overwrite=overwrite,
                on_progress=on_progress,
            )
        )
        return self._outcome(result)

    @staticmethod
    def _outcome(result: RandomizerResult) -> RandomizationOutcome:
        """The shared result, in this product's own reported shape."""
        section = result.document["modules"][MODULE_ID]
        counts = section.get("counts", {})
        return RandomizationOutcome(
            seed=result.master_seed,
            policy_id=POLICY_ID,
            tool_version=result.tool_version,
            supported=counts.get("supported", 0),
            randomized=counts.get("randomized", 0),
            destinations_moved=counts.get("destinations_moved", 0),
            skipped=counts.get("skipped", 0),
            skipped_reasons=dict(section.get("skipped_reasons", {})),
            class_counts=dict(section.get("class_counts", {})),
            output_path=result.output_path,
            output_sha256=result.output_sha256,
            output_size=result.output_size,
            manifest_path=result.manifest_path,
            changed_byte_count=result.changed_byte_count,
            source_sha256=result.source_sha256,
            source_unchanged=result.source_unchanged,
            randomizer_manifest=section.get("randomizer", {}),
            spoiler_path=result.spoiler_path,
        )


# --- module-level conveniences ----------------------------------------------

_DEFAULT_SERVICE: WarpRandomizerService | None = None


def default_service() -> WarpRandomizerService:
    """The process-wide service. One catalog load for the whole application."""
    global _DEFAULT_SERVICE
    if _DEFAULT_SERVICE is None:
        _DEFAULT_SERVICE = WarpRandomizerService()
    return _DEFAULT_SERVICE


def verify_rom(path: str | Path) -> RomVerification:
    return default_service().verify_rom(path)


def randomize_warps(
    source_rom: str | Path,
    output_rom: str | Path,
    seed: str | int = DEFAULT_SEED,
    *,
    policy: str = POLICY_ID,
    overwrite: bool = False,
    on_progress: ProgressCallback | None = None,
) -> RandomizationOutcome:
    """``randomize_warps(source_rom, output_rom, seed, policy)``, standalone."""
    return default_service().randomize_warps(
        source_rom,
        output_rom,
        seed,
        policy=policy,
        overwrite=overwrite,
        on_progress=on_progress,
    )
