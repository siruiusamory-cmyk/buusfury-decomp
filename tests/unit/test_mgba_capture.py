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


def test_p008_clip_observer_stays_read_only():
    """The clip-sequence observer is evidence-grade and must never drive
    input, so a scripted run cannot be confused with a human one."""
    root = Path(__file__).resolve().parents[2]
    probe = (root / "tools/runtime/p008_clip_sequence.lua").read_text(
        encoding="utf-8"
    )

    assert "setKeys" not in probe
    assert "addKeys" not in probe
    assert "clearKeys" not in probe
    assert "emu:write" not in probe
    assert "local IDLE_CLIP = 0x0851C618" in probe
    assert "local CLIP = 0x04C" in probe


def test_tilepaint001_observer_is_read_only_and_allowlisted():
    """MAP-TILE-PAINT-001's runtime observer must only READ emulated state.

    It exists to answer "did the retail engine load the authored map cell?", so
    a script that could also write memory or drive input would make that answer
    unfalsifiable. The runtime addresses it uses are the ones TOOLKIT-029
    proved; re-deriving them would be a second, drifting copy.
    """
    root = Path(__file__).resolve().parents[2]
    observer = (root / "tools/runtime/tilepaint001_live_screenblock.lua").read_text(
        encoding="utf-8"
    )
    injector = (root / "tools/runtime/inject_mgba_lua.ps1").read_text(
        encoding="utf-8"
    )

    assert "setKeys" not in observer
    assert "addKeys" not in observer
    assert "clearKeys" not in observer
    assert "emu:write" not in observer
    # The runtime-proven live MapEntry pointer and table geometry.
    assert "local ACTIVE_MAP_PTR = 0x03001980" in observer
    assert "local MAP_ENTRY_BASE = 0x0808E2E0" in observer
    assert "local MAP_ENTRY_SIZE = 0x38" in observer
    # It accepts both game-code spellings: the 0.11 dev build returns the bare
    # code, and asserting only the prefixed form has broken an observer before.
    assert '"AGB-BG3E"' in observer
    # It reads each BG's screen base from LIVE BGxCNT rather than hardcoding one.
    assert "bg%d_screen_base" in observer
    assert "tilepaint001_live_screenblock.lua" in injector


def test_p008_mash_driver_is_separate_and_varies_its_interval():
    """the maintainer asked that repetitive mashing be scripted. The driver is a
    deliberately separate tool: a fixed period could alias against an internal
    timer, so the interval varies and is recorded on every row."""
    root = Path(__file__).resolve().parents[2]
    driver = (root / "tools/runtime/p008_mash_driver.lua").read_text(
        encoding="utf-8"
    )
    observer = (root / "tools/runtime/p008_clip_sequence.lua").read_text(
        encoding="utf-8"
    )
    injector = (root / "tools/runtime/inject_mgba_lua.ps1").read_text(
        encoding="utf-8"
    )

    # The driver drives input; the observer must not.
    assert "addKeys" in driver
    assert "clearKeys" in driver
    assert "addKeys" not in observer
    # Interval variation, and the gap recorded per row.
    assert "local GAPS = {" in driver
    assert "gap_used" in driver
    # Input is released on every exit path, so a stopped run cannot leave A held.
    assert driver.count("emu:clearKeys(KEY_A_MASK)") >= 3
    # It reads, never writes, emulated memory.
    assert "emu:write" not in driver
    assert "p008_mash_driver.lua" in injector


