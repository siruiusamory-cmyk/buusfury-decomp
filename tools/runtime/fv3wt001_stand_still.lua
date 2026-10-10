-- FRIEND-V3-WT-SPLIT-CONTAINER-001 release 3: the stand-still driver, WITH the observer.
--
-- WHY IT EXISTS. The action lottery needs an enemy's swing cadence measured on several builds.
-- Owner fights are the expensive part, so this drives the machine instead: it loads the read-only
-- observer and then presses A long enough to clear the pre-fight dialogue and start the battle,
-- after which it presses nothing at all. A player who stands still is the cleanest possible
-- stimulus for an enemy's cadence: every swing in the log is the enemy choosing to swing.
--
-- INPUT AUTOMATION IS NOT CAUSAL EVIDENCE for anything about the player. It is used here only to
-- hold the player still while the ENEMY's behaviour is measured at the observer's spawn-leaf
-- breakpoint. Every cadence number still comes from the game.
--
-- DRIVING LIVES IN THIS FILE, not in the observer, per docs/skills/mgba-runtime.md: the observer
-- at the path named by FV3WT001_OBSERVER stays read-only and unmodified.
--
-- BOUNDED. It releases the keys and removes its own callback at FV3WT001_DRIVE_LAST (default
-- 1080), so a run can never be left holding a button.

local observer = os.getenv("FV3WT001_OBSERVER")
assert(observer and #observer > 0, "set FV3WT001_OBSERVER to the observer's path")
dofile(observer)

local function knob(name, default)
    return tonumber(os.getenv(name) or "") or default
end

local A = 0x01
local FIRST = knob("FV3WT001_DRIVE_FIRST", 240)
local PERIOD = knob("FV3WT001_DRIVE_PERIOD", 45)
local HOLD = knob("FV3WT001_DRIVE_HOLD", 6)
local LAST = knob("FV3WT001_DRIVE_LAST", 1080)

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
        -- The marker path is the launcher's own global, not the observer's local, so this file
        -- does not depend on what the observer chose to expose.
        local marker = rom011_marker_path
        if marker then
            local mark = io.open(marker:gsub("[^/\\]+$", "") .. "drive.txt", "w")
            if mark then
                mark:write(string.format("pressed A until frame %d, then stood still\n", LAST))
                mark:close()
            end
        end
    end
end)
