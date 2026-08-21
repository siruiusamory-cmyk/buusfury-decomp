"""Bounded read-only mGBA probe for ROM-009 dynamic exact-object attribution."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from tools.runtime.rom008_query_probe import (
    Rom008RspClient,
    _read_bytes,
    _read_u32,
    run_probe,
)
from tools.runtime.rom009_object_trace import (
    POINT_QUERY_CALLSITE_TARGETS,
    POINT_SCHEDULER_GUARD_PC,
    PRECALLER_GUARD_PCS,
    QUERY_CAPABLE_CALLER_ENTRIES,
    SCHEDULER_FLAG_GATES,
    SCHEDULER_PREDECESSOR_CALLSITE_TARGETS,
    DynamicExactObjectTracker,
    classify_precaller_guard,
    classify_scheduler_flag_gate,
    point_scheduler_guard_rejects,
)
from tools.runtime.rom010_probe_status import (
    classify_probe_exception,
    classify_probe_result,
    probe_exit_code,
    write_probe_output,
)


def _evaluate_precaller_guard(
    client: Rom008RspClient, registers: Sequence[int]
) -> dict[str, object]:
    pc = registers[15]
    if pc in SCHEDULER_FLAG_GATES:
        halfword = int.from_bytes(_read_bytes(client, registers[0] + 4, 2), "little")
        return classify_scheduler_flag_gate(pc, halfword)
    if pc == 0x08012A36:
        manager = _read_u32(client, registers[5] + 0x10)
    elif pc == 0x08021CC8:
        if registers[7] != 0x03002BFC:
            raise RuntimeError("pre-caller scheduler global disagrees with verified literal")
        manager = _read_u32(client, 0x0872A6D0)
    else:
        raise RuntimeError("unexpected pre-caller guard")
    return classify_precaller_guard(pc, manager, registers[0])


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path)
    parser.add_argument("state", type=Path)
    parser.add_argument("save", type=Path)
    parser.add_argument("--state-sha256", required=True)
    parser.add_argument("--save-sha256", required=True)
    parser.add_argument("--lua", type=Path, required=True)
    parser.add_argument("--injector", type=Path, required=True)
    parser.add_argument(
        "--mgba", type=Path, default=Path(r"C:\Program Files\mGBA\mGBA.exe")
    )
    parser.add_argument(
        "--profiles",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "config" / "roms.yaml",
    )
    parser.add_argument("--timeout", type=float, default=25.0)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.timeout <= 0:
        raise SystemExit("--timeout must be positive")
    mgba_path = args.mgba.resolve()
    try:
        result = run_probe(
            rom_path=args.rom.resolve(),
            state_path=args.state.resolve(),
            save_path=args.save.resolve(),
            state_sha256=args.state_sha256,
            save_sha256=args.save_sha256,
            lua_path=args.lua.resolve(),
            injector_path=args.injector.resolve(),
            mgba_path=mgba_path,
            profile_path=args.profiles.resolve(),
            timeout_seconds=args.timeout,
            tracker_factory=DynamicExactObjectTracker,
            dynamic_load=True,
            run_label="rom010",
            fallback_callsite_targets={
                **POINT_QUERY_CALLSITE_TARGETS,
                **SCHEDULER_PREDECESSOR_CALLSITE_TARGETS,
            },
            scheduler_guard_pc=POINT_SCHEDULER_GUARD_PC,
            scheduler_guard_validator=point_scheduler_guard_rejects,
            fallback_entry_pcs=QUERY_CAPABLE_CALLER_ENTRIES,
            fallback_guard_pcs=(*PRECALLER_GUARD_PCS, *SCHEDULER_FLAG_GATES),
            fallback_guard_evaluator=_evaluate_precaller_guard,
            point_context_pointer_address=0x03001C34,
        )
        status = classify_probe_result(result)
    except Exception as exc:
        payload = {
            "probe_status": classify_probe_exception(exc, mgba_path=mgba_path).to_dict()
        }
        if args.output is not None:
            write_probe_output(
                args.output,
                payload,
                workspace_root=Path(__file__).resolve().parents[2],
            )
        print(json.dumps(payload, indent=2))
        return 3
    result["probe_status"] = status.to_dict()
    if args.output is not None:
        write_probe_output(
            args.output,
            result,
            workspace_root=Path(__file__).resolve().parents[2],
        )
    print(json.dumps(result, indent=2))
    return probe_exit_code(status)


if __name__ == "__main__":
    raise SystemExit(main())
