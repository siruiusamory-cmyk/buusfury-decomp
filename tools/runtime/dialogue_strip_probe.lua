-- How do ORDINARY dialogue characters become visible on screen?
--
-- READ-ONLY. It reads registers and memory, installs breakpoints and writes host
-- files inside the run directory. It writes no emulated memory and presses no
-- keys; driving is a separate file (npc_talk_driver.lua).
--
-- TICKET: the dialogue-rendering investigation resumed from memory node 842da34b.
-- Two things were already proven and are NOT re-litigated here:
--   * 0x0800B55C is a real OBJ writer (cp8 sheet-frame copy + OAM append), and
--   * it is NOT the ordinary dialogue-character placer (its visual diagnostic
--     landed on overlay/highlight sprites).
-- The open question is the presentation path for the ORDINARY spoken glyphs,
-- whose pixels are observed in OBJ VRAM inside 0x06014360..0x06014EC0.
--
-- TWO MODELS, and this run is designed to falsify one of them from OAM diffs:
--   Model A  ordinary characters are individual/per-character OAM entries;
--   Model B  they are a small stable set of strip/line OAM entries whose tile
--            pixels are rewritten as the reveal proceeds.
--
-- WHAT IS MEASURED, in the order the ticket asks for it:
--   1. the active OBJ interpretation: DISPCNT raw (BG mode, OBJ 1D/2D, BG/OBJ
--      enable), and per OAM entry the colour depth, shape, size, affine state,
--      flip state and palette bank;
--   2. a full 128-entry OAM inventory at each snapshot, with the EXACT tile set
--      each entry covers (1D and 2D mapping both implemented, 4bpp and 8bpp),
--      tested against the character window by BYTE INTERSECTION rather than by
--      "starting tile is inside the window";
--   3. a per-30-frame exact byte diff of the whole window, so a reveal can be
--      correlated with the bytes that actually moved and with the OAM entries
--      that sit on top of them.
--
-- PLUS the per-character composition events, which are the other half of the
-- question and are cheap to log (registers only):
--   0x0803DE5E  ldr r3,[r0,#0x20] inside the glyph composer 0x0803DE50.
--               r0 = the strip descriptor, r1 = the source glyph code,
--               r3 = the rasteriser the descriptor points at.
--   0x0800B08E  strb r0,[r6,#4]: the horizontal advance x = width(glyph)+1+x.
--   0x0800B092  str r2,[r4,#0x14]: the source cursor, +2 bytes = one unit.
--   0x0800B006  the reveal pass writing one (x,y) position-queue entry.
--   0x0801227A  the dialogue record copier: LIVENESS. Silent channels beside a
--               silent liveness channel prove nothing (mgba-runtime.md s.8).
--
-- THE SESSION ENDS ITSELF with os.exit(0) at the frame budget, so the procedure
-- stays: launch, do not poll, wait for the window to close, collect afterwards.

local COMPOSE = 0x0803DE5E
local ADVANCE = 0x0800B08E
local CONSUME = 0x0800B092
local QWRITE = 0x0800B006
local COPIER = 0x0801227A

local DISPCNT = 0x04000000
local BGCNT = { 0x04000008, 0x0400000A, 0x0400000C, 0x0400000E }
local OAM = 0x07000000
local OBJ_TILES = 0x06010000

-- The ordinary-character OBJ VRAM window, as given by the ticket. Tile 539
-- starts it; 0x06014EC0 is immediately before tile 630, so the window is the 91
-- 32-byte tiles 539..629.
local WIN_LO, WIN_HI = 0x06014360, 0x06014EC0

local BUDGET = 3000
local OAM_PERIOD = 120
local WIN_PERIOD = 30

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local out = (os.getenv("TOOLKIT031_OUT") or (exp_dir .. "strip-probe.csv"))

assert(emu ~= nil, "mGBA did not attach the emulation core")
assert(emu.setBreakpoint and emu.clearBreakpoint, "requires the 0.11 breakpoint API")
local code = emu:getGameCode()
assert(code == "BG3E" or code == "AGB-BG3E", "unexpected game code: " .. tostring(code))
assert(emu:romSize() == 8388608, "unexpected ROM size")

-- ---------------------------------------------------------------------------
-- OAM entry geometry. Sizes are the GBA's own tables; nothing here is inferred
-- from what this particular game happens to use.
-- ---------------------------------------------------------------------------
local SHAPE = { [0] = "square", [1] = "wide", [2] = "tall", [3] = "invalid" }
local DIMS = {
    [0] = { { 8, 8 }, { 16, 16 }, { 32, 32 }, { 64, 64 } },   -- square
    [1] = { { 16, 8 }, { 32, 8 }, { 32, 16 }, { 64, 32 } },   -- wide
    [2] = { { 8, 16 }, { 8, 32 }, { 16, 32 }, { 32, 64 } },   -- tall
}

local header = { "frame", "event", "a", "b", "c", "d", "note" }
local file = assert(io.open(out, "w"), "cannot open " .. tostring(out))
file:write(table.concat(header, ",") .. "\n")
file:flush()

local frames, snapshots, win_snaps, oam_snaps = 0, 0, 0, 0
local compose_hits, advance_hits, consume_hits, qwrite_hits, copier_hits = 0, 0, 0, 0, 0

local function r16(a)
    local ok, v = pcall(function() return emu:read16(a) end)
    if ok then return v end
end
local function r32(a)
    local ok, v = pcall(function() return emu:read32(a) end)
    if ok then return v end
end
local function reg(n)
    local ok, v = pcall(function() return tonumber(emu:readRegister(n)) end)
    if ok then return v end
end
local function r8(a)
    local ok, v = pcall(function() return emu:read8(a) end)
    if ok then return v end
end
local function hx(v) if v == nil then return "" end return string.format("0x%08X", v) end
local function h4(v) if v == nil then return "" end return string.format("0x%04X", v) end

local function row(t)
    local parts = { t.frame ~= nil and tostring(t.frame) or tostring(frames), t.event or "" }
    for i = 3, #header do
        parts[i] = t[header[i]] ~= nil and tostring(t[header[i]]) or ""
    end
    file:write(table.concat(parts, ",") .. "\n")
    file:flush()
end

local function dispcnt() return r16(DISPCNT) or 0 end

-- ---------------------------------------------------------------------------
-- Exact tile coverage of one OAM entry, honouring the live mapping mode.
-- Returns first_byte, last_byte (inclusive) or nil when the entry is unusable.
-- ---------------------------------------------------------------------------
local function coverage(a0, a1, a2, oneD)
    if (a0 & 0x0200) ~= 0 then return nil end          -- disabled
    local shape = (a0 >> 14) & 3
    local size = (a1 >> 14) & 3
    local dims = DIMS[shape]
    if dims == nil then return nil end                 -- shape 3 is prohibited
    local w, h = dims[size + 1][1], dims[size + 1][2]
    local eight = (a0 & 0x2000) ~= 0
    -- 32-byte units per 8x8 cell. MEASURED, run renderpath-02: the text object's
    -- four strip slots 178, 242, 370 and 498 are allocated contiguously in
    -- 32-byte units (178+64=242, 242+128=370, 370+128=498, 498+128=626) across
    -- mixed 32x64 and 64x64 256-colour sprites, and the engine's own per-frame
    -- blit computes 0x06010000 + slot*32. The OAM tile field is therefore an
    -- index of 32-byte units for 8bpp too, and an 8bpp cell is two of them.
    local units = eight and 2 or 1
    local step = units * 32
    local cells = (w // 8) * (h // 8)
    local base = a2 & 0x3FF
    local lo, hi
    if oneD then
        lo = OBJ_TILES + base * 32
        hi = lo + cells * units * 32 - 1
    else  -- 2D: the tile number names a column in a 32-column character table and
        -- rows advance by 32 units of 32 bytes.
        local step_units = eight and 2 or 1
        local min_u, max_u
        for cy = 0, (h // 8) - 1 do
            for cx = 0, (w // 8) - 1 do
                local u = base + cx * step_units + cy * 32
                if min_u == nil or u < min_u then min_u = u end
                if max_u == nil or u > max_u then max_u = u end
            end
        end
        lo = OBJ_TILES + min_u * 32
        hi = OBJ_TILES + (max_u + step_units) * 32 - 1
    end
    return lo, hi, w, h, step, cells, shape, size, eight
end

local function raw_oam()
    local t = {}
    for i = 0, 127 do
        local b = OAM + i * 8
        t[i] = { r16(b) or 0, r16(b + 2) or 0, r16(b + 4) or 0 }
    end
    return t
end

local function read_window()
    local n = (WIN_HI - WIN_LO) // 4
    local t = {}
    for i = 0, n - 1 do t[i] = r32(WIN_LO + i * 4) or 0 end
    return t
end

local last_win = nil
local win_changes = 0

local function win_diff()
    local now = read_window()
    win_snaps = win_snaps + 1
    if last_win == nil then
        last_win = now
        return nil
    end
    local changed_bytes, first_t, last_t = 0, nil, nil
    local tiles = {}
    for i = 0, #now do
        if now[i] ~= last_win[i] then
            changed_bytes = changed_bytes + 4
            local tile = ((WIN_LO + i * 4) - OBJ_TILES) // 32
            if first_t == nil or tile < first_t then first_t = tile end
            if last_t == nil or tile > last_t then last_t = tile end
            tiles[tile] = true
        end
    end
    local ntiles = 0
    for _ in pairs(tiles) do ntiles = ntiles + 1 end
    last_win = now
    if changed_bytes == 0 then return { 0, 0, nil, nil } end
    win_changes = win_changes + 1
    return { changed_bytes, ntiles, first_t, last_t }
end

local function oam_snapshot(event, d)
    local disp = d or dispcnt()
    local oneD = (disp & 0x0040) ~= 0
    local oam = raw_oam()
    oam_snaps = oam_snaps + 1
    snapshots = snapshots + 1

    local enabled, onscreen, covering = 0, 0, {}
    local detail = {}
    for i = 0, 127 do
        local e = oam[i]
        local a0, a1, a2 = e[1], e[2], e[3]
        if a0 ~= 0 and (a0 & 0x0200) == 0 then
            enabled = enabled + 1
            local y = a0 & 0xFF
            local x = a1 & 0x1FF
            if y < 160 and x < 240 then onscreen = onscreen + 1 end
            local lo, hi, w, h, step, cells, shape, size, eight =
                coverage(a0, a1, a2, oneD)
            -- BYTE INTERSECTION, not "the starting tile is inside the window":
            -- an object that starts below the window can still overlap it.
            if lo and hi >= WIN_LO and lo < WIN_HI then
                covering[#covering + 1] = string.format(
                    "%d:t%d-%d(%s%d bpp=%d xy=%d,%d pal=%d pri=%d)",
                    i, (lo - OBJ_TILES) // 32, (hi - OBJ_TILES) // 32,
                    SHAPE[shape], size, eight and 8 or 4, x, y,
                    (a2 >> 12) & 0xF, (a2 >> 10) & 3)
            end
            detail[#detail + 1] = string.format(
                "%3d a0=%s a1=%s a2=%s y=%3d x=%3d tile=%3d %s size=%d %s w=%d h=%d step=%d cells=%d affine=%d flip=%d,%d pal=%d pri=%d bytes=%s..%s",
                i, h4(a0), h4(a1), h4(a2), y, x, a2 & 0x3FF, SHAPE[shape], size,
                eight and "8bpp" or "4bpp", w or 0, h or 0, step or 0, cells or 0,
                (a0 >> 8) & 1, (a1 >> 12) & 1, (a1 >> 13) & 1,
                (a2 >> 12) & 0xF, (a2 >> 10) & 3,
                lo and hx(lo) or "-", hi and hx(hi) or "-")
        end
    end

    local f = io.open(string.format("%soam_%s_%05d.txt", exp_dir, event, frames), "w")
    if f then
        f:write(string.format("frame %d event %s dispcnt %s\n", frames, event, h4(disp)))
        f:write(string.format("obj_1d_mapping %d bg_mode %d bg_enable %d obj_enable %d forced_blank %d\n",
            oneD and 1 or 0, disp & 7,
            (disp >> 8) & 0xF, (disp >> 12) & 1, (disp >> 7) & 1))
        for k = 0, 3 do
            f:write(string.format("BG%dCNT %s\n", k, h4(r16(BGCNT[k + 1]) or 0)))
        end
        f:write(string.format("oam_enabled %d oam_onscreen %d covering_window %d\n",
            enabled, onscreen, #covering))
        f:write("--- entries (non-zero, enabled) ---\n")
        for _, line in ipairs(detail) do f:write(line .. "\n") end
        f:write("--- all 128 raw entries ---\n")
        for i = 0, 127 do
            f:write(string.format("%3d %s %s %s\n", i, h4(oam[i][1]), h4(oam[i][2]), h4(oam[i][3])))
        end
        f:close()
    end

    row({ event = "OAMSNAP", a = enabled, b = onscreen, c = #covering,
          d = oneD and "1D" or "2D",
          note = "dispcnt=" .. h4(disp) .. " cover=[" .. table.concat(covering, " ") .. "]" })
    return enabled, #covering
end

-- ---------------------------------------------------------------------------

local last_compose_desc, last_advance_frame = nil, -1000

local bp_compose = emu:setBreakpoint(function(info)
    compose_hits = compose_hits + 1
    local desc = reg("r0")
    local glyph = reg("r1")
    -- The breakpoint fires BEFORE the instruction executes, so r3 still holds
    -- whatever the previous composition left there. Read the field the
    -- instruction is about to load instead.
    local raster = desc and r32(desc + 0x20) or nil
    last_compose_desc = desc
    local x = desc and r32(desc + 4) or nil
    local y = desc and r32(desc + 8) or nil
    local buf = desc and r32(desc) or nil
    local font = desc and r32(desc + 0x0C) or nil
    -- The strip descriptor is text_object+0x80, so the object is desc-0x80 and
    -- its four strip tile slots are the ones the OAM builder and the per-frame
    -- atlas blit both use. Recording them here is what ties a byte range in
    -- OBJ VRAM to the OAM entries that display it.
    local obj = desc and (desc - 0x80) or nil
    local slots = ""
    if obj then
        slots = string.format("obj=%s t78=%d t7a=%d t7c=%d t7e=%d active=%d",
            hx(obj), r16(obj + 0x78) or -1, r16(obj + 0x7a) or -1,
            r16(obj + 0x7c) or -1, r16(obj + 0x7e) or -1, r32(obj + 0x50) or -1)
    end
    row({ event = "COMPOSE", a = hx(desc), b = glyph,
          c = x and string.format("%d", x) or "", d = y and string.format("%d", y) or "",
          note = string.format("lr=%s rasteriser=%s font=%s buffer=%s %s",
              hx(reg("r14")), hx(raster), hx(font), hx(buf), slots) })
end, COMPOSE)

local bp_advance = emu:setBreakpoint(function(info)
    advance_hits = advance_hits + 1
    local desc = reg("r6")
    local newx = reg("r0")
    local oldx = desc and r32(desc + 4) or nil
    if frames - last_advance_frame < 1 and advance_hits % 8 ~= 0 then return end
    last_advance_frame = frames
    row({ event = "ADVANCE", a = hx(desc),
          b = newx and string.format("%d", newx & 0xFF) or "",
          c = oldx and string.format("%d", oldx) or "",
          d = (newx and oldx) and string.format("%d", (newx & 0xFF) - oldx - 1) or "",
          note = "d = old + width + 1; width in column d" })
end, ADVANCE)

-- The source-cursor store 0x0800B092, upgraded from a counter to a record.
-- The breakpoint fires BEFORE the store, so [r4+0x14] is still the OLD cursor
-- and r2 is the value about to be written. r6 is the text object plus 0x60, so
-- [r6+4] is the persistent horizontal cursor and [r6+5] its y.
local bp_consume = emu:setBreakpoint(function(info)
    consume_hits = consume_hits + 1
    local obj = reg("r4")
    local newcur = reg("r2")
    local objcur = reg("r6")
    local oldcur = obj and r32(obj + 0x14) or nil
    row({ event = "CONSUME", a = hx(obj),
          b = oldcur and string.format("0x%08X", oldcur) or "",
          c = newcur and string.format("0x%08X", newcur) or "",
          d = objcur and string.format("%d", r8(objcur + 4) or -1) or "",
          note = string.format("cursor %s -> %s, persistent x byte %s",
              oldcur and string.format("0x%08X", oldcur) or "?",
              newcur and string.format("0x%08X", newcur) or "?",
              objcur and tostring(r8(objcur + 4)) or "?") })
end, CONSUME)

-- The two-glyph experiment's own entry point, armed only when the launcher names
-- it. It is the first instruction of the cave's expansion path, so a row here is
-- the engine reaching the gated branch with r1 holding the source unit.
local expand_hits = 0
local shot_after_expand = nil
local expand_addr = tonumber(os.getenv("DIALOGUE_EXPAND_ADDR") or "", 16)
local bp_expand = nil
if expand_addr then
    bp_expand = emu:setBreakpoint(function(info)
        expand_hits = expand_hits + 1
        -- The strip upload runs once per frame, so the composed pair reaches VRAM
        -- on the next frame. A screenshot three frames later is the line as the
        -- player sees it right after that reveal.
        shot_after_expand = frames + 3
        local src = reg("r0")
        local unit = reg("r1")
        local strip = reg("r5")
        local objcur = reg("r6")
        row({ event = "EXPAND", a = hx(src), b = unit,
              c = objcur and tostring(r8(objcur + 4)) or "",
              d = objcur and tostring(r8(objcur + 5)) or "",
              note = string.format("unit %s at x %s y %s, strip+4=%s",
                  tostring(unit),
                  objcur and tostring(r8(objcur + 4)) or "?",
                  objcur and tostring(r8(objcur + 5)) or "?",
                  strip and tostring(r32(strip + 4)) or "?") })
    end, expand_addr)
end

local bp_q = emu:setBreakpoint(function(info)
    qwrite_hits = qwrite_hits + 1
    row({ event = "QWRITE", a = hx(reg("r4")), b = hx(reg("r3")), c = hx(reg("r2")),
          note = "reveal pass queue entry" })
end, QWRITE)

local bp_copier = emu:setBreakpoint(function(info)
    copier_hits = copier_hits + 1
    row({ event = "COPIER", note = "dialogue load; liveness " .. copier_hits })
    pcall(function() emu:screenshot(string.format("%scopier_%05d.png", exp_dir, frames)) end)
    oam_snapshot("COPIER")
end, COPIER)

local cid
cid = callbacks:add("frame", function()
    frames = frames + 1

    if frames % OAM_PERIOD == 0 then
        oam_snapshot("TICK")
    end

    if frames % WIN_PERIOD == 0 then
        local d = win_diff()
        if d then
            row({ event = "WINDOW", a = d[1], b = d[2],
                  c = d[3] and string.format("%d", d[3]) or "",
                  d = d[4] and string.format("%d", d[4]) or "",
                  note = "changed bytes in 0x06014360..0x06014EC0; tiles first..last" })
        end
    end

    if shot_after_expand and frames >= shot_after_expand then
        shot_after_expand = nil
        pcall(function() emu:screenshot(string.format("%sexpand_%05d.png", exp_dir, frames)) end)
    end

    if frames % 60 == 0 then
        pcall(function() emu:screenshot(string.format("%sshot_%05d.png", exp_dir, frames)) end)
    end

    if frames == 5 or frames % 1200 == 0 then
        -- What the emulator itself has mapped at the patched sites. A hook that
        -- appears never to transfer is either not in the running image or not
        -- reached, and those are different bugs.
        row({ event = "ROMCHECK", a = h4(r16(0x0800B066)), b = h4(r16(0x0800B068)),
              c = h4(r16(0x087B8A00)), d = h4(r16(0x087B8A04)),
              note = string.format("romSize=%d gameCode=%s w066=%s w068=%s w7B8A00=%s w7B8A04=%s",
                  emu:romSize(), tostring(emu:getGameCode()),
                  hx(r32(0x0800B066)), hx(r32(0x0800B068)),
                  hx(r32(0x087B8A00)), hx(r32(0x087B8A04))) })
    end

    if frames >= BUDGET then
        for _, bp in ipairs({ bp_compose, bp_advance, bp_consume, bp_q, bp_copier, bp_expand }) do
            if bp then pcall(function() emu:clearBreakpoint(bp) end) end
        end
        row({ event = "SUMMARY", note = string.format(
              "compose=%d advance=%d consume=%d qwrite=%d copier=%d expand=%d oam_snaps=%d win_snaps=%d win_changes=%d",
              compose_hits, advance_hits, consume_hits, qwrite_hits, copier_hits,
              expand_hits, oam_snaps, win_snaps, win_changes) })
        callbacks:remove(cid)
        local m = io.open(done_path, "w")
        if m then m:write("done:StripProbe") m:close() end
        os.exit(0)
    end
end)
