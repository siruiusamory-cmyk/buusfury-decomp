-- P-003 armed punch: launched under --gdb halt; primes while paused;
-- presses A at first frames after GDB continue; per-tick zone diff.
local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p003-armed.csv"

local RELEASE_AT = 4
local END = 120

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

    -- prime the diff baseline while the core is halted
    local prev = {}
    for i = 0, 0x4000 // 4 do
        prev[i] = emu:read32(0x0203C000 + i * 4)
    end

    local armed = assert(io.open(exp_dir .. "armed-marker.txt", "w"))
    armed:write("armed")
    armed:close()
    wline("armed")

    local t = 0
    local pressed = false
    local callback_id
    callback_id = callbacks:add("frame", function()
        t = t + 1
        if not pressed and t >= 2 then
            pressed = true
            emu:setKeys(0x001)
            wline("PRESS,t" .. t)
        end
        if t == RELEASE_AT then
            emu:setKeys(0)
        end
        if t == END then
            callbacks:remove(callback_id)
            emu:setKeys(0)
            wline("end")
            finish("done:ArmedPunch")
            return
        end

        local ptr = emu:read32(0x03001C34)
        local px, py = 0, 0
        if ptr ~= 0 then
            px = emu:read32(ptr + 0x1A0)
            py = emu:read32(ptr + 0x1A4)
        end

        local changes = {}
        local n = 0
        for i = 0, 0x4000 // 4 do
            local v = emu:read32(0x0203C000 + i * 4)
            if prev[i] ~= v then
                if n < 120 then
                    changes[#changes + 1] =
                        string.format("%x:%x>%x", 0x3C000 + i * 4, prev[i], v)
                    n = n + 1
                end
                prev[i] = v
            end
        end

        if t <= 30 or t % 10 == 0 or n > 20 then
            wline(string.format(
                "t%d,px%x,py%x,e1%x,e2%x,p1%x,p2%x,walk%x,%s",
                t, px, py,
                emu:read32(0x0203DE7C), emu:read32(0x0203DEE4),
                emu:read32(0x0203DBB4), emu:read32(0x0203DC20),
                emu:read32(0x0203DF88),
                table.concat(changes, ";")))
        end
    end)
end

local ok, err = xpcall(run, function(e) return tostring(e) end)
if not ok then finish("error:" .. tostring(err)) end
