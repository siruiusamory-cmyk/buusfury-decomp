"""Public semantic authoring API for placement-clone scenes.

Callers supply loaded SDK domain handles (`Maps`, and the placement-type and
descriptor views built from them) plus project paths, and name everything by
SEMANTIC identity: `map:NNNN`, `map:NNNN/placement:NNNN`, a
`<profile>/placement_type:NNNN` selector, a descriptor identity, a trigger name.
Callers never inspect handles, offsets, pointers, or project TOML, and this
module computes no ROM-format value of its own: it composes the existing public
SDK reads (`Maps`, `PlacementTypes`, `PlacementEvents`) and the existing
authoring writer (`project.placements.clone_placement`), and returns
already-serializable views.

This mirrors `dialogue.py`: semantic-identity-in, fail-closed, no Qt. The typed
error is a subclass of the project `ProjectError` family, so a GUI slot catches
one parent for both this façade's own validation and `clone_placement`'s.
"""

from __future__ import annotations

from pathlib import Path

from .data.behavior_triggers import BEHAVIOR_TRIGGER_CONTRACTS
from .entities import PlacementTypeError, PlacementTypes
from .maps import MapError, MapIdentity, Maps, PlacementIdentity, UnknownMapError
from .placement_events import PlacementEvents
from .project.model import ProjectError
from .project.placements import BehaviorTrigger, clone_placement


class SceneAuthoringError(ProjectError):
    """Expected scene-authoring failure suitable for a product error.

    Subclasses `ProjectError` so a caller catches that one family for both this
    façade's own validation and the `clone_placement` writer, which raises
    `ProjectValidationError`/`ProjectLoadError` from that same family.
    """


def _placement_from_identity(identity: str) -> PlacementIdentity:
    """Parse a `map:NNNN/placement:NNNN` slug, or fail closed."""
    try:
        map_part, placement_part = identity.split("/")
        map_index = int(map_part.split(":")[1])
        placement_index = int(placement_part.split(":")[1])
        if not map_part.startswith("map:") or not placement_part.startswith("placement:"):
            raise ValueError
        return PlacementIdentity(map_index, placement_index)
    except (AttributeError, ValueError, IndexError) as exc:
        raise SceneAuthoringError(
            f"{identity!r} is not a placement identity (map:NNNN/placement:NNNN)"
        ) from exc


def _map_from_identity(identity: str) -> MapIdentity:
    """Parse a `map:NNNN` slug, or fail closed."""
    try:
        if not isinstance(identity, str) or not identity.startswith("map:"):
            raise ValueError
        return MapIdentity(int(identity.split(":")[1]))
    except (ValueError, IndexError, MapError) as exc:
        raise SceneAuthoringError(f"{identity!r} is not a map identity (map:NNNN)") from exc


def _placement_types(maps: Maps) -> PlacementTypes | None:
    """The placement-type view for this ROM, or None when unsupported.

    Fail-closed: an unsupported ROM has no authorable clone sources rather than a
    crash, matching the read-only-when-unsupported rule.
    """
    try:
        return PlacementTypes(maps)
    except PlacementTypeError:
        return None


def list_authorable_maps(maps: Maps) -> list[dict]:
    """Every map that can be authored, as `{identity, label, placement_count}`.

    A map is authorable when it owns at least one existing placement, because a
    clone needs an existing record as its template source.
    """
    result = []
    for entry in maps.entries():
        placements = maps.map_placements(entry.identity)
        if not placements:
            continue
        result.append(
            {
                "identity": str(entry.identity),
                "label": str(entry.identity),
                "placement_count": len(placements),
            }
        )
    return result


def map_placements(maps: Maps, map_id: str) -> list[dict]:
    """Existing placements for one map, annotated with type and clone-source use.

    Each entry: `{identity, position_low, position_high, placement_type,
    classification, is_clone_source}`. `placement_type`/`classification` are None
    when this ROM has no verified type view.
    """
    identity = _map_from_identity(map_id)
    try:
        maps.entry(identity)
    except UnknownMapError as exc:
        raise SceneAuthoringError(str(exc)) from exc
    types = _placement_types(maps)
    result = []
    for placement in maps.map_placements(identity):
        type_id = None
        classification = None
        if types is not None:
            try:
                ptype = types.type_of(placement.identity)
                type_id = str(ptype.identity)
                classification = ptype.classification
            except PlacementTypeError:
                pass
        result.append(
            {
                "identity": str(placement.identity),
                "position_low": placement.record.position_low,
                "position_high": placement.record.position_high,
                "placement_type": type_id,
                "classification": classification,
                # Any existing placement is a valid clone source; a type is not
                # required to clone, only to attach an on_defeat trigger.
                "is_clone_source": True,
            }
        )
    return result


