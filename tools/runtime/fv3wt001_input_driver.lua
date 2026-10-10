-- FRIEND-V3-WT-SPLIT-CONTAINER-001: INPUT DRIVER, separate from the read-only observer
-- by rule (docs/skills/mgba-runtime.md section 7). This is the file that presses keys;
-- tools/runtime/fv3wt001_container_route_watch.lua never does.
--
-- WHY IT EXISTS. Measured in build/toolkit031/fv3wt001-census-noinput on this image and
-- state: over 2000 frames the dialogue record copier 0x0801227A and BOTH table-load sites
-- recorded ZERO hits while the liveness dispatch thunk 0x08046AA4 fired 49,894 times. A
-- savestate restores a dialogue that was already copied before the state was written, so
-- with no input that path is never re-entered and the selector census measures nothing.
-- Pressing A is what makes the engine load a dialogue record again.
--
-- A ONLY, and SLOW: one press per 120 frames (about two seconds), held 6 frames. No
-- directional input - a walked-off character reaches no NPC, and mashing skips the
-- per-glyph reveal. Bounded: it releases the keys and removes its own callback at
-- frame 1500, so the run cannot be left holding a button.

local A = 0x01
local FIRST = 300
local PERIOD = 120
local HOLD = 6
local LAST = 1500
local frame = 0
local cid

cid = callbacks:add("frame", function()
    frame = frame + 1
    if frame >= FIRST and frame <= LAST then
        local phase = (frame - FIRST) % PERIOD
        if phase == 0 then
            emu:setKeys(A)
        elseif phase == HOLD then
            emu:setKeys(0)
        end
    elseif frame == LAST + 1 then
        emu:setKeys(0)
        callbacks:remove(cid)
    end
end)
