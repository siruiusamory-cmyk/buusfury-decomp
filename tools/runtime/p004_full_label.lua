-- P-003 FULL-memory labeled punches: EWRAM+IWRAM diff around each punch.
local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p004-full-label.csv"
local HORIZON = 10800
local COALESCE = 25

local RANGES = {
    { 0x02000000, 0x02040000 },
    { 0x03000000, 0x03008000 },
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

    local armed = assert(io.open(exp_dir .. "armed-marker.txt", "w"))
    armed:write("armed")
    armed:close()

    local ref = {}
    local seeded = false
    local t, pid, preva, lastedge = 0, 0, 0, -1000
    local pending = nil

    callbacks:add("frame", function()
        t = t + 1
        local stopf = io.open(exp_dir .. "STOP-NOW.txt", "r")
        if stopf then
            stopf:close()
            finish("done:FullLabel")
            return
        end
        if t > HORIZON then finish("done:FullLabel") return end
        if not seeded then
            for _, rg in ipairs(RANGES) do
                for a = rg[1], rg[2] - 4, 4 do ref[a] = emu:read32(a) end
            end
            seeded = true
            wline("seeded")
            return
        end

        local k = emu:read16(0x03003304)
        if (k & 1) == 1 and (preva & 1) == 0 and (t - lastedge) > COALESCE then
            pid = pid + 1
            lastedge = t
            pending = { pid = pid, abs = { t + 1, t + 9, t + 17 } }
            local ptr = emu:read32(0x03001C34)
            local px, py = 0, 0
            if ptr ~= 0 then
                px = emu:read32(ptr + 0x1A0)
                py = emu:read32(ptr + 0x1A4)
            end
            wline(string.format("PUNCH,%d,%d,px%x,py%x", pid, t, px, py))
        end
        preva = k

        if pending then
            while #pending.abs > 0 and t >= pending.abs[1] do
                table.remove(pending.abs, 1)
                local parts = {}
                for _, rg in ipairs(RANGES) do
                    for a = rg[1], rg[2] - 4, 4 do
                        local v = emu:read32(a)
                        if ref[a] ~= v then
                            parts[#parts + 1] =
                                string.format("%x:%x>%x", a, ref[a], v)
                            ref[a] = v
                        end
                    end
                end
                wline(string.format("DUMP,%d,%d,%s",
                    pending.pid, t, table.concat(parts, ",")))
            end
            if #pending.abs == 0 then pending = nil end
        end
    end)
end

local ok, err = xpcall(run, function(e) return tostring(e) end)
if not ok then finish("error:" .. tostring(err)) end
