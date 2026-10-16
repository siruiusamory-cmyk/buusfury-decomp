-- RUNTIME-CONSUMER-001: ROM READ watchpoint recorder for mGBA 0.11 (Lua).
--
-- Read-only with respect to the emulated machine: this file arms read watchpoints
-- and writes files. It writes no emulated memory and presses no keys, so the
-- read-only observer guarantee in docs/skills/mgba-runtime.md section 7 holds.
--
-- CHANNELS, kept separate so a silence is attributable (mgba-runtime.md section 8):
--   TARGET   every read inside an armed row -> (pc, address, width, accessType)
--   LIVENESS frame ticks, written to the run directory's frame-tick.txt, and a
--            counter file; a silent target with a silent liveness proves nothing.
--
-- Inputs (environment, so one file serves every probe):
--   RT001_OUT   directory for these outputs (default: the run directory)
--   RT001_LIST  file of "<start hex> <end hex> <bytes>" rows to watch
--   RT001_CSV   CSV path (default <RT001_OUT>rt001-hits.csv)
--   RT001_CAP   stop after this many distinct (pc,address) pairs (default 20000)
--   RT001_INPUT file of "<frame> <keys>" lines, OPTIONAL. <keys> is "0" or a
--               "+"-joined list of GBA key names (A, B, SELECT, START, RIGHT,
--               LEFT, UP, DOWN, R, L). Keys go through emu:addKey and
--               emu:clearKey, which take a GBA_KEY INDEX: mgba master
--               src/core/scripting.c binds addKey(_, S32, key) and
--               _mScriptCoreAddKey does core->addKeys(core, 1 << key). Input is
--               not an emulated memory write, so the read-only guarantee in
--               docs/skills/mgba-runtime.md section 7 still holds; with
--               RT001_INPUT unset this probe presses no key at all.

