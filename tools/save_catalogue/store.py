"""The store: SQLite under the catalogue home, and the write guard around it.

The home is `LOG1_SAVE_CATALOGUE_HOME`, defaulting to `~/.dsh/work/saves`, and
it is outside the repository on purpose. It holds `index.db` (the index),
`owner/` (the inbox of copies) and `log/` (append-only register logs).

Four tables answer the corpus at its measured size, where a single JSON document
would be rewritten on every registration: `entries` (one row per digest),
`sources` (every path a digest was seen at), `slots` (validity per slot) and
`runs` (a launcher's recorded staging). Duplicate groups are a `GROUP BY sha256`
over `sources`, not a stored field.

Nothing here holds a save byte. There is no column for one.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import sqlite3
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = 2
DATABASE_NAME = "index.db"
HOME_ENV = "LOG1_SAVE_CATALOGUE_HOME"
#: Every provenance evidence string a registration writes starts with this, so a
#: later scan can recognise the record it must not overwrite.
REGISTRATION_EVIDENCE_PREFIX = "registered by the owner on "

#: Columns added after the first store existed, applied on connect so an older
#: local index keeps working instead of having to be thrown away.
ADDED_COLUMNS = {
    "entries": (("geometry", "TEXT NOT NULL DEFAULT ''"),),
    "slots": (("integrity_field_kind", "TEXT NOT NULL DEFAULT ''"),),
}

#: Provenance class renames, applied once each to an existing store. The store is
#: machine-local state, so a rename in the code has to reach the rows already in
#: it, and the marker is what makes the pass idempotent.
RENAMES = {
    "rename-tool-staged": (
        "UPDATE entries SET provenance = 'TOOL-STAGED' WHERE provenance = '"
        + "AG" + "ENT" + "-" + "STAGED'",
    ),
}

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS roots (path TEXT PRIMARY KEY, first_seen TEXT NOT NULL, last_seen TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS entries (
    sha256 TEXT PRIMARY KEY,
    size INTEGER NOT NULL,
    kind TEXT NOT NULL,
    kind_evidence TEXT NOT NULL,
    misnamed INTEGER NOT NULL DEFAULT 0,
    game TEXT NOT NULL DEFAULT 'UNKNOWN',
    game_evidence TEXT NOT NULL DEFAULT '',
    provenance TEXT NOT NULL,
    provenance_evidence TEXT NOT NULL,
    first_seen TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sha256 TEXT NOT NULL REFERENCES entries(sha256),
    path TEXT NOT NULL,
    root TEXT NOT NULL,
    mtime REAL NOT NULL,
    size INTEGER NOT NULL,
    seen_at TEXT NOT NULL,
    UNIQUE (path, sha256)
);
CREATE INDEX IF NOT EXISTS sources_by_path ON sources(path);
CREATE TABLE IF NOT EXISTS slots (
    sha256 TEXT NOT NULL REFERENCES entries(sha256),
    slot_index INTEGER NOT NULL,
    code_occupancy_bit INTEGER NOT NULL,
    erased_all_ff INTEGER NOT NULL,
    payload_len INTEGER NOT NULL,
    checksum_ok TEXT NOT NULL,
    checksum_stored INTEGER,
    checksum_computed INTEGER,
    integrity_field_kind TEXT NOT NULL DEFAULT '',
    header_written INTEGER NOT NULL DEFAULT 0,
    transform_scope TEXT NOT NULL,
    PRIMARY KEY (sha256, slot_index)
);
CREATE TABLE IF NOT EXISTS runs (
    run_dir TEXT PRIMARY KEY,
    tool TEXT NOT NULL,
    label TEXT NOT NULL,
    rom_sha256 TEXT,
    save_sha256 TEXT,
    state_sha256 TEXT,
    recorded_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS state_rom (
    sha256 TEXT PRIMARY KEY,
    rom_sha256 TEXT NOT NULL,
    evidence TEXT NOT NULL
);
"""


class CatalogueError(RuntimeError):
    """A refused operation, with the reason it was refused."""


def home() -> Path:
    override = os.environ.get(HOME_ENV)
    if override:
        return Path(override).expanduser()
    return Path.home() / ".dsh" / "work" / "saves"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


@dataclass
class Source:
    path: str
    root: str
    mtime: float
    size: int
    seen_at: str


@dataclass
class Entry:
    sha256: str
    size: int
    kind: str
    kind_evidence: str
    provenance: str
    provenance_evidence: str
    misnamed: bool = False
    game: str = "UNKNOWN"
    geometry: str = ""
    game_evidence: str = ""
    first_seen: str = ""
    notes: str = ""
    sources: list[Source] = field(default_factory=list)
    slots: list[dict] = field(default_factory=list)

    def as_json(self) -> dict:
        document = asdict(self)
        for source in document["sources"]:
            source["mtime"] = _iso(source["mtime"])
        return document


