"""Configuration and presets for the enemy randomizer pack.

Every knob is a value in a frozen dataclass, so a configuration can be hashed
into the manifest and compared between runs. Nothing here reads the environment,
the clock, or a file: the same object always describes the same randomization.

Bounded policies, not arbitrary integers
========================================

The stat policy is **multiplicative around each record's own original value**::

    randomized = clamp(original * numerator / denominator)

and never ``random(global_min, global_max)``. That distinction is the ticket's
progression safeguard and it is the whole reason a level-1 area cannot receive
an endgame number: a weak enemy scaled by at most 2.0 stays weak, while the same
multiplier on an endgame enemy stays endgame. A global range would flatten the
game's progression curve into noise.

The arithmetic is integer-only (``original * numerator // denominator``), so
there is no floating-point rounding question and the result is bit-identical on
every machine.

Ranges were chosen after measuring the canonical corpus, not guessed. Over the
118 stat-linked selectors: ``hp`` 1..125000 (u24), ``exp`` 0..236265 (u24),
``level`` 1..175 (u8), ``strength`` 0..130, ``power`` 0..110,
``endurance`` 0..125 (all u8). Every field therefore has ample headroom under
both presets, and the per-field ceiling in :mod:`stat_fields` is the real bound.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from fractions import Fraction

from .seeds import MODULE_ENEMY_PLACEMENT, MODULE_ENEMY_STAT, MODULE_ENEMY_TYPE


class ConfigError(ValueError):
    """A configuration that cannot describe a legal run."""


@dataclass(frozen=True, slots=True)
class StatRange:
    """A multiplicative band, as an exact rational.

    ``low``/``high`` are :class:`~fractions.Fraction` so ``0.75`` is exactly
    three quarters rather than the nearest double. The band is applied per field
    as ``original * f``, floored, and then clamped to the field's legal domain.
    """

    low: Fraction
    high: Fraction
    label: str

    def __post_init__(self) -> None:
        if self.low <= 0 or self.high <= 0:
            raise ConfigError(f"{self.label}: a multiplier band must be positive")
        if self.low > self.high:
            raise ConfigError(
                f"{self.label}: low multiplier {self.low} exceeds high {self.high}"
            )

    @classmethod
    def of(cls, low: str | int | Fraction, high: str | int | Fraction, label: str) -> "StatRange":
        """Build a band from exact literals, e.g. ``StatRange.of("3/4", "27/20")``."""
        return cls(Fraction(low), Fraction(high), label)

    def to_json(self) -> dict:
        return {"low": str(self.low), "high": str(self.high), "label": self.label}


#: The conservative band for an actual streamed playthrough. Deliberately narrow:
#: variety without turning a fight into a coin flip, and no value can move more
#: than 35% in either direction.
STREAM_SAFE_STATS = StatRange.of("3/4", "27/20", "stream-safe")

#: The aggressive band. Present because it costs nothing once the policy exists,
#: not because it is the acceptance target. A 2x ceiling on a level-1 enemy is
#: still a level-1 enemy, which is what keeps this from breaking progression.
CHAOS_STATS = StatRange.of("1/2", "2", "chaos")

#: The stat fields this pack will randomize, and their legal domains.
#:
#: Two independent bounds meet here and the tighter one wins, which is why these
#: are not simply "the width of the field":
#:
#: * the **storage** width, from the codec (``formats/stat_tables.py``):
#:   ``exp``/``hp`` are u24, the other four are u8. A value outside these does not
#:   fit the bytes and the codec refuses to encode it.
#: * the **domain** the stat authority enforces
#:   (``tools.webfoot.stats.ENEMY_FIELDS``): ``level`` is bounded to 1..200,
#:   which is the game's level cap measured at ``0x08013A00``
#:   (``cmp r6, #0xc8``). A u8 could hold 255, but a level above 200 is outside
#:   the game's own model, so 200 is the correct ceiling and 255 would be a bug
#:   waiting for a high-rolling seed.
#:
#: ``hp`` IN THIS RECORD IS THE DISPLAYED HIT-POINT VALUE, not a fixed-point
#: quantity. The measured evidence is the repository's own identification oracle:
#: the wolf is found by ``find_enemies_by_hp(175)``
#: (``tools/webfoot/formats/stat_tables.py``), i.e. the record holds 175 - the
#: number the player sees. P-010's 1024-raw-units-per-displayed-point figure
#: describes the RUNTIME ACTOR's HP, a different quantity in a different place.
#: Applying it here puts a floor of 1024 under a field whose observed values run
#: down to 1, so every record below 1024 would be clamped upward whatever the seed.
#: The floor is therefore 1: a displayed HP of zero would be a dead enemy. See
#: section 6 of ``docs/research/ENEMY_RANDOMIZER_VERIFICATION.md``.
#:
#: Zero is a legal value for ``exp``, ``strength``, ``power`` and ``endurance``
#: (measured: 13, 25, 47 and 4 records respectively), so their floor is 0 and a
#: multiplicative policy leaves an original zero at zero rather than inventing a
#: minimum. ``hp`` and ``level`` have nonzero floors because zero would make the
#: enemy invalid rather than merely weak.
MINIMUM_ENEMY_HP = 1

#: u24 ceiling, shared by the two 24-bit fields.
_U24_MAX = (1 << 24) - 1

#: The game's own level cap, from `tools.webfoot.stats.ENEMY_FIELDS`.
MAXIMUM_ENEMY_LEVEL = 200

STAT_FIELDS: dict[str, tuple[int, int]] = {
    "hp": (MINIMUM_ENEMY_HP, _U24_MAX),
    "exp": (0, _U24_MAX),
    "level": (1, MAXIMUM_ENEMY_LEVEL),
    "strength": (0, 255),
    "power": (0, 255),
    "endurance": (0, 255),
}

#: The default field set. ``type_id`` is deliberately absent: it is the record's
#: identity, not a stat, and randomizing it would silently rewrite the placement
#: type relationship the eligibility model depends on.
DEFAULT_STAT_FIELDS: tuple[str, ...] = ("hp", "exp", "level", "strength", "power", "endurance")


#: How the enemy-type module chooses which slots an identity may be installed onto.
#:
#: There is exactly one mode, and it exists because no other is available on this
#: evidence. It installs an identity only onto a slot whose flags, behavior
#: descriptor and children already match the donor's, so every resulting object is a
#: configuration some canonical placement holds.
#:
#: ITS CONSEQUENCE, which two independent reviews converged on and which this file
#: previously mis-described twice:
#:
#: * within one such group the records differ ONLY in ``(type, id, position)``, so
#:   exchanging ``(type, id)`` between two members is exactly exchanging their
#:   positions; and
#: * installing the coupled fields as well does not help either. The factory word is
#:   constant across the corpus, so a record that receives another record's
#:   ``(type, id, flags, descriptor)`` has simply BECOME that record; the map ends up
#:   holding the same multiset of canonical records in different places. Measured:
#:   0 of 949 such installs produced a record with no exact canonical match.
#:
#: So this module cannot change what enemy a player meets. Either it permutes
#: identity within field-identical records, which composes with the placement
#: shuffle to the identity permutation, or it permutes whole records, which is a
#: relocation by another name. **Ticket Module C is NOT delivered**, and claiming
#: otherwise was the error two reviews caught. What the module does deliver is a
#: well-defined, validated permutation over proven slots, which is why it stays
#: compiled and tested rather than deleted: it is correct, it is inert with respect
#: to the world, and it costs one pass over the corpus.
#:
#: A mode that really retyped would have to install an identity onto a slot with
#: DIFFERENT coupled fields, producing an object whose behavior descriptor belongs to
#: a different enemy than its sprite and stats. Nothing in this project establishes
#: that such an object is coherent, so this pack does not produce one. Delivering
#: Module C needs a measured compatibility dimension first; see section 5.2 of
#: ``docs/research/ENEMY_RANDOMIZER_VERIFICATION.md``.
TYPING_PROVEN_PAIR = "proven-pair"

TYPING_MODES: dict[str, dict] = {
    TYPING_PROVEN_PAIR: {
        "installs": "identity only, onto a slot whose coupled fields already match",
        "player_visible_effect": (
            "none: enemies are relocated, not retyped. With the placement shuffle "
            "also enabled the two compose to the identity, and neither mode of this "
            "module can change which enemy a player meets"
        ),
        "hybrid": "impossible by construction",
        "delivers_ticket_module_c": False,
    },
}


def typing_retypes(mode: str) -> bool:
    """Always False. Kept so a caller reads the reason rather than assuming.

    No mode of this module changes an enemy's type; see :data:`TYPING_MODES`. The
    function exists so that a future mode which *does* retype has an obvious place
    to say so, and so that current callers cannot quietly assume the opposite.
    """
    return False


@dataclass(frozen=True, slots=True)
class EnemyRandomizerConfig:
    """One complete description of a run.

    ``enabled`` names the modules to run. A module that is absent is skipped
    entirely and its seed is still derived and recorded, so a manifest always
    states what a run *could* have done as well as what it did.

    Module independence is a property of the seeds, not of this object, so
    flipping a flag here cannot perturb a module that stayed on.
    """

    stat_range: StatRange | None = STREAM_SAFE_STATS
    stat_fields: tuple[str, ...] = DEFAULT_STAT_FIELDS
    placement_scope: str = "same-map"
    type_scope: str = "same-map"
    type_requires_canonical_pair: bool = True
    #: Which slots an identity may be installed onto. One mode exists; see
    #: :data:`TYPING_MODES` for why, and for what it does and does not deliver.
    typing_mode: str = TYPING_PROVEN_PAIR
    enabled: frozenset[str] = field(
        default_factory=lambda: frozenset(
            {MODULE_ENEMY_TYPE, MODULE_ENEMY_PLACEMENT, MODULE_ENEMY_STAT}
        )
    )

    def __post_init__(self) -> None:
        if self.placement_scope != "same-map":
            raise ConfigError(
                f"unsupported placement scope {self.placement_scope!r}; this "
                "version shuffles proven slots within one map only"
            )
        if self.type_scope != "same-map":
            raise ConfigError(
                f"unsupported type scope {self.type_scope!r}; this version "
                "shuffles canonical identity pairs within one map only"
            )
        if not self.type_requires_canonical_pair:
            raise ConfigError(
                "this version only shuffles canonical (stat selector, sprite id) "
                "pairs; composing a pair no canonical placement exercises would "
                "produce a hybrid entity"
            )
        unknown = set(self.stat_fields) - set(STAT_FIELDS)
        if unknown:
            raise ConfigError(
                f"unknown stat field(s): {', '.join(sorted(unknown))}; "
                f"known: {', '.join(sorted(STAT_FIELDS))}"
            )
        if self.typing_mode not in TYPING_MODES:
            raise ConfigError(
                f"unknown typing mode {self.typing_mode!r}; known: "
                f"{', '.join(sorted(TYPING_MODES))}"
            )
        if self.stat_range is not None and MODULE_ENEMY_STAT in self.enabled and not self.stat_fields:
            raise ConfigError("stat randomization is enabled but no stat field is selected")
        if MODULE_ENEMY_STAT in self.enabled and self.stat_range is None:
            raise ConfigError("stat randomization is enabled but no stat range is configured")

    def wants(self, module_id: str) -> bool:
        return module_id in self.enabled

    def to_json(self) -> dict:
        """The configuration block of a manifest, stable under key ordering."""
        return {
            "enabled_modules": sorted(self.enabled),
            "stat_range": self.stat_range.to_json() if self.stat_range else None,
            "stat_fields": list(self.stat_fields),
            "placement_scope": self.placement_scope,
            "type_scope": self.type_scope,
            "type_requires_canonical_pair": self.type_requires_canonical_pair,
            "typing_mode": self.typing_mode,
            # The mode's consequence travels with the manifest, so a reader learns
            # what the run actually did rather than what its module is called.
            "typing_mode_effect": TYPING_MODES[self.typing_mode]["player_visible_effect"],
            "delivers_ticket_module_c": TYPING_MODES[self.typing_mode][
                "delivers_ticket_module_c"
            ],
        }


@dataclass(frozen=True, slots=True)
class Preset:
    """A named configuration plus the prose a user needs to judge it."""

    name: str
    description: str
    config: EnemyRandomizerConfig

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "enabled_modules": sorted(self.config.enabled),
            "stat_range": self.config.stat_range.label if self.config.stat_range else None,
        }


def _all_enemy_modules() -> frozenset[str]:
    return frozenset({MODULE_ENEMY_TYPE, MODULE_ENEMY_PLACEMENT, MODULE_ENEMY_STAT})


#: The acceptance target: a conservative run for an actual streamed playthrough.
#:
#: Everything randomized is bounded and reversible in effect: identities come
#: only from pairs the retail engine already builds, placements only move
#: between slots the map already had, and stats move by at most 35%. Excluded by
#: construction rather than by a list: every actor the model cannot positively
#: classify, every script-attached placement, every selector outside the verified
#: stat extent, and any slot sitting in a door trigger.
STREAM_SAFE = Preset(
    name="stream-safe",
    description=(
        "Conservative streamed-playthrough preset: same-map enemy identity and "
        "placement shuffles over canonically proven pairs and slots, with enemy "
        "stats scaled within 0.75x-1.35x of their original values."
    ),
    config=EnemyRandomizerConfig(stat_range=STREAM_SAFE_STATS),
)

#: The aggressive band, kept deliberately small in scope: it changes the
#: multiplier range and nothing else, so enabling it cannot widen eligibility or
#: reach an actor the safe preset leaves alone.
CHAOS = Preset(
    name="chaos",
    description=(
        "Aggressive stats only: the same proven identities, slots and "
        "exclusions as stream-safe, with enemy stats scaled within 0.5x-2.0x of "
        "their original values."
    ),
    config=EnemyRandomizerConfig(stat_range=CHAOS_STATS),
)

#: The warp randomizer's module is not run by these presets: it is a separate
#: product with its own output and its own manifest. It appears here only as a
#: seed the pack derives (see :mod:`seeds`), which is what lets one master seed
#: address a warp + enemy run without the two sharing a stream.
PRESETS: dict[str, Preset] = {preset.name: preset for preset in (STREAM_SAFE, CHAOS)}


def preset(name: str) -> Preset:
    """Look a preset up by name, refusing an unknown one rather than guessing."""
    try:
        return PRESETS[name]
    except KeyError:
        raise ConfigError(
            f"unknown preset {name!r}; available: {', '.join(sorted(PRESETS))}"
        ) from None


def with_modules(
    config: EnemyRandomizerConfig, *, enabled: frozenset[str] | None = None
) -> EnemyRandomizerConfig:
    """A copy of ``config`` with a different enabled set."""
    if enabled is None:
        return config
    return replace(config, enabled=frozenset(enabled))
