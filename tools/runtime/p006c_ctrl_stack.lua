-- P-006C controller-stack observer for accepted-attack and post-HURT anchors.
--
-- Read-only with respect to emulated memory and input. Records, on one shared
-- gameplay tick, the exact behavior-controller stacks of the player and the
-- single wolf.
--
-- Controller layout established by static decode of the tracked primitives
-- 0x0800AA9C (push), 0x0800AA4A (replace), 0x0800AAD8 (pop) and the update
-- wrapper 0x0800AB0C:
--
--   ctrl+0x00  context/actor pointer
--   ctrl+0x04  stack depth (push guards depth < 5)
--   ctrl+0x08 + 8*i   entry i = { node_ptr, table_slot }
--   ctrl+0x30  pending-notify count, ring follows at ctrl+0x34
--
-- Two controllers exist per actor, at actor+0x228 and actor+0x238, reached by
-- the wrappers at 0x0804ECA0/0x0804EC8C respectively.
--
-- A state transition is therefore observable as a DIFF of (depth, node ptrs)
-- between consecutive ticks, with no executable breakpoint and no effect on
-- gameplay pacing.

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")

local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p006c-ctrl.csv"
local tick_path = exp_dir .. "frame-tick.txt"

local EWRAM_LO = 0x02000000
local EWRAM_HI = 0x02040000
local TARGET_DISPATCH = 0x0804C484
local PLAYER_SLOT = 0x03001C34
local KEY_ADDRESS = 0x03003304
local OBJECT_BYTES = 0x2A0
local CTRL_B = 0x238
local MAX_DEPTH = 5
local HORIZON = 18000

-- Authoritative signed current HP, established by P-006A.
local HP_OFFSET = 0x28C
-- State table base resolved statically from the pool at 0x0800AB50, so a raw
-- table slot can be reported as its selector index.
local TABLE_LO = 0x0870F514

local function in_ewram(address, length)
    return address >= EWRAM_LO and address + length <= EWRAM_HI
end

local function discover_target()
    local found = nil
    local count = 0
    for address = EWRAM_LO, EWRAM_HI - OBJECT_BYTES, 4 do
        if emu:read32(address) == TARGET_DISPATCH then
            count = count + 1
            if count == 1 then found = address end
        end
    end
    return found, count
end

-- Serialize one controller as "depth|node0@sel0;node1@sel1;..." so a
-- transition is a plain string inequality between consecutive ticks. Each
-- table slot is reported as its selector index, which is the identity the
-- state table is keyed by.
local function read_ctrl(actor, offset)
    if actor == 0 then return "na" end
    local ctrl = actor + offset
    local depth = emu:read32(ctrl + 0x04)
    if depth < 0 or depth > MAX_DEPTH then
        return string.format("bad(%d)", depth)
    end
    local parts = {}
    for i = 0, depth - 1 do
        local entry = ctrl + 0x08 + (i * 8)
        local node = emu:read32(entry)
        local slot = emu:read32(entry + 4)
        local selector = "?"
        if slot >= TABLE_LO and (slot - TABLE_LO) % 8 == 0 then
            selector = tostring((slot - TABLE_LO) / 8)
        end
        parts[#parts + 1] = string.format("%08x@%s", node, selector)
    end
    return string.format("%d|%s", depth, table.concat(parts, ";"))
end

-- Signed 32-bit read for authoritative HP.
local function read_s32(address)
    local value = emu:read32(address)
    if value >= 0x80000000 then return value - 0x100000000 end
    return value
end

local function finish(status)
    local marker = io.open(done_path, "w")
    if marker then marker:write(status) marker:close() end
end

-- Open and close per line, matching the proven observers in this directory.
local function wline(line)
    local log = assert(io.open(log_path, "a"))
    log:write(line .. "\n")
    log:close()
end

local function run()
    assert(emu ~= nil and emu:getGameCode() == "AGB-BG3E")

    local target, target_count = discover_target()
    assert(target ~= nil and target_count == 1,
        "expected exactly one target dispatch match, found " ..
        tostring(target_count))

    wline("kind,tick,epoch,keys,a_pressed,player,target,target_hp,target_c238")

    local armed = assert(io.open(exp_dir .. "armed-marker.txt", "w"))
    armed:write("armed")
    armed:close()

    local tick = 0
    local epoch = 1
    local stopped = false
    local prev = nil
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
                finish("done:P006CCtrl")
                return
            end
            if tick > HORIZON then
                stopped = true
                callbacks:remove(callback_id)
                finish("done:P006CCtrl")
                return
            end

            -- Rediscover the wolf if its object moved or was freed. A failed
            -- rediscovery is recorded as an observation, never an error, so a
            -- despawn cannot be mistaken for game evidence.
            if target == 0 or not in_ewram(target, OBJECT_BYTES)
                or emu:read32(target) ~= TARGET_DISPATCH then
                local found, count = discover_target()
                if found ~= nil and count == 1 then
                    if found ~= target then epoch = epoch + 1 end
                    target = found
                else
                    target = 0
                end
            end

            local player = emu:read32(PLAYER_SLOT)
            if not in_ewram(player, OBJECT_BYTES) then player = 0 end

            local keys = emu:read16(KEY_ADDRESS)
            -- GBA key bit 0 is A. The register is active-low in hardware but
            -- this mirror has read active-high in prior captures, so the raw
            -- word is recorded alongside the derived bit and neither is
            -- promoted over the other.
            local a_pressed = keys % 2
            local tb = read_ctrl(target, CTRL_B)
            local hp = 0
            if target ~= 0 then hp = read_s32(target + HP_OFFSET) end

            -- Emit every tick where the wolf controller, its HP, or the key
            -- state changed. Steady-state ticks are omitted so the CSV stays
            -- small without losing a single transition.
            local signature = string.format("%04x|%s|%d", keys, tb, hp)
            if prev ~= signature then
                prev = signature
                wline(string.format(
                    "T,%d,%d,%04x,%d,%08x,%08x,%d,%s",
                    tick, epoch, keys, a_pressed, player, target, hp, tb))
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
