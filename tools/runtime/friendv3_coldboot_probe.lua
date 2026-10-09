-- FRIEND-V3-COLD-BOOT-ACCEPTANCE-001: the cold-boot acceptance instrument.
--
-- WHY THIS EXISTS. Every earlier Kibito comparison loaded a savestate, and that
-- state's EWRAM carried decoded dialogue captured on an older build, so each of those
-- comparisons read the image under test beside restored RAM. This instrument is for a
-- launch with NO savestate: the game boots from the battery save, builds its own
-- dialogue cache, and the question is answered directly - does the text the engine
-- copies come from THIS image?
--
-- READ-ONLY. It reads registers and memory, arms one breakpoint as a liveness channel,
-- and writes host files inside the run directory. It never touches input and never
-- writes emulated memory. The operator drives. (docs/skills/mgba-runtime.md 7 and 8.)
--
-- WHAT IT WRITES
--   coldboot.csv    one row per 60 frames: frame, pc, copier hits, rom size as mGBA
--                   reports it. A flat pc with a stalled frame count is the wedge.
--   copier rows     the first copies the engine performs, with a text snippet read
--                   from each pointer register. The snippet is what makes this cold
--                   boot evidence about THIS image rather than about the save.
--   shot_*.png      every 300 frames, so the operator-visible dialogue is on record.
--   marker.txt      "armed" as soon as it is injected, then the end status.
--
-- The dialogue record copier is the liveness channel. A silent instrument beside a
-- silent liveness channel proves nothing, so a run with no copier hits says the route
-- never reached dialogue, not that the image is clean.

local COPIER = 0x0801227A

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local out = (os.getenv("TOOLKIT031_OUT") or (exp_dir .. "coldboot.csv"))
local declared_size = tonumber(os.getenv("DIALOGUE_ROM_SIZE") or "")

-- The snippet window and the screenshot cadence are the two things a run needs to
-- change, because 40 units stop inside a line that opens with eight control codes and
-- five seconds can miss a dialogue box between two copies. Both are environment
-- overrides with these defaults, so a session can widen them without editing this file.
local function knob(name, default)
    return tonumber(os.getenv(name) or "") or default
end

local HORIZON = 200000     -- about fifty minutes; the operator closes the window
local SHOT_EVERY = knob("DIALOGUE_SHOT_EVERY", 300)   -- default one shot every five seconds
local BEAT_EVERY = 60
local SNIPPET_UNITS = knob("DIALOGUE_SNIPPET_UNITS", 40)
local SNIPPET_ROWS = 40    -- the first copies only: the cutscene's own lines

assert(emu ~= nil, "mGBA did not attach the emulation core")
assert(emu.setBreakpoint and emu.clearBreakpoint, "requires the 0.11 breakpoint API")
local code = emu:getGameCode()
assert(code == "BG3E" or code == "AGB-BG3E", "unexpected game code: " .. tostring(code))

local done = false
local function finish(status)
    if done then return end
    done = true
    local f = io.open(done_path, "w")
    if f then f:write(status) f:close() end
end

local function run()
    local csv = assert(io.open(out, "w"))
    csv:write("frame,pc,copier,rom_size\n")
    csv:flush()

    local copier_hits = 0
    local snippet_rows = 0

    -- A register read that cannot take the observer down with it.
    local function reg(name)
        local ok, value = pcall(function() return tonumber(emu:readRegister(name)) end)
        if ok and value then return value end
        return 0
    end

    -- The copied record's text, read as UTF-16LE units. Non-printable units become
    -- dots so a CSV row stays a CSV row; the point is to recognise a name, not to
    -- decode the whole stream.
    local function snippet(address)
        if address < 0x02000000 or address > 0x0203FFFF then return "-" end
        local units = {}
        for index = 0, SNIPPET_UNITS - 1 do
            local ok, low, high = pcall(function()
                return emu:read8(address + index * 2), emu:read8(address + index * 2 + 1)
            end)
            if not ok or low == nil or high == nil then break end
            local value = low + high * 256
            if value == 0 then break end
            units[#units + 1] = (value >= 32 and value < 127) and string.char(value) or "."
        end
        return table.concat(units)
    end

    local function escape(text)
        return (text:gsub(",", ";"))
    end

    local breakpoint_id
    breakpoint_id = emu:setBreakpoint(function()
        copier_hits = copier_hits + 1
        if snippet_rows < SNIPPET_ROWS then
            snippet_rows = snippet_rows + 1
            csv:write(string.format(
                "copy,%d,r0=%08X r1=%08X r2=%08X r3=%08X,a=%s,b=%s,c=%s,d=%s\n",
                snippet_rows, reg("r0"), reg("r1"), reg("r2"), reg("r3"),
                escape(snippet(reg("r0"))), escape(snippet(reg("r1"))),
                escape(snippet(reg("r2"))), escape(snippet(reg("r3")))))
            csv:flush()
        end
    end, COPIER)

    finish("armed")

    local frame = 0
    local callback_id
    callback_id = callbacks:add("frame", function()
        frame = frame + 1
        if frame >= HORIZON then
            callbacks:remove(callback_id)
            pcall(function() emu:clearBreakpoint(breakpoint_id) end)
            csv:close()
            finish("done:horizon")
            return
        end
        if frame % SHOT_EVERY == 0 then
            pcall(function()
                emu:screenshot(string.format("%sshot_%06d.png", exp_dir, frame))
            end)
        end
        if frame % BEAT_EVERY == 0 then
            local ok, pc = pcall(function() return emu:readRegister("pc") end)
            local ok_size, size = pcall(function() return emu:romSize() end)
            csv:write(string.format("%d,0x%08X,%d,%s\n", frame, (ok and pc) or 0,
                                    copier_hits, (ok_size and tostring(size)) or "?"))
            csv:flush()
        end
    end)
end

local ok, err = xpcall(run, function(e) return tostring(e) end)
if not ok then finish("error:" .. tostring(err)) end
