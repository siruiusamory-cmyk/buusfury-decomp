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

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .data.behavior_triggers import BEHAVIOR_TRIGGER_CONTRACTS
from .data.script_effects import SCRIPT_EFFECTS
from .entities import PlacementTypeError, PlacementTypes
from .formats.script_vm import ScriptError
from .maps import MapError, MapIdentity, Maps, PlacementIdentity, UnknownMapError
from .placement_events import PlacementEvents
from .project.model import ProjectError, ProjectValidationError, read_project
from .project.placements import (
    BehaviorTrigger,
    PLACEMENT_POSITION_RANGE,
    clone_placement,
    remove_authored_placement,
)


class SceneAuthoringError(ProjectError):
    """Expected scene-authoring failure suitable for a product error.

    Subclasses `ProjectError` so a caller catches that one family for both this
    façade's own validation and the `clone_placement` writer, which raises
    `ProjectValidationError`/`ProjectLoadError` from that same family.
    """


class MapSupport(str, Enum):
    EDITABLE = "Editable"
    PARTIAL = "Partial"
    READ_ONLY = "Read-only"


@dataclass(frozen=True, slots=True)
class PendingChange:
    """One project mutation described in semantic, author-facing language."""

    identity: str
    object_identity: str
    summary: str
    details: tuple[str, ...] = ()
    revertible: bool = False


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


def list_maps(maps: Maps) -> list[dict]:
    """Every known map with an evidence-backed authoring support state."""
    types = _placement_types(maps)
    eligible: set[str] = set()
    contract = BEHAVIOR_TRIGGER_CONTRACTS.get(maps.profile.id, {}).get("on_defeat")
    effects = SCRIPT_EFFECTS.get(maps.profile.id, {})
    if types is not None and contract is not None and effects:
        for placement in maps.placements():
            try:
                ptype = types.type_of(placement.identity)
            except PlacementTypeError:
                continue
            if (
                str(ptype.identity) == contract["placement_type"]
                and ptype.classification == contract["required_classification"]
            ):
                eligible.add(str(placement.identity))

    result = []
    for entry in maps.entries():
        placements = maps.map_placements(entry.identity)
        if any(str(placement.identity) in eligible for placement in placements):
            support = MapSupport.EDITABLE
            reason = "Placement, entity, authored script, and proven interaction are supported."
        elif placements:
            support = MapSupport.PARTIAL
            reason = "Placements can be inspected and cloned; no proven visible interaction is available."
        else:
            support = MapSupport.READ_ONLY
            reason = "No supported placement source is available."
        result.append({
            "identity": str(entry.identity),
            "label": str(entry.identity),
            "placement_count": len(placements),
            "support": support.value,
            "support_reason": reason,
        })
    return result


def list_authorable_maps(maps: Maps) -> list[dict]:
    """Every map that can be authored, as `{identity, label, placement_count}`.

    A map is authorable when it owns at least one existing placement, because a
    clone needs an existing record as its template source.
    """
    return [item for item in list_maps(maps) if item["support"] != MapSupport.READ_ONLY.value]


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


def scene_placements(
    maps: Maps, map_id: str, project_dir: str | Path | None = None
) -> list[dict]:
    """Retail plus authored placements currently composing one project map."""
    result = [dict(item, provenance="Retail") for item in map_placements(maps, map_id)]
    if project_dir is None:
        return result
    project = read_project(project_dir)
    if project.meta.profile_id != maps.profile.id:
        raise ProjectValidationError(
            f"project profile {project.meta.profile_id!r} does not match open ROM profile "
            f"{maps.profile.id!r}"
        )
    map_identity = _map_from_identity(map_id)
    types = _placement_types(maps)
    for clone in project.maps.get(map_identity.index, {}).get("authored_placements", ()):
        type_identity = None
        classification = None
        if types is not None:
            try:
                ptype = types.type_of(_placement_from_identity(clone.clone_from))
                type_identity = str(ptype.identity)
                classification = ptype.classification
            except PlacementTypeError:
                pass
        result.append({
            "identity": clone.identity,
            "position_low": clone.position_low,
            "position_high": clone.position_high,
            "placement_type": type_identity,
            "classification": classification,
            "is_clone_source": False,
            "provenance": "Project",
        })
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
    except ScriptError:
        # No verified descriptor contract for this profile -> nothing assignable.
        return []
    return [
        {"identity": descriptor.identity, "event": descriptor.event}
        for descriptor in events.descriptors
    ]


