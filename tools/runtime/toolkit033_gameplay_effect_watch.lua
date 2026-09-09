-- TOOLKIT-033 read-only observer for one authored native effect.
--
-- It proves four independent edges: authored descriptor -> authored script,
-- native_stack opcode -> slot 178, slot 178 entry -> three expected stack
-- arguments, and the rendered frame captured after the handler. It never
-- writes emulated memory and never drives input.

local TRAMPOLINE    = 0x0800421E
local INTERPRETER   = 0x08004038
local NATIVE_STACK  = 0x08003CBE
local TEXT_HANDLER  = 0x08003030

local DESCRIPTOR = tonumber(os.getenv("TK033_DESCRIPTOR") or "") or 0
local SCRIPT = tonumber(os.getenv("TK033_SCRIPT") or "") or 0
local SCRIPT_LEN = tonumber(os.getenv("TK033_SCRIPT_LEN") or "") or 0
local EXPECT_HANDLER = (os.getenv("TK033_EXPECT_HANDLER") or "1") == "1"
local EXPECT_TEXT = tonumber(os.getenv("TK033_EXPECT_TEXT") or "1525")
local EXPECT_X = tonumber(os.getenv("TK033_EXPECT_X") or "120")
local EXPECT_Y = tonumber(os.getenv("TK033_EXPECT_Y") or "105")

assert(DESCRIPTOR ~= 0 and SCRIPT ~= 0 and SCRIPT_LEN > 0,
    "TK033 descriptor/script identity must come from the generated build")

local ACTIVE_MAP_PTR = 0x03001980
local MAP_ENTRY_BASE = 0x0808E2E0
local MAP_ENTRY_SIZE = 0x38
local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = os.getenv("TOOLKIT033_OUT") or (exp_dir .. "toolkit033-effect.csv")

assert(emu and emu.setBreakpoint and emu.clearBreakpoint,
    "requires the mGBA 0.11 scripted-breakpoint API")
local game_code = emu:getGameCode()
assert(game_code == "BG3E" or game_code == "AGB-BG3E",
    "unexpected game code: " .. tostring(game_code))
assert(emu:romSize() == 8388608, "unexpected ROM size")

local file = assert(io.open(log_path, "w"), "cannot open observer output")
file:write("kind,frame,map_index,pc,descriptor,payload,cursor,depth,arg0,arg1,arg2,verdict,note\n")
file:flush()

local frames = 0
local authored_entries = 0
local native_opcode_hits = 0
local handler_hits = 0
local last_authored_frame = -1
local last_authored_native_frame = -1
local screenshots = {}

local function safe8(address)
    local ok, value = pcall(function() return emu:read8(address) end)
    if ok then return value end
end

local function safe32(address)
    local ok, value = pcall(function() return emu:read32(address) end)
    if ok then return value end
end

local function reg(name)
    local ok, value = pcall(function() return tonumber(emu:readRegister(name)) end)
    if ok then return value end
end

local function hex(value)
    if value == nil then return "" end
    return string.format("0x%08X", value)
end

local function current_map()
    local entry = safe32(ACTIVE_MAP_PTR)
    if not entry or entry < MAP_ENTRY_BASE then return nil end
    return (entry - MAP_ENTRY_BASE) // MAP_ENTRY_SIZE
end

local function row(kind, descriptor, payload, cursor, depth, a0, a1, a2, verdict, note)
    local map = current_map()
    file:write(string.format("%s,%d,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n",
        kind, frames, map and tostring(map) or "", hex(reg("pc")),
        hex(descriptor), hex(payload), hex(cursor), depth or "",
        a0 or "", a1 or "", a2 or "", verdict or "", note or ""))
    file:flush()
end

local function in_script(value)
    return value and value >= SCRIPT and value < SCRIPT + SCRIPT_LEN
end

local function schedule_screenshots(prefix)
    if #screenshots > 0 then return end
    for _, delay in ipairs({1, 5, 15}) do
        screenshots[#screenshots + 1] = {
            frame = frames + delay,
            path = exp_dir .. prefix .. "-plus" .. tostring(delay) .. ".png",
        }
    end
end

