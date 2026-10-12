"""Frozen dataclasses must not hand out a mutable container.

A frozen dataclass stops a field from being rebound. It does not stop the
container in that field from being written, so a caller that mutates the mapping
changes a value the class told everyone was fixed. That shape reached review
three times in the DBZ lane: ``RawEdits.bytes_by_offset`` (fixed at ``bf34499``),
the SDK's ``RawByteEdits`` (``3c00c810``), and a third copy the 2026-10-12 retro
recorded as still latent in QA-era code, which this walk reports no longer
exists (``tools/qa`` now holds no dataclass at all). Each round cost a reviewer
the same measurement, which is what this file does once, over ``tools/``.

The rule: a field of a frozen dataclass annotated ``dict``, ``list`` or ``set``
(the ``typing`` spellings and ``X | None`` / ``Optional[X]`` included) is a
defect unless ``__post_init__`` rebinds it to something that is not a fresh
mutable container. ``Mapping``, ``Sequence``, ``tuple`` and ``frozenset`` are
accepted as written.

The allowlist below is the legacy set measured at
``c3fc145c2f7f0c15b60dbcd8f1e2271b430f39ec``: 27 classes, 49 fields. An ast
store-sweep of the same tree (subscript stores, mutator calls, deletes) finds
exactly two places where such a class writes into its own container field:
``RecordEdits.edits`` (``enemy_randomizer/records.py:85``, a deliberate
accumulator) and ``TextSurface._inventory_cache`` (``dragonbyte/textsurface.py``
:459, a documented cache). Every other entry is read-only in practice and carries
the reason it is not wrapped.

Two ceilings, stated rather than implied:

* A field NAME added to an allowlisted class is not covered, so the allowlist
  cannot hide a new one; a field whose containers are only nested inside an
  accepted annotation (``Mapping[str, dict]``) is not inspected.
* An allowlist entry for a class that no longer exists is not an error, so a
  rename fails loudly at the renamed class instead of silently.
"""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS = REPO_ROOT / "tools"

#: Annotations that hand out a container the reader can write.
MUTABLE_CONTAINERS = frozenset(
    {
        "ChainMap",
        "Counter",
        "Dict",
        "List",
        "MutableMapping",
        "MutableSequence",
        "MutableSet",
        "OrderedDict",
        "Set",
        "defaultdict",
        "deque",
        "dict",
        "list",
        "set",
    }
)

#: Calls whose result is an immutable view of the input.
IMMUTABLE_WRAPPERS = frozenset({"MappingProxyType", "frozenset", "tuple"})

#: Calls and displays that are a fresh mutable container, so a rebind to one is
#: not a wrap.
MUTABLE_RHS = (ast.Dict, ast.List, ast.Set, ast.DictComp, ast.ListComp, ast.SetComp)

_SURFACE = (
    "derived state about an immutable image, set through object.__setattr__ because the "
    "record is frozen and slotted (textsurface.py:290-295): the caches are built on first "
    "use and the inventory cache is filled as selectors are read (textsurface.py:445-459); "
    "the two lookup tables are built by the loader and read afterwards"
)
_CACHE = (
    "an index built once from the record's own immutable tables and read afterwards "
    "(eligibility.py:186-193, atlas.py:717-727)"
)
_DOCUMENT = (
    "the authored project document's own record tables (model.py:286-322): the loader "
    "builds a new document and the writers read these tables, so the freeze stops a "
    "field swap and not a table edit; reading the tables as immutable is a separate "
    "change with its own callers"
)
_PAYLOAD = (
    "the record's own published document: to_json() returns these mappings directly "
    "(enemy_randomizer/manifest.py:86-118, write.py:966-979)"
)
_RESULT = (
    "a run or render result record whose mapping is read, never written by its own "
    "class: the ast store-sweep over tools/ reports no write site for it"
)
_ACCUMULATOR = (
    "an accumulator, not a value: set() writes into edits (records.py:78-85), the one "
    "place in tools/ where a frozen class writes into its own container field; the "
    "freeze here stops rebinding only, and changing the accumulator's API is its own "
    "ticket"
)
_RESEARCH = (
    "a research script's in-process result object; no other module reads it"
)

