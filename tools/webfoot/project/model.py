"""The authored project: what a mod IS on disk, and what it promises.

TOOLKIT-002. A mod is a directory of text, not a sequence of edits applied to a
binary. That inversion is the whole point of this ticket, and three properties
follow from it:

**The project is the authoring surface; the ROM is the truth.** `project.toml`
pins the base ROM by SHA-256 and the profile by id, so a project carries the
identity of the thing it was authored against and can refuse to build against
anything else. It does NOT carry a path to that ROM: a path is a fact about one
machine, and a project that recorded one would stop being portable the moment
it was cloned.

**Authored values are semantic.** `hp = 200`, never `0x00711BE0 = 0xC8`. A mod
that stored offsets would break when anything moved and would be unreadable to
a future decomp backend; a mod that stores `hp` survives both. Addresses appear
in the project only as commentary the build never reads back.

**Unknown bytes are the project's responsibility.** Both stat layouts have
spans this project has not decoded, and byte-identical reconstruction requires
them verbatim. They live in the authored file as an opaque hex blob per record
(`raw`), which the user is not expected to edit and which the build re-emits
untouched. Dropping them would make the round-trip proof unachievable; hiding
them somewhere outside the authored tree would make the project incomplete.

Layout, deliberately the smallest thing that works:

    project/
      project.toml      identity: format version, profile, base ROM hash
      enemies/          one file per stat table, not one file per record
        enemies.toml
      characters/
        characters.toml
      text/             TOOLKIT-004
        strings.toml

One file per table rather than per record: 141 single-record files would be a
worse Git experience, not a better one, and nothing here needs per-record file
granularity. Directories exist only for the supported content types; no empty
directories are reserved for systems that do not exist yet.

**Text carries no `raw` blob, and that is not an inconsistency.** A stat record
needs one because only part of its stride is decoded, so the undecoded spans
have to ride along verbatim. The text codec is lossless over the whole pool -
every byte, control codes included, survives `decode` then `encode` - so the
authored string already IS the complete description of its bytes. Adding a
redundant hex copy would create a second source of truth that could disagree
with the first, which is worse than having one.

1,534 strings live in a single `text/strings.toml` rather than in per-scene
files, because nothing here yet knows which scene a string belongs to. Inventing
a grouping would mean inventing facts; the index key already sorts stably and
gives a one-line-per-edit diff.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from ..formats import stat_tables as st
from ..formats import text_tables as tt
from .format import ProjectFormatError, dump_toml, load_toml

#: Bumped when the authored layout changes incompatibly. A project declaring a
#: version this toolkit does not implement is refused rather than guessed at.
PROJECT_FORMAT_VERSION = 1

_PROJECT_FILE = "project.toml"
_ENEMY_FILE = Path("enemies") / "enemies.toml"
_CHARACTER_FILE = Path("characters") / "characters.toml"
_TEXT_FILE = Path("text") / "strings.toml"

#: Authored field order within a record. Fixed, so output is deterministic;
#: chosen for reading rather than sorted, because a human edits these.
_ENEMY_FIELD_ORDER = ("hp", "exp", "level", "strength", "power", "endurance")
_CHARACTER_FIELD_ORDER = (
    "level",
    "hp",
    "ep",
    "strength",
    "power",
    "endurance",
    "speed",
)

#: Decoded-but-not-editable fields. They are authored so the file is a complete
#: description of the record, and validated on load, but no CLI edit path
#: exposes them: `type_id` IS the enemy identity, and `person` /
#: `technique_count` index tables this ticket does not decode.
_ENEMY_FIXED_FIELDS = ("type_id",)
_CHARACTER_FIXED_FIELDS = ("person", "technique_count")


class ProjectError(ValueError):
    """Base error for project source problems."""


class ProjectLoadError(ProjectError):
    """Raised when a project cannot be read or its schema is unusable."""


class ProjectValidationError(ProjectError):
    """Raised when project content is structurally valid but semantically wrong.

    Distinct from `ProjectLoadError` on purpose: one means "this is not a
    project", the other means "this is a project that says something false".
    Both fail before any output is written.
    """


@dataclass(frozen=True, slots=True)
class ProjectMeta:
    """What `project.toml` pins. Everything here is identity, not preference.

    `base_rom_sha256` is the contract: a build against any other image is
    refused. `profile_id` names the metadata contract - which extents the
    records were authored against - and is checked independently, because a
    matching hash with mismatched extents would still be wrong.
    """

    format_version: int
    profile_id: str
    game: str
    base_rom_sha256: str
    base_rom_size: int
    name: str

    def to_document(self) -> dict[str, Any]:
        return {
            "project": {
                "format_version": self.format_version,
                "name": self.name,
            },
            "base": {
                "profile_id": self.profile_id,
                "game": self.game,
                "sha256": self.base_rom_sha256,
                "size": self.base_rom_size,
            },
        }

    @classmethod
    def from_document(cls, document: Mapping[str, Any]) -> "ProjectMeta":
        project = _require_table(document, "project", _PROJECT_FILE)
        base = _require_table(document, "base", _PROJECT_FILE)

        version = project.get("format_version")
        if type(version) is not int:
            raise ProjectLoadError(
                f"{_PROJECT_FILE}: project.format_version must be an integer"
            )
        if version != PROJECT_FORMAT_VERSION:
            raise ProjectLoadError(
                f"{_PROJECT_FILE}: project format version {version} is not "
                f"supported; this toolkit implements version "
                f"{PROJECT_FORMAT_VERSION}"
            )

        sha256 = _require_str(base, "sha256", "base", _PROJECT_FILE).lower()
        if len(sha256) != 64 or any(c not in "0123456789abcdef" for c in sha256):
            raise ProjectLoadError(
                f"{_PROJECT_FILE}: base.sha256 must be 64 hexadecimal characters"
            )
        size = base.get("size")
        if type(size) is not int or size <= 0:
            raise ProjectLoadError(
                f"{_PROJECT_FILE}: base.size must be a positive integer"
            )

        return cls(
            format_version=version,
            profile_id=_require_str(base, "profile_id", "base", _PROJECT_FILE),
            game=_require_str(base, "game", "base", _PROJECT_FILE),
            base_rom_sha256=sha256,
            base_rom_size=size,
            name=_require_str(project, "name", "project", _PROJECT_FILE),
        )


@dataclass(frozen=True, slots=True)
class StatProject:
    """A whole loaded project: identity plus authored records.

    Records are held keyed by durable `StatIdentity`, and every record carries
    the opaque bytes it was extracted with. That pairing is what makes a build
    lossless: the semantic fields describe what a person edits, and `raw`
    carries everything the project has not learned to describe yet.
    """

    meta: ProjectMeta
    enemies: dict[st.StatIdentity, dict[str, Any]]
    characters: dict[st.StatIdentity, dict[str, Any]]
    #: TOOLKIT-004. Authored strings by durable identity. Empty for a project
    #: extracted before text support existed, which stays loadable: a missing
    #: `text/strings.toml` means "this project does not author text", not
    #: "this project is broken". A build then leaves the ROM's text alone.
    strings: dict[tt.TextIdentity, str] = field(default_factory=dict)


# --- helpers -------------------------------------------------------------


def _require_table(
    document: Mapping[str, Any], key: str, where: object
) -> Mapping[str, Any]:
    value = document.get(key)
    if not isinstance(value, Mapping):
        raise ProjectLoadError(f"{where}: missing required [{key}] table")
    return value


def _require_str(
    table: Mapping[str, Any], key: str, section: str, where: object
) -> str:
    value = table.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ProjectLoadError(
            f"{where}: {section}.{key} must be a non-empty string"
        )
    return value.strip()


def _require_int(
    table: Mapping[str, Any], key: str, label: str, where: object
) -> int:
    value = table.get(key)
    # bool is an int subclass; `hp = true` must not silently become 1.
    if type(value) is not int:
        raise ProjectValidationError(
            f"{where}: {label}.{key} must be an integer, got {value!r}"
        )
    return value


def _require_hex_blob(
    table: Mapping[str, Any], label: str, where: object, size: int
) -> bytes:
    raw = table.get("raw")
    if not isinstance(raw, str):
        raise ProjectValidationError(
            f"{where}: {label}.raw must be a hexadecimal string carrying the "
            "record's undecoded bytes; without it the record cannot be rebuilt"
        )
    try:
        blob = bytes.fromhex(raw)
    except ValueError as exc:
        raise ProjectValidationError(f"{where}: {label}.raw is not valid hex: {exc}") from exc
    if len(blob) != size:
        raise ProjectValidationError(
            f"{where}: {label}.raw must be exactly {size} bytes; got {len(blob)}"
        )
    return blob


# --- serialization -------------------------------------------------------


def _enemy_document(
    records: list[tuple[st.StatIdentity, st.EnemyRecord, bytes, str | None]],
) -> dict[str, Any]:
    """Build the enemies document, ordered by durable identity key.

    Sorted by `type_id`, NOT by table position. Table order is a fact about the
    current ROM layout; identity order is a fact about the project. Sorting by
    identity means a record that moves in the ROM does not move in the file,
    which is the difference between a diff that shows one edit and a diff that
    shows a reshuffle.
    """
    tables: dict[str, Any] = {}
    for identity, record, original, alias in sorted(records, key=lambda item: item[0].key):
        entry: dict[str, Any] = {}
        if alias is not None:
            entry["alias"] = alias
        entry["type_id"] = record.type_id
        for field in _ENEMY_FIELD_ORDER:
            entry[field] = getattr(record, field)
        entry["raw"] = original.hex()
        tables[str(identity.key)] = entry
    return {"enemy": tables}


def _character_document(
    records: list[tuple[st.StatIdentity, st.BaseStatRecord, bytes, str]],
) -> dict[str, Any]:
    tables: dict[str, Any] = {}
    for identity, record, original, alias in sorted(records, key=lambda item: item[0].key):
        entry: dict[str, Any] = {"alias": alias}
        for field in _CHARACTER_FIELD_ORDER:
            entry[field] = getattr(record, field)
        for field in _CHARACTER_FIXED_FIELDS:
            entry[field] = getattr(record, field)
        entry["raw"] = original.hex()
        tables[str(identity.key)] = entry
    return {"character": tables}


def _text_document(strings: list[tuple[tt.TextIdentity, str]]) -> dict[str, Any]:
    """Build the strings document, ordered by durable identity key.

    The key is the pointer-table index zero-padded to four digits, so the
    lexical order TOML preserves is also the numeric order - `text:0009` sorts
    before `text:0010`, which a bare `9` and `10` would not.

    Each entry is a single `text` field. No address, no length, no `raw`: the
    address is where the string sits today, the length follows from the text,
    and the codec is lossless so the text is already complete.
    """
    tables: dict[str, Any] = {}
    for identity, text in sorted(strings, key=lambda item: item[0].index):
        tables[identity.key] = {"text": text}
    return {"text": tables}


def write_project(
    directory: str | Path,
    meta: ProjectMeta,
    *,
    enemies: list[tuple[st.StatIdentity, st.EnemyRecord, bytes, str | None]],
    characters: list[tuple[st.StatIdentity, st.BaseStatRecord, bytes, str]],
    strings: list[tuple[tt.TextIdentity, str]] | None = None,
) -> list[Path]:
    """Write the whole authored tree. Returns the files written, in order.

    Overwrites deliberately: extraction is idempotent by design, so re-running
    it over an existing project must converge rather than refuse. That is the
    opposite of `emit_image`, which refuses to overwrite - a built ROM is an
    artefact whose provenance would become unanswerable if silently replaced,
    while an authored file is source the user can diff and revert.
    """
    root = Path(directory)
    written: list[Path] = []

    documents = [
        (Path(_PROJECT_FILE), meta.to_document()),
        (_ENEMY_FILE, _enemy_document(enemies)),
        (_CHARACTER_FILE, _character_document(characters)),
    ]
    # Written only when there is text to write, so a profile without a declared
    # string table produces no empty file claiming it authors one.
    if strings:
        documents.append((_TEXT_FILE, _text_document(strings)))

    for relative, document in documents:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        # newline="\n" explicitly: the default on Windows would translate to
        # CRLF and the "same project extracts to the same bytes" property would
        # then depend on which machine ran the extraction.
        path.write_text(dump_toml(document), encoding="utf-8", newline="\n")
        written.append(path)

    return written


def _read_document(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ProjectLoadError(f"project file is missing: {path}") from exc
    except OSError as exc:
        raise ProjectLoadError(f"cannot read {path}: {exc}") from exc
    try:
        return load_toml(text)
    except ProjectFormatError as exc:
        raise ProjectLoadError(f"{path}: {exc}") from exc


def _read_records(
    path: Path,
    section: str,
    kind: str,
    fields: tuple[str, ...],
    fixed: tuple[str, ...],
    record_size: int,
) -> dict[st.StatIdentity, dict[str, Any]]:
    document = _read_document(path)
    table = document.get(section)
    if not isinstance(table, Mapping):
        raise ProjectLoadError(f"{path}: missing required [{section}] table")

    records: dict[st.StatIdentity, dict[str, Any]] = {}
    for key, entry in table.items():
        label = f"{section}.{key}"
        if not isinstance(entry, Mapping):
            raise ProjectLoadError(f"{path}: {label} must be a table")
        try:
            identity = st.StatIdentity(kind=kind, key=int(key, 10))
        except ValueError as exc:
            raise ProjectLoadError(
                f"{path}: {label} is not a valid {kind} identity key: {exc}"
            ) from exc

        values: dict[str, Any] = {}
        for field in fields + fixed:
            values[field] = _require_int(entry, field, label, path)
        values["raw"] = _require_hex_blob(entry, label, path, record_size)

        alias = entry.get("alias")
        if alias is not None and not isinstance(alias, str):
            raise ProjectLoadError(f"{path}: {label}.alias must be a string")
        values["alias"] = alias

        unexpected = set(entry) - set(fields) - set(fixed) - {"raw", "alias"}
        if unexpected:
            joined = ", ".join(sorted(unexpected))
            raise ProjectLoadError(
                f"{path}: {label} has unknown fields: {joined}"
            )

        if identity in records:
            raise ProjectLoadError(f"{path}: duplicate {kind} identity {identity}")
        records[identity] = values

    if not records:
        raise ProjectLoadError(f"{path}: [{section}] declares no records")
    return records


def _read_strings(path: Path) -> dict[tt.TextIdentity, str]:
    """Load `text/strings.toml`, or nothing at all if it is absent.

    Absence is legal and means the project does not author text - a project
    extracted before TOOLKIT-004 stays loadable, and a build leaves the ROM's
    text untouched. A file that exists but is malformed is still an error;
    "missing" and "wrong" are different answers.

    Every string is encode-checked here, at load, so a malformed control token
    is reported against its own line before any image is opened. That is the
    validation-before-emission rule: the cheapest place to refuse is the
    earliest one.
    """
    if not path.is_file():
        return {}

    document = _read_document(path)
    table = document.get("text")
    if not isinstance(table, Mapping):
        raise ProjectLoadError(f"{path}: missing required [text] table")

    strings: dict[tt.TextIdentity, str] = {}
    for key, entry in table.items():
        label = f"text.{key}"
        if not isinstance(entry, Mapping):
            raise ProjectLoadError(f"{path}: {label} must be a table")

        prefix, _, digits = key.partition(":")
        if prefix != "text" or not digits.isdigit():
            raise ProjectLoadError(
                f"{path}: {label} is not a valid text identity key; expected "
                'the form "text:0000"'
            )
        try:
            identity = tt.TextIdentity(int(digits, 10))
        except tt.TextCodecError as exc:
            raise ProjectLoadError(f"{path}: {label}: {exc}") from exc

        unexpected = set(entry) - {"text"}
        if unexpected:
            joined = ", ".join(sorted(unexpected))
            raise ProjectLoadError(f"{path}: {label} has unknown fields: {joined}")

        text = entry.get("text")
        if not isinstance(text, str):
            raise ProjectValidationError(f"{path}: {label}.text must be a string")
        try:
            tt.encode_string(text)
        except tt.TextCodecError as exc:
            raise ProjectValidationError(f"{path}: {label}.text is not encodable: {exc}") from exc

        if identity in strings:
            # Unreachable through TOML (duplicate keys are a parse error), but
            # the key form is normalized above, so two spellings of one index
            # could otherwise collide silently.
            raise ProjectLoadError(f"{path}: duplicate text identity {identity}")
        strings[identity] = text

    if not strings:
        raise ProjectLoadError(f"{path}: [text] declares no strings")
    return strings


def read_project(directory: str | Path) -> StatProject:
    """Load and structurally validate a project. Opens no ROM.

    Semantic validation against a base image happens in `webfoot.build`, which
    is the layer that has an image to validate against. Everything checkable
    from the text alone is checked here.
    """
    root = Path(directory)
    if not root.is_dir():
        raise ProjectLoadError(f"project directory does not exist: {root}")

    meta = ProjectMeta.from_document(_read_document(root / _PROJECT_FILE))
    enemies = _read_records(
        root / _ENEMY_FILE,
        "enemy",
        "enemy",
        _ENEMY_FIELD_ORDER,
        _ENEMY_FIXED_FIELDS,
        st.ENEMY_RECORD_SIZE,
    )
    characters = _read_records(
        root / _CHARACTER_FILE,
        "character",
        "character",
        _CHARACTER_FIELD_ORDER,
        _CHARACTER_FIXED_FIELDS,
        st.BASE_STAT_RECORD_SIZE,
    )

    for identity, values in enemies.items():
        if values["type_id"] != identity.key:
            raise ProjectValidationError(
                f"{root / _ENEMY_FILE}: enemy.{identity.key} declares type_id "
                f"{values['type_id']}; the identity key and type_id are the "
                "same fact and must agree"
            )

    strings = _read_strings(root / _TEXT_FILE)

    return StatProject(
        meta=meta,
        enemies=enemies,
        characters=characters,
        strings=strings,
    )
