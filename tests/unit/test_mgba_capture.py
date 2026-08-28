from __future__ import annotations

from io import BytesIO
from pathlib import Path
import socket

import pytest

from tools.runtime.mgba_capture import (
    CAPTURE_MAGIC,
    CaptureRspClient,
    iter_capture_records,
    scan_aligned_ewram_pointers,
    write_capture_record,
)
from tools.runtime.capture_mgba_event import (
    _is_readable_work_ram,
    _read_gameplay_tick,
    _resolve_gameplay_tick_file,
    _resolve_output_dir,
    _stack_length,
)
from tools.runtime.rom006_gdb_probe import rsp_packet


class FakeSocket:
    def __init__(self, chunks=()):
        self.chunks = list(chunks)
        self.sent = []
        self.timeouts = []

    def settimeout(self, timeout):
        self.timeouts.append(timeout)

    def recv(self, _size):
        if not self.chunks:
            raise socket.timeout()
        return self.chunks.pop(0)

    def sendall(self, data):
        self.sent.append(data)


@pytest.mark.parametrize("text, expected", [("64", 64), ("0xC0", 192), ("1024", 1024)])
def test_stack_length_accepts_bounded_aligned_values(text, expected):
    assert _stack_length(text) == expected


@pytest.mark.parametrize("text", ["60", "65", "1028"])
def test_stack_length_rejects_unbounded_or_unaligned_values(text):
    with pytest.raises(Exception):
        _stack_length(text)


def test_gameplay_tick_file_is_bounded_to_capture_run_sibling(tmp_path):
    output_dir = tmp_path / "run" / "capture"
    output_dir.mkdir(parents=True)
    expected = output_dir.parent / "frame-tick.txt"

    assert _resolve_gameplay_tick_file(expected, output_dir) == expected.resolve()
    with pytest.raises(ValueError):
        _resolve_gameplay_tick_file(tmp_path / "other" / "frame-tick.txt", output_dir)
    with pytest.raises(ValueError):
        _resolve_gameplay_tick_file(output_dir.parent / "other.txt", output_dir)


def test_gameplay_tick_reader_accepts_only_decimal_complete_values(tmp_path):
    tick = tmp_path / "frame-tick.txt"
    assert _read_gameplay_tick(tick) == ""
    tick.write_text("42", encoding="ascii")
    assert _read_gameplay_tick(tick) == "42"
    tick.write_text("42x", encoding="ascii")
    assert _read_gameplay_tick(tick) == ""


@pytest.mark.parametrize("address", [0x02000000, 0x0203FFF0, 0x03000000, 0x03007FF0])
def test_capture_dump_accepts_bounded_ewram_and_iwram(address):
    assert _is_readable_work_ram(address, 0x10)


@pytest.mark.parametrize("address", [0x01FFFFF0, 0x0203FFF1, 0x03007FF1, 0x04000000])
def test_capture_dump_rejects_out_of_bounds_work_ram(address):
    assert not _is_readable_work_ram(address, 0x10)


@pytest.mark.parametrize(
    "payload",
    ["?", "qSupported", "g", "c", "Z0,801920e,2", "z0,801920e,2", "Z2,203d508,2", "m203d504,c0"],
)
def test_capture_allowlist_accepts_only_observation_and_execution_control(payload):
    assert CaptureRspClient.command_is_allowed(payload)


@pytest.mark.parametrize(
    "payload",
    ["M203d504,2:0000", "X203d504,2:xx", "P0=00000000", "G00", "Z1,801920e,2", "s"],
)
def test_capture_allowlist_rejects_memory_register_and_unneeded_control_writes(payload):
    assert not CaptureRspClient.command_is_allowed(payload)


def test_response_parser_discards_noise_acknowledges_and_keeps_next_frame():
    fake = FakeSocket([b"noise+$OK#9a$S05#b8"])
    client = CaptureRspClient(fake)

    assert client.read_response(timeout=1) == "OK"
    assert client.read_response(timeout=1) == "S05"
    assert fake.sent == [b"+", b"+"]