def test_p008_contact_observer_latches_any_punch_clip_not_only_from_idle():
    """An earlier revision only latched active_punch when the previous clip was
    idle. Real combat goes punch to punch or hurt to punch without passing
    through idle, so the tracker froze on a non-punch clip and every row
    carried a stale value."""
    root = Path(__file__).resolve().parents[2]
    probe = (root / "tools/runtime/p008_contact_trace.lua").read_text(
        encoding="utf-8"
    )
    injector = (root / "tools/runtime/inject_mgba_lua.ps1").read_text(
        encoding="utf-8"
    )

    # Membership is an explicit set, not "anything that is not idle".
    assert "local PUNCH_CLIPS = {" in probe
    assert "if PUNCH_CLIPS[clip] then" in probe
    assert "prev_clip == IDLE_CLIP and clip ~= IDLE_CLIP" not in probe
    # Two wolves can be struck, so an unattributable tick is flagged.
    assert "simultaneous" in probe
    # The human drives this capture, so it must never touch input. Match the
    # call form rather than the bare word, because the file's own header
    # comment names these APIs while explaining that it does not use them.
    assert "emu:setKeys" not in probe
    assert "emu:addKeys" not in probe
    assert "emu:clearKeys" not in probe
    assert "emu:write" not in probe
    assert "p008_contact_trace.lua" in injector


def test_p010_death_timeline_observer_is_read_only_and_discovers_targets():
    """P-010 needs the death lifecycle and the reward writes on one clock.

    The observer supplies the shared gameplay tick the breakpoints are stamped
    with, so it must be allowlisted; and it must perform no input, or the
    input-free guarantee that makes the capture evidence would be void.

    Targets are discovered rather than pinned. P-007 established that asserting
    a single enemy aborts on the two-wolf state, and that absolute EWRAM
    addresses are not stable actor identity.
    """
    root = Path(__file__).resolve().parents[2]
    observer = (root / "tools/runtime/p010_death_timeline.lua").read_text(
        encoding="utf-8"
    )
    injector = (root / "tools/runtime/inject_mgba_lua.ps1").read_text(
        encoding="utf-8"
    )

    # Confirmed anchors, used as given rather than rediscovered.
    assert "local HP = 0x28C" in observer
    assert "local CTRL = 0x238" in observer
    assert "local CLIP = 0x04C" in observer
    # Save base was confirmed this ticket from ROM pool 0x086B7080.
    assert "local SAVE_BASE = 0x03001068" in observer
    assert "local GOKU_XP = 0x03001584" in observer

    # Read-only: no input, no emulated writes.
    assert "emu:setKeys" not in observer
    assert "emu:addKeys" not in observer
    assert "emu:clearKeys" not in observer
    assert "emu:write" not in observer

    # Discovery, not a pinned actor address.
    assert "looks_like_actor" in observer
    assert "0x0203D504" not in observer

    assert "p010_death_timeline.lua" in injector


def test_mapgfxdiag001_observer_is_read_only_and_requires_a_real_area_entry():
    """MAP-GFX-DIAG-001 compares the SDK's ROM render with the engine's own.

    Two properties make that comparison evidence rather than assertion. The
    observer must only read emulated state - a script that could also write
    memory or drive input would make "the engine drew this" unfalsifiable - and
    it must refuse to dump a background that a savestate merely restored, which
    is why it waits for an observed departure from the target map before it
    latches anything.
    """
    root = Path(__file__).resolve().parents[2]
    observer = (root / "tools/runtime/mapgfxdiag001_map_layer_dump.lua").read_text(
        encoding="utf-8"
    )
    injector = (root / "tools/runtime/inject_mgba_lua.ps1").read_text(
        encoding="utf-8"
    )

    assert "setKeys" not in observer
    assert "addKeys" not in observer
    assert "clearKeys" not in observer
    assert "emu:write" not in observer

    # The runtime-proven live MapEntry pointer and table geometry.
    assert "local ACTIVE_MAP_PTR = 0x03001980" in observer
    assert "local MAP_ENTRY_BASE = 0x0808E2E0" in observer
    assert "local MAP_ENTRY_SIZE = 0x38" in observer
    # It accepts both game-code spellings: the 0.11 dev build returns the bare
    # code, and asserting only the prefixed form has broken an observer before.
    assert '"AGB-BG3E"' in observer
    # Each displayed BG's screenblock is read at the base LIVE BGxCNT names.
    assert "bg%d_screen_base_block" in observer
    # A savestate restore is not an area build, so a departure must be observed;
    # and an area entry fades in, so the dump also waits for the background
    # palette to stop changing before it latches anything.
    assert "saw_departure" in observer
    assert "local DWELL_FRAMES = 90" in observer
    assert "local SETTLE_FRAMES = 45" in observer
    assert "palette_signature" in observer
    # The display is captured from the emulator's own framebuffer rather than
    # from a host window rectangle, which can hold whatever is stacked on top.
    assert "emu:screenshot" in observer
    # The camera state address is a recorded candidate, never a conclusion.
    assert "camera_candidate_corroborated" in observer

    assert "mapgfxdiag001_map_layer_dump.lua" in injector


