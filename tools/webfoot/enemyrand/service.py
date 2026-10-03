"""The application boundary of the standalone *Enemy Randomizer*.

A product boundary, in the exact sense :mod:`tools.webfoot.warprand.service` is
one: it holds the product's identity, its output naming, its module composition
and its disclaimer, and it delegates every *application* rule to
:class:`tools.webfoot.randomizer.service.RandomizerService`. There is no ROM
check here, no path safety check here, no manifest and no spoiler machinery here -
all of that is shared, which is the whole point of the retrofit the sibling tool
underwent in the same change.

The composition
===============

The enemy pack plans its two modules in ONE pass over the image: it loads 8 MiB
once, builds one slot model and returns one merged change set whose records are
encoded exactly once. That is a property of the pack, not a preference, and the
registry expresses it as a module *group* rather than by planning twice. What this
boundary does is choose which of those two modules the user enabled, and hand that
choice to the foundation.

Nothing in this file knows an enemy's name, a stat field or a map.
"""

from __future__ import annotations

from pathlib import Path

from ..randomizer.registry import progress_steps, resolve_enabled
from ..randomizer.service import (
    MANIFEST_SUFFIX,
    SPOILER_SUFFIX,
    RandomizerRequest,
    RandomizerResult,
    RandomizerService,
    RomVerification,
    default_manifest_path,
    default_spoiler_path,
    random_seed,
    sanitize_seed_for_filename,
    shorten_hash,
)
from ..randomizer.service import default_output_path as _shared_default_output_path

# --- product identity --------------------------------------------------------

#: The shipped product name. One string for the window title, the manifest and the
#: release notes; a second spelling would be a second product.
#:
#: The ticket's working name was ``Enemy Randomizer`` and that is what ships. It is
#: deliberately NOT "Enemy Type Randomizer": nothing here changes an enemy's
#: species, and a name that implied it would be the one claim this tool must never
#: make.
TOOL_NAME = "Enemy Randomizer"

#: The product version. It belongs beside each module's algorithm version in the
#: manifest, because a seed only identifies a mapping alongside the algorithms
#: that consumed it.
TOOL_VERSION = "0.1.0"

#: The launch seed. The ticket's own regression fixture, chosen as the default on
#: purpose: the packaged smoke run and the golden cross-check both use it, so the
#: shipped default is the fixture that is actually verified rather than a second
#: value that only the tests know.
DEFAULT_SEED = "StreamBlind-0001"

#: The default output name, beside the selected image and in the same shape the
#: warp tool uses, so two siblings produce two obviously related files.
#: ``{seed}`` receives the *filename-safe* seed, never the algorithm seed.
OUTPUT_TEMPLATE = "Buu's Fury - Enemy Randomized - {seed}.gba"

#: The two modules this product composes. Order matters for the progress display
#: and the manifest, and it is the registry's canonical order.
MODULE_IDS: tuple[str, ...] = ("enemy-placement", "enemy-stat")

#: The limitation this product does not hide. It travels in the window and in
#: every manifest, because a shared artifact should carry its caveat even when the
#: window that made it is long gone.
PROGRESSION_DISCLAIMER = (
    "Enemy stats and placements are randomized, so difficulty varies from the "
    "original game. Progression is bounded, but full-game balance is not "
    "guaranteed. Enemy species and types are NOT changed."
)

#: The real phases of one run, in order, for a progress display. Derived from the
#: modules that actually run, so a placement-only run names one phase and not two.
PROGRESS_STEPS: tuple[str, ...] = progress_steps(set(MODULE_IDS))


# --- naming ------------------------------------------------------------------


def default_output_path(rom_path: str | Path, seed: str) -> Path:
    """``<ROM folder>/Buu's Fury - Enemy Randomized - <safe seed>.gba``.

    Beside the selected image, which is where a user who just picked a ROM expects
    the result, and never a repository-internal build directory: the app is shipped
    to people who have no checkout.
    """
    return _shared_default_output_path(rom_path, seed, OUTPUT_TEMPLATE)


# --- the boundary ------------------------------------------------------------