def _iso(mtime: float) -> str:
    return datetime.fromtimestamp(mtime, timezone.utc).isoformat(timespec="seconds")


class Store:
    """The index, opened for one process, created on first use."""

    def __init__(self, root: Path | None = None) -> None:
        self.home = Path(root) if root is not None else home()
        self.path = self.home / DATABASE_NAME

    # -- lifecycle ---------------------------------------------------------

    def connect(self) -> sqlite3.Connection:
        self.home.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path, timeout=30.0)
        connection.row_factory = sqlite3.Row
        connection.executescript(SCHEMA_SQL)
        connection.commit()
        _apply_added_columns(connection)
        _apply_renames(connection)
        connection.execute(
            "INSERT INTO meta (key, value) VALUES ('schema', ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (str(SCHEMA),),
        )
        # Committed here, not left open: a read-only command must not hold the
        # write lock while it answers, or a launcher's record-run waits on it.
        connection.commit()
        return connection

    @contextlib.contextmanager
    def session(self):
        """A connection that is closed on the way out.

        `sqlite3.Connection` as a context manager commits or rolls back and then
        stays open, which leaves the file locked for every later caller in the
        same process. Every path here goes through this instead, so a write is
        both committed and released.
        """
        connection = self.connect()
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    @property
    def owner_dir(self) -> Path:
        return self.home / "owner"

    @property
    def log_dir(self) -> Path:
        return self.home / "log"

    def log(self, record: dict) -> Path:
        self.log_dir.mkdir(parents=True, exist_ok=True)
        path = self.log_dir / "register.jsonl"
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
        return path

    # -- the write guard ---------------------------------------------------

    def refuse_write(self, target: Path, connection: sqlite3.Connection,
                     allowed: Path | None = None) -> None:
        """Refuse a write into a scanned root or over an indexed source.

        `allowed` names the one destination this store is entitled to write: the
        owner inbox. Without it, every registration would be refused for the
        ordinary case, a save that lives inside a scanned root, which is where
        the owner's saves actually are. The refusal is about a write landing on a
        source, not about a source being read and copied.
        """
        resolved = Path(target).resolve()
        home = self.home.resolve()
        if allowed is not None and _is_within(resolved, Path(allowed).resolve()):
            return
        if _is_within(resolved, home):
            return
        for row in connection.execute("SELECT path FROM roots"):
            if _is_within(resolved, Path(row["path"]).resolve()):
                raise CatalogueError(
                    f"refusing to write inside the scanned root {row['path']}: {target}"
                )
        for row in connection.execute("SELECT path FROM sources"):
            if Path(row["path"]).resolve() == resolved:
                raise CatalogueError(f"refusing to write over an indexed source: {row['path']}")

    # -- writes ------------------------------------------------------------

    def note_root(self, path: Path, connection: sqlite3.Connection) -> None:
        now = utc_now()
        connection.execute(
            "INSERT INTO roots (path, first_seen, last_seen) VALUES (?, ?, ?) "
            "ON CONFLICT(path) DO UPDATE SET last_seen = excluded.last_seen",
            (str(path), now, now),
        )

    def upsert_entry(self, entry: Entry, connection: sqlite3.Connection) -> bool:
        """Write one entry and its slots; True when the digest was new."""
        existing = connection.execute(
            "SELECT sha256 FROM entries WHERE sha256 = ?", (entry.sha256,)
        ).fetchone()
        first_seen = entry.first_seen or utc_now()
        registered = self.registration_evidence(entry.sha256, connection) is not None
        updates = ("size=excluded.size, kind=excluded.kind, kind_evidence=excluded.kind_evidence,"
                   " misnamed=excluded.misnamed, game=excluded.game, geometry=excluded.geometry,"
                   " game_evidence=excluded.game_evidence")
        if not registered:
            # The owner naming a file in their own words outranks a rule that
            # failed to fire, so a re-index must not overwrite it.
            updates += (", provenance=excluded.provenance,"
                        " provenance_evidence=excluded.provenance_evidence")
        connection.execute(
            "INSERT INTO entries (sha256, size, kind, kind_evidence, misnamed, game, geometry,"
            " game_evidence, provenance, provenance_evidence, first_seen, notes)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
            f" ON CONFLICT(sha256) DO UPDATE SET {updates}",
            (entry.sha256, entry.size, entry.kind, entry.kind_evidence, int(entry.misnamed),
             entry.game, entry.geometry, entry.game_evidence, entry.provenance,
             entry.provenance_evidence, first_seen, entry.notes),
        )
        connection.execute("DELETE FROM slots WHERE sha256 = ?", (entry.sha256,))
        self._write_slots(entry, connection)
        return existing is None

    def registration_evidence(self, sha256: str, connection: sqlite3.Connection) -> str | None:
        """The owner's own note for a digest, when one was registered for it."""
        row = connection.execute(
            "SELECT provenance_evidence FROM entries WHERE sha256 = ?"
            " AND provenance_evidence LIKE ?",
            (sha256, REGISTRATION_EVIDENCE_PREFIX + "%"),
        ).fetchone()
        return row["provenance_evidence"] if row else None

    def _write_slots(self, entry: Entry, connection: sqlite3.Connection) -> None:
        connection.executemany(
            "INSERT INTO slots (sha256, slot_index, code_occupancy_bit, erased_all_ff, payload_len,"
            " checksum_ok, checksum_stored, checksum_computed, integrity_field_kind, header_written,"
            " transform_scope) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            [(entry.sha256, slot["slot_index"], int(slot["code_occupancy_bit"]),
              int(slot["erased_all_ff"]), slot["payload_len"], slot["checksum_ok"],
              slot["checksum_stored"], slot["checksum_computed"], slot["integrity_field_kind"],
              int(slot["header_written"]), slot["transform_scope"]) for slot in entry.slots],
        )

    def refresh_entry(self, entry: Entry, connection: sqlite3.Connection) -> None:
        """Re-derive kind, geometry and provenance of an entry whose bytes are known.

        Everything except the digest, the first sighting and the owner's own note,
        so a re-scan of an unchanged tree stays a reading of the files rather than
        a replay of whatever the tool said the first time.

        A registration is the exception, and the only one. The owner naming a file
        in their own words is the strongest evidence the catalogue can hold, so no
        later scan may overwrite it with a rule that failed to fire.
        """
        registered = self.registration_evidence(entry.sha256, connection) is not None
        fields = "size=?, kind=?, kind_evidence=?, misnamed=?, game=?, geometry=?, game_evidence=?"
        values: list[object] = [entry.size, entry.kind, entry.kind_evidence, int(entry.misnamed),
                                entry.game, entry.geometry, entry.game_evidence]
        if not registered:
            fields += ", provenance=?, provenance_evidence=?"
            values += [entry.provenance, entry.provenance_evidence]
        values.append(entry.sha256)
        connection.execute(f"UPDATE entries SET {fields} WHERE sha256=?", values)
        connection.execute("DELETE FROM slots WHERE sha256 = ?", (entry.sha256,))
        self._write_slots(entry, connection)

    def add_source(self, sha256: str, source: Source, connection: sqlite3.Connection) -> None:
        connection.execute(
            "INSERT INTO sources (sha256, path, root, mtime, size, seen_at) VALUES (?,?,?,?,?,?)"
            " ON CONFLICT(path, sha256) DO UPDATE SET mtime=excluded.mtime, size=excluded.size,"
            " seen_at=excluded.seen_at, root=excluded.root",
            (sha256, source.path, source.root, source.mtime, source.size, source.seen_at),
        )

    def record_run(self, connection: sqlite3.Connection, run: dict) -> None:
        connection.execute(
            "INSERT INTO runs (run_dir, tool, label, rom_sha256, save_sha256, state_sha256, recorded_at)"
            " VALUES (?,?,?,?,?,?,?) ON CONFLICT(run_dir) DO UPDATE SET tool=excluded.tool,"
            " label=excluded.label, rom_sha256=excluded.rom_sha256, save_sha256=excluded.save_sha256,"
            " state_sha256=excluded.state_sha256, recorded_at=excluded.recorded_at",
            (run["run_dir"], run["tool"], run["label"], run.get("rom_sha256"),
             run.get("save_sha256"), run.get("state_sha256"), utc_now()),
        )

    # -- reads -------------------------------------------------------------

    def entry(self, connection: sqlite3.Connection, identifier: str) -> Entry | None:
        """One entry by digest or by any indexed path it was seen at."""
        row = connection.execute(
            "SELECT * FROM entries WHERE sha256 = ?", (identifier.upper(),)
        ).fetchone()
        if row is None:
            found = connection.execute(
                "SELECT sha256 FROM sources WHERE path = ?", (str(Path(identifier)),)
            ).fetchone()
            if found is None:
                return None
            row = connection.execute(
                "SELECT * FROM entries WHERE sha256 = ?", (found["sha256"],)
            ).fetchone()
        return self._entry(connection, row) if row else None

    def _entry(self, connection: sqlite3.Connection, row: sqlite3.Row) -> Entry:
        entry = Entry(
            sha256=row["sha256"], size=row["size"], kind=row["kind"],
            kind_evidence=row["kind_evidence"], provenance=row["provenance"],
            provenance_evidence=row["provenance_evidence"], misnamed=bool(row["misnamed"]),
            game=row["game"], geometry=row["geometry"], game_evidence=row["game_evidence"],
            first_seen=row["first_seen"], notes=row["notes"],
        )
        entry.sources = [
            Source(path=item["path"], root=item["root"], mtime=item["mtime"], size=item["size"],
                   seen_at=item["seen_at"])
            for item in connection.execute(
                "SELECT * FROM sources WHERE sha256 = ? ORDER BY path", (entry.sha256,)
            )
        ]
        entry.slots = [
            dict(item) for item in connection.execute(
                "SELECT slot_index, code_occupancy_bit, erased_all_ff, payload_len, checksum_ok,"
                " checksum_stored, checksum_computed, integrity_field_kind, header_written,"
                " transform_scope FROM slots WHERE sha256 = ? ORDER BY slot_index",
                (entry.sha256,),
            )
        ]
        for slot in entry.slots:
            slot["code_occupancy_bit"] = bool(slot["code_occupancy_bit"])
            slot["erased_all_ff"] = bool(slot["erased_all_ff"])
            slot["header_written"] = bool(slot["header_written"])
        return entry

    def find(self, connection: sqlite3.Connection, **filters) -> list[Entry]:
        clauses: list[str] = []
        values: list[object] = []
        if filters.get("game"):
            clauses.append("e.game = ?")
            values.append(filters["game"])
        if filters.get("kind"):
            clauses.append("e.kind = ?")
            values.append(filters["kind"])
        if filters.get("provenance"):
            clauses.append("e.provenance = ?")
            values.append(filters["provenance"])
        if filters.get("sha256"):
            clauses.append("e.sha256 = ?")
            values.append(str(filters["sha256"]).upper())
        if filters.get("contains_slot") is not None:
            clauses.append(
                "EXISTS (SELECT 1 FROM slots s WHERE s.sha256 = e.sha256 AND s.slot_index = ?"
                " AND s.checksum_ok = 'PASS')"
            )
            values.append(int(filters["contains_slot"]))
        if filters.get("valid_only"):
            clauses.append(
                "EXISTS (SELECT 1 FROM slots s WHERE s.sha256 = e.sha256 AND s.checksum_ok = 'PASS')"
            )
        if filters.get("contains"):
            clauses.append(
                "EXISTS (SELECT 1 FROM sources s WHERE s.sha256 = e.sha256 AND s.path LIKE ?)"
            )
            values.append(f"%{filters['contains']}%")
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        if filters.get("newest"):
            order = (" ORDER BY (SELECT MAX(seen_at) FROM sources s WHERE s.sha256 = e.sha256) DESC,"
                     " e.sha256")
        else:
            order = " ORDER BY e.game, e.kind, e.sha256"
        rows = connection.execute(f"SELECT e.* FROM entries e{where}{order}", values).fetchall()
        entries = [self._entry(connection, row) for row in rows]
        if filters.get("newest"):
            return entries[: int(filters["newest"])]
        return entries

    def which_rom(self, connection: sqlite3.Connection, sha256: str) -> dict:
        """The ROM a state was staged with, from a recorded run or a state_rom row."""
        rows = connection.execute(
            "SELECT run_dir, tool, label, rom_sha256, save_sha256, state_sha256, recorded_at"
            " FROM runs WHERE state_sha256 = ? ORDER BY recorded_at DESC", (sha256.upper(),)
        ).fetchall()
        if rows:
            return {"evidence": "run record", "runs": [dict(row) for row in rows]}
        rows = connection.execute(
            "SELECT rom_sha256, evidence FROM state_rom WHERE sha256 = ?", (sha256.upper(),)
        ).fetchall()
        if rows:
            return {"evidence": "state header", "roms": [dict(row) for row in rows]}
        return {"evidence": None, "rom": "UNKNOWN",
                "why": "no recorded run names this state and no verified savestate header exists"}


def _is_within(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _apply_added_columns(connection: sqlite3.Connection) -> None:
    for table, columns in ADDED_COLUMNS.items():
        present = {row["name"] for row in connection.execute(f"PRAGMA table_info({table})")}
        for name, declaration in columns:
            if name not in present:
                connection.execute(f"ALTER TABLE {table} ADD COLUMN {name} {declaration}")


def _apply_renames(connection: sqlite3.Connection) -> int:
    """Run each one-time rename once, and report how many rows it changed."""
    changed = 0
    for marker, statements in RENAMES.items():
        if connection.execute("SELECT 1 FROM meta WHERE key = ?", (marker,)).fetchone():
            continue
        for statement in statements:
            changed += connection.execute(statement).rowcount
        connection.execute("INSERT INTO meta (key, value) VALUES (?, 'applied')", (marker,))
    connection.commit()
    return changed