def test_p010_timeline_reports_the_lethal_edge_distinctly():
    """A death is the HP crossing to <= 0, which is a different row from an
    ordinary damage tick. Collapsing them would lose T_LETHAL, the anchor the
    whole timeline is measured against."""
    root = Path(__file__).resolve().parents[2]
    observer = (root / "tools/runtime/p010_death_timeline.lua").read_text(
        encoding="utf-8"
    )

    assert 'kind = "LETHAL"' in observer
    assert "hp <= 0 and state.hp > 0" in observer
    # Reward edges are logged even with no target tracked, because a reward can
    # land after its enemy has already been removed.
    assert '"ZENI,%d' in observer
    assert '"ITEM,%d' in observer
    assert '"XP,%d' in observer


def test_toolkit029_placement_watch_is_read_only_and_allowlisted():
    """TOOLKIT-029's runtime probe observes whether the engine consumes the
    authored map 10 slot. It must never drive input: the ticket's evidence
    depends on the run being ordinary gameplay, and a probe that pressed keys
    would also silently break the read-only guarantee every other observer
    carries."""
    root = Path(__file__).resolve().parents[2]
    probe = (root / "tools/runtime/toolkit029_placement_watch.lua").read_text(
        encoding="utf-8"
    )
    injector = (root / "tools/runtime/inject_mgba_lua.ps1").read_text(
        encoding="utf-8"
    )

    assert "setKeys" not in probe
    assert "addKey" not in probe
    assert "clearKey" not in probe
    assert "emu:write" not in probe
    assert "toolkit029_placement_watch.lua" in injector


def test_toolkit029_probe_separates_structure_from_instantiation():
    """The two questions must stay distinct in the evidence. That the engine is
    pointed at the expanded array (count/array/slot2) does NOT establish that an
    object was built from it, and a probe that reported only the first would
    invite exactly the overclaim this ticket has to avoid."""
    root = Path(__file__).resolve().parents[2]
    probe = (root / "tools/runtime/toolkit029_placement_watch.lua").read_text(
        encoding="utf-8"
    )

    # Channel 1: the live MapEntry pointer ROM-007 established.
    assert "0x03001980" in probe
    assert "slot2-is-authored-body" in probe
    # Channel 2: a scan for live references to the authored record body.
    assert "0x087EA400" in probe
    assert "AUTHORED-RECORD-REFERENCED-IN-EWRAM" in probe


def test_toolkit029_probe_scans_a_canonical_control():
    """A negative instantiation result is only trustworthy alongside a positive
    control. Scanning the canonical bodies on the same frames means "authored
    record absent" can be distinguished from "the scan finds nothing at all",
    which is the failure mode that would otherwise masquerade as refutation."""
    root = Path(__file__).resolve().parents[2]
    probe = (root / "tools/runtime/toolkit029_placement_watch.lua").read_text(
        encoding="utf-8"
    )

    assert "0x08075638" in probe  # canonical map 40 slot 1 = the clone source
    assert "0x08075670" in probe  # canonical map 40 slot 3
    assert "canonical-control-present" in probe
    assert "CONTROL-ABSENT-scan-uninformative" in probe


