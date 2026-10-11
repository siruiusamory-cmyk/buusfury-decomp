-- Dialogue line-limit probe: read the limit the engine passes to its own line fitter.
--
-- READ-ONLY. This script touches no input and no emulated memory; it arms breakpoints and logs the
-- registers at them, nothing else. Its predecessor pressed keys to open a dialogue box on its own, which
-- moved the player around while the operator was trying to play: the operator drives the emulator, the
-- script only measures. Nothing is written outside its run directory.
--
-- WHAT IT MEASURES. The dialogue path calls the line fitter with a limit in r2:
--
--   0x0800AF12  ldr r0,[r4,#0x4c]   ; r4 = the text object, so r0 = its layout record
--   0x0800AF16  ldr r7,[r0,#0x4]    ; the limit at rest
--   0x0800AF30  sub r7,#0x14        ; 20 pixels less, only when FUN_0800AE00 is non-zero AND
--                                   ; [r4+0x28] == 0, so the flag alone does not decide it
--   0x0800AF32  add r2,r7,#0x0
--   0x0800AF3A  bl 0x0803de6a       ; the fitter
--
-- Arming 0x0800AF3A captures the limit in force, the layout pointer, the layout's own limit field and
-- the flag, which is how the two real values were measured: 128 for the layout at 0x08071744 and 144 for
-- the one at 0x08071730.
--
-- LIVENESS. Two channels that fire while PLAYING, because a savestate load constructs nothing and a
-- construction-time site is silent by construction (P-053): the animation selector 0x0800ECDA and the
-- frame reader 0x0800EF38. A silent fitter channel with a firing liveness channel is a real negative;
-- both silent means the instrument is unproven, and the closing line says which case it is.
--
-- Environment, set by the launcher: TOOLKIT031_OUT names the log file. DIALOGUE_PROBE_LIMIT bounds the
-- run in frames so it prints its verdict by itself.

-- The launcher names the log. A working-directory default would contradict this file's promise to write
-- only inside its run directory, so an unset variable is reported and nothing is written until it is set.
local OUT = os.getenv("TOOLKIT031_OUT")
local FRAME_LIMIT = tonumber(os.getenv("DIALOGUE_PROBE_LIMIT") or "0") or 0

local FITTER_CALL = 0x0800AF3A
local TEXT_OBJECT_LAYOUT = 0x4C
local TEXT_OBJECT_FLAG = 0x28
local LAYOUT_LIMIT = 0x04
local ANIMATION_SELECTOR = 0x0800ECDA
local FRAME_READER = 0x0800EF38

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

log(string.format("PROBE start, out=%s (read-only: no input, no writes)", OUT))

local function arm(address, label, handler)
  local ok, err = pcall(emu.setBreakpoint, emu, function()
    handler()
    return false
  end, address)
  log(string.format("ARM %s 0x%08X ok=%s err=%s", label, address, tostring(ok), tostring(err)))
end

arm(ANIMATION_SELECTOR, "liveness-animation-selector", function()
  liveness = liveness + 1
  if liveness == 1 or liveness % 500 == 0 then
    log(string.format("LIVE frame=%d hits=%d site=animation-selector", frames, liveness))
  end
end)

arm(FRAME_READER, "liveness-frame-reader", function()
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
  local key = string.format("%d/%s/%s", limit, tostring(layout_limit), tostring(flag))
  if hits <= 60 and not seen[key] then
    seen[key] = true
    log(string.format("FIT frame=%d limit=%d layout=0x%s layout_limit=%s flag=%s",
                      frames, limit,
                      layout and string.format("%08X", layout) or "00000000",
                      tostring(layout_limit), tostring(flag)))
  end
end)

local function distinct()
  local count = 0
  for _ in pairs(seen) do count = count + 1 end
  return count
end

local frame_id
frame_id = callbacks:add("frame", function()
  frames = frames + 1
  if FRAME_LIMIT > 0 and frames >= FRAME_LIMIT and not finished then
    finished = true
    local verdict = "UNPROVEN: liveness and the fitter were both silent"
    if liveness > 0 and hits > 0 then
      verdict = "execution observed on both channels"
    elseif liveness > 0 then
      verdict = "REAL NEGATIVE: liveness fired, the fitter did not"
    end
    log(string.format("PROBE done frames=%d fitter_calls=%d liveness=%d distinct=%d :: %s",
                      frames, hits, liveness, distinct(), verdict))
    callbacks:remove(frame_id)
  end
end)

-- The operand and the layout index, which the coordinator asked to tie on the machine. 0x080122A6 is the
-- box constructor reading the dialogue record's operand byte (record+3); 0x0800B29E is the text-object
-- builder storing the layout pointer it computed from the index. Logging both with the frame number gives
-- the pair: the index is r0 at the store, and 0x08071720 + 0x10 + index*0x14 is the layout.
arm(0x080122A6, "box-operand", function()
  -- The constructor loads the dialogue record's +0x03 byte here; the destination register carries the
  -- operand, and reading the record directly is the value that matters. Both are logged so a mismatch shows.
  local record = reg("r1")
  local from_register = reg("r2")
  local from_memory = nil
  if record and record >= 0x02000000 then
    local raw = emu:read8(record + 3)
    from_memory = raw
  end
  log(string.format("OPERAND frame=%d operand_register=%s operand_memory=%s record=%s",
                    frames, tostring(from_register), tostring(from_memory),
                    record and string.format("0x%08X", record) or "nil"))
end)

arm(0x0800B29E, "layout-store", function()
  local layout = reg("r0")
  local text_object = reg("r4")
  if layout == nil then return end
  local index = nil
  if layout and layout >= 0x08071720 and layout < 0x0807177C then
    index = (layout - (0x08071720 + 0x10)) // 0x14
  end
  log(string.format("LAYOUT frame=%d layout=0x%08X index=%s text_object=%s",
                    frames, layout, tostring(index),
                    text_object and string.format("0x%08X", text_object) or "nil"))
end)

-- Exposed so the bootstrap can mark the moment the savestate has loaded. Every channel line after that mark
-- is attributable to the loaded scene; a channel that stays silent afterwards is a real negative, and one
-- that is silent before it means nothing at all.
function dialogue_probe_note(text)
  log(string.format("NOTE frame=%d %s", frames, text))
end

log("PROBE armed")
