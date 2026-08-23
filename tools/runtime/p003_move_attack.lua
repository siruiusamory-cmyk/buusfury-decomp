-- P-003 move-then-attack probe: walks away from the NPC, then presses the
-- candidate attack button, with screenshot at attack+12.
local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p003-attack-log.csv"

local fname = done_path:match("[^/\\]+$") or done_path
local LEG_NAME = fname
if LEG_NAME:sub(1, 5) == "done-" then LEG_NAME = LEG_NAME:sub(6) end
if LEG_NAME:sub(-4) == ".txt" then LEG_NAME = LEG_NAME:sub(1, -5) end

local WARMUP = 300
local WALK = 28
local GAP = 8
local HOLD = 4
local POST = 44

local BUTTON = (LEG_NAME == "MoveB") and 0x002 or 0x001
local WALK_MASK = 0x010 -- Right

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
    assert(emu ~= nil, "no core")
    assert(emu:getGameCode() == "AGB-BG3E")
    emu:setKeys(0)

    local t = -WARMUP - 1
    local phase = "warmup"
    local prev = {}
    local shot_done = false

    local callback_id
    callback_id = callbacks:add("frame", function()
        t = t + 1
        if t == 0 then phase = "walk"; emu:setKeys(WALK_MASK)
        elseif t == WALK then phase = "gap"; emu:setKeys(0)
        elseif t == WALK + GAP then phase = "press"; emu:setKeys(BUTTON)
        elseif t == WALK + GAP + HOLD then phase = "post"; emu:setKeys(0)
        elseif t == WALK + GAP + HOLD + POST then
            callbacks:remove(callback_id)
            wline(LEG_NAME .. ",end,,,,,,,")
            finish("done:" .. LEG_NAME)
            return
        end

        if phase ~= "warmup" then
            local ptr = emu:read32(0x03001C34)
            local inp = emu:read16(0x03003304)
            local mgr = emu:read32(0x03002A64)
            if ptr == 0 then
                wline(string.format("%s,%d,no-player,%d,,,%s",
                    LEG_NAME, t, inp, phase))
                prev = {}
                return
            end
            local x = emu:read32(ptr + 0x1A0)
            local y = emu:read32(ptr + 0x1A4)
            local f10 = emu:read32(ptr + 0x10)

            if phase == "post" and not shot_done and t >= WALK + GAP + HOLD + 12 then
                shot_done = true
                emu:screenshot(exp_dir .. "p003-" .. LEG_NAME .. ".png")
            end

            local changes = {}
            for i = 0, 0x23C // 4 do
                local v = emu:read32(ptr + i * 4)
                if prev[i] ~= nil and prev[i] ~= v and i * 4 ~= 0x10 then
                    changes[#changes + 1] =
                        string.format("%x:%x>%x", i * 4, prev[i], v)
                end
                prev[i] = v
            end
            wline(string.format("%s,%d,%x,%d,%d,%d,%s,%x|%s",
                LEG_NAME, t, ptr, x, y, mgr, inp,
                f10, table.concat(changes, ";")))
        end
    end)
end

local ok, err = xpcall(run, function(e) return tostring(e) end)
if not ok then
    finish("error:" .. tostring(err))
    console:log("P-003 move-attack error: " .. tostring(err))
end
