-- RANDOMIZER-ENEMY-PACK-001: read-only reward observer.
--
-- WHY THIS EXISTS. A human smoke reported that killed enemies no longer dropped
-- Zeni or items. The shipping preset writes ONLY placement coordinates, leaving the
-- sprite id, the stat selector, the behavior descriptor and the flags byte-identical,
-- so the report cannot be explained by identity corruption and has to be measured
-- rather than argued about.
--
-- WHAT IT WATCHES. Two RAM counters, both from the documented RAM map (P-010):
--   0x0300155C  Zeni
--   0x0300114C  item count
-- It records every CHANGE with the frame and the before/after value, so a kill that
-- produced no reward is visible as "no row", and a kill that produced one is visible
-- as "delta". Reading absolute values alone would not separate the two.
--
-- LIVENESS. A fixed-stride heartbeat carries both current values, so a silent
-- reward channel is distinguishable from an observer that never ran.
--
-- READ-ONLY. emu:read32 only. No emulated memory is written and no input is driven.

local OUT = os.getenv("ENEMYPACK003_OUT")
if not OUT then
  local run_dir = nil
  if type(rom011_marker_path) == "string" then
    run_dir = rom011_marker_path:match("^(.*)/[^/]*$")
  end
  if run_dir then
    OUT = run_dir .. "/enemypack003-rewards.csv"
  else
    error("no output path: set ENEMYPACK003_OUT or rom011_marker_path")
  end
end

local ZENI_ADDR = 0x0300155C
local ITEM_COUNT_ADDR = 0x0300114C
local HEARTBEAT_STRIDE = 300

local csv = assert(io.open(OUT, "w"))
csv:write("frame,event,zeni,item_count,delta_zeni,delta_items\n")
csv:flush()

local frame = 0
local last_zeni = nil
local last_items = nil
local zeni_gains = 0
local item_gains = 0

local function u32(addr)
  local ok, v = pcall(function() return emu:read32(addr) end)
  if ok then return v end
  return nil
end

local function row(event, zeni, items, dz, di)
  csv:write(string.format("%d,%s,%s,%s,%s,%s\n", frame, event,
    zeni ~= nil and tostring(zeni) or "",
    items ~= nil and tostring(items) or "",
    dz ~= nil and tostring(dz) or "",
    di ~= nil and tostring(di) or ""))
  csv:flush()
end

callbacks:add("frame", function()
  frame = frame + 1
  local zeni = u32(ZENI_ADDR)
  local items = u32(ITEM_COUNT_ADDR)

  if zeni ~= nil and last_zeni == nil then
    -- First observation: record the baseline so later deltas are meaningful.
    last_zeni = zeni
    last_items = items
    row("baseline", zeni, items, 0, 0)
  elseif zeni ~= nil and last_zeni ~= nil then
    local dz = zeni - last_zeni
    local di = (items ~= nil and last_items ~= nil) and (items - last_items) or 0
    if dz ~= 0 or di ~= 0 then
      if dz > 0 then zeni_gains = zeni_gains + 1 end
      if di > 0 then item_gains = item_gains + 1 end
      row("reward", zeni, items, dz, di)
      last_zeni = zeni
      last_items = items
    end
  end

  if frame % HEARTBEAT_STRIDE == 0 then
    row("heartbeat", zeni, items, zeni_gains, item_gains)
  end
end)

print([[enemypack003 reward observer armed]])
