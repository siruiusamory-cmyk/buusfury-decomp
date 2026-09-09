-- TOOLKIT-030: runtime evidence that the behavior ATTACHED by the SDK to an
-- authored placement is actually EXECUTED by the original Buu's Fury engine.
--
-- Read-only with respect to emulated memory and input: this file contains no
-- key-writing or memory-writing calls at all, so the read-only observer
-- guarantee enforced by tests/unit/test_mgba_capture.py stays true. Any input
-- driving belongs in a separate driver script, per the standing rule that
-- observers stay read-only. (The test greps for the API names, so they are
-- deliberately not spelled out here.)
--
-- WHY THIS EXISTS. TOOLKIT-029 proved the engine INSTANTIATES an authored
-- placement. It explicitly claimed nothing about that entity's behavior.
-- TOOLKIT-030 attaches an existing verified behavior to the authored record by
-- writing its `+0x14` descriptor pointer from project state, and this observer
-- asks the one question that distinguishes "serialized" from "executed".
--
-- WHAT THE ENGINE ACTUALLY DOES. Three measured links, none assumed:
--
--   1. PLACEMENT -> DESCRIPTOR (TOOLKIT-016). A placement record's `+0x14`
--      names a 2-word descriptor {handler, payload}. The authored build writes
--      0x0808D788 there; the canonical template names 0x080555A0 instead, whose
--      handler 0x0800421D is a bare `bx lr` - the NULL behavior.
--
--   2. DESCRIPTOR -> SCRIPT (TOOLKIT-016). Handler 0x0800421F is the script
--      trampoline: `ldr r1,[r0,#4]` then `bl 0x08004038`, so the descriptor's
--      payload 0x0808D77C is interpreted as bytecode.
--
--   3. SCRIPT -> COLLISION (measured for this ticket). The script is
--          push_many(4, 52,192,84,200); native_stack(43); terminate
--      Native dispatch slot 43 of table 0x08055098 holds 0x0800099D, entry
--      0x0800099C, which pops exactly four values into a 16-byte stack struct
--      and calls 0x08009930 twice with r2 = 1:
--          0x080009D8  ldr r0,[pc,#0x198]   ; -> 0x08054FBC
--          0x080009DA  ldr r4,[r0,#0x24]
--          0x080009DE  adds r4,#0x80
--          0x080009E0  ldr r1,[r4,#0x28]    ; first grid
--          0x080009EC  ldr r1,[r4,#0x30]    ; second grid
--      0x08009930 then divides each edge by 8 (`asrs #3`, pixel -> tile) and
--      walks the tile rectangle setting bits. The sibling routine 0x080009F6 is
--      byte-for-byte the same with r2 = 0, i.e. bit CLEAR, which is what
--      identifies slot 43 as the SET direction.
--
-- So the discriminating observable is a collision rectangle at tiles
-- (52>>3, 192>>3) .. (84>>3, 200>>3) = (6,24)..(10,25). Note the operands are
-- LITERAL, pushed by the script itself: the handler never reads the placement's
-- own position, so the rect appears at those absolute tiles and NOT at the
-- authored entity. That is expected, and it is recorded here so a later reader
-- does not treat the offset as a defect.
--
-- CHANNELS, kept separate so neither can be read as the other:
--
--   CHANNEL 1 - STRUCTURE. Through the live MapEntry pointer at 0x03001980
--   (ROM-007), read the count and array base, then read slot (count-1) and
--   follow it to the authored body, and read that body's `+0x14`. This shows
--   the engine is pointed at a record carrying the AUTHORED descriptor. It does
--   NOT show the script ran.
--
--   CHANNEL 2 - EFFECT. Resolve the live collision grids through 0x08054FBC and
--   sample the authored rect's tiles plus an off-rect control tile. A rect that
--   reads SET on the authored build and CLEAR at the same tiles on the
--   canonical build is execution evidence. Sampling the SAME tiles on both
--   builds is what makes this discriminating rather than merely suggestive.
--
-- HONEST FAILURE MODE. If the grid pointers do not resolve, the sampler reports
-- `GRID-UNRESOLVED` and proves NOTHING either way. TOOLKIT-029's EWRAM scan was
-- invalidated precisely because it could not distinguish "absent" from "this
-- instrument sees nothing", so an unresolved grid is never written as a clear
-- rect. A broken instrument is not negative evidence.

local ACTIVE_MAP_PTR    = 0x03001980
local MAP_ENTRY_BASE    = 0x0808E2E0
local MAP_ENTRY_SIZE    = 0x38
local TARGET_INDEX      = 40

local AUTHORED_BODY     = 0x087EA400   -- authored placement body
local AUTHORED_ARRAY    = 0x087EA420   -- relocated 5-slot pointer array
local CANON_ARRAY       = 0x08075690   -- canonical 4-slot array

-- The two descriptors that separate the authored build from its control.
local NULL_DESCRIPTOR     = 0x080555A0  -- handler 0x0800421D, `bx lr`
local BEHAVIOR_DESCRIPTOR = 0x0808D788  -- handler 0x0800421F, script 0x0808D77C

-- Collision grid resolution, measured at 0x080009D8..0x080009EC.
local GRID_HOLDER   = 0x08054FBC
local GRID_OBJ_OFF  = 0x24
local GRID_BIAS     = 0x80
local GRID_A_OFF    = 0x28
local GRID_B_OFF    = 0x30

-- The authored rect, in the script's own literal operands.
local RECT_X0, RECT_Y0, RECT_X1, RECT_Y1 = 52, 192, 84, 200
-- 0x08009930 stride: `lsls r0,r4,#5` indexes rows by 32 bytes, and the column
-- bit is `(x & 31)` within the word at `(x >> 5) * 4`. Rows are therefore
-- 32 bytes = 256 tile columns wide.
local GRID_ROW_BYTES = 32

local run_dir = nil
if type(rom011_marker_path) == "string" then
    run_dir = rom011_marker_path:match("^(.*)/[^/]*$")
end
local function in_run(name)
    if run_dir then return run_dir .. "/" .. name end
    return name
end

local out = os.getenv("TOOLKIT030_OUT") or in_run("toolkit030-behavior.csv")
local file = assert(io.open(out, "w"), "cannot open output: " .. tostring(out))
file:write("frame,map_index,count,array_base,last_slot,body_descriptor,",
           "descriptor_kind,grid_a,grid_b,rect_set_a,rect_set_b,rect_total,",
           "control_tile_a,control_tile_b,note\n")
file:flush()

assert(emu ~= nil, "mGBA did not attach the emulation core")
assert(emu:getGameCode() == "AGB-BG3E", "unexpected game code")
assert(emu:romSize() == 8388608, "unexpected ROM size")

local frame = 0

local function safe32(addr)
    local ok, v = pcall(function() return emu:read32(addr) end)
    if ok and v then return v end
    return nil
end

local function safe8(addr)
    local ok, v = pcall(function() return emu:read8(addr) end)
    if ok and v then return v end
    return nil
end

-- Read one tile bit out of a grid, using the exact indexing 0x08009930 uses:
-- row = y >> 3, col = x >> 3, byte = base + row*32 + (col >> 3), bit = col & 7.
local function tile_bit(base, x, y)
    if not base or base == 0 then return nil end
    local col = x >> 3
    local row = y >> 3
    local byte = safe8(base + row * GRID_ROW_BYTES + (col >> 3))
    if not byte then return nil end
    return (byte >> (col & 7)) & 1
end

-- Count set tiles across the authored rectangle. Returns nil when the grid
-- cannot be read at all, so an unresolved grid never masquerades as a clear one.
local function rect_set_count(base)
    if not base or base == 0 then return nil, 0 end
    local set, total = 0, 0
    local y = RECT_Y0
    while y <= RECT_Y1 do
        local x = RECT_X0
        while x <= RECT_X1 do
            local bit = tile_bit(base, x, y)
            if bit == nil then return nil, 0 end
            total = total + 1
            set = set + bit
            x = x + 8
        end
        y = y + 8
    end
    return set, total
end

-- CORRECTION, made against a live run rather than reasoned about. `ldr r0,[pc,#N]`
-- loads the LITERAL VALUE into r0, so r0 IS 0x08054FBC - the base of a table of
-- object pointers - and the very next access is `[r0+0x24]`. Treating
-- 0x08054FBC as itself a pointer adds one dereference too many; the first run of
-- this observer did exactly that and logged grid_a = 0xE3A00001, an ARM
-- instruction word, which is what exposed the error.
local function resolve_grids()
    local obj = safe32(GRID_HOLDER + GRID_OBJ_OFF)   -- 0x030019A4 in the canonical image
    if not obj or obj == 0 then return nil, nil end
    -- The grids are runtime state, so a ROM-space value here means the chain is
    -- wrong and the sample must be refused rather than reported as a clear rect.
    local function ram(p)
        if not p or p < 0x02000000 or p >= 0x08000000 then return nil end
        return p
    end
    if not ram(obj) then return nil, nil end
    local base = obj + GRID_BIAS
    return ram(safe32(base + GRID_A_OFF)), ram(safe32(base + GRID_B_OFF))
end

local function hex(v)
    if v == nil then return "" end
    return string.format("0x%08X", v)
end

local function on_frame()
    frame = frame + 1
    -- Sample about four times a second; the grid is written once per map load,
    -- so a tight poll would only add noise and cost.
    if frame % 15 ~= 0 then return end

    local entry = safe32(ACTIVE_MAP_PTR)
    if not entry or entry < MAP_ENTRY_BASE then return end
    local index = (entry - MAP_ENTRY_BASE) // MAP_ENTRY_SIZE
    if index ~= TARGET_INDEX then return end

    local count = safe8(entry + 0x04)
    local array = safe32(entry + 0x14)
    local last_slot, descriptor = nil, nil
    if count and array and count > 0 then
        last_slot = safe32(array + (count - 1) * 4)
        if last_slot then descriptor = safe32(last_slot + 0x14) end
    end

    local kind = "OTHER"
    if descriptor == BEHAVIOR_DESCRIPTOR then
        kind = "AUTHORED-BEHAVIOR"
    elseif descriptor == NULL_DESCRIPTOR then
        kind = "INHERITED-NULL"
    elseif descriptor == nil then
        kind = "UNREAD"
    end

    local grid_a, grid_b = resolve_grids()
    local set_a, total_a = rect_set_count(grid_a)
    local set_b, total_b = rect_set_count(grid_b)

    -- An off-rect control tile. If the whole grid reads as set, the rect result
    -- means nothing, so this is what keeps a saturated grid from looking like a
    -- successful authored write.
    local ctrl_a = tile_bit(grid_a, RECT_X0, RECT_Y0 - 32)
    local ctrl_b = tile_bit(grid_b, RECT_X0, RECT_Y0 - 32)

    local note
    if set_a == nil and set_b == nil then
        note = "GRID-UNRESOLVED-scan-uninformative"
    elseif kind == "AUTHORED-BEHAVIOR" then
        note = "authored descriptor live; rect sampled"
    elseif kind == "INHERITED-NULL" then
        note = "CONTROL inherited-null descriptor; rect sampled"
    else
        note = "descriptor unrecognised"
    end

    file:write(string.format("%d,%d,%s,%s,%s,%s,%s,%s,%s,%s,%s,%d,%s,%s,%s\n",
        frame, index,
        count and tostring(count) or "",
        hex(array), hex(last_slot), hex(descriptor), kind,
        hex(grid_a), hex(grid_b),
        set_a and tostring(set_a) or "",
        set_b and tostring(set_b) or "",
        math.max(total_a, total_b),
        ctrl_a and tostring(ctrl_a) or "",
        ctrl_b and tostring(ctrl_b) or "",
        note))
    file:flush()
end

callbacks:add("frame", on_frame)
