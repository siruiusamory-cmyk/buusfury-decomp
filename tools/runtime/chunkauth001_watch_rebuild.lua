-- MAP-CHUNK-AUTHORING-001 live-watch observer, for the LEAVE-AND-RE-ENTER experiment.
--
-- Derived from `tilepaint001_watch_rebuild.lua`, whose methodology it keeps
-- exactly: it watches the live screenblocks, writes a numbered snapshot whenever
-- one CHANGES, and records the live MapEntry pointer each snapshot was taken
-- under, so a human walking out of an area and back in leaves a snapshot
-- sequence that proves the engine BUILT the map rather than restored it from a
-- savestate. A savestate restores the already-assembled background, so a
-- savestate-only capture cannot see a ROM-side map edit at all.
--
-- Two things are added, and both are required by this ticket rather than
-- incidental:
--
-- 1. THE GENERATED IMAGE SIZE IS ACCEPTED. The parent observer asserts
--    `romSize() == 8388608`. This ticket's derivative is a GENERATED 16 MiB
--    image - the authored chunk body is materialized above the canonical 8 MiB
--    EOF, which is the addressability question the ticket exists to answer - so
--    that assert refuses the very image under test. The size is not merely
--    allowed: it is WRITTEN INTO EVERY ROW, so the capture states which image the
--    engine was reading instead of leaving it to be assumed. Only the canonical
--    size and the profile's declared generated-expansion size are accepted; any
--    other image is still refused.
--
-- 2. THE LIVE CHUNK ADDRESS IS RECORDED. Every row carries the address the
--    ENGINE's own loaded layer record holds for map 40's BG1 chunk cell 0, read
--    through the live MapEntry -> root -> layer record chain. This is the
--    runtime-liveness evidence for the allocated address: it is the engine's
--    state, not the file's bytes, and it distinguishes an engine that resolved
--    the authored reference from one that never looked.
--
-- READ-ONLY with respect to emulated state and input: it reads emulated memory
-- and its own latched registers and writes host files under the run directory.
-- It contains none of the input- or memory-writing API names the read-only guard
-- in tests/unit/test_mgba_capture.py greps for. (The guard greps the names, so
-- they are deliberately not spelled out here, including in comments.)
--
-- RUNTIME-PROVEN ADDRESSES (do NOT re-derive):
--   0x03001980 = live MapEntry pointer; table base 0x0808E2E0, stride 0x38.
--   The root/layer chain below is MAP-TILE-PAINT-001's accepted reader:
--   MapEntry + 0x2C is the source word, its target is the root, and a root's
--   +0x18 slot holds the BG1 dominant layer record whose +0x18 window is the
--   four-byte chunk reference.

local ACTIVE_MAP_PTR = 0x03001980
local MAP_ENTRY_BASE = 0x0808E2E0
local MAP_ENTRY_SIZE = 0x38

-- The dominant layer form and the fields this observer reads. Stated once, from
-- the accepted map reader, so the observation and the writer cannot disagree.
local MAP_ENTRY_SOURCE_OFFSET = 0x2C
local ROOT_BG1_SLOT_OFFSET = 0x18
local LAYER_HANDLER_DOMINANT = 0x08008087
local LAYER_CHUNK_WINDOW_OFFSET = 0x18
local WATCHED_MAP_INDEX = 40
local WATCHED_CELL = 0

local DISPCNT = 0x04000000
local BGCNT   = { 0x04000008, 0x0400000A, 0x0400000C, 0x0400000E }

local SCREENBLOCK_BYTES = 0x800
local SCREENBLOCK_ENTRIES = 1024

-- The two image sizes this observer accepts: the canonical retail image, and the
-- generated 16 MiB image the profile declares as its expansion output size.
local CANONICAL_ROM_BYTES = 8388608
local GENERATED_ROM_BYTES = 16777216

-- Sampling cadence. 30 frames is half a second at 60fps: fast enough to catch an
-- area build, cheap enough that reading 4 x 2 KiB per sample does not disturb
-- the run.
local SAMPLE_EVERY = 30
-- Bounded, so a long session cannot fill the disk. Each snapshot is ~8 KiB.
local MAX_SNAPSHOTS = 48

local run_dir = nil
if type(rom011_marker_path) == "string" then
    run_dir = rom011_marker_path:match("^(.*)/[^/]*$")
end
local function in_run(name)
    if run_dir then return run_dir .. "/" .. name end
    return name
end

assert(emu ~= nil, "mGBA did not attach the emulation core")
local game_code = emu:getGameCode()
assert(game_code == "BG3E" or game_code == "AGB-BG3E",
    "unexpected game code: " .. tostring(game_code))

local rom_size = emu:romSize()
assert(rom_size == CANONICAL_ROM_BYTES or rom_size == GENERATED_ROM_BYTES,
    "unexpected ROM size: " .. tostring(rom_size))

local function safe8(addr)
    local ok, v = pcall(function() return emu:read8(addr) end)
    if ok and v then return v end
    return nil
end

local function safe16(addr)
    local ok, v = pcall(function() return emu:read16(addr) end)
    if ok and v then return v end
    return nil
end

local function safe32(addr)
    local ok, v = pcall(function() return emu:read32(addr) end)
    if ok and v then return v end
    return nil
end

