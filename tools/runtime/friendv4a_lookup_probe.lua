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
local DEFINITION_SLOTS = 0x54

local hits = { animation = 0, lookup = 0, lookup_mode5 = 0, resolver = 0 }
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

arm(SPRITE_RESOLVER, "sprite-resolver", function()
  hits.resolver = hits.resolver + 1
end)

-- Frame callbacks are registered through the `callbacks` table on this build.
local frame_id = nil
if callbacks and callbacks.add then
  local ok, id = pcall(function()
    return callbacks:add("frame", function()
    frames = frames + 1
    if frames % 600 == 0 then
      log(string.format("HEARTBEAT frames=%d resolver=%d animation=%d lookup=%d lookup_mode5=%d",
                        frames, hits.resolver, hits.animation, hits.lookup, hits.lookup_mode5))
    end
    if FRAME_LIMIT > 0 and frames >= FRAME_LIMIT and not started then
      started = true
      log(string.format("STOP frames=%d resolver=%d animation=%d lookup=%d lookup_mode5=%d",
                        frames, hits.resolver, hits.animation, hits.lookup, hits.lookup_mode5))
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
