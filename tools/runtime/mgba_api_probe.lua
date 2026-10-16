-- Diagnose which breakpoint signature the packaged 0.11 build accepts, and whether the
-- program counter can be read at all.
--
-- WHY. The render observer reported `ok=false "Error calling function (invoking failed)"`
-- from `emu:setBreakpoint(address, callback)` while the game was demonstrably rendering a
-- dialogue box, and its heartbeat logged pc 0x000001C4 for thousands of frames. Two
-- possibilities produce that pair: the arm call is wrong, or the emulator's function-call
-- bridge is broken for this build. This probe tells them apart by trying each plausible
-- signature inside its own `pcall` and writing the outcome, so the answer is measurement
-- rather than another guess.
--
-- READ-ONLY. It arms breakpoints, reads registers, writes one host file inside the run
-- directory. No input, no emulated memory write.

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local out = exp_dir .. "api.txt"

local function finish(status)
    local handle = io.open(done_path, "w")
    if handle then
        handle:write(status .. "\n")
        handle:close()
    end
end

local function run()
    local log = assert(io.open(out, "w"))
    local function note(format, ...)
        log:write(string.format(format, ...) .. "\n")
        log:flush()
    end

    note("game_code=%s", tostring(emu:getGameCode()))
    local ok_size, size = pcall(function() return emu:romSize() end)
    note("romSize ok=%s value=%s", tostring(ok_size), tostring(size))
    note("setBreakpoint type=%s", type(emu.setBreakpoint))
    note("readRegister type=%s", type(emu.readRegister))
    note("read16 type=%s", type(emu.read16))

    -- Can a register be read at all? A plausible pc is inside ROM or EWRAM.
    for _, name in ipairs({ "pc", "r0", "r1", "r15" }) do
        local ok, value = pcall(function() return emu:readRegister(name) end)
        note("readRegister(%s) ok=%s value=%s", name, tostring(ok), tostring(value))
    end

    -- Each candidate signature, tried in isolation. A callback that sets a flag is enough
    -- to prove the arm took; whether it ever FIRES is reported by the frame callback.
    local fired = 0
    local function mark() fired = fired + 1 end
    local attempts = {
        { "address_then_callback", function() return emu:setBreakpoint(0x0801227A, mark) end },
        { "callback_then_address", function() return emu:setBreakpoint(mark, 0x0801227A) end },
        { "address_only", function() return emu:setBreakpoint(0x0801227A) end },
        { "callback_only", function() return emu:setBreakpoint(mark) end },
        { "named_address", function() return emu:setBreakpoint("0x0801227A", mark) end },
    }
    for _, attempt in ipairs(attempts) do
        local ok, result = pcall(attempt[2])
        note("arm %s ok=%s result=%s", attempt[1], tostring(ok), tostring(result))
    end

    local frame = 0
    local callback_id
    callback_id = callbacks:add("frame", function()
        frame = frame + 1
        if frame == 60 then
            local ok, pc = pcall(function() return emu:readRegister("pc") end)
            note("frame60 pc ok=%s value=%s", tostring(ok), tostring(pc))
            local ok2, v = pcall(function() return emu:read16(0x08000000) end)
            note("frame60 read16(rom0) ok=%s value=%s", tostring(ok2), tostring(v))
        end
        if frame == 120 then
            local ok, pc = pcall(function() return emu:readRegister("pc") end)
            note("frame120 pc ok=%s value=%s", tostring(ok), tostring(pc))
            note("callback_fires f=%d", fired)
            log:close()
            callbacks:remove(callback_id)
            finish("done")
        end
    end)
end

local ok, err = xpcall(run, function(problem) return tostring(problem) end)
if not ok then
    local handle = io.open(exp_dir .. "api-error.txt", "w")
    if handle then
        handle:write(tostring(err) .. "\n")
        handle:close()
    end
    finish("error:" .. tostring(err))
end
