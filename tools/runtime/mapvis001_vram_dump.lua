-- MAP-VIS-001 Phase 2: read-only VRAM/palette/OAM/IO oracle dump.
--
-- Read-only with respect to emulated memory and input: this file only READS
-- emulated memory (emu:read8/read16/read32) and writes host files (io/os). It
-- contains none of the input- or memory-writing API names the read-only guard
-- in tests/unit/test_mgba_capture.py greps for, so the observer guarantee
-- stays true. (The test greps the names, so they are deliberately not spelled
-- out here, including in comments.)
--
-- WHY THIS EXISTS. MAP-VIS-001 proves how a Buu's Fury retail map becomes
-- background pixels. The private savestate is already positioned in map 40 with
-- the retail-assembled tileset/tilemap/palette LIVE in VRAM. That live VRAM is
-- the ground-truth oracle. We dump it once, read-only, and derive the ROM->VRAM
-- provenance backward in the next phase (the Python decoder). No human play is
-- needed: the state loads into map 40, so once map 40 is confirmed live we dump
-- exactly once and stop.
--
-- MAP RESOLUTION (runtime-proven, TOOLKIT-029 / MAP_FORMAT.md, do NOT re-derive):
--   0x03001980 = live MapEntry pointer. MapEntry table base 0x0808E2E0, stride
--   0x38. Map index = (ptr - 0x0808E2E0) / 0x38. Target is index 40.
--
-- DUMP TARGETS (GBATEK):
--   VRAM    0x06000000..0x06017FFF   (98304 bytes)
--   Palette 0x05000000..0x050003FF   (1024 bytes)
--   OAM     0x07000000..0x070003FF   (1024 bytes)
--   IO regs 0x04000000..0x0400005F   (96 bytes; captures DISPCNT + all BGxCNT +
--                                      BGxHOFS/VOFS scroll registers)
-- Each is written as RAW LITTLE-ENDIAN BYTES, exactly as the bus reads them.

local ACTIVE_MAP_PTR = 0x03001980
local MAP_ENTRY_BASE = 0x0808E2E0
local MAP_ENTRY_SIZE = 0x38
local TARGET_INDEX   = 40

local VRAM_LO, VRAM_HI = 0x06000000, 0x06018000   -- [lo, hi), 0x18000 bytes
local PAL_LO,  PAL_HI  = 0x05000000, 0x05000400    -- 0x400 bytes
local OAM_LO,  OAM_HI  = 0x07000000, 0x07000400    -- 0x400 bytes
local IO_LO,   IO_HI   = 0x04000000, 0x04000060    -- 0x60 bytes

local DISPCNT = 0x04000000
local BGCNT   = { 0x04000008, 0x0400000A, 0x0400000C, 0x0400000E }

-- Output location. inject_mgba_lua.ps1 sets the global `rom011_marker_path`
-- before dofile()ing this script; that path is already validated to sit beneath
-- the ignored build tree. Deriving the output paths from its directory keeps
-- every artifact inside the run directory without depending on environment
-- variables, which do not survive UI-driven injection into a running mGBA.
local run_dir = nil
if type(rom011_marker_path) == "string" then
    run_dir = rom011_marker_path:match("^(.*)/[^/]*$")
end
local function in_run(name)
    if run_dir then return run_dir .. "/" .. name end
    return name
end

assert(emu ~= nil, "mGBA did not attach the emulation core")
-- The 0.11 dev build returns either the bare "BG3E" or the prefixed "AGB-BG3E";
-- accept both (mgba-runtime skill).
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

-- Dump [lo, hi) to `name` as raw bytes. Reads in 16-bit words where the span is
-- even (halving the per-frame read count), falling back to a byte for a bad
-- word or an odd tail. Returns the number of bytes written.
local function dump_region(lo, hi, name)
    local path = in_run(name)
    local f = assert(io.open(path, "wb"), "cannot open output: " .. tostring(path))
    local written = 0
    local addr = lo
    while addr + 1 < hi do
        local w = safe16(addr)
        if w == nil then
            -- Bad half-word: write two zero bytes so the offsets stay aligned.
            f:write(string.char(0, 0))
        else
            f:write(string.char(w & 0xFF, (w >> 8) & 0xFF))
        end
        written = written + 2
        addr = addr + 2
    end
    if addr < hi then
        local b = safe8(addr) or 0
        f:write(string.char(b & 0xFF))
        written = written + 1
    end
    f:close()
    return written
