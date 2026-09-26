-- MAP-WARP-RUNTIME-EDIT-001 read-only transition observer.
--
-- READ-ONLY with respect to emulated state and input: it calls the emulator's
-- memory readers, and it writes only host files inside the run directory. It
-- contains none of the input- or memory-modifying API names the read-only guard
-- in tests/unit/test_mgba_capture.py greps for, and deliberately does not spell
-- them out here either, comments included.
--
-- WHY IT EXISTS. The ticket retargets ONE existing transition - map 40's first
-- selector-1 record, the one retail sends to map 39 - at a different existing
-- map, and needs the retail engine itself to be seen arriving somewhere else.
-- A changed ROM record is not that evidence, so this observer records, from the
-- running emulator:
--
--   * the live map identity every frame it changes, so the map entered after the
--     trigger is unambiguous and attributable to a frame;
--   * the destination key bytes of the target record AS THE ENGINE'S OWN ROUTE
--     REACHES IT - MapEntry[map].+0x2C -> word[0] -> root.+0x44 -> element 0 ->
--     record - rather than from a hardcoded record address, so the record being
--     read is proved to be the one the engine would walk;
--   * the map that key resolves to, by the same two-byte scan the engine's own
--     lookup performs over the live MapEntry table;
--   * the record's four region endpoints, so "the caller-supplied position was
--     not touched" is visible in the same rows as the key that was.
--
-- A savestate restores emulated RAM, including whatever the engine built when
-- the area was last loaded, so a ROM-side record change can only be seen after
-- the engine has RE-ENTERED the area. That is why the run procedure requires the
-- operator to leave map 40 and come back before triggering the transition, and
-- why the row kinds below separate a rebuild from a state restore: `MAP` rows
-- alone cannot tell them apart, so `TARGET_ENTER` marks a genuine arrival at the
-- target map after having been elsewhere.
--
-- RUNTIME-PROVEN ADDRESSES (do NOT re-derive):
--   0x03001980 = live MapEntry pointer; table base 0x0808E2E0, stride 0x38.
-- The record route offsets come from the transition authority:
--   MapEntry + 0x2C, root + 0x40 (count) / + 0x44 (array), element width 4.

local ACTIVE_MAP_PTR = 0x03001980
local MAP_ENTRY_BASE = 0x0808E2E0
local MAP_ENTRY_SIZE = 0x38
local MAP_ENTRY_SOURCE_OFFSET = 0x2C
local ROOT_ARRAY_OFFSET = 0x44
local RECORD_REGION_OFFSET = 0x08
local RECORD_KEY_HIGH_OFFSET = 0x11
local RECORD_KEY_LOW_OFFSET = 0x12
local ELEMENT_WIDTH = 4

local MAP_COUNT = 452
local TARGET_MAP = 40
local TARGET_ELEMENT = 0

-- 120 frames is two seconds at 60fps: frequent enough that a silent channel is
-- distinguishable from a quiet one, cheap enough not to disturb play.
local HEARTBEAT_EVERY = 120
-- Bounded so a long session cannot fill the disk.
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

-- The live map identity, from the pointer the engine itself keeps.
local function live_map_index()
    local entry = safe32(ACTIVE_MAP_PTR)
    if entry == nil or entry < MAP_ENTRY_BASE then return nil, entry end
    local offset = entry - MAP_ENTRY_BASE
    if offset % MAP_ENTRY_SIZE ~= 0 then return nil, entry end
    local index = offset // MAP_ENTRY_SIZE
    if index >= MAP_COUNT then return nil, entry end
    return index, entry
end

-- The record the engine's own route reaches for one map's element, with every
-- hop recorded so the derivation is auditable in the CSV rather than asserted.
local function route_to_record(map_index, element)
    local entry = MAP_ENTRY_BASE + map_index * MAP_ENTRY_SIZE
    local source = safe32(entry + MAP_ENTRY_SOURCE_OFFSET)
    if source == nil or source < 0x08000000 then return nil end
    local root = safe32(source)
    if root == nil or root < 0x08000000 then return nil end
    local array = safe32(root + ROOT_ARRAY_OFFSET)
    if array == nil or array < 0x08000000 then return nil end
    local record = safe32(array + element * ELEMENT_WIDTH)
    if record == nil or record < 0x08000000 then return nil end
    return { entry = entry, source = source, root = root, array = array,
             record = record }
end

-- The same two-byte scan the engine's own lookup performs over the MapEntry
-- table: +0x00 and +0x01 compared separately against the record's two bytes.
local function resolve_key(high, low)
    for index = 0, MAP_COUNT - 1 do
        local base = MAP_ENTRY_BASE + index * MAP_ENTRY_SIZE
        if safe8(base) == high and safe8(base + 1) == low then
            return index
        end
    end
    return nil
