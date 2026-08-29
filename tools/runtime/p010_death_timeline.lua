-- P-010 enemy death / reward timeline observer.
--
-- Read-only with respect to emulated memory and input. It calls no setKeys,
-- addKeys or clearKeys; a driver belongs in a separate file so the input-free
-- guarantee on this capture stays checkable.
--
-- Purpose: put the death lifecycle and the reward events on ONE clock. The
-- breakpoints supply the executable anchors (HP write, EXP write); this
-- observer supplies the shared gameplay tick they are stamped with, plus the
-- enemy-side state the breakpoints cannot see.
--
-- Anchors already confirmed by earlier tickets, used here as given:
--   target +0x28C  signed 32-bit current HP, fixed point, 1024 units = 1 HP
--   target +0x238  controller root (P-006B)
--   target +0x04C  current animation clip pointer (P-006C)
--   HP <= 0        death condition, writer 0x0800FA50 (P-006A)
--
-- The wolves are discovered rather than assumed. P-007 established that
-- asserting a single enemy aborts on the two-wolf state, and absolute EWRAM
-- addresses are not stable actor identity, so each frame re-reads the slot
-- table and reports every tracked target it can still see.

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")

local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p010-timeline.csv"
local tick_path = exp_dir .. "frame-tick.txt"

local EWRAM_LO = 0x02000000
local EWRAM_HI = 0x02040000
local OBJECT_BYTES = 0x2A0

local HP = 0x28C
local CTRL = 0x238
local CLIP = 0x04C

-- Save block base, confirmed this ticket: ROM pool 0x086B7080 holds 0x03001068.
local SAVE_BASE = 0x03001068
local ZENI = SAVE_BASE + 0x4F4
local ITEM_COUNT = SAVE_BASE + 0xE4
-- Goku's XP. Character blocks stride 0x68; XP sits at block+0x24.
local GOKU_XP = 0x03001584

local SCAN_LO = 0x0203C000
local SCAN_HI = 0x0203E000
local SCAN_STEP = 4

local HORIZON = 40000

local function in_ewram(address, length)
    return address >= EWRAM_LO and address + length <= EWRAM_HI
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

-- A tracked target is any EWRAM object whose controller root and HP field both
-- read plausibly. This is deliberately loose: a false positive costs one noisy
-- row, while a false negative loses the death that the run exists to capture.
local function looks_like_actor(address)
    if not in_ewram(address, OBJECT_BYTES) then return false end
    local ctrl = emu:read32(address + CTRL)
    if ctrl == 0 then return false end
    if not in_ewram(ctrl, 4) and (ctrl < 0x08000000 or ctrl >= 0x08800000) then
        return false
    end
    local hp = emu:read32(address + HP)
    -- Live enemies in this state sit well under one million raw units.
    return hp > 0 and hp < 0x00100000
end

local function run()
    assert(emu ~= nil and emu:getGameCode() == "AGB-BG3E")

    wline("kind,tick,target,hp,hp_shown,clip,ctrl,zeni,items,xp")

    local armed = assert(io.open(exp_dir .. "armed-marker.txt", "w"))
    armed:write("armed")
    armed:close()

    local tick = 0
    local stopped = false
    local callback_id
    local tracked = {}
    local prev_zeni, prev_items, prev_xp

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
                finish("done:P010Timeline")
                return
            end
            if tick > HORIZON then
                stopped = true
                callbacks:remove(callback_id)
                finish("done:P010Timeline")
                return
            end

            local zeni = emu:read32(ZENI)
            local items = emu:read8(ITEM_COUNT)
            local xp = emu:read32(GOKU_XP)

            -- Progression edges. These are the reward side of the timeline and
            -- are logged even when no target is tracked, because a reward can
            -- land after its enemy has already been removed.
            if prev_zeni ~= nil and zeni ~= prev_zeni then
                wline(string.format("ZENI,%d,,,,,%d,%d,%d",
                    tick, zeni, items, xp))
            end
            if prev_items ~= nil and items ~= prev_items then
                wline(string.format("ITEM,%d,,,,,%d,%d,%d",
                    tick, zeni, items, xp))
            end
            if prev_xp ~= nil and xp ~= prev_xp then
                wline(string.format("XP,%d,,,,,%d,%d,%d",
                    tick, zeni, items, xp))
            end
            prev_zeni, prev_items, prev_xp = zeni, items, xp

            -- Re-scan periodically so a wolf that spawns mid-run is picked up.
            if tick % 30 == 1 then
                for address = SCAN_LO, SCAN_HI - 1, SCAN_STEP do
                    if looks_like_actor(address) and not tracked[address] then
                        tracked[address] = {hp = emu:read32(address + HP),
                                            clip = emu:read32(address + CLIP),
                                            dead_at = nil}
                        wline(string.format("SCAN,%d,%08x,%d,%d,%08x,%08x,%d,%d,%d",
                            tick, address, tracked[address].hp,
                            (tracked[address].hp + 1023) // 1024,
                            tracked[address].clip,
                            emu:read32(address + CTRL), zeni, items, xp))
                    end
                end
            end

            for address, state in pairs(tracked) do
                if in_ewram(address, OBJECT_BYTES) then
                    local hp = emu:read32(address + HP)
                    local clip = emu:read32(address + CLIP)

                    if hp ~= state.hp then
                        local kind = "HP"
                        -- HP is signed; the lethal edge is the crossing to <= 0.
                        if hp <= 0 and state.hp > 0 then
                            kind = "LETHAL"
                            state.dead_at = tick
                        end
                        wline(string.format(
                            "%s,%d,%08x,%d,%d,%08x,%08x,%d,%d,%d",
                            kind, tick, address, hp, (hp + 1023) // 1024,
                            clip, emu:read32(address + CTRL), zeni, items, xp))
                        state.hp = hp
                    end

                    -- Clip changes after the lethal hit are the death-state
                    -- lifecycle: entry, animation, and whatever precedes
                    -- removal. Before death they are ordinary combat and are
                    -- not worth a row here.
                    if clip ~= state.clip then
                        if state.dead_at ~= nil then
                            wline(string.format(
                                "DEADCLIP,%d,%08x,%d,%d,%08x,%08x,%d,%d,%d",
                                tick, address, emu:read32(address + HP),
                                (emu:read32(address + HP) + 1023) // 1024,
                                clip, emu:read32(address + CTRL),
                                zeni, items, xp))
                        end
                        state.clip = clip
                    end
                end
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
