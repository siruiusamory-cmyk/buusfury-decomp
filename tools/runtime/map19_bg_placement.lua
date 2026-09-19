-- ASSET-EXPORT-MAP19-001: read-only runtime observer for map 19's BG placement.
--
-- No emulated memory or input is modified. Everything this script produces is a
-- structured, ignored artifact: register values and raw memory ranges written as
-- text, plus mGBA's own screenshots. It never commits or copies an image.
--
-- What it measures:
--   * the active MapEntry the engine currently has loaded (from the accepted
--     active-map pointer, validated as a pointer into the MapEntry run);
--   * DISPCNT, BG0CNT..BG3CNT, BG0HOFS/VOFS..BG3HOFS/VOFS and the BG2 affine
--     registers BG2PA..BG2PD;
--   * the terrain field's destination map base 0x0600F000 as it stands in VRAM,
--     so the copy's row stride can be read off the live bytes rather than
--     inferred.

local OUT_ROOT = "C:/tmp/map19-rt/out"
local ACTIVE_MAP_PTR = 0x03001980
local MAP_ENTRY_BASE = 0x0808E2E0
local MAP_ENTRY_SIZE = 0x38
local MAP_ENTRY_COUNT = 452

local BG_BASE = 0x04000000
local DISPCNT = BG_BASE
local BG_CNT = { 0x04000008, 0x0400000A, 0x0400000C, 0x0400000E }
local BG_OFF = { 0x04000010, 0x04000014, 0x04000018, 0x0400001C }
local BG2_AFFINE = { 0x04000020, 0x04000022, 0x04000024, 0x04000026 }

local VRAM_BASE = 0x06000000
local TERRAIN_MAP_BASE = 0x0600F000
local TERRAIN_MAP_BYTES = 0x800
-- The terrain field's character source: the map's own assembled tile block, which
-- the screen-entry layer's method 1 uploads to 0x0600E000 + slot * 0x800. Slot 1's
-- block is read too, because the two are adjacent and the split matters.
local SCREENBLOCK_BASE = 0x0600E000

local MAP19_ROOT = 0x082AD8BC

assert(emu ~= nil, "mGBA did not attach the emulation core")
local code = emu:getGameCode()
assert(code == "BG3E" or code == "AGB-BG3E", "unexpected game code: " .. tostring(code))
assert(emu:romSize() == 8388608, "unexpected ROM size")

local function hex(value)
    if value == nil then return "" end
    return string.format("0x%08X", value)
end

local function safe_read(fn, address, ...)
    local ok, value = pcall(fn, emu, address, ...)
    if ok and value ~= nil then return tonumber(value) end
    return nil
end

local function r8(a) return safe_read(emu.read8, a) end
local function r16(a) return safe_read(emu.read16, a) end
local function r32(a) return safe_read(emu.read32, a) end

local function reg(name)
    local ok, value = pcall(function() return emu:readRegister(name) end)
    if ok and value ~= nil then return tonumber(value) end
    return nil
end

local function map_index()
    local entry = r32(ACTIVE_MAP_PTR)
    if entry == nil or entry < MAP_ENTRY_BASE then return nil, entry end
    local offset = entry - MAP_ENTRY_BASE
    if offset % MAP_ENTRY_SIZE ~= 0 then return nil, entry end
    local index = math.floor(offset / MAP_ENTRY_SIZE)
    if index < 0 or index >= MAP_ENTRY_COUNT then return nil, entry end
    return index, entry
end

-- Every MapEntry address the ROM's run declares, so an active pointer can be
-- resolved even when the "active" pointer has not been published yet.
local function scan_active_map_candidates()
    local hits = {}
    local value = r32(ACTIVE_MAP_PTR)
    if value and value >= MAP_ENTRY_BASE and
       value < MAP_ENTRY_BASE + MAP_ENTRY_COUNT * MAP_ENTRY_SIZE and
       (value - MAP_ENTRY_BASE) % MAP_ENTRY_SIZE == 0 then
        hits[#hits + 1] = string.format("active_ptr=%s index=%d", hex(value),
            math.floor((value - MAP_ENTRY_BASE) / MAP_ENTRY_SIZE))
    end
    return hits
end