-- The address the ENGINE currently holds for the watched map's BG1 cell 0.
--
-- Returns nil unless the whole chain resolves and the record really is the
-- dominant chunk form, so "no value" can never be mistaken for "the engine holds
-- zero here". This is deliberately the engine's LOADED state - the layer record
-- the loader built - and not the ROM's bytes read through the ROM window.
local function watched_chunk_address()
    local entry = safe32(ACTIVE_MAP_PTR)
    if entry == nil or entry < MAP_ENTRY_BASE then return nil end
    local offset = entry - MAP_ENTRY_BASE
    if offset % MAP_ENTRY_SIZE ~= 0 then return nil end
    if offset // MAP_ENTRY_SIZE ~= WATCHED_MAP_INDEX then return nil end

    local source = safe32(entry + MAP_ENTRY_SOURCE_OFFSET)
    if source == nil or source < 0x08000000 then return nil end
    local root = safe32(source)
    if root == nil or root < 0x08000000 then return nil end
    local record = safe32(root + ROOT_BG1_SLOT_OFFSET)
    if record == nil or record < 0x08000000 then return nil end
    if safe32(record) ~= LAYER_HANDLER_DOMINANT then return nil end
    local chunk_x = safe8(record + 0x14)
    if chunk_x == nil or chunk_x == 0 then return nil end
    return safe32(record + LAYER_CHUNK_WINDOW_OFFSET + WATCHED_CELL * 4)
end

-- Read one screenblock as 1024 half-words, plus a cheap content signature so a
-- comparison does not need to keep 8 KiB per BG in memory.
local function read_screenblock(base)
    local values = {}
    local signature = 0
    for index = 0, SCREENBLOCK_ENTRIES - 1 do
        local v = safe16(base + index * 2) or 0
        values[index + 1] = v
        -- A cheap order-sensitive rolling signature.
        signature = (signature * 31 + v) % 4294967296
    end
    return values, signature
end

local function write_screenblock(path, values)
    local f = assert(io.open(path, "wb"), "cannot open output: " .. tostring(path))
    for index = 1, SCREENBLOCK_ENTRIES do
        local v = values[index]
        f:write(string.char(v & 0xFF, (v >> 8) & 0xFF))
    end
    f:close()
end

local function screen_bases(dispcnt, bg)
    local bases = {}
    for i = 1, 4 do
        local n = i - 1
        local enabled = 0
        if dispcnt ~= nil then enabled = (dispcnt >> (8 + n)) & 0x1 end
        local cnt = bg[i]
        if enabled == 1 and cnt ~= nil then
            bases[n] = 0x06000000 + (((cnt >> 8) & 0x1F) * SCREENBLOCK_BYTES)
        end
    end
    return bases
end

local frame = 0
local snapshots = 0
local last_signature = {}
local index_path = in_run("snapshots.csv")
local index_file = assert(io.open(index_path, "w"), "cannot open index")
index_file:write(
    "snapshot,frame,map_index,map_entry_ptr,rom_size,"
    .. "watched_map,watched_cell,watched_chunk_address,"
    .. "bg0_base,bg1_base,bg2_base,bg3_base\n")
index_file:flush()

local function hex_or_blank(value)
    if value == nil then return "" end
    return string.format("0x%08X", value)
end

local function record(map_index, entry, bases)
    local name = string.format("snapshot_%03d", snapshots)
    local dispcnt = safe16(DISPCNT)
    local bg = {}
    for i = 1, 4 do bg[i] = safe16(BGCNT[i]) end
    for n = 0, 3 do
        local base = bases[n]
        if base ~= nil then
            local values = read_screenblock(base)
            write_screenblock(in_run(name .. string.format("_bg%d.bin", n)), values)
        end
    end
    index_file:write(string.format(
        "%d,%d,%s,%s,%d,%d,%d,%s,%s,%s,%s,%s\n",
        snapshots, frame,
        map_index and tostring(map_index) or "",
        hex_or_blank(entry),
        rom_size,
        WATCHED_MAP_INDEX, WATCHED_CELL,
        hex_or_blank(watched_chunk_address()),
        hex_or_blank(bases[0]), hex_or_blank(bases[1]),
        hex_or_blank(bases[2]), hex_or_blank(bases[3])))
    index_file:flush()
    snapshots = snapshots + 1
end

callbacks:add("frame", function()
    frame = frame + 1

    if frame % SAMPLE_EVERY == 0 and snapshots < MAX_SNAPSHOTS then
        local dispcnt = safe16(DISPCNT)
        local bg = {}
        for i = 1, 4 do bg[i] = safe16(BGCNT[i]) end
        local bases = screen_bases(dispcnt, bg)

        local changed = false
        for n = 0, 3 do
            local base = bases[n]
            if base ~= nil then
                local _values, signature = read_screenblock(base)
                if last_signature[n] ~= signature then
                    last_signature[n] = signature
                    changed = true
                end
            end
        end

        if changed then
            local entry = safe32(ACTIVE_MAP_PTR)
            local map_index = nil
            if entry ~= nil and entry >= MAP_ENTRY_BASE then
                local offset = entry - MAP_ENTRY_BASE
                if offset % MAP_ENTRY_SIZE == 0 then
                    map_index = offset // MAP_ENTRY_SIZE
                end
            end
            record(map_index, entry, bases)
        end
    end

    -- Readiness marker, written on the first frame so the injector's wait
    -- resolves whether or not a snapshot has happened yet.
    if frame == 1 and type(rom011_marker_path) == "string" then
        local mk = io.open(rom011_marker_path, "w")
        if mk then mk:write("armed\n") mk:close() end
    end
end)
