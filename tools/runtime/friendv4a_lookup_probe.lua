-- FRIEND-V4-BROLY-001 release 4A read-only observer: does the actor drive the definition a script
-- resolves, and does the slot that definition is asked for exist?
--
-- WHAT IT MEASURES. The review's blocking finding was about two mechanisms meeting:
--
--   0x0800ECDA  the animation selector. `ldr r2,[r0,#0x58]` is the actor's sprite definition,
--               `r1` is the animation index, and `*(u32*)(def + 0x54 + 4*index)` is the record the
--               actor will play. A null record means the actor plays nothing.
--   0x08011C70  the actor lookup. Scripts find an actor by DEFINITION POINTER and compare it, so the
--               definition a script id resolves to must be the definition a placed actor carries.
--               `r0` is the definition being sought and `r1` the mode; mode 5 is the pointer compare.
--
-- The claim under test: with ids 73 and 98 pointing at their own definition copies while the placed
-- sites keep their retail ids, an actor placed with 98 (map 451, Heaven) or 73 (the ship scene) drives
-- the COPY, and the slot its script asks for is non-null.
--
-- WHAT IT DOES NOT DO. No emulated memory is written, no input register is touched, nothing is written
-- outside its run directory. It never loads a state: the operator plays.
--
-- LIVENESS, REPORTED AS A CASE. A silent channel is not a negative, so three channels are armed and
-- the log states which fired: the sprite-id resolver 0x08000158 (fires constantly during play), a
-- frame heartbeat, and the two sites above. If nothing fires the instrument is unproven; if liveness
-- fires and the sites are silent, that path was not taken in this run.
--
-- Environment, set by the launcher: TOOLKIT031_OUT names the log file. FRIENDV4A_FRAME_LIMIT bounds
-- the run so it finishes by itself.

local OUT = os.getenv("TOOLKIT031_OUT") or "friendv4a-lookup-probe.txt"
local FRAME_LIMIT = tonumber(os.getenv("FRIENDV4A_FRAME_LIMIT") or "0") or 0

local ANIMATION_SELECTOR = 0x0800ECDA
local ACTOR_LOOKUP = 0x08011C70
local SPRITE_RESOLVER = 0x08000158
local FRAME_READER = 0x0800EF38
local DEFINITION_SLOTS = 0x54

local hits = { animation = 0, lookup = 0, lookup_mode5 = 0, resolver = 0,
               frame_reader = 0 }
local armed = {}
local frames = 0
local started = false
local seen_definitions = {}

local function log(line)
  local file = io.open(OUT, "a")
  if file then
    file:write(line .. "\n")
    file:close()
  end
end

local function safe(fn, ...)
  local ok, value = pcall(fn, ...)
  if ok then return value end
  return nil
end

local function reg(name)
  return tonumber(safe(emu.readRegister, emu, name))
end

local function r32(address)
  if address == nil then return nil end
  return tonumber(safe(emu.read32, emu, address))
end

local function hex(value)
  if value == nil then return "nil" end
  return string.format("0x%08X", value)
end

local function report_definition(def, index)
  if def == nil or index == nil then return end
  if index < 0 or index > 63 then return end
  local slot = r32(def + DEFINITION_SLOTS + 4 * index)
  local key = hex(def) .. ":" .. tostring(index)
  if seen_definitions[key] then return end
  seen_definitions[key] = true
  log(string.format("ANIMATION def=%s index=%d slot=%s %s", hex(def), index, hex(slot),
                    slot and slot ~= 0 and "PLAYS" or "NULL"))
end

-- The signature is measured, not assumed: this build accepts `handler, address` (the project's own
-- observers use it) and rejects `address, callback` with "invoking failed". A failed arm is fatal to
-- the run's meaning, so it is logged and counted, never passed over.
local function arm(address, name, callback)
  local handler = function(_info) callback() end
  local ok = pcall(emu.setBreakpoint, emu, handler, address)
  armed[name] = ok and true or false
  log(string.format("ARM %s at 0x%08X armed=%s", name, address, tostring(ok)))
  if not ok then
    log("ARM FAILED " .. name .. ": an unarmed channel proves nothing about this run")
  end
  return ok
end

log("FRIENDV4A-OBSERVER start log=" .. OUT)
log("game code " .. tostring(safe(emu.getGameCode, emu)) ..
    " rom size " .. tostring(safe(emu.romSize, emu)))

arm(ANIMATION_SELECTOR, "animation-selector", function()
  hits.animation = hits.animation + 1
  local object = reg("r0")
  local index = reg("r1")
  local def = object and r32(object + 0x58) or nil
  report_definition(def, index)
end)

arm(ACTOR_LOOKUP, "actor-lookup", function()
  hits.lookup = hits.lookup + 1
  local def = reg("r0")
  local mode = reg("r1")
  if mode == 5 then
    hits.lookup_mode5 = hits.lookup_mode5 + 1
    log(string.format("LOOKUP mode=5 definition=%s", hex(def)))
  else
    log(string.format("LOOKUP mode=%s definition=%s", tostring(mode), hex(def)))
  end
end)