class EnemyRandomizerService:
    """The application boundary. GUI-free, so it is testable without Qt.

    One instance owns one shared service, which owns one ROM profile catalog,
    loaded once, and one loaded image per unchanged source file. The second part
    matters: the enemy pack's context is the expensive half of a run, and caching
    it means pressing Randomize twice on the same ROM costs a plan rather than a
    reload.
    """

    def __init__(
        self,
        *,
        catalog=None,
        supported_profile=None,
        tool_version: str = TOOL_VERSION,
        service: RandomizerService | None = None,
    ) -> None:
        self.tool_version = tool_version
        self._shared = (
            service
            if service is not None
            else RandomizerService(catalog=catalog, supported_profile=supported_profile)
        )

    # --- what this product offers ----------------------------------------

    @property
    def allowed_modules(self) -> tuple[str, ...]:
        """The modules this product may run.

        The registry knows more modules than this product offers, and that is the
        point: a product is a *selection* over the registry. ``enemy-type`` is not
        registered at all, so it cannot be selected here by any spelling.
        """
        return MODULE_IDS

    def resolve_modules(self, requested=None) -> frozenset[str]:
        """The enabled set for this product, or a refusal naming what it offers."""
        return resolve_enabled(self.allowed_modules, requested)

    @property
    def shared(self) -> RandomizerService:
        return self._shared

    @property
    def catalog(self):
        return self._shared.catalog

    # --- supported image -------------------------------------------------

    def supported_profile(self):
        """The one profile this product randomizes, read from the packaged catalog.

        Every "expected" value in a refusal comes from verified profile data rather
        than from a literal here, so a profile change cannot leave the app checking
        yesterday's image.
        """
        return self._shared.supported_profile()

    # --- seed ------------------------------------------------------------

    def normalize_seed(self, seed: str | int) -> str:
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
        return default_spoiler_path(output_rom)

    def output_is_the_input(self, source_rom: str | Path, output_rom: str | Path) -> bool:
        return self._shared.output_is_the_input(source_rom, output_rom)

    # --- the run ---------------------------------------------------------

    def build_request(
        self,
        source_rom: str | Path,
        output_rom: str | Path,
        seed: str | int = DEFAULT_SEED,
        *,
        enabled=None,
        module_settings=None,
        spoiler: bool = False,
        overwrite: bool = False,
        on_progress=None,
    ) -> RandomizerRequest:
        """The shared request this product's run describes.

        ``enabled`` is resolved against this product's own module list here so a
        caller gets a refusal while building the request, and the same list travels
        on the request so the *service* enforces it too - the check that matters,
        because a hand-built request never passes through this method.
        """
        return RandomizerRequest(
            source_rom=Path(source_rom),
            output_rom=Path(output_rom),
            master_seed=str(seed),
            enabled=self.resolve_modules(enabled),
            allowed_modules=frozenset(MODULE_IDS),
            module_settings=dict(module_settings or {}),
            tool_name=TOOL_NAME,
            tool_version=self.tool_version,
            progression=PROGRESSION_DISCLAIMER,
            spoiler=bool(spoiler),
            overwrite=overwrite,
            on_progress=on_progress,
        )

    def randomize(self, request: RandomizerRequest) -> RandomizerResult:
        """The shared window protocol: run exactly the request it was handed.

        No product check here. An earlier version had one, and an independent
        review pointed out that the warp product did not - which is what happens
        when a rule is written per client instead of once. The rule now lives in
        :meth:`tools.webfoot.randomizer.service.RandomizerService.run`, enforced
        against :attr:`RandomizerRequest.allowed_modules`, so both products and any
        future one get it without remembering to.
        """
        return self._shared.run(request)

    def randomize(self, request: RandomizerRequest) -> RandomizerResult:
        """The shared window protocol: run exactly the request it was handed.

        There is deliberately no product check here. An earlier version had one,
        and an independent review pointed out that the warp product did not - which
        is what happens when a rule is written per client instead of once. The rule
        now lives in
        :meth:`tools.webfoot.randomizer.service.RandomizerService.run`, enforced
        against :attr:`RandomizerRequest.allowed_modules`, so both products and any
        future one get it without having to remember.
        """
        return self._shared.run(request)

    # --- the same call, spelled for a script -----------------------------

    def randomize_enemies(
        self,
        source_rom: str | Path,
        output_rom: str | Path,
        seed: str | int = DEFAULT_SEED,
        *,
        enabled=None,
        module_settings=None,
        spoiler: bool = False,
        overwrite: bool = False,
        on_progress=None,
    ) -> RandomizerResult:
        """One run, from a script or a test, without a window."""
        return self.randomize(
            self.build_request(
                source_rom,
                output_rom,
                seed,
                enabled=enabled,
                module_settings=module_settings,
                spoiler=spoiler,
                overwrite=overwrite,
                on_progress=on_progress,
            )
        )


# --- module-level conveniences ----------------------------------------------

_DEFAULT_SERVICE: EnemyRandomizerService | None = None


def default_service() -> EnemyRandomizerService:
    """The process-wide service. One catalog load for the whole application."""
    global _DEFAULT_SERVICE
    if _DEFAULT_SERVICE is None:
        _DEFAULT_SERVICE = EnemyRandomizerService()
    return _DEFAULT_SERVICE


__all__ = [
    "DEFAULT_SEED",
    "MANIFEST_SUFFIX",
    "MODULE_IDS",
    "OUTPUT_TEMPLATE",
    "PROGRESSION_DISCLAIMER",
    "PROGRESS_STEPS",
    "SPOILER_SUFFIX",
    "TOOL_NAME",
    "TOOL_VERSION",
    "EnemyRandomizerService",
    "default_output_path",
    "default_service",
    "random_seed",
    "sanitize_seed_for_filename",
    "shorten_hash",
]
