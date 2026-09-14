-- MAP-VIS-002: read-only provenance observer for BG char/screen copy callsites.
-- No emulated memory or input is modified. Host output stays in the ignored
-- run directory derived from the launcher's marker path.

local CHAR_COPY = 0x08009C72
local SCREEN_COPY = 0x08007D5C
local DECOMPRESS = 0x0803D940
local ACTIVE_MAP_PTR = 0x03001980
local MAP_ENTRY_BASE = 0x0808E2E0
local MAP_ENTRY_SIZE = 0x38

assert(emu and emu.setBreakpoint and emu.clearBreakpoint,
    "requires mGBA 0.11 scripted-breakpoint API")
local code = emu:getGameCode()
assert(code == "BG3E" or code == "AGB-BG3E", "unexpected game code")
assert(emu:romSize() == 8388608, "unexpected ROM size")

local marker_path = assert(rom011_marker_path, "marker path not provided")
local run_dir = marker_path:match("^(.*)/[^/]*$")
local output_path = run_dir .. "/mapvis002-bg-provenance.csv"
local summary_path = run_dir .. "/mapvis002-bg-summary.txt"
local file = assert(io.open(output_path, "w"), "cannot open provenance output")
file:write("kind,frame,map_index,pc,r0,r1,r2,r3,r4,r5,r6,r7\n")
file:flush()

local frame = 0
local counts = { CHAR = 0, SCREEN = 0, DECOMPRESS = 0 }

local function reg(name)
    local ok, value = pcall(function() return emu:readRegister(name) end)
    if ok and value ~= nil then return tonumber(value) end
    return nil
end

local function safe32(address)
    local ok, value = pcall(function() return emu:read32(address) end)
    if ok and value ~= nil then return tonumber(value) end
    return nil
end

local function map_index()
    local entry = safe32(ACTIVE_MAP_PTR)
    if entry == nil or entry < MAP_ENTRY_BASE then return nil end
    local offset = entry - MAP_ENTRY_BASE
    if offset % MAP_ENTRY_SIZE ~= 0 then return nil end
    local index = offset // MAP_ENTRY_SIZE
    if index < 0 or index >= 452 then return nil end
    return index
end

local function hex(value)
    if value == nil then return "" end
    return string.format("0x%08X", value)
end

local function row(kind)
    counts[kind] = counts[kind] + 1
    file:write(string.format("%s,%d,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n",
        kind, frame, map_index() or "", hex(reg("pc")), hex(reg("r0")),
        hex(reg("r1")), hex(reg("r2")), hex(reg("r3")), hex(reg("r4")),
        hex(reg("r5")), hex(reg("r6")), hex(reg("r7"))))
    file:flush()
end

local char_id
char_id = emu:setBreakpoint(function()
    row("CHAR")
    if counts.CHAR >= 24 then emu:clearBreakpoint(char_id) end
end, CHAR_COPY)

local screen_id
screen_id = emu:setBreakpoint(function()
    row("SCREEN")
    if counts.SCREEN >= 16 then emu:clearBreakpoint(screen_id) end
end, SCREEN_COPY)

local decompress_id
decompress_id = emu:setBreakpoint(function()
    if counts.DECOMPRESS < 8 then row("DECOMPRESS")
    else counts.DECOMPRESS = counts.DECOMPRESS + 1 end
end, DECOMPRESS)

callbacks:add("frame", function()
    frame = frame + 1
    if frame == 1 then
        local marker = assert(io.open(marker_path, "w"))
        marker:write("armed\n")
        marker:close()
    end
    if frame == 180 then
        local summary = assert(io.open(summary_path, "w"))
        summary:write(string.format("frames=%d char=%d screen=%d decompress=%d\n",
            frame, counts.CHAR, counts.SCREEN, counts.DECOMPRESS))
        summary:close()
    end
end)
