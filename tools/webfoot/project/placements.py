"""Explicit authored clones, separate from extracted canonical placement rows.

The map-scoped name is project identity, never a ROM offset or engine id_raw.
Position overrides, an explicit behavior attachment, and one evidence-scoped
behavior trigger are supported. Every other structural word comes from the
verified canonical template, including children and unknown words.

TOOLKIT-030: `behavior` names an EXISTING semantic descriptor identity, so the
authored record's `+0x14` is chosen by project state rather than inherited from
the clone source. It selects an already-verified `{handler, payload}` descriptor;
it does not author a descriptor, script or event body, and no author-facing ROM
address is accepted here.

TOOLKIT-032: `behavior` may instead name this record's OWN authored behavior -
    `map:NNNN/authored:<name>/behavior` - in which case `script` carries the body as
    a list of mnemonic instructions, plus the narrow evidence-backed semantic
    operations declared for that profile. TOOLKIT-033 adds exactly one:
    `show_centered_sprite_text text:NNNN X Y`. Both forms assemble through the
    production `script_vm` codec at build time. No ROM address, no opaque hex blob
    and no descriptor bytes are accepted from project source.
"""
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import re

from .atomic import replace_document
from .format import dump_toml


PLACEMENT_POSITION_RANGE = (0, 65535)


class BehaviorTrigger(str, Enum):
    """Author-facing behavior start conditions with runtime-proven semantics."""

    ON_DEFEAT = "on_defeat"


