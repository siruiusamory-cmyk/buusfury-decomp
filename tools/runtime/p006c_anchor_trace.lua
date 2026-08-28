-- P-006C shared-tick observer for accepted-attack and post-HURT anchors.
-- Read-only with respect to emulated memory and input.
local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")

local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p006c-anchor.csv"
local tick_path = exp_dir .. "frame-tick.txt"
local EWRAM_LO = 0x02000000
local EWRAM_HI = 0x02040000
local TARGET_DISPATCH = 0x0804C484
local PLAYER_SLOT = 0x03001C34
local OBJECT_BYTES = 0x2A0
local HORIZON = 18000

local function in_ewram(address, length)
    return address >= EWRAM_LO and address + length <= EWRAM_HI
end

local function discover_target()
    local found = {}
    for address = EWRAM_LO, EWRAM_HI - OBJECT_BYTES, 4 do
        if emu:read32(address) == TARGET_DISPATCH then
            found[#found + 1] = address
        end
    end
    if #found ~= 1 then
        error("expected exactly one target dispatch match, found " .. #found)
    end
    return found[1]
end

local function finish(status)
    local marker = io.open(done_path, "w")
    if marker then marker:write(status) marker:close() end
end

local function run()
    assert(emu ~= nil and emu:getGameCode() == "AGB-BG3E")

    local function wline(line)
        local log = assert(io.open(log_path, "a"))
        log:write(line .. "\n")
        log:close()
    end

    local target = discover_target()
    local epoch = 1
    wline("kind,tick,epoch,keys,target,wolf_depth,wolf_graph,wolf_active," ..
        "player,player_depth,player_graph,player_active")

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

            local stop_file = io.open(exp_dir .. "STOP-NOW.txt", "r")
            if stop_file then
                stop_file:close()
                stopped = true
                callbacks:remove(callback_id)
                finish("done:P006CAnchor")
                return
            end
            if tick > HORIZON then
                stopped = true
                callbacks:remove(callback_id)
                finish("done:P006CAnchor")
                return
            end

            if not in_ewram(target, OBJECT_BYTES)
                or emu:read32(target) ~= TARGET_DISPATCH then
                target = discover_target()
                epoch = epoch + 1
            end

            local player = emu:read32(PLAYER_SLOT)
            if not in_ewram(player, OBJECT_BYTES) then player = 0 end

            local player_depth, player_graph, player_active = 0, 0, 0
            if player ~= 0 then
                player_depth = emu:read32(player + 0x23C)
                player_graph = emu:read32(player + 0x244)
                player_active = emu:read32(player + 0x268)
            end

            wline(string.format(
                "T,%d,%d,%04x,%08x,%08x,%08x,%08x,%08x,%08x,%08x,%08x",
                tick, epoch, emu:read16(0x03003304), target,
                emu:read32(target + 0x23C), emu:read32(target + 0x244),
                emu:read32(target + 0x268), player, player_depth,
                player_graph, player_active))
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
