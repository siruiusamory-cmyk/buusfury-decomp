-- P-004 trace: double punch with per-tick enemy-struct window diff.
local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p004-trace.csv"

local WARMUP = 240

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

    wline("started,Trace2")
    assert(emu ~= nil and emu:getGameCode() == "AGB-BG3E")
    emu:setKeys(0)

    local t = -WARMUP - 1
    local phase = "warmup"
    local prev = {}

    local callback_id
    callback_id = callbacks:add("frame", function()
        t = t + 1
        if t == 0 then phase = "turn"; emu:setKeys(0x020)
        elseif t == 4 then phase = "gap"; emu:setKeys(0)
        elseif t == 8 then phase = "punch1"; emu:setKeys(0x001)
        elseif t == 12 then phase = "wait"; emu:setKeys(0)
        elseif t == 30 then phase = "punch2"; emu:setKeys(0x001)
        elseif t == 34 then phase = "post"; emu:setKeys(0)
        elseif t == 70 then
            callbacks:remove(callback_id)
            wline("end")
            finish("done:Trace2")
            return
        end

        if phase ~= "warmup" then
            local ptr = emu:read32(0x03001C34)
            local inp = emu:read16(0x03003304)
            local hp1 = emu:read32(0x0203DBB4)
            local hp2 = emu:read32(0x0203DC20)
            local changes = {}
            for i = 0, 0x140 // 4 do
                local off = 0x3DB40 + i * 4
                local v = emu:read32(0x02000000 + off)
                if prev[off] ~= nil and prev[off] ~= v then
                    changes[#changes + 1] =
                        string.format("%x:%x>%x", off, prev[off], v)
                end
                prev[off] = v
            end
            wline(string.format("t%d,inp%d,hp%d:%d,%s", t, inp,
                hp1, hp2, table.concat(changes, ";")))
        end
    end)
end

local ok, err = xpcall(run, function(e) return tostring(e) end)
if not ok then finish("error:" .. tostring(err)) end
