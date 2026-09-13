-- ROM-EXPAND-001: record the retail compressed-dialogue consumer loading the
-- selector-1 table entry from an expanded generated image. This observer never
-- writes emulated memory or input.

local CONSUMER = 0x08012240
local LIVE = 0x08004038
local TABLE = 0x087B5B64
local TARGET_HANDLE = 0x02002641
local TARGET_POINTER = 0x08800000

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = os.getenv("ROM_EXPAND_001_OUT") or (exp_dir .. "rom-expand-001.csv")

assert(emu and emu.setBreakpoint and emu.clearBreakpoint,
    "requires mGBA 0.11 scripted breakpoints")
local code = emu:getGameCode()
assert(code == "BG3E" or code == "AGB-BG3E", "unexpected game code: " .. tostring(code))
assert(emu:romSize() == 16777216, "expected 16 MiB generated ROM")

local file = assert(io.open(log_path, "w"), "cannot open observer output")
file:write("kind,pc,handle,selector,table_entry,note\n")
file:flush()
local frames = 0
local screenshots = {}

local function hex(v)
    return v and string.format("0x%08X", v) or ""
end

local function row(kind, pc, handle, selector, pointer, note)
    file:write(string.format("%s,%s,%s,%s,%s,%s\n", kind, hex(pc), hex(handle),
        selector and tostring(selector) or "", hex(pointer), note))
    file:flush()
end

-- The target breakpoint is immediately before the packed-handle load. r5 is
-- the ROM-resident dialog record; reading r5+4 mirrors the consumer's next
-- instruction and keeps the raw handle distinct from decoded fields.
local hits = 0
emu:setBreakpoint(function(info)
    local r5 = tonumber(emu:readRegister("r5"))
    local handle = r5 and emu:read32(r5 + 4) or nil
    local selector = handle and (handle % 64) or nil
    local pointer = selector and emu:read32(TABLE + selector * 4) or nil
    hits = hits + 1
    local note = (handle == TARGET_HANDLE and selector == 1 and pointer == TARGET_POINTER)
        and "target expanded selector consumed" or "other compressed-dialogue handle"
    row("CONSUMER", CONSUMER, handle, selector, pointer, note)
    if note == "target expanded selector consumed" then
        -- The consumer runs before the render update. Capture several frames
        -- later, after the normal dialogue path has presented the line.
        screenshots[#screenshots + 1] = { frame = frames + 8, hit = hits }
    end
end, CONSUMER)

-- A liveness channel distinguishes an unobserved consumer from a dead probe.
local live = 0
emu:setBreakpoint(function(info)
    live = live + 1
    if live == 1 then row("LIVENESS", LIVE, nil, nil, nil, "shared interpreter reached") end
end, LIVE)

callbacks:add("frame", function()
    frames = frames + 1
    for _, shot in ipairs(screenshots) do
        if frames == shot.frame then
            local path = exp_dir .. "rom-expand-001-dialogue-" .. tostring(shot.hit) .. ".png"
            emu:screenshot(path)
            row("SCREENSHOT", nil, nil, nil, nil, path)
        end
    end
end)

row("ARMED", nil, nil, nil, emu:read32(TABLE + 4), "selector 1 pointer at arm time")
local marker = assert(io.open(done_path, "w"), "cannot open marker")
marker:write("armed\n")
marker:close()
print([[ROM-EXPAND-001 observer armed]])
