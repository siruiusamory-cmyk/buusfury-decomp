-- MAP-GFX-DIAG-001 runtime observer: dump the retail engine's OWN assembled
-- background for one target map, after a genuine, SETTLED area entry.
--
-- READ-ONLY with respect to emulated state and input: this file only READS
-- emulated memory (emu:read8/read16/read32), reads the emulator's own framebuffer
-- through its screenshot call, and writes host files under the run directory. It
-- contains none of the input- or memory-writing API names the read-only guard in
-- tests/unit/test_mgba_capture.py greps for, so the observer guarantee holds.
-- (The guard greps the names, so they are deliberately not spelled out here,
-- including in comments.)
--
-- WHY THIS EXISTS. The SDK renders a Buu's Fury map from immutable ROM bytes.
-- The only oracle for "is that what the engine draws" is the engine's own VRAM
-- after it has built the area. Two traps have to be closed for that oracle to
-- mean anything:
--
--   1. A savestate restores an ALREADY-ASSEMBLED background, so the observer
--      refuses to dump until it has watched the live map index leave the target
--      and come back.
--   2. An area entry FADES IN, and the fade rewrites the whole background
--      palette every frame. A dump taken during the fade catches a black palette
--      and half-written screenblocks. Measured on the first run of this observer:
--      a dump 30 frames after re-entry had 2 of 256 palette entries equal to the
--      ROM's and two of four screen planes still empty. So the dump now also
--      waits for the palette to STOP CHANGING, which is the engine's own signal
--      that the fade has finished.
--
-- WHAT IS DUMPED, and which hypothesis each piece decides:
--   vram.bin          char area + every screenblock: the assembled character
--                     block (tile/index decode, atlas bank selection, bit depth)
--                     and the engine's own screen entries (chunk composition,
--                     flips, palette bits).
--   palette.bin       live BG palette: palette selection, and any runtime fade.
--   display.png       the emulator's own framebuffer: what the display actually
--                     shows, which is what decides per-layer screen placement.
--   io_regs.bin       DISPCNT, BGxCNT, BGxHOFS/VOFS, BLDCNT/BLDALPHA/BLDY:
--                     bit depth, layering order, per-layer scroll, blending.
--   screenblock_bgN   one 32x32-entry plane per displayed BG, at the base LIVE
--                     BGxCNT names rather than a hardcoded block.
--   manifest          the live MapEntry pointer, the root the engine loaded,
--                     each layer slot's record and its own grid/window words.
--
-- RUNTIME-PROVEN ADDRESSES (do NOT re-derive):
--   0x03001980 = live MapEntry pointer. MapEntry table base 0x0808E2E0, stride
--   0x38, so map index = (ptr - base) / stride (TOOLKIT-029).
--   VRAM 0x06000000, palette 0x05000000, OAM 0x07000000, IO 0x04000000.
--   0x030019A4 = CANDIDATE per-map camera state. It is recorded as a candidate
--   and is only called corroborated when its max-scroll words equal the live
--   root's own extent words minus one; no conclusion rests on it otherwise.

local ACTIVE_MAP_PTR = 0x03001980
local MAP_ENTRY_BASE = 0x0808E2E0
local MAP_ENTRY_SIZE = 0x38
local TARGET_INDEX   = 36

-- The engine rebuilds an area only on entry, so a dump needs an observed
-- departure and a settled return. DWELL_FRAMES is the map staying put;
-- SETTLE_FRAMES is the background palette staying put, which is how a finished
-- fade is recognised.
local DWELL_FRAMES = 90
local SETTLE_FRAMES = 45
local MAX_DUMPS = 2

local DISPCNT = 0x04000000
local BGCNT   = { 0x04000008, 0x0400000A, 0x0400000C, 0x0400000E }
-- BGxHOFS/BGxVOFS pairs, two halfwords each.
local BGOFS   = { 0x04000010, 0x04000014, 0x04000018, 0x0400001C }