def test_response_parser_rejects_bad_checksum_before_accepting_next_frame():
    fake = FakeSocket([b"$NO#00" + rsp_packet("OK")])
    client = CaptureRspClient(fake)

    assert client.read_response(timeout=1) == "OK"
    assert fake.sent == [b"-", b"+"]


def test_memory_reader_chunks_requests_and_truncates_oversized_reply():
    first = bytes(range(200)).hex()
    second = bytes(range(8)).hex()
    fake = FakeSocket([rsp_packet(first), rsp_packet(second)])
    client = CaptureRspClient(fake)

    data = client.read_memory(0x02000000, 200)

    assert data == bytes(range(192)) + bytes(range(8))
    assert rsp_packet("m2000000,c0") in fake.sent
    assert rsp_packet("m20000c0,8") in fake.sent


def test_memory_reader_retries_remaining_bytes_after_short_reply():
    fake = FakeSocket([rsp_packet("01020304"), rsp_packet("05060708")])
    client = CaptureRspClient(fake)

    assert client.read_memory(0x02000000, 8) == bytes(range(1, 9))
    assert rsp_packet("m2000000,8") in fake.sent
    assert rsp_packet("m2000004,4") in fake.sent


def test_pointer_scan_preserves_offsets_without_claiming_semantics():
    data = bytes.fromhex("04000002") + b"\0" * 4 + bytes.fromhex("03000002")

    assert scan_aligned_ewram_pointers(data) == ((0, 0x02000004),)


def test_capture_record_round_trips_and_detects_truncation():
    stream = BytesIO()
    stream.write(CAPTURE_MAGIC)
    write_capture_record(stream, 3, 0x0203D504, b"wolf")

    assert list(iter_capture_records(stream.getvalue())) == [
        (3, 0x0203D504, b"wolf")
    ]
    with pytest.raises(ValueError, match="truncated"):
        list(iter_capture_records(stream.getvalue()[:-1]))


def test_capture_output_is_restricted_to_ignored_build_tree(tmp_path):
    with pytest.raises(ValueError, match="repository build"):
        _resolve_output_dir(tmp_path / "tracked-looking-output")


def test_launcher_preserves_proven_single_owner_order_and_private_inputs():
    root = Path(__file__).resolve().parents[2]
    launcher = (root / "tools/runtime/run_mgba_capture.ps1").read_text(
        encoding="utf-8"
    )

    copy_state = launcher.index("Copy-Item -LiteralPath $resolvedState")
    launch = launcher.index("$process = Start-Process")
    inject = launcher.index("inject_mgba_lua.ps1")
    capture = launcher.index("tools.runtime.capture_mgba_event")
    first_continue = (root / "tools/runtime/capture_mgba_event.py").read_text(
        encoding="utf-8"
    ).index("client.continue_execution()")

    assert copy_state < launch < inject < capture
    assert first_continue > 0
    assert "--savestate', ('\"' + $workingState" in launcher
    assert "TCP port 2345 is already in use" in launcher
    assert launcher.count("Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedRom") == 2
    assert launcher.count("Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedState") == 2


