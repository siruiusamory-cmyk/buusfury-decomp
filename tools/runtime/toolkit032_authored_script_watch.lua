-- TOOLKIT-032: does the engine EXECUTE a script body the SDK authored -- bytes
-- that did not exist in canonical Buu's Fury?
--
-- Read-only with respect to emulated memory and input: this file writes no
-- emulated memory and presses no keys, so the read-only observer guarantee
-- enforced by tests/unit/test_mgba_capture.py stays true. Breakpoints stop and
-- resume the core; they do not modify it.
--
-- WHAT TOOLKIT-031 ALREADY PROVED, and why that is not enough here.
-- TOOLKIT-031 observed the script trampoline 0x0800421E reached five times
-- carrying the authored descriptor 0x0808D788 and its root 0x0808D77C, with the
-- interpreter entered on the same frame. But that descriptor and that script
-- body were CANONICAL -- the SDK selected existing content, it did not create
-- it. So "the attached behavior executed" was proven and "new behavior content
-- executed" was not.
--
-- WHAT THIS OBSERVER MUST ADD. The authored descriptor and the authored script
-- body are now both allocated by the build into the TOOLKIT-028 verified region
-- [0x087EA400, 0x087EA500). Reaching the trampoline is therefore no longer the
-- claim; reaching THE AUTHORED BYTES is. The addresses below are supplied by
-- the build manifest rather than hardcoded guesses, because an observer that
-- watched the wrong address would produce a confident zero.
--
-- THE CENTRAL DISCRIMINATOR. The interpreter 0x08004038 begins by loading the
-- script cursor; the authored body lives at AUTHORED_SCRIPT. A breakpoint at
-- the interpreter whose handler checks whether the live cursor points INTO
-- [AUTHORED_SCRIPT, AUTHORED_SCRIPT + AUTHORED_SCRIPT_LEN) is what separates
-- "some script ran" from "OUR script ran". Recording the first bytes read back
-- from that cursor proves which body the interpreter is about to walk.
--
-- CHANNELS, kept separate so none can be read as another:
--
--   CHANNEL A - TRAMPOLINE. Breakpoint at 0x0800421E. r0 is the descriptor, so
--   r0 says WHICH attachment ran. Carried over unchanged from TOOLKIT-031 so
--   this run reproduces that result as well as extending it.
--
--   CHANNEL B - AUTHORED SCRIPT ENTRY. Breakpoint at the interpreter
--   0x08004038. On entry the handler reads the candidate cursor registers and
--   asks whether any points into the authored body. A hit here is the ticket's
--   required proof: the interpreter entered the newly allocated bytes.
--
--   CHANNEL C - BYTE ATTRIBUTION. On an authored entry, read the 7 bytes at
--   AUTHORED_SCRIPT out of emulated ROM and log them. If the engine is walking
--   our body, those bytes are 00 54 00 4B 07 14 11. This is what makes the
--   claim "the engine executed THESE bytes" rather than "the PC was nearby".
--
--   CHANNEL D - STRUCTURE. The live placement slot's +0x14, sampled
--   periodically, confirming the authored entity carried the authored
--   descriptor for the whole run. NOT execution evidence, and never reported
--   as such.
--
--   CHANNEL E - LIVENESS / POSITIVE CONTROL. Every interpreter entry is
--   counted, authored or not. The interpreter is shared -- dialogue, events and
--   cutscenes all reach it -- so a nonzero count proves the instrument can see
--   script execution at all. Per TOOLKIT-031 and docs/runtime-capture.md, a
--   silent authored channel means NOTHING unless this channel fired.
--
-- HONEST FAILURE MODE. If the breakpoint API is absent the script aborts rather
-- than silently degrading to a poll: an instrument that cannot see execution
-- must not produce rows that look like a negative result.

