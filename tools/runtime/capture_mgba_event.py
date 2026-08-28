"""Capture bounded, object-attributed mGBA breakpoint events.

The program connects to an already launched, GDB-halted mGBA process.  It is
the sole GDB owner: it installs the breakpoint and sends the first continue.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import time

from tools.runtime.mgba_capture import (
    CAPTURE_MAGIC,
    EWRAM_HI,
    EWRAM_LO,
    ROM_HI,
    ROM_LO,
    connect_capture_client,
    scan_aligned_ewram_pointers,
    write_capture_record,
)


def _u32(text: str) -> int:
    return int(text, 0)


def _register_index(text: str) -> int:
    lowered = text.lower()
    if not lowered.startswith("r"):
        raise argparse.ArgumentTypeError("dump register must be r0 through r12")
    try:
        index = int(lowered[1:])
    except ValueError as exc:
        raise argparse.ArgumentTypeError("dump register must be r0 through r12") from exc
    if not 0 <= index <= 12:
        raise argparse.ArgumentTypeError("dump register must be r0 through r12")
    return index


def _stack_length(text: str) -> int:
    length = int(text, 0)
    if length < 64 or length > 1024 or length % 4:
        raise argparse.ArgumentTypeError(
            "stack length must be a 4-byte multiple from 64 through 1024"
        )
    return length


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--breakpoint", type=_u32, default=None)
    parser.add_argument("--additional-breakpoint", type=_u32, action="append", default=[])
    parser.add_argument("--breakpoint-length", type=_u32, default=2)
    parser.add_argument("--dump-register", type=_register_index, default=1)
    parser.add_argument("--dump-length", type=_u32, default=0x240)
    parser.add_argument("--stack-length", type=_stack_length, default=64,
                        help="Bounded stack bytes used to derive ROM return candidates")
    parser.add_argument("--lr-filter", type=_u32, default=None,
                        help="Record only stops whose normalized LR matches this value")
    parser.add_argument("--dump-word0-filter", type=_u32, default=None,
                        help="Record only stops whose dump object starts with this u32")
    parser.add_argument("--primary-dump-word0-filter", type=_u32, default=None,
                        help="Apply a dump word-0 filter only at the primary breakpoint")
    parser.add_argument("--decrease-register", type=_register_index, default=None,
                        help="Record only when this register is below the compared live value")
    parser.add_argument("--compare-dump-offset", type=_u32, default=0,
                        help="Offset from dump object for --decrease-register comparison")
    parser.add_argument("--compare-length", type=_u32, default=4,
                        help="Comparison field width in bytes (1, 2, or 4)")
    parser.add_argument("--max-stops", type=int, default=20)
    parser.add_argument("--window-seconds", type=float, default=600.0)
    parser.add_argument("--stop-file", type=Path)
    parser.add_argument("--gameplay-tick-file", type=Path)
    parser.add_argument("--scan-ewram-pointers", action="store_true")
    parser.add_argument("--watchpoint", type=_u32, default=None,
                        help="Z2 write watchpoint address")
    parser.add_argument("--watchpoint-length", type=_u32, default=2,
                        help="Watchpoint byte length (default 2 for u16)")
    parser.add_argument("--read-address", type=_u32, default=None,
                        help="Optional address to read at each accepted stop")
    parser.add_argument("--read-length", type=_u32, default=2,
                        help="Bytes to read from read-address")
    return parser.parse_args()


def _is_readable_ewram(address: int, length: int) -> bool:
    return EWRAM_LO <= address and address + length <= EWRAM_HI


def _is_readable_work_ram(address: int, length: int) -> bool:
    return _is_readable_ewram(address, length) or (
        0x03000000 <= address and address + length <= 0x03008000
    )


def _resolve_output_dir(path: Path) -> Path:
    root = Path(__file__).resolve().parents[2]
    build_root = (root / "build").resolve()
    output_dir = path.resolve()
    if not output_dir.is_relative_to(build_root):
        raise ValueError("capture output directory must be under repository build/")
    return output_dir


def _resolve_gameplay_tick_file(path: Path | None, output_dir: Path) -> Path | None:
    if path is None:
        return None
    resolved = path.resolve()
    if resolved.parent != output_dir.parent or resolved.name != "frame-tick.txt":
        raise ValueError("gameplay tick file must be the run directory's frame-tick.txt")
    return resolved


def _read_gameplay_tick(path: Path | None) -> str:
    if path is None or not path.exists():
        return ""
    text = path.read_text(encoding="ascii").strip()
    if not text.isdecimal():
        return ""
    return text


def run_capture(args: argparse.Namespace) -> int:
    output_dir = _resolve_output_dir(args.output_dir)
    gameplay_tick_file = _resolve_gameplay_tick_file(args.gameplay_tick_file, output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    events_path = output_dir / "events.csv"
    dumps_path = output_dir / "dumps.wfcap"
    pointers_path = output_dir / "ewram-pointers.csv"
    manifest_path = output_dir / "capture.json"
    ready_path = output_dir / "capture-ready.txt"

    manifest = {
        "schema": 1,
        "breakpoint": f"0x{args.breakpoint:08X}" if args.breakpoint is not None else None,
        "breakpoints": [
            f"0x{address:08X}"
            for address in dict.fromkeys(
                ([args.breakpoint] if args.breakpoint is not None else [])
                + args.additional_breakpoint
            )
        ],
        "breakpoint_length": args.breakpoint_length,
        "dump_register": f"r{args.dump_register}",
        "dump_length": args.dump_length,
        "stack_length": args.stack_length,
        "lr_filter": f"0x{args.lr_filter & ~1:08X}" if args.lr_filter is not None else None,
        "dump_word0_filter": (
            f"0x{args.dump_word0_filter:08X}"
            if args.dump_word0_filter is not None else None
        ),
        "primary_dump_word0_filter": (
            f"0x{args.primary_dump_word0_filter:08X}"
            if args.primary_dump_word0_filter is not None else None
        ),
        "decrease_register": (
            f"r{args.decrease_register}"
            if args.decrease_register is not None else None
        ),
        "compare_dump_offset": args.compare_dump_offset,
        "compare_length": args.compare_length,
        "max_stops": args.max_stops,
        "window_seconds": args.window_seconds,
        "gameplay_tick_file": str(gameplay_tick_file) if gameplay_tick_file else None,
        "scan_ewram_pointers": args.scan_ewram_pointers,
        "watchpoint": f"0x{args.watchpoint:08X}" if args.watchpoint else None,
        "watchpoint_length": args.watchpoint_length if args.watchpoint else None,
        "read_address": f"0x{args.read_address:08X}" if args.read_address else None,
        "status": "starting",
        "stops": 0,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    client = connect_capture_client()

    breakpoints = list(dict.fromkeys(
        ([args.breakpoint] if args.breakpoint is not None else [])
        + args.additional_breakpoint
    ))
    watchpoint_packet = None
    clear_watchpoint_packet = None
    if args.watchpoint is not None:
        watchpoint_packet = f"Z2,{args.watchpoint:x},{args.watchpoint_length:x}"
        clear_watchpoint_packet = f"z2,{args.watchpoint:x},{args.watchpoint_length:x}"
    stops = 0
    skipped_stops = 0
    started = time.monotonic()
    failure: BaseException | None = None
    try:
        halt = client.command("?")
        for address in breakpoints:
            armed = client.command(f"Z0,{address:x},{args.breakpoint_length:x}")
            if armed != "OK":
                raise RuntimeError(f"mGBA rejected breakpoint 0x{address:08X}: {armed}")
        if watchpoint_packet:
            warmed = client.command(watchpoint_packet)
            if warmed != "OK":
                raise RuntimeError(f"mGBA rejected watchpoint: {warmed}")
            print(f"Z0={manifest['breakpoint']} Z2=0x{args.watchpoint:08X} both armed", flush=True)
        ready_path.write_text(
            f"halt={halt}\nbreakpoints={','.join(manifest['breakpoints']) or 'None'}\n",
            encoding="utf-8",
        )
        print(
            f"capture armed at {','.join(manifest['breakpoints']) or 'Lua-only'}; "
            "human play may begin",
            flush=True,
        )

        with (
            events_path.open("w", newline="", encoding="utf-8") as events_file,
            dumps_path.open("wb") as dumps_file,
            pointers_path.open("w", newline="", encoding="utf-8") as pointers_file,
        ):
            events = csv.writer(events_file)
            pointers = csv.writer(pointers_file)
            events.writerow(
                ["stop", "gameplay_tick", "elapsed_seconds", "pc", "lr", "sp"]
                + [f"r{index}" for index in range(13)]
                + ["dump_address", "stack_rom_chain", "read_value"]
            )
            pointers.writerow(["stop", "object_address", "field_offset", "pointer"])
            dumps_file.write(CAPTURE_MAGIC)
            client.continue_execution()

            while stops < args.max_stops and time.monotonic() - started < args.window_seconds:
                if args.stop_file is not None and args.stop_file.exists():
                    break
                try:
                    stop_reply = client.read_response(timeout=5.0)
                except TimeoutError:
                    print(
                        f"idle {time.monotonic() - started:.0f}s, stops={stops}",
                        flush=True,
                    )
                    continue
                if not stop_reply.startswith(("S", "T")):
                    print(f"unexpected RSP event: {stop_reply[:40]}", flush=True)
                    continue

                registers = client.registers()
                pc = registers[15] & ~1
                lr = registers[14] & ~1
                dump_address = registers[args.dump_register]
                matches = args.lr_filter is None or lr == (args.lr_filter & ~1)
                if matches and args.dump_word0_filter is not None:
                    matches = (
                        _is_readable_ewram(dump_address, 4)
                        and int.from_bytes(client.read_memory(dump_address, 4), "little")
                        == args.dump_word0_filter
                    )
                if (
                    matches
                    and args.primary_dump_word0_filter is not None
                    and args.breakpoint is not None
                    and pc == (args.breakpoint & ~1)
                ):
                    matches = (
                        _is_readable_work_ram(dump_address, 4)
                        and int.from_bytes(client.read_memory(dump_address, 4), "little")
                        == args.primary_dump_word0_filter
                    )
                if matches and args.decrease_register is not None:
                    compare_address = dump_address + args.compare_dump_offset
                    matches = _is_readable_ewram(compare_address, args.compare_length)
                    if matches:
                        current_value = int.from_bytes(
                            client.read_memory(compare_address, args.compare_length),
                            "little",
                        )
                        mask = (1 << (args.compare_length * 8)) - 1
                        incoming_value = registers[args.decrease_register] & mask
                        matches = incoming_value < current_value
                if not matches:
                    skipped_stops += 1
                    if skipped_stops == 1 or skipped_stops % 20 == 0:
                        print(
                            f"skipped stop {skipped_stops}: pc=0x{pc:08X} "
                            f"lr=0x{lr:08X} r{args.dump_register}=0x{dump_address:08X}",
                            flush=True,
                        )
                    client.continue_execution()
                    continue

                stops += 1
                sp = registers[13] & ~3
                stack = client.read_memory(sp, args.stack_length)
                stack_chain = [
                    value
                    for offset in range(0, len(stack), 4)
                    if ROM_LO
                    <= (value := int.from_bytes(stack[offset : offset + 4], "little"))
                    < ROM_HI
                ]
                dumped = b""
                if _is_readable_work_ram(dump_address, args.dump_length):
                    dumped = client.read_memory(dump_address, args.dump_length)
                    write_capture_record(dumps_file, stops, dump_address, dumped)
                    if args.scan_ewram_pointers:
                        for field_offset, pointer in scan_aligned_ewram_pointers(dumped):
                            pointers.writerow(
                                [stops, f"0x{dump_address:08X}", field_offset, f"0x{pointer:08X}"]
                            )

                read_value = ""
                if args.read_address is not None:
                    try:
                        raw_value = client.read_memory(args.read_address, args.read_length)
                        value = int.from_bytes(raw_value, "little")
                        read_value = f"0x{value:0{args.read_length * 2}X}"
                    except Exception:
                        read_value = "READ_ERR"

                events.writerow(
                    [stops, _read_gameplay_tick(gameplay_tick_file),
                     f"{time.monotonic() - started:.6f}", f"0x{pc:08X}",
                     f"0x{lr:08X}", f"0x{sp:08X}"]
                    + [f"0x{value:08X}" for value in registers[:13]]
                    + [
                        f"0x{dump_address:08X}" if dumped else "",
                        "|".join(f"0x{value:08X}" for value in stack_chain),
                        read_value,
                    ]
                )
                events_file.flush()
                dumps_file.flush()
                pointers_file.flush()
                print(
                    f"stop {stops}: pc=0x{pc:08X} r{args.dump_register}=0x{dump_address:08X} "
                    f"dumped={len(dumped)}",
                    flush=True,
                )
                client.continue_execution()
    except BaseException as exc:
        failure = exc
        raise
    finally:
        try:
            for address in breakpoints:
                client.command(f"z0,{address:x},{args.breakpoint_length:x}")
        except Exception:
            pass
        if clear_watchpoint_packet:
            try:
                client.command(clear_watchpoint_packet)
            except Exception:
                pass
        client.sock.close()
        manifest["status"] = "failed" if failure is not None else "complete"
        if failure is not None:
            manifest["error_type"] = type(failure).__name__
        manifest["stops"] = stops
        manifest["skipped_stops"] = skipped_stops
        manifest["elapsed_seconds"] = round(time.monotonic() - started, 6)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"capture complete: {stops} stop(s) in {output_dir}", flush=True)
    return 0


def main() -> int:
    args = _parse_args()
    if args.max_stops <= 0 or args.window_seconds <= 0 or args.dump_length <= 0:
        raise SystemExit("max stops, window, and dump length must be positive")
    if args.compare_length not in (1, 2, 4):
        raise SystemExit("compare length must be 1, 2, or 4 bytes")
    if args.primary_dump_word0_filter is not None and args.breakpoint is None:
        raise SystemExit("primary dump filter requires --breakpoint")
    return run_capture(args)


if __name__ == "__main__":
    raise SystemExit(main())
