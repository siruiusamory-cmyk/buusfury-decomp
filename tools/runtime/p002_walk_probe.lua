-- P-002 walking displacement probe for mGBA 0.10.5.
-- One condition per launch; initial state comes from --savestate.
-- Samples player position (+0x1A0/+0x1A4 via 0x03001C34) and buffered
-- input halfword (0x03003304) every gameplay frame.
-- Output: CSV log + done marker beneath ignored build/.

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p002-walk-log.csv"

local fname = done_path:match("[^/\\]+$") or done_path
local LEG_NAME = fname
if LEG_NAME:sub(1, 5) == "done-" then LEG_NAME = LEG_NAME:sub(6) end
if LEG_NAME:sub(-4) == ".txt" then LEG_NAME = LEG_NAME:sub(1, -5) end
local WARMUP = 300
local PRE_FRAMES = 6
local HOLD_FRAMES = 8

local function key(name, fallback)
    if C and C.GBA_KEY and C.GBA_KEY[name] ~= nil then
        return C.GBA_KEY[name]
    end
    return fallback
end

local MASKS = {
    D_up_right = 0x050,
    D_up_left = 0x060,
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
    local last_x, last_y = nil, nil
    local hold_applied = false

    local callback_id
    callback_id = callbacks:add("frame", function()
        frame_in_leg = frame_in_leg + 1

        if frame_in_leg == 0 then
            phase = "pre"
        elseif frame_in_leg == PRE_FRAMES then
            phase = "hold"
            emu:setKeys(mask)
            hold_applied = true
        elseif frame_in_leg == PRE_FRAMES + HOLD_FRAMES then
            emu:setKeys(0)
            callbacks:remove(callback_id)
            wline(LEG_NAME .. ",end-of-hold,,,,,,")
            finish("done:" .. LEG_NAME)
            return
        end

        if phase == "pre" or phase == "hold" or phase == "warmup" then
            if phase == "warmup" and frame_in_leg % 60 == 0 then
                wline(LEG_NAME .. "," .. frame_in_leg .. ",warmup-tick")
            end
            if phase == "warmup" then return end
            local ptr = emu:read32(0x03001C34)
            if ptr == 0 then
                wline(LEG_NAME .. "," .. frame_in_leg .. ",no-player")
                return
            end
            local x = emu:read32(ptr + 0x1A0)
            local y = emu:read32(ptr + 0x1A4)
            local dx, dy = 0, 0
            if last_x then
                dx = x - last_x
                dy = y - last_y
            end
            local inp = emu:read16(0x03003304)
            wline(string.format("%s,%d,%d,%d,%d,%d,%d,%s",
                LEG_NAME, frame_in_leg, x, y, dx, dy, inp, phase))
            last_x, last_y = x, y
        end
    end)

    assert(hold_applied ~= nil)
end

local ok, err = xpcall(run, function(e)
    return tostring(e) ..
        "\n" .. (debug and debug.traceback and debug.traceback("", 2) or "")
end)
if not ok then
    finish("error:" .. tostring(err):gsub("[\r\n]+", " "))
    console:log("P-002 probe error: " .. tostring(err))
end


