"""Explicit authored clones, separate from extracted canonical placement rows.

The map-scoped name is project identity, never a ROM offset or engine id_raw.
Only position overrides are supported. All structural words come from the
verified canonical template, including descriptor, children and unknown words.
"""
from dataclasses import dataclass
from pathlib import Path
import re

from .format import dump_toml


@dataclass(frozen=True, slots=True)
class AuthoredPlacement:
    identity: str
    map_index: int
    clone_from: str
    position_low: int
    position_high: int
    provenance: str = "AUTHORED_CLONE"

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
        if any(type(v) is not int or not 0 <= v <= 65535
               for v in (self.position_low, self.position_high)):
            raise ProjectValidationError("authored position halfwords must be unsigned 16-bit integers")

    def to_document(self):
        return {"provenance": self.provenance, "clone_from": self.clone_from,
                "position_low": self.position_low, "position_high": self.position_high}

    def serialize(self, template):
        """Use the production variable-length codec; no invented opaque bytes."""
        return template.with_position(self.position_low, self.position_high).to_bytes()


def parse_authored(table, map_index):
    from .model import ProjectLoadError
    if not isinstance(table, dict):
        raise ProjectLoadError("authored_placements must be a table")
    result = []
    fields = {"clone_from", "position_low", "position_high", "provenance"}
    for key, row in sorted(table.items()):
        if not isinstance(row, dict) or set(row) != fields:
            raise ProjectLoadError(f"{key}: authored clone requires exactly {sorted(fields)}; structural fabrication unsupported")
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


def clone_placement(project_dir, *, map_index, source, name, position_low, position_high):
    """Add a named clone to an existing map in a project. Opens no ROM.

    Clones copy canonical template structure, not current edits to that template.
    Full base reconciliation still occurs during validate/build.
    """
    from .model import read_project, _read_document, _MAP_FILE, ProjectValidationError
    project = read_project(project_dir)
    if map_index not in project.maps:
        raise ProjectValidationError(f"unknown owning map: {map_index}")
    clone = AuthoredPlacement(f"map:{map_index:04d}/authored:{name}", map_index,
                             source, position_low, position_high)
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
    path.write_text(dump_toml(doc), encoding="utf-8", newline="\n")
    return clone
