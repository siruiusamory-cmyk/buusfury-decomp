-- MAP-TILE-PAINT-001 live-watch observer, for the LEAVE-AND-RE-ENTER experiment.
--
-- READ-ONLY with respect to emulated state and input: it reads emulated memory
-- and its own latched registers and writes host files under the run directory.
-- It contains none of the input- or memory-writing API names the read-only guard
-- in tests/unit/test_mgba_capture.py greps for. (The guard greps the names, so
-- they are deliberately not spelled out here, including in comments.)
--
-- WHY THIS EXISTS, and why it is not the same as
-- `tilepaint001_live_screenblock.lua`. A savestate restores emulated RAM and
-- VRAM, including the map background the engine had already assembled, so a
-- ROM-side map edit can never appear under a state taken after the map loaded -
-- measured: the retail and derivative runs under one state were byte-identical
-- in VRAM, palette, all four screenblocks and IO. The engine only re-reads the
-- map when it BUILDS it, which happens on entering an area.
--
-- So this observer watches for the map being built: every `SAMPLE_EVERY` frames
-- it reads the live screenblock of each enabled BG, and whenever that content
-- DIFFERS from the last latched content it writes a numbered snapshot. A human
-- walks out of the area and back in; the snapshot sequence then contains the
-- background the ROM produced for the new build, with no keypress timing
-- required from anyone.
--
-- It also records which live MapEntry pointer each snapshot was taken under, so
-- a snapshot set can be attributed to a map rather than assumed.
--
-- RUNTIME-PROVEN ADDRESSES (do NOT re-derive):
--   0x03001980 = live MapEntry pointer; table base 0x0808E2E0, stride 0x38.

local ACTIVE_MAP_PTR = 0x03001980
local MAP_ENTRY_BASE = 0x0808E2E0
local MAP_ENTRY_SIZE = 0x38

local DISPCNT = 0x04000000
local BGCNT   = { 0x04000008, 0x0400000A, 0x0400000C, 0x0400000E }

local SCREENBLOCK_BYTES = 0x800
local SCREENBLOCK_ENTRIES = 1024

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
assert(emu:romSize() == 8388608, "unexpected ROM size")

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
index_file:write("snapshot,frame,map_index,map_entry_ptr,bg0_base,bg1_base,bg2_base,bg3_base\n")
index_file:flush()

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
        "%d,%d,%s,%s,%s,%s,%s,%s\n",
        snapshots, frame,
        map_index and tostring(map_index) or "",
        entry and string.format("0x%08X", entry) or "",
        bases[0] and string.format("0x%08X", bases[0]) or "",
        bases[1] and string.format("0x%08X", bases[1]) or "",
        bases[2] and string.format("0x%08X", bases[2]) or "",
        bases[3] and string.format("0x%08X", bases[3]) or ""))
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