local TRAMPOLINE  = 0x0800421E   -- ldr r1,[r0,#4] ; bl 0x08004038
local INTERPRETER = 0x08004038   -- the VM dispatch loop

-- Supplied by the launcher from the build manifest. Hardcoding these would risk
-- watching an address the build did not actually use.
local AUTHORED_DESCRIPTOR  = tonumber(os.getenv("TK032_DESCRIPTOR") or "") or 0
local AUTHORED_SCRIPT      = tonumber(os.getenv("TK032_SCRIPT") or "") or 0
local AUTHORED_SCRIPT_LEN  = tonumber(os.getenv("TK032_SCRIPT_LEN") or "") or 7

assert(AUTHORED_DESCRIPTOR ~= 0,
    "TK032_DESCRIPTOR must be supplied from the build manifest")
assert(AUTHORED_SCRIPT ~= 0,
    "TK032_SCRIPT must be supplied from the build manifest")

local ACTIVE_MAP_PTR = 0x03001980
local MAP_ENTRY_BASE = 0x0808E2E0
local MAP_ENTRY_SIZE = 0x38

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = (os.getenv("TOOLKIT032_OUT") or (exp_dir .. "toolkit032-authored-script.csv"))

assert(emu ~= nil, "mGBA did not attach the emulation core")
assert(emu.setBreakpoint and emu.clearBreakpoint,
    "requires the mGBA 0.11 scripted-breakpoint API; a polling fallback " ..
    "cannot see execution and must not be substituted")
-- mGBA 0.11 returns the bare 4-character code (measured: "BG3E"), not the
-- "AGB-" prefixed form some older scripts assert on. Accept both.
local game_code = emu:getGameCode()
assert(game_code == "BG3E" or game_code == "AGB-BG3E",
    "unexpected game code: " .. tostring(game_code))
assert(emu:romSize() == 8388608, "unexpected ROM size")

local file = assert(io.open(log_path, "w"), "cannot open output: " .. tostring(log_path))
file:write("kind,frame,map_index,pc,descriptor,payload,cursor,bytes,verdict,note\n")
file:flush()

local frames = 0
local tramp_hits = 0
local interp_hits = 0
local authored_script_hits = 0

local function safe32(addr)
    local ok, v = pcall(function() return emu:read32(addr) end)
    if ok and v then return v end
    return nil
end

local function safe8(addr)
    local ok, v = pcall(function() return emu:read8(addr) end)
    if ok and v then return v end
    return nil
end

local function hex(v)
    if v == nil then return "" end
    return string.format("0x%08X", v)
end

local function current_map()
    local entry = safe32(ACTIVE_MAP_PTR)
    if not entry or entry < MAP_ENTRY_BASE then return nil end
    return (entry - MAP_ENTRY_BASE) // MAP_ENTRY_SIZE
end

-- The authored body, read back out of the running machine's ROM view. If the
-- interpreter is walking our allocation these are the bytes it sees.
local function authored_bytes()
    local parts = {}
    for i = 0, AUTHORED_SCRIPT_LEN - 1 do
        local b = safe8(AUTHORED_SCRIPT + i)
        if b == nil then return "" end
        parts[#parts + 1] = string.format("%02X", b)
    end
    return table.concat(parts, " ")
end

local function in_authored_script(addr)
    if addr == nil then return false end
    return addr >= AUTHORED_SCRIPT and addr < (AUTHORED_SCRIPT + AUTHORED_SCRIPT_LEN)
end

local function write_row(kind, pc, descriptor, payload, cursor, bytes, verdict, note)
    local map = current_map()
    file:write(string.format("%s,%d,%s,%s,%s,%s,%s,%s,%s,%s\n",
        kind, frames,
        map and tostring(map) or "",
        hex(pc), hex(descriptor), hex(payload), hex(cursor),
        bytes or "", verdict or "", note or ""))
    file:flush()
end

-- CHANNEL A: the trampoline, with the descriptor that selected it. Reproduces
-- TOOLKIT-031's measurement against the authored descriptor of THIS build.
local bp_tramp = emu:setBreakpoint(function(info)
    tramp_hits = tramp_hits + 1
    local pc = tonumber(emu:readRegister("pc"))
    local r0 = tonumber(emu:readRegister("r0"))
    local payload = r0 and safe32(r0 + 4) or nil
    local verdict, note
    if r0 == AUTHORED_DESCRIPTOR and payload == AUTHORED_SCRIPT then
        verdict = "AUTHORED-DESCRIPTOR"
        note = "authored descriptor reached trampoline carrying authored script pointer"
    elseif r0 == AUTHORED_DESCRIPTOR then
        verdict = "AUTHORED-DESC-BAD-PAYLOAD"
        note = "authored descriptor with unexpected payload"
    else
        verdict = "OTHER-CANONICAL"
        note = "other descriptor executed"
    end
    write_row("TRAMP", pc, r0, payload, nil, nil, verdict, note)
end, TRAMPOLINE)

-- CHANNEL B + C + E: the interpreter. Every entry counts for liveness; an entry
-- whose cursor points into the authored allocation is the ticket's proof.
--
-- The cursor register is not assumed. The trampoline does `ldr r1,[r0,#4]` then
-- calls the interpreter, so r1 is the expected carrier, but r0 and r2 are also
-- probed and whichever lands inside the authored body is recorded by name. That
-- avoids both a false negative from watching the wrong register and a false
-- positive from asserting a register convention that was never measured.
local bp_interp = emu:setBreakpoint(function(info)
    interp_hits = interp_hits + 1
    local pc = tonumber(emu:readRegister("pc"))
    local hit_reg, hit_val = nil, nil
    for _, name in ipairs({"r1", "r0", "r2", "r3"}) do
        local ok, v = pcall(function() return tonumber(emu:readRegister(name)) end)
        if ok and in_authored_script(v) then
            hit_reg, hit_val = name, v
            break
        end
    end
    if hit_reg then
        authored_script_hits = authored_script_hits + 1
        write_row("AUTHORED-SCRIPT", pc, AUTHORED_DESCRIPTOR, AUTHORED_SCRIPT,
            hit_val, authored_bytes(), "AUTHORED-SCRIPT-ENTERED",
            "interpreter entered authored body via " .. hit_reg ..
            "; authored_hits=" .. tostring(authored_script_hits))
    elseif interp_hits <= 20 or interp_hits % 500 == 0 then
        -- Liveness only, logged sparsely: this fires often and the file is
        -- evidence, not a trace.
        write_row("INTERP", pc, nil, nil, nil, nil, "LIVENESS",
            "interpreter reached; liveness only, hits=" .. tostring(interp_hits))
    end
end, INTERPRETER)

local callback_id
callback_id = callbacks:add("frame", function()
    frames = frames + 1
    -- CHANNEL D: periodic structural confirmation, clearly labelled so it is
    -- never mistaken for execution evidence. A silent execution channel means
    -- nothing if the authored entity was never instantiated at all.
    if frames % 60 == 0 then
        local desc, payload = nil, nil
        local entry = safe32(ACTIVE_MAP_PTR)
        if entry and entry >= MAP_ENTRY_BASE then
            local count = safe8(entry + 0x04)
            local array = safe32(entry + 0x14)
            if count and array and count > 0 then
                local slot = safe32(array + (count - 1) * 4)
                if slot then
                    desc = safe32(slot + 0x14)
                    if desc then payload = safe32(desc + 4) end
                end
            end
        end
        local verdict = "STRUCT"
        if desc == AUTHORED_DESCRIPTOR and payload == AUTHORED_SCRIPT then
            verdict = "AUTHORED-ATTACHMENT-LIVE"
        end
        write_row("STRUCT", nil, desc, payload, nil, nil, verdict,
            "structural sample only; not execution")
    end
    -- Bounded, but long enough that the run is ended by the operator closing
    -- the window rather than by the observer expiring mid-experiment.
    if frames >= 216000 then
        if bp_tramp then emu:clearBreakpoint(bp_tramp) end
        if bp_interp then emu:clearBreakpoint(bp_interp) end
        write_row("SUMMARY", nil, nil, nil, nil, authored_bytes(), "SUMMARY",
            "trampoline_hits=" .. tostring(tramp_hits) ..
            " interpreter_hits=" .. tostring(interp_hits) ..
            " authored_script_hits=" .. tostring(authored_script_hits))
        callbacks:remove(callback_id)
        local marker = assert(io.open(done_path, "w"))
        marker:write("done:TOOLKIT032AuthoredScriptWatch")
        marker:close()
    end
end)
