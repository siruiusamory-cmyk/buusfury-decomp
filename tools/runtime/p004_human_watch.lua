-- P-004 human session: per-tick diff OUTSIDE sprite zone + HP/pos log.
-- Zone: 0x02033000..0x0203DE50 and 0x0203DFA0..0x0203FF00 (skip sprite
-- work 0x3DE60..0x3DF9F). Player-still frames flagged for analysis.
local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p004-actor-diff.csv"
local HORIZON = 14400

local RANGES = {
    { 0x0203C400, 0x0203DE50 },
}

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
    for _, rg in ipairs(RANGES) do
        for a = rg[1], rg[2] - 4, 4 do
            prev[a] = emu:read32(a)
        end
    end

    local armed = assert(io.open(exp_dir .. "armed-marker.txt", "w"))
    armed:write("armed")
    armed:close()

    local t = 0
    local callback_id
    callback_id = callbacks:add("frame", function()
        t = t + 1
        if t > HORIZON then
            callbacks:remove(callback_id)
            finish("done:HumanWatch")
            return
        end
        local ptr = emu:read32(0x03001C34)
        local px, py = 0, 0
        if ptr ~= 0 then
            px = emu:read32(ptr + 0x1A0)
            py = emu:read32(ptr + 0x1A4)
        end
        local hp = emu:read32(0x0203DC20)
        local mhp = emu:read32(0x0203DBB4)
        local k = emu:read16(0x03003304)

        local parts = {
            string.format("t%d,px%x,py%x,hp%x,mhp%x,k%x",
                t, px, py, hp, mhp, k),
        }
        for _, rg in ipairs(RANGES) do
            for a = rg[1], rg[2] - 4, 4 do
                local v = emu:read32(a)
                if prev[a] ~= v then
                    parts[#parts + 1] =
                        string.format("%x:%x>%x", a, prev[a], v)
                    prev[a] = v
                end
            end
        end
        wline(table.concat(parts, ","))
    end)
end

local ok, err = xpcall(run, function(e) return tostring(e) end)
if not ok then finish("error:" .. tostring(err)) end
