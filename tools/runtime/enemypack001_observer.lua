-- RANDOMIZER-ENEMY-PACK-001 read-only runtime observer.
--
-- Purpose: prove the randomized ROM boots, loads maps, and progresses, and give
-- the operator a durable log of which maps were reached. It is a liveness and
-- map-identity channel for the enemy-pack smoke, not a gameplay driver.
--
-- READ-ONLY. No emulated memory is written and no input is driven. It only calls
-- emu:read32/read16, emu:screenshot and emu:getGameCode, and writes host files
-- inside the run directory named by its environment. That keeps it inside the
-- mgba-runtime rule that observers never mutate the core and never drive input.
--
-- LIVENESS. A silent channel is not negative evidence, so this observer emits two
-- independent channels:
--   * `heartbeat` rows on a fixed frame stride, so an empty log is distinguishable
--     from "the script never ran";
--   * `map` rows whenever the engine's live MapEntry pointer changes, which is
--     positive evidence that maps have been constructed and the player moved.
-- It also writes lua-ready.txt after installing its callbacks, so the launcher can
-- tell "not armed yet" from "armed and silent".

-- Output location. The TRACKED launcher (tools/runtime/run_mgba_capture.ps1) sets
-- the Lua global `rom011_marker_path` before the observer runs, and that path is
-- already validated to sit beneath the ignored build tree. Deriving the output
-- from it keeps every generated artifact inside the run directory without a
-- second contract, and without depending on environment variables, which do not
-- survive UI-driven injection into an already-running mGBA. Same convention as
-- toolkit029_placement_watch.lua and enemypack002_live_slots.lua.
local run_dir = nil
if type(rom011_marker_path) == "string" then
  run_dir = rom011_marker_path:match("^(.*)/[^/]*$")
end
local OUT_DIR = os.getenv("ENEMYPACK_OUT")
if not OUT_DIR then
  if run_dir then
    OUT_DIR = run_dir
  else
    error("no output directory: rom011_marker_path is unset and ENEMYPACK_OUT is not set")
  end
end

-- The engine's live MapEntry pointer. Sampled through the same word the
-- warp-runtime observers read; it resolves to the map table base plus
-- index * 0x38, which is how a map identity is recovered without a name guess.
local MAP_ENTRY_POINTER = 0x03001980
local MAP_TABLE_BASE = 0x0808E2E0
local MAP_ENTRY_STRIDE = 0x38

-- Strides, in frames. A frame is ~1/60 s at normal speed, but mGBA here runs
-- unthrottled, so these are frame counts rather than wall-clock bounds.
local HEARTBEAT_STRIDE = 300
local SCREENSHOT_STRIDE = 600
local SAMPLE_STRIDE = 15

local csv = io.open(OUT_DIR .. "/enemypack-observer.csv", "w")
if not csv then
  error("could not open the observer CSV for writing")
end
csv:write("frame,event,map_index,map_entry_pointer,game_code\n")
csv:flush()

local ready = io.open(OUT_DIR .. "/lua-ready.txt", "w")
if ready then
  ready:write("ready\n")
  ready:close()
end

local frame = 0
local last_map = -1
local last_pointer = 0
local last_screenshot = 0
local maps_seen = 0
local screenshots = 0

local function game_code()
  -- The 0.11 dev build returns the BARE code ("BG3E"), not "AGB-BG3E"; accept
  -- both spellings rather than asserting one, because asserting the prefixed form
  -- is a documented way to break an observer.
  local ok, code = pcall(function() return emu:getGameCode() end)
  if not ok or code == nil then return "unknown" end
  return tostring(code)
end

local function row(event, map_index, pointer)
  csv:write(string.format("%d,%s,%d,0x%08X,%s\n",
    frame, event, map_index, pointer, game_code()))
  csv:flush()
end

callbacks:add("frame", function()
  frame = frame + 1

  if frame % SAMPLE_STRIDE == 0 then
    local pointer = emu:read32(MAP_ENTRY_POINTER)
    -- A zero pointer means the engine has not built a map yet (title/menu). Only
    -- a pointer inside the map table is a map identity, so anything else is
    -- reported as "not in a map" rather than mis-indexed into a wrong number.
    local index = -1
    if pointer >= MAP_TABLE_BASE then
      local delta = pointer - MAP_TABLE_BASE
      if delta % MAP_ENTRY_STRIDE == 0 and delta < 452 * MAP_ENTRY_STRIDE then
        index = delta // MAP_ENTRY_STRIDE
      end
    end
    if index ~= last_map then
      row(index >= 0 and "map" or "map_unresolved", index, pointer)
      if index >= 0 then maps_seen = maps_seen + 1 end
      last_map = index
      last_pointer = pointer
    end
  end

  if frame % HEARTBEAT_STRIDE == 0 then
    row("heartbeat", last_map, last_pointer)
  end

  if frame % SCREENSHOT_STRIDE == 0 and frame ~= last_screenshot then
    last_screenshot = frame
    local name = string.format("%s/shot-%05d.png", OUT_DIR, frame)
    -- A screenshot is host-side output only; it does not touch emulated memory.
    local ok = pcall(function() emu:screenshot(name) end)
    if ok then screenshots = screenshots + 1 end
  end
end)

-- A summary row, written when the operator closes the window. mGBA does not give
-- the script a reliable shutdown hook, so the last heartbeat plus the file itself
-- is the evidence; this row is emitted opportunistically by a periodic check.
callbacks:add("frame", function()
  if frame > 0 and frame % 1800 == 0 then
    row("summary", last_map, last_pointer)
  end
end)

print([[enemypack observer armed]])
