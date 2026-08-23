-- P-003 punch timing probe: tap vs held A, with OAM differential.
local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p003-punch-log.csv"

local fname = done_path:match("[^/\\]+$") or done_path
local LEG_NAME = fname
if LEG_NAME:sub(1, 5) == "done-" then LEG_NAME = LEG_NAME:sub(6) end
if LEG_NAME:sub(-4) == ".txt" then LEG_NAME = LEG_NAME:sub(1, -5) end

local WARMUP = 300
local WALK = 28
local GAP = 8
local HOLD = (LEG_NAME == "HoldA") and 14 or ((LEG_NAME == "TapA") and 2 or 0)
local POST = 56

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

    wline("started," .. LEG_NAME)
    assert(emu ~= nil and emu:getGameCode() == "AGB-BG3E")
    emu:setKeys(0)

    local t = -WARMUP - 1
    local phase = "warmup"
    local prevO = {}

    local callback_id
    callback_id = callbacks:add("frame", function()
        t = t + 1
        if t == 0 then phase = "walk"; emu:setKeys(0x010)
        elseif t == WALK then phase = "gap"; emu:setKeys(0)
        elseif t == WALK + GAP then phase = "press"; emu:setKeys(0x001)
        elseif t == WALK + GAP + HOLD then phase = "post"; emu:setKeys(0)
        elseif t == WALK + GAP + HOLD + POST then
            callbacks:remove(callback_id)
            wline(LEG_NAME .. ",end")
            finish("done:" .. LEG_NAME)
            return
        end

        if phase ~= "warmup" and phase ~= "walk" then
            local inp = emu:read16(0x03003304)
            local changes = {}
            for i = 0, 15 do
                local v = emu:read32(0x07000000 + i * 4)
                if prevO[i] ~= nil and prevO[i] ~= v then
                    changes[#changes + 1] =
                        string.format("o%x:%x>%x", i * 4, prevO[i], v)
                end
                prevO[i] = v
            end
            local ptr = emu:read32(0x03001C34)
            local f10 = ptr ~= 0 and emu:read32(ptr + 0x10) or 0
            wline(string.format("%s,%d,%d,%x,%s", LEG_NAME, t, inp, f10,
                table.concat(changes, ";")))
        end
    end)
end

local ok, err = xpcall(run, function(e) return tostring(e) end)
if not ok then finish("error:" .. tostring(err)) end