@dataclass(frozen=True, slots=True)
class AuthoredPlacement:
    identity: str
    map_index: int
    clone_from: str
    position_low: int
    position_high: int
    provenance: str = "AUTHORED_CLONE"
    #: An existing descriptor's semantic identity, or None to inherit the
    #: template's. Never a ROM address: resolution happens against the verified
    #: descriptor catalog at build time, so an unknown identity fails closed.
    behavior: str | None = None
    #: TOOLKIT-032. The authored script body, as production opcode mnemonics with
    #: integer operands. Present exactly when `behavior` names this record's own
    #: authored behavior; the bytes are produced by `script_vm.assemble_source`.
    script: tuple[str, ...] | None = None
    #: A deliberate gameplay condition that selects the declared behavior.
    #: Absence preserves the legacy, semantically UNKNOWN dispatch relationship.
    trigger: BehaviorTrigger | None = None

    @property
    def authored_behavior(self):
        """True when `behavior` names a body this project authors, not a ROM one."""
        return self.behavior == f"{self.identity}/behavior"

    def __post_init__(self):
        from .model import ProjectValidationError
        if type(self.map_index) is not int or self.map_index < 0:
            raise ProjectValidationError("authored owner must be a non-negative map index")
        prefix = f"map:{self.map_index:04d}/authored:"
        if (not isinstance(self.identity, str) or
                not self.identity.startswith(prefix) or
                re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", self.identity[len(prefix):]) is None):
            raise ProjectValidationError("authored identity must be map:NNNN/authored:<stable-name>")
        if (not isinstance(self.clone_from, str) or
                re.fullmatch(r"map:[0-9]{4,}/placement:[0-9]{4,}", self.clone_from) is None):
            raise ProjectValidationError("clone_from must name an extracted canonical placement")
        if self.provenance != "AUTHORED_CLONE":
            raise ProjectValidationError("unsupported authored placement provenance")
        if any(type(v) is not int or not PLACEMENT_POSITION_RANGE[0] <= v <= PLACEMENT_POSITION_RANGE[1]
               for v in (self.position_low, self.position_high)):
            raise ProjectValidationError("authored position halfwords must be unsigned 16-bit integers")
        if self.behavior is not None and not (
                isinstance(self.behavior, str) and (
                    re.fullmatch(r"map:[0-9]{4,}/placement:[0-9]{4,}/descriptor", self.behavior)
                    or self.authored_behavior)):
            raise ProjectValidationError(
                "behavior must name an existing placement descriptor identity, "
                "map:NNNN/placement:NNNN/descriptor, or this record's own authored "
                f"behavior, {self.identity}/behavior; raw ROM addresses are not an "
                "authoring API")
        # TOOLKIT-032. A script body and an authored behavior identity are one
        # declaration: neither means anything without the other, so each without the
        # other fails closed rather than being silently ignored.
        if self.script is not None and not self.authored_behavior:
            raise ProjectValidationError(
                f"{self.identity}: a script body requires behavior = "
                f"{self.identity}/behavior; a script cannot be attached to a "
                "descriptor this project does not author")
        if self.authored_behavior and self.script is None:
            raise ProjectValidationError(
                f"{self.identity}: an authored behavior requires a script body")
        if self.script is not None:
            if (not isinstance(self.script, (tuple, list)) or not self.script or
                    any(not isinstance(line, str) or not line.strip() for line in self.script)):
                raise ProjectValidationError(
                    "an authored script must be a non-empty list of instruction strings")
            object.__setattr__(self, "script", tuple(self.script))
        if self.trigger is not None:
            try:
                trigger = BehaviorTrigger(self.trigger)
            except (TypeError, ValueError):
                raise ProjectValidationError(
                    "trigger must be exactly 'on_defeat'; raw or unsupported trigger "
                    "values are not an authoring API") from None
            if self.behavior is None:
                raise ProjectValidationError(
                    f"{self.identity}: trigger {trigger.value} requires a behavior")
            object.__setattr__(self, "trigger", trigger)

    def to_document(self):
        document = {"provenance": self.provenance, "clone_from": self.clone_from,
                    "position_low": self.position_low, "position_high": self.position_high}
        if self.behavior is not None:
            document["behavior"] = self.behavior
        if self.script is not None:
            document["script"] = list(self.script)
        if self.trigger is not None:
            document["trigger"] = self.trigger.value
        return document

    def serialize(self, template, descriptor_pointer=None):
        """Use the production variable-length codec; no invented opaque bytes.

        `descriptor_pointer` is the resolved address of the declared behavior's
        descriptor. It is supplied by the build, which resolves the semantic
        identity against the verified catalog; this method never resolves an
        address itself and never accepts one from project source.
        """
        from dataclasses import replace
        from .model import ProjectValidationError
        record = template.with_position(self.position_low, self.position_high)
        if self.behavior is not None and not self.authored_behavior:
            if descriptor_pointer is None:
                raise ProjectValidationError(
                    f"{self.identity}: declared behavior {self.behavior} was not resolved")
            record = replace(record, descriptor_pointer_raw=descriptor_pointer)
        elif descriptor_pointer is not None:
            # TOOLKIT-032: an authored behavior has no address until the build
            # allocates its descriptor, so the record is serialized carrying the
            # template's pointer and the real one is written into it afterwards, by
            # the same production codec, once it exists.
            record = replace(record, descriptor_pointer_raw=descriptor_pointer)
        return record.to_bytes()


def parse_authored(table, map_index):
    from .model import ProjectLoadError
    if not isinstance(table, dict):
        raise ProjectLoadError("authored_placements must be a table")
    result = []
    fields = {"clone_from", "position_low", "position_high", "provenance"}
    for key, row in sorted(table.items()):
        # `behavior` is optional: absent means inherit the template's descriptor,
        # which is exactly the pre-TOOLKIT-030 behavior. `script` is optional and
        # meaningful only alongside an authored behavior, which AuthoredPlacement
        # enforces rather than trusting.
        if not isinstance(row, dict) or set(row) - {"behavior", "script", "trigger"} != fields:
            raise ProjectLoadError(f"{key}: authored clone requires exactly {sorted(fields)} plus optional 'behavior', 'script', and 'trigger'; structural fabrication unsupported")
        result.append(AuthoredPlacement(key, map_index, **row))
    return tuple(result)


def validate_templates(maps):
    from .model import ProjectValidationError
    extracted = {f"map:{index:04d}/placement:{p['index']:04d}"
                 for index, m in maps.items() for p in m.get("placements", ())}
    seen = set()
    for index, m in maps.items():
        for clone in m.get("authored_placements", ()):
            if not isinstance(clone, AuthoredPlacement) or clone.map_index != index:
                raise ProjectValidationError("authored placement owning map mismatch")
            if clone.identity in seen:
                raise ProjectValidationError(f"duplicate authored identity: {clone.identity}")
            seen.add(clone.identity)
            if clone.clone_from not in extracted:
                raise ProjectValidationError(f"{clone.identity}: missing extracted clone template {clone.clone_from}")


def clone_placement(project_dir, *, map_index, source, name, position_low, position_high,
                    behavior=None, script=None, trigger=None):
    """Add a named clone to an existing map in a project. Opens no ROM.

    Clones copy canonical template structure, not current edits to that template.
    Full base reconciliation still occurs during validate/build.
    """
    from .model import read_project, _read_document, _MAP_FILE, ProjectValidationError
    project = read_project(project_dir)
    if map_index not in project.maps:
        raise ProjectValidationError(f"unknown owning map: {map_index}")
    clone = AuthoredPlacement(f"map:{map_index:04d}/authored:{name}", map_index,
                             source, position_low, position_high, behavior=behavior,
                             script=script, trigger=trigger)
    values = project.maps[map_index]
    values["authored_placements"] = (*values.get("authored_placements", ()), clone)
    validate_templates(project.maps)
    path = Path(project_dir) / _MAP_FILE
    doc = _read_document(path)
    # Preserve the spelling of existing numeric map keys.
    key = next(k for k in doc["map"] if int(k.split(":")[1]) == map_index)
    authored = doc["map"][key].setdefault("authored_placements", {})
    authored[clone.identity] = clone.to_document()
    doc["map"][key]["authored_placements"] = dict(sorted(authored.items()))
    replace_document(path, dump_toml(doc))
    return clone


def remove_authored_placement(project_dir, identity):
    """Remove one authored placement by semantic identity.

    Returns whether project source changed. Extracted placements are never
    accepted, so this is a narrow project-level revert rather than binary undo.
    """
    from .model import read_project, _read_document, _MAP_FILE, ProjectValidationError

    if not isinstance(identity, str):
        raise ProjectValidationError("authored placement identity must be a string")
    map_part, separator, authored_part = identity.partition("/")
    if (
        separator != "/"
        or not map_part.startswith("map:")
        or not map_part[4:].isdigit()
        or not authored_part.startswith("authored:")
        or not authored_part[9:]
    ):
        raise ProjectValidationError(
            "revert requires an authored identity, map:NNNN/authored:<name>"
        )
    map_index = int(map_part[4:])
    project = read_project(project_dir)
    if map_index not in project.maps:
        raise ProjectValidationError(f"unknown owning map: {map_index}")
    if not any(
        placement.identity == identity
        for placement in project.maps[map_index].get("authored_placements", ())
    ):
        return False

    path = Path(project_dir) / _MAP_FILE
    doc = _read_document(path)
    key = next(k for k in doc["map"] if int(k.split(":")[1]) == map_index)
    authored = doc["map"][key].get("authored_placements")
    if not isinstance(authored, dict) or identity not in authored:
        raise ProjectValidationError(
            f"{identity}: loaded project and source document disagree"
        )
    del authored[identity]
    if authored:
        doc["map"][key]["authored_placements"] = dict(sorted(authored.items()))
    else:
        del doc["map"][key]["authored_placements"]
    replace_document(path, dump_toml(doc))
    return True


def set_project_placement_position(
    project_dir,
    *,
    map_index: int,
    placement_identity: str,
    position_low: int,
    position_high: int,
):
    """Set one extracted or authored placement position in project source.

    This is deliberately a project-source operation: it accepts a semantic
    placement identity and lossless halfwords, validates the loaded project,
    then updates only its declared position fields.  It never accepts a ROM
    address or writes a ROM.  ``True`` means the project document changed.
    """
    from .model import _MAP_FILE, ProjectValidationError, _read_document, read_project

    if type(map_index) is not int or map_index < 0:
        raise ProjectValidationError("map index must be a non-negative integer")
    if any(
        type(value) is not int
        or not PLACEMENT_POSITION_RANGE[0] <= value <= PLACEMENT_POSITION_RANGE[1]
        for value in (position_low, position_high)
    ):
        raise ProjectValidationError("position halfwords must be unsigned 16-bit integers")
    if not isinstance(placement_identity, str):
        raise ProjectValidationError("placement identity must be a string")

    project = read_project(project_dir)
    if map_index not in project.maps:
        raise ProjectValidationError(f"unknown owning map: {map_index}")
    values = project.maps[map_index]
    path = Path(project_dir) / _MAP_FILE
    document = _read_document(path)
    key = next(key for key in document["map"] if int(key.split(":")[1]) == map_index)
    entry = document["map"][key]

    if "/authored:" in placement_identity:
        clone = next(
            (
                item
                for item in values.get("authored_placements", ())
                if item.identity == placement_identity
            ),
            None,
        )
        if clone is None:
            raise ProjectValidationError(
                f"unknown authored placement: {placement_identity}"
            )
        authored = entry.get("authored_placements")
        if not isinstance(authored, dict) or placement_identity not in authored:
            raise ProjectValidationError(
                f"{placement_identity}: loaded project and source document disagree"
            )
        current = (clone.position_low, clone.position_high)
        if current == (position_low, position_high):
            return False
        authored[placement_identity]["position_low"] = position_low
        authored[placement_identity]["position_high"] = position_high
        entry["authored_placements"] = dict(sorted(authored.items()))
    else:
        marker = "/placement:"
        map_part, separator, placement_part = placement_identity.partition(marker)
        if (
            separator != marker
            or map_part != f"map:{map_index:04d}"
            or not placement_part.isdigit()
        ):
            raise ProjectValidationError(
                "canonical placement identity must be map:NNNN/placement:NNNN"
            )
        placement_index = int(placement_part, 10)
        row = next(
            (
                item
                for item in values.get("placements", ())
                if item["index"] == placement_index
            ),
            None,
        )
        if row is None:
            raise ProjectValidationError(f"unknown placement: {placement_identity}")
        placements = entry.get("placements")
        placement_key = f"placement:{placement_index:04d}"
        if not isinstance(placements, dict) or placement_key not in placements:
            raise ProjectValidationError(
                f"{placement_identity}: loaded project and source document disagree"
            )
        current = (row["position_low"], row["position_high"])
        if current == (position_low, position_high):
            return False
        placements[placement_key]["position_low"] = position_low
        placements[placement_key]["position_high"] = position_high

    replace_document(path, dump_toml(document))
    return True
