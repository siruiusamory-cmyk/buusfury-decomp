"""Walking the roots, sniffing each file, and attributing it.

A file is opened read-only, hashed once, and recorded by `(path, size, mtime)`:
a re-scan of an unchanged tree re-hashes nothing, and `verify` is the mode that
re-hashes everything on purpose.

Provenance is a class plus the evidence that fired, never a guess:

* ``OWNER`` - registered through the CLI, or matched to the emulator's own
  recent-ROM list (`qt.ini` `[mru]`) with a save that sits beside a ROM from
  that list, or present in a protected backup directory;
* ``AGENT-STAGED`` - the digest is a known blank staged pattern;
* ``DERIVED`` - the file sits in a launcher run directory with an `inputs.json`
  that names this file's digest as its ROM, save or state, and only when the
  recorded path resolves to this file;
* ``BACKUP`` - under a protected backup directory;
* ``UNKNOWN`` - none of the above, with the reason every rule failed.
"""

from __future__ import annotations

import configparser
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from . import geometry, sniff, store
from .store import CatalogueError, Entry, Source, Store, sha256_of, utc_now

#: Suffixes the corpus actually uses for a battery save, and the prefix for a
#: savestate. `.save` and `.sav.bak` belong to unrelated software on this
#: machine and are deliberately not walked.
BATTERY_SUFFIXES = (".sav", ".srm")
STATE_SUFFIX_PREFIX = ".ss"

#: Directories never descended into: version control, virtual environments and
#: package caches hold unrelated `.sav`-shaped files and are not the corpus.
SKIP_DIRECTORIES = frozenset(
    {".git", ".venv", "venv", "node_modules", "site-packages", "__pycache__",
     ".pytest_cache", ".hypothesis", "dist", "$RECYCLE.BIN", "System Volume Information"}
)

#: Protected backup directories: read-only sources of a known-copy class.
DEFAULT_PROTECTED_BACKUPS = (Path.home() / ".dsh" / "work" / "log1-protected-rom-backups",)

#: Known blank patterns staged into every launcher run directory, by digest.
#: Both digests were measured from the corpus on 2026-10-12, not transcribed.
KNOWN_BLANK_DIGESTS = {
    "0223B3E0D4436D601C61D37B14184B430C19213D646C3724DA3B79CD1F099AC1":
        "512 bytes of 0xFF then 7,680 bytes of 0x00, staged into every launcher run directory",
    "7D2C7AC4888BFD75CD5F56E8D61F69595121183AFC81556C876732FD3782C62F":
        "fully erased: all 0xFF",
}


@dataclass(frozen=True)
class Provenance:
    provenance: str
    evidence: str


def default_roots() -> list[Path]:
    """The roots that matter, derived from the home directory and the checkout.

    The checkout parent is the directory this package's repository sits in, so
    no machine-specific absolute path is written down. `~` (the user profile)
    is deliberately absent from the defaults: it holds unrelated `.sav` files
    and is not the corpus. `--root` adds it for a caller who wants it.
    """
    roots: list[Path] = []
    # parents[2] is the checkout root, parents[3] the directory it sits in, so
    # the sibling worktrees are found without writing one machine's path down.
    checkout_parent = Path(__file__).resolve().parents[3]
    for pattern in ("log1-remake*", "log1-*"):
        for candidate in sorted(checkout_parent.glob(pattern)):
            build = candidate / "build"
            if build.is_dir() and build not in roots:
                roots.append(build)
    downloads = Path.home() / "Downloads"
    if downloads.is_dir():
        roots.append(downloads)
    roots.extend(_mgba_directories())
    roots.extend(DEFAULT_PROTECTED_BACKUPS)
    return roots


def _mgba_config_paths() -> list[Path]:
    appdata = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    config = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    local = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    return [
        appdata / "mgba" / "config.ini",
        appdata / "mgba" / "qt.ini",
        config / "mgba" / "config.ini",
        config / "mgba" / "qt.ini",
        local / "mgba" / "config.ini",
        local / "mgba" / "qt.ini",
    ]


def mgba_config() -> configparser.ConfigParser:
    parser = configparser.ConfigParser()
    parser.read([str(path) for path in _mgba_config_paths() if path.is_file()], encoding="utf-8")
    return parser


