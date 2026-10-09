"""Rewrite the Tulma and Bulma lines in the friend image, in the right speakers' slots.

WHY A DIRECT SPAN WRITE. The dialogue containers this image's table names (selectors 0..5) are
Webfoot containers of kind 0, the STORED form: the payload after the 8-byte header is the
decoded stream itself, and `webfoot_lz.pack` cannot emit kind 0 at all. So the honest route is
byte-exact: the new text replaces the old inside the stored payload, with no re-encode.

WHY THE TWO RECORDS ARE LAID OUT TOGETHER. A record's length lives in its handle, not in a
terminator: the records here are back-to-back. Bulma's new line needs 128 bytes where her span
holds 112, so it cannot grow in place. Her record and Tulma's are contiguous (112 + 138 = 250
bytes) and the two replacements need 220, so the pair is re-laid out inside their own combined
region and both handles are updated to match. Nothing else in the container moves, which is
what keeps every other record's absolute offsets valid. This is why the writer refuses when
the records are not adjacent or when the pair has no room: either case would need a container
re-layout, which is a different mechanism.

WHY THE SLOT MATTERS MORE THAN THE ORDER. Each record is addressed by its own handle, so the
speaker of a line is whichever scene asks for that record. Keeping each speaker's new wording
in that speaker's own slot is therefore the whole change; the physical order in the container
is preserved as it was.

WHAT THIS REFUSES. A base whose digest is not the expected one, a span that does not decode to
the wording it is supposed to replace, records that are not adjacent, a pair with too little
room, a replacement carrying a control unit, a container that is not the stored form, and a
handle site whose stored word is not the one being replaced.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.webfoot.compressed_dialogue import dialogue_record_inventory  # noqa: E402
from tools.webfoot.formats import webfoot_lz as wl  # noqa: E402
from tools.webfoot.handles import pack_handle  # noqa: E402
from tools.webfoot.write import WriteError, ensure_not_source_alias  # noqa: E402

#: The literal word that names this image's dialogue container table. On a post-splice image
#: the retail literal at 0x7B5B64 no longer points at the live table; this one does.
TABLE_LITERAL = 0x123CC
ROM_BASE = 0x08000000
CONTAINER_HEADER = 8
SELECTOR = 2

#: The two slots, each with the wording it holds now and the wording it must hold. The
#: speaker is which slot the line lives in, so a slot is never lent to the other character.
TARGETS = (
    {
        "speaker": "bulma",
        "decoded_start": 60182,
        "decoded_length": 112,
        "old_text": "Isn't this wonderful? Our family is back together again!",
        "new_text": "Look at how mad Tulma is! Do you think I went too far this time?",
    },
    {
        "speaker": "tulma",
        "decoded_start": 60294,
        "decoded_length": 138,
        "old_text": ("It's great that \ue000mc\ue001 is back. "
                     "Everyone seems so happy to be together."),
        "new_text": "That bitch! She knew I was going to wear this!",
    },
)
#: The engine's break-point unit, used to fill the rest of the combined region.
SPACE = 0x0020


class TulmaDialogueError(ValueError):
    """Raised when a guard refuses rather than writing an unproven byte."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _container_file_offset(image: bytes) -> int:
    table = struct.unpack_from("<I", image, TABLE_LITERAL)[0] - ROM_BASE
    word = table + SELECTOR * 4
    pointer = struct.unpack_from("<I", image, word)[0]
    if not ROM_BASE <= pointer < ROM_BASE + len(image):
        raise TulmaDialogueError(f"selector {SELECTOR} is not a ROM pointer ({pointer:#010x})")
    return pointer - ROM_BASE


def _stored_payload(image: bytes, offset: int) -> bytes:
    """The container's decoded stream, refusing any form that is not stored verbatim."""
    container = wl.unpack(image, offset)
    payload = image[offset + CONTAINER_HEADER: offset + CONTAINER_HEADER + container.declared_size]
    if bytes(container.data) != payload:
        raise TulmaDialogueError(
            f"the container at {offset:#x} is kind {container.kind} and its payload is not "
            "stored verbatim, so an in-place edit is not proven for it"
        )
    return payload


