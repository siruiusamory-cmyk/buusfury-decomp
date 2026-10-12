-- INPUT DRIVER for the dialogue operand measurement: it loads the read-only probe and presses keys.
--
-- WHY THIS IS A SEPARATE FILE. The runtime rule is that observers stay read-only and driving code lives
-- somewhere else. The probe (`dialogue_limit_probe.lua`) therefore touches no input at all, and this file
-- does the pressing: it dofiles the probe so both run in one emulator, then walks and talks on a bounded
-- schedule so a dialogue box opens. Nothing here writes emulated memory, and the key presses are not
-- evidence - only the probe's log is.
--
-- Bounded: it stops pressing after LAST_STEP and releases every key when it does.

-- When the launcher already loads the probe (the arrangement that demonstrably fires its channels), the
-- driver must not load it again: a second copy would re-arm the same breakpoints inside the same emulator.
-- DIAGogue_PROBE_PATH therefore names the probe only when this file is the launcher's own script.
local probe = os.getenv("DIALOGUE_PROBE_PATH")
if probe and probe ~= "" then
  dofile(probe)
end

local A_KEY = 0x0001
local DIRECTIONS = { 0x0010, 0x0020, 0x0040, 0x0080 }   -- right, left, up, down
-- The schedule starts only after the savestate has loaded: pressing keys during the load opens menus and
-- leaves the game paused, which is what made every earlier driver run silent on every channel.
local WARMUP = 0
local STEP_PERIOD = 90
local WALK_FRAMES = 45
local TAP_LENGTH = 6
local LAST_STEP = 4200

local frames = 0
local driver_id
local state_loaded = false

-- The probe exposes this hook and the launcher's bootstrap calls it once the state is in memory.
local probe_note = dialogue_probe_note
dialogue_probe_note = function(text)
  if probe_note then probe_note(text) end
  if text == "STATE loaded" then
    state_loaded = true
    frames = 0            -- the walk schedule is measured from the load, not from script start
  end
end
local log_file = os.getenv("TOOLKIT031_OUT")

local function note(line)
  local file = io.open(log_file, "a")
  if file then
    file:write(line .. "\n")
    file:close()
  end
end

local function release_after(mask, hold)
  emu:setKeys(mask)
  local release = frames + hold
  local id
  id = callbacks:add("frame", function()
    if frames >= release then
      emu:setKeys(0)
      callbacks:remove(id)
    end
  end)
end

driver_id = callbacks:add("frame", function()
  frames = frames + 1
  if not state_loaded then return end
  if frames < WARMUP then return end
  local offset = frames - WARMUP
  if offset > LAST_STEP then
    emu:setKeys(0)
    callbacks:remove(driver_id)
    note(string.format("DRIVER stopped at frame %d", frames))
    return
  end
  if offset % STEP_PERIOD == 0 then
    local step = offset / STEP_PERIOD
    release_after(DIRECTIONS[(step % #DIRECTIONS) + 1], WALK_FRAMES)
    note(string.format("DRIVER walk frame=%d dir=%d", frames, (step % #DIRECTIONS) + 1))
    local talk_at = frames + WALK_FRAMES + 20
    local id
    id = callbacks:add("frame", function()
      if frames >= talk_at then
        release_after(A_KEY, TAP_LENGTH)
        note(string.format("DRIVER talk frame=%d", frames))
        callbacks:remove(id)
      end
    end)
  end
end)

note("DRIVER armed")