-- Background palette words sampled every frame to detect a running fade. The
-- fade rewrites every entry, so five spread across the table is enough to see it
-- move while costing nothing per frame.
local PALETTE_PROBE = { 0x05000004, 0x05000008, 0x05000010, 0x05000040, 0x05000100 }

local CAMERA_STATE = 0x030019A4

local SCREENBLOCK_BYTES = 0x800
local VRAM_LO, VRAM_HI = 0x06000000, 0x06018000
local PAL_LO,  PAL_HI  = 0x05000000, 0x05000400
local IO_LO,   IO_HI   = 0x04000000, 0x04000060

-- Layer-slot pointers on the root, and the dominant record's grid/window.
local ROOT_LAYER_SLOTS = { 0x14, 0x18, 0x1C, 0x20 }
local LAYER_CHUNK_X = 0x14
local LAYER_CHUNK_Y = 0x15
local LAYER_WINDOW  = 0x18
local ROOT_BG_ADDEND = 0x04
local ROOT_EXTENT_X = 0x08
local ROOT_EXTENT_Y = 0x0A
local ROOT_SELECTOR_STREAM = 0x48
local ROOT_BANK_TABLE = 0x4C
local ROOT_ANIMATED_COUNT = 0x0C
local MAP_ENTRY_SCENE_POINTER = 0x2C

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
local function dec(v) if v == nil then return "" end return tostring(v) end

local function write_status(frame, start_index, index, saw_other, dwell, settle, dumps)
    local f = io.open(in_run("observer_status.txt"), "w")
    if not f then return end
    f:write("frame," .. tostring(frame) .. "\n")
    f:write("start_index," .. dec(start_index) .. "\n")
    f:write("live_index," .. dec(index) .. "\n")
    f:write("saw_departure," .. tostring(saw_other) .. "\n")
    f:write("dwell_frames," .. tostring(dwell) .. "\n")
    f:write("settle_frames," .. tostring(settle) .. "\n")
    f:write("dumps," .. tostring(dumps) .. "\n")
    f:write("target_index," .. tostring(TARGET_INDEX) .. "\n")
    f:close()
end

