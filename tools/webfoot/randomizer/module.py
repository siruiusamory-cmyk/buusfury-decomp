"""The randomizer-module contract: what a module is, and what it may not do.

A module owns *semantics*. The application shell owns everything else - which
image is supported, what the output is called, whether a write is safe, what the
manifest and spoiler contain, how a window presents it. That split is the whole
reason this package exists, and the contract below is the seam.

A module therefore:

1. **never creates its own RNG.** It is handed its derived seed and, where it
   needs a stream, draws from the seed authority the pack already owns.
2. **never opens or writes the ROM.** It returns
   :class:`~tools.webfoot.write.ByteChange` objects and the one writer
   (:func:`~tools.webfoot.write.emit_image`) publishes them, so no module can
   bypass source-ROM protection.
3. **never sees a widget.** Nothing here imports Qt, and an architecture test
   asserts it.
4. **runs alone or beside its siblings**, because its seed is a function of the
   master seed and its own module id and of nothing else.

A module that cannot plan against an image or a settings combination refuses with
:class:`~tools.webfoot.randomizer.errors.ModuleRefusedError` - a sentence for a
person - rather than a bare ``ValueError`` the window would report as a crash.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import ClassVar, Mapping, Sequence

from ..write import ByteChange

#: The two setting kinds this project actually needs. Deliberately tiny: a
#: universal schema engine would be more machinery than three modules justify,
#: and the extension seam is what matters, not the vocabulary.
SETTING_BOOL = "bool"
SETTING_CHOICE = "choice"

SETTING_KINDS: tuple[str, ...] = (SETTING_BOOL, SETTING_CHOICE)


class ModuleContractError(ValueError):
    """A module violates the contract. A defect, not a user refusal."""


@dataclass(frozen=True, slots=True)
class SettingDescriptor:
    """One setting a module exposes, described rather than rendered.

    The shell turns this into a widget. A module that returned a widget instead
    would tie its algorithm to a toolkit and make "run this module headlessly"
    impossible, which is exactly the property the combined-mode proof needs.
    """

    key: str
    kind: str
    label: str
    help: str = ""
    default: object = False
    choices: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.kind not in SETTING_KINDS:
            raise ModuleContractError(
                f"setting {self.key!r}: unknown kind {self.kind!r}; "
                f"known: {', '.join(SETTING_KINDS)}"
            )
        if self.kind == SETTING_CHOICE:
            if not self.choices:
                raise ModuleContractError(
                    f"setting {self.key!r}: a choice needs at least one option"
                )
            if self.default not in self.choices:
                raise ModuleContractError(
                    f"setting {self.key!r}: default {self.default!r} is not one of "
                    f"{self.choices}"
                )
        elif self.choices:
            raise ModuleContractError(
                f"setting {self.key!r}: only a choice carries options"
            )
        if self.kind == SETTING_BOOL and not isinstance(self.default, bool):
            raise ModuleContractError(
                f"setting {self.key!r}: a boolean setting needs a boolean default"
            )


@dataclass(frozen=True, slots=True)
class ModulePlan:
    """What one module contributes to one run.

    ``changes`` are semantic byte edits against the verified base. The shell
    merges every enabled module's changes into ONE
    :class:`~tools.webfoot.write.WritePlan`, which refuses overlapping writes -
    so a module pair that would fight over a byte fails closed at the writer
    rather than resolving by order.
    """

    module_id: str
    changes: tuple[ByteChange, ...] = ()
    #: This module's own section of the shared manifest. Bounded, and additive.
    manifest: Mapping[str, object] = field(default_factory=dict)
    #: This module's own section of the combined spoiler document, or ``None``
    #: when the module has nothing to hide.
    spoiler: Mapping[str, object] | None = None
    #: One-line statements for the success readout, in the module's own words.
    summary_lines: tuple[str, ...] = ()
    #: Statements the manifest must carry because this module ran. The Module C
    #: disclosure travels here, so a run cannot record what it did without also
    #: recording what it did not do.
    limitations: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class GroupPlanRequest:
    """Everything a module group needs to plan, and nothing more.

    Deliberately not a superset of the service's own state: a module cannot reach
    the output path, the manifest path or the overwrite policy from here, because
    a module that could decide those would be a second application.
    """

    context: "RandomizerContextLike"
    master_seed: str
    #: The module ids of THIS group that are enabled. A group plans once and emits
    #: one :class:`ModulePlan` per enabled member.
    enabled: frozenset[str]
    #: Derived seed per module id, for every registered module - including the
    #: disabled ones, so a manifest always states what a run could have done.
    module_seeds: Mapping[str, str]
    #: Per-module settings, already merged with the module's declared defaults.
    settings: Mapping[str, Mapping[str, object]]
    #: The build/project commit to record, where the caller has one. A packaged
    #: user does not, and a missing commit is a provenance gap rather than a
    #: reason to refuse an otherwise reproducible run.
    sdk_commit: str | None = None


class RandomizerModule(ABC):
    """One randomizer, as the application shell sees it.

    Class attributes are declarations, not configuration: they are read by the
    registry before any run exists, so they must be answerable without a ROM.
    """

    #: The stable, permanent id. It is the manifest key, the seed namespace and
    #: the module's public name; renaming one is a format break.
    id: ClassVar[str]

    #: What a person reads.
    display_name: ClassVar[str]
    description: ClassVar[str]

    #: Whether a product that offers this module starts with it on.
    default_enabled: ClassVar[bool] = True

    #: The module's own algorithm version. Bump it when a change would alter the
    #: bytes this module produces for an unchanged seed, because a seed is only
    #: reproducible alongside the algorithm version that consumed it.
    algorithm_version: ClassVar[int] = 1

    #: The name of this module's seed derivation. Unique across the registry; the
    #: manifest records it beside the derived seed so a reader can tell how the
    #: seed was reached.
    seed_namespace: ClassVar[str]

    #: The phase caption this module contributes to the progress display.
    progress_label: ClassVar[str]

    #: Declared settings. Empty for a module with no knobs.
    settings: ClassVar[tuple[SettingDescriptor, ...]] = ()

    # --- identity --------------------------------------------------------

    @classmethod
    def describe(cls) -> dict:
        """The module's public description, for an About block or a manifest."""
        return {
            "id": cls.id,
            "display_name": cls.display_name,
            "description": cls.description,
            "algorithm_version": cls.algorithm_version,
            "seed_namespace": cls.seed_namespace,
            "default_enabled": cls.default_enabled,
        }

    # --- defaults --------------------------------------------------------

    @classmethod
    def default_settings(cls) -> dict[str, object]:
        return {setting.key: setting.default for setting in cls.settings}

    @classmethod
    def resolve_settings(cls, supplied: Mapping[str, object] | None) -> dict[str, object]:
        """The module's declared defaults, overridden by ``supplied``.

        An unknown key is refused rather than ignored: a silently dropped setting
        would run a different configuration than the one the caller asked for and
        the manifest would describe.
        """
        resolved = cls.default_settings()
        for key, value in (supplied or {}).items():
            if key not in resolved:
                raise ModuleContractError(
                    f"module {cls.id!r} has no setting {key!r}; "
                    f"known: {', '.join(sorted(resolved)) or 'none'}"
                )
            descriptor = next(s for s in cls.settings if s.key == key)
            if descriptor.kind == SETTING_CHOICE and value not in descriptor.choices:
                raise ModuleContractError(
                    f"module {cls.id!r} setting {key!r}: {value!r} is not one of "
                    f"{descriptor.choices}"
                )
            if descriptor.kind == SETTING_BOOL and not isinstance(value, bool):
                raise ModuleContractError(
                    f"module {cls.id!r} setting {key!r} takes a boolean"
                )
            resolved[key] = value
        return resolved

    # --- seed ------------------------------------------------------------

    @classmethod
    def derive_seed(cls, master_seed: str) -> str:
        """This module's seed for ``master_seed``.

        Modules that draw from a domain-separated stream override this. The
        default is the identity, and a module may only keep it by saying so: the
        identity is a legacy namespace whose outputs are history, and a *new*
        module that consumed the master seed directly would be able to perturb an
        existing module's result by being added.
        """
        raise ModuleContractError(
            f"module {cls.id!r} must declare how its seed is derived"
        )

    # --- the two calls the shell makes -----------------------------------

    @classmethod
    def validate(cls, context: "RandomizerContextLike", settings: Mapping[str, object]) -> None:
        """Refuse before anything is planned, or return.

        Default is to accept. A module with a real precondition (an image feature
        it needs, a settings combination it cannot honour) overrides this and
        raises :class:`~tools.webfoot.randomizer.errors.ModuleRefusedError`.

        A classmethod because a module is a stateless declaration: every call gets
        its context, its settings and its seed as arguments, so nothing about one
        run can survive into the next. That is what lets the registry hold classes
        and hand the SAME instance-free module to a GUI, a test and a corpus run.
        """

    @classmethod
    @abstractmethod
    def plan(
        cls,
        context: "RandomizerContextLike",
        settings: Mapping[str, object],
        *,
        seed: str,
    ) -> ModulePlan:
        """Plan this module against the verified image. Writes nothing."""


class RandomizerContextLike:
    """The slice of the run context a module is allowed to read.

    Declared as a protocol-by-documentation rather than a ``Protocol`` with a
    runtime check: the real context lives in :mod:`.context`, and a module that
    annotated its parameter with the concrete class would pull the whole loader
    stack into import time. What a module may use is:

    * ``context.path`` - the selected image, opened read-only;
    * ``context.profile`` - the verified :class:`~tools.webfoot.profile.RomProfile`;
    * ``context.identification`` - the :class:`~tools.webfoot.rom.RomIdentification`;
    * ``context.image()`` - the base bytes, cached for the whole run;
    * ``context.enemy_context()`` - the enemy pack's loaded context, built on
      first use and reused for every enemy module in the run.
    """


#: Convenience alias: a module group emits one plan per enabled member.
ModulePlans = Sequence[ModulePlan]
