-- MAP-TILE-PAINT-001 runtime observer: does the RETAIL ENGINE load an authored
-- chunk-cell paint?
--
-- READ-ONLY with respect to emulated state and input: this file only READS
-- emulated memory (emu:read8/read16/read32) and its own latched registers, and
-- writes host files under the run directory. It contains none of the input- or
-- memory-writing API names the read-only guard in tests/unit/test_mgba_capture.py
-- greps for, so the observer guarantee holds. (The guard greps the names, so they
-- are deliberately not spelled out here, including in comments.)
--
-- WHY THIS EXISTS. MAP-TILE-PAINT-001 has to prove that a map-layout edit made
-- through DragonByte Z reaches the ACTUAL Buu's Fury engine, not merely that the
-- build wrote bytes. The private savestate is positioned in map 40 with the
-- engine's assembled background already live in VRAM, so live VRAM is the
-- ground-truth oracle: whatever the engine put in the screenblock for the
-- painted cell IS what the display scans out.
--
-- WHAT IT PROVES, exactly. A dominant layer's chunk cell holds an entry offset
-- into the map's character block. Two runs of the SAME state - retail ROM and
-- authored derivative - must differ, inside the painted cell's own 32x32-tile
-- screen region, by exactly the entry values the authored chunk supplies, and
-- must agree everywhere else in that screenblock. So the observer dumps the
-- whole screenblock for each displayed BG and the entry-offset base it saw, and
-- the comparison is done off-line in Python against the accepted ROM decoders.
--
-- RUNTIME-PROVEN ADDRESSES (do NOT re-derive):
--   0x03001980 = live MapEntry pointer. MapEntry table base 0x0808E2E0, stride
--   0x38, so map index = (ptr - base) / stride (TOOLKIT-029).
--   VRAM 0x06000000, palette 0x05000000, OAM 0x07000000, IO 0x04000000.
--
-- The screenblock a BG displays is read from LIVE BGxCNT (bits 8-12 screen base
-- block) rather than assumed, because the engine programs BGxCNT per map and a
-- hardcoded base would silently describe a different map's block.

local ACTIVE_MAP_PTR = 0x03001980
local MAP_ENTRY_BASE = 0x0808E2E0
local MAP_ENTRY_SIZE = 0x38
local TARGET_INDEX   = 40

local DISPCNT = 0x04000000
local BGCNT   = { 0x04000008, 0x0400000A, 0x0400000C, 0x0400000E }

-- One 32x32-entry screenblock is 0x800 bytes; VRAM holds 32 of them.
local SCREENBLOCK_BYTES = 0x800
local VRAM_LO, VRAM_HI = 0x06000000, 0x06018000
local PAL_LO,  PAL_HI  = 0x05000000, 0x05000400
local IO_LO,   IO_HI   = 0x04000000, 0x04000060

-- Output directory. inject_mgba_lua.ps1 sets the global `rom011_marker_path`
-- before dofile()ing this script; that path is already validated to sit beneath
-- the ignored build tree, so deriving outputs from its directory keeps every
-- artifact inside the run directory without depending on environment variables.
local run_dir = nil
if type(rom011_marker_path) == "string" then
    run_dir = rom011_marker_path:match("^(.*)/[^/]*$")
end
local function in_run(name)
    if run_dir then return run_dir .. "/" .. name end
    return name
end

assert(emu ~= nil, "mGBA did not attach the emulation core")
-- 0.11 returns either the bare "BG3E" or the prefixed "AGB-BG3E"; accept both.
local game_code = emu:getGameCode()
assert(game_code == "BG3E" or game_code == "AGB-BG3E",
    "unexpected game code: " .. tostring(game_code))
assert(emu:romSize() == 8388608, "unexpected ROM size")

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

-- Dump [lo, hi) to `name` as raw little-endian bytes. Reads in half-words and
-- falls back to a byte for a bad word, so a transient miss shifts nothing.
local function dump_region(lo, hi, name)
    local path = in_run(name)
    local f = assert(io.open(path, "wb"), "cannot open output: " .. tostring(path))
    local written = 0
    local addr = lo
    while addr + 1 < hi do
        local w = safe16(addr)
        if w == nil then
            f:write(string.char(0, 0))
        else
            f:write(string.char(w & 0xFF, (w >> 8) & 0xFF))
        end
        written = written + 2
        addr = addr + 2
    end
    if addr < hi then
        f:write(string.char((safe8(addr) or 0) & 0xFF))
        written = written + 1
    end
    f:close()
    return written
