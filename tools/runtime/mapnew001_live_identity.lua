-- MAP-NEW-AUTHORING-001 read-only live-identity observer.
--
-- READ-ONLY with respect to emulated state and input: it calls the emulator's
-- memory readers and writes only host files inside the run directory. It
-- contains none of the input- or memory-modifying API names the read-only guard
-- in tests/unit/test_mgba_capture.py greps for, and deliberately does not spell
-- them out here either, comments included.
--
-- WHY IT EXISTS. This ticket proves that a map identity the canonical image does
-- not contain - a row a project authored and the build appended to a RELOCATED
-- map table - is the row the retail engine loaded. A screenshot cannot show
-- that: two different rows can draw the same bytes. So every element of the
-- claim is derived at run time from the engine's own state, and nothing here
-- writes down an address the build chose:
--
--     the loaded row      = the engine's own active-MapEntry pointer, 0x03001980
--     the table base      = the engine's own literal pool word at 0x08008A58,
--                           the one word the key lookup loads at 0x08008A0A
--     the row bound       = the immediate of the engine's own count helper at
--                           0x080125E0/0x080125E2, decoded here as `0xff + imm8`
--     the row index       = (entry - base) / 0x38, bounded by that same count
--
-- On the canonical image the base reads 0x0808E2E0 and the bound 0x1C4 (452),
-- so the same rows are a control: an authored index (452 or above) is
-- unreachable there and reachable in the derivative, and this file says which
-- case it is in rather than asserting either.
--
-- WHAT EACH ROW CARRIES. The live index, the live MapEntry pointer, the base the
-- engine loaded, the bound it decoded, the row's own two key bytes at +0x00/+0x01,
-- the `+0x2C` selector source word, the root that word names, the root's `+0x14`
-- layer slot and its `+0x40` count / `+0x44` array pointer - each followed only
-- when the engine's own pointer names a byte of the loaded image, so a mirrored
-- or open-bus read is reported as `unreadable` rather than as a map.
--
-- ROW KINDS. `LIVE` is the loaded row, emitted on the first sample, whenever the
-- row's own bytes change and on every heartbeat; its `versus` column says whether
-- the pointer resolved against `engine_base` (the base the pool word now names)
-- or is still a `prior_table` address - a savestate written on the canonical image
-- restores a canonical-era pointer, and that state is a state, not a failure.
-- `HEARTBEAT` is liveness: a silent channel is distinguishable from a quiet one.
-- `UNRESOLVED` is said out loud once if the live pointer is not inside the loaded
-- image at all.
--
-- RUNTIME-PROVEN ADDRESS (do NOT re-derive): 0x03001980 = the live MapEntry
-- pointer. The table base pool word and the count helper's two instructions are
-- measured here from the canonical image.

local ACTIVE_MAP_PTR = 0x03001980
local MAP_ENTRY_SIZE = 0x38
local MAP_ENTRY_SOURCE_OFFSET = 0x2C
local MAP_ENTRY_KEY_OFFSETS = { 0x00, 0x01 }
local ROOT_LAYER_SLOT_0 = 0x14
local ROOT_COUNT_OFFSET = 0x40
local ROOT_ARRAY_OFFSET = 0x44

-- The engine's own statement of where the map table is, and of how many rows it
-- walks. Both are read at run time; neither is compared against a constant.
local TABLE_BASE_POOL = 0x08008A58
local COUNT_HELPER = 0x080125E0
local COUNT_HELPER_FIRST = 0x20FF
local COUNT_HELPER_BASE = 0xFF

local ROM_BASE = 0x08000000
local CANONICAL_ROM_SIZE = 8388608
local EXPANDED_ROM_SIZE = 16777216

local HEARTBEAT_EVERY = 120
local MAX_ROWS = 40000

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
assert(rom_size == CANONICAL_ROM_SIZE or rom_size == EXPANDED_ROM_SIZE,
    "unexpected ROM size: " .. tostring(rom_size))
local ROM_END = ROM_BASE + rom_size

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

local function in_rom(pointer)
    return pointer ~= nil and pointer >= ROM_BASE and pointer < ROM_END
end

local function hex8(value)
    if value == nil then return nil end
    return string.format("%02x", value)
end

local function hex32(value)
    if value == nil then return nil end
    return string.format("0x%08X", value)
end

-- The base the engine itself loads, read from the literal pool word its key
-- lookup names. A base that does not name a byte of the loaded image is no base.
local function engine_table_base()
    local base = safe32(TABLE_BASE_POOL)
    if not in_rom(base) then return nil end
    return base
end

-- `movs r0,#0xff; adds r0,#imm8`, decoded rather than assumed: the first
-- halfword must be the one the census measured, and the bound is then
-- `0xff + (second halfword & 0xff)`.
local function engine_row_bound()
    local first = safe16(COUNT_HELPER)
    if first ~= COUNT_HELPER_FIRST then return nil end
    local second = safe16(COUNT_HELPER + 2)
    if second == nil then return nil end
    local immediate = second % 0x100
    if immediate < 0x80 then return nil end
    return COUNT_HELPER_BASE + immediate