def _mgba_directories() -> list[Path]:
    """Save and state directories the emulator itself was configured with."""
    parser = mgba_config()
    found: list[Path] = []
    for section, keys in (
        ("ports.qt", ("savedir", "saveDirectory")),
        ("ports.qt", ("ssdir", "savestateDirectory")),
        ("savegame", ("savedir",)),
    ):
        if not parser.has_section(section):
            continue
        for key in keys:
            value = parser.get(section, key, fallback="").strip()
            if not value:
                continue
            candidate = Path(os.path.expandvars(value)).expanduser()
            if candidate.is_dir() and candidate not in found:
                found.append(candidate)
    return found


def recent_roms() -> dict[Path, str]:
    """The emulator's own recent-ROM list: resolved path -> the path as recorded."""
    parser = mgba_config()
    entries: dict[Path, str] = {}
    for section in parser.sections():
        if section != "mru":
            continue
        for _, value in parser.items(section):
            text = value.strip()
            if not text:
                continue
            candidate = Path(os.path.expandvars(text)).expanduser()
            if candidate.suffix.lower() in (".gba", ".agb"):
                entries[candidate] = text
    return entries


def resolve_provenance(path: Path, sha256: str, size: int,
                       roots: list[Path], protected: list[Path],
                       roms: dict[Path, str] | None = None) -> Provenance:
    stat = path.stat()
    for directory in protected:
        if _is_within(path, directory):
            return Provenance("BACKUP", f"inside the protected backup directory {directory}")
    runner = _run_record(path, sha256, roots)
    if runner is not None:
        return runner
    if sha256 in KNOWN_BLANK_DIGESTS:
        return Provenance("AGENT-STAGED", f"digest matches the known blank pattern: {KNOWN_BLANK_DIGESTS[sha256]}")
    if path.suffix.lower() in BATTERY_SUFFIXES:
        match = _recent_rom_match(path, stat, roms if roms is not None else recent_roms())
        if match is not None:
            return Provenance("OWNER", match)
    return Provenance(
        "UNKNOWN",
        "no rule fired: not inside a protected backup, not a known blank digest, not named by a run"
        " record, and no recent-ROM entry has a sibling save matching this stem",
    )


def _recent_rom_match(path: Path, stat: os.stat_result, roms: dict[Path, str]) -> str | None:
    for rom, recorded in sorted(roms.items(), key=lambda item: str(item[0])):
        if rom.parent.resolve() != path.parent.resolve() or rom.stem != path.stem:
            continue
        rom_mtime = rom.stat().st_mtime
        relation = "newer" if stat.st_mtime >= rom_mtime else "older"
        return (f"emulator recent-ROM entry {recorded} has the sibling save {path.name};"
                f" save mtime {utc_of(stat.st_mtime)} is {relation} than the image mtime"
                f" {utc_of(rom_mtime)}")
    return None


def sibling_rom(path: Path, roms: dict[Path, str]) -> Path | None:
    """The ROM this save sits beside, when the emulator's own list names one.

    A ROM the emulator recorded is evidence about the file next to it, which is
    how a save named `v3.sav` can still be attributed.
    """
    for rom in roms:
        if rom.parent.resolve() == path.parent.resolve() and rom.stem == path.stem:
            return rom
    return None


def utc_of(mtime: float) -> str:
    return datetime.fromtimestamp(mtime, timezone.utc).isoformat(timespec="seconds")


def _run_record(path: Path, sha256: str, roots: list[Path]) -> Provenance | None:
    """DERIVED: the file sits in a run directory whose inputs.json names it."""
    for root in roots:
        if not _is_within(path, root):
            continue
        for directory in _parents_up_to(path.parent, root):
            manifest = directory / "inputs.json"
            if not manifest.is_file():
                continue
            try:
                document = json.loads(manifest.read_bytes().decode("utf-8-sig"))
            except (OSError, ValueError):
                continue
            if not isinstance(document, dict):
                continue
            label = document.get("label", directory.name)
            for field, recorded in (("rom_path", "rom_sha256"), ("save_path", "save_sha256"),
                                    ("state_path", "state_sha256")):
                named = document.get(field)
                if named and Path(named) == path and document.get(recorded, "").upper() == sha256:
                    return Provenance(
                        "DERIVED",
                        f"run directory {directory} names this file as {field} with digest"
                        f" {sha256} and label {label}",
                    )
    return None


def _parents_up_to(path: Path, root: Path) -> list[Path]:
    chain: list[Path] = []
    current = path
    root = root.resolve()
    while True:
        chain.append(current)
        if current.resolve() == root or current.parent == current:
            break
        current = current.parent
    return chain