-- The resolver is the one door every actor's art goes through, and it is called with the sprite id
-- in r0 when the actor is built. Logging each distinct id once names the actors in a scene even when
-- they never change animation state, which the selector-based channels cannot see.
local resolver_ids = {}
-- The draw path: runs for every actor every frame it is drawn, so a standing actor appears here even
-- though it never re-selects its animation. `read32(r0-4)` is the actor's definition pointer.
local drawn_definitions = {}
arm(FRAME_READER, "frame-reader", function()
  hits.frame_reader = (hits.frame_reader or 0) + 1
  local component = reg("r0")
  if component == nil then return end
  local definition = r32(component - 4)
  if definition == nil then return end
  local key = hex(definition)
  local seen = drawn_definitions[key] or 0
  drawn_definitions[key] = seen + 1
  if seen == 0 then
    local record = r32(component + 0x50)
    local frames = record and r32(record) or nil
    log(string.format("DRAWN definition=%s animation_record=%s frames=%s", key, hex(record),
                      tostring(frames)))
  end
end)

arm(SPRITE_RESOLVER, "sprite-resolver", function()
  hits.resolver = hits.resolver + 1
  local sprite_id = reg("r0")
  if sprite_id == nil then return end
  local key = tostring(sprite_id)
  resolver_ids[key] = (resolver_ids[key] or 0) + 1
  if resolver_ids[key] <= 2 then
    local definition = nil
    -- 0x086B6BB4 + 4*id is the character-table word; it is dereferenced to the definition.
    definition = r32(0x086B6BB4 + 4 * sprite_id)
    log(string.format("SPRITE id=%d definition=%s", sprite_id, hex(definition)))
  end
end)

-- One-shot memory hunt for definition pointers. Every actor stores its definition at `+0x58`, so a
-- standing actor that never animates AND was built before the state was loaded is still findable: a
-- word in RAM equal to a definition address IS an actor (or a template) using that definition. Scanning
-- 256 KiB per frame is not something an observer should do, so this runs once, after the scene is up.
local HUNT = {
  { name = "donor", value = 0x086A9B78 },
  { name = "retail73", value = 0x086AB24C },
  { name = "retail98", value = 0x086AC6A4 },
  { name = "copy73", value = 0x089B2E80 },
  { name = "copy98", value = 0x089B304C },
}
local hunt_done = false

local function hunt()
  if hunt_done then return end
  hunt_done = true
  local counts = {}
  for _, region in ipairs({ { 0x02000000, 0x02040000 }, { 0x03000000, 0x03008000 } }) do
    local address = region[1]
    while address < region[2] do
      local value = r32(address)
      if value ~= nil then
        for _, target in ipairs(HUNT) do
          if value == target.value then
            counts[target.name] = (counts[target.name] or 0) + 1
            if counts[target.name] <= 3 then
              log(string.format("HUNT %s at 0x%08X animRecord=%s next=%s", target.name, address,
                                hex(r32(address - 4)), hex(r32(address + 4))))
            end
          end
        end
      end
      address = address + 4
    end
  end
  for _, target in ipairs(HUNT) do
    log(string.format("HUNT TOTAL %s = %d", target.name, counts[target.name] or 0))
  end
end

-- The dialogue box's position, at the two stores that set it.
local BOX_X_STORE = 0x0800B1D8
local BOX_Y_STORE = 0x0800B1D6

arm(BOX_X_STORE, "box-x", function()
  local x = reg("r2")
  log(string.format("BOX x=%s", tostring(x)))
end)

arm(BOX_Y_STORE, "box-y", function()
  local y = reg("r1")
  log(string.format("BOX y=%s", tostring(y)))
end)

-- Frame callbacks are registered through the `callbacks` table on this build.
local frame_id = nil
if callbacks and callbacks.add then
  local ok, id = pcall(function()
    return callbacks:add("frame", function()
    frames = frames + 1
    local drawn = 0
    for _ in pairs(drawn_definitions) do drawn = drawn + 1 end
    if frames == 900 then
      hunt()
    end
    -- Native-resolution screenshots at a few frames, into the run directory the launcher set up.
    if frames >= 600 and frames <= 18000 and frames % 300 == 0 then
      local directory = OUT:gsub("[^/\\]+$", "")
      local ok, err = pcall(function()
        return emu:screenshot(string.format("%sshot-%d.png", directory, frames))
      end)
      log(string.format("SHOT frame=%d ok=%s %s", frames, tostring(ok), tostring(err)))
    end
    if frames % 600 == 0 then
      log(string.format("HEARTBEAT frames=%d resolver=%d animation=%d lookup=%d lookup_mode5=%d",
                        frames, hits.resolver, hits.animation, hits.lookup,
                        hits.lookup_mode5, drawn))
    end
    if FRAME_LIMIT > 0 and frames >= FRAME_LIMIT and not started then
      started = true
      log(string.format("STOP frames=%d resolver=%d animation=%d lookup=%d lookup_mode5=%d",
                        frames, hits.resolver, hits.animation, hits.lookup,
                        hits.lookup_mode5, drawn))
    end
    end)
  end)
  if ok then
    frame_id = id
    log("HEARTBEAT ARMED via callbacks:add(frame)")
  else
    log("HEARTBEAT ARM FAILED: " .. tostring(id))
  end
else
  log("FRAME CALLBACK UNAVAILABLE: the heartbeat and the frame bound are not armed")
end

log(string.format("ARMED animation=%s lookup=%s resolver=%s heartbeat=%s",
                  tostring(armed["animation-selector"]), tostring(armed["actor-lookup"]),
                  tostring(armed["sprite-resolver"]), tostring(frame_id ~= nil)))
