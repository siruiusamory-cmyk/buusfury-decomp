-- P-006 per-frame reaction trace. The moving HURT-path target is rediscovered
-- from its observed dispatch word on every load epoch; no EWRAM address is reused.
local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")

local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p006-reaction.csv"
local tick_path = exp_dir .. "frame-tick.txt"
local EWRAM_LO = 0x02000000
local EWRAM_HI = 0x02040000
local TARGET_DISPATCH = 0x0804C484
local PLAYER_ENTITY_SLOT = 0x03001C34
local HP_OFFSET = 0x28C
-- Includes the controller at +0x238 and authoritative signed HP at +0x28C.
local OBJECT_BYTES = 0x2A0
local LINKED_PTR_OFFSET = 0x1D8
local LINKED_BYTES = 0x80
local HORIZON = 18000

local function in_ewram(address, length)
    return address >= EWRAM_LO and address + length <= EWRAM_HI
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

    local function discover_linked(tgt)
        local ptr = emu:read32(tgt + LINKED_PTR_OFFSET)
        if ptr == 0 or not in_ewram(ptr, LINKED_BYTES) then
            return nil
        end
        return ptr
    end

    local function snapshot_linked(addr)
        local snap = {}
        for off = 0, LINKED_BYTES - 4, 4 do
            snap[off] = emu:read32(addr + off)
        end
        return snap
    end

    local target = discover_target()
    local epoch = 1
    local previous = {}
    for offset = 0, OBJECT_BYTES - 4, 4 do
        previous[offset] = emu:read32(target + offset)
    end
    local linked = discover_linked(target)
    local linked_prev = linked and snapshot_linked(linked) or {}
    if linked then
        wline(string.format("EPOCH,%d,target,%08x,dispatch,%08x,linked,%08x",
            epoch, target, TARGET_DISPATCH, linked))
    else
        wline(string.format("EPOCH,%d,target,%08x,dispatch,%08x,linked,none",
            epoch, target, TARGET_DISPATCH))
    end

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
                finish("done:P006Reaction")
                return
            end
            if tick > HORIZON then
                stopped = true
                callbacks:remove(callback_id)
                finish("done:P006Reaction")
                return
            end

            if not in_ewram(target, OBJECT_BYTES) or emu:read32(target) ~= TARGET_DISPATCH then
                target = discover_target()
                epoch = epoch + 1
                previous = {}
                for offset = 0, OBJECT_BYTES - 4, 4 do
                    previous[offset] = emu:read32(target + offset)
                end
                linked = discover_linked(target)
                linked_prev = linked and snapshot_linked(linked) or {}
                if linked then
                    wline(string.format("EPOCH,%d,target,%08x,dispatch,%08x,linked,%08x",
                        epoch, target, TARGET_DISPATCH, linked))
                else
                    wline(string.format("EPOCH,%d,target,%08x,dispatch,%08x,linked,none",
                        epoch, target, TARGET_DISPATCH))
                end
            end

            -- re-discover linked object every frame (it populates late)
            local cur_linked_ptr = discover_linked(target)
            if cur_linked_ptr ~= linked then
                linked = cur_linked_ptr
                linked_prev = linked and snapshot_linked(linked) or {}
                if linked then
                    wline(string.format("LINKED,%d,target,%08x,ptr,%08x",
                        tick, target, linked))
                else
                    wline(string.format("LINKED,%d,target,%08x,ptr,none",
                        tick, target))
                end
            end

            local player = emu:read32(PLAYER_ENTITY_SLOT)
            local px, py = 0, 0
            if in_ewram(player, 0x1A8) then
                px = emu:read32(player + 0x1A0)
                py = emu:read32(player + 0x1A4)
            end

            local changes = {}
            for offset = 0, OBJECT_BYTES - 4, 4 do
                local value = emu:read32(target + offset)
                if value ~= previous[offset] then
                    changes[#changes + 1] = string.format(
                        "%03x:%08x>%08x", offset, previous[offset], value)
                    previous[offset] = value
                end
            end

            local lchanges = {}
            if linked then
                for off = 0, LINKED_BYTES - 4, 4 do
                    local val = emu:read32(linked + off)
                    if val ~= linked_prev[off] then
                        lchanges[#lchanges + 1] = string.format(
                            "%03x:%08x>%08x", off, linked_prev[off], val)
                        linked_prev[off] = val
                    end
                end
            end

            local hp = in_ewram(target + HP_OFFSET, 4)
                and emu:read32(target + HP_OFFSET) or 0
            wline(string.format(
                "T,%d,epoch,%d,keys,%04x,target,%08x,hp,%08x,field04,%08x,wx,%08x,wy,%08x," ..
                "player,%08x,px,%08x,py,%08x,changes,%s,linked_changes,%s",
                tick, epoch, emu:read16(0x03003304), target,
                hp, emu:read32(target + 0x04), emu:read32(target + 0x1A0),
                emu:read32(target + 0x1A4), player, px, py,
                table.concat(changes, ";"),
                table.concat(lchanges, ";")))
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

local ok, err = xpcall(run, function(e) return tostring(e) end)
if not ok then finish("error:" .. tostring(err)) end