end

-- Decode a BGxCNT half-word per GBATEK: bits 0-1 priority, 2-3 char base block,
-- 6 mosaic, 7 color mode (0=16/16, 1=256/1), 8-12 screen base block, 13 affine
-- wrap, 14-15 screen size.
local function decode_bgcnt(v)
    if v == nil then return "", "", "", "", "" end
    local priority     = v & 0x3
    local char_base    = (v >> 2) & 0x3
    local color_mode   = (v >> 7) & 0x1        -- 0 = 4bpp, 1 = 8bpp
    local screen_base  = (v >> 8) & 0x1F
    local screen_size  = (v >> 14) & 0x3
    local color_str = (color_mode == 1) and "8bpp" or "4bpp"
    return char_base, screen_base, screen_size, color_str, priority
end

local function h(v) if v == nil then return "" end return string.format("0x%08X", v) end
local function h16(v) if v == nil then return "" end return string.format("0x%04X", v) end

local dumped = false

local function do_dump(entry, index, frame)
    dumped = true

    local v_vram = dump_region(VRAM_LO, VRAM_HI, "vram.bin")
    local v_pal  = dump_region(PAL_LO,  PAL_HI,  "palette.bin")
    local v_oam  = dump_region(OAM_LO,  OAM_HI,  "oam.bin")
    local v_io   = dump_region(IO_LO,   IO_HI,   "io_regs.bin")

    local dispcnt = safe16(DISPCNT)
    local bg = {}
    for i = 1, 4 do bg[i] = safe16(BGCNT[i]) end

    local mpath = in_run("dump_manifest.csv")
    local m = assert(io.open(mpath, "w"), "cannot open manifest: " .. tostring(mpath))
    m:write("field,value\n")
    m:write("game_code," .. tostring(game_code) .. "\n")
    m:write("rom_size," .. tostring(emu:romSize()) .. "\n")
    m:write("map_entry_ptr," .. h(entry) .. "\n")
    m:write("map_index," .. tostring(index) .. "\n")
    m:write("dispcnt," .. h16(dispcnt) .. "\n")
    for i = 1, 4 do
        m:write(string.format("bg%dcnt,%s\n", i - 1, h16(bg[i])))
    end
    m:write("frame_at_dump," .. tostring(frame) .. "\n")
    m:write("vram.bin," .. tostring(v_vram) .. "\n")
    m:write("palette.bin," .. tostring(v_pal) .. "\n")
    m:write("oam.bin," .. tostring(v_oam) .. "\n")
    m:write("io_regs.bin," .. tostring(v_io) .. "\n")
    for i = 1, 4 do
        local cb, sb, ss, cm, pr = decode_bgcnt(bg[i])
        local n = i - 1
        m:write(string.format("bg%d_char_base_block,%s\n", n, tostring(cb)))
        m:write(string.format("bg%d_screen_base_block,%s\n", n, tostring(sb)))
        m:write(string.format("bg%d_screen_size_bits,%s\n", n, tostring(ss)))
        m:write(string.format("bg%d_color_mode,%s\n", n, tostring(cm)))
        m:write(string.format("bg%d_priority,%s\n", n, tostring(pr)))
    end
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

    -- Armed marker. The injector waits ~10s for this to appear (readiness). The
    -- reference writes it unconditionally at load; here readiness must mean "the
    -- observer is live", NOT "map 40 was found", or the wait could hang if the
    -- state happens to settle a frame late. So write it on the FIRST frame
    -- regardless, AFTER attempting the dump. The savestate loads INTO map 40, so
    -- the dump almost always happens on this same first frame; if it does not,
    -- readiness still resolves and the callback keeps polling and dumps map 40
    -- when it appears.
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
