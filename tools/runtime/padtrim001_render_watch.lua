-- FRIEND-V3-TEXT-AND-DIALOGUE-PASS-001: the padding-repair render instrument.
--
-- WHAT IT IS FOR. The trailing-pad repair shortens a record's handle by its pad, so the
-- engine copies fewer units and the record reads its text with the gap gone. Static reading
-- says every other record's span still reads what it read before, because no byte moved.
-- Only the engine can say whether a shortened record still DISPLAYS correctly, and whether
-- the space units that remain in the stream are drawn or collapsed.
--
-- READ-ONLY. One breakpoint as a liveness channel, registers and memory read, host files
-- written inside the run directory. No input, no emulated memory write. The operator
-- drives. (docs/skills/mgba-runtime.md 7 and 8.)
--
-- WHY THE OUTPUT NAMES ARE FIXED RATHER THAN TAKEN FROM TOOLKIT031_OUT. That variable is
-- set by the launcher to the generic `toolkit031-execution.csv` and its own collector reads
-- it; writing this instrument's heartbeat there loses it, which is what the first live run
-- measured (a live session with screenshots and an empty heartbeat). The file names here
-- are this observer's own, in the run directory, and the launcher's generic CSV is left to
-- the launcher.
--
-- LIVENESS. A run with no copier hits proves nothing: it says the route never reached
-- dialogue, not that the rendering is correct. The dialogue record copier at 0x0801227A is
-- the liveness channel.
--
-- WHAT IT WRITES
--   padtrim.csv   one row per 60 frames: frame, pc, copier hits.
--   copies.txt    every copied line, with the longest run of space units on it.
--   shot_*.png    every SHOT_EVERY frames.
--   marker.txt    "armed" on injection, then the end status.

local COPIER = 0x0801227A

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local out = exp_dir .. "padtrim.csv"
local copies_path = exp_dir .. "copies.txt"

local function knob(name, default)
    return tonumber(os.getenv(name) or "") or default
end

local HORIZON = knob("PADTRIM_HORIZON", 200000)
local SHOT_EVERY = knob("DIALOGUE_SHOT_EVERY", 240)
local SNIPPET_UNITS = knob("DIALOGUE_SNIPPET_UNITS", 120)
local BEAT_EVERY = 60

assert(emu ~= nil, "mGBA did not attach the emulation core")
assert(emu.setBreakpoint and emu.clearBreakpoint, "requires the 0.11 breakpoint API")
local code = emu:getGameCode()
assert(code == "BG3E" or code == "AGB-BG3E", "unexpected game code: " .. tostring(code))

local done = false
local function finish(status)
    if done then return end
    done = true
    local handle = io.open(done_path, "w")
    if handle then
        handle:write(status .. "\n")
        handle:close()
    end
end

local function run()
    -- The heartbeat is opened and written FIRST, before any breakpoint is armed, so a
    -- silent channel can be told apart from a dead instrument: frames present with no
    -- copier hits is a real negative, frames absent is an unproven instrument.
    local csv = assert(io.open(out, "w"))
    csv:write("frame,pc,copier_hits\n")
    csv:flush()

    local copies = assert(io.open(copies_path, "w"))
    copies:write("row,longest_space_run,units,text\n")
    copies:flush()

    local copier_hits = 0
    local rows = 0
    local ROW_LIMIT = 400

    local function reg(name)
        local ok, value = pcall(function() return emu:readRegister(name) end)
        return (ok and value) or 0
    end

    local function line(pointer)
        if not pointer or pointer < 0x08000000 then return nil end
        local units = {}
        local longest = 0
        local run = 0
        for index = 0, SNIPPET_UNITS - 1 do
            local ok, value = pcall(function() return emu:read16(pointer + index * 2) end)
            if not ok or value == nil or value == 0 then break end
            units[#units + 1] = value
            if value == 0x20 then
                run = run + 1
                if run > longest then longest = run end
            else
                run = 0
            end
        end
        return units, longest
    end

    local function render(units)
        local parts = {}
        for _, unit in ipairs(units) do
            if unit >= 0x20 and unit < 0x7F then
                parts[#parts + 1] = string.char(unit)
            else
                parts[#parts + 1] = string.format("\\x%04X", unit)
            end
        end
        return (table.concat(parts):gsub(",", ";"))
    end

    -- BREAKPOINT SIGNATURE IS (CALLBACK, ADDRESS), CALLBACK FIRST. Measured, not guessed:
    -- tools/runtime/mgba_api_probe.lua tried five spellings in one live session and only
    -- `emu:setBreakpoint(fn, address)` returned ok=true. `(address, fn)`, `(address)` and
    -- `(fn)` all return "Error calling function (invoking failed)", which is the same
    -- message a Lua-side error produces, so the wrong order is indistinguishable from a
    -- broken build by message alone. This observer had the order reversed, which is why
    -- its channel was silent while the game rendered a dialogue box.
    local arm_error = "none"
    local breakpoint_id = nil
    local ok_arm, arm_result = pcall(function()
        breakpoint_id = emu:setBreakpoint(function()
            copier_hits = copier_hits + 1
            if rows < ROW_LIMIT then
                for _, name in ipairs({ "r1", "r0", "r2", "r3" }) do
                    local units, longest = line(reg(name))
                    if units and #units > 2 then
                        rows = rows + 1
                        copies:write(string.format("%d,%d,%d,%s\n", rows, longest, #units,
                                                   render(units)))
                        copies:flush()
                        break
                    end
                end
            end
        end, COPIER)
    end)

    finish("armed")

    local frame = 0
    local callback_id
    callback_id = callbacks:add("frame", function()
        frame = frame + 1
        if frame >= HORIZON then
            callbacks:remove(callback_id)
            pcall(function() emu:clearBreakpoint(breakpoint_id) end)
            csv:close()
            copies:close()
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
            csv:write(string.format("%d,0x%08X,%d\n", frame, (ok and pc) or 0, copier_hits))
            csv:flush()
        end
        if frame == BEAT_EVERY then
            -- The arm result is reported once, into the run's own heartbeat, so a failed
            -- arm and a quiet channel can never be confused again.
            local note = io.open(exp_dir .. "arm.txt", "w")
            if note then
                note:write(string.format("ok=%s id=%s err=%s\n", tostring(ok_arm),
                                         tostring(arm_result), tostring(arm_error)))
                note:close()
            end
        end
    end)
end

local ok, err = xpcall(run, function(problem) return tostring(problem) end)
if not ok then finish("error:" .. tostring(err)) end