def _is_within(path: Path, root: Path) -> bool:
    resolved, anchor = Path(path).resolve(), Path(root).resolve()
    return resolved == anchor or anchor in resolved.parents


# -- the walk -----------------------------------------------------------------


def iter_candidates(root: Path):
    """Every candidate file under one root, deterministically ordered."""
    for directory, names, files in os.walk(root, onerror=lambda _error: None):
        names[:] = sorted(name for name in names if name not in SKIP_DIRECTORIES)
        for name in sorted(files):
            suffix = Path(name).suffix.lower()
            if suffix in BATTERY_SUFFIXES or (suffix and suffix.startswith(STATE_SUFFIX_PREFIX)):
                yield Path(directory) / name


@dataclass
class ScanReport:
    roots: list[str]
    missing_roots: list[str]
    new: int = 0
    updated: int = 0
    unchanged: int = 0
    rehashed: int = 0
    changed: list[dict] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.changed is None:
            self.changed = []

    def as_json(self) -> dict:
        return {
            "roots": self.roots,
            "missing_roots": self.missing_roots,
            "new": self.new,
            "updated": self.updated,
            "unchanged": self.unchanged,
            "rehashed": self.rehashed,
            "changed": self.changed,
        }


def fingerprint(size: int, mtime: float) -> tuple[int, int]:
    return size, int(mtime)


def scan(store_home: Path | None = None, roots: list[Path] | None = None,
         verify: bool = False, protected: list[Path] | None = None,
         rehash: bool = False) -> ScanReport:
    """Index every candidate under the roots. Never writes to a source.

    The fingerprint is `(size, mtime)`, so a re-scan of an unchanged tree reads
    each file's head and geometry and re-hashes nothing. `rehash` overrides that
    for the one case it cannot see: the tool's own reading rules changed, so an
    entry has to be re-derived from the bytes rather than refreshed in place.
    """
    index = Store(store_home)
    selected = [Path(root) for root in roots] if roots else default_roots()
    guard = [Path(root) for root in (protected if protected is not None else DEFAULT_PROTECTED_BACKUPS)]
    report = ScanReport(roots=[str(root) for root in selected],
                        missing_roots=[str(root) for root in selected if not root.exists()])
    roms = recent_roms()
    with index.session() as connection:
        for root in selected:
            if not root.exists():
                continue
            index.note_root(root, connection)
            for path in iter_candidates(root):
                _index_one(index, connection, path, root, guard, roms, verify, report, rehash)
        connection.commit()
    return report


def _index_one(index: Store, connection, path: Path, root: Path, protected: list[Path],
               roms: dict[Path, str], verify: bool, report: ScanReport,
               rehash: bool = False) -> None:
    try:
        stat = path.stat()
    except OSError:
        return
    known = connection.execute(
        "SELECT sha256, mtime, size FROM sources WHERE path = ?", (str(path),)
    ).fetchone()
    unchanged = (
        known is not None
        and not rehash
        and fingerprint(known["size"], known["mtime"]) == fingerprint(stat.st_size, stat.st_mtime)
    )
    if verify:
        # The fingerprint is not a verification of the bytes, so verify hashes
        # every indexed source whatever its size and mtime say, and changes
        # nothing: it re-hashes, reports drift and never repairs.
        if known is None:
            return
        digest = sha256_of(path)
        report.rehashed += 1
        if known["sha256"] != digest:
            report.changed.append({"path": str(path), "indexed": known["sha256"], "found": digest})
        return
    if unchanged:
        # Same file, so the digest stands; kind, geometry and provenance are
        # re-derived, because each is a reading of the file and the rules rather
        # than of the clock, and a re-scan must never re-hash the corpus. A copy
        # in the store's own home is left as it is: its provenance is the
        # registration, which no rule can rediscover.
        report.unchanged += 1
        if not _is_within(path, index.home):
            index.refresh_entry(
                _entry_for(index, connection, path, known["sha256"], stat, root, protected, roms),
                connection,
            )
        return
    try:
        digest = sha256_of(path)
    except OSError:
        return
    report.rehashed += 1
    entry = _entry_for(index, connection, path, digest, stat, root, protected, roms)
    created = index.upsert_entry(entry, connection)
    index.add_source(digest, Source(path=str(path), root=str(root), mtime=stat.st_mtime,
                                    size=stat.st_size, seen_at=utc_now()), connection)
    if created:
        report.new += 1
    else:
        report.updated += 1