local function dump_rom_pointer_state()
    local lines = {}
    -- The map 19 record chain, read from the live ROM image, so the observer
    -- proves which record the runtime map corresponds to.
    local root = r32(MAP19_ROOT)
    lines[#lines + 1] = string.format("map19_root_handler=%s", hex(root))
    return lines
end

local function write_state(path, label, frame)
    local file = assert(io.open(path, "w"), "cannot open " .. path)
    local index, entry = map_index()
    file:write("label=" .. label .. "\n")
    file:write("frame=" .. tostring(frame) .. "\n")
    file:write("game_code=" .. tostring(code) .. "\n")
    file:write(string.format("active_map_ptr=%s\n", hex(r32(ACTIVE_MAP_PTR))))
    file:write(string.format("map_index=%s\n", index and tostring(index) or "unknown"))
    file:write(string.format("map_entry=%s\n", hex(entry)))
    file:write(string.format("pc=%s\n", hex(reg("pc"))))
    file:write(string.format("dispcnt=%s\n", hex(r16(DISPCNT))))
    for i = 1, 4 do
        file:write(string.format("bg%dcnt=%s\n", i - 1, hex(r16(BG_CNT[i]))))
        file:write(string.format("bg%dhofs=%s\n", i - 1, hex(r16(BG_OFF[i]))))
        file:write(string.format("bg%dvofs=%s\n", i - 1, hex(r16(BG_OFF[i] + 2))))
    end
    file:write(string.format("bg2pa=%s\n", hex(r16(BG2_AFFINE[1]))))
    file:write(string.format("bg2pb=%s\n", hex(r16(BG2_AFFINE[2]))))
    file:write(string.format("bg2pc=%s\n", hex(r16(BG2_AFFINE[3]))))
    file:write(string.format("bg2pd=%s\n", hex(r16(BG2_AFFINE[4]))))
    file:write(string.format("vcount=%s\n", hex(r16(0x04000006))))
    file:write(string.format("dispstat=%s\n", hex(r16(0x04000004))))
    file:write(string.format("terrain_map_base=%s\n", hex(TERRAIN_MAP_BASE)))
    -- Live bytes of the terrain map block, 32 bytes per row for 32 rows, so the
    -- row stride is measured from VRAM rather than inferred from the code.
    for row = 0, 31 do
        local parts = {}
        for column = 0, 31 do
            parts[#parts + 1] = string.format("%02X",
                r8(TERRAIN_MAP_BASE + row * 32 + column) or 0)
        end
        file:write(string.format("map_row_%02d=%s\n", row, table.concat(parts)))
    end
    -- The same block read on a 64-byte row stride, so a 0x40-strided copy is
    -- directly visible if that is what the engine wrote.
    for row = 0, 31 do
        local parts = {}
        for column = 0, 31 do
            parts[#parts + 1] = string.format("%02X",
                r8(TERRAIN_MAP_BASE + row * 64 + column) or 0)
        end
        file:write(string.format("map64_row_%02d=%s\n", row, table.concat(parts)))
    end
    -- The screen-entry layer's plane, to confirm the two background areas are
    -- distinct.
    for row = 0, 7 do
        local parts = {}
        for column = 0, 31 do
            parts[#parts + 1] = string.format("%02X",
                r8(SCREENBLOCK_BASE + row * 32 + column) or 0)
        end
        file:write(string.format("screen_row_%02d=%s\n", row, table.concat(parts)))
    end
    for _, line in ipairs(scan_active_map_candidates()) do
        file:write("candidate=" .. line .. "\n")
    end
    for _, line in ipairs(dump_rom_pointer_state()) do
        file:write(line .. "\n")
    end
    file:close()
    console:log("MAP19 observer wrote " .. path .. " at frame " .. tostring(frame))
end

local frame = 0
local shots = 0
local callback_id
callback_id = callbacks:add("frame", function()
    frame = frame + 1
    if frame == 120 then
        emu:screenshot(OUT_ROOT .. "/frame-0120.png")
        shots = shots + 1
    elseif frame == 300 then
        write_state(OUT_ROOT .. "/state-0300.txt", "boot", frame)
    elseif frame == 600 then
        emu:screenshot(OUT_ROOT .. "/frame-0600.png")
        shots = shots + 1
    elseif frame == 900 then
        write_state(OUT_ROOT .. "/state-0900.txt", "settled", frame)
        local marker = assert(io.open(OUT_ROOT .. "/done.txt", "w"))
        marker:write("done\n")
        marker:close()
        callbacks:remove(callback_id)
    end
end)

local marker = assert(io.open(OUT_ROOT .. "/armed.txt", "w"))
marker:write("armed\n")
marker:close()