#: (path relative to the repository root, class name) -> (field names, reason).
ALLOWLIST: dict[tuple[str, str], tuple[frozenset[str], str]] = {
    ("tools/dragonbyte/textsurface.py", "TextSurface"): (
        frozenset({"_dialogue_cache", "_event_cache", "_inventory_cache", "_records_cache",
                   "_target_cache", "corpora", "pool_offsets"}), _SURFACE,
    ),
    ("tools/research/build_dialogue_token_engine.py", "Body"): (
        frozenset({"words"}), _RESEARCH,
    ),
    ("tools/research/dialogue_wrap_sim.py", "Font"): (
        frozenset({"code_map"}), _RESEARCH,
    ),
    ("tools/research/logx_frame_probe.py", "AnimationWalk"): (
        frozenset({"frame_piece_counts", "unique_frame_targets"}), _RESEARCH,
    ),
    ("tools/research/sprite_new_runtime.py", "Experiment"): (
        frozenset({"report"}), _RESEARCH,
    ),
    ("tools/research/sprite_new_runtime.py", "PaletteAssignment"): (
        frozenset({"index_of_colour"}), _RESEARCH,
    ),
    ("tools/webfoot/atlas.py", "RangeIndex"): (
        frozenset({"_by_owner"}), _CACHE,
    ),
    ("tools/webfoot/enemy_randomizer/eligibility.py", "SlotModel"): (
        frozenset({"refusal_index"}), _CACHE,
    ),
    ("tools/webfoot/enemy_randomizer/manifest.py", "RunManifest"): (
        frozenset({"configuration", "exclusions", "module_seeds", "module_summaries",
                   "slot_summary"}), _PAYLOAD,
    ),
    ("tools/webfoot/enemy_randomizer/manifest.py", "SpoilerLog"): (
        frozenset({"module_seeds", "module_summaries"}), _PAYLOAD,
    ),
    ("tools/webfoot/enemy_randomizer/planner.py", "EnemyRandomization"): (
        frozenset({"module_seeds"}), _RESULT,
    ),
    ("tools/webfoot/enemy_randomizer/records.py", "RecordEdits"): (
        frozenset({"edits"}), _ACCUMULATOR,
    ),
    ("tools/webfoot/enemy_randomizer/stats.py", "StatDecision"): (
        frozenset({"original", "randomized"}), _RESULT,
    ),
    ("tools/webfoot/map_render.py", "MapRenderResult"): (
        frozenset({"provenance"}), _RESULT,
    ),
    ("tools/webfoot/project/model.py", "AuthoredAppearances"): (
        frozenset({"appearances"}), _DOCUMENT,
    ),
    ("tools/webfoot/project/model.py", "AuthoredChunks"): (
        frozenset({"chunks"}), _DOCUMENT,
    ),
    ("tools/webfoot/project/model.py", "AuthoredMaps"): (
        frozenset({"maps"}), _DOCUMENT,
    ),
    ("tools/webfoot/project/model.py", "AuthoredSprite"): (
        frozenset({"animations"}), _DOCUMENT,
    ),
    ("tools/webfoot/project/model.py", "AuthoredSprites"): (
        frozenset({"sprites"}), _DOCUMENT,
    ),
    ("tools/webfoot/project/model.py", "GraphicsOverrides"): (
        frozenset({"palette", "pixels"}), _DOCUMENT,
    ),
    ("tools/webfoot/project/model.py", "LayoutEdits"): (
        frozenset({"maps"}), _DOCUMENT,
    ),
    ("tools/webfoot/project/model.py", "MapStructure"): (
        frozenset({"layers", "resizes"}), _DOCUMENT,
    ),
    ("tools/webfoot/project/model.py", "StatProject"): (
        frozenset({"characters", "dialogues", "enemies", "maps", "placement_events",
                   "placement_types", "strings"}), _DOCUMENT,
    ),
    ("tools/webfoot/project/model.py", "TransitionCreations"): (
        frozenset({"creations"}), _DOCUMENT,
    ),
    ("tools/webfoot/project/model.py", "TransitionEdits"): (
        frozenset({"maps"}), _DOCUMENT,
    ),
    ("tools/webfoot/tileset_compositor.py", "RenderedView"): (
        frozenset({"detail"}), _RESULT,
    ),
    ("tools/webfoot/write.py", "SpriteAuthoringProvenance"): (
        frozenset({"actor", "identity"}), _PAYLOAD,
    ),
}