def placement_relationships(
    maps: Maps, placement_identity: str, project_dir: str | Path | None = None
) -> dict:
    """Known semantic relationships and backlinks for one placement."""
    if "/authored:" in placement_identity:
        if project_dir is None:
            raise SceneAuthoringError(
                f"project path required for authored placement: {placement_identity}"
            )
        project = read_project(project_dir)
        if project.meta.profile_id != maps.profile.id:
            raise ProjectValidationError(
                f"project profile {project.meta.profile_id!r} does not match open ROM profile "
                f"{maps.profile.id!r}"
            )
        map_part = placement_identity.split("/", 1)[0]
        map_index = _map_from_identity(map_part).index
        clone = next((item for item in project.maps.get(map_index, {}).get(
            "authored_placements", ()) if item.identity == placement_identity), None)
        if clone is None:
            raise SceneAuthoringError(f"unknown authored placement: {placement_identity}")
        source = placement_relationships(maps, clone.clone_from)
        return {
            "placement": clone.identity,
            "clone_from": clone.clone_from,
            "entity": source["entity"],
            "entity_type": source["entity_type"],
            "classification": source["classification"],
            "behavior": clone.behavior or source["behavior"],
            "script": (f"{clone.identity}/behavior/script" if clone.script
                       else source["script"]),
            "dialogue": None,
            "used_by": (clone.identity,),
        }

    placement = _placement_from_identity(placement_identity)
    canonical = {str(item.identity) for item in maps.map_placements(MapIdentity(placement.map_index))}
    if placement_identity not in canonical:
        raise SceneAuthoringError(f"unknown placement: {placement_identity}")

    type_identity = None
    entity_identity = None
    classification = None
    types = _placement_types(maps)
    if types is not None:
        try:
            ptype = types.type_of(placement)
            type_identity = str(ptype.identity)
            entity_identity = str(ptype.enemy_identity) if ptype.enemy_identity else None
            classification = ptype.classification
        except PlacementTypeError:
            pass

    behavior_identity = None
    script_identity = None
    used_by: tuple[str, ...] = ()
    try:
        descriptor = PlacementEvents(maps).descriptor_of(placement)
    except ScriptError:
        descriptor = None
    if descriptor is not None:
        behavior_identity = descriptor.identity
        script_identity = descriptor.event
        used_by = tuple(sorted(descriptor.placements))

    return {
        "placement": placement_identity,
        "clone_from": None,
        "entity": entity_identity,
        "entity_type": type_identity,
        "classification": classification,
        "behavior": behavior_identity,
        "script": script_identity,
        # The verified map-scene event family deliberately exposes no dialogue
        # edge; placement_events.py documents that refutation.
        "dialogue": None,
        "used_by": used_by,
    }


def script_effect_options(maps: Maps) -> list[dict]:
    """Specialized authored-script choices from the profile's SDK contract."""
    result = []
    for identity, effect in sorted(SCRIPT_EFFECTS.get(maps.profile.id, {}).items()):
        result.append({
            "identity": identity,
            "label": identity.replace("_", " "),
            "text_count": effect["text_count"],
            "coordinate_ranges": dict(effect["coordinate_ranges"]),
        })
    return result


def placement_editor_constraints() -> dict:
    """Project-domain bounds needed by the specialized placement editor."""
    return {
        "position_low": PLACEMENT_POSITION_RANGE,
        "position_high": PLACEMENT_POSITION_RANGE,
    }