def _entry_for(index: Store, connection, path: Path, digest: str,
               stat: os.stat_result, root: Path, protected: list[Path],
               roms: dict[Path, str]) -> Entry:
    with path.open("rb") as handle:
        head = handle.read(sniff.SIGNATURE_LEN + 8)
    chunks = sniff.png_chunk_names(path) if head.startswith(sniff.PNG_SIGNATURE) else frozenset()
    kind = sniff.sniff(head, stat.st_size, path.suffix, chunks)
    provenance = resolve_provenance(path, digest, stat.st_size, [root], protected, roms)
    known_notes = connection.execute(
        "SELECT notes, geometry FROM entries WHERE sha256 = ?", (digest,)
    ).fetchone()
    remembered = known_notes["geometry"] if known_notes else ""
    game, evidence, slot_rows = _game_and_slots(path, stat.st_size, kind, remembered, roms)
    return Entry(
        sha256=digest, size=stat.st_size, kind=kind.kind, kind_evidence=kind.evidence,
        misnamed=kind.misnamed, game=game, geometry=game if game != "UNKNOWN" else "",
        game_evidence=evidence, provenance=provenance.provenance,
        provenance_evidence=provenance.evidence, first_seen=utc_now(),
        notes=known_notes["notes"] if known_notes else "", slots=slot_rows,
    )


def game_by_name(name: str) -> str | None:
    """The title a filename names, from the same strings the emulator records.

    A ROM name is evidence about the save that sits beside it, so it counts; a
    medium size that two titles share is not evidence and is used only when it
    identifies one title on its own.
    """
    return geometry.game_by_name(name)


def _game_and_slots(path: Path, size: int, kind, remembered: str = "",
                    roms: dict[Path, str] | None = None) -> tuple[str, str, list[dict]]:
    """Owning game and per-slot validity, from the per-title geometry table.

    `remembered` is the geometry this digest was already assigned, and `roms` the
    emulator's own recent list. Both matter because two titles share the
    8,192-byte medium: a save named `v3.sav` names no title, so its sibling image
    is the next best evidence, and dropping a layout the index already holds
    would erase what an earlier reading found.
    """
    if kind.kind in (sniff.unknown_state, sniff.savestate):
        return ("UNKNOWN",
                "the extension says state; no verified savestate header exists, so no game is"
                " claimed from the file",
                [])
    game = game_by_name(path.stem)
    note = ""
    if game is None:
        # A ROM the emulator recorded, sitting beside this save under the same
        # stem, names the title the save belongs to.
        rom = sibling_rom(path, roms)
        if rom is not None:
            game = game_by_name(rom.stem)
            if game is not None:
                note = f"; the title comes from the sibling image {rom.name}"
    if game is None:
        by_size = geometry.geometry_by_size(size)
        game = by_size.game if by_size is not None else None
        if game is None:
            # Two titles can share a medium size, so ask the bytes: the layout
            # whose slot 0 validates is the one this image was written with.
            by_checksum = geometry.game_by_checksum(path.read_bytes())
            if by_checksum is not None:
                game = by_checksum
                note = ("; the title is the layout this image validates under, chosen from the"
                        " titles that share the medium size")
        if game is None and remembered and geometry.geometry_for(remembered) is not None:
            game = remembered
            note = ("; the layout was assigned in an earlier scan and the medium size matches more"
                    " than one title")
    if game is None:
        return ("UNKNOWN",
                f"no geometry is proven for a {size}-byte image, no title names this file, and more"
                " than one title claims this medium size, so no game is claimed",
                [])
    layout = geometry.geometry_for(game)
    slots = geometry.slots(path.read_bytes(), game)
    rows = [
        {
            "slot_index": slot.slot_index,
            "code_occupancy_bit": slot.code_occupancy_bit,
            "erased_all_ff": slot.erased_all_ff,
            "payload_len": slot.payload_len,
            "checksum_ok": slot.checksum_ok,
            "checksum_stored": slot.checksum_stored,
            "checksum_computed": slot.checksum_computed,
            "integrity_field_kind": slot.integrity_field_kind,
            "header_written": slot.header_written,
            "transform_scope": slot.transform_scope,
        }
        for slot in slots
    ]
    return (game,
            f"{layout.medium_size}-byte medium, slot k at {layout.slot_base:#x} + k*"
            f"{layout.slot_stride:#x}, payload {layout.payload_len:#x} de-swizzled, integrity"
            f" {layout.checksum_kind}, transform_scope={layout.transform_scope}; "
            f"{layout.evidence}{note}",
            rows)