def test_toolkit030_behavior_watch_is_read_only_and_allowlisted():
    """TOOLKIT-030's probe observes whether the engine EXECUTES the behavior the
    SDK attached to an authored placement. It must never drive input: the
    evidence depends on the run being ordinary gameplay, and a probe that
    pressed keys would also silently break the read-only guarantee every other
    observer carries."""
    root = Path(__file__).resolve().parents[2]
    probe = (root / "tools/runtime/toolkit030_behavior_watch.lua").read_text(
        encoding="utf-8"
    )
    injector = (root / "tools/runtime/inject_mgba_lua.ps1").read_text(
        encoding="utf-8"
    )

    assert "setKeys" not in probe
    assert "addKey" not in probe
    assert "clearKey" not in probe
    assert "emu:write" not in probe
    assert "toolkit030_behavior_watch.lua" in injector


def test_toolkit030_probe_separates_attachment_from_execution():
    """Two distinct questions, kept in separate columns. That the live record
    carries the authored descriptor does NOT establish that its script ran, and
    a probe reporting only the first would invite exactly the overclaim this
    ticket has to avoid - TOOLKIT-029 stopped at instantiation for the same
    reason."""
    root = Path(__file__).resolve().parents[2]
    probe = (root / "tools/runtime/toolkit030_behavior_watch.lua").read_text(
        encoding="utf-8"
    )

    # Channel 1: the attached descriptor, through the live MapEntry pointer.
    assert "0x03001980" in probe
    assert "0x0808D788" in probe          # the authored behavior descriptor
    assert "AUTHORED-BEHAVIOR" in probe
    # Channel 2: the collision effect that behavior actually produces.
    assert "0x08054FBC" in probe          # collision grid holder, measured
    assert "rect_set_count" in probe


def test_toolkit030_probe_distinguishes_authored_from_inherited():
    """The independence control has to be visible in the runtime evidence too.
    The inherited-null descriptor is what the clone template carries, so a run
    that reports it is the CONTROL, and the probe must label the two apart
    rather than reporting a single undifferentiated 'descriptor present'."""
    root = Path(__file__).resolve().parents[2]
    probe = (root / "tools/runtime/toolkit030_behavior_watch.lua").read_text(
        encoding="utf-8"
    )

    assert "0x080555A0" in probe          # the null descriptor the template has
    assert "INHERITED-NULL" in probe
    assert "CONTROL inherited-null descriptor" in probe


def test_toolkit030_probe_refuses_to_read_a_broken_grid_as_negative():
    """A broken instrument is not negative evidence. TOOLKIT-029's EWRAM scan was
    invalidated because it could not tell 'absent' from 'this instrument sees
    nothing'; an unresolved collision grid must be labelled uninformative rather
    than written out as a clear rectangle."""
    root = Path(__file__).resolve().parents[2]
    probe = (root / "tools/runtime/toolkit030_behavior_watch.lua").read_text(
        encoding="utf-8"
    )

    assert "GRID-UNRESOLVED-scan-uninformative" in probe
    # An off-rect control tile keeps a saturated grid from looking like success.
    assert "control_tile_a" in probe


def test_launcher_generated_rom_mode_is_explicit_and_still_verifies_a_digest():
    """TOOLKIT-030 could not launch a generated authored ROM at all, because the
    launcher hard-pinned the canonical SHA-256 with no override, and it started
    mGBA by hand instead. The fix is a mode that is *more* verified than that
    bypass, not less: the caller must name the exact expected digest, and the
    launcher still refuses anything that does not equal it."""
    root = Path(__file__).resolve().parents[2]
    launcher = (root / "tools/runtime/run_mgba_capture.ps1").read_text(
        encoding="utf-8"
    )

    # Opting in is explicit and carries the expectation with it.
    assert "[string]$GeneratedRomSha256," in launcher
    assert "Generated ROM identity mismatch" in launcher
    # The supplied digest must be a full digest, not a prefix or a pattern.
    assert "^[0-9A-F]{64}$" in launcher
    # Size is still checked in generated mode.
    assert "Generated ROM size mismatch" in launcher
    # The run records which mode it used, so evidence is self-describing.
    assert "rom_mode" in launcher


