-- P-008 scripted melee driver and per-variant equivalence probe.
--
-- THIS SCRIPT WRITES INPUT. It is deliberately a separate tool from the
-- read-only observers in this directory. Those observers are guaranteed
-- input-free, and tests in tests/unit/test_mgba_capture.py assert that
-- "setKeys" does not appear in them. Do not merge this driver into one of
-- them; that would silently void the read-only evidence guarantee.
--
-- Purpose: the operator asked that repetitive button mashing be scripted rather
-- than performed by hand. This presses A on a varying interval and records, for
-- every accepted punch, the clip variant chosen and the timing of the attack,
-- so the three variants can be compared on equal terms.
--
-- P-006C anchors used here:
--   player object   slot 0x03001C34
--   clip pointer    player+0x04C, idle 0x0851C618
--   accepted punch  idle -> punch clip while A is held
--   target HP       target+0x28C signed 32-bit
--   damage record   record+0x18, authoritative writer 0x0800FA50
--
-- P-008 established that the three punch clips are contiguous indices 4, 5 and
-- 6 of the character animation table at 0x0851C898.
--
-- INTERVAL VARIATION IS DELIBERATE. A fixed-period mash can alias against an
-- internal timer and manufacture a pattern that is an artifact of the script
-- rather than the game. The press interval therefore cycles through a small
-- set of odd and even values, and the interval used is recorded on every row
-- so any suspected aliasing can be checked after the fact.

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")

local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p008-equivalence.csv"
local tick_path = exp_dir .. "frame-tick.txt"

local EWRAM_LO = 0x02000000
local EWRAM_HI = 0x02040000
local PLAYER_SLOT = 0x03001C34
local OBJECT_BYTES = 0x2A0
local CLIP = 0x04C
local IDLE_CLIP = 0x0851C618
local HP_OFFSET = 0x28C
local TARGET_DISPATCH = 0x0804C484

-- Bit index for A, per the mGBA scripting documentation, where C.GBA_KEY.A is
-- 0 and a key mask is 1 shifted by that index.
local KEY_A_MASK = 1

-- Press A for this many frames, then release for a varying gap. Accepted
-- punches are gated to roughly one per 20 ticks by the game itself, so these
-- gaps sit around and above that floor without being a single fixed period.
local PRESS_FRAMES = 4
local GAPS = { 18, 21, 24, 19, 27, 22, 31, 20 }

local HORIZON = 40000

local function in_ewram(address, length)
    return address >= EWRAM_LO and address + length <= EWRAM_HI
end

local function read_s32(address)
    local value = emu:read32(address)
    if value >= 0x80000000 then return value - 0x100000000 end
    return value
end

local function discover_target()
    for address = EWRAM_LO, EWRAM_HI - OBJECT_BYTES, 4 do
        if emu:read32(address) == TARGET_DISPATCH then return address end
    end
    return 0
end

local function wline(line)
    local log = assert(io.open(log_path, "a"))
    log:write(line .. "\n")
    log:close()
end

local function finish(status)
    local marker = io.open(done_path, "w")
    if marker then marker:write(status) marker:close() end
end

local function run()
    assert(emu ~= nil and emu:getGameCode() == "AGB-BG3E")

    wline("kind,tick,clip,prev_clip,gap_used,press_tick," ..
        "duration,target,target_hp,hp_delta")

    local armed = assert(io.open(exp_dir .. "armed-marker.txt", "w"))
    armed:write("armed")
    armed:close()

    local tick = 0
    local stopped = false
    local prev_clip = nil
    local gap_index = 1
    local next_press = 30
    local press_until = 0
    local last_gap = 0
    local last_press_tick = 0
    local punch_start = nil
    local punch_clip = nil
    local prev_hp = nil
    local callback_id

    callback_id = callbacks:add("frame", function()
        local ok, err = xpcall(function()
            if stopped then return end
            tick = tick + 1

            local tick_file = assert(io.open(tick_path, "w"))
            tick_file:write(tostring(tick))
            tick_file:close()

            local stop_file = io.open(exp_dir .. "STOP-NOW.txt", "r")
            if stop_file then
                stop_file:close()
                stopped = true
                emu:clearKeys(KEY_A_MASK)
                callbacks:remove(callback_id)
                finish("done:P008Mash")
                return
            end
            if tick > HORIZON then
                stopped = true
                emu:clearKeys(KEY_A_MASK)
                callbacks:remove(callback_id)
                finish("done:P008Mash")
                return
            end

            -- Drive A on a varying cadence.
            if tick >= next_press and press_until == 0 then
                emu:addKeys(KEY_A_MASK)
                press_until = tick + PRESS_FRAMES
                last_gap = GAPS[gap_index]
                last_press_tick = tick
                gap_index = gap_index + 1
                if gap_index > #GAPS then gap_index = 1 end
            elseif press_until ~= 0 and tick >= press_until then
                emu:clearKeys(KEY_A_MASK)
                press_until = 0
                next_press = tick + last_gap
            end

            local player = emu:read32(PLAYER_SLOT)
            if not in_ewram(player, OBJECT_BYTES) then return end
            local clip = emu:read32(player + CLIP)

            local target = discover_target()
            local hp = 0
            if target ~= 0 then hp = read_s32(target + HP_OFFSET) end

            if prev_clip ~= clip then
                -- A punch begins when the clip leaves idle for a punch clip.
                if prev_clip == IDLE_CLIP and clip ~= IDLE_CLIP then
                    punch_start = tick
                    punch_clip = clip
                    prev_hp = hp
                elseif punch_start ~= nil and clip == IDLE_CLIP then
                    -- and ends when it returns to idle. Duration and any HP
                    -- change across the attack are attributed to the variant.
                    local delta = 0
                    if prev_hp ~= nil then delta = hp - prev_hp end
                    wline(string.format(
                        "PUNCH,%d,%08x,%08x,%d,%d,%d,%08x,%d,%d",
                        tick, punch_clip, IDLE_CLIP, last_gap,
                        last_press_tick, tick - punch_start,
                        target, hp, delta))
                    punch_start = nil
                    punch_clip = nil
                end
                prev_clip = clip
            end
        end, function(e)
            return tostring(e) .. "\n" .. debug.traceback(e, 2)
        end)
        if not ok then
            stopped = true
            emu:clearKeys(KEY_A_MASK)
            callbacks:remove(callback_id)
            finish("error:frame:" .. err)
        end
    end)
end

local ok, err = xpcall(run, function(e)
    return tostring(e) .. "\n" .. debug.traceback(e, 2)
end)
if not ok then finish("error:init:" .. err) end
