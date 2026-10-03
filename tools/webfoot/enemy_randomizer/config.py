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
#: WHAT IT ACTUALLY DOES, which two independent reviews converged on and which two
#: earlier revisions of this comment got wrong in opposite directions:
#:
#: * within one coupled-field group the records differ ONLY in ``(type, id,
#:   position)``, so EXCHANGING identity between two members is equivalent to
#:   exchanging their positions. The group's multiset of records is unchanged;
#: * installing the coupled fields as well does not help. The factory word is
#:   constant across the corpus, so a record that receives another's ``(type, id,
#:   flags, descriptor)`` has simply BECOME that record. Measured: 0 of 949 such
#:   installs produced a record with no exact canonical match.
#:
#: So this module never changes a map's SET of enemies and never creates a record
#: that canonical does not already contain. It relocates identity within a group.
#:
#: It does NOT compose with the placement shuffle to the identity, and an earlier
#: revision wrongly said it did. The placement shuffle permutes the whole map's
#: eligible slots from its own independent seed, while this one permutes only within
#: coupled groups, so the composed arrangement is identity at a permuted position -
#: generally a NEW arrangement, and with ``--only enemy-type`` alone a player really
#: does meet a different enemy at a given spot inside each group.
#:
#: **Ticket Module C is NOT delivered** in the sense the ticket means, which is that
#: an ordinary enemy can become a different KIND of enemy: no identity crosses a
#: coupled-field boundary, so no enemy is retyped. The module is correct, it is a
#: strict relocation, and it is recorded as such - every manifest carries
#: ``configuration.delivers_ticket_module_c: false`` and the effect string below.
#:
#: A mode that really retyped would have to install an identity onto a slot with
#: DIFFERENT coupled fields, producing an object whose behavior descriptor belongs to
#: a different enemy than its sprite and stats. Nothing in this project establishes
#: that such an object is coherent, so this pack does not produce one; delivering
#: Module C needs a measured compatibility dimension first. See section 5.2 of
#: ``docs/research/ENEMY_RANDOMIZER_VERIFICATION.md``.
TYPING_PROVEN_PAIR = "proven-pair"

TYPING_MODES: dict[str, dict] = {
    TYPING_PROVEN_PAIR: {
        "installs": "identity only, onto a slot whose coupled fields already match",
        "player_visible_effect": (
            "relocation-equivalent within each coupled group: exchanges identity "
            "between slots whose other fields are identical. It never changes a "
            "map's set of enemies and never creates a record canonical does not "
            "already hold, so it cannot make one enemy become a different kind of "
            "enemy. Composed with the placement shuffle it yields identity at a "
            "permuted position, which is a new arrangement rather than the identity; "
            "on its own it does move which enemy stands at a given spot inside a group"
        ),
        "hybrid": "impossible by construction",
        "delivers_ticket_module_c": False,
    },
}


def typing_retypes(mode: str) -> bool:
    """Always False. Kept so a caller reads the reason rather than assuming.

    No mode of this module makes an enemy become a different kind of enemy; see
    :data:`TYPING_MODES`. The function exists so a future mode that *does* retype has
    an obvious place to say so, and so current callers cannot quietly assume the
    opposite.
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
    #: The default is the SHIPPING set, not "everything". A library caller who
    #: constructs a bare EnemyRandomizerConfig must not silently get the
    #: undelivered module, or the default and the preset would disagree about what a
    #: run does.
    enabled: frozenset[str] = field(default_factory=lambda: SHIPPING_MODULES)

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


#: The modules a preset may enable, and therefore the modules a SHIPPING run may
#: enable. The enemy-type module is deliberately absent.
#:
#: It is not in this set because it does not deliver what it is named for: on
#: current evidence its only coherent swap is a relocation of the coupled canonical
#: record (section 5.2 of the evidence document), so enabling it in a streamed run
#: would rewrite roughly 467 identities per seed - measured as 949 flags-or-descriptor rewrites in the removed retyping mode, and 467 identity swaps in the surviving one - to change nothing a player can
#: perceive, while lending the preset an implied capability it does not have. A
#: preset that enabled it would be a claim.
#:
#: The module stays compiled and tested so the research result is reproducible and so
#: a future ticket has somewhere to put a real compatibility dimension. It remains
#: reachable ONLY by asking for it explicitly through ``--only enemy-type``, which
#: reports ``delivers_ticket_module_c: false`` in its manifest like every other run.
SHIPPING_MODULES: frozenset[str] = frozenset(
    {MODULE_ENEMY_PLACEMENT, MODULE_ENEMY_STAT}
)

#: The acceptance target: a conservative run for an actual streamed playthrough.
#:
#: Composed of PROVEN modules only. Placements move between slots the map already
#: had, and stats move by at most 35% of their own original values. Excluded by
#: construction rather than by a list: every actor the model cannot positively
#: classify, every script-attached placement, every placement whose script root was
#: never decoded, every selector outside the verified stat extent, and any slot
#: sitting in a door trigger.
#:
#: The enemy-type module is DISABLED here. It is not a proven module; see
#: :data:`SHIPPING_MODULES`.
STREAM_SAFE = Preset(
    name="stream-safe",
    description=(
        "Conservative streamed-playthrough preset for a blind run. Enables the "
        "proven modules only: same-map enemy PLACEMENT shuffling over canonically "
        "proven slots, plus bounded enemy stat randomization within 0.75x-1.35x of "
        "each record's original values. Enemy-TYPE randomization is DISABLED and "
        "Module C is undelivered; the manifest states this on every run."
    ),
    config=EnemyRandomizerConfig(stat_range=STREAM_SAFE_STATS, enabled=SHIPPING_MODULES),
)

#: The aggressive band, kept deliberately small in scope: it changes the
#: multiplier range and nothing else, so enabling it cannot widen eligibility or
#: reach an actor the safe preset leaves alone. It enables the same proven modules.
CHAOS = Preset(
    name="chaos",
    description=(
        "Aggressive stats only: the same proven modules, slots and exclusions as "
        "stream-safe, with enemy stats scaled within 0.5x-2.0x of their original "
        "values. Enemy-TYPE randomization remains DISABLED and Module C is "
        "undelivered."
    ),
    config=EnemyRandomizerConfig(stat_range=CHAOS_STATS, enabled=SHIPPING_MODULES),
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