def test_p006_trace_rediscovers_target_and_avoids_runtime_object_constants():
    root = Path(__file__).resolve().parents[2]
    trace = (root / "tools/runtime/p006_reaction_trace.lua").read_text(
        encoding="utf-8"
    )

    assert "discover_target()" in trace
    assert "emu:read32(target) ~= TARGET_DISPATCH" in trace
    assert "0x0203D504" not in trace
    assert "0x0203D508" not in trace
    assert "setKeys" not in trace
    assert 'tick_path = exp_dir .. "frame-tick.txt"' in trace
    assert 'tick_file:write(tostring(tick))' in trace
    assert "HP_OFFSET = 0x28C" in trace
    assert "OBJECT_BYTES = 0x2A0" in trace
    assert '"T,%d,epoch,%d,keys,%04x,target,%08x,hp,%08x' in trace

    injector = (root / "tools/runtime/inject_mgba_lua.ps1").read_text(
        encoding="utf-8"
    )
    assert "p006_reaction_trace.lua" in injector
    for retired_name in (
        "p006_save_state.lua",
        "p006_load_slot1.lua",
        "p006_auto_punch.lua",
    ):
        assert retired_name not in injector
    assert "build\\test_debug.lua" not in injector

    for retired_name in (
        "p006_save_state.lua",
        "p006_load_slot1.lua",
        "p006_auto_punch.lua",
        "p006_armed_punch.lua",
        "p006_load_and_scan.lua",
    ):
        retired = (root / "tools/runtime" / retired_name).read_text(encoding="utf-8")
        assert retired.startswith('error("RETIRED:')

    launcher = (root / "tools/runtime/run_mgba_capture.ps1").read_text(
        encoding="utf-8"
    )
    assert "--decrease-register" in launcher
    assert "--additional-breakpoint" in launcher
    assert "--gameplay-tick-file" in launcher
    assert "--primary-dump-word0-filter" in launcher
    assert "additional_breakpoints = @($parsedAdditionalBreakpoints" in launcher
    assert "$item -split ','" in launcher
    capture = (root / "tools/runtime/capture_mgba_event.py").read_text(
        encoding="utf-8"
    )
    assert 'action="append"' in capture
    assert "pc == (args.breakpoint & ~1)" in capture
    assert '["stop", "gameplay_tick", "elapsed_seconds"' in capture
    assert "--compare-dump-offset" in launcher
    assert "if ($Breakpoint -ne 0)" in launcher
    assert "DiscoverWolf" not in launcher
    assert "HpRead" not in launcher
    assert "','.join(manifest['breakpoints']) or 'Lua-only'" in (
        root / "tools/runtime/capture_mgba_event.py"
    ).read_text(encoding="utf-8")


def test_p006_trace_monitors_linked_ewram_object():
    """Verify the trace reads target+0x1D8 as a linked pointer and tracks its changes."""
    root = Path(__file__).resolve().parents[2]
    trace = (root / "tools/runtime/p006_reaction_trace.lua").read_text(
        encoding="utf-8"
    )

    # Linked pointer read at offset 0x1D8
    assert "LINKED_PTR_OFFSET = 0x1D8" in trace
    assert "LINKED_BYTES = 0x80" in trace

    # Discovery and EWRAM validation
    assert "discover_linked" in trace
    assert "in_ewram(ptr, LINKED_BYTES)" in trace

    # Linked address appears in EPOCH lines
    assert "linked,%08x" in trace
    assert "linked,none" in trace

    # Per-frame linked_changes column in CSV
    assert "linked_changes" in trace

    # Linked re-discovery on epoch change
    epoch_idx = trace.index("epoch = epoch + 1")
    assert "discover_linked(target)" in trace[epoch_idx:epoch_idx + 300]


def test_p006c_anchor_trace_is_read_only_and_uses_dynamic_objects():
    root = Path(__file__).resolve().parents[2]
    trace = (root / "tools/runtime/p006c_anchor_trace.lua").read_text(
        encoding="utf-8"
    )
    injector = (root / "tools/runtime/inject_mgba_lua.ps1").read_text(
        encoding="utf-8"
    )

    assert "discover_target()" in trace
    assert "PLAYER_SLOT = 0x03001C34" in trace
    assert "emu:read32(target + 0x23C)" in trace
    assert "emu:read32(target + 0x244)" in trace
    assert "emu:read32(player + 0x23C)" in trace
    assert 'tick_path = exp_dir .. "frame-tick.txt"' in trace
    assert "emu:write" not in trace
    assert "setKeys" not in trace
    assert "p006c_anchor_trace.lua" in injector


def test_p006c_dev_breakpoint_probe_is_read_only_and_allowlisted():
    root = Path(__file__).resolve().parents[2]
    probe = (root / "tools/runtime/p006c_dev_breakpoint_probe.lua").read_text(
        encoding="utf-8"
    )
    injector = (root / "tools/runtime/inject_mgba_lua.ps1").read_text(
        encoding="utf-8"
    )

    assert "emu:setBreakpoint" in probe
    assert "emu:clearBreakpoint" in probe
    assert "emu:readRegister" in probe
    assert "emu:write" not in probe
    assert "setKeys" not in probe
    assert "p006c_dev_breakpoint_probe.lua" in injector


