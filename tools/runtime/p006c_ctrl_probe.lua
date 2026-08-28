-- P-006C bounded layout probe: locate the behavior-controller structures on
-- the player object and on the wolf, instead of assuming both actors use the
-- same offsets.
--
-- Read-only with respect to emulated memory and input.
--
-- A controller is recognized structurally, using the shape established by the
-- static decode of 0x0800AA9C / 0x0800AA4A / 0x0800AAD8:
--
--   ctrl+0x04            depth, and the push primitive guards depth < 5
--   ctrl+0x08 + 8*i      entry i = { node_ptr, table_slot }
--   entry.table_slot     lies inside the state table at 0x0870F514
--   entry.node_ptr       is a live EWRAM instance pointer
--
-- Any offset whose depth is in [1,5] and whose top entry has a table slot
-- inside the state table is reported as a controller candidate.

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")

local exp_dir = done_path:gsub("[^/\\]+$", "")
local out_path = exp_dir .. "p006c-ctrl-probe.csv"
local tick_path = exp_dir .. "frame-tick.txt"

local EWRAM_LO = 0x02000000
local EWRAM_HI = 0x02040000
local TARGET_DISPATCH = 0x0804C484
local PLAYER_SLOT = 0x03001C34
local OBJECT_BYTES = 0x2A0
local SCAN_BYTES = 0x400
local MAX_DEPTH = 5

-- State table base resolved statically from the literal pool at 0x0800AB50.
local TABLE_LO = 0x0870F514
local TABLE_HI = TABLE_LO + 0x0400 * 8

local SAMPLE_TICKS = 12

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

local function wline(line)
    local log = assert(io.open(out_path, "a"))
    log:write(line .. "\n")
    log:close()
end

-- Report every offset in the object that structurally looks like a controller.
local function probe(label, actor, tick)
    if actor == 0 or not in_ewram(actor, SCAN_BYTES) then return end
    for offset = 0, SCAN_BYTES - 0x40, 4 do
        local ctrl = actor + offset
        local depth = emu:read32(ctrl + 0x04)
        if depth >= 1 and depth <= MAX_DEPTH then
            local top = ctrl + 0x08 + ((depth - 1) * 8)
            local node = emu:read32(top)
            local slot = emu:read32(top + 4)
            if slot >= TABLE_LO and slot < TABLE_HI and (slot - TABLE_LO) % 8 == 0
                and in_ewram(node, 4) then
                wline(string.format(
                    "C,%d,%s,%08x,+%03x,%d,%08x,%08x,%d",
                    tick, label, actor, offset, depth, node, slot,
                    (slot - TABLE_LO) / 8))
            end
        end
    end
end

local function finish(status)
    local marker = io.open(done_path, "w")
    if marker then marker:write(status) marker:close() end
end

local function run()
    assert(emu ~= nil and emu:getGameCode() == "AGB-BG3E")

    local target, target_count = discover_target()
    assert(target ~= nil and target_count == 1,
        "expected exactly one target dispatch match, found " ..
        tostring(target_count))

    wline("kind,tick,actor_label,actor,offset,depth,node,slot,selector")

    local armed = assert(io.open(exp_dir .. "armed-marker.txt", "w"))
    armed:write("armed")
    armed:close()

    local tick = 0
    local stopped = false
    local callback_id

    callback_id = callbacks:add("frame", function()
        local ok, err = xpcall(function()
            if stopped then return end
            tick = tick + 1

            local tick_file = assert(io.open(tick_path, "w"))
            tick_file:write(tostring(tick))
            tick_file:close()

            -- Sample a bounded number of ticks, spaced out so a transient
            -- state is less likely to be missed, then stop on its own.
            if tick % 30 == 0 and (tick / 30) <= SAMPLE_TICKS then
                local player = emu:read32(PLAYER_SLOT)
                if not in_ewram(player, SCAN_BYTES) then player = 0 end
                probe("player", player, tick)
                probe("wolf", target, tick)
            end

            if tick > 30 * (SAMPLE_TICKS + 1) then
                stopped = true
                callbacks:remove(callback_id)
                finish("done:P006CCtrlProbe")
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