def _name_of(node: ast.expr) -> str | None:
    """The name an expression denotes, unwrapping a quoted annotation."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        try:
            return _name_of(ast.parse(node.value, mode="eval").body)
        except SyntaxError:
            return None
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Subscript):
        return _name_of(node.value)
    return None


def _container_of(annotation: ast.expr) -> str | None:
    """The mutable container an annotation hands out, if any.

    ``Optional``, ``Union`` and ``X | None`` are looked through, because a field
    that may be ``None`` still hands out a dict when it is not.
    """
    if isinstance(annotation, ast.Constant) and isinstance(annotation.value, str):
        try:
            return _container_of(ast.parse(annotation.value, mode="eval").body)
        except SyntaxError:
            return None
    if isinstance(annotation, ast.BinOp) and isinstance(annotation.op, ast.BitOr):
        for side in (annotation.left, annotation.right):
            found = _container_of(side)
            if found is not None:
                return found
        return None
    if isinstance(annotation, ast.Subscript):
        base = _name_of(annotation.value)
        if base in {"Optional", "Union"}:
            for item in ast.walk(annotation.slice):
                if isinstance(item, ast.expr):
                    found = _container_of(item)
                    if found is not None:
                        return found
            return None
        return base if base in MUTABLE_CONTAINERS else None
    if isinstance(annotation, ast.Name):
        return annotation.id if annotation.id in MUTABLE_CONTAINERS else None
    name = _name_of(annotation)
    return name if name in MUTABLE_CONTAINERS else None


def _is_frozen(cls: ast.ClassDef) -> bool:
    for decorator in cls.decorator_list:
        node = decorator.func if isinstance(decorator, ast.Call) else decorator
        if _name_of(node) != "dataclass":
            continue
        if not isinstance(decorator, ast.Call):
            return False
        return any(
            keyword.arg == "frozen"
            and isinstance(keyword.value, ast.Constant)
            and bool(keyword.value.value)
            for keyword in decorator.keywords
        )
    return False


def _rebinds_immutably(post_init: ast.FunctionDef | None) -> set[str]:
    """Field names ``__post_init__`` rebuilds from something that is not mutable.

    A rebind to a name the reader cannot see into (a tuple built a few lines up)
    counts: the guard's question is whether the class rebuilds the container, and
    the annotation is what states the type a reader may rely on.
    """
    wrapped: set[str] = set()
    if post_init is None:
        return wrapped
    for call in ast.walk(post_init):
        if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Attribute):
            continue
        if call.func.attr != "__setattr__" or _name_of(call.func.value) != "object":
            continue
        if len(call.args) < 3 or not isinstance(call.args[1], ast.Constant):
            continue
        field, value = call.args[1].value, call.args[2]
        if isinstance(value, MUTABLE_RHS):
            continue
        called = {_name_of(inner.func) for inner in ast.walk(value) if isinstance(inner, ast.Call)}
        if called & IMMUTABLE_WRAPPERS:
            wrapped.add(field)
        elif not called & MUTABLE_CONTAINERS:
            wrapped.add(field)
    return wrapped


def mutable_container_fields(
    source: str, filename: str = "<synthetic>"
) -> list[tuple[str, str, int]]:
    """``(class, field, line)`` for every frozen field that hands out a container."""
    found: list[tuple[str, str, int]] = []
    for cls in ast.walk(ast.parse(source, filename=filename)):
        if not isinstance(cls, ast.ClassDef) or not _is_frozen(cls):
            continue
        post_init = next(
            (item for item in cls.body
             if isinstance(item, ast.FunctionDef) and item.name == "__post_init__"),
            None,
        )
        wrapped = _rebinds_immutably(post_init)
        for statement in cls.body:
            if not isinstance(statement, ast.AnnAssign):
                continue
            if not isinstance(statement.target, ast.Name):
                continue
            if _container_of(statement.annotation) is None:
                continue
            if statement.target.id in wrapped:
                continue
            found.append((cls.name, statement.target.id, statement.lineno))
    return found


def _tools_hits() -> list[tuple[str, str, str, int]]:
    """``(path, class, field, line)`` for every field under tools/ that is not wrapped."""
    hits: list[tuple[str, str, str, int]] = []
    for path in sorted(TOOLS.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        relative = path.relative_to(REPO_ROOT).as_posix()
        source = path.read_text(encoding="utf-8")
        for cls, field, line in mutable_container_fields(source, relative):
            hits.append((relative, cls, field, line))
    return hits


def test_no_frozen_dataclass_in_tools_hands_out_a_mutable_container() -> None:
    """The rule, over every module under tools/."""
    unwrapped = [
        f"{path}:{line} {cls}.{field}"
        for path, cls, field, line in _tools_hits()
        if field not in ALLOWLIST.get((path, cls), (frozenset(), ""))[0]
    ]
    assert not unwrapped, (
        "a frozen dataclass hands out a mutable container. Wrap it in __post_init__ "
        "with object.__setattr__ (MappingProxyType for a dict, tuple for a list, "
        "frozenset for a set), annotate the immutable view instead, or add the field "
        "to ALLOWLIST in this file with the reason it is deliberate:\n  "
        + "\n  ".join(unwrapped)
    )


def test_every_allowlist_entry_states_a_reason() -> None:
    """An allowlist entry without a reason is a silent exemption."""
    for entry, (fields, reason) in ALLOWLIST.items():
        assert fields, f"{entry} allowlists no field"
        assert reason.strip(), f"{entry} states no reason"


def test_the_walk_flags_a_field_that_hands_out_a_dict() -> None:
    assert mutable_container_fields(
        "from dataclasses import dataclass, field\n"
        "@dataclass(frozen=True)\n"
        "class Sample:\n"
        "    items: dict[str, int] = field(default_factory=dict)\n"
    ) == [("Sample", "items", 4)]


def test_the_walk_looks_through_optional_and_the_typing_spellings() -> None:
    for annotation in ("dict | None = None", "Optional[Dict[str, int]] = None",
                       "List[int] = field(default_factory=list)", "Set[int] | None = None",
                       '"dict[str, int]" = None'):
        assert mutable_container_fields(
            "from dataclasses import dataclass, field\n"
            "from typing import Dict, List, Optional, Set\n"
            "@dataclass(frozen=True)\n"
            "class Sample:\n"
            f"    items: {annotation}\n"
        ) == [("Sample", "items", 5)], annotation


def test_the_walk_accepts_an_immutable_annotation() -> None:
    for annotation in ("Mapping[str, int] = field(default_factory=dict)",
                       "tuple[int, ...] = ()", "frozenset[int] = frozenset()"):
        assert mutable_container_fields(
            "from dataclasses import dataclass, field\n"
            "from typing import Mapping\n"
            "@dataclass(frozen=True)\n"
            "class Sample:\n"
            f"    items: {annotation}\n"
        ) == [], annotation


def test_the_walk_accepts_a_post_init_that_wraps() -> None:
    for wrapped in ("MappingProxyType(dict(self.items))", "tuple(self.items)",
                    "frozenset(self.items)", "built"):
        assert mutable_container_fields(
            "from dataclasses import dataclass, field\n"
            "from types import MappingProxyType\n"
            "@dataclass(frozen=True)\n"
            "class Sample:\n"
            "    items: dict[str, int] = field(default_factory=dict)\n"
            "    def __post_init__(self) -> None:\n"
            f"        object.__setattr__(self, 'items', {wrapped})\n"
        ) == [], wrapped


def test_the_walk_rejects_a_rebind_to_a_fresh_mutable_container() -> None:
    """A rebind that builds a new dict, list or set leaves the field just as open."""
    for rebind in ("{}", "[]", "set()", "dict(self.items)", "{name: 1 for name in ()}"):
        assert mutable_container_fields(
            "from dataclasses import dataclass, field\n"
            "@dataclass(frozen=True)\n"
            "class Sample:\n"
            "    items: dict[str, int] = field(default_factory=dict)\n"
            "    def __post_init__(self) -> None:\n"
            f"        object.__setattr__(self, 'items', {rebind})\n"
        ) == [("Sample", "items", 4)], rebind


def test_the_walk_ignores_a_dataclass_that_is_not_frozen() -> None:
    """An unfrozen dataclass is mutable by design, so it is out of this rule."""
    for declaration in ("@dataclass", "@dataclass(slots=True)", "@dataclass(frozen=False)"):
        assert mutable_container_fields(
            "from dataclasses import dataclass, field\n"
            f"{declaration}\n"
            "class Sample:\n"
            "    items: dict[str, int] = field(default_factory=dict)\n"
        ) == [], declaration
