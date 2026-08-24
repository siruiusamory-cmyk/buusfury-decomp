-- P-003: single armed punch, full dump of entity zone per tick.
local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p003-zdump.csv"

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

    assert(emu ~= nil and emu:getGameCode() == "AGB-BG3E")
    emu:setKeys(0)

    local prev = {}
    for i = 0, 0x140 // 4 do
        prev[i] = emu:read32(0x0203DE60 + i * 4)
    end

    local armed = assert(io.open(exp_dir .. "armed-marker.txt", "w"))
    armed:write("armed")
    armed:close()

    local t = 0
    local callback_id
    callback_id = callbacks:add("frame", function()
        t = t + 1
        if t == 12 then
            emu:setKeys(0x001)
            wline("PRESS,t" .. t)
        elseif t >= 14 then
            emu:setKeys(0)
        end
        if t >= 50 then
            callbacks:remove(callback_id)
            emu:setKeys(0)
            finish("done:ZoneDump")
            return
        end
        local parts = { string.format("t%d", t) }
        for i = 0, 0x140 // 4 do
            local v = emu:read32(0x0203DE60 + i * 4)
            if prev[i] ~= v then
                parts[#parts + 1] =
                    string.format("%x:%x>%x", 0xDE60 + i * 4, prev[i], v)
                prev[i] = v
            end
        end
        wline(table.concat(parts, ","))
    end)
end

local ok, err = xpcall(run, function(e) return tostring(e) end)
if not ok then finish("error:" .. tostring(err)) end
