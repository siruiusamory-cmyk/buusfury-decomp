-- P-003 attack scout for mGBA 0.10.5.
-- One condition per launch (--savestate provides clean start).
-- Samples buffered input, player position, spatial-registry count, and a
-- per-tick DIFFERENTIAL of player entity words +0x000..+0x23C so that
-- attack-specific state changes pop out against the no-input control.
-- Output: append-only CSV under ignored build/.

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p003-attack-log.csv"

local fname = done_path:match("[^/\\]+$") or done_path
local LEG_NAME = fname
if LEG_NAME:sub(1, 5) == "done-" then LEG_NAME = LEG_NAME:sub(6) end
if LEG_NAME:sub(-4) == ".txt" then LEG_NAME = LEG_NAME:sub(1, -5) end

local WARMUP = 300
local PRE_FRAMES = 8
local HOLD_FRAMES = 4
local POST_FRAMES = 36

local MASKS = {
    Scout_none = 0x000,
    Scout_A = 0x001,
    Scout_B = 0x002,
    Scout_start = 0x008,
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

    wline("started," .. LEG_NAME)
    assert(emu ~= nil, "mGBA did not attach the emulation core")
    assert(emu:getGameCode() == "AGB-BG3E",
        "game code: " .. tostring(emu:getGameCode()))

    local mask = MASKS[LEG_NAME]
    assert(mask, "unknown leg " .. LEG_NAME)
    emu:setKeys(0)

    local frame_in_leg = -WARMUP - 1
    local phase = "warmup"
    local prev = {}

    local callback_id
    callback_id = callbacks:add("frame", function()
        frame_in_leg = frame_in_leg + 1

        if frame_in_leg == 0 then
            phase = "pre"
        elseif frame_in_leg == PRE_FRAMES then
            phase = "press"
            emu:setKeys(mask)
        elseif frame_in_leg == PRE_FRAMES + HOLD_FRAMES then
            phase = "post"
            emu:setKeys(0)
        elseif frame_in_leg == PRE_FRAMES + HOLD_FRAMES + POST_FRAMES then
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
                    LEG_NAME, frame_in_leg, inp, phase))
                prev = {}
                return
            end
            local x = emu:read32(ptr + 0x1A0)
            local y = emu:read32(ptr + 0x1A4)
            local f10 = emu:read32(ptr + 0x10)

            if frame_in_leg == PRE_FRAMES + HOLD_FRAMES + 12 then
                emu:screenshot(exp_dir .. "p003-" .. LEG_NAME .. ".png")
            end

            -- differential over entity words 0x000..0x23C
            local changes = {}
            for i = 0, 0x23C // 4 do
                local v = emu:read32(ptr + i * 4)
                if prev[i] ~= nil and prev[i] ~= v then
                    if i * 4 ~= 0x10 then
                        changes[#changes + 1] =
                            string.format("%x:%x>%x", i * 4, prev[i], v)
                    end
                end
                prev[i] = v
            end
            wline(string.format("%s,%d,%x,%d,%d,%d,%s,%x|%s",
                LEG_NAME, frame_in_leg, ptr, x, y, mgr, inp,
                f10, table.concat(changes, ";")))
        end
    end)
end

local ok, err = xpcall(run, function(e)
    return tostring(e)
end)
if not ok then
    finish("error:" .. tostring(err):gsub("[\r\n]+", " "))
    console:log("P-003 scout error: " .. tostring(err))
end
