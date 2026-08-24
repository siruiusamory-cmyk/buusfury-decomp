-- P-004 wander probe: no input; three EWRAM snapshots to locate the
-- enemy's moving position words; HP-candidate drift tracked per tick.
local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p004-wander.csv"

local WARMUP = 240
local SNAP = {60, 160, 260, 360}
local END = 380

local function finish(status)
    local d = io.open(done_path, "w")
    if d then d:write(status) d:close() end
end

local function run()
    local function wline(s)
        local lg = assert(io.open(log_path, "a"))
        lg:write(s .. "\n")
        lg:close()
    end

    wline("started,Wander")
    assert(emu ~= nil and emu:getGameCode() == "AGB-BG3E")
    emu:setKeys(0)

    local t = -WARMUP - 1
    local snaps = {}
    local next_snap = 1

    local callback_id
    callback_id = callbacks:add("frame", function()
        t = t + 1
        if t == END then
            callbacks:remove(callback_id)
            wline("end")
            finish("done:Wander")
            return
        end

        if t >= 0 and t % 10 == 0 then
            local ptr = emu:read32(0x03001C34)
            local px, py = 0, 0
            if ptr ~= 0 then
                px = emu:read32(ptr + 0x1A0)
                py = emu:read32(ptr + 0x1A4)
            end
            wline(string.format("t%d,px%x,py%x,hp1%x,hp2%x", t, px, py,
                emu:read32(0x0203DBB4), emu:read32(0x0203DC20)))
        end

        if t >= 0 and next_snap <= #SNAP and t == SNAP[next_snap] then
            local data = emu:readRange(0x02030000, 0x10000)
            local f = assert(io.open(
                exp_dir .. "p004-wander-s" .. next_snap .. ".bin", "wb"))
            f:write(data)
            f:close()
            snaps[next_snap] = true
            next_snap = next_snap + 1
        end
    end)
end

local ok, err = xpcall(run, function(e) return tostring(e) end)
if not ok then finish("error:" .. tostring(err)) end