def clone_source_candidates(
    maps: Maps, map_id: str, require_type: str | None = None
) -> list[dict]:
    """Existing placements usable as clone sources, annotated with their type.

    When `require_type` names a `<profile>/placement_type:NNNN` selector, only
    placements resolving to that type are returned; a placement with no verified
    type is never returned in that filtered case (fail-closed).
    """
    identity = _map_from_identity(map_id)
    try:
        maps.entry(identity)
    except UnknownMapError as exc:
        raise SceneAuthoringError(str(exc)) from exc
    types = _placement_types(maps)
    result = []
    for placement in maps.map_placements(identity):
        type_id = None
        classification = None
        if types is not None:
            try:
                ptype = types.type_of(placement.identity)
                type_id = str(ptype.identity)
                classification = ptype.classification
            except PlacementTypeError:
                pass
        if require_type is not None and type_id != require_type:
            continue
        result.append(
            {
                "identity": str(placement.identity),
                "placement_type": type_id,
                "classification": classification,
            }
        )
    return result


def assignable_descriptors(maps: Maps) -> list[dict]:
    """Existing descriptor identities assignable as a placement behavior.

    Each entry: `{identity, event}`. Empty when the ROM declares no verified
    placement-descriptor contract (fail-closed rather than raising).
    """
    try:
        events = PlacementEvents(maps)
    except Exception:
        # No verified descriptor contract for this profile -> nothing assignable.
        return []
    return [
        {"identity": descriptor.identity, "event": descriptor.event}
        for descriptor in events.descriptors
    ]


def trigger_options(maps: Maps, source_identity: str) -> list[str]:
    """Semantic triggers valid for a given clone source.

    `on_defeat` is offered ONLY when the source resolves to the profile's
    qualifying placement type with the required classification, per the
    behavior-trigger evidence contract. A source with no such type offers none.
    """
    placement = _placement_from_identity(source_identity)
    contract = BEHAVIOR_TRIGGER_CONTRACTS.get(maps.profile.id)
    if contract is None:
        return []
    types = _placement_types(maps)
    if types is None:
        return []
    try:
        ptype = types.type_of(placement)
    except PlacementTypeError:
        return []
    options = []
    on_defeat = contract.get("on_defeat")
    if (
        on_defeat is not None
        and str(ptype.identity) == on_defeat["placement_type"]
        and ptype.classification == on_defeat["required_classification"]
    ):
        options.append(BehaviorTrigger.ON_DEFEAT.value)
    return options


def add_authored_npc(
    project_dir: str | Path,
    map_id: str,
    source_identity: str,
    name: str,
    position: tuple[int, int],
    *,
    behavior: str | None = None,
    script: tuple[str, ...] | None = None,
    trigger: str | None = None,
    maps: Maps | None = None,
) -> str:
    """Author one NPC by cloning an existing placement. Returns its identity.

    Semantic inputs only: `map_id` is `map:NNNN`, `source_identity` is
    `map:NNNN/placement:NNNN`, `position` is `(low, high)` unsigned 16-bit
    halfwords, `trigger` is a trigger name string. Calls the Python
    `clone_placement` directly (never the CLI, which omits `--script`). On any
    invalid input it raises `SceneAuthoringError` and writes nothing, because
    `clone_placement` validates before touching the project file.

    When `maps` is supplied, `trigger` is checked against `trigger_options` for
    the source first, so an unsupported trigger fails closed with a clear message
    before the writer is reached.
    """
    map_identity = _map_from_identity(map_id)
    source = _placement_from_identity(source_identity)
    try:
        low, high = position
    except (TypeError, ValueError) as exc:
        raise SceneAuthoringError("position must be a (low, high) pair") from exc

    if trigger is not None and maps is not None:
        allowed = trigger_options(maps, source_identity)
        if trigger not in allowed:
            raise SceneAuthoringError(
                f"trigger {trigger!r} is not valid for source {source_identity}; "
                f"valid triggers: {allowed or 'none'}"
            )

    try:
        clone = clone_placement(
            project_dir,
            map_index=map_identity.index,
            source=str(source),
            name=name,
            position_low=low,
            position_high=high,
            behavior=behavior,
            script=list(script) if script is not None else None,
            trigger=trigger,
        )
    except ProjectError as exc:
        # clone_placement raises ProjectValidationError/ProjectLoadError; re-raise
        # as the façade type so the GUI catches one parent, preserving the message.
        raise SceneAuthoringError(str(exc)) from exc
    return clone.identity