def test_launcher_supports_explicit_mgba_startup_lua_mode():
    root = Path(__file__).resolve().parents[2]
    launcher = (root / "tools/runtime/run_mgba_capture.ps1").read_text(
        encoding="utf-8"
    )

    assert "[switch]$LuaStartup" in launcher
    assert "LuaStartup requires LuaPath" in launcher
    assert "'--script'" in launcher
    assert "-and -not $LuaStartup" in launcher
    assert '"`r`n"' in launcher


def test_p006_hit_bracket_uses_dynamic_event_and_adjacent_full_ewram_frames():
    root = Path(__file__).resolve().parents[2]
    scan = (root / "tools/runtime/p006_hit_bracket_scan.lua").read_text(
        encoding="utf-8"
    )
    injector = (root / "tools/runtime/inject_mgba_lua.ps1").read_text(
        encoding="utf-8"
    )

    assert "discover_target()" in scan
    assert "0x0203D504" not in scan
    assert "EVENT_OFFSET = 0x1D4" in scan
    assert "previous_snapshot = emu:readRange(EWRAM_LO, EWRAM_BYTES)" in scan
    assert '"p006-hit-before.bin"' in scan
    assert '"p006-hit-before2.bin"' in scan
    assert '"p006-hit-event.bin"' in scan
    assert '"p006-hit-after1.bin"' in scan
    assert '"p006-hit-after2.bin"' in scan
    assert "IWRAM_LO = 0x03000000" in scan
    assert '"p006-hit-iwram-before.bin"' in scan
    assert '"p006-hit-iwram-before2.bin"' in scan
    assert '"p006-hit-iwram-event.bin"' in scan
    assert '"p006-hit-iwram-after1.bin"' in scan
    assert '"p006-hit-iwram-after2.bin"' in scan
    assert "marker ~= previous_marker" in scan
    assert "setKeys" not in scan
    assert "p006_hit_bracket_scan.lua" in injector
    assert "p006_load_and_scan.lua" not in injector


def test_launcher_fails_closed_on_wrong_mgba_version():
    """The stable 0.10.5 install was once overwritten in place by a 0.11
    development build, so the launcher silently ran an unaccepted emulator.
    Identity must be verified from the binary, not assumed from its path."""
    root = Path(__file__).resolve().parents[2]
    launcher = (root / "tools/runtime/run_mgba_capture.ps1").read_text(
        encoding="utf-8"
    )

    assert "$RequiredMGBVersion = '0.10.5'" in launcher
    assert "VersionInfo.FileVersion" in launcher
    assert "mGBA version mismatch" in launcher
    # The default must not point at the shared install that was overwritten.
    assert r"[string]$MGBPath = 'C:\Program Files\mGBA" not in launcher
    assert "mgba-0.10.5" in launcher


def test_injector_selects_scripting_prompt_by_identity():
    """Qt may report an empty IsReadOnly for every Edit in the Scripting
    window. Selecting the first non-read-only element then picks the log pane
    and SetValue throws, so the prompt is matched by control identity."""
    root = Path(__file__).resolve().parents[2]
    injector = (root / "tools/runtime/inject_mgba_lua.ps1").read_text(
        encoding="utf-8"
    )

    assert "EndsWith('.prompt')" in injector
    assert "QGBA::HistoryLineEdit" in injector
    # The bare truthiness test is what broke; an explicit comparison is fine.
    assert "if (-not $edit.Current.IsReadOnly) { $prompt = $edit; break }" \
        not in injector


def test_controller_stack_observer_is_read_only_and_uses_decoded_layout():
    """P-006C reads the wolf behavior controller directly, so it must use the
    statically decoded offsets and must never write emulated state or input.

    A runtime probe found a controller only at actor+0x238; the +0x228 offset
    and the player object matched nothing, so the observer reads +0x238 alone.
    """
    root = Path(__file__).resolve().parents[2]
    observer = (root / "tools/runtime/p006c_ctrl_stack.lua").read_text(
        encoding="utf-8"
    )
    injector = (root / "tools/runtime/inject_mgba_lua.ps1").read_text(
        encoding="utf-8"
    )

    assert "local CTRL_B = 0x238" in observer
    assert "local MAX_DEPTH = 5" in observer
    assert "local TABLE_LO = 0x0870F514" in observer
    assert "local HP_OFFSET = 0x28C" in observer
    assert "discover_target()" in observer
    assert "0x0203D504" not in observer
    assert "setKeys" not in observer
    assert "emu:write" not in observer
    assert "p006c_ctrl_stack.lua" in injector