def test_launcher_generated_mode_has_no_accept_anything_escape_hatch():
    """The guard must not gain a wildcard, a skip switch, or a way to pass the
    canonical digest through the generated path and call it verified."""
    root = Path(__file__).resolve().parents[2]
    launcher = (root / "tools/runtime/run_mgba_capture.ps1").read_text(
        encoding="utf-8"
    )

    # No switch that turns verification off.
    for escape in (
        "$SkipRomHashCheck",
        "$AllowAnyRom",
        "$IgnoreRomHash",
        "$ForceRom",
    ):
        assert escape not in launcher

    # Reusing the canonical digest under the generated flag is refused, so the
    # two modes cannot be silently collapsed into one.
    assert "GeneratedRomSha256 is the canonical digest" in launcher


def test_launcher_canonical_guard_is_unchanged_by_default():
    """Callers that say nothing must keep exactly the strict canonical check
    they had before the generated mode existed."""
    root = Path(__file__).resolve().parents[2]
    launcher = (root / "tools/runtime/run_mgba_capture.ps1").read_text(
        encoding="utf-8"
    )

    assert (
        "$expectedRomSha256 = "
        "'940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E'"
    ) in launcher
    assert "Canonical ROM identity mismatch; capture refused before launch" in launcher
    # The canonical branch is the fallback when no generated digest is supplied.
    assert "} elseif ($romInfo.Length -ne $expectedRomSize" in launcher


def test_toolkit031_observer_measures_execution_not_downstream_effect():
    """TOOLKIT-030's collision sampler was non-discriminating: both builds read
    the same saturated grid, so it could not separate 'the script ran' from
    'these tiles were already set'. The replacement must watch the program
    counter reach the handler instead of inferring execution from world state."""
    root = Path(__file__).resolve().parents[2]
    probe = (root / "tools/runtime/toolkit031_execution_watch.lua").read_text(
        encoding="utf-8"
    )

    # The script trampoline itself is the observable.
    assert "0x0800421E" in probe
    assert "setBreakpoint" in probe
    # And the descriptor is recorded, so a hit is attributable rather than a
    # bare count that cannot say WHICH attachment executed.
    assert "0x0808D788" in probe          # authored descriptor
    assert "0x0808D77C" in probe          # its script root
    assert "AUTHORED-BEHAVIOR" in probe


def test_toolkit031_observer_refuses_to_degrade_to_a_blind_poll():
    """Zero hits only mean something if the instrument can see hits at all. If
    the breakpoint API is missing the observer must abort rather than emit rows
    that look like a measured negative."""
    root = Path(__file__).resolve().parents[2]
    probe = (root / "tools/runtime/toolkit031_execution_watch.lua").read_text(
        encoding="utf-8"
    )

    assert "requires the mGBA 0.11 scripted-breakpoint API" in probe
    assert "cannot see execution and must not be substituted" in probe
    # Structural rows exist but are labelled so they cannot be read as execution.
    assert "structural sample only; not execution" in probe


def test_toolkit033_observer_is_read_only_discriminating_and_allowlisted():
    root = Path(__file__).resolve().parents[2]
    probe_path = root / "tools/runtime/toolkit033_gameplay_effect_watch.lua"
    probe = probe_path.read_text(encoding="utf-8")
    injector = (root / "tools/runtime/inject_mgba_lua.ps1").read_text(
        encoding="utf-8")

    assert "toolkit033_gameplay_effect_watch.lua" in injector
    assert "0x08004038" in probe       # authored script entry
    assert "0x08003CBE" in probe       # native_stack opcode handler
    assert "0x08003030" in probe       # selected slot-178 handler
    assert 'safe32(cursor_holder)' in probe  # live cursor via [r1]
    assert "last_authored_native_frame" in probe
    assert "EXPECTED-ARGS" in probe
    assert "emu:screenshot" in probe
    assert "negative" in probe
    assert "emu:write" not in probe
    assert "emu:addKey" not in probe and "emu:clearKey" not in probe


