-- RANDOMIZER-ENEMY-PACK-001: live placement-slot enumerator (read-only).
--
-- PURPOSE. Show which enemy identity and coordinates the RUNNING IMAGE serves for
-- each of a map's object-array slots, so the same savestate can be compared across
-- the canonical image and a randomized derivative.
--
-- WHAT IT READS, stated exactly, because an earlier version of this header
-- overstated it and a reviewer was right to reject the claim. The map loader walks
-- the map's own object array (TOOLKIT-024, verbatim: `MapEntry+0x04` is the
-- unsigned byte COUNT, `MapEntry+0x14` the pointer array base, and each slot is a
-- record body whose `+0x00` word is its factory pointer). This observer follows
-- that route and reads the RECORD out of the currently loaded ROM: `+0x08` is the
-- stat selector, `+0x10` the sprite id, `+0x0C` the position.
--
-- So it reports what the image SERVES, not what an actor object ends up holding.
-- It distinguishes a build that applied the edits from one that did not, which is
-- what this comparison needs, and it does NOT by itself prove that a constructed
-- actor carries the randomized identity. That stronger statement needs an observer
-- over live actor objects; see section 10 of
-- docs/research/ENEMY_RANDOMIZER_VERIFICATION.md, where it is recorded as open.
--
-- This is deliberately a COMPARISON instrument: run it over the same savestate on
-- the canonical image and on a randomized image and diff the `type`/`id` columns.
-- A difference in map 40/41 is the edit observed at runtime; no difference would be
-- a real negative.
--
-- READ-ONLY. It calls emu:read8/read32 and emu:screenshot only. It writes no
-- emulated memory and drives no input, so the observer guarantee enforced by
-- tests/unit/test_mgba_capture.py holds.
--
-- LIVENESS. Silent output is never treated as a negative: every run writes a
-- header immediately, a `boot` row on the first frame, and a `heartbeat` row on a
-- fixed stride, so "the script never ran" is distinguishable from "the map had no
-- placement objects".

-- Output location. The TRACKED launcher (tools/runtime/run_mgba_capture.ps1)
-- sets the Lua global `rom011_marker_path` before the observer runs, and it
-- already validated that path to sit beneath the ignored build tree. Deriving the
-- CSV path from it keeps every generated artifact inside the run directory
-- without a second contract, and without depending on environment variables,
-- which do not survive UI-driven injection into an already-running mGBA. This is
-- the same convention toolkit029_placement_watch.lua uses.
--
-- ENEMYPACK002_OUT remains supported for a caller that sets it explicitly.
local run_dir = nil
if type(rom011_marker_path) == "string" then
  run_dir = rom011_marker_path:match("^(.*)/[^/]*$")
end
local OUT = os.getenv("ENEMYPACK002_OUT")
if not OUT then
  if run_dir then
    OUT = run_dir .. "/enemypack002-slots.csv"
  else
    error("no output path: rom011_marker_path is unset and ENEMYPACK002_OUT is not set")
  end
end

local ACTIVE_MAP_PTR = 0x03001980   -- ROM-007: live MapEntry pointer
local MAP_TABLE_BASE = 0x0808E2E0   -- buus_fury_usa_rev0 map table
local MAP_ENTRY_STRIDE = 0x38
local MAP_COUNT = 452
local PLACEMENT_FACTORY = 0x0800FD55

local HEARTBEAT_STRIDE = 600
local ROW_STRIDE = 900

-- One header, and EVERY row emits the same number of columns. An earlier revision
-- wrote 13 fields in the boot row and 14 in the heartbeat row against a 12-column
-- header, which makes the file unparseable by the reader that is supposed to diff
-- two runs - the exact purpose this instrument exists for. `note` carries the
-- per-row extra (the game code on boot, the seen counters on a heartbeat) in the
-- one column reserved for it, so the shape is uniform.
local HEADER = "frame,event,map_index,map_entry,count,slot,object,body,type,id,pos_low,pos_high,note\n"
local COLUMNS = 13

local csv = assert(io.open(OUT, "w"))
csv:write(HEADER)
csv:flush()

local ready = io.open(OUT .. ".ready", "w")
if ready then ready:write("ready\n") ready:close() end

local frame = 0
local emitted_boot = false
local last_key = nil
local last_emit = 0
local objects_seen = 0
local maps_seen = 0

