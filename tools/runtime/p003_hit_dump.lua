-- P-003/P-004 combat hit probe: before/after EWRAM dumps + per-tick trace.
local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")

local fname = done_path:match("[^/\\]+$") or done_path
local LEG_NAME = fname
if LEG_NAME:sub(1, 5) == "done-" then LEG_NAME = LEG_NAME:sub(6) end
if LEG_NAME:sub(-4) == ".txt" then LEG_NAME = LEG_NAME:sub(1, -5) end

local log_path = exp_dir .. "p003-hit-" .. LEG_NAME .. ".csv"

local WARMUP = 240
local DUMP_BEFORE = 6
local PRESS_AT = 8
local RELEASE_AT = 12
local DUMP_AFTER = 50
local END_AT = 56
local DOUBLE = LEG_NAME == 'DoubleA'

local function finish(status)
    local d = io.open(done_path, "w")
    if d then d:write(status) d:close() end
end

local function boot(status)
    local d = io.open(exp_dir .. "p003-boot.txt", "a")
    if d then d:write(status .. "\n") d:close() end
end

local function dump(name)
    local data = emu:readRange(0x02000000, 0x40000)
    local f = assert(io.open(exp_dir .. name, "wb"))
    f:write(data)
    f:close()
end

local function run()
    boot("run-enter " .. LEG_NAME)
    local function wline(s)
        local lg = assert(io.open(log_path, "a"))
        lg:write(s .. "\n")
        lg:close()
    end

    wline("started," .. LEG_NAME)
    assert(emu ~= nil and emu:getGameCode() == "AGB-BG3E")
    emu:setKeys(0)

    local t = -WARMUP - 1
    local phase = "warmup"
    local dumped_before = false
    local dumped_after = false

    local callback_id
    callback_id = callbacks:add("frame", function()
        t = t + 1
        if t == 0 then
            phase = "live"
            if LEG_NAME == "MissA" then emu:setKeys(0x020) end
        elseif t == 4 and LEG_NAME == "MissA" then
            emu:setKeys(0)
        elseif t == PRESS_AT and LEG_NAME ~= "Ctrl" then
            emu:setKeys(0x001)
        elseif t == 30 and LEG_NAME == 'DoubleA' then
            emu:setKeys(0x001)
        elseif t == 34 and LEG_NAME == 'DoubleA' then
            emu:setKeys(0)
        elseif t == RELEASE_AT then
            emu:setKeys(0)
        elseif t == END_AT then
            callbacks:remove(callback_id)
            wline(LEG_NAME .. ",end")
            finish("done:" .. LEG_NAME)
            return
        end

        if phase == "live" then
            if t == DUMP_BEFORE and not dumped_before then
                dumped_before = true
                dump("p003-" .. LEG_NAME .. "-before.bin")
            end
            if t == DUMP_AFTER and not dumped_after then
                dumped_after = true
                dump("p003-" .. LEG_NAME .. "-after.bin")
            end

            local ptr = emu:read32(0x03001C34)
            local inp = emu:read16(0x03003304)
            local mgr = emu:read32(0x03002A64)
            if ptr == 0 then
                wline(string.format("%s,%d,no-player,%d,%d",
                    LEG_NAME, t, inp, mgr))
                return
            end
            local x = emu:read32(ptr + 0x1A0)
            local hp1 = emu:read32(0x0203CE4C)
            local hp2 = emu:read32(0x0203CE54)
            local hp3 = emu:read32(0x0203CF64)
            local y = emu:read32(ptr + 0x1A4)
            wline(string.format("%s,%d,%x,%d,%d,%d,%d,%x,%x,%x", LEG_NAME, t,
                ptr, x, y, mgr, inp, hp1, hp2, hp3))
            if t == 4 or t == 20 or t == 45 then
                emu:screenshot(exp_dir .. "p003-" .. LEG_NAME .. "-t" .. t .. ".png")
            end
        end
    end)
end

local ok, err = xpcall(run, function(e) return tostring(e) end)
boot("run-exit ok=" .. tostring(ok) .. " err=" .. tostring(err))
if not ok then finish("error:" .. tostring(err)) end