# -- register -----------------------------------------------------------------


def register(store_home: Path | None, path: Path, note: str, force: bool = False) -> dict:
    """Copy a file into the owner inbox, record the note, leave the original.

    The entry must already be indexed, so the copy carries the same digest the
    index already holds. If it is not, the answer is to scan the file's root
    first rather than to invent an entry with no kind and no geometry.

    A known staged blank is refused: it is a tool's scratch pattern, and marking
    it as the owner's would be a false statement about a file no owner chose.
    `force` records it anyway, for an owner who really did keep one.
    """
    index = Store(store_home)
    source = Path(path)
    if not source.is_file():
        raise CatalogueError(f"not a file: {source}")
    digest = sha256_of(source)
    if digest in KNOWN_BLANK_DIGESTS and not force:
        raise CatalogueError(
            f"{source} is a known staged blank ({KNOWN_BLANK_DIGESTS[digest]}); refusing to record"
            " it as the owner's, pass --force to override"
        )
    with index.session() as connection:
        known = connection.execute(
            "SELECT sha256 FROM entries WHERE sha256 = ?", (digest,)
        ).fetchone()
        if known is None:
            raise CatalogueError(
                f"{source} is not indexed; scan its root first so the entry carries its kind,"
                " geometry and provenance"
            )
        owner = index.owner_dir
        owner.mkdir(parents=True, exist_ok=True)
        _refuse_outside_home(index, owner)
        target = owner / f"{digest[:16]}-{source.name}"
        index.refuse_write(target, connection, allowed=owner)
        copied = False
        if not target.exists():
            import shutil

            shutil.copy2(source, target)
            copied = True
        if sha256_of(target) != digest:
            raise CatalogueError(f"inbox copy does not match the source digest: {target}")
        record = {
            "sha256": digest, "original": str(source), "inbox": str(target),
            "source_name": source.name, "note": note, "registered_at": utc_now(),
            "size": source.stat().st_size,
        }
        # The registration is the strongest evidence the catalogue can hold: the
        # owner said what this file is, in their own words.
        index.add_source(digest, Source(path=str(target), root=str(owner),
                                        mtime=target.stat().st_mtime, size=target.stat().st_size,
                                        seen_at=utc_now()), connection)
        connection.execute(
            "UPDATE entries SET provenance = 'OWNER', provenance_evidence = ?, notes = ?"
            " WHERE sha256 = ?",
            (f"{store.REGISTRATION_EVIDENCE_PREFIX}{record['registered_at']} from {source}: {note}",
             note, digest),
        )
        log_path = index.log(record)
        connection.commit()
    return {**record, "copied": copied, "log": str(log_path)}


def _refuse_outside_home(index: Store, target: Path) -> None:
    if not _is_within(target, index.home):
        raise CatalogueError(f"refusing to write outside the catalogue home: {target}")


# -- record-run ---------------------------------------------------------------


def record_run(store_home: Path | None, run_dir: Path, tool: str, label: str | None) -> dict:
    """A launcher's one call: what it staged, by digest, into the store."""
    index = Store(store_home)
    run_dir = Path(run_dir)
    manifest = run_dir / "inputs.json"
    if not manifest.is_file():
        raise CatalogueError(f"no run manifest at {manifest}")
    try:
        # utf-8-sig because the launchers write this file with PowerShell's
        # `Set-Content -Encoding utf8`, which emits a byte-order mark on this
        # machine and would otherwise refuse every real run manifest.
        document = json.loads(manifest.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as error:
        raise CatalogueError(f"cannot read {manifest}: {error}") from error
    if not isinstance(document, dict):
        raise CatalogueError(f"{manifest} is not a JSON object")
    record = {
        "run_dir": str(run_dir),
        "tool": tool,
        "label": str(label or document.get("label") or run_dir.name),
        "rom_sha256": _digest(document.get("rom_sha256")),
        "save_sha256": _digest(document.get("save_sha256")),
        "state_sha256": _digest(document.get("state_sha256")),
    }
    with index.session() as connection:
        index.record_run(connection, record)
        connection.commit()
    return record


def _digest(value) -> str | None:
    return str(value).upper() if value else None