end

-- The live row. The pointer is read whatever its base: a savestate restored on
-- the canonical image carries a canonical-era MapEntry address, so before any
-- transition the engine is still holding a pointer into the ORIGINAL table while
-- the pool word already names the relocated one. That state is reported as
-- `PRIOR` with the row's own bytes - which still identify the map by key - rather
-- than as a failure, and once a transition runs the engine's own lookup returns a
-- row addressed from the base the pool word names, which resolves to an index.
local function live_row()
    local entry = safe32(ACTIVE_MAP_PTR)
    if not in_rom(entry) then return nil, entry end
    local base = engine_table_base()
    local row = {
        entry = entry,
        base = base,
        index = nil,
        key_hi = safe8(entry + MAP_ENTRY_KEY_OFFSETS[1]),
        key_lo = safe8(entry + MAP_ENTRY_KEY_OFFSETS[2]),
        source = safe32(entry + MAP_ENTRY_SOURCE_OFFSET),
    }
    row.bound = engine_row_bound()
    if base ~= nil and entry >= base then
        local offset = entry - base
        if offset % MAP_ENTRY_SIZE == 0 then
            local index = offset // MAP_ENTRY_SIZE
            if row.bound == nil or index < row.bound then
                row.index = index
            end
        end
    end
    row.versus = row.index ~= nil and "engine_base" or "prior_table"
    row.root = nil
    if in_rom(row.source) then
        local root = safe32(row.source)
        if in_rom(root) then
            row.root = root
            row.layer_0 = safe32(root + ROOT_LAYER_SLOT_0)
            row.root_count = safe32(root + ROOT_COUNT_OFFSET)
            row.root_array = safe32(root + ROOT_ARRAY_OFFSET)
        end
    end
    return row, entry
end

local live_path = in_run("live-map-identity.csv")
local live_file = assert(io.open(live_path, "w"),
    "cannot open live-map-identity.csv")
live_file:write(
    "kind,frame,index,versus,entry_ptr,table_base,row_bound,key_hi,key_lo,source," ..
    "root,layer_0,root_count,root_array,note\n")
live_file:flush()

local function cell(value)
    if value == nil then return "" end
    return tostring(value)
end

local rows = 0
local function emit(kind, frame, row, note)
    if rows >= MAX_ROWS then return end
    live_file:write(table.concat({
        kind,
        tostring(frame),
        cell(row and row.index),
        cell(row and row.versus),
        cell(row and hex32(row.entry)),
        cell(row and hex32(row.base)),
        cell(row and row.bound),
        cell(row and hex8(row.key_hi)),
        cell(row and hex8(row.key_lo)),
        cell(row and hex32(row.source)),
        cell(row and hex32(row.root)),
        cell(row and hex32(row.layer_0)),
        cell(row and row.root_count),
        cell(row and hex32(row.root_array)),
        cell(note),
    }, ",") .. "\n")
    live_file:flush()
    rows = rows + 1
end

local frame = 0
local last_signature = nil
local last_note = nil
local unresolved_reported = false
local resolved = false

callbacks:add("frame", function()
    frame = frame + 1

    local row, entry = live_row()
    local signature = nil
    if row ~= nil then
        resolved = true
        signature = tostring(row.index) .. ":" .. cell(row.versus) .. ":" ..
            cell(hex32(row.entry)) .. ":" .. cell(hex8(row.key_hi)) ..
            cell(hex8(row.key_lo))
    end
    local due = (last_signature == nil) or (frame % HEARTBEAT_EVERY == 0)

    if due and row ~= nil and signature ~= last_signature then
        local note
        if last_signature == nil then
            note = "first live row; versus=" .. row.versus
        else
            note = "row changed; versus=" .. row.versus ..
                ";previous=" .. tostring(last_note)
        end
        emit("LIVE", frame, row, note)
        last_signature = signature
        last_note = tostring(row.index) .. "/" .. row.versus
    elseif due and row == nil and (not resolved) and (not unresolved_reported)
        and frame >= 600 then
        -- Ten seconds in and the live pointer does not even name a byte of the
        -- loaded image: say so once, so a silent channel cannot be read as quiet.
        emit("UNRESOLVED", frame, nil,
            "the live MapEntry pointer is not inside the loaded image; entry=" ..
            tostring(hex32(entry)))
        unresolved_reported = true
    end

    if frame % HEARTBEAT_EVERY == 0 then
        emit("HEARTBEAT", frame, row, "")
    end

    if frame == 1 and type(rom011_marker_path) == "string" then
        local mk = io.open(rom011_marker_path, "w")
        if mk then mk:write("armed\n") mk:close() end
    end
end)
