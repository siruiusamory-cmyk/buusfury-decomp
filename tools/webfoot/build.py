"""Nothing on this path consults the clock, the filesystem order, the machine name or a random source, because the same project must produce the same bytes."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from . import capability
from .allocation import AllocationError
from .appearance_authoring import (
    AppearanceAuthoringError,
    materialize_authored_appearances,
)
from .map_authoring import (
    AuthoredMap as AuthoredMapRequest,
    MapAuthoringError,
    authored_map_facts,
    materialize_authored_maps,
    validate_authored_maps,
)
from .profile import RomProfile, RomProfileCatalog, VerificationStatus
from .project import (
    PROJECT_FORMAT_VERSION,
    ProjectMeta,
    ProjectValidationError,
    StatProject,
    raw_byte_changes,
    raw_byte_no_op_problems,
    read_project,
    read_raw_bytes,
    write_project,
)
from .project.atomic import replace_document
from .rom import RomIdentification, identify_rom
from .stats import (
    CHARACTER_FIELDS,
    ENEMY_FIELDS,
    StatProfileError,
    StatTables,
    load_stat_tables,
)
from .text import (
    TextProfileError,
    TextStrings,
    TextTooLongError,
    load_text_strings,
)
from .maps import (
    MAP_FIELDS,
    MapIdentity,
    Maps,
    PlacementIdentity,
    load_maps,
)
from .formats.map_entry import MapEntryProfileError
from .formats.sprite_graphics import SpriteFormatError
from .map_paint import MapPaintError, plan_layout_cells
from .map_chunk import ChunkAuthoringError, materialize_authored_chunks
from .formats.map_transitions import MapTransitionError, TransitionArrival
from .map_transitions import (
    AuthoredTransitionCreation,
    AuthoredTransitionEdit,
    CreatedTransitionIdentity,
    MapTransitionsError,
    TransitionIdentity,
    materialize_transition_creations,
    plan_transition_edits,
    transition_creations_to_requests,
    transition_edits_to_requests,
)
from .map_resize import (
    MapStructureError,
    materialize_map_structure,
    structural_placements,
)
from .packaged import packaged_profile
from .sprite_attachment import SpriteAttachmentError
from .sprite_authoring import (
    SpriteAuthoringError,
    materialize_authored_sprites,
)
from .sprite_identity import SpriteIdentityError
from .write import (
    ByteChange,
    ProjectProvenance,
    WriteManifest,
    emit_image,
    plan_changes,
)


class BuildError(ValueError):
    """Base error for the extract/validate/build lifecycle."""


class ProjectRomMismatchError(BuildError):
    """Raised when a project is built against a ROM it was not authored for.

    This is the fail-closed rule the project format exists to enforce. A
    project pins one base image by SHA-256; applying it to a different image
    would produce a ROM whose provenance is a lie, because the manifest would
    claim edits that landed at offsets meaning something else entirely.
    """


@dataclass(frozen=True, slots=True)
class ValidationReport:

    project_name: str
    profile_id: str
    base_sha256: str
    enemy_count: int
    character_count: int
    problems: tuple[str, ...]
    string_count: int = 0
    map_count: int = 0

    @property
    def passed(self) -> bool:
        return not self.problems


@dataclass(frozen=True, slots=True)
class BuildResult:

    manifest: WriteManifest
    output_path: Path
    manifest_path: Path | None
    project_name: str


class _ManifestBesideOutput:

    __slots__ = ()

    def __repr__(self) -> str:  # pragma: no cover - diagnostics only
        return "MANIFEST_BESIDE_OUTPUT"


# Pass None for no manifest at all and a path to redirect it, because the default publishes the provenance manifest beside the emitted image.
MANIFEST_BESIDE_OUTPUT = _ManifestBesideOutput()


def manifest_path_for_build(manifest_path, output_path: str | Path) -> Path | None:
    from .authored_image import manifest_path_for

    if manifest_path is MANIFEST_BESIDE_OUTPUT:
        return manifest_path_for(output_path)
    return None if manifest_path is None else Path(manifest_path)




_EXTRACTABLE = (
    capability.Capability.ENEMY_STATS,
    capability.Capability.CHARACTER_BASE_STATS,
    capability.Capability.TEXT_STRINGS,
    capability.Capability.MAP_ENTRIES,
)


def _require_extractable_profile(identification: RomIdentification) -> RomProfile:
    match = identification.profile_match
    if match.status is not VerificationStatus.VERIFIED or match.profile is None:
        raise BuildError("extraction requires an exactly verified ROM")
    profile = match.profile
    declared = [item for item in _EXTRACTABLE if capability.declared(profile, item)]
    if not declared:
        raise BuildError(
            f"profile {profile.id!r} declares no extractable content; this "
            "toolkit can read none of its stats, characters or text"
        )
    return profile


def extract_project(
    rom_path: str | Path,
    project_dir: str | Path,
    catalog: RomProfileCatalog,
    *,
    name: str | None = None,
    graphics: bool = True,
) -> list[Path]:
    """Read a verified ROM and write a deterministic project. Never writes the ROM, and graphics=False skips 7,390 sprite payloads at the cost of authoring reach only, because a build from such a project still re-emits unchanged graphics from the base."""
    target = Path(project_dir)
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        raise BuildError(
            f"{target} is not empty; extract writes a new project into a clean "
            "directory so it never overwrites authored files. Remove it or "
            "choose an empty destination."
        )

    identification = identify_rom(rom_path, catalog)
    profile = _require_extractable_profile(identification)

    meta = ProjectMeta(
        format_version=PROJECT_FORMAT_VERSION,
        profile_id=profile.id,
        game=profile.game,
        base_rom_sha256=identification.hashes.sha256,
        base_rom_size=identification.size,
        name=name if name is not None else profile.id,
    )

    try:
        tables = load_stat_tables(rom_path, catalog)
    except StatProfileError:
        enemies: list = []
        characters: list = []
    else:
        enemies = [
            (entry.identity, entry.record, entry.original_bytes, None)
            for entry in tables.enemies()
        ]
        characters = [
            (entry.identity, entry.record, entry.original_bytes, entry.alias)
            for entry in tables.characters()
        ]

    # Text is extracted when the verified profile declares a string table, and
    # omitted otherwise. `TextProfileError` here means "this ROM has no text
    # this toolkit can read", which is a fact about the profile rather than a
    # failure of the extraction - so the rest of the project is still written.
    try:
        strings = [
            (entry.identity, entry.text)
            for entry in load_text_strings(rom_path, catalog).entries()
        ]
    except TextProfileError:
        strings = []

    # Maps are extracted when the verified profile declares the map table, and
    # omitted otherwise - Legacy of Goku II's records are a variant layout and
    # its profile deliberately does not declare `map_entries` against this
    # codec, so `MapEntryProfileError` here means "this ROM has no maps this
    # toolkit can read" rather than a failure.
    try:
        loaded_maps = load_maps(rom_path, catalog)
        maps = _map_documents(loaded_maps)
    except MapEntryProfileError:
        maps = []

    written = write_project(
        project_dir,
        meta,
        enemies=enemies,
        characters=characters,
        strings=strings,
        maps=maps,
    )
    if capability.declared(profile, capability.Capability.PLACEMENT_TYPES):
        from .entities import load_placement_types
        from .project.model import PLACEMENT_TYPES_FILE
        from .project.format import dump_toml
        document = load_placement_types(rom_path, catalog).project_document()
        target = Path(project_dir) / PLACEMENT_TYPES_FILE
        replace_document(target, dump_toml(document))
        written.append(target)
    from .data.placement_contracts import CONTRACTS
    if profile.id in CONTRACTS:
        from .placement_events import PlacementEvents
        import json
        events = PlacementEvents(loaded_maps)
        document = events.project_document()
        document['reference_graph'] = load_placement_types(rom_path, catalog).reference_document().to_compact_json()
        target = Path(project_dir) / 'events/placement_descriptors.json'
        replace_document(target, json.dumps(document, sort_keys=True, separators=(',', ':')) + '\n')
        written.append(target)
    if graphics and capability.declared(profile, capability.Capability.ACTOR_SPRITES):
        written.extend(
            _extract_graphics(rom_path, project_dir, identification)
        )
    return written


def _extract_graphics(
    rom_path: str | Path,
    project_dir: str | Path,
    identification: RomIdentification,
) -> list[Path]:
    from .formats import indexed_png, sprite_graphics
    from .graphics import load_actor_sprites
    from .project.format import dump_toml
    from .project.model import GRAPHICS_ASSET_DIR, GRAPHICS_FILE

    image = Path(rom_path).read_bytes()
    sprites = load_actor_sprites(image, identification)
    root = Path(project_dir)
    asset_root = root / GRAPHICS_ASSET_DIR
    asset_root.mkdir(parents=True, exist_ok=True)

    palette = sprites.palette.rgb
    written: list[Path] = []
    assets: dict[str, dict] = {}
    for graphic in sprites.graphics():
        filename = f"graphic_{graphic.identity.index:04d}.png"
        target = asset_root / filename
        encoded = indexed_png.encode(
            graphic.pixels,
            graphic.width,
            graphic.height,
            palette,
            transparent_index=sprite_graphics.TRANSPARENT_INDEX,
        )
        target.write_bytes(encoded)
        written.append(target)
        assets[str(graphic.identity)] = {
            "file": (GRAPHICS_ASSET_DIR / filename).as_posix(),
            "width": graphic.width,
            "height": graphic.height,
            "bit_depth": 8 if graphic.colour_256 else 4,
            # The extent an edit is bounded by. Recorded because it is a fact
            # about the base image that the PNG cannot carry.
            "packed_size": graphic.packed_size,
            "shared": graphic.shared,
            "consumer_count": len(graphic.consumers),
            "characters": [str(c) for c in graphic.characters],
            "png_sha256": sha256(encoded).hexdigest(),
            "pixels_sha256": sha256(graphic.pixels).hexdigest(),
        }

    characters = {
        str(character.identity): {
            "animation_count": len(character.animation_offsets),
            "graphics": [str(g) for g in character.graphics],
        }
        for character in sprites.characters()
    }

    manifest = {
        "graphics": {
            "profile_id": sprites.profile.id,
            "transparent_index": sprite_graphics.TRANSPARENT_INDEX,
            # The palette travels as raw GBA words. An RGB triple cannot round
            # trip to a unique 15-bit word, so storing display colour here would
            # make the project lossy against its own source.
            "palette_raw": list(sprites.palette.raw),
        },
        "asset": assets,
        "character": characters,
    }
    manifest_path = root / GRAPHICS_FILE
    replace_document(manifest_path, dump_toml(manifest))
    written.append(manifest_path)
    return written


def _map_documents(maps: Maps) -> list[dict]:
    documents: list[dict] = []
    from .data.placement_contracts import CONTRACTS
    from .placement_events import PlacementEvents
    relationships = PlacementEvents(maps) if maps.profile.id in CONTRACTS else None
    for entry in maps.entries():
        array = maps.slot_array(entry.identity)
        document: dict = {
            "index": entry.identity.index,
            "key": entry.identity.key,
            "raw": entry.original_bytes,
            "slots": None if array is None else array.array.original_bytes,
            "shape": None if array is None else array.shape.value,
        }
        for name in MAP_FIELDS:
            document[name] = maps.field(entry.identity, name)
        placements = maps.map_placements(entry.identity)
        if placements:
            # The halfwords are named by position in the word and never by axis, because this project has not established which one is X.
            document["placements"] = [
                {
                    "index": item.identity.placement_index,
                    "position_low": item.record.position_low,
                    "position_high": item.record.position_high,
                    "raw": item.original_bytes,
                    **({'descriptor': relationships.descriptor_of(item.identity).identity,
                        'child_count': item.record.child_count,
                        'child_pointers_raw': list(item.record.child_pointers_raw),
                        'record_size': item.record.consumed_length} if relationships else {}),
                }
                for item in placements
            ]
        documents.append(document)
    return documents




def _check_identity(
    project: StatProject,
    identification: RomIdentification,
    profile: RomProfile,
) -> list[str]:
    problems: list[str] = []
    actual_sha256 = identification.hashes.sha256

    if project.meta.base_rom_sha256 != actual_sha256:
        problems.append(
            f"base ROM mismatch: project requires sha256 "
            f"{project.meta.base_rom_sha256}, supplied ROM is {actual_sha256}"
        )
    if project.meta.base_rom_size != identification.size:
        problems.append(
            f"base ROM size mismatch: project requires "
            f"{project.meta.base_rom_size} bytes, supplied ROM is "
            f"{identification.size}"
        )
    if project.meta.profile_id != profile.id:
        problems.append(
            f"profile mismatch: project targets {project.meta.profile_id!r}, "
            f"supplied ROM verified as {profile.id!r}"
        )
    return problems


def _check_records(project: StatProject, tables: StatTables | None) -> list[str]:
    problems: list[str] = []
    if tables is None:
        if project.enemies or project.characters:
            return [
                "project authors stat records, but this ROM's profile declares "
                "no stat tables; a build would silently drop every authored record"
            ]
        return problems

    for label, authored, live, allowed in (
        ("enemy", project.enemies, {e.identity: e for e in tables.enemies()}, ENEMY_FIELDS),
        (
            "character",
            project.characters,
            {c.identity: c for c in tables.characters()},
            CHARACTER_FIELDS,
        ),
    ):
        for identity in sorted(set(authored) - set(live), key=lambda i: i.key):
            problems.append(
                f"{identity}: project declares a {label} record that this ROM "
                "does not contain"
            )
        for identity in sorted(set(live) - set(authored), key=lambda i: i.key):
            problems.append(
                f"{identity}: project is missing this {label} record; a build "
                "would silently leave it at its base value"
            )

        for identity in sorted(set(authored) & set(live), key=lambda i: i.key):
            values = authored[identity]
            entry = live[identity]

            if values["raw"] != entry.original_bytes:
                problems.append(
                    f"{identity}: authored raw bytes do not match this ROM; the "
                    "record's undecoded data was extracted from a different image"
                )

            for field, (minimum, maximum) in allowed.items():
                value = values[field]
                if value < minimum:
                    problems.append(
                        f"{identity}.{field}={value} is below the minimum {minimum}"
                    )
                elif maximum is not None and value > maximum:
                    problems.append(
                        f"{identity}.{field}={value} exceeds the maximum {maximum}"
                    )

    return problems


def _check_strings(project: StatProject, strings: TextStrings | None) -> list[str]:
    problems: list[str] = []
    if not project.strings:
        return problems
    if strings is None:
        return [
            "project authors text, but this ROM's profile declares no string "
            "table; a build would silently drop every authored string"
        ]

    live = {entry.identity: entry for entry in strings.entries()}

    for identity in sorted(set(project.strings) - set(live), key=_identity_order):
        problems.append(
            f"{identity}: project declares a string that this ROM does not contain"
        )
    for identity in sorted(set(live) - set(project.strings), key=_identity_order):
        problems.append(
            f"{identity}: project is missing this string; a build would silently "
            "leave it at its base value"
        )

    for identity in sorted(set(project.strings) & set(live), key=_identity_order):
        try:
            strings.set_text(identity, project.strings[identity])
        except (TextTooLongError, ValueError) as exc:
            problems.append(str(exc))

    return problems


def _check_layout(
    project: StatProject, profile: RomProfile, canonical_image: bytes | None
) -> list[str]:
    edits = project.layout.cells()
    chunks = project.chunks
    structure = project.structure
    structural_slots = structure.structural_slots()
    if structural_slots:
        edits = {
            key: value
            for key, value in edits.items()
            if (key[0], key[1]) not in structural_slots
        }
    if not edits and (chunks is None or chunks.is_empty()) and structure.is_empty():
        return []
    canonical = packaged_profile()
    if canonical.identity.sha256 != profile.identity.sha256:
        return [
            "project paints a map layout, but this ROM's profile is not the "
            "canonical layout domain; a build would silently drop every painted cell"
        ]
    ordinal_edits = {
        key: value for key, value in edits.items() if type(value) is int
    }
    authored_edits = {
        key: value for key, value in edits.items() if type(value) is str
    }
    problems: list[str] = []
    if ordinal_edits:
        try:
            plan_layout_cells(canonical_image, ordinal_edits, profile=canonical)
        except MapPaintError as exc:
            problems.append(f"authored map layout: {exc}")
    structural_refs: tuple = ()
    if not structure.is_empty():
        # MAP-RESIZE-AND-LAYERS-001. A resize and an authored layer are checked by
        # the same authority a build uses, so an unsupported slot, an impossible
        # dimension, an unresolved authored layer or an out-of-vocabulary
        # initialization is a named problem before anything is planned.
        try:
            materialize_map_structure(
                canonical_image, structure, project.layout, profile=canonical
            )
        except MapStructureError as exc:
            problems.append(f"authored map structure: {exc}")
        try:
            structural_refs = structural_placements(
                canonical_image, structure, project.layout, profile=canonical
            )
        except MapStructureError as exc:
            problems.append(f"authored map structure: {exc}")
    if authored_edits or (chunks is not None and not chunks.is_empty()) or structural_refs:
        from .map_chunk import materialize_authored_chunks

        try:
            materialize_authored_chunks(
                canonical_image,
                chunks.chunks if chunks is not None else {},
                authored_edits,
                profile=canonical,
                structural=structural_refs,
            )
        except ChunkAuthoringError as exc:
            problems.append(f"authored map chunk: {exc}")
    return problems


def _check_graphics(project, profile, project_dir, image, identification) -> list[str]:
    from .graphics_authoring import (CanonicalGraphics, GraphicsAuthoringError,
                                     read_graphics_manifest, resolve_pixel_overrides)

    try:
        manifest = read_graphics_manifest(project_dir)
    except GraphicsAuthoringError as exc:
        return [f"authored graphic pixels: {exc}"]
    if manifest is None:
        return []
    if manifest.profile_id != profile.id:
        return [
            "authored graphic pixels: the extracted graphics manifest was written "
            f"for {manifest.profile_id!r}, but this ROM is {profile.id!r}; every "
            "authored PNG would be resolved against the wrong assets"
        ]
    if not capability.declared(profile, capability.Capability.ACTOR_SPRITES):
        return [
            "authored graphic pixels: the project has an extracted graphics manifest "
            "but this ROM's profile declares no actor_sprites; a build would silently "
            "drop every authored pixel"
        ]
    if image is None:
        return []
    try:
        resolve_pixel_overrides(
            project_dir, manifest, CanonicalGraphics(image, identification).pixels_of
        )
    except GraphicsAuthoringError as exc:
        return [f"authored graphic pixels: {exc}"]
    return []


_TRANSITION_ERRORS = (MapTransitionsError, MapTransitionError)

_SPRITE_ERRORS = (SpriteAuthoringError, SpriteIdentityError, SpriteAttachmentError,
                  SpriteFormatError, AllocationError)

_APPEARANCE_ERRORS = (AppearanceAuthoringError, AllocationError)

_MAP_AUTHORING_ERRORS = (MapAuthoringError, AllocationError)


def _map_authoring_requests(project: StatProject) -> tuple[AuthoredMapRequest, ...]:
    return tuple(
        AuthoredMapRequest(name=item.name, donor=item.donor, key=item.key)
        for item in project.authored_maps.ordered()
    )


def _check_authored_maps(
    project: StatProject, profile: RomProfile, canonical_image, identification,
) -> list[str]:
    if project.authored_maps.is_empty():
        return []
    if not capability.declared(profile, capability.Capability.MAP_ENTRIES):
        return [
            "project authors a new map, but this ROM's profile declares no map_entry "
            "table; a build would silently drop it"
        ]
    if canonical_image is None:
        return []
    try:
        validate_authored_maps(
            canonical_image, identification, profile, project.authored_maps)
    except _MAP_AUTHORING_ERRORS as exc:
        return [f"authored map: {exc}"]
    return []


def _authored_sprite_id(project: StatProject) -> int | None:
    if project.sprites.is_empty():
        return None
    return project.sprites.only().sprite_id


def _sprite_maps(project: StatProject) -> frozenset[MapIdentity]:
    return frozenset(MapIdentity(index) for index in project.sprites.actor_maps())


def _sprite_map_clashes(project: StatProject, maps) -> list[str]:
    problems: list[str] = []
    for index in project.sprites.actor_maps():
        values = project.maps.get(index)
        if not values:
            continue
        if values.get("authored_placements"):
            problems.append(
                f"map {index} receives an authored placement expansion and a new "
                "actor; both re-emit the map's object array, so a build cannot "
                "apply both"
            )
        if maps is None:
            continue
        identity = MapIdentity(index)
        differing = sorted(name for name in MAP_FIELDS
                           if maps.field(identity, name) != values[name])
        if differing:
            problems.append(
                f"map {index}'s {', '.join(differing)} is edited and a new actor is "
                "appended to it; the actor's plan emits that map's record itself, "
                "so the field edit would be dropped"
            )
    return problems


def _check_sprites(
    project: StatProject, profile: RomProfile, project_dir, canonical_image,
    identification, maps,
) -> list[str]:
    if project.sprites.is_empty():
        return []
    problems = _sprite_map_clashes(project, maps)
    for name, declared in (("actor sprites", capability.Capability.ACTOR_SPRITES),
                           ("map entries", capability.Capability.MAP_ENTRIES)):
        if not capability.declared(profile, declared):
            return problems + [
                "project authors a new actor sprite, but this ROM's profile "
                f"declares no {name}; a build would silently drop it"
            ]
    if canonical_image is None:
        return problems
    try:
        materialize_authored_sprites(canonical_image, identification, profile,
                                     project.sprites, project_dir)
    except _SPRITE_ERRORS as exc:
        return problems + [f"authored actor sprite: {exc}"]
    return problems


def _check_appearances(
    project: StatProject, profile: RomProfile, canonical_image, identification,
) -> list[str]:
    if project.appearances.is_empty():
        return []
    for name, required in (("an appearance table", capability.Capability.APPEARANCES),
                           ("a text table", capability.Capability.TEXT_STRINGS),
                           ("actor sprites", capability.Capability.ACTOR_SPRITES)):
        if not capability.declared(profile, required):
            return [
                "project authors a new appearance definition, but this ROM's "
                f"profile declares no {name}; a build would silently drop it"
            ]
    if canonical_image is None:
        return []
    try:
        materialize_authored_appearances(
            canonical_image, identification, profile, project.appearances,
            authored_sprite_id=_authored_sprite_id(project),
        )
    except _APPEARANCE_ERRORS as exc:
        return [f"authored appearance definition: {exc}"]
    return []


def _transition_requests(project: StatProject) -> dict[TransitionIdentity, AuthoredTransitionEdit]:
    return transition_edits_to_requests(project.transitions)


def _authored_facts(
    project: StatProject, canonical: RomProfile, canonical_image: bytes | None
):
    if canonical_image is None:
        return None
    return authored_map_facts(canonical_image, canonical, project.authored_maps)


def _check_transitions(
    project: StatProject, profile: RomProfile, canonical_image: bytes | None
) -> list[str]:
    requests = _transition_requests(project)
    if not requests:
        return []
    canonical = packaged_profile()
    if canonical.identity.sha256 != profile.identity.sha256:
        return [
            "project authors map transitions, but this ROM's profile is not the "
            "canonical transition domain; a build would silently drop every "
            "authored transition"
        ]
    try:
        plan_transition_edits(
            canonical_image, requests, profile=canonical,
            authored=_authored_facts(project, canonical, canonical_image),
        )
    except _TRANSITION_ERRORS as exc:
        return [f"authored map transition: {exc}"]
    return []


def _creation_requests(
    project: StatProject,
) -> dict[CreatedTransitionIdentity, AuthoredTransitionCreation]:
    return transition_creations_to_requests(project.transition_creations)


def _check_transition_creations(
    project: StatProject, profile: RomProfile, canonical_image: bytes | None
) -> list[str]:
    requests = _creation_requests(project)
    if not requests:
        return []
    canonical = packaged_profile()
    if canonical.identity.sha256 != profile.identity.sha256:
        return [
            "project creates map transitions, but this ROM's profile is not the "
            "canonical transition domain; a build would silently drop every created "
            "transition"
        ]
    try:
        materialize_transition_creations(
            canonical_image, requests, profile=canonical,
            authored=_authored_facts(project, canonical, canonical_image),
        )
    except _TRANSITION_ERRORS as exc:
        return [f"created map transition: {exc}"]
    return []


def _check_maps(project: StatProject, maps: Maps | None) -> list[str]:
    from .authored_placements import check_authored_placement_policy
    problems, authored_policy = check_authored_placement_policy(project, maps)
    maps = authored_policy.map_view
    if not project.maps:
        return problems
    if maps is None:
        return [
            "project authors maps, but this ROM's profile declares no map "
            "table; a build would silently drop every authored map"
        ]

    live = {entry.identity.index: entry for entry in maps.entries()}

    for index in sorted(set(project.maps) - set(live)):
        problems.append(
            f"map:{index:04d}: project declares a map that this ROM does not contain"
        )
    for index in sorted(set(live) - set(project.maps)):
        problems.append(
            f"map:{index:04d}: project is missing this map; a build would "
            "silently leave it at its base value"
        )

    for index in sorted(set(project.maps) & set(live)):
        identity = MapIdentity(index)
        values = project.maps[index]
        entry = live[index]

        if values["raw"] != entry.original_bytes:
            problems.append(
                f"{identity}: authored raw bytes do not match this ROM; the "
                "record was extracted from a different image"
            )

        array = maps.slot_array(identity)
        authored_slots = values.get("slots")
        if array is None and authored_slots is not None:
            problems.append(
                f"{identity}: project authors a slot extent, but this ROM's "
                "record declares none"
            )
        elif array is not None and authored_slots is None:
            problems.append(
                f"{identity}: project is missing this map's slot extent; a "
                "build would silently leave it at its base value"
            )
        elif array is not None and authored_slots != array.array.original_bytes:
            problems.append(
                f"{identity}: authored slot bytes do not match this ROM; the "
                "extent was extracted from a different image"
            )

        elif array is not None and values.get("shape") != array.shape.value:
            problems.append(
                f"{identity}: authored slot shape {values.get('shape')!r} does "
                f"not match this ROM's {array.shape.value!r}"
            )

        owned = maps.map_placements(identity)
        authored_placements = values.get("placements", [])
        expected_indices = [p.identity.placement_index for p in owned]
        actual_indices = [p["index"] for p in authored_placements]
        if len(owned) != len(authored_placements):
            problems.append(
                f"{identity}: project authors {len(authored_placements)} "
                f"placement(s) but this ROM's map owns {len(owned)}"
            )
        elif actual_indices != expected_indices:
            problems.append(f"{identity}: extracted placement identities/order differ from canonical run")
        else:
            by_index = {item.identity.placement_index: item for item in owned}
            for item in authored_placements:
                placement_index = item["index"]
                live_placement = by_index.get(placement_index)
                if live_placement is None:
                    problems.append(
                        f"{identity}/placement:{placement_index:04d}: project "
                        "declares a placement that this ROM's map does not own"
                    )
                    continue
                if item["raw"] != live_placement.original_bytes:
                    problems.append(
                        f"{live_placement.identity}: authored raw bytes do not "
                        "match this ROM; the record was extracted from a "
                        "different image"
                    )
                problems += authored_policy.placement_problems(item, live_placement)
                for half in ("position_low", "position_high"):
                    if not 0 <= item[half] <= 0xFFFF:
                        problems.append(
                            f"{live_placement.identity}: {half}={item[half]} "
                            "is outside the 0..65535 range this field holds"
                        )

        for name, (minimum, maximum) in MAP_FIELDS.items():
            value = values[name]
            if value < minimum:
                problems.append(
                    f"{identity}.{name}={value} is below the minimum {minimum}"
                )
            elif value > maximum:
                problems.append(
                    f"{identity}.{name}={value} exceeds the maximum {maximum}"
                )

    if not problems:
        problems += authored_policy.final_problems()
    return problems


def _check_dialogues(project: StatProject, profile: RomProfile,
                     rom_path: str | Path) -> list[str]:
    if not project.dialogues:
        return []
    from .compressed_dialogue import CompressedDialogueError, target_named
    from .dialogue import validate_dialogue_replacement
    canonical = Path(rom_path).read_bytes()
    problems = []
    for name, text in sorted(project.dialogues.items()):
        try:
            target = target_named(name)
            validation = validate_dialogue_replacement(target, text, profile, canonical)
            if not validation.valid:
                raise CompressedDialogueError(
                    "; ".join(problem.message for problem in validation.problems)
                )
        except CompressedDialogueError as exc:
            problems.append(f"dialogue:{name}: {exc}")
    return problems


def _check_raw_bytes(
    project_dir: str | Path, image: bytes | None
) -> list[str]:
    if image is None:
        read_raw_bytes(project_dir)
        return []
    edits = read_raw_bytes(project_dir)
    raw_byte_changes(edits, image)
    return raw_byte_no_op_problems(edits, image)


def _identity_order(identity: object) -> int:
    return getattr(identity, "index", -1)


def _load_for_project(
    project_dir: str | Path,
    rom_path: str | Path,
    catalog: RomProfileCatalog,
) -> tuple[
    StatProject,
    RomIdentification,
    RomProfile,
    StatTables | None,
    TextStrings | None,
    Maps | None,
]:
    project = read_project(project_dir)
    identification = identify_rom(rom_path, catalog)
    profile = _require_extractable_profile(identification)
    try:
        tables: StatTables | None = load_stat_tables(rom_path, catalog)
    except StatProfileError:
        tables = None
    try:
        strings: TextStrings | None = load_text_strings(rom_path, catalog)
    except TextProfileError:
        strings = None
    try:
        maps: Maps | None = load_maps(rom_path, catalog)
    except MapEntryProfileError:
        maps = None
    return project, identification, profile, tables, strings, maps




def validate_project(
    project_dir: str | Path,
    rom_path: str | Path,
    catalog: RomProfileCatalog,
) -> ValidationReport:
    """Check a project against a base ROM. Writes nothing, ever."""
    project, identification, profile, tables, strings, maps = _load_for_project(
        project_dir, rom_path, catalog
    )

    problems = _check_identity(project, identification, profile)
    if not problems:
        from .project.model import GRAPHICS_FILE

        authored_graphics = (Path(project_dir) / GRAPHICS_FILE).is_file()
        authored_raw_bytes = read_raw_bytes(project_dir)
        canonical_image = (
            Path(rom_path).read_bytes()
            if (project.layout.cells() or project.dialogues
                or not project.structure.is_empty()
                or not project.transitions.is_empty()
                or not project.transition_creations.is_empty()
                or not project.sprites.is_empty()
                or not project.appearances.is_empty()
                or not project.authored_maps.is_empty()
                or authored_raw_bytes
                or authored_graphics)
            else None
        )
        problems = (
            _check_records(project, tables)
            + _check_strings(project, strings)
            + _check_maps(project, maps)
            + _check_layout(project, profile, canonical_image)
            + _check_transitions(project, profile, canonical_image)
            + _check_transition_creations(project, profile, canonical_image)
            + _check_sprites(project, profile, project_dir, canonical_image,
                             identification, maps)
            + _check_appearances(project, profile, canonical_image, identification)
            + _check_authored_maps(project, profile, canonical_image, identification)
            + _check_graphics(project, profile, project_dir, canonical_image, identification)
            + _check_dialogues(project, profile, rom_path)
            + _check_raw_bytes(project_dir, canonical_image)
        )

    return ValidationReport(
        project_name=project.meta.name,
        profile_id=project.meta.profile_id,
        base_sha256=project.meta.base_rom_sha256,
        enemy_count=len(project.enemies),
        character_count=len(project.characters),
        string_count=len(project.strings),
        map_count=len(project.maps),
        problems=tuple(problems),
    )




def _apply_project_to_tables(project: StatProject, tables: StatTables) -> None:
    for identity, values in project.enemies.items():
        entry = tables.enemy(identity)
        for field in ENEMY_FIELDS:
            if getattr(entry.record, field) != values[field]:
                tables.set_enemy_field(identity, field, values[field])

    for identity, values in project.characters.items():
        entry = tables.character(identity)
        for field in CHARACTER_FIELDS:
            if getattr(entry.record, field) != values[field]:
                tables.set_character_field(identity, field, values[field])


def _apply_project_to_maps(project: StatProject, maps: Maps) -> None:
    for index, values in project.maps.items():
        identity = MapIdentity(index)
        for name in MAP_FIELDS:
            if maps.field(identity, name) != values[name]:
                maps.set_field(identity, name, values[name])

        # TOOLKIT-008. An authored placement whose halfwords differ from the
        # loaded record is staged as an edit. An index the loaded image does not
        # own is refused by `Maps.placement`, so a project naming a placement
        # that this ROM does not have fails before anything is written.
        for item in values.get("placements", ()):
            placement_identity = PlacementIdentity(index, item["index"])
            current = maps.placement(placement_identity).record
            if (
                current.position_low != item["position_low"]
                or current.position_high != item["position_high"]
            ):
                maps.set_placement_position(
                    placement_identity,
                    low=item["position_low"],
                    high=item["position_high"],
                )


def build_project(
    project_dir: str | Path,
    rom_path: str | Path,
    output_path: str | Path,
    catalog: RomProfileCatalog,
    *,
    manifest_path: str | Path | None | _ManifestBesideOutput = MANIFEST_BESIDE_OUTPUT,
) -> BuildResult:
    """Build a project into a NEW ROM image; the base is never modified, and a project that does not validate produces an error and no output file."""
    project, identification, profile, tables, strings, maps = _load_for_project(
        project_dir, rom_path, catalog
    )

    identity_problems = _check_identity(project, identification, profile)
    if identity_problems:
        raise ProjectRomMismatchError("; ".join(identity_problems))

    # LOG1-RAW-WRITE-BUILD-001. The raw byte document is read here, once, and only
    # when the project authors one. That read decides whether the canonical image
    # has to be opened, and the same image then backs both the plan's raw changes
    # below and the validation of the document above them, so what a build applies
    # and what it opens the image for cannot be two different answers.
    raw_edits = read_raw_bytes(project_dir)
    raw_image = Path(rom_path).read_bytes() if raw_edits else None

    problems = (
        _check_records(project, tables)
        + _check_strings(project, strings)
        + _check_maps(project, maps)
        + _check_dialogues(project, profile, rom_path)
        + _check_raw_bytes(project_dir, raw_image)
    )
    if problems:
        raise ProjectValidationError(
            f"project failed validation with {len(problems)} problem(s): "
            + "; ".join(problems[:5])
            + ("; ..." if len(problems) > 5 else "")
        )

    # ARCH-REFACTOR-001: the sequencing that joins the authored-materialization
    # steps is owned by `authored_placements`, which owns every step. This driver
    # supplies the reference graph and receives the result; it no longer encodes
    # what a missing document means, how a LayoutError is reported, or which maps
    # must yield their canonical structures to an authored expansion.
    #
    # TOOLKIT-036: this is also where the build-scoped RESERVATION SET starts. Two
    # allocating domains - authored placements and relocated text - draw from the
    # same profile-declared free regions, and each used to derive its reserved set
    # from its own reference document alone, so neither could see the other's
    # allocations. They met only in the merged `plan_changes` below, which detects
    # an overlap but cannot prevent one. The coordinator now carries one set of
    # allocated spans forward in its EXISTING domain order - placements here, text
    # at its existing `strings.changes()` position - so every completed allocation
    # is visible to every later allocating domain. No new priority policy: the
    # order is the one this function already had.
    from .authored_placements import materialize_for_build
    reserved: tuple = ()
    authored_changes, authored_map_identities, reserved = materialize_for_build(
        project, maps, _placement_document, reserved)

    # SPRITE-NEW-PROJECT-SURFACE-001. The map domain must yield the record of any
    # map an authored actor is appended to, for the same reason TOOLKIT-028 yields
    # one to an authored placement expansion: the attachment planner rewrites that
    # map's ``MapEntry+0x04`` count and ``+0x14`` array pointer itself, so
    # re-encoding the record at its canonical values here would collide with it
    # byte-for-byte. The two combinations that would give one map's object array
    # two writers are refused by the same check `validate` runs, so a project that
    # cannot be built is refused at validation rather than at the last step.
    sprite_maps = _sprite_maps(project)
    sprite_clashes = _sprite_map_clashes(project, maps)
    if sprite_maps & authored_map_identities:
        clash = ", ".join(sorted(str(identity)
                                 for identity in sprite_maps & authored_map_identities))
        sprite_clashes.append(
            f"this project authors a new actor on {clash} and also gives that map an "
            "authored placement expansion; both re-emit the map's object array, so a "
            "build cannot apply both"
        )
    if sprite_clashes:
        raise ProjectValidationError("; ".join(sprite_clashes))
    authored_map_identities = authored_map_identities | sprite_maps

    # Every declared subsystem contributes every record, edited or not - that is
    # what proves the round trip, since an unedited record must re-encode to its
    # original bytes and `plan_changes` then drops it as a no-op.
    changes: list[ByteChange] = []
    base_bytes: bytes | None = None

    # LOG1-RAW-WRITE-BUILD-001. The project's raw byte document joins the plan as
    # one more contributor of ordinary `ByteChange`es: a raw edit is not a second
    # mutation engine, it is a change whose owner is the image address it lands
    # at. It is read from the committed project the same way every other document
    # is, never from the application's journal, so a build applies what was saved
    # and not what is pending.
    #
    # The bytes it replaces are read from the canonical image HERE, not from the
    # document, which does not store them: `plan_changes` then refuses the change
    # unless the image it is handed really holds those bytes, which is what makes
    # a write authored against a different image a refusal rather than a guess.
    if raw_image is not None:
        changes += raw_byte_changes(raw_edits, raw_image)
        base_bytes = raw_image

    if tables is not None:
        _apply_project_to_tables(project, tables)
        changes += tables.changes()
        base_bytes = tables.base_bytes
    if strings is not None:
        # The second allocating domain. It plans against the declared free regions
        # minus everything the first one took, so its bodies cannot be handed bytes
        # that are already spoken for. Its own allocations extend the set in turn.
        strings.reserve(reserved)
        changes += strings.changes()
        reserved += strings.allocated_spans()
        base_bytes = strings.base_bytes if base_bytes is None else base_bytes
    if maps is not None:
        _apply_project_to_maps(project, maps)
        # SPRITE-NEW-PROJECT-SURFACE-001 extends that yield to a map an authored
        # actor is appended to. An authored FIELD on such a map was already refused
        # above, because this domain emits the whole record.
        changes += maps.changes(authored_maps=authored_map_identities)
        from .data.placement_contracts import CONTRACTS
        if maps.profile.id in CONTRACTS:
            from .placement_events import PlacementEvents
            changes += PlacementEvents(maps).changes()
        base_bytes = maps.base_bytes if base_bytes is None else base_bytes

    changes += authored_changes

    # GRAPHICS-IMPORT-BOUNDARY-001 extends the same block to authored pixels, and
    # the two are resolved together on purpose: they are one authored surface
    # (`project.graphics_overrides`), they are validated by one gate, and they must
    # reach the ONE plan below without either overwriting the other. A project that
    # authors both therefore loads the sprite corpus exactly once.
    palette_overrides = project.graphics_overrides.palette
    sprites = None
    pixel_overrides: dict = {}
    graphics_manifest = None
    graphics_image: bytes | None = None
    if palette_overrides or capability.declared(profile, capability.Capability.ACTOR_SPRITES):
        from .graphics_authoring import (CanonicalGraphics, read_graphics_manifest,
                                         resolve_pixel_overrides)
        image = Path(rom_path).read_bytes()
        graphics_image = image
        graphics_manifest = read_graphics_manifest(project_dir)
        if graphics_manifest is not None and graphics_manifest.profile_id != profile.id:
            raise ProjectValidationError(
                f"the project's extracted graphics manifest was written for "
                f"{graphics_manifest.profile_id!r}, but this ROM is {profile.id!r}; "
                "a build would resolve every authored PNG against the wrong assets"
            )
        canonical = CanonicalGraphics(image, identification)
        pixel_overrides = resolve_pixel_overrides(
            project_dir, graphics_manifest, canonical.pixels_of
        )
        if palette_overrides or pixel_overrides:
            if not capability.declared(profile, capability.Capability.ACTOR_SPRITES):
                authored = ("palette overrides" if palette_overrides else "pixel overrides")
                raise ProjectValidationError(
                    f"project authors {authored}, but this ROM's profile declares no "
                    "actor_sprites; a build would silently drop them"
                )
            sprites = canonical.sprites
        if palette_overrides:
            for index in sorted(palette_overrides):
                red, green, blue = palette_overrides[index]
                offset, new = sprites.plan_palette_entry_rgb(index, red, green, blue)
                changes.append(
                    ByteChange(
                        offset=offset,
                        old=image[offset : offset + len(new)],
                        new=new,
                        owner=f"palette_entry:{index:03d}",
                        reason=f"WORKBENCH-005 palette recolour to rgb({red},{green},{blue})",
                    )
                )
            base_bytes = image if base_bytes is None else base_bytes

    # MAP-TILE-PAINT-001: authored chunk-cell paints contribute ByteChanges the
    # same way every other subsystem does. Each painted cell is a four-byte
    # in-place replacement of a dominant layer's chunk pointer with a chunk a
    # dominant layer of the same map already uses, planned through the ONE paint
    # authority
    # (`map_paint.MapPainter`), so it merges into the single plan below where an
    # overlap with another owner is a hard error rather than a silent
    # last-writer-wins. A non-canonical profile cannot be painted at all, and
    # that is refused here rather than silently dropping the authored cells.
    layout_edits = project.layout.cells()
    structural_slots = project.structure.structural_slots()
    if structural_slots:
        layout_edits = {
            key: value
            for key, value in layout_edits.items()
            if (key[0], key[1]) not in structural_slots
        }
    ordinal_edits = {
        key: value for key, value in layout_edits.items() if type(value) is int
    }
    authored_edits = {
        key: value for key, value in layout_edits.items() if type(value) is str
    }
    chunk_edits: tuple = ()
    chunk_materialization = None
    generated_allocations: list = []
    if ordinal_edits:
        canonical = packaged_profile()
        if canonical.identity.sha256 != profile.identity.sha256:
            raise ProjectValidationError(
                "project paints a map layout, but this ROM's profile is not the "
                "canonical layout domain; a build would silently drop every "
                "painted cell"
            )
        image = Path(rom_path).read_bytes()
        try:
            changes += plan_layout_cells(image, ordinal_edits, profile=canonical)
        except MapPaintError as exc:
            raise ProjectValidationError(f"authored map layout: {exc}") from exc
        base_bytes = image if base_bytes is None else base_bytes

    # MAP-CHUNK-AUTHORING-001's domain: the third allocating domain, and the
    # first whose pointer is neither a selector nor an array index but a full
    # 32-bit address in a dominant layer's own window. It runs against the same
    # reservation set as every other domain, so an authored chunk body cannot be
    # handed bytes an earlier domain already took, and it extends that set in
    # turn for the domains after it.
    if authored_edits or (project.chunks and not project.chunks.is_empty()) or not project.structure.is_empty():
        canonical = packaged_profile()
        if canonical.identity.sha256 != profile.identity.sha256:
            raise ProjectValidationError(
                "project authors map chunks, but this ROM's profile is not the "
                "canonical chunk domain; a build would silently drop them"
            )
        image = Path(rom_path).read_bytes()
        structural_refs: tuple = ()
        if not project.structure.is_empty():
            try:
                structural_refs = structural_placements(
                    image, project.structure, project.layout, profile=canonical
                )
            except MapStructureError as exc:
                raise ProjectValidationError(f"authored map structure: {exc}") from exc
        try:
            chunk_materialization = materialize_authored_chunks(
                image,
                project.chunks.chunks,
                authored_edits,
                profile=canonical,
                reserved=reserved,
                structural=structural_refs,
            )
        except ChunkAuthoringError as exc:
            raise ProjectValidationError(f"authored map chunk: {exc}") from exc
        changes += chunk_materialization.changes
        reserved += chunk_materialization.reserved
        generated_allocations += list(chunk_materialization.generated_allocations)
        chunk_edits = chunk_materialization.provenance
        base_bytes = image if base_bytes is None else base_bytes

    # MAP-RESIZE-AND-LAYERS-001's domain: the fourth allocating domain, and the
    # first whose pointer holder is a **map root's own layer-slot field** rather
    # than a chunk window cell. It runs after the chunk domain because a record's
    # window may name a project-authored chunk body, whose address only exists once
    # that domain has placed it. Every record is EXPANDED_ONLY: a dominant record
    # grows with the authored grid and the canonical image declares one 256-byte
    # free region, so the domain's aggregate demand cannot be served canonically.
    structure_edits: tuple = ()
    if not project.structure.is_empty():
        canonical = packaged_profile()
        if canonical.identity.sha256 != profile.identity.sha256:
            raise ProjectValidationError(
                "project authors map structure, but this ROM's profile is not the "
                "canonical map domain; a build would silently drop it"
            )
        image = Path(rom_path).read_bytes()
        placed_chunks = (
            {build.identity: build.rom_address for build in chunk_materialization.builds}
            if chunk_materialization is not None
            else {}
        )
        try:
            structure_materialization = materialize_map_structure(
                image,
                project.structure,
                project.layout,
                profile=canonical,
                reserved=reserved,
                chunk_addresses=placed_chunks,
            )
        except MapStructureError as exc:
            raise ProjectValidationError(f"authored map structure: {exc}") from exc
        changes += structure_materialization.changes
        reserved += structure_materialization.reserved
        generated_allocations += list(structure_materialization.generated_allocations)
        structure_edits = structure_materialization.provenance
        base_bytes = image if base_bytes is None else base_bytes

    transition_edits: tuple = ()
    if not project.transitions.is_empty():
        canonical = packaged_profile()
        if canonical.identity.sha256 != profile.identity.sha256:
            raise ProjectValidationError(
                "project authors map transitions, but this ROM's profile is not the "
                "canonical transition domain; a build would silently drop every "
                "authored transition"
            )
        image = Path(rom_path).read_bytes()
        try:
            transition_application = plan_transition_edits(
                image, _transition_requests(project), profile=canonical,
                authored=_authored_facts(project, canonical, image),
            )
        except _TRANSITION_ERRORS as exc:
            raise ProjectValidationError(f"authored map transition: {exc}") from exc
        changes += transition_application.changes
        transition_edits = transition_application.provenance
        base_bytes = image if base_bytes is None else base_bytes

    # MAP-WARP-CREATE-PROJECT-001's domain: the first transition domain that
    # allocates. It runs after the edit domain because the two are independent - an
    # edit rewrites a canonical record in place, a creation appends a new one - and
    # after every other allocating domain so its record and expanded array are placed
    # clear of the spans those domains already reserved. It returns its own spans to
    # that same build-scoped set, and it is the only writer of `root + 0x40` and
    # `root + 0x44` in the whole toolkit.
    transition_creations: tuple = ()
    if not project.transition_creations.is_empty():
        canonical = packaged_profile()
        if canonical.identity.sha256 != profile.identity.sha256:
            raise ProjectValidationError(
                "project creates map transitions, but this ROM's profile is not the "
                "canonical transition domain; a build would silently drop every "
                "created transition"
            )
        image = Path(rom_path).read_bytes()
        try:
            creation_materialization = materialize_transition_creations(
                image, _creation_requests(project), profile=canonical, reserved=reserved,
                authored=_authored_facts(project, canonical, image),
            )
        except _TRANSITION_ERRORS as exc:
            raise ProjectValidationError(f"created map transition: {exc}") from exc
        changes += creation_materialization.changes
        reserved += creation_materialization.reserved
        generated_allocations += list(creation_materialization.generated_allocations)
        transition_creations = creation_materialization.provenance
        base_bytes = image if base_bytes is None else base_bytes


    dialogue_image = None
    dialogue_provenance: tuple = ()
    dialogue_edits: tuple = ()
    if project.dialogues:
        if base_bytes is None:
            raise BuildError("compressed dialogue requires a canonical build image")
        from .compressed_dialogue import dialogue_edits_for, materialize_dialogues
        dialogue_runs, dialogue_reserved, dialogue_image, dialogue_provenance = materialize_dialogues(
            base_bytes, profile, project.dialogues, reserved
        )
        for run in dialogue_runs:
            changes += run.changes
        dialogue_edits = dialogue_edits_for(dialogue_runs)
        reserved += dialogue_reserved
        generated_allocations += list(dialogue_provenance)

    sprite_relocations: tuple = ()
    sprite_authoring: tuple = ()
    if not project.sprites.is_empty():
        image = Path(rom_path).read_bytes()
        try:
            sprite_materialization = materialize_authored_sprites(
                image, identification, profile, project.sprites, project_dir,
                reserved=reserved, corpus=sprites)
        except _SPRITE_ERRORS as exc:
            raise ProjectValidationError(f"authored actor sprite: {exc}") from exc
        changes += sprite_materialization.changes
        reserved += sprite_materialization.reserved
        generated_allocations += list(sprite_materialization.generated_allocations)
        sprite_relocations = sprite_materialization.relocations
        sprite_authoring = (sprite_materialization.provenance(),)
        base_bytes = image if base_bytes is None else base_bytes

    appearance_relocations: tuple = ()
    if not project.appearances.is_empty():
        image = Path(rom_path).read_bytes()
        try:
            appearance_materialization = materialize_authored_appearances(
                image, identification, profile, project.appearances,
                authored_sprite_id=_authored_sprite_id(project),
                reserved=reserved,
            )
        except _APPEARANCE_ERRORS as exc:
            raise ProjectValidationError(
                f"authored appearance definition: {exc}") from exc
        changes += appearance_materialization.changes
        reserved += appearance_materialization.reserved
        generated_allocations += list(
            appearance_materialization.generated_allocations)
        appearance_relocations = appearance_materialization.relocations
        base_bytes = image if base_bytes is None else base_bytes

    # MAP-NEW-AUTHORING-001's domain: the MapEntry table is re-emitted whole with
    # the project's authored rows appended, the one literal-pool word that names
    # the table is repointed and the one compiled row bound is raised, all in this
    # change list. It runs AFTER every other domain that writes a `MapEntry` field -
    # a map field edit, an expanded placement run, an appended map actor - because
    # those writes are planned at the CANONICAL table offset and the engine reads
    # only the moved copy. `prior_changes` is what lets the copy carry them; a
    # domain that ran later could not be carried, which is why this is the last
    # writing domain and only the graphics pixels are after it.
    authored_map_relocations: tuple = ()
    if not project.authored_maps.is_empty():
        image = Path(rom_path).read_bytes()
        try:
            authored_map_materialization = materialize_authored_maps(
                image, identification, profile, _map_authoring_requests(project),
                reserved=reserved, prior_changes=tuple(changes),
            )
        except _MAP_AUTHORING_ERRORS as exc:
            raise ProjectValidationError(f"authored map: {exc}") from exc
        changes += authored_map_materialization.changes
        reserved += authored_map_materialization.reserved
        generated_allocations += list(
            authored_map_materialization.generated_allocations)
        authored_map_relocations = authored_map_materialization.relocations
        base_bytes = image if base_bytes is None else base_bytes

    # GRAPHICS-IMPORT-BOUNDARY-001: authored graphic pixels are the last allocating
    # domain, and they run here rather than beside the palette block above for a
    # deliberate reason. A re-encoded payload that fits its original container
    # extent is a plain in-place overwrite and takes nothing from the reservation
    # set; one that does not fit asks the ONE allocation authority for storage. By
    # running after every other allocating domain, a graphics relocation can only
    # ever be placed clear of what they already took, and it cannot move where any
    # of them land. The original payload bytes are deliberately left intact, so a
    # reference this toolkit did not discover still reaches the art it always did.
    graphic_relocations: tuple = ()
    if pixel_overrides:
        from .allocation import AllocationError
        from .formats.sprite_graphics import SpriteFormatError
        from .graphics_authoring import GraphicsAuthoringError, plan_graphic_overrides
        try:
            materialization = plan_graphic_overrides(
                graphics_image,
                identification,
                pixel_overrides,
                reserved=reserved,
                sprites=sprites,
            )
        except (GraphicsAuthoringError, SpriteFormatError, AllocationError) as exc:
            raise ProjectValidationError(f"authored graphic pixels: {exc}") from exc
        changes += materialization.changes
        reserved += materialization.reserved
        generated_allocations += list(materialization.generated_allocations)
        graphic_relocations = materialization.relocations

    if base_bytes is None:
        # Unreachable: `_require_extractable_profile` refuses a profile that
        # declares nothing, so at least one subsystem loaded. Kept because
        # silently emitting a copy of the base would look like a successful
        # build that applied the project.
        raise BuildError(
            f"profile {profile.id!r} declares no buildable content"
        )

    generated_image = dialogue_image
    if generated_allocations:
        expansion = profile.generated_expansion
        if expansion is None:
            raise ProjectValidationError(
                "a build domain allocated storage above canonical EOF, but this "
                "ROM's profile declares no generated expansion to authorize it"
            )
        generated_image = expansion.generated_image(
            profile.size,
            tuple(item.allocated_range for item in generated_allocations),
        )

    plan = plan_changes(
        base_bytes,
        changes,
        profile_id=profile.id,
        base_sha256=identification.hashes.sha256,
        relocations=(graphic_relocations + sprite_relocations
                     + appearance_relocations + authored_map_relocations),
        generated_image=generated_image,
        generated_allocations=tuple(generated_allocations),
        dialogue_edits=dialogue_edits,
        chunk_edits=chunk_edits,
        structure_edits=structure_edits,
        transition_edits=transition_edits,
        transition_creations=transition_creations,
        sprite_authoring=sprite_authoring,
    )

    resolved_manifest = manifest_path_for_build(manifest_path, output_path)

    manifest = emit_image(
        rom_path,
        output_path,
        plan,
        manifest_path=resolved_manifest,
        project=ProjectProvenance(
            name=project.meta.name,
            format_version=project.meta.format_version,
        ),
    )

    return BuildResult(
        manifest=manifest,
        output_path=Path(output_path),
        manifest_path=resolved_manifest,
        project_name=project.meta.name,
    )


def _placement_document(maps):
    from .entities import PlacementTypes, PlacementTypeError
    from .capability import CapabilityError
    try:
        return PlacementTypes(maps).reference_document()
    except (PlacementTypeError, CapabilityError):
        return None


def authored_capacity_plan(project_dir, rom_path, catalog):
    project, identification, profile, tables, strings, maps = _load_for_project(
        project_dir, rom_path, catalog)
    problems = _check_identity(project, identification, profile)
    if problems:
        raise ProjectRomMismatchError("; ".join(problems))
    problems = (_check_records(project, tables) + _check_strings(project, strings)
                + _check_maps(project, maps))
    if problems:
        raise ProjectValidationError("; ".join(problems))
    from .authored_placements import prepare_authored_runs
    return prepare_authored_runs(project, maps)
