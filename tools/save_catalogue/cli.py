"""The catalogue CLI: one call per question, `--json` on every command.

`find`, `show`, `which-rom`, `diff`, `verify` and `register` are the owner's
commands. `scan` and `record-run` are the indexing ones: `scan` walks the roots,
`record-run` is the single call a launcher makes after it stages a save or a
state.

`diff` prints slot-level counts and offsets only, never bytes, and never a
decoded field.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import walk as scanning
from . import sniff, store
from .store import CatalogueError, Store, home


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--store", metavar="DIR",
                        help="catalogue home (default: the environment, then ~)")
    common.add_argument("--json", action="store_true", help="machine-readable output")
    parser = argparse.ArgumentParser(
        prog="tools.save_catalogue",
        description="Index every battery save and savestate on this machine.",
        parents=[common],
    )
    commands = parser.add_subparsers(dest="command", required=True)

    walk = commands.add_parser("scan", parents=[common],
                               help="index the roots; re-hash only what changed")
    walk.add_argument("--root", action="append", default=[], metavar="DIR",
                      help="a root to walk; repeatable, and the defaults apply when absent")
    walk.add_argument("--verify", action="store_true",
                      help="re-hash every indexed source and report drift")
    walk.add_argument("--rehash", action="store_true",
                      help="re-derive every file even where the fingerprint is unchanged")
    walk.add_argument("--protected", action="append", default=[], metavar="DIR",
                      help="a protected backup directory (read-only)")

    listing = commands.add_parser("find", parents=[common], help="query the index")
    listing.add_argument("--game")
    listing.add_argument("--kind", choices=sniff.KINDS)
    listing.add_argument("--provenance",
                         choices=("OWNER", "TOOL-STAGED", "DERIVED", "BACKUP", "UNKNOWN"))
    listing.add_argument("--valid-only", action="store_true")
    listing.add_argument("--newest", type=int, metavar="N")
    listing.add_argument("--contains-slot", type=int, metavar="K")
    listing.add_argument("--path-contains", metavar="TEXT")

    show = commands.add_parser("show", parents=[common], help="one entry by digest or by indexed path")
    show.add_argument("identifier")

    which = commands.add_parser("which-rom", parents=[common], help="the ROM a state was staged with")
    which.add_argument("state")

    diff = commands.add_parser("diff", parents=[common], help="slot-level comparison of two entries")
    diff.add_argument("first")
    diff.add_argument("second")

    verify = commands.add_parser("verify", parents=[common], help="re-hash indexed sources and report drift")
    verify.add_argument("--root", action="append", default=[], metavar="DIR")

    register = commands.add_parser("register", parents=[common], help="copy a file into the owner inbox")
    register.add_argument("path")
    register.add_argument("--note", required=True)
    register.add_argument("--force", action="store_true",
                          help="record even a known staged blank the tool staged itself")

    record = commands.add_parser("record-run", parents=[common], help="record a launcher's staged run")
    record.add_argument("--run-dir", required=True)
    record.add_argument("--tool", required=True)
    record.add_argument("--label")

    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    index = Store(Path(arguments.store) if arguments.store else None)
    try:
        document = _dispatch(arguments, index)
    except CatalogueError as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        return 2
    if arguments.json:
        json.dump(document, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        _render(document)
    return 0


def _dispatch(arguments, index: Store) -> dict:
    if arguments.command == "scan":
        roots = [Path(item) for item in arguments.root] or None
        protected = [Path(item) for item in arguments.protected] or None
        return scanning.scan(index.home, roots, arguments.verify, protected,
                             arguments.rehash).as_json()
    if arguments.command == "verify":
        roots = [Path(item) for item in arguments.root] or None
        return scanning.scan(index.home, roots, verify=True).as_json()
    if arguments.command == "register":
        return scanning.register(index.home, Path(arguments.path), arguments.note, arguments.force)
    if arguments.command == "record-run":
        return scanning.record_run(index.home, Path(arguments.run_dir), arguments.tool,
                                   arguments.label)
    with index.session() as connection:
        if arguments.command == "find":
            return {"entries": [item.as_json() for item in index.find(
                connection,
                game=arguments.game,
                kind=arguments.kind,
                provenance=arguments.provenance,
                valid_only=arguments.valid_only,
                newest=arguments.newest,
                contains_slot=arguments.contains_slot,
                contains=arguments.path_contains,
            )]}
        if arguments.command == "show":
            entry = index.entry(connection, arguments.identifier)
            if entry is None:
                raise CatalogueError(f"nothing indexed for {arguments.identifier}")
            return {"entry": entry.as_json()}
        if arguments.command == "which-rom":
            entry = index.entry(connection, arguments.state)
            digest = entry.sha256 if entry else arguments.state
            return {"state": digest, **index.which_rom(connection, digest)}
        if arguments.command == "diff":
            first = index.entry(connection, arguments.first)
            second = index.entry(connection, arguments.second)
            if first is None or second is None:
                missing = arguments.first if first is None else arguments.second
                raise CatalogueError(f"nothing indexed for {missing}")
            return _diff(first, second)
    raise CatalogueError(f"unknown command {arguments.command}")


def _diff(first, second) -> dict:
    """Slot-level: erased, checksum verdict and computed value. No bytes."""
    slots: list[dict] = []
    for left, right in zip(first.slots, second.slots):
        first_facts = {"erased_all_ff": left["erased_all_ff"], "checksum_ok": left["checksum_ok"],
                       "checksum_computed": left["checksum_computed"]}
        second_facts = {"erased_all_ff": right["erased_all_ff"], "checksum_ok": right["checksum_ok"],
                        "checksum_computed": right["checksum_computed"]}
        slots.append({
            "slot_index": left["slot_index"],
            "offset": _offset(left["slot_index"]),
            "last_byte_offset": _last_offset(left["slot_index"]),
            "first": first_facts,
            "second": second_facts,
            "differs": first_facts != second_facts,
        })
    return {
        "first": {"sha256": first.sha256, "size": first.size, "kind": first.kind},
        "second": {"sha256": second.sha256, "size": second.size, "kind": second.kind},
        "slots": slots,
        "differing_slots": [item["slot_index"] for item in slots if item["differs"]],
        "note": "counts and offsets only; no save byte is read out or printed",
    }


def _offset(slot_index: int) -> str:
    return hex(0x10 + slot_index * 0x8B0)


def _last_offset(slot_index: int) -> str:
    return hex(0x10 + (slot_index + 1) * 0x8B0 - 1)


def _render(document) -> None:
    if "roots" in document:
        body = document
        print(f"roots            : {len(body['roots'])}")
        for missing in body["missing_roots"]:
            print(f"  MISSING ROOT   : {missing}")
        print(f"new {body['new']}  updated {body['updated']}  unchanged {body['unchanged']}"
              f"  re-hashed {body['rehashed']}")
        for item in body["changed"]:
            print(f"  CHANGED        : {item['path']} indexed {item['indexed']} found {item['found']}")
        for item in body["problems"]:
            print(f"  PROBLEM        : {item['path']} {item['error']}")
        return
    if "entries" in document:
        for entry in document["entries"]:
            print(_line(entry))
        print(f"{len(document['entries'])} entry(ies)")
        return
    if "entry" in document:
        entry = document["entry"]
        print(_line(entry))
        print(f"  kind evidence  : {entry['kind_evidence']}")
        print(f"  game evidence  : {entry['game_evidence']}")
        print(f"  provenance     : {entry['provenance_evidence']}")
        for source in entry["sources"]:
            print(f"  source         : {source['path']} (mtime {source['mtime']})")
        for slot in entry["slots"]:
            print(f"  slot {slot['slot_index']}       : checksum_ok={slot['checksum_ok']}"
                  f" erased_all_ff={slot['erased_all_ff']}"
                  f" code_occupancy_bit={slot['code_occupancy_bit']}"
                  f" header_written={slot['header_written']}"
                  f" transform_scope={slot['transform_scope']}")
        return
    if "slots" in document:
        print(f"{document['first']['sha256']}  {document['first']['kind']}")
        print(f"{document['second']['sha256']}  {document['second']['kind']}")
        for slot in document["slots"]:
            print(f"  slot {slot['slot_index']} at {slot['offset']}:"
                  f" first={slot['first']} second={slot['second']} differs={slot['differs']}")
        print(f"differing slots: {document['differing_slots']}")
        return
    print(json.dumps(document, indent=2, sort_keys=True))


def _line(entry: dict) -> str:
    marks = {"PASS": "V", "CORRUPT": "C", "UNKNOWN": "."}
    slots = "".join(marks.get(slot["checksum_ok"], "?") for slot in entry["slots"]) or "-"
    return (f"{entry['sha256'][:16]}  {entry['kind']:<16} {entry['game']:<10}"
            f" {entry['provenance']:<12} slots={slots}  {entry['size']} B")


if __name__ == "__main__":
    raise SystemExit(main())