end

-- One 32x32 screenblock, row-major little-endian half-words, as 16-bit values.
local function dump_screenblock(base, name)
    local path = in_run(name)
    local f = assert(io.open(path, "wb"), "cannot open output: " .. tostring(path))
    for index = 0, 1023 do
        local v = safe16(base + index * 2)
        if v == nil then
            f:write(string.char(0, 0))
        else
            f:write(string.char(v & 0xFF, (v >> 8) & 0xFF))
        end
    end
    f:close()
    return 1024
end

local function h16(v) if v == nil then return "" end return string.format("0x%04X", v) end
local function h32(v) if v == nil then return "" end return string.format("0x%08X", v) end

local dumped = false

local function do_dump(entry, index, frame)
    dumped = true

    dump_region(VRAM_LO, VRAM_HI, "vram.bin")
    dump_region(PAL_LO, PAL_HI, "palette.bin")
    dump_region(IO_LO, IO_HI, "io_regs.bin")

    local dispcnt = safe16(DISPCNT)
    local bg = {}
    for i = 1, 4 do bg[i] = safe16(BGCNT[i]) end

    local mpath = in_run("runtime_manifest.csv")
    local m = assert(io.open(mpath, "w"), "cannot open manifest: " .. tostring(mpath))
    m:write("field,value\n")
    m:write("game_code," .. tostring(game_code) .. "\n")
    m:write("rom_size," .. tostring(emu:romSize()) .. "\n")
    m:write("map_entry_ptr," .. h32(entry) .. "\n")
    m:write("map_index," .. tostring(index) .. "\n")
    m:write("frame_at_dump," .. tostring(frame) .. "\n")
    m:write("dispcnt," .. h16(dispcnt) .. "\n")

    for i = 1, 4 do
        local n = i - 1
        local cnt = bg[i]
        m:write(string.format("bg%dcnt,%s\n", n, h16(cnt)))
        if cnt == nil then
            m:write(string.format("bg%d_screen_base,%s\n", n, ""))
            m:write(string.format("bg%d_screen_base_block,%s\n", n, ""))
            m:write(string.format("bg%d_color_mode,%s\n", n, ""))
            m:write(string.format("bg%d_enabled,%s\n", n, ""))
            m:write(string.format("bg%d_screenblock_sha_unused,%s\n", n, ""))
        else
            local screen_base = 0x06000000 + (((cnt >> 8) & 0x1F) * SCREENBLOCK_BYTES)
            local color_mode = (cnt >> 7) & 0x1
            -- DISPCNT bits 8..11 enable BG0..BG3.
            local enabled = 0
            if dispcnt ~= nil then enabled = (dispcnt >> (8 + n)) & 0x1 end
            m:write(string.format("bg%d_screen_base,%s\n", n, h32(screen_base)))
            m:write(string.format("bg%d_screen_base_block,%d\n", n, (cnt >> 8) & 0x1F))
            m:write(string.format("bg%d_color_mode,%s\n", n,
                color_mode == 1 and "8bpp" or "4bpp"))
            m:write(string.format("bg%d_enabled,%d\n", n, enabled))
            dump_screenblock(screen_base, string.format("screenblock_bg%d.bin", n))
        end
    end

    m:write("screenblock_entries,1024\n")
    m:close()
end

local frame = 0

callbacks:add("frame", function()
    frame = frame + 1
    if dumped then return end

    local entry = safe32(ACTIVE_MAP_PTR)
    if entry ~= nil and entry >= MAP_ENTRY_BASE then
        local offset = entry - MAP_ENTRY_BASE
        if offset % MAP_ENTRY_SIZE == 0 then
            local index = offset // MAP_ENTRY_SIZE
            if index == TARGET_INDEX then
                do_dump(entry, index, frame)
            end
        end
    end

    -- Armed marker. The injector waits ~10s for this. Readiness means "the
    -- observer is live", NOT "map 40 was found": the state loads INTO map 40 so
    -- the dump usually happens on this same frame, but if the state settles a
    -- frame late the callback keeps polling and the marker must not hang the
    -- wait. Written on the first frame regardless, AFTER attempting the dump.
    if type(rom011_marker_path) == "string" then
        local ok = io.open(rom011_marker_path)
        if ok then
            ok:close()
        else
            local mk = io.open(rom011_marker_path, "w")
            if mk then mk:write("armed\n") mk:close() end
        end
    end
end)
