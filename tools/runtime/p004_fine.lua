-- P-003: per-tick fine capture of wolf controller neighborhood.
local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p004-fine.csv"
local HORIZON = 10800
local LO, HI = 0x0203C700, 0x0203CB00

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
    for a = LO, HI - 4, 4 do prev[a] = emu:read32(a) end

    local armed = assert(io.open(exp_dir .. "armed-marker.txt", "w"))
    armed:write("armed")
    armed:close()

    local t, pid, preva = 0, 0, 0
    callbacks:add("frame", function()
        t = t + 1
        local stopf = io.open(exp_dir .. "STOP-NOW.txt", "r")
        if stopf then stopf:close() finish("done:Fine") return end
        if t > HORIZON then finish("done:Fine") return end
        local k = emu:read16(0x03003304)
        if (k & 1) == 1 and (preva & 1) == 0 then
            pid = pid + 1
            wline("PUNCH," .. pid .. "," .. t)
        end
        preva = k
        local parts = { string.format("t%d,k%x", t, k) }
        for a = LO, HI - 4, 4 do
            local v = emu:read32(a)
            if prev[a] ~= v then
                parts[#parts + 1] =
                    string.format("%x:%x>%x", a, prev[a], v)
                prev[a] = v
            end
        end
        wline(table.concat(parts, ","))
    end)
end

local ok, err = xpcall(run, function(e) return tostring(e) end)
if not ok then finish("error:" .. tostring(err)) end
