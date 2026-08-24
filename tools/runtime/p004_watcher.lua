-- P-004 armed watcher: state loads with ki blast in flight; per-tick diff
-- of entity zone 0x0203C000..0x02040000 from tick 0; full-EWRAM snapshots.
local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p004-watcher.csv"

local END = 150
local SNAPS = {0, 15, 30, 45, 60, 90, 120}

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

    wline("started,Watcher")
    assert(emu ~= nil and emu:getGameCode() == "AGB-BG3E")
    emu:setKeys(0)

    local t = -1
    local prev = {}
    local next_snap = 1
    local primed = false

    local callback_id
    callback_id = callbacks:add("frame", function()
        t = t + 1
        if t == END then
            callbacks:remove(callback_id)
            wline("end")
            finish("done:Watcher")
            return
        end

        local ptr = emu:read32(0x03001C34)
        local px, py = 0, 0
        if ptr ~= 0 then
            px = emu:read32(ptr + 0x1A0)
            py = emu:read32(ptr + 0x1A4)
        end

        -- prime prev on first executed tick
        if not primed then
            primed = true
            for i = 0, 0x4000 // 4 do
                prev[i] = emu:read32(0x0203C000 + i * 4)
            end
            emu:screenshot(exp_dir .. "p004-watch-t0.png")
            local data = emu:readRange(0x02000000, 0x40000)
            local f0 = assert(io.open(
                exp_dir .. "p004-watch-s0.bin", "wb"))
            f0:write(data)
            f0:close()
            next_snap = 2
            wline(string.format("t%d,primed,px%x,py%x", t, px, py))
            return
        end

        local changes = {}
        local n = 0
        for i = 0, 0x4000 // 4 do
            local v = emu:read32(0x0203C000 + i * 4)
            if prev[i] ~= v then
                if n < 150 then
                    changes[#changes + 1] =
                        string.format("%x:%x>%x", 0x3C000 + i * 4,
                            prev[i], v)
                    n = n + 1
                end
                prev[i] = v
            end
        end

        wline(string.format("t%d,px%x,py%x,hp1%x,hp2%x,mgr%x,%s",
            t, px, py,
            emu:read32(0x0203DBB4), emu:read32(0x0203DC20),
            emu:read32(0x03002A64),
            table.concat(changes, ";")))

        if next_snap <= #SNAPS and t == SNAPS[next_snap] then
            local data = emu:readRange(0x02000000, 0x40000)
            local f = assert(io.open(
                exp_dir .. "p004-watch-s" .. SNAPS[next_snap] .. ".bin", "wb"))
            f:write(data)
            f:close()
            next_snap = next_snap + 1
        end
    end)
end

local ok, err = xpcall(run, function(e) return tostring(e) end)
if not ok then finish("error:" .. tostring(err)) end