local function do_dump(entry, index, frame, ordinal)
    local tag = "_" .. tostring(ordinal)

    dump_region(VRAM_LO, VRAM_HI, "vram" .. tag .. ".bin")
    dump_region(PAL_LO, PAL_HI, "palette" .. tag .. ".bin")
    dump_region(IO_LO, IO_HI, "io_regs" .. tag .. ".bin")

    -- The emulator's own framebuffer, so the display is captured without
    -- depending on which host window happens to be on top.
    local shot_ok, shot_err = pcall(function()
        return emu:screenshot(in_run("display" .. tag .. ".png"))
    end)

    -- The root the ENGINE loaded, reached the same way the renderer reaches it:
    -- MapEntry + 0x2C is the content-stream word whose target is the root.
    local source = safe32(entry + MAP_ENTRY_SCENE_POINTER)
    local root = nil
    if source ~= nil then root = safe32(source) end

    local dispcnt = safe16(DISPCNT)
    local bg = {}
    local ofs = {}
    for i = 1, 4 do
        bg[i] = safe16(BGCNT[i])
        ofs[i] = { safe16(BGOFS[i]), safe16(BGOFS[i] + 2) }
    end

    local mpath = in_run("manifest" .. tag .. ".csv")
    local m = assert(io.open(mpath, "w"), "cannot open manifest: " .. tostring(mpath))
    m:write("field,value\n")
    m:write("game_code," .. tostring(game_code) .. "\n")
    m:write("rom_size," .. tostring(emu:romSize()) .. "\n")
    m:write("dump_ordinal," .. tostring(ordinal) .. "\n")
    m:write("frame_at_dump," .. tostring(frame) .. "\n")
    m:write("screenshot," .. tostring(shot_ok and "written" or ("failed: " .. tostring(shot_err))) .. "\n")
    m:write("map_entry_ptr," .. h32(entry) .. "\n")
    m:write("map_index," .. tostring(index) .. "\n")
    m:write("scene_pointer_value," .. h32(source) .. "\n")
    m:write("root_address," .. h32(root) .. "\n")
    m:write("dispcnt," .. h16(dispcnt) .. "\n")

    for i = 1, 4 do
        local n = i - 1
        local cnt = bg[i]
        m:write(string.format("bg%dcnt,%s\n", n, h16(cnt)))
        m:write(string.format("bg%d_hofs,%s\n", n, dec(ofs[i][1])))
        m:write(string.format("bg%d_vofs,%s\n", n, dec(ofs[i][2])))
        if cnt == nil then
            m:write(string.format("bg%d_screen_base,%s\n", n, ""))
            m:write(string.format("bg%d_char_base_block,%s\n", n, ""))
            m:write(string.format("bg%d_screen_base_block,%s\n", n, ""))
            m:write(string.format("bg%d_screen_size_bits,%s\n", n, ""))
            m:write(string.format("bg%d_color_mode,%s\n", n, ""))
            m:write(string.format("bg%d_priority,%s\n", n, ""))
            m:write(string.format("bg%d_enabled,%s\n", n, ""))
        else
            local screen_base = 0x06000000 + (((cnt >> 8) & 0x1F) * SCREENBLOCK_BYTES)
            local enabled = 0
            if dispcnt ~= nil then enabled = (dispcnt >> (8 + n)) & 0x1 end
            m:write(string.format("bg%d_screen_base,%s\n", n, h32(screen_base)))
            m:write(string.format("bg%d_char_base_block,%d\n", n, (cnt >> 2) & 0x3))
            m:write(string.format("bg%d_screen_base_block,%d\n", n, (cnt >> 8) & 0x1F))
            m:write(string.format("bg%d_screen_size_bits,%d\n", n, (cnt >> 14) & 0x3))
            m:write(string.format("bg%d_color_mode,%s\n", n,
                ((cnt >> 7) & 0x1) == 1 and "8bpp" or "4bpp"))
            m:write(string.format("bg%d_priority,%d\n", n, cnt & 0x3))
            m:write(string.format("bg%d_enabled,%d\n", n, enabled))
            if enabled == 1 then
                dump_screenblock(screen_base, string.format("screenblock_bg%d%s.bin", n, tag))
            end
        end
    end

    -- The root's own words, read from the LIVE image, so the layer records and
    -- the extent the engine actually loaded are evidence rather than a host-side
    -- assumption about which root is live.
    if root ~= nil then
        local extent_x = safe16(root + ROOT_EXTENT_X)
        local extent_y = safe16(root + ROOT_EXTENT_Y)
        m:write("root_extent_x_raw," .. h16(extent_x) .. "\n")
        m:write("root_extent_y_raw," .. h16(extent_y) .. "\n")
        m:write("root_animated_count," .. dec(safe32(root + ROOT_ANIMATED_COUNT)) .. "\n")
        m:write("root_selector_stream," .. h32(safe32(root + ROOT_SELECTOR_STREAM)) .. "\n")
        m:write("root_bank_table," .. h32(safe32(root + ROOT_BANK_TABLE)) .. "\n")
        local addends = ""
        for i = 0, 3 do
            local b = safe8(root + ROOT_BG_ADDEND + i)
            if b == nil then b = -1 end
            addends = addends .. tostring(b)
            if i < 3 then addends = addends .. ":" end
        end
        m:write("root_bg_addends," .. addends .. "\n")

        -- The candidate camera state, recorded raw and corroborated only if its
        -- max-scroll words equal the live root's extent words minus one.
        local cam_max_x = safe16(CAMERA_STATE + 0x9C)
        local cam_max_y = safe16(CAMERA_STATE + 0x9E)
        m:write("camera_candidate_address," .. h32(CAMERA_STATE) .. "\n")
        m:write("camera_candidate_max_x," .. h16(cam_max_x) .. "\n")
        m:write("camera_candidate_max_y," .. h16(cam_max_y) .. "\n")
        local corroborated = "no"
        if extent_x ~= nil and extent_y ~= nil and cam_max_x ~= nil and cam_max_y ~= nil then
            if cam_max_x == (extent_x - 1) and cam_max_y == (extent_y - 1) then
                corroborated = "yes"
            end
        end
        m:write("camera_candidate_corroborated," .. corroborated .. "\n")

        for i = 1, 4 do
            local n = i - 1
            local record = safe32(root + ROOT_LAYER_SLOTS[i])
            m:write(string.format("layer%d_record,%s\n", n, h32(record)))
            if record ~= nil and record ~= 0 then
                local cx = safe8(record + LAYER_CHUNK_X)
                local cy = safe8(record + LAYER_CHUNK_Y)
                m:write(string.format("layer%d_handler,%s\n", n,
                    h32(safe32(record))))
                m:write(string.format("layer%d_chunk_x,%s\n", n, dec(cx)))
                m:write(string.format("layer%d_chunk_y,%s\n", n, dec(cy)))
                if cx ~= nil and cy ~= nil then
                    local cells = cx * cy
                    local shown = cells
                    if shown > 8 then shown = 8 end
                    local window = ""
                    for cell = 0, shown - 1 do
                        window = window .. h32(safe32(record + LAYER_WINDOW + cell * 4))
                        if cell < shown - 1 then window = window .. " " end
                    end
                    m:write(string.format("layer%d_cells,%d\n", n, cells))
                    m:write(string.format("layer%d_window_head,%s\n", n, window))
                end
            end
        end
    end

    m:write("screenblock_entries,1024\n")
    m:close()
