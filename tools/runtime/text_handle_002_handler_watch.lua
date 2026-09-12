-- TEXT-HANDLE-002: narrow live path capture for one ROM-resident text record.
--
-- This observer has one target only: record 0x08781CF8, whose +0x04 word is
-- 0x02002641 ("Good luck, Goku!").  It records only the candidate dispatch
-- sites supplied by the prior live consumer capture and a known-live
-- interpreter control.  No emulated input or memory is written.

local TARGET_RECORD = 0x08781CF8
local EVENT_POOL_LO = 0x0877C5A4
local EVENT_POOL_HI = 0x0879B704
local SITES = {
    { name = "candidate_opcode_05_thunk", pc = 0x0801242C },
    { name = "candidate_text_intermediate", pc = 0x0801227E },
    { name = "known_text_consumer", pc = 0x08012230 },
}
local INTERPRETER = 0x08004038

local marker_path = assert(rom011_marker_path, "marker path not provided")
local output_path = os.getenv("TEXTHANDLE002_OUT")
if output_path == nil then
    output_path = marker_path:gsub("[^/\\]+$", "") .. "text-handle-002.jsonl"
end

assert(emu ~= nil and emu.setBreakpoint ~= nil and emu.clearBreakpoint ~= nil,
    "requires the mGBA 0.11 scripted-breakpoint API")
local game_code = emu:getGameCode()
assert(game_code == "BG3E" or game_code == "AGB-BG3E",
    "unexpected game code: " .. tostring(game_code))
assert(emu:romSize() == 8388608, "unexpected ROM size")

local file = assert(io.open(output_path, "w"), "cannot open observer output")
local frames = 0
local liveness_hits = 0
local site_hits = 0

local function safe32(address)
    local ok, value = pcall(function() return emu:read32(address) end)
    if ok and value ~= nil then return value end
    return nil
end

local function hex(value)
    if value == nil then return "null" end
    return string.format('"0x%08X"', value)
end

local function json_string(value)
    return '"' .. value:gsub('\\', '\\\\'):gsub('"', '\\"') .. '"'
end

local function registers()
    local values = {}
    for index = 0, 12 do
        local ok, value = pcall(function() return emu:readRegister("r" .. index) end)
        values["r" .. index] = ok and value or nil
    end
    for _, name in ipairs({ "sp", "lr", "pc", "cpsr" }) do
        local ok, value = pcall(function() return emu:readRegister(name) end)
        values[name] = ok and value or nil
    end
    return values
end

local function register_json(values)
    local fields = {}
    for index = 0, 12 do
        local name = "r" .. index
        fields[#fields + 1] = json_string(name) .. ":" .. hex(values[name])
    end
    for _, name in ipairs({ "sp", "lr", "pc", "cpsr" }) do
        fields[#fields + 1] = json_string(name) .. ":" .. hex(values[name])
    end
    return "{" .. table.concat(fields, ",") .. "}"
end

local function stack_json(sp)
    local words = {}
    for index = 0, 15 do
        words[#words + 1] = hex(safe32(sp + index * 4))
    end
    return "[" .. table.concat(words, ",") .. "]"
end

local function target_register(values)
    for index = 0, 12 do
        local name = "r" .. index
        if values[name] == TARGET_RECORD then return name end
    end
    return nil
end

local function pool_registers_json(values)
    local fields = {}
    for index = 0, 12 do
        local name = "r" .. index
        local value = values[name]
        if value ~= nil and value >= EVENT_POOL_LO and value < EVENT_POOL_HI then
            fields[#fields + 1] = json_string(name) .. ":" .. hex(value)
        end
    end
    return "{" .. table.concat(fields, ",") .. "}"
end

local function record_words_json()
    local words = {}
    for index = 0, 5 do
        words[#words + 1] = hex(safe32(TARGET_RECORD + index * 4))
    end
    return "[" .. table.concat(words, ",") .. "]"
end

local function emit(fields)
    file:write("{" .. table.concat(fields, ",") .. "}\n")
    file:flush()
end

local function capture_site(name, site)
    return function()
        site_hits = site_hits + 1
        local values = registers()
        local target_reg = target_register(values)
        emit({
            '"event":"SITE"',
            '"site":' .. json_string(name),
            '"armed_pc":' .. hex(site),
            '"hit":' .. tostring(site_hits),
            '"frame":' .. tostring(frames),
            '"target_register":' .. (target_reg and json_string(target_reg) or "null"),
            '"target_record":' .. hex(TARGET_RECORD),
            '"record_words":' .. record_words_json(),
            '"packed_handle_at_plus_04":' .. hex(safe32(TARGET_RECORD + 4)),
            '"pool_registers":' .. pool_registers_json(values),
            '"registers":' .. register_json(values),
            '"stack":' .. stack_json(values.sp),
        })
    end
end

for _, spec in ipairs(SITES) do
    local id = emu:setBreakpoint(capture_site(spec.name, spec.pc), spec.pc)
    assert(id ~= nil and id >= 0,
        string.format("breakpoint install failed at 0x%08X", spec.pc))
end

local live_id = emu:setBreakpoint(function()
    liveness_hits = liveness_hits + 1
    if liveness_hits <= 3 then
        emit({
            '"event":"LIVENESS"',
            '"site":"0x08004038"',
            '"count":' .. tostring(liveness_hits),
            '"frame":' .. tostring(frames),
        })
    end
end, INTERPRETER)
assert(live_id ~= nil and live_id >= 0, "interpreter liveness breakpoint install failed")

callbacks:add("frame", function() frames = frames + 1 end)

emit({
    '"event":"ARMED"',
    '"target_record":"0x08781CF8"',
    '"packed_handle":"0x02002641"',
    '"candidate_sites":["0x0801242C","0x0801227E","0x08012230"]',
    '"liveness_site":"0x08004038"',
})

local marker = assert(io.open(marker_path, "w"), "cannot open marker")
marker:write("armed\n")
marker:close()
print([[TEXT-HANDLE-002 armed: target path plus interpreter liveness]])
