-- INPUT DRIVER, separate from the read-only observer by rule.
--
-- Taken verbatim from the session that measured the dialogue reveal path; it is
-- tracked here so the run is reproducible from a fresh worktree (it was an
-- untracked file in the primary checkout, and untracked files do not travel).
--
-- A ONLY, and SLOW: one press every 180 frames (about three seconds), held 6.
-- Directional input is deliberately absent - an earlier version inherited a LEFT
-- press from the tracked rom_expand_001 driver, which walked the character off the
-- NPC so no dialogue ever opened. Mashing is also wrong: it skips the typewriter,
-- and the per-glyph reveal is the event being measured.
--
-- It writes no file and touches no emulated memory; it only presses keys.

local A = 0x01
local PERIOD = 180
local frame = 0
local cid

cid = callbacks:add("frame", function()
    frame = frame + 1
    local phase = frame % PERIOD
    if phase == 0 then
        emu:setKeys(A)
    elseif phase == 6 then
        emu:setKeys(0)
    end
    if frame >= 39000 then
        emu:setKeys(0)
        callbacks:remove(cid)
    end
end)
