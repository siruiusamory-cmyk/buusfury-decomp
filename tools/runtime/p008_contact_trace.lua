-- P-008 melee contact observer: per-variant damage equivalence.
--
-- READ-ONLY with respect to emulated memory and input. The human drives, so
-- this script must not touch input; tests assert setKeys/addKeys/clearKeys are
-- absent here, which is what guarantees a capture was human-driven.
--
-- The scripted driver already established that accepted-attack DURATION is
-- exactly 16 ticks for all three punch variants. What remains is DAMAGE
-- equivalence, which needs landed hits, so this run is human-driven combat.
--
-- Anchors, all previously established:
--   player object   slot 0x03001C34
--   clip pointer    player+0x04C, idle 0x0851C618
--   punch clips     0x0851C680, 0x0851C6A0, 0x0851C6C0
--   target HP       target+0x28C signed 32-bit
--   wolf identity   dispatch word 0x0804C484 at target+0x00
--
-- Attribution rule: a punch is credited with the HP loss observed on a wolf
-- while that punch's clip is active. The capture state holds TWO wolves and
-- both can be struck, so each wolf is tracked separately and the row records
-- WHICH wolf lost HP. A tick where two wolves lose HP at once is recorded as
-- two rows, and is flagged, because it cannot be attributed to one swing.
--
-- Wolves are rediscovered every rescan interval so the human can kill them,
-- leave the area, and return to fight respawned ones without restarting.

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")

local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p008-contact.csv"
local tick_path = exp_dir .. "frame-tick.txt"

local EWRAM_LO = 0x02000000
local EWRAM_HI = 0x02040000
local PLAYER_SLOT = 0x03001C34
local KEY_ADDRESS = 0x03003304
local TARGET_DISPATCH = 0x0804C484
local OBJECT_BYTES = 0x2A0
local CLIP = 0x04C
local IDLE_CLIP = 0x0851C618
local HP_OFFSET = 0x28C

-- The three normal-melee variants, indices 4, 5 and 6 of the character
-- animation table at 0x0851C898. Membership is tested explicitly rather than
-- inferred from "not idle", because the player has many non-idle clips that
-- are not punches, such as being hurt.
local PUNCH_CLIPS = {
    [0x0851C680] = true,
    [0x0851C6A0] = true,
    [0x0851C6C0] = true,
}

local MAX_TARGETS = 32
local RESCAN_TICKS = 15
local HORIZON = 60000

local function in_ewram(address, length)
    return address >= EWRAM_LO and address + length <= EWRAM_HI
end

local function read_s32(address)
    local value = emu:read32(address)
    if value >= 0x80000000 then return value - 0x100000000 end
    return value
end

local function discover_targets()
    local found = {}
    for address = EWRAM_LO, EWRAM_HI - OBJECT_BYTES, 4 do
        if emu:read32(address) == TARGET_DISPATCH then
            found[#found + 1] = address
            if #found >= MAX_TARGETS then break end
        end
    end
    return found
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

    wline("kind,tick,clip,active_punch,punch_start,wolf,hp,hp_delta," ..
        "simultaneous,keys")

    local armed = assert(io.open(exp_dir .. "armed-marker.txt", "w"))
    armed:write("armed")
    armed:close()

    local tick = 0
    local stopped = false
    local targets = {}
    local rescan_at = 0
    local hp_prev = {}
    local prev_clip = nil
    local active_punch = nil
    local punch_start = nil
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
                callbacks:remove(callback_id)
                finish("done:P008Contact")
                return
            end
            if tick > HORIZON then
                stopped = true
                callbacks:remove(callback_id)
                finish("done:P008Contact")
                return
            end

            if tick >= rescan_at then
                targets = discover_targets()
                rescan_at = tick + RESCAN_TICKS
            end

            local player = emu:read32(PLAYER_SLOT)
            if not in_ewram(player, OBJECT_BYTES) then return end
            local keys = emu:read16(KEY_ADDRESS)
            local clip = emu:read32(player + CLIP)

            -- Track which punch variant is currently animating.
            --
            -- Latch on any transition INTO a punch clip, not only on
            -- idle-to-punch. Requiring the previous clip to be idle was wrong:
            -- in real combat the player goes punch to punch, or hurt to punch,
            -- without passing through idle. In run 20260828-111132-b8551f49
            -- that made active_punch latch once at tick 857 on 0x0851C628, a
            -- non-punch clip, and never update, so all 30 rows carried a stale
            -- value. The damage figures there survived only because the "clip"
            -- column is read live at the hit tick.
            if prev_clip ~= clip then
                if PUNCH_CLIPS[clip] then
                    active_punch = clip
                    punch_start = tick
                else
                    active_punch = nil
                    punch_start = nil
                end
                prev_clip = clip
            end

            -- Collect every wolf that lost HP this tick before writing any
            -- row, so a tick affecting two wolves can be marked as such
            -- rather than silently credited to one swing.
            local drops = {}
            for _, target in ipairs(targets) do
                if in_ewram(target, OBJECT_BYTES)
                    and emu:read32(target) == TARGET_DISPATCH then
                    local hp = read_s32(target + HP_OFFSET)
                    local was = hp_prev[target]
                    if was ~= nil and hp < was then
                        drops[#drops + 1] = { target, hp, hp - was }
                    end
                    hp_prev[target] = hp
                end
            end

            local simultaneous = 0
            if #drops > 1 then simultaneous = 1 end
            for _, d in ipairs(drops) do
                wline(string.format(
                    "HIT,%d,%08x,%s,%s,%08x,%d,%d,%d,%04x",
                    tick, clip,
                    active_punch and string.format("%08x", active_punch)
                        or "none",
                    punch_start and tostring(punch_start) or "none",
                    d[1], d[2], d[3], simultaneous, keys))
            end
        end, function(e)
            return tostring(e) .. "\n" .. debug.traceback(e, 2)
        end)
        if not ok then
            stopped = true
            callbacks:remove(callback_id)
            finish("error:frame:" .. err)
        end
    end)
end

local ok, err = xpcall(run, function(e)
    return tostring(e) .. "\n" .. debug.traceback(e, 2)
end)
if not ok then finish("error:init:" .. err) end
