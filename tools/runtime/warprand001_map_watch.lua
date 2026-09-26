-- ROMHACK-WARP-RANDOMIZER-001 read-only map-arrival observer.
--
-- READ-ONLY with respect to emulated state and input: it calls the emulator's
-- memory readers, and it writes only host files inside the run directory. It
-- contains none of the input- or memory-modifying API names the read-only guard
-- in tests/unit/test_mgba_capture.py greps for, and deliberately does not spell
-- them out here either, comments included.
--
-- WHY IT EXISTS. The randomized derivative changes where 496 of the 735
-- selector-1 transition records lead - 248 reciprocal door pairs moved as whole
-- pairs - and the ticket's runtime smoke is a HUMAN-OPERATED playthrough: no
-- scripted route, no automated input, no required map. What the operator cannot
-- supply by hand is the map IDENTITY on each side of a warp - the game never
-- displays it - and this project's rule is that the active MapEntry is identified
-- from runtime rather than guessed from a map name. So this observer latches, once
-- per map change, the map identity the engine itself keeps and the identity it
-- came from, which turns the playthrough into the (source map -> destination map)
-- list the ticket asks for.
--
-- It records no judgement. Whether the arrival was usable, and whether the facing
-- or the placement caused an immediate softlock, are the operator's observations
-- and are reported as such; this file supplies the map identities those
-- observations attach to, and nothing more.
--
-- RUNTIME-PROVEN ADDRESSES (do NOT re-derive):
--   0x03001980 = live MapEntry pointer; table base 0x0808E2E0, stride 0x38.
--   0x03001C34 = the player slot, stored by 0x080109AA (080109E6 str r4,[r0]).
--   0x03001C34 + 0x10 = the facing byte the engine writes, from
--   MAP-WARP-FACING-TRACE-001.

local ACTIVE_MAP_PTR = 0x03001980
local MAP_ENTRY_BASE = 0x0808E2E0
local MAP_ENTRY_SIZE = 0x38
local PLAYER_SLOT = 0x03001C34
local PLAYER_FACING_OFFSET = 0x10

local MAP_COUNT = 452

-- 120 frames is two seconds at 60fps: frequent enough that a silent channel is
-- distinguishable from a quiet one, cheap enough not to disturb play.
local HEARTBEAT_EVERY = 120
-- Bounded so a long session cannot fill the disk.
local MAX_ROWS = 20000

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

local function safe32(addr)
    local ok, v = pcall(function() return emu:read32(addr) end)
    if ok and v then return v end
    return nil
end

-- The live map identity, from the pointer the engine itself keeps. A pointer
-- that is not an aligned address in the table is reported as unresolved rather
-- than coerced into an index.
local function live_map_index()
    local entry = safe32(ACTIVE_MAP_PTR)
    if entry == nil or entry < MAP_ENTRY_BASE then return nil, entry end
    local offset = entry - MAP_ENTRY_BASE
    if offset % MAP_ENTRY_SIZE ~= 0 then return nil, entry end
    local index = offset // MAP_ENTRY_SIZE
    if index >= MAP_COUNT then return nil, entry end
    return index, entry
end

-- The live player's own facing byte, or nil when the slot does not hold a
-- pointer into work RAM. A null or implausible slot is reported as such rather
-- than dereferenced into noise.
local function live_player_facing()
    local player = safe32(PLAYER_SLOT)
    if player == nil or player < 0x02000000 or player >= 0x03008000 then
        return player, nil
    end
    return player, safe8(player + PLAYER_FACING_OFFSET)
end

local function hex8(value)
    if value == nil then return "" end
    return string.format("%02x", value)
end

local function hex32(value)
    if value == nil then return "" end
    return string.format("0x%08X", value)
end

local arrivals_path = in_run("warprand001_arrivals.csv")
local arrivals_file = assert(
    io.open(arrivals_path, "w"), "cannot open warprand001_arrivals.csv")
arrivals_file:write(
    "kind,frame,map_index,from_map,map_entry_ptr,player_ptr,player_facing_raw,note\n")
arrivals_file:flush()

local rows = 0
local function emit(kind, frame, map_index, from_map, entry, player, player_facing, note)
    if rows >= MAX_ROWS then return end
    arrivals_file:write(string.format(
        "%s,%d,%s,%s,%s,%s,%s,%s\n",
        kind, frame,
        map_index and tostring(map_index) or "",
        from_map and tostring(from_map) or "",
        hex32(entry),
        hex32(player),
        hex8(player_facing),
        note or ""))
    arrivals_file:flush()
    rows = rows + 1
end

local frame = 0
local last_map = nil
local started = false

callbacks:add("frame", function()
    frame = frame + 1

    local map_index, entry = live_map_index()
    local changed = (map_index ~= nil and map_index ~= last_map)

    if not started then
        local player, player_facing = live_player_facing()
        emit("START", frame, map_index, nil, entry, player, player_facing,
            "first live map identity")
        started = true
        last_map = map_index
    elseif changed then
        local player, player_facing = live_player_facing()
        -- The previous map is the source side of whatever warp just fired; the
        -- map this row names is the destination side. A change with no previous
        -- identity (the first read after a load) is reported as such rather than
        -- paired with a guess.
        emit("ARRIVAL", frame, map_index, last_map, entry, player, player_facing,
            last_map and ("from=" .. tostring(last_map)) or "no previous map identity")
        last_map = map_index
    elseif frame % HEARTBEAT_EVERY == 0 then
        emit("HEARTBEAT", frame, map_index, last_map, entry, nil, nil, "")
    end

    if frame == 1 and type(rom011_marker_path) == "string" then
        local mk = io.open(rom011_marker_path, "w")
        if mk then mk:write("armed\n") mk:close() end
    end
end)
