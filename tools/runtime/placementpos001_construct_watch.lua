-- PLACEMENT-POS-001 Phase 1/2: capture the placement position construction chain.
--
-- PHASE 2 UPDATE (folded Phase 1b). The Phase 1 run proved raw_0 -> actor+0x1A0
-- at runtime (40/40) but could NOT read actor+0x1A4 post-store: mGBA fires a
-- setBreakpoint callback BEFORE the trapped instruction runs, and the old
-- store_high trap sat exactly on 0x0800FDD8 (the str to +0x1A4), so that write
-- had not happened yet (0/40 match on +0x1A4). The fix here is one SETTLED trap
-- at 0x0800FDDA -- the first instruction AFTER 0x0800FDD8 -- where BOTH
-- 0x0800FDD2 (str -> +0x1A0) and 0x0800FDD8 (str -> +0x1A4) are committed. Now
-- actor+0x1A0>>8 == raw_0 AND actor+0x1A4>>8 == raw_1 are both TESTABLE from one
-- row. The pre-write store_low/store_high traps are removed; read_low
-- (0x0800FDC8) and liveness (0x08004038) stay.
--
-- Read-only with respect to emulated memory and input. This file sets
-- breakpoints and READS CPU registers and memory at the stop; it contains no
-- key-writing or memory-writing calls, so the read-only observer guarantee
-- enforced by tests/unit/test_mgba_capture.py stays true. Any input driving
-- (walking the player into map 40 so the mutated placement constructs) is done
-- BY THE HUMAN operator, never by this script.
--
-- WHY THIS EXISTS. PLACEMENT-POS-001 Phase 0 (docs/research/
-- PLACEMENT_POSITION_PROVENANCE.md) located, statically, where a placement's
-- record +0x0C position word is read and stored during construction:
--
--   inside function 0x0800FD74, r5 = &placement[+0x0C], r4 = actor object base:
--     0x0800FDC8  ldrsh r2,[r5,#0]   read position_raw_0 (low HW), sign-extended
--     0x0800FDCC  ldrsh r5,[r5,#2]   read position_raw_1 (high HW), sign-extended
--     0x0800FDD0  lsls  r2,r2,#8     position_raw_0 << 8   (Q8, interpreted)
--     0x0800FDD2  str   r2,[r1]      store to actor+0x1A0
--     0x0800FDD6  lsls  r3,r5,#8     position_raw_1 << 8
--     0x0800FDD8  str   r3,[r0]      store to actor+0x1A4
--
-- Phase 0 assigns NO axis and NO unit. This observer captures the runtime
-- values so Phase 1 can correlate actor+0x1A0/+0x1A4 (>>8) against the object's
-- actual on-screen position. It does NOT itself decide the axis.
--
-- WHY A BREAKPOINT, NOT A POLL. Construction is a transient event: r4 (the
-- actor base) only exists in that register at the store. A per-frame poll
-- cannot see it. Placement construction fires during a MAP LOAD, so the human
-- must, after arming, walk the player into a fresh area (e.g. through the
-- map-39 doorway in savestate 58228e1d, which node 666922c9 recorded as leading
-- to a transition). A savestate already sitting on a map has already run
-- construction and will NOT re-fire this breakpoint (mgba-runtime SKILL section
-- 5 ordering rule).
--
-- LIVENESS (mgba-runtime SKILL section 8). A silent target proves nothing. A
-- second breakpoint on the shared script interpreter 0x08004038 (reached by
-- dialogue/cutscenes) is the liveness channel. In the closure:
--   target silent + liveness silent  -> nothing proven, instrument unproven
--   target silent + liveness fires   -> real negative (that path not taken)
--   target fires                     -> construction observed
--
-- VEHICLE. This runs under the 0.11 dev build that exposes emu:setBreakpoint
-- (build/tools/mgba-dev/..., verified by VersionInfo, not path). It is injected
-- via inject_mgba_lua.ps1 into a human-played, free-running core -- NOT the GDB
-- launcher (under which a frame callback records zero ticks). Nothing in this
-- script owns the emulator's lifetime; the operator ends the run by closing the
-- window.

-- SETTLED PC: the first instruction AFTER both stores (0x0800FDD2 -> +0x1A0 and
-- 0x0800FDD8 -> +0x1A4). Trapping here (pre-instruction callback) means BOTH
-- writes are already committed, so reading r4+0x1A0 and r4+0x1A4 yields the
-- final Q8 values. Disasm: 0x0800FDDA ldr r0,[r4,#0x58].
local BP_SETTLED    = 0x0800FDDA
-- Read PC (raw halfwords still in [r5]); captured too, so the raw values and
-- the actor base are both witnessed at one construction.
local BP_READ_LOW   = 0x0800FDC8   -- ldrsh r2,[r5,#0]
local BP_LIVENESS   = 0x08004038   -- shared script interpreter (liveness)

local ACTOR_OFF_1A0 = 0x1A0
local ACTOR_OFF_1A4 = 0x1A4

-- Output path is derived from the injected marker path (validated beneath the
-- ignored build tree by inject_mgba_lua.ps1), matching the toolkit029 shape.
local run_dir = nil
if type(rom011_marker_path) == "string" then
    run_dir = rom011_marker_path:match("^(.*)/[^/]*$")
end
local function in_run(name)
    if run_dir then return run_dir .. "/" .. name end
    return name
end

local out = os.getenv("PLACEMENTPOS001_OUT") or in_run("placementpos001-construct.csv")
local file = assert(io.open(out, "w"), "cannot open output: " .. tostring(out))
file:write("event,pc,r4_actor_base,r5,position_raw_0,position_raw_1,",
           "actor_1A0,actor_1A4,actor_1A0_asr8,actor_1A4_asr8,note\n")
file:flush()

assert(emu ~= nil, "mGBA did not attach the emulation core")
-- The 0.11 dev build returns the BARE game code "BG3E" (SKILL section 2); accept
-- both spellings so this assert does not become the misleading failure.
local code = emu:getGameCode()
assert(code == "BG3E" or code == "AGB-BG3E", "unexpected game code: " .. tostring(code))
assert(emu:romSize() == 8388608, "unexpected ROM size")

local function safe32(addr)
    local ok, v = pcall(function() return emu:read32(addr) end)
    if ok and v then return v end
    return nil
end

-- 32-bit arithmetic shift right by 8 (the inverse of the construction <<8), so
-- the row can show the integer coordinate the engine reads back at 0x080101AA.
local function asr8(v)
    if v == nil then return nil end
    local shifted = v >> 8
    if v >= 0x80000000 then            -- sign bit set: propagate it
        shifted = shifted | (0xFF000000)
        shifted = shifted & 0xFFFFFFFF
        shifted = shifted - 0x100000000  -- present as a signed value
    end
    return shifted
end

local function reg(name)
    -- mGBA exposes CPU registers via emu:readRegister on the dev build; guard it
    -- so a missing API degrades to an empty cell rather than crashing the run.
    local ok, v = pcall(function() return emu:readRegister(name) end)
    if ok and v then return v end
    return nil
end

local function h(v) if v == nil then return "" end return string.format("0x%08X", v) end
local function d(v) if v == nil then return "" end return tostring(v) end

local liveness_fired = false

-- SETTLED: both stores committed. Read r4+0x1A0 and r4+0x1A4 off the actor base
-- (r4, rediscovered per load -- never hard-coded). actor_1A0_asr8 must equal
-- raw_0 and actor_1A4_asr8 must equal raw_1 for a clean construction; that is
-- the Phase 2 test the CSV validates.
emu:setBreakpoint(function()
    local r4 = reg("r4")
    local r5 = reg("r5")
    local a1a0 = (r4 ~= nil) and safe32(r4 + ACTOR_OFF_1A0) or nil
    local a1a4 = (r4 ~= nil) and safe32(r4 + ACTOR_OFF_1A4) or nil
    file:write(string.format("settled,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n",
        h(BP_SETTLED), h(r4), h(r5), "", "",
        h(a1a0), h(a1a4), d(asr8(a1a0)), d(asr8(a1a4)),
        "both stores committed; 1A0>>8==raw_0 and 1A4>>8==raw_1 testable"))
    file:flush()
end, BP_SETTLED)

-- READ-LOW: raw halfwords still addressable via r5 = &placement[+0x0C].
emu:setBreakpoint(function()
    local r4 = reg("r4")
    local r5 = reg("r5")
    local raw0, raw1 = nil, nil
    if r5 ~= nil then
        local w = safe32(r5)
        if w then
            raw0 = w & 0xFFFF
            raw1 = (w >> 16) & 0xFFFF
        end
    end
    file:write(string.format("read_low,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n",
        h(BP_READ_LOW), h(r4), h(r5), d(raw0), d(raw1),
        "", "", "", "",
        "raw halfwords at &placement+0x0C via r5"))
    file:flush()
end, BP_READ_LOW)

-- LIVENESS.
emu:setBreakpoint(function()
    if not liveness_fired then
        liveness_fired = true
        file:write(string.format("liveness,%s,,,,,,,,,%s\n",
            h(BP_LIVENESS), "interpreter 0x08004038 reached -> core is live"))
        file:flush()
    end
end, BP_LIVENESS)

-- Armed marker: written only after every breakpoint is installed, so its
-- presence means the observer is genuinely live. inject_mgba_lua.ps1 supplies
-- the path and waits on it.
local marker = os.getenv("PLACEMENTPOS001_MARKER") or rom011_marker_path
if type(marker) == "string" then
    local m = io.open(marker, "w")
    if m then m:write("armed\n") m:close() end
end
