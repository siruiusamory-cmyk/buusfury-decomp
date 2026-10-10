-- INPUT DRIVER, separate from the read-only observer by rule.
--
-- WHY. The strongest missing evidence for FRIEND-V3-PLAYTEST-BOOST-001 is a
-- screenshot of a character status screen showing the boosted level. Getting past
-- the title screen is the first step of that route and this file does only that:
-- it activates the title screen's highlighted entry (A) and then repeats A at a
-- slow fixed period inside a bounded window, after which it releases every key and
-- removes itself. Driving code belongs in its own file, never inside the observer
-- (docs/skills/mgba-runtime.md section 6), and the input is deliberate and bounded
-- the way appearance001_table_watch.lua states its own key schedule.
--
-- It is deliberately blind. No direction input and no mashing: the game's menu
-- structure is not established anywhere in this repository, so a guessed multi-step
-- route would not be evidence. The run produces the first screen after the title,
-- which is what a human then needs as an exact starting point.
--
-- It writes no file and touches no emulated memory; it only presses keys.

local A = 0x01
local HOLD = 6
local FIRST = 1000
local PERIOD = 150
local LAST = 1900

local frame = 0
local cid
cid = callbacks:add("frame", function()
    frame = frame + 1
    if frame > LAST then
        emu:setKeys(0)
        callbacks:remove(cid)
        return
    end
    if frame < FIRST then return end
    local offset = frame - FIRST
    if offset % PERIOD == 0 then
        emu:setKeys(A)
    elseif offset % PERIOD == HOLD then
        emu:setKeys(0)
    end
end)
