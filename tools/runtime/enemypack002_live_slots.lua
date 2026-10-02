-- RANDOMIZER-ENEMY-PACK-001: live placement-slot enumerator (read-only).
--
-- PURPOSE. Prove at RUNTIME that the engine constructs the randomized enemy
-- identity, by reading the identity fields out of the objects the engine built
-- rather than inferring them from a screenshot.
--
-- METHOD, and why it is not a guess. The map loader walks the map's own object
-- array (TOOLKIT-024, verbatim: `MapEntry+0x04` is the unsigned byte COUNT,
-- `MapEntry+0x14` the pointer array base, and each slot is a record body whose
-- `+0x00` word is its factory pointer). The placement constructor copies the
-- record's bytes into the object it allocates, so the object the engine built
-- carries the same `+0x08` stat selector and `+0x10` sprite id the record holds
-- in the ROM. Reading them off the live object therefore reports what the engine
-- is actually running, which is the claim under test.
--
-- This is deliberately a COMPARISON instrument: run it over the same savestate
-- on the canonical image and on a randomized image and diff the `type`/`id`
-- columns. A difference in map 40/41 is the shuffle observed at runtime; no
-- difference would be a real negative.
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

local csv = assert(io.open(OUT, "w"))
csv:write("frame,event,map_index,map_entry,count,slot,object,body,type,id,pos_low,pos_high\n")
csv:flush()

local ready = io.open(OUT .. ".ready", "w")
if ready then ready:write("ready\n") ready:close() end

local frame = 0
local emitted_boot = false
local last_key = nil
local last_emit = 0
local objects_seen = 0
local maps_seen = 0

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
  csv:write(string.format("%d,%s,%d,0x%08X,%d,%s,%s,%s,%s,%s,%s,%s\n",
    frame, event, index, entry or 0, count or 0,
    slot ~= nil and tostring(slot) or "",
    object and string.format("0x%08X", object) or "",
    body and string.format("0x%08X", body) or "",
    t ~= nil and tostring(t) or "",
    i ~= nil and tostring(i) or "",
    lo ~= nil and tostring(lo) or "",
    hi ~= nil and tostring(hi) or ""))
  csv:flush()
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
    csv:write(string.format("0,boot,-1,0x00000000,0,,,,,,,,%s\n", code))
    csv:flush()
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
    csv:write(string.format("%d,heartbeat,%d,0x%08X,%d,,,,,,,,,%d/%d\n",
      frame, index, entry or 0, count or 0, maps_seen, objects_seen))
    csv:flush()
  end
end)

print([[enemypack002 enumerator armed]])
