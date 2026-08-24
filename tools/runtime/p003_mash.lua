-- P-003 mash-A contact discovery: let enemy approach, tap A repeatedly,
-- log everything needed to isolate the first accepted press.
local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p003-mash.csv"

local WARMUP = 20      -- let the ki impact (t~8) pass
local MASH_START = 20
local PRESS = 2
local GAP = 10
local END = 220

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

    wline("started,Mash")
    assert(emu ~= nil and emu:getGameCode() == "AGB-BG3E")
    emu:setKeys(0)

    local t = -1
    local prev = {}
    local primed = false
    local press_index = 0
    local press_tick = -1

    local callback_id
    callback_id = callbacks:add("frame", function()
        t = t + 1
        if t == END then
            callbacks:remove(callback_id)
            wline("end")
            finish("done:Mash")
            return
        end

        if t >= MASH_START then
            local m = (t - MASH_START) % (PRESS + GAP)
            if m < PRESS then
                if m == 0 then
                    press_index = press_index + 1
                    press_tick = t
                    wline(string.format("PRESS,%d,%d", press_index, t))
                end
                emu:setKeys(0x001)
            else
                emu:setKeys(0)
            end
        end

        local ptr = emu:read32(0x03001C34)
        local px, py = 0, 0
        if ptr ~= 0 then
            px = emu:read32(ptr + 0x1A0)
            py = emu:read32(ptr + 0x1A4)
        end

        local changes = {}
        local n = 0
        if primed then
            for i = 0, 0x4000 // 4 do
                local v = emu:read32(0x0203C000 + i * 4)
                if prev[i] ~= v then
                    if n < 120 then
                        changes[#changes + 1] =
                            string.format("%x:%x>%x", 0x3C000 + i * 4,
                                prev[i], v)
                        n = n + 1
                    end
                    prev[i] = v
                end
            end
        else
            primed = true
            for i = 0, 0x4000 // 4 do
                prev[i] = emu:read32(0x0203C000 + i * 4)
            end
        end

        wline(string.format(
            "t%d,px%x,py%x,e1%x,e2%x,p1%x,p2%x,walk%x,pi%d,%s",
            t, px, py,
            emu:read32(0x0203DE7C), emu:read32(0x0203DEE4),
            emu:read32(0x0203DBB4), emu:read32(0x0203DC20),
            emu:read32(0x0203DF88),
            press_index,
            table.concat(changes, ";")))
    end)
end

local ok, err = xpcall(run, function(e) return tostring(e) end)
if not ok then finish("error:" .. tostring(err)) end
