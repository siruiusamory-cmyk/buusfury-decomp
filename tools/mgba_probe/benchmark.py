"""Reproducible ROM-011 stock/disarmed/armed playability gate."""

from __future__ import annotations

import argparse
import json
import shutil
import socket
import subprocess
import time
from pathlib import Path
from typing import Sequence

from tools.mgba_probe.runtime import (
    ArmRequest,
    instrumented_environment,
    sha256,
    verify_instrumented_mgba,
)
from tools.runtime.rom006_gdb_probe import EXPECTED_SHA256, EXPECTED_SIZE, _connect
from tools.runtime.rom011_live_watch import Rom011RspClient


VCOUNT = 0x04000006
SCANLINES_PER_FRAME = 228
MAX_UNAMBIGUOUS_GAP = 0.014
MAX_PHASE_GAP = 0.050
MIN_SAMPLE_SECONDS = 2.0
# Valid EWRAM sentinel used only to keep the probe armed during the speed gate.
# Runtime semantic capture always uses the dynamically discovered live object X.
BENCHMARK_X = 0x0203FF00
BENCHMARK_DESCRIPTOR = 0x08294948


def analyze_vcount_samples(samples: Sequence[tuple[float, int]]) -> dict[str, float | int]:
    if len(samples) < 3:
        raise ValueError("VCOUNT benchmark requires at least three samples")
    wraps_observed = 0
    qualified_seconds = 0.0
    max_gap = 0.0
    qualified = 0
    for (before_time, before), (after_time, after) in zip(samples, samples[1:]):
        if not 0 <= before < SCANLINES_PER_FRAME or not 0 <= after < SCANLINES_PER_FRAME:
            raise ValueError("VCOUNT sample is outside the GBA scanline range")
        gap = after_time - before_time
        if gap < 0:
            raise ValueError("VCOUNT timestamps must increase")
        if gap == 0:
            continue
        max_gap = max(max_gap, gap)
        if gap > MAX_PHASE_GAP:
            raise RuntimeError("VCOUNT sampling gap is too large for wrap counting")
        if after < before:
            wraps_observed += 1
        if gap > MAX_UNAMBIGUOUS_GAP:
            continue
        qualified_seconds += gap
        qualified += 1
    if qualified_seconds < MIN_SAMPLE_SECONDS:
        raise RuntimeError("too little unambiguous VCOUNT time for a speed result")
    total_seconds = samples[-1][0] - samples[0][0]
    return {
        "fps": wraps_observed / total_seconds,
        "wraps_observed": wraps_observed,
        "samples": len(samples),
        "qualified_intervals": qualified,
        "qualified_seconds": qualified_seconds,
        "max_gap_ms": max_gap * 1000,
    }


