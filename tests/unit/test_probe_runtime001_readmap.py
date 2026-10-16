"""The PROBE-RUNTIME-001 read-map observer's JSON writer, state gate and span rows.

These tests run the SHIPPED observer with a fake emulation core, drive one frame so
it finalizes, and parse the READMAP.json it wrote. The cases carry the values the
observer has to get right: a refused state, a state frame that is not a whole frame
number >= 1, a load that returned false without raising, a load error carrying a
quote, a backslash, a newline, a tab and a carriage return, an unattributable
watchpoint fire beside a working control, and a span whose first_pc is absent.

The observer is Lua. A Lua interpreter is located at run time: the lupa binding
(Lua 5.4, the version mGBA embeds) if importable, else lua5.4/lua/luajit on PATH.
When no interpreter exists these tests SKIP with that reason instead of passing on
a substring of the source, because a substring proves nothing about behaviour.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

OBSERVER = (
    Path(__file__).resolve().parents[2]
    / "tools"
    / "runtime"
    / "probe_runtime001_readmap.lua"
)

# The load error the fake core raises, byte for byte: newline, tab, quote,
# backslash and carriage return all have to survive the escape.
LOAD_ERROR = 'load failed\n\tquote " backslash \\ carriage\r'

# The two span ranges the fake fire uses: the in-run positive control, and one
# ordinary span the fire misses so its callback cannot be attributed.
CONTROL_MIN = 0x086B82EC
BROKEN_SPAN_ID = "R1_A1_selfnaming"
BROKEN_SPAN_MIN = 0x08072CD4

DRIVER = r'''
local OBS = os.getenv("READMAP_B6_OBSERVER")
local SCENARIO = os.getenv("READMAP_B6_SCENARIO")
local frame_cb = nil
local next_id = 0
emu = {}
local function id() next_id = next_id + 1 return next_id end
emu.getGameCode = function() return "BG3E" end
emu.romSize = function() return 8388608 end
emu.read8 = function() return 0 end
emu.read16 = function() return 0 end
emu.read32 = function() return 0 end
emu.readRange = function() return {} end
emu.readRegister = function() return 0 end
emu.currentFrame = function() return 0 end
emu.screenshot = function() end
emu.setBreakpoint = function() return id() end
emu.clearBreakpoint = function() end
emu.setWatchpoint = function() return id() end
-- Every armed watch is kept, so the driver can fire the callback the observer
-- installed for a given span range.
local watches = {}
emu.setRangeWatchpoint = function(...)
    local args = { ... }
    local cb, lo, hi = nil, nil, nil
    for _, v in ipairs(args) do
        if type(v) == "function" then cb = cb or v
        elseif type(v) == "number" then
            if lo == nil then lo = v elseif hi == nil then hi = v end
        end
    end
    watches[#watches + 1] = { cb = cb, min = lo, max = hi }
    return id()
end
emu.loadStateFile = function()
    if SCENARIO == "load_false" then return false end
    if SCENARIO == "load_error" then
        error('load failed\n\tquote " backslash \\ carriage\r', 0)
    end
    return true
end
callbacks = { add = function(self, name, fn) frame_cb = fn return 1 end }
dofile(OBS)
if frame_cb == nil then error("the observer registered no frame callback") end
if SCENARIO == "undecodable" then
    local control, broken
    for _, w in ipairs(watches) do
        if w.min == 0x086B82EC then control = w end
        if w.min == 0x08072CD4 then broken = w end
    end
    if control == nil or broken == nil then
        error("the fake core did not see both watches: " .. tostring(#watches))
    end
    -- One attributable fire inside the control's own range, one fire whose
    -- address belongs to no part of the span it arrived on.
    control.cb({ address = 0x086B8300, width = 1, accessType = 2 })
    broken.cb({ address = 0x00123456, width = 1, accessType = 2 })
end
frame_cb()
'''

# Each scenario's state variables. An absent key means that variable is not set at
# all, which is the state-path-without-AT case.
SCENARIOS = {
    "refused": {"PROBE_RUNTIME_STATE": "C:/b6/refused.ss1"},
    "load_false": {"PROBE_RUNTIME_STATE": "C:/b6/load_false.ss1",
                   "PROBE_RUNTIME_STATE_AT": "1"},
    "load_error": {"PROBE_RUNTIME_STATE": "C:/b6/load_error.ss1",
                   "PROBE_RUNTIME_STATE_AT": "1"},
    "at_half": {"PROBE_RUNTIME_STATE": "C:/b6/at_half.ss1",
                "PROBE_RUNTIME_STATE_AT": "1.5"},
    "at_zero": {"PROBE_RUNTIME_STATE": "C:/b6/at_zero.ss1",
                "PROBE_RUNTIME_STATE_AT": "0"},
    "at_negative": {"PROBE_RUNTIME_STATE": "C:/b6/at_negative.ss1",
                    "PROBE_RUNTIME_STATE_AT": "-3"},
    "at_text": {"PROBE_RUNTIME_STATE": "C:/b6/at_text.ss1",
                "PROBE_RUNTIME_STATE_AT": "not a frame"},
    "undecodable": {},
}


def _interpreter():
    try:
        import lupa  # noqa: F401
        return "lupa"
    except ImportError:
        pass
    for name in ("lua5.4", "lua", "luajit"):
        if shutil.which(name):
            return name
    pytest.skip(
        "no Lua interpreter on this host, so the observer cannot be executed: "
        "install lupa (pip, provides Lua 5.4) or lua5.4"
    )


def run_driver(scenario, out_dir, observer=None):
    """Run the shipped observer once and return its parsed READMAP.json."""
    if scenario not in SCENARIOS:
        raise ValueError(scenario)
    observer = Path(observer or OBSERVER)
    assert observer.is_file(), f"{observer} is missing"
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    updates = {
        "PROBE_RUNTIME_DIR": str(out_dir).replace("\\", "/"),
        "PROBE_RUNTIME_FRAMES": "1",
        "PROBE_RUNTIME_BREAKPOINTS": "0",
        "READMAP_B6_OBSERVER": str(observer).replace("\\", "/"),
        "READMAP_B6_SCENARIO": scenario,
    }
    updates.update(SCENARIOS[scenario])
    names = ("PROBE_RUNTIME_DIR", "PROBE_RUNTIME_FRAMES", "PROBE_RUNTIME_BREAKPOINTS",
             "READMAP_B6_OBSERVER", "READMAP_B6_SCENARIO",
             "PROBE_RUNTIME_STATE", "PROBE_RUNTIME_STATE_AT")
    saved = {name: os.environ.get(name) for name in names}
    interpreter = _interpreter()
    if interpreter == "lupa":
        import lupa
        runtime = getattr(lupa, "lua54", lupa).LuaRuntime()
    else:
        driver_path = out_dir / "driver.lua"
        driver_path.write_text(DRIVER, encoding="utf-8")
    try:
        # A scenario that names no AT frame must have the variable absent from the
        # environment the observer reads.
        os.environ.pop("PROBE_RUNTIME_STATE_AT", None)
        os.environ.update(updates)
        if interpreter == "lupa":
            runtime.execute(DRIVER)
        else:
            subprocess.run(
                [shutil.which(interpreter), str(driver_path)],
                check=True, capture_output=True, text=True, timeout=120,
            )
    finally:
        for name, value in saved.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
    readmap = out_dir / "READMAP.json"
    assert readmap.is_file(), (
        f"the observer wrote no READMAP.json for scenario {scenario}; "
        f"api.txt next to it: {(out_dir / 'probe-runtime001-api.txt').is_file()}"
    )
    return json.loads(readmap.read_text(encoding="utf-8"))


def read_api(out_dir):
    api = Path(out_dir) / "probe-runtime001-api.txt"
    assert api.is_file(), f"the observer wrote no api file to {out_dir}"
    return api.read_text(encoding="utf-8")


def test_a_refused_state_is_valid_json_with_a_null_frame(tmp_path):
    """No AT frame at all: the refusal must still serialize as JSON."""
    doc = run_driver("refused", tmp_path)
    assert doc["state"]["frame"] is None, doc["state"]
    assert doc["state"]["ok"] is False, doc["state"]
    assert "is not set" in doc["state"]["result"], doc["state"]


def test_a_load_that_returns_false_is_reported_as_a_failed_load(tmp_path):
    """ok means the load succeeded, not that the call did not raise."""
    doc = run_driver("load_false", tmp_path)
    assert doc["state"]["ok"] is False, doc["state"]
    assert doc["state"]["result"] == "false", doc["state"]
    assert doc["state"]["frame"] == 1, doc["state"]


def test_a_load_error_with_control_characters_round_trips(tmp_path):
    """A quote, a backslash, a newline, a tab and a carriage return survive."""
    doc = run_driver("load_error", tmp_path)
    assert doc["state"]["ok"] is False, doc["state"]
    assert doc["state"]["result"] == LOAD_ERROR, doc["state"]


@pytest.mark.parametrize("scenario, raw", [
    ("at_half", "1.5"),
    ("at_zero", "0"),
    ("at_negative", "-3"),
    ("at_text", "not a frame"),
])
def test_an_at_frame_that_is_not_a_whole_frame_number_is_refused(scenario, raw, tmp_path):
    """A fractional, zero, negative or non-numeric AT frame never loads."""
    doc = run_driver(scenario, tmp_path)
    api = read_api(tmp_path)
    state = doc["state"]
    assert state["ok"] is False, state
    assert state["frame"] is None, state
    assert raw in state["result"], state
    assert "must be an integer >= 1" in state["result"], state
    assert "STATE REFUSED" in api, api
    assert "STATE frame=" not in api, "the state was loaded despite a refused AT frame"


def test_an_undecodable_fire_is_never_reported_as_unread(tmp_path):
    """A broken channel on one span must not read as a quotable zero."""
    doc = run_driver("undecodable", tmp_path)
    assert doc["verdict"].startswith("ABORT"), doc["verdict"]
    spans = {span["id"]: span for span in doc["spans"]}
    control = spans["PC_party"]
    broken = spans[BROKEN_SPAN_ID]
    assert control["hits"] == 1, control
    assert control["result"] == "READ", control
    assert broken["undecodable"] == 1, broken
    assert broken["hits"] == 0, broken
    assert broken["result"] == "UNDECODABLE", broken


def test_an_absent_first_pc_is_json_null_and_not_a_string(tmp_path):
    doc = run_driver("load_false", tmp_path)
    silent = [span for span in doc["spans"] if span["hits"] == 0]
    assert silent, "the fake core read nothing, so every span is silent"
    for span in silent:
        assert span["first_pc"] is None, span
        assert span["first_frame"] is None, span
    assert doc["verdict"], doc


def test_the_readmap_observer_does_not_claim_the_width_is_unexposed():
    source = OBSERVER.read_text(encoding="utf-8")
    assert "Width is not exposed" not in source, (
        "the summary writer and the JSON note still carry the pre-fix width claim"
    )