def test_toolkit034_dispatch_observer_is_bounded_read_only_and_allowlisted():
    """The caller capture must preserve attribution rather than guessing a trigger.

    It is an observer only: neither input nor emulated memory may be modified.
    The complete register and bounded stack snapshot make the indirect callsite
    decodable from a captured authored trampoline entry.
    """
    root = Path(__file__).resolve().parents[2]
    probe = (root / "tools/runtime/toolkit034_dispatch_caller_watch.lua").read_text(
        encoding="utf-8"
    )
    injector = (root / "tools/runtime/inject_mgba_lua.ps1").read_text(
        encoding="utf-8"
    )

    assert "toolkit034_dispatch_caller_watch.lua" in injector
    assert "TOOLKIT031_OUT" in probe
    assert "0x0800421E" in probe
    assert "0x08004038" in probe
    assert "NATIVE_STACK_BREAKPOINT = 0x08003CBE" in probe
    assert "NATIVE_STACK_HANDLER_ENTRY = 0x08003CC0" in probe
    assert "TEXT_HANDLER = 0x08003030" in probe
    assert "0x0800F866" in probe
    assert "0x08018950" in probe
    assert "0x08011A38" in probe
    assert "0x08011A3E" in probe
    assert "0x08011A5A" in probe
    assert "0x087EA420" in probe and "0x087EA428" in probe
    assert "AUTHORED_NATIVE_CURSOR = 0x087EA431" in probe
    assert "NATIVE_SLOT_178 = 178" in probe
    assert "EXPECT_TEXT = 1525" in probe
    assert "EXPECT_X = 120" in probe and "EXPECT_Y = 105" in probe
    assert "0x080555A0" in probe
    assert "CANONICAL_CONTROL_MAP = 40" in probe
    assert "map_index == CANONICAL_CONTROL_MAP" in probe
    assert "game_code == \"BG3E\"" in probe
    assert "emu:romSize() == 8388608" in probe
    assert "requires the mGBA 0.11 scripted-breakpoint API" in probe
    assert "STACK_WINDOW_BYTES = 0x40" in probe
    assert '"pc", "lr", "sp", "r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7"' in probe
    assert "stack_3c" in probe
    assert "f62c_saved_r4" in probe
    assert "f62c_saved_r5" in probe
    assert "f62c_saved_r6" in probe
    assert "f62c_saved_r7" in probe
    assert "f62c_caller_lr" in probe
    assert "safe32(sp + 0xDC)" in probe
    assert "safe32(sp + 0xEC)" in probe
    assert "assign behavior or trigger semantics to the caller" in probe
    assert "AUTHORED-DESCRIPTOR-PAYLOAD" in probe
    assert "AUTHORED-ACTOR" in probe
    assert "AUTHORED-EVENT-OBJECT" in probe
    assert "0x03001980" in probe
    assert "0x03003304" in probe
    assert "actor + 0x228" in probe
    assert "actor + 0x1A0" in probe and "actor + 0x1A4" in probe
    assert "actor + 0x28C" in probe
    assert "actor_hp_raw" in probe
    assert "actor_context(registers.r1)" in probe
    assert '"DEATH-CALLBACK"' in probe
    assert '"AUTHORED-ACTOR-DEATH"' in probe
    assert '"CANONICAL-NULL-ACTOR-DEATH"' in probe
    assert "runtime-confirmed death callback entry" in probe
    assert "frames ~= last_authored_trampoline_frame" in probe
    assert "frames ~= last_authored_script_frame" in probe
    assert "cursor == AUTHORED_NATIVE_CURSOR" in probe
    assert "slot == NATIVE_SLOT_178" in probe

    assert '"NATIVE-OPCODE"' in probe
    assert '"AUTHORED-NATIVE-SLOT-178"' in probe
    assert '"NATIVE-HANDLER"' in probe
    assert '"AUTHORED-NATIVE-178-EXPECTED-ARGS"' in probe
    assert "depth and depth >= 3" in probe
    assert "a0 == EXPECT_TEXT" in probe
    assert "a1 == EXPECT_X and a2 == EXPECT_Y" in probe
    assert "script_cursor" in probe and "native_slot_raw" in probe
    assert "vm_depth_raw" in probe
    assert "vm_arg0_raw" in probe and "vm_arg1_raw" in probe
    assert "vm_arg2_raw" in probe
    assert "emu:screenshot" in probe
    assert "object + 0x1C" in probe
    assert "event_object_register" in probe
    assert "event_word_00" in probe
    assert "event_word_04_raw" in probe
    assert "safe32(object + 0x04)" in probe
    assert "semantics UNKNOWN" in probe
    assert "MAX_FRAMES = 216000" in probe
    assert "emu:write" not in probe
    assert "emu:setKeys" not in probe
    assert "emu:addKeys" not in probe
    assert "emu:clearKeys" not in probe