def plan(image: bytes) -> dict:
    """The region to rewrite and the handle words to update, each verified against the base."""
    offset = _container_file_offset(image)
    payload = _stored_payload(image, offset)
    base = offset + CONTAINER_HEADER

    for target in TARGETS:
        span = payload[target["decoded_start"]:
                      target["decoded_start"] + target["decoded_length"]]
        if span.decode("utf-16le") != target["old_text"]:
            raise TulmaDialogueError(
                f"{target['speaker']}: the span at {target['decoded_start']} does not hold the "
                "wording this rewrite replaces"
            )
        if any(ord(character) < 0x20 for character in target["new_text"]):
            raise TulmaDialogueError(
                f"{target['speaker']}: the replacement carries a control unit"
            )

    ordered = sorted(TARGETS, key=lambda t: t["decoded_start"])
    for left, right in zip(ordered, ordered[1:]):
        if left["decoded_start"] + left["decoded_length"] != right["decoded_start"]:
            raise TulmaDialogueError(
                f"{left['speaker']} and {right['speaker']} are not adjacent; growing one would "
                "move every record after it, which this writer does not do"
            )
    region_start = ordered[0]["decoded_start"]
    region_end = ordered[-1]["decoded_start"] + ordered[-1]["decoded_length"]
    region_bytes = region_end - region_start
    needed = sum(len(t["new_text"].encode("utf-16le")) for t in ordered)
    if needed > region_bytes:
        raise TulmaDialogueError(
            f"the pair needs {needed} bytes and its region holds {region_bytes}; a container "
            "re-layout is a different mechanism"
        )

    records = {f"{r.handle.decoded_start}:{r.handle.decoded_length}": r
               for r in dialogue_record_inventory(image, SELECTOR, len(payload))}
    region = bytearray()
    handles = []
    cursor = region_start
    for target in ordered:
        text = target["new_text"].encode("utf-16le")
        old_handle = pack_handle(SELECTOR, target["decoded_start"], target["decoded_length"])
        record = records.get(f"{target['decoded_start']}:{target['decoded_length']}")
        if record is None:
            raise TulmaDialogueError(
                f"{target['speaker']}: no record carries ({target['decoded_start']}, "
                f"{target['decoded_length']})"
            )
        if not record.sites:
            raise TulmaDialogueError(
                f"{target['speaker']}: the record is not named by any word, so nothing would "
                "reach the replacement"
            )
        for site in record.sites:
            if struct.unpack_from("<I", image, site)[0] != old_handle:
                raise TulmaDialogueError(f"the handle word at {site:#x} is not the one replaced")
        handles.append({
            "speaker": target["speaker"],
            "old_handle": old_handle,
            "old_handle_hex": f"0x{old_handle:08X}",
            "new_start": cursor,
            "new_length": len(text),
            "new_handle": pack_handle(SELECTOR, cursor, len(text)),
            "sites": list(record.sites),
        })
        region.extend(text)
        cursor += len(text)
    region.extend(SPACE.to_bytes(2, "little") * ((region_bytes - len(region)) // 2))
    if len(region) != region_bytes:
        raise TulmaDialogueError("the padded region does not fill the region exactly")

    return {
        "container_offset": offset,
        "payload_offset": base,
        "region_start": region_start,
        "region_bytes": region_bytes,
        "region_file_offset": base + region_start,
        "region": bytes(region),
        "handles": handles,
    }


def apply(image: bytes, planned: dict) -> bytes:
    out = bytearray(image)
    at = planned["region_file_offset"]
    length = len(planned["region"])
    out[at:at + length] = planned["region"]
    for handle in planned["handles"]:
        for site in handle["sites"]:
            current = struct.unpack_from("<I", out, site)[0]
            if current != handle["old_handle"]:
                raise TulmaDialogueError(f"the handle word at {site:#x} moved under this write")
            struct.pack_into("<I", out, site, handle["new_handle"])
    return bytes(out)


def verify(base: bytes, out: bytes, planned: dict) -> dict:
    """Reopen the output and require the new wording, the new handles, and nothing else."""
    offset = _container_file_offset(out)
    payload = _stored_payload(out, offset)
    records = {f"{r.handle.decoded_start}:{r.handle.decoded_length}": r
               for r in dialogue_record_inventory(out, SELECTOR, len(payload))}
    read_back = {}
    for handle in planned["handles"]:
        key = f"{handle['new_start']}:{handle['new_length']}"
        record = records.get(key)
        if record is None:
            raise TulmaDialogueError(f"the output carries no record for {key}")
        text = payload[handle["new_start"]:handle["new_start"] + handle["new_length"]]
        read_back[handle["speaker"]] = text.decode("utf-16le")
        for old in TARGETS:
            if old["speaker"] == handle["speaker"] and text.decode("utf-16le") != old["new_text"]:
                raise TulmaDialogueError(f"{handle['speaker']}: the output does not read the new line")
    for target in TARGETS:
        if target["old_text"] in payload.decode("utf-16le"):
            raise TulmaDialogueError(f"{target['speaker']}: the old wording survives")

    before = _stored_payload(base, _container_file_offset(base))
    # Two coordinate spaces on purpose: the decoded payload is indexed from its own start, and
    # the image is indexed from the file. Mixing them is how a confinement check passes a
    # change it should have caught.
    payload_region = set(range(planned["region_start"],
                               planned["region_start"] + planned["region_bytes"]))
    image_region = set(range(planned["region_file_offset"],
                             planned["region_file_offset"] + planned["region_bytes"]))
    changed_outside_payload = [i for i in range(len(payload))
                               if payload[i] != before[i] and i not in payload_region]
    if changed_outside_payload:
        raise TulmaDialogueError(
            f"{len(changed_outside_payload)} decoded bytes changed outside the region"
        )
    # A handle is a 4-byte word, so the allowed bytes are the word, not just its first byte.
    handle_sites = {site + i for handle in planned["handles"]
                    for site in handle["sites"] for i in range(4)}
    image_diff = [i for i in range(len(out)) if out[i] != base[i]]
    stray = [i for i in image_diff if i not in image_region and i not in handle_sites]
    if stray:
        raise TulmaDialogueError(
            f"{len(stray)} image bytes changed outside the region and the handle words; "
            f"first at {stray[0]:#x}"
        )
    return {
        "read_back": read_back,
        "image_bytes_changed": len(image_diff),
        "image_bytes_changed_in_region": len(
            [i for i in image_diff if i in image_region]),
        "handle_words_changed": len(
            [i for i in image_diff if i in handle_sites]),
        "container_packed_size_before": wl.unpack(base, offset).packed_size,
        "container_packed_size_after": wl.unpack(out, offset).packed_size,
    }


def _write_staged(path: Path, data: bytes) -> None:
    """Write through a sibling temporary file, then rename, so a partial write is visible.

    The precedent is `apply_friend_v3_text_edits.py`: the output appears whole or not at all,
    so a reader never sees a half-written image.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".",
                                     suffix=".partial", delete=False) as handle:
        staged = Path(handle.name)
        try:
            handle.write(data)
        except BaseException:
            handle.close()
            staged.unlink(missing_ok=True)
            raise
    staged.replace(path)


def run(base_path: Path, expect_sha256: str, out_path: Path, report_path: Path) -> dict:
    # First and total, before anything is read for writing: a source is an input on every path
    # and an output on none, and a hard link of the canonical image is the same file.
    ensure_not_source_alias(base_path, out_path)
    ensure_not_source_alias(base_path, report_path)
    ensure_not_source_alias(out_path, report_path)
    base = base_path.read_bytes()
    digest = sha256(base)
    if digest != expect_sha256.lower():
        raise TulmaDialogueError(
            f"{base_path} is {digest}, not the base this rewrite was proven against "
            f"({expect_sha256.lower()})"
        )
    planned = plan(base)
    out = apply(base, planned)
    report = {
        "ticket": "FRIEND-V3-TULMA-GRAPHICS-001 dialogue expansion (owner-authorized)",
        "base_path": str(base_path),
        "base_sha256": digest,
        "base_size": len(base),
        "output_path": str(out_path),
        "output_sha256": sha256(out),
        "output_size": len(out),
        "container_offset": planned["container_offset"],
        "region_start": planned["region_start"],
        "region_bytes": planned["region_bytes"],
        "region_file_offset": planned["region_file_offset"],
        "handles": planned["handles"],
        "speakers": [{"speaker": t["speaker"], "old_text": t["old_text"],
                      "new_text": t["new_text"]} for t in TARGETS],
        "verification": verify(base, out, planned),
    }
    _write_staged(out_path, out)
    _write_staged(report_path,
                  (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    if sha256(base_path.read_bytes()) != digest:
        raise TulmaDialogueError("the base image changed during the build")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", required=True, type=Path)
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        report = run(args.base, args.expect_sha256, args.out, args.report)
    except (TulmaDialogueError, WriteError) as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    print(f"output {report['output_sha256']}  {report['output_size']} bytes")
    for handle in report["handles"]:
        print(f"  {handle['speaker']:6s} handle {handle['old_handle_hex']} -> "
              f"0x{handle['new_handle']:08X} at {[hex(s) for s in handle['sites']]}")
    for speaker, text in report["verification"]["read_back"].items():
        print(f"  reads  {speaker:6s} {text!r}")
    print(f"verify {json.dumps({k: v for k, v in report['verification'].items() if k != 'read_back'}, sort_keys=True)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