def _measure(
    *,
    name: str,
    executable: Path,
    environment: dict[str, str] | None,
    rom: Path,
    state: Path,
    save: Path,
    run_root: Path,
    duration: float,
    arm: bool,
) -> dict[str, object]:
    case_root = run_root / name
    case_root.mkdir()
    state_copy = case_root / state.name
    save_copy = case_root / save.name
    shutil.copy2(state, state_copy)
    shutil.copy2(save, save_copy)
    states = case_root / "states"
    screenshots = case_root / "screenshots"
    states.mkdir()
    screenshots.mkdir()
    command = [
        str(executable), "--gdb", "--savestate", str(state_copy),
        "-C", f"savegamePath={case_root}",
        "-C", f"savestatePath={states}",
        "-C", f"screenshotPath={screenshots}",
        "-C", "volume=0",
        "-C", "audioSync=0",
        "-C", "videoSync=1",
        "-C", "fpsTarget=59.7275",
        str(rom),
    ]
    process = subprocess.Popen(
        command,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        time.sleep(0.5)
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            detail = (stderr or stdout or "no emulator output").strip()
            raise RuntimeError(
                f"{name} emulator exited before GDB startup ({process.returncode}): {detail}"
            )
        with _connect(time.monotonic() + 15) as sock:
            client = Rom011RspClient(sock)
            initial_status = client.command("?")
            arm_response = None
            if arm:
                arm_response = client.arm_native_probe(
                    ArmRequest(1, BENCHMARK_X, 1, BENCHMARK_DESCRIPTOR)
                )
                if arm_response != "OK":
                    raise RuntimeError(f"native benchmark arm rejected: {arm_response}")
            try:
                client.command("c", timeout=0.25)
                raise RuntimeError("emulator stopped before VCOUNT sampling began")
            except socket.timeout:
                pass
            packet = client.allow_read(VCOUNT, 2)
            samples: list[tuple[float, int]] = []
            deadline = time.perf_counter() + duration
            while time.perf_counter() < deadline:
                response = client.command(packet, timeout=1.0)
                if len(response) != 4:
                    raise RuntimeError(
                        f"VCOUNT sampling received an unexpected stop/response: {response}"
                    )
                samples.append(
                    (time.perf_counter(), int.from_bytes(bytes.fromhex(response), "little"))
                )
            sock.sendall(b"\x03")
            stop_response = client._read_response(5.0)
        (case_root / "vcount-samples.json").write_text(
            json.dumps(samples) + "\n", encoding="utf-8"
        )
        result = analyze_vcount_samples(samples)
        result.update(
            {
                "case": name,
                "initial_status": initial_status,
                "stop_response": stop_response,
                "arm_response": arm_response,
                "input_injected": False,
                "ui_automation": False,
            }
        )
        return result
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def run_gate(
    *,
    stock: Path,
    instrumented: Path,
    manifest_path: Path,
    rom: Path,
    state: Path,
    save: Path,
    state_sha256: str,
    save_sha256: str,
    run_root: Path,
    duration: float = 5.0,
) -> dict[str, object]:
    if duration < 3:
        raise ValueError("speed-gate duration must be at least three seconds")
    run_root = run_root.resolve()
    allowed_parent = (Path(__file__).resolve().parents[2] / "build" / "rom011").resolve()
    if run_root.parent != allowed_parent or run_root.exists():
        raise ValueError("benchmark root must be one new direct child of build/rom011")
    if rom.stat().st_size != EXPECTED_SIZE or sha256(rom) != EXPECTED_SHA256:
        raise RuntimeError("verified ROM identity mismatch")
    if sha256(state).lower() != state_sha256.lower():
        raise RuntimeError("save-state identity mismatch")
    if sha256(save).lower() != save_sha256.lower():
        raise RuntimeError("save identity mismatch")
    manifest = verify_instrumented_mgba(instrumented, manifest_path)
    environment = instrumented_environment(manifest)
    stock_version = subprocess.run(
        [str(stock), "--version"], check=True, capture_output=True, text=True, timeout=10
    ).stdout.strip()
    if "0.10.5" not in stock_version:
        raise RuntimeError("stock control is not mGBA 0.10.5")
    run_root.mkdir(parents=True)
    before = {path: sha256(path) for path in (rom, state, save)}
    results = [
        _measure(name="stock", executable=stock, environment=None, rom=rom, state=state, save=save, run_root=run_root, duration=duration, arm=False),
        _measure(name="instrumented-disarmed", executable=instrumented, environment=environment, rom=rom, state=state, save=save, run_root=run_root, duration=duration, arm=False),
        _measure(name="instrumented-armed", executable=instrumented, environment=environment, rom=rom, state=state, save=save, run_root=run_root, duration=duration, arm=True),
    ]
    after = {path: sha256(path) for path in before}
    if after != before:
        raise RuntimeError("benchmark modified an original ROM/save/state input")
    by_name = {str(item["case"]): item for item in results}
    stock_fps = float(by_name["stock"]["fps"])
    automated_passed = all(float(item["fps"]) >= 50 for item in results)
    report = {
        "schema": "log1-mgba-performance-gate-v1",
        "stock_version": stock_version,
        "instrumented_version": manifest["version_output"],
        "method": "observed GBA VCOUNT rollover lower bound over GDB without memory watchpoints",
        "duration_seconds_per_case": duration,
        "results": results,
        "quantitative_throughput_ratio_valid": False,
        "ratio_limitations": [
            "VCOUNT gaps longer than one frame make exact missed-wrap counts ambiguous",
            "stock Qt and instrumented SDL frontends are not an uncapped like-for-like throughput comparison",
        ],
        "acceptance": {
            "minimum_observed_rollover_rate_hz": 50,
            "automated_near_realtime_observation_passed": automated_passed,
            "human_input_latency_observation": "pending",
            "complete": False,
        },
        "original_inputs_unchanged": True,
    }
    report_path = run_root / "performance-gate.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not automated_passed:
        raise RuntimeError(f"native probe failed speed gate; report: {report_path}")
    return report


def reanalyze_gate_report(run_root: Path) -> dict[str, object]:
    """Recompute metrics from an existing gate's immutable raw VCOUNT samples."""
    report_path = run_root / "performance-gate.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if not isinstance(report, dict) or report.get("schema") != "log1-mgba-performance-gate-v1":
        raise ValueError("performance gate report schema mismatch")
    results = report.get("results")
    if not isinstance(results, list) or len(results) != 3:
        raise ValueError("performance gate report must contain three cases")
    for result in results:
        if not isinstance(result, dict) or not isinstance(result.get("case"), str):
            raise ValueError("performance gate case is malformed")
        sample_path = run_root / result["case"] / "vcount-samples.json"
        samples = json.loads(sample_path.read_text(encoding="utf-8"))
        result.update(analyze_vcount_samples(samples))
    by_name = {str(item["case"]): item for item in results}
    report["method"] = (
        "observed GBA VCOUNT rollover lower bound over GDB without memory watchpoints"
    )
    report.pop("disarmed_ratio_to_stock", None)
    report.pop("armed_ratio_to_stock", None)
    automated_passed = all(float(item["fps"]) >= 50 for item in results)
    report["quantitative_throughput_ratio_valid"] = False
    report["ratio_limitations"] = [
        "VCOUNT gaps longer than one frame make exact missed-wrap counts ambiguous",
        "stock Qt and instrumented SDL frontends are not an uncapped like-for-like throughput comparison",
    ]
    report["acceptance"] = {
        "minimum_observed_rollover_rate_hz": 50,
        "automated_near_realtime_observation_passed": automated_passed,
        "human_input_latency_observation": "pending",
        "complete": False,
    }
    report["analysis_revision"] = "direct-vcount-wrap-v2"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock", type=Path, required=True)
    parser.add_argument("--instrumented", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--rom", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--save", type=Path, required=True)
    parser.add_argument("--state-sha256", required=True)
    parser.add_argument("--save-sha256", required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--duration", type=float, default=5.0)
    args = parser.parse_args(argv)
    report = run_gate(
        stock=args.stock.resolve(), instrumented=args.instrumented.resolve(),
        manifest_path=args.manifest.resolve(), rom=args.rom.resolve(),
        state=args.state.resolve(), save=args.save.resolve(),
        state_sha256=args.state_sha256, save_sha256=args.save_sha256,
        run_root=args.run_root, duration=args.duration,
    )
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
