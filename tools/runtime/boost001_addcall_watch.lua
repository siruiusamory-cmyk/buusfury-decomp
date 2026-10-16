-- FRIEND-V3-PLAYTEST-BOOST-001: dump the registers at the Bandana hook and at the callee.
--
-- WHY. The trampoline's control flow is proven: BL returns to the callee, the callee
-- returns to the trampoline, `pop {r0-r3}` leaves LR intact, `bx lr` lands on the
-- instruction after the hook, and the stack is restored exactly. The hook therefore
-- fails on its ARGUMENTS or on what the callee does with them, not on its return. This
-- observer records the register state at three sites so that claim is testable:
--
--   0x08004892  the hook itself, where the trampoline reads r4 as the save-block base
--   0x08004448  the add routine's entry, where a real caller would have set r0 and r1
--   0x08004466  the add routine's exit, so a call that completed is visible
--
-- It also reads the word at r4+0xE4 and r4+0xE8, so a bad base shows up as a wild
-- address rather than as a number that has to be interpreted.
--
-- READ-ONLY. Registers and memory only. No key, no write to emulated state.

local HOOK = 0x083C22FC
local ADD_ENTRY = 0x08004448
local ADD_EXIT = 0x08004466

local function knob(name, default)
    return tonumber(os.getenv(name) or "") or default
end

local MAX_FRAMES = knob("ADDCALL_MAX_FRAMES", 9000)
local HEAD = 0x03007F00
local LIMIT = knob("ADDCALL_LIMIT", 24)

local marker_path = rom011_marker_path
assert(type(marker_path) == "string" and #marker_path > 0, "marker path not provided")
local run_dir = marker_path:gsub("[^/\\]+$", "")
local function in_run(name) return run_dir .. name end

assert(emu ~= nil, "mGBA did not attach the emulation core")
local code = emu:getGameCode()
assert(code == "BG3E" or code == "AGB-BG3E", "unexpected game code: " .. tostring(code))

local function status(text)
    local handle = io.open(marker_path, "w")
    if handle then handle:write(text) handle:close() end
end

local function reg8(address)
    local ok, value = pcall(function() return emu:read8(address) end)
    if ok and value then return value end
    return -1
end

local function reg(name)
    local ok, value = pcall(function() return emu:readRegister(name) end)
    if ok and value then return value end
    return -1
end

local function word(address)
    local b0 = reg8(address)
    local b1 = reg8(address + 1)
    local b2 = reg8(address + 2)
    local b3 = reg8(address + 3)
    if b0 < 0 or b1 < 0 or b2 < 0 or b3 < 0 then return -1 end
    return b0 + b1 * 256 + b2 * 65536 + b3 * 16777216
end

local rows = 0
local frames = 0
local out = assert(io.open(in_run("addcall.csv"), "w"))
out:write("seq,site,frame,r0,r1,r2,r3,r4,r5,r6,r7,sp,lr,at_r4_plus_e4,at_r4_plus_e8,stack_head\n")
out:flush()

local function record(site, frame)
    if rows >= LIMIT then return end
    rows = rows + 1
    local r4 = reg("r4")
    local base_count = (r4 ~= -1) and word(r4 + 0xE4) or -1
    local base_entry = (r4 ~= -1) and word(r4 + 0xE8) or -1
    local sp_now = reg("sp")
    local stack_words = ""
    if sp_now > 0 then
        local parts = {}
        for k = 0, 4 do parts[#parts + 1] = string.format("%08X", word(sp_now + k * 4)) end
        stack_words = table.concat(parts, " ")
    end
    out:write(string.format(
        "%d,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%s\n",
        rows, site, frame,
        reg("r0"), reg("r1"), reg("r2"), reg("r3"), r4,
        reg("r5"), reg("r6"), reg("r7"), reg("sp"), reg("lr"),
        base_count, base_entry, stack_words))
    out:flush()
end

status("armed")

-- One breakpoint only. The two observers that worked in this tree each armed exactly
-- one; arming three in a loop produced no hits at all in the run that tried it.
local hooked = {}
local hook_id
hook_id = emu:setBreakpoint(function()
    record("hook", frames)
end, HOOK)

local frames = 0
local out = assert(io.open(in_run("addcall.csv"), "w"))
out:write("seq,site,frame,r0,r1,r2,r3,r4,r5,r6,r7,sp,lr,at_r4_plus_e4,at_r4_plus_e8,stack_head\n")
out:flush()

local function record(site, frame)
    if rows >= LIMIT then return end
    rows = rows + 1
    local r4 = reg("r4")
    local base_count = (r4 ~= -1) and word(r4 + 0xE4) or -1
    local base_entry = (r4 ~= -1) and word(r4 + 0xE8) or -1
    local sp_now = reg("sp")
    local stack_words = ""
    if sp_now > 0 then
        local parts = {}
        for k = 0, 4 do parts[#parts + 1] = string.format("%08X", word(sp_now + k * 4)) end
        stack_words = table.concat(parts, " ")
    end
    out:write(string.format(
        "%d,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%s\n",
        rows, site, frame,
        reg("r0"), reg("r1"), reg("r2"), reg("r3"), r4,
        reg("r5"), reg("r6"), reg("r7"), reg("sp"), reg("lr"),
        base_count, base_entry, stack_words))
    out:flush()
end

status("armed")

local hooked = {}
local function arm(address, site)
    local id
    id = emu:setBreakpoint(function()
        record(site, frames)
    end, address)
    hooked[#hooked + 1] = id
end

arm(HOOK, "hook")
arm(ADD_ENTRY, "add-entry")
arm(ADD_EXIT, "add-exit")

local callback
callback = callbacks:add("frame", function()
    frames = frames + 1
    if frames >= MAX_FRAMES or rows >= LIMIT then
        out:close()
        pcall(function() emu:clearBreakpoint(hook_id) end)
        status(string.format("done:frames=%d rows=%d", frames, rows))
        pcall(function() callbacks:remove(callback) end)
    end
end)
