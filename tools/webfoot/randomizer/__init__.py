"""The shared randomizer application foundation.

One shell, several modules
==========================

This package exists because the project now ships more than one randomizer and
intends to ship more. Before it, each randomizer carried its own ROM picker, its
own output naming, its own manifest shape and its own idea of what "safe" means.
That was affordable with one product and unaffordable with three, because the
eventual combined tool has to run several modules against one ROM and produce one
output, one manifest and one spoiler - which is only possible if those things
belong to the application rather than to a module.

The layers, outermost last::

    tools/webfoot/randomizer/module.py       what a module is and may not do
    tools/webfoot/randomizer/registry.py     which modules exist, in what order
    tools/webfoot/randomizer/modules/        map-warp, enemy-placement, enemy-stat
    tools/webfoot/randomizer/context.py      one verified image, loaded once
    tools/webfoot/randomizer/service.py      one run, one safe write, one record
    tools/webfoot/randomizer/gui.py          one window over that boundary
    <product>/gui.py                          a product's configuration of it

Standalone products are *compositions*, not applications
========================================================

The shipped executables are thin configured entrypoints::

    Map Warp Randomizer   -> RandomizerApp(allowed_modules=["map-warp"])
    Enemy Randomizer      -> RandomizerApp(allowed_modules=[
                                 "enemy-placement", "enemy-stat"])

The eventual combined ``Buu's Fury Randomizer`` is the same shell with three ids
in that list. If adding it ever requires copying GUI or backend code, this package
has failed at the one thing it was built to do.

What this package deliberately does not have
============================================

No plugin loading, no entry-point discovery, no dependency injection, no scripting
hook, no runtime module download and no generic workflow engine. The registry is a
static tuple, the module contract is five class attributes and two methods, and
the settings vocabulary is two kinds. Three proven modules and several obvious
future ones were the design target; a marketplace was not.
"""

from __future__ import annotations

from .context import RandomizerContext
from .errors import (
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
from .manifest import FORMAT_VERSION, build_manifest, canonical_json, document_digest
from .module import (
    SETTING_BOOL,
    SETTING_CHOICE,
    GroupPlanRequest,
    ModuleContractError,
    ModulePlan,
    RandomizerModule,
    SettingDescriptor,
)
from .registry import (
    MODULE_ORDER,
    ModuleGroup,
    default_enabled_ids,
    derive_module_seeds,
    known_module_ids,
    module_for,
    modules,
    plan_modules,
    progress_steps,
    resolve_enabled,
    validate_registry,
)
from .service import (
    MANIFEST_SUFFIX,
    SPOILER_SUFFIX,
    ProgressCallback,
    RandomizerRequest,
    RandomizerResult,
    RandomizerService,
    RomVerification,
    default_manifest_path,
    default_output_path,
    default_service,
    default_spoiler_path,
    random_seed,
    sanitize_seed_for_filename,
    shorten_hash,
)
from .spoiler import build_spoiler

__all__ = [
    "FORMAT_VERSION",
    "GroupPlanRequest",
    "MANIFEST_SUFFIX",
    "MODULE_ORDER",
    "ManifestWriteError",
    "ModuleConflictError",
    "ModuleContractError",
    "ModuleGroup",
    "ModulePlan",
    "ModuleRefusedError",
    "OutputAlreadyExistsError",
    "OutputPathRefusedError",
    "ProgressCallback",
    "RandomizerAppError",
    "RandomizerContext",
    "RandomizerModule",
    "RandomizerRequest",
    "RandomizerResult",
    "RandomizerService",
    "RomVerification",
    "SETTING_BOOL",
    "SETTING_CHOICE",
    "SPOILER_SUFFIX",
    "SeedRefusedError",
    "SettingDescriptor",
    "SourceChangedError",
    "UnsupportedRomError",
    "build_manifest",
    "build_spoiler",
    "canonical_json",
    "default_enabled_ids",
    "default_manifest_path",
    "default_output_path",
    "default_service",
    "default_spoiler_path",
    "derive_module_seeds",
    "document_digest",
    "known_module_ids",
    "module_for",
    "modules",
    "plan_modules",
    "progress_steps",
    "random_seed",
    "resolve_enabled",
    "sanitize_seed_for_filename",
    "shorten_hash",
    "validate_registry",
]