def test_text_handle_002_observer_is_narrow_read_only_and_allowlisted():
    """The handler probe must preserve an attributable live route, not poll."""
    root = Path(__file__).resolve().parents[2]
    probe = (root / "tools/runtime/text_handle_002_handler_watch.lua").read_text(
        encoding="utf-8"
    )
    injector = (root / "tools/runtime/inject_mgba_lua.ps1").read_text(
        encoding="utf-8"
    )

    assert "text_handle_002_handler_watch.lua" in injector
    assert "0x08781CF8" in probe
    assert "0x02002641" in probe
    assert "0x0801242C" in probe
    assert "0x0801227E" in probe
    assert "0x08012230" in probe
    assert "0x08004038" in probe
    assert "record_words" in probe
    assert "packed_handle_at_plus_04" in probe
    assert "requires the mGBA 0.11 scripted-breakpoint API" in probe
    assert "emu:write" not in probe
    assert "emu:addKey" not in probe and "emu:clearKey" not in probe


def test_toolkit031_finisher_counts_toolkit034_row_kinds_as_live_channels():
    """A TOOLKIT-034 capture must not be falsely summarised as a blind zero.

    The established finisher remains compatible with historical EXEC/INTERP
    CSVs while recognising the new observer's code-site row names.
    """
    root = Path(__file__).resolve().parents[2]
    finisher = (root / "tools/runtime/finish_toolkit031_session.ps1").read_text(
        encoding="utf-8"
    )

    assert "@('EXEC', 'TRAMPOLINE')" in finisher
    assert "@('INTERP', 'INTERPRETER')" in finisher
    assert "EXECUTION OBSERVED - descriptors reaching the trampoline:" in finisher
    assert "$historicalExec | Group-Object descriptor_kind, descriptor" in finisher
    assert "$callerExec | Group-Object attribution, r0, payload" in finisher
    assert "TOOLKIT-034 caller snapshots (attribution, descriptor, payload):" in finisher


def test_rom_expand_observer_and_session_gate_bind_exact_generated_size():
    """Expansion proof accepts only the caller's exact hash and exact size."""
    root = Path(__file__).resolve().parents[2]
    session = (root / "tools/runtime/start_toolkit031_session.ps1").read_text(
        encoding="utf-8"
    )
    observer = (root / "tools/runtime/rom_expand_001_dialogue_watch.lua").read_text(
        encoding="utf-8"
    )
    injector = (root / "tools/runtime/inject_mgba_lua.ps1").read_text(
        encoding="utf-8"
    )

    assert "[UInt32]$ExpectedRomSize = 8388608" in session
    assert "$romInfo.Length -ne $ExpectedRomSize" in session
    assert "rom_expand_001_dialogue_watch.lua" in injector
    assert "0x08012240" in observer
    assert "0x02002641" in observer
    assert "0x08800000" in observer
    assert "emu:romSize() == 16777216" in observer
    assert "emu:screenshot" in observer
    assert "emu:write" not in observer
    assert "emu:setKey" not in observer