end

local function current_index()
    local entry = safe32(ACTIVE_MAP_PTR)
    if entry == nil or entry < MAP_ENTRY_BASE then return nil, nil end
    local offset = entry - MAP_ENTRY_BASE
    if offset % MAP_ENTRY_SIZE ~= 0 then return nil, nil end
    local index = offset // MAP_ENTRY_SIZE
    if index < 0 or index >= 452 then return nil, nil end
    return index, entry
end

-- The background palette's own signature this frame, as a string so two frames
-- compare in one operation.
local function palette_signature()
    local parts = {}
    for i = 1, #PALETTE_PROBE do
        parts[i] = tostring(safe16(PALETTE_PROBE[i]))
    end
    return table.concat(parts, ":")
end

local frame = 0
local start_index = nil
local saw_departure = false
local dwell = 0
local settle = 0
local last_palette = nil
local dumps = 0

callbacks:add("frame", function()
    frame = frame + 1

    local signature = palette_signature()
    if signature == last_palette then
        settle = settle + 1
    else
        settle = 0
        last_palette = signature
    end

    local index, entry = current_index()
    if index ~= nil then
        if start_index == nil then start_index = index end
        if index ~= TARGET_INDEX then
            saw_departure = true
            dwell = 0
        else
            dwell = dwell + 1
            if saw_departure and dwell >= DWELL_FRAMES and settle >= SETTLE_FRAMES
                    and dumps < MAX_DUMPS then
                dumps = dumps + 1
                do_dump(entry, index, frame, dumps)
                -- The next dump needs its own observed departure, so two dumps
                -- are two independent entries rather than one long visit.
                saw_departure = false
                dwell = 0
            end
        end
        write_status(frame, start_index, index, saw_departure, dwell, settle, dumps)
    end

    -- Armed marker. The injector waits ~10s for this. Readiness means "the
    -- observer is live", NOT "the target map was reached": the operator still
    -- has to walk there. Written on the first frame regardless.
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