end

local function hex8(value)
    if value == nil then return "" end
    return string.format("%02x", value)
end

local function hex32(value)
    if value == nil then return "" end
    return string.format("0x%08X", value)
end

local session_path = in_run("session.csv")
local session_file = assert(io.open(session_path, "w"), "cannot open session.csv")
session_file:write("kind,frame,map_index,map_entry_ptr,source,root,array,record," ..
    "key_hi,key_lo,key_resolves_to,region_hex,note\n")
session_file:flush()

local rows = 0
local function emit(kind, frame, map_index, entry, route, key_hi, key_lo, key_map, note)
    if rows >= MAX_ROWS then return end
    local region = ""
    if route ~= nil and route.record ~= nil then
        local parts = {}
        for i = 0, 7 do
            parts[#parts + 1] = hex8(safe8(route.record + RECORD_REGION_OFFSET + i))
        end
        region = table.concat(parts)
    end
    session_file:write(string.format(
        "%s,%d,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n",
        kind, frame,
        map_index and tostring(map_index) or "",
        hex32(entry),
        route and hex32(route.source) or "",
        route and hex32(route.root) or "",
        route and hex32(route.array) or "",
        route and hex32(route.record) or "",
        hex8(key_hi), hex8(key_lo),
        key_map and tostring(key_map) or "",
        region,
        note or ""))
    session_file:flush()
    rows = rows + 1
end

-- The target record's key, resolved through the live table. Read once at start
-- and again on every map change: the ROM bytes cannot change during a run, so a
-- difference between two reads would itself be a finding.
local function target_facts()
    local route = route_to_record(TARGET_MAP, TARGET_ELEMENT)
    if route == nil then return nil end
    local key_hi = safe8(route.record + RECORD_KEY_HIGH_OFFSET)
    local key_lo = safe8(route.record + RECORD_KEY_LOW_OFFSET)
    return {
        route = route,
        key_hi = key_hi,
        key_lo = key_lo,
        key_map = (key_hi ~= nil and key_lo ~= nil)
            and resolve_key(key_hi, key_lo) or nil,
    }
end

local frame = 0
local last_map = nil
local seen_other_map = false
local target_reported = false
local unresolved_reported = false

callbacks:add("frame", function()
    frame = frame + 1

    local map_index, entry = live_map_index()
    local changed = (map_index ~= nil and map_index ~= last_map)

    -- The route is re-read whenever the map changes, and once more as soon as it
    -- first resolves: the state is loaded AFTER this observer is injected, so
    -- frame 1 can still be boot code whose table reads mean nothing yet.
    local facts = nil
    if (not target_reported) or changed then
        facts = target_facts()
    end

    if (not target_reported) and facts ~= nil and facts.key_hi ~= nil then
        emit("TARGET", frame, map_index, entry, facts.route,
            facts.key_hi, facts.key_lo, facts.key_map,
            "target record via MapEntry+0x2C -> root+0x44")
        target_reported = true
    elseif (not target_reported) and (not unresolved_reported) and frame >= 600 then
        -- Ten seconds in and the route still does not resolve: say so once, so a
        -- silent channel is distinguishable from a resolved one.
        emit("TARGET_UNRESOLVED", frame, map_index, entry, nil, nil, nil, nil,
            "map " .. TARGET_MAP .. " element " .. TARGET_ELEMENT ..
            " did not resolve through MapEntry+0x2C -> root+0x44")
        unresolved_reported = true
    end

    if changed then
        local note
        if last_map == nil then
            note = "first observed map"
        else
            note = "from=" .. tostring(last_map)
        end
        if map_index ~= TARGET_MAP then
            -- Having been somewhere else is what makes a later arrival at the
            -- target map a genuine rebuild rather than a restored state.
            seen_other_map = true
        elseif seen_other_map then
            note = note .. ";rebuilt-after-leaving"
        end
        emit("MAP", frame, map_index, entry,
            facts and facts.route or nil,
            facts and facts.key_hi or nil,
            facts and facts.key_lo or nil,
            facts and facts.key_map or nil,
            note)
        last_map = map_index
    elseif frame % HEARTBEAT_EVERY == 0 then
        emit("HEARTBEAT", frame, map_index, entry, nil, nil, nil, nil, "")
    end

    if frame == 1 and type(rom011_marker_path) == "string" then
        local mk = io.open(rom011_marker_path, "w")
        if mk then mk:write("armed\n") mk:close() end
    end
end)
