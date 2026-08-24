-- P-003 armed single-punch (or control): prime while GDB-halted.
-- Env via marker name: PUNCH=1 -> one A press at t=12; PUNCH=0 -> no input.
local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p003-one-log.csv"
local punch = string.find(done_path, "Punch", 1, true) ~= nil

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

    local armed = assert(io.open(exp_dir .. "armed-marker.txt", "w"))
    armed:write("armed")
    armed:close()
    wline("armed,punch=" .. tostring(punch))

    local t = 0
    local callback_id
    callback_id = callbacks:add("frame", function()
        t = t + 1
        if punch and t == 12 then
            wline("PRESS,1," .. t)
            emu:setKeys(0x001)
        elseif punch and t >= 14 then
            emu:setKeys(0)
        end
        if t >= 60 then
            callbacks:remove(callback_id)
            emu:setKeys(0)
            wline("end")
            finish("done:ArmedOne")
            return
        end
        local ptr = emu:read32(0x03001C34)
        local px, py = 0, 0
        if ptr ~= 0 then
            px = emu:read32(ptr + 0x1A0)
            py = emu:read32(ptr + 0x1A4)
        end
        wline(string.format(
            "t%d,px%x,py%x,e1%x,e2%x,p1%x,p2%x",
            t, px, py,
            emu:read32(0x0203DE7C), emu:read32(0x0203DEE4),
            emu:read32(0x0203DBB4), emu:read32(0x0203DC20)))
    end)
end

local ok, err = xpcall(run, function(e) return tostring(e) end)
if not ok then finish("error:" .. tostring(err)) end