local marker_path = rom011_marker_path
assert(marker_path and #marker_path > 0, "marker path not provided")
local exp_dir = marker_path:gsub("[^/\\]+$", "")

local out_dir   = os.getenv("RT001_OUT") or exp_dir
local csv_path  = os.getenv("RT001_CSV") or (out_dir .. "rt001-hits.csv")
local list_path = os.getenv("RT001_LIST") or (out_dir .. "rt001-rows.txt")
local api_path  = out_dir .. "rt001-api.txt"
local live_path = out_dir .. "rt001-liveness.txt"
local keys_path = out_dir .. "rt001-info-keys.txt"
local tick_path = exp_dir .. "frame-tick.txt"
local cap       = tonumber(os.getenv("RT001_CAP") or "") or 20000

local function w(path, text, mode)
    local f = io.open(path, mode or "w")
    if f then f:write(text) f:close() end
end

local log = {
    "emu=" .. tostring(emu ~= nil),
    "setWatchpoint=" .. tostring(emu and emu.setWatchpoint ~= nil),
    "setRangeWatchpoint=" .. tostring(emu and emu.setRangeWatchpoint ~= nil),
    "setBreakpoint=" .. tostring(emu and emu.setBreakpoint ~= nil),
    "clearBreakpoint=" .. tostring(emu and emu.clearBreakpoint ~= nil),
    "romSize=" .. tostring(emu and emu:romSize()),
    "gameCode=" .. tostring(emu and emu:getGameCode()),
    "marker=" .. marker_path,
    "list=" .. list_path,
    "cap=" .. tostring(cap),
}
w(api_path, table.concat(log, "\n") .. "\n")

local arm_enabled = (os.getenv("RT001_ARM") or "1") ~= "0"
if arm_enabled then
    assert(emu and emu.setRangeWatchpoint and emu.setWatchpoint,
        "this mGBA build has no Lua watchpoint API; refusing to run a channel that cannot see reads")
end

local rows = {}
for line in io.lines(list_path) do
    local a, b, n = line:match("^%s*(%x+)%s+(%x+)%s*(%d*)")
    if a and b then
        rows[#rows + 1] = { start = tonumber(a, 16), stop = tonumber(b, 16), bytes = tonumber(n or "0") or 0 }
    end
end
assert(#rows > 0, "no rows in " .. list_path)

local input_path = os.getenv("RT001_INPUT")
local schedule = {}
if input_path and #input_path > 0 then
    for line in io.lines(input_path) do
        local at, spec = line:match("^%s*(%d+)%s+(%S+)")
        if at then schedule[tonumber(at)] = spec end
    end
    assert(C and C.GBA_KEY, "RT001_INPUT was given but this build exposes no C.GBA_KEY")
end
local KEY_NAMES = { "A", "B", "SELECT", "START", "RIGHT", "LEFT", "UP", "DOWN", "R", "L" }
local function apply_keys(spec)
    local want = {}
    if spec ~= "0" then
        for name in spec:gmatch("[^+]+") do want[name] = true end
    end
    for _, name in ipairs(KEY_NAMES) do
        local index = C.GBA_KEY[name]
        if index then
            if want[name] then emu:addKey(index) else emu:clearKey(index) end
        end
    end
end
local scheduled = 0
for _ in pairs(schedule) do scheduled = scheduled + 1 end

local csv = assert(io.open(csv_path, "w"))
csv:write("pc,address,width,access,frame,row_start\n")
csv:flush()

local hits, frames, armed, capped = 0, 0, 0, false
local dirty = false
local seen, ids = {}, {}

local function disarm()
    for _, id in ipairs(ids) do
        if id then pcall(function() emu:clearBreakpoint(id) end) end
    end
end

local function record(pc, address, width, access, row_start)
    local key = string.format("%08X:%08X", pc, address)
    if seen[key] then return end
    seen[key] = true
    hits = hits + 1
    csv:write(string.format("%08X,%08X,%d,%s,%d,%08X\n",
        pc, address, width or 0, tostring(access), frames, row_start))
    dirty = true
    if hits % 20 == 0 then csv:flush() end
    if hits >= cap and not capped then
        capped = true
        disarm()
        csv:flush()
        w(live_path, string.format("CAP-REACHED frames=%d hits=%d armed=%d\n", frames, hits, armed))
    end
end

local function on_read(info)
    local pc = tonumber(emu:readRegister("pc")) or 0
    local address = tonumber(info and info.address) or 0
    local width = tonumber(info and info.width) or 0
    local access = info and info.accessType
    if hits == 0 then
        local keys = {}
        for k, v in pairs(info or {}) do keys[#keys + 1] = tostring(k) .. "=" .. tostring(v) end
        w(keys_path, table.concat(keys, ",") .. "\n")
    end
    local row = 0
    for _, r in ipairs(rows) do
        if address >= r.start and address < r.stop then row = r.start break end
    end
    record(pc, address, width, access, row)
end

for _, r in ipairs(rows) do
    local ok, id = pcall(function() return emu:setRangeWatchpoint(on_read, r.start, r.stop, 2, -1) end)
    if ok and id and id >= 0 then
        ids[#ids + 1] = id
        armed = armed + 1
    else
        w(api_path, string.format("arm FAILED 0x%08X..0x%08X -> %s\n", r.start, r.stop, tostring(id)), "a")
    end
end

w(live_path, string.format("READY armed=%d rows=%d cap=%d input=%d\n", armed, #rows, cap, scheduled))

callbacks:add("frame", function()
    frames = frames + 1
    local spec = schedule[frames]
    if spec then apply_keys(spec) end
    if dirty then csv:flush() dirty = false end
    if frames % 10 == 0 then w(tick_path, tostring(frames)) end
    if frames % 300 == 0 then
        w(live_path, string.format("frames=%d hits=%d armed=%d\n", frames, hits, armed))
    end
    if frames == 600 or frames == 3600 then
        pcall(function() emu:screenshot(out_dir .. "rt001-shot-" .. tostring(frames) .. ".png") end)
    end
end)
