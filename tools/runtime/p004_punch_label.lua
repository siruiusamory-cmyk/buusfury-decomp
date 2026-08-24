-- P-003 human-labeled punches: number A rising edges, log zone diff.
local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p004-punch-label.csv"
local HORIZON = 10800
local ZLO, ZHI = 0x0203C400, 0x0203DE50

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
    local prev = {}
    for a = ZLO, ZHI - 4, 4 do prev[a] = emu:read32(a) end

    local armed = assert(io.open(exp_dir .. "armed-marker.txt", "w"))
    armed:write("armed")
    armed:close()

    local t, pid, preva = 0, 0, 0
    callbacks:add("frame", function()
        t = t + 1
        if t > HORIZON then finish("done:PunchLabel") return end
        local ptr = emu:read32(0x03001C34)
        local px, py = 0, 0
        if ptr ~= 0 then
            px = emu:read32(ptr + 0x1A0)
            py = emu:read32(ptr + 0x1A4)
        end
        local k = emu:read16(0x03003304)
        if (k & 1) == 1 and (preva & 1) == 0 then
            pid = pid + 1
            wline(string.format("PUNCH,%d,%d,px%x,py%x", pid, t, px, py))
        end
        preva = k
        local parts = { string.format("t%d,px%x,py%x,k%x,e248%x,e24c%x,e29c%x",
            t, px, py, k,
            emu:read32(0x0203D248), emu:read32(0x0203D24C),
            emu:read32(0x0203D29C)) }
        for a = ZLO, ZHI - 4, 4 do
            local v = emu:read32(a)
            if prev[a] ~= v then
                parts[#parts + 1] = string.format("%x:%x>%x", a, prev[a], v)
                prev[a] = v
            end
        end
        wline(table.concat(parts, ","))
    end)
end

local ok, err = xpcall(run, function(e) return tostring(e) end)
if not ok then finish("error:" .. tostring(err)) end