def visible_text_options(text_strings, effect_identity: str) -> list[dict]:
    """Text identities and previews accepted by one authored script effect."""
    effects = SCRIPT_EFFECTS.get(text_strings.profile.id, {})
    effect = effects.get(effect_identity)
    if effect is None:
        raise SceneAuthoringError(f"unsupported authored script effect: {effect_identity}")
    return [
        {"identity": str(entry.identity), "text": entry.text}
        for entry in text_strings.entries()
        if entry.identity.index < effect["text_count"]
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


def pending_changes(project_dir: str | Path, maps: Maps) -> list[PendingChange]:
    """Describe current project edits without exposing byte locations."""
    project = read_project(project_dir)
    if project.meta.profile_id != maps.profile.id:
        raise ProjectValidationError(
            f"project profile {project.meta.profile_id!r} does not match open ROM profile "
            f"{maps.profile.id!r}"
        )
    types = _placement_types(maps)
    result: list[PendingChange] = []
    canonical = {str(p.identity): p for p in maps.placements()}

    for map_index, values in sorted(project.maps.items()):
        for row in values.get("placements", ()):
            identity = f"map:{map_index:04d}/placement:{row['index']:04d}"
            original = canonical.get(identity)
            if original is None:
                continue
            before = (original.record.position_low, original.record.position_high)
            after = (row["position_low"], row["position_high"])
            if before != after:
                result.append(PendingChange(
                    f"placement-edit:{identity}", identity,
                    f"Position changed on {identity}: {before[0]}, {before[1]} -> {after[0]}, {after[1]}",
                ))

        for clone in values.get("authored_placements", ()):
            details = [
                f"Added placement to map:{map_index:04d}",
                f"Position set to {clone.position_low}, {clone.position_high}",
                f"Cloned from {clone.clone_from}",
            ]
            if types is not None:
                try:
                    ptype = types.type_of(_placement_from_identity(clone.clone_from))
                    if ptype.enemy_identity is not None:
                        details.append(f"Entity set to {ptype.enemy_identity}")
                    else:
                        details.append(f"Entity type set to {ptype.identity}")
                except PlacementTypeError:
                    pass
            if clone.behavior:
                details.append(f"Behavior assigned: {clone.behavior}")
            if clone.trigger:
                details.append(f"Interaction assigned: {clone.trigger.value}")
            if clone.script:
                details.append(f"Script assigned: {clone.identity}/behavior/script")
                effect_line = next((line for line in clone.script if line.split()[0] in
                                    SCRIPT_EFFECTS.get(maps.profile.id, {})), None)
                if effect_line:
                    details.append(f"Visible response assigned: {effect_line}")
            result.append(PendingChange(
                f"authored-placement:{clone.identity}", clone.identity,
                f"Added placement {clone.identity} to map:{map_index:04d}",
                tuple(details), True,
            ))

    for name in sorted(project.dialogues):
        from .compressed_dialogue import CompressedDialogueError, target_named

        try:
            target = target_named(name)
            revertible = target.profile_id in (None, maps.profile.id)
        except CompressedDialogueError:
            revertible = False
        result.append(PendingChange(
            f"dialogue:{name}", name, f"Dialogue changed: {name}", (), revertible
        ))
    return result


def revert_pending_change(
    project_dir: str | Path, maps: Maps, change_identity: str
) -> bool:
    """Revert one supported semantic project mutation."""
    if change_identity.startswith("authored-placement:"):
        return remove_authored_placement(
            project_dir, change_identity.removeprefix("authored-placement:")
        )
    if change_identity.startswith("dialogue:"):
        from .compressed_dialogue import CompressedDialogueError, target_named
        from .dialogue import remove_dialogue_replacement

        name = change_identity.removeprefix("dialogue:")
        try:
            target = target_named(name)
        except CompressedDialogueError as exc:
            raise SceneAuthoringError(f"unsupported dialogue change: {name}") from exc
        return remove_dialogue_replacement(project_dir, maps.profile, target)
    raise SceneAuthoringError(f"pending change cannot be reverted independently: {change_identity}")