local bp_tramp = emu:setBreakpoint(function()
    local descriptor = reg("r0")
    local payload = descriptor and safe32(descriptor + 4) or nil
    if descriptor == DESCRIPTOR then
        row("TRAMP", descriptor, payload, nil, nil, nil, nil, nil,
            payload == SCRIPT and "AUTHORED-DESCRIPTOR" or "BAD-PAYLOAD",
            "authored descriptor reached script trampoline")
    end
end, TRAMPOLINE)

local bp_interp = emu:setBreakpoint(function()
    local cursor, carrier
    for _, name in ipairs({"r1", "r0", "r2", "r3"}) do
        local value = reg(name)
        if in_script(value) then cursor, carrier = value, name; break end
    end
    if cursor then
        authored_entries = authored_entries + 1
        last_authored_frame = frames
        row("SCRIPT", DESCRIPTOR, SCRIPT, cursor, nil, nil, nil, nil,
            "AUTHORED-SCRIPT", "cursor carried by " .. carrier)
        if not EXPECT_HANDLER then schedule_screenshots("negative") end
    end
end, INTERPRETER)

local bp_native = emu:setBreakpoint(function()
    -- At 0x08003CC0 the engine loads r3=[r1], then the slot byte from [r3].
    -- Read that exact live cursor before either instruction retires. Requiring
    -- the authored interpreter-entry frame binds the opcode to this script.
    if frames == last_authored_frame then
        native_opcode_hits = native_opcode_hits + 1
        local cursor_holder = reg("r1")
        local cursor = cursor_holder and safe32(cursor_holder) or nil
        local slot = cursor and safe8(cursor) or nil
        if slot == 178 then last_authored_native_frame = frames end
        row("NATIVE-OPCODE", DESCRIPTOR, SCRIPT, cursor, nil,
            slot, nil, nil, slot == 178 and "SLOT-178" or "WRONG-SLOT",
            "live native_stack cursor and slot in authored-entry frame")
    end
end, NATIVE_STACK)

local bp_handler = emu:setBreakpoint(function()
    if frames ~= last_authored_native_frame then return end
    handler_hits = handler_hits + 1
    -- Slot handlers receive the VM stack object in r0. The handler's first pop
    -- loads [r0], subtracts one, stores it back, scales it by four, adds r0 and
    -- reads [r0+4+index*4]. Thus [r0] is the depth/index (called the VM stack
    -- pointer in the static notes), not an address; following words are values.
    local stack = reg("r0")
    local depth = stack and safe32(stack) or nil
    local a0 = stack and safe32(stack + 4) or nil
    local a1 = stack and safe32(stack + 8) or nil
    local a2 = stack and safe32(stack + 12) or nil
    local expected = depth and depth >= 3 and a0 == EXPECT_TEXT and
        a1 == EXPECT_X and a2 == EXPECT_Y
    row("HANDLER", DESCRIPTOR, SCRIPT, nil, depth, a0, a1, a2,
        expected and "EXPECTED-ARGS" or "OTHER-ARGS",
        "native slot 178 handler entry")
    if expected then schedule_screenshots("effect") end
end, TEXT_HANDLER)

local callback_id
callback_id = callbacks:add("frame", function()
    frames = frames + 1
    for _, shot in ipairs(screenshots) do
        if shot.frame == frames then
            emu:screenshot(shot.path)
            row("SCREENSHOT", DESCRIPTOR, SCRIPT, nil, nil, nil, nil, nil,
                "CAPTURED", shot.path:gsub(",", "_"))
        end
    end
    if frames >= 216000 then
        emu:clearBreakpoint(bp_tramp)
        emu:clearBreakpoint(bp_interp)
        emu:clearBreakpoint(bp_native)
        emu:clearBreakpoint(bp_handler)
        row("SUMMARY", nil, nil, nil, nil, nil, nil, nil, "SUMMARY",
            "authored_entries=" .. authored_entries ..
            " native_opcode_hits=" .. native_opcode_hits ..
            " handler_hits=" .. handler_hits)
        callbacks:remove(callback_id)
        local marker = assert(io.open(done_path, "w"))
        marker:write("done:TOOLKIT033GameplayEffectWatch")
        marker:close()
    end
end)