def test_controller_layout_probe_is_bounded_and_read_only():
    """The layout probe is what established that only wolf+0x238 is a
    controller. It must stay read-only and must recognise a controller
    structurally rather than assuming an offset."""
    root = Path(__file__).resolve().parents[2]
    probe = (root / "tools/runtime/p006c_ctrl_probe.lua").read_text(
        encoding="utf-8"
    )
    injector = (root / "tools/runtime/inject_mgba_lua.ps1").read_text(
        encoding="utf-8"
    )

    assert "local TABLE_LO = 0x0870F514" in probe
    assert "local MAX_DEPTH = 5" in probe
    assert "discover_target()" in probe
    assert "0x0203D504" not in probe
    assert "setKeys" not in probe
    assert "emu:write" not in probe
    assert "p006c_ctrl_probe.lua" in injector


def test_punch_field_probe_is_read_only_and_selects_no_field():
    """The punch anchor was found by snapshotting the whole player object and
    correlating changes against A edges, after two proposed-field candidates
    were refuted. The probe must keep recording input edges independently, so a
    press that changes nothing stays visible."""
    root = Path(__file__).resolve().parents[2]
    probe = (root / "tools/runtime/p006c_punch_field_probe.lua").read_text(
        encoding="utf-8"
    )
    injector = (root / "tools/runtime/inject_mgba_lua.ps1").read_text(
        encoding="utf-8"
    )

    assert "local PLAYER_SLOT = 0x03001C34" in probe
    assert "local OBJECT_BYTES = 0x2A0" in probe
    # An A edge is logged on its own row, not only alongside a field change.
    assert 'wline(string.format(\n                    "A,%d,%04x,1' in probe
    assert "0x0203DEB4" not in probe
    assert "setKeys" not in probe
    assert "emu:write" not in probe
    assert "p006c_punch_field_probe.lua" in injector


def test_pool_probe_logs_input_independently_of_phase_changes():
    """A capture in which the human pressed A throughout recorded keys as zero
    on every row, because every write sat inside the phase-change loop."""
    root = Path(__file__).resolve().parents[2]
    probe = (root / "tools/runtime/p006c_pool_probe.lua").read_text(
        encoding="utf-8"
    )

    assert "previous_keys ~= keys" in probe
    # A newly discovered object must not masquerade as a phase transition.
    assert 'kind = "NEW"' in probe
    assert "setKeys" not in probe
    assert "emu:write" not in probe


def test_p007_observer_tracks_every_wolf_and_flags_absent_actors():
    """The P-007 acquisition state holds two wolves. An earlier revision
    asserted exactly one and aborted at init before arming, and it also emitted
    numeric deltas against a despawned actor, which read as enormous
    distances."""
    root = Path(__file__).resolve().parents[2]
    probe = (root / "tools/runtime/p007_wolf_ai_trace.lua").read_text(
        encoding="utf-8"
    )
    injector = (root / "tools/runtime/inject_mgba_lua.ps1").read_text(
        encoding="utf-8"
    )

    # Discovery returns every match and records the real count.
    assert "discover_targets()" in probe
    assert "expected exactly one target dispatch match" not in probe
    assert '"SCAN,0,0000,%08x,count=%d' in probe
    # An absent actor yields a sentinel, never a zero-derived delta.
    assert 'local dx, dy = "na", "na"' in probe
    # Decoded offsets, not guesses.
    assert "local POS_X = 0x1A0" in probe
    assert "local POS_Y = 0x1A4" in probe
    assert "local CTRL = 0x238" in probe
    assert "local TABLE_LO = 0x0870F514" in probe
    # Read-only, and no reused runtime address.
    assert "setKeys" not in probe
    assert "emu:write" not in probe
    assert "0x0203D504" not in probe
    assert "p007_wolf_ai_trace.lua" in injector
