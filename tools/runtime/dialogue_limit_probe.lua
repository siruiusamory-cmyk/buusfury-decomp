-- Dialogue line-limit probe: read the wrap limit the engine passes to its line fitter.
--
-- THIS FILE PRESSES KEYS, so it is a DRIVER, not a read-only observer. It exists because opening a
-- dialogue box needs input and the box is the only way to reach the code under test. What it records is
-- not causal evidence: the logged values are parameters the engine computes and writes itself. Opening
-- the box and reading the parameter are separate matters, and the key presses claim nothing about
-- behaviour.
--
-- WHAT IT MEASURES. The dialogue path calls the line fitter with a limit in r2:
--
--   0x0800AF12  ldr r0,[r4,#0x4c]   ; r4 = the text object, so r0 = its layout record
--   0x0800AF16  ldr r7,[r0,#0x4]    ; the limit at rest
--   0x0800AF30  sub r7,#0x14        ; 20 pixels less when [r4+0x28] == 0 and FUN_0800AE00 was non-zero
--   0x0800AF32  add r2,r7,#0x0
--   0x0800AF3A  bl 0x0803de6a       ; the fitter
--
-- Arming 0x0800AF3A therefore captures the limit in force, the layout pointer, the layout's own limit
-- field, and the flag that decides the 20-pixel reduction. The purpose is to settle two numbers and
-- whether the reduction follows the portrait, which is why the log records the flag rather than guessing.
--
-- Input schedule: after a warm-up it WALKS in a rotating direction and then talks, repeating, because an
-- A tap only opens a box when the player is standing at whoever speaks. Every key is released after each
-- step and at the end of the run.
--
-- LIVENESS. The sprite-id resolver 0x08000158 is armed as a liveness channel: it fires constantly during
-- play. A silent fitter channel with a firing liveness channel is a real negative for that scene; both
-- silent means the instrument is dead and the run proves nothing. The closing line says which it is.
--
-- Environment, set by the launcher: TOOLKIT031_OUT names the log file. DIALOGUE_PROBE_LIMIT bounds the
-- run in frames so it finishes by itself.

local OUT = os.getenv("TOOLKIT031_OUT") or "dialogue-limit-probe.txt"
local FRAME_LIMIT = tonumber(os.getenv("DIALOGUE_PROBE_LIMIT") or "0") or 0

local FITTER_CALL = 0x0800AF3A
local TEXT_OBJECT_LAYOUT = 0x4C
local TEXT_OBJECT_FLAG = 0x28
local LAYOUT_LIMIT = 0x04

local A_KEY = 0x0001
local DIRECTIONS = { 0x0010, 0x0020, 0x0040, 0x0080 }   -- right, left, up, down
local WARMUP = 240
local STEP_PERIOD = 60
local WALK_FRAMES = 40
local TALK_AFTER_WALK = 20
local TAP_LENGTH = 6
local LAST_STEP = 3000

local frames = 0
local hits = 0
local liveness = 0
local seen = {}
local finished = false

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
  return tonumber(safe(emu.read32, emu, address))
end

log(string.format("PROBE start, out=%s", OUT))

local function arm(address, label, handler)
  local ok, err = pcall(emu.setBreakpoint, emu, function()
    handler()
    return false
  end, address)
  log(string.format("ARM %s 0x%08X ok=%s err=%s", label, address, tostring(ok), tostring(err)))
end

-- LIVENESS FOR A STATE-LOAD RUN. The sprite resolver 0x08000158 counts actors as they are BUILT, so a
-- savestate load leaves it silent by construction (P-053). These two fire while PLAYING, which is what
-- makes a silent fitter channel a real negative instead of a dead instrument: the animation selector
-- runs as actors animate, and the frame reader runs as their frames advance.
arm(0x0800ECDA, "liveness-animation-selector", function()
  liveness = liveness + 1
  if liveness == 1 or liveness % 500 == 0 then
    log(string.format("LIVE frame=%d hits=%d site=animation-selector", frames, liveness))
  end
end)

arm(0x0800EF38, "liveness-frame-reader", function()
  liveness = liveness + 1
  if liveness == 1 or liveness % 500 == 0 then
    log(string.format("LIVE frame=%d hits=%d site=frame-reader", frames, liveness))
  end
end)

arm(FITTER_CALL, "fitter-call", function()
  local limit = reg("r2")
  local text_object = reg("r4")
  if not limit or not text_object then return end
  hits = hits + 1
  local layout = r32(text_object + TEXT_OBJECT_LAYOUT)
  local layout_limit = nil
  if layout and layout >= 0x08000000 then
    layout_limit = r32(layout + LAYOUT_LIMIT)
  end
  local flag = r32(text_object + TEXT_OBJECT_FLAG)
  local key = string.format("limit=%d layout=%s layout_limit=%s flag=%s",
                            limit, tostring(layout and string.format("0x%08X", layout) or "nil"),
                            tostring(layout_limit), tostring(flag))
  if hits <= 40 and not seen[key] then
    seen[key] = true
    log(string.format("FIT frame=%d limit=%d layout=0x%s layout_limit=%s flag=%s",
                      frames, limit,
                      layout and string.format("%08X", layout) or "00000000",
                      tostring(layout_limit), tostring(flag)))
  end
end)

local function hold(mask, frames_to_hold)
  emu:setKeys(mask)
  local release = frames + frames_to_hold
  local id
  id = callbacks:add("frame", function()
    if frames >= release then
      emu:setKeys(0)
      callbacks:remove(id)
    end
  end)
end

local frame_id
frame_id = callbacks:add("frame", function()
  frames = frames + 1
  if frames < WARMUP then return end
  local offset = frames - WARMUP
  if offset <= LAST_STEP and offset % STEP_PERIOD == 0 then
    local step = offset / STEP_PERIOD
    hold(DIRECTIONS[(step % #DIRECTIONS) + 1], WALK_FRAMES)
    log(string.format("WALK frame=%d dir=%d", frames, (step % #DIRECTIONS) + 1))
    local talk_at = frames + WALK_FRAMES + TALK_AFTER_WALK
    local id
    id = callbacks:add("frame", function()
      if frames >= talk_at then
        emu:setKeys(A_KEY)
        local release = frames + TAP_LENGTH
        local id2
        id2 = callbacks:add("frame", function()
          if frames >= release then
            emu:setKeys(0)
            callbacks:remove(id2)
          end
        end)
        log(string.format("TALK frame=%d", frames))
        callbacks:remove(id)
      end
    end)
  end
  if FRAME_LIMIT > 0 and frames >= FRAME_LIMIT then
    emu:setKeys(0)
    if not finished then
      finished = true
      local verdict = "UNPROVEN: liveness and the fitter were both silent"
      if liveness > 0 and hits > 0 then
        verdict = "execution observed on both channels"
      elseif liveness > 0 then
        verdict = "REAL NEGATIVE: liveness fired, the fitter did not"
      end
      log(string.format("PROBE done frames=%d fitter_calls=%d liveness=%d distinct=%d :: %s",
                        frames, hits, liveness, (function()
                          local count = 0
                          for _ in pairs(seen) do count = count + 1 end
                          return count
                        end)(), verdict))
    end
    callbacks:remove(frame_id)
  end
end)

log("PROBE armed")
