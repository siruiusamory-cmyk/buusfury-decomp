"""The PROBE-RUNTIME-001 read-map observer's JSON writer, executed.

These tests run the SHIPPED observer with a fake emulation core, drive one frame
so it finalizes, and parse the READMAP.json it actually wrote. The cases carry the
values the writer has to get right: a refused state (no AT frame), a load that
returned false without raising, a load error carrying a quote, a backslash, a
newline, a tab and a carriage return, and a span whose first_pc is absent.

The observer is Lua. A Lua interpreter is located at run time: the lupa binding
(Lua 5.4, the version mGBA embeds) if importable, else lua5.4/lua/luajit on PATH.
When no interpreter exists the tests SKIP with that reason instead of passing on a
substring of the source, because a substring proves nothing about the bytes the
writer emits.
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
emu.setRangeWatchpoint = function() return id() end
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
frame_cb()
'''

# The scenario's two state variables. "refused" is the path-without-AT case.
SCENARIOS = {
    "refused": {"PROBE_RUNTIME_STATE": "C:/b6/refused.ss1"},
    "load_false": {"PROBE_RUNTIME_STATE": "C:/b6/load_false.ss1",
                   "PROBE_RUNTIME_STATE_AT": "1"},
    "load_error": {"PROBE_RUNTIME_STATE": "C:/b6/load_error.ss1",
                   "PROBE_RUNTIME_STATE_AT": "1"},
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
        "no Lua interpreter on this host, so the observer's JSON writer cannot be "
        "executed: install lupa (pip, provides Lua 5.4) or lua5.4"
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
        # The refusal case is a state path with NO AT frame, so that variable must
        # be absent from the environment the observer reads.
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


def test_a_refused_state_is_valid_json_with_a_null_frame(tmp_path):
    """No AT frame: the refusal must still serialize as JSON."""
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