def test_warpedit001_observer_is_read_only_and_uses_the_engine_route():
    """MAP-WARP-RUNTIME-EDIT-001's observer must only READ emulated state.

    The ticket's claim is that the retail engine itself arrives at a different map
    after one transition record is retargeted. A script that could also write
    memory or drive input would make that unfalsifiable, and a scripted run could
    not be told apart from the human-played one the ticket requires.
    """
    root = Path(__file__).resolve().parents[2]
    observer = (
        root / "tools/runtime/warpedit001_transition_watch.lua"
    ).read_text(encoding="utf-8")
    injector = (root / "tools/runtime/inject_mgba_lua.ps1").read_text(
        encoding="utf-8"
    )

    assert "setKeys" not in observer
    assert "addKeys" not in observer
    assert "clearKeys" not in observer
    assert "emu:write" not in observer

    # The runtime-proven live MapEntry pointer and table geometry.
    assert "local ACTIVE_MAP_PTR = 0x03001980" in observer
    assert "local MAP_ENTRY_BASE = 0x0808E2E0" in observer
    assert "local MAP_ENTRY_SIZE = 0x38" in observer
    # Both game-code spellings: the 0.11 dev build returns the bare code, and
    # asserting only the prefixed form has broken an observer before.
    assert '"AGB-BG3E"' in observer
    assert "emu:romSize() == 8388608" in observer

    # The record must be reached by the SAME route the engine walks, not by a
    # pinned address: MapEntry + 0x2C -> word[0] -> root + 0x44 -> element.
    assert "local MAP_ENTRY_SOURCE_OFFSET = 0x2C" in observer
    assert "local ROOT_ARRAY_OFFSET = 0x44" in observer
    assert "route_to_record" in observer
    # The target record's own address is derived, never written down. If it ever
    # appears here, the observer stopped proving it reads the engine's record.
    assert "0x0829343C" not in observer
    assert "0x829343C" not in observer

    # The two destination key bytes are read from the running image, and the map
    # they name is resolved by the same two-byte scan the engine's lookup does.
    assert "local RECORD_KEY_HIGH_OFFSET = 0x11" in observer
    assert "local RECORD_KEY_LOW_OFFSET = 0x12" in observer
    assert "resolve_key" in observer
    # The region is read in the same rows, so "the position was not touched" is
    # visible beside the key that was.
    assert "local RECORD_REGION_OFFSET = 0x08" in observer

    # Liveness: a silent observer must be distinguishable from a quiet one, and
    # an unresolved route must be said out loud rather than omitted.
    assert "HEARTBEAT" in observer
    assert "TARGET_UNRESOLVED" in observer

    assert "warpedit001_transition_watch.lua" in injector


def test_warpedit001_launcher_verifies_identity_and_owns_no_session_lifetime():
    """The session launcher must pin the exact ROM and then get out of the way.

    Two separate bugs killed a live session part-way through: a deadline that
    counted setup and force-killed mGBA mid-play, and a background job whose
    teardown took the emulator with it. So the launcher may hold no wait loop,
    start no job, and clean up nothing - and it must refuse a run directory that
    already exists rather than deleting a prior session's evidence.
    """
    root = Path(__file__).resolve().parents[2]
    launcher = (root / "tools/runtime/start_warpedit001_live.ps1").read_text(
        encoding="utf-8"
    )
    finisher = (root / "tools/runtime/finish_warpedit001_session.ps1").read_text(
        encoding="utf-8"
    )

    # Exact ROM digest, and the version read from the binary rather than trusted
    # from its path.
    assert "^[0-9A-F]{64}$" in launcher
    assert "ROM identity mismatch; run refused" in launcher
    assert "VersionInfo.FileVersion" in launcher
    assert "mGBA version mismatch" in launcher
    # The savestate is copied and the copy verified, so the private original is
    # never what the emulator loads.
    assert "Savestate copy hash mismatch" in launcher
    # The state is loaded after the observer is injected.
    assert launcher.index("inject_mgba_lua.ps1") < launcher.index("toolkit031_load_state.ps1")

    # No ownership of the session.
    assert "Start-Job" not in launcher
    assert "Wait-Process" not in launcher
    assert "Stop-Process" not in launcher
    assert "Remove-Item" not in launcher
    assert "RunSeconds" not in launcher

    # The finisher re-verifies the ROM and refuses to read a silent observer as a
    # negative.
    assert "CHANGED - INVESTIGATE" in finisher
    assert "a silent" in finisher
    assert "NOT evidence of absence" in finisher