--- Write one row, always COLUMNS wide, refusing to emit a ragged line.
local function write_row(fields, note)
  while #fields < COLUMNS - 1 do fields[#fields + 1] = "" end
  fields[COLUMNS] = note or ""
  assert(#fields == COLUMNS, "row has " .. #fields .. " columns, expected " .. COLUMNS)
  csv:write(table.concat(fields, ",") .. "\n")
  csv:flush()
end

local function u8(addr)
  local ok, v = pcall(function() return emu:read8(addr) end)
  if ok then return v end
  return nil
end

local function u32(addr)
  local ok, v = pcall(function() return emu:read32(addr) end)
  if ok then return v end
  return nil
end

local function map_index_of(pointer)
  if pointer == nil or pointer < MAP_TABLE_BASE then return -1 end
  local delta = pointer - MAP_TABLE_BASE
  if delta % MAP_ENTRY_STRIDE ~= 0 then return -1 end
  local index = delta // MAP_ENTRY_STRIDE
  if index >= MAP_COUNT then return -1 end
  return index
end

local function emit(event, index, entry, count, slot, object, body, t, i, lo, hi)
  write_row({
    tostring(frame), event, tostring(index),
    string.format("0x%08X", entry or 0), tostring(count or 0),
    slot ~= nil and tostring(slot) or "",
    object and string.format("0x%08X", object) or "",
    body and string.format("0x%08X", body) or "",
    t ~= nil and tostring(t) or "",
    i ~= nil and tostring(i) or "",
    lo ~= nil and tostring(lo) or "",
    hi ~= nil and tostring(hi) or "",
  })
end

local function survey(event)
  local entry = u32(ACTIVE_MAP_PTR)
  local index = map_index_of(entry)
  if entry == nil or index < 0 then
    emit(event, index, entry, 0, nil, nil, nil, nil, nil, nil, nil)
    return nil
  end
  local count = u8(entry + 0x04)
  local array = u32(entry + 0x14)
  if count == nil or array == nil or count == 0 or array == 0 then
    emit(event, index, entry, count, nil, nil, nil, nil, nil, nil, nil)
    return index
  end
  for slot = 0, count - 1 do
    local body = u32(array + slot * 4)
    if body ~= nil and body ~= 0 then
      local factory = u32(body)
      if factory == PLACEMENT_FACTORY then
        -- The record body the engine is reading for THIS load. Its +0x08 and
        -- +0x10 are the identity the constructor will install, so reporting them
        -- per slot is the survey: diff the type/id columns between two images run
        -- from the same savestate.
        emit(event, index, entry, count, slot, nil, body,
             u32(body + 0x08), u32(body + 0x10),
             u32(body + 0x0C) & 0xFFFF, (u32(body + 0x0C) >> 16) & 0xFFFF)
        objects_seen = objects_seen + 1
      end
    end
  end
  return index
end

callbacks:add("frame", function()
  frame = frame + 1

  if not emitted_boot then
    emitted_boot = true
    local code = "unknown"
    local ok, value = pcall(function() return emu:getGameCode() end)
    if ok and value then code = tostring(value) end
    write_row({"0", "boot", "-1", "0x00000000", "0"}, "game_code=" .. code)
  end

  -- Emit when the live map state actually CHANGES, rather than on a clock. The
  -- savestate load settles over several frames, so a settled survey is worth more
  -- than a dense one, and a deduplicated log is directly diffable between the
  -- canonical and randomized runs.
  local entry = u32(ACTIVE_MAP_PTR)
  local index = map_index_of(entry)
  local array = (index >= 0) and u32(entry + 0x14) or 0
  local count = (index >= 0) and u8(entry + 0x04) or 0
  local key = string.format("%d:%s:%s", index, tostring(array), tostring(count))
  if index >= 0 then
    if key ~= last_key then
      if last_key == nil then
        maps_seen = maps_seen + 1
      end
      survey("map")
      last_key = key
      last_emit = frame
    elseif frame - last_emit >= ROW_STRIDE then
      last_emit = frame
      survey("dwell")
    end
  end

  if frame % HEARTBEAT_STRIDE == 0 then
    write_row(
      {tostring(frame), "heartbeat", tostring(index),
       string.format("0x%08X", entry or 0), tostring(count or 0)},
      string.format("maps_seen=%d objects_seen=%d", maps_seen, objects_seen))
  end
end)

print([[enemypack002 enumerator armed]])
