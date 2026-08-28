-- P-006C mGBA 0.11 capability probe.  It is read-only: confirm that a
-- scripted breakpoint callback resumes emulation and exposes live registers.
local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")

local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p006c-dev-breakpoint-probe.csv"
local breakpoint_pc = 0x0800AA4A
local frames = 0
local hits = 0
local breakpoint_id

local function write_line(line)
    local log = assert(io.open(log_path, "a"))
    log:write(line .. "\n")
    log:close()
end

local function finish(status)
    local marker = assert(io.open(done_path, "w"))
    marker:write(status)
    marker:close()
end

assert(emu and emu.setBreakpoint and emu.clearBreakpoint,
    "requires mGBA 0.11 scripted-breakpoint API")
write_line("kind,frame,pc,r0,r1")
breakpoint_id = emu:setBreakpoint(function(info)
    hits = hits + 1
    write_line(string.format("B,%d,%08x,%08x,%08x", frames,
        tonumber(emu:readRegister("pc")), tonumber(emu:readRegister("r0")),
        tonumber(emu:readRegister("r1"))))
    if hits >= 2 then emu:clearBreakpoint(breakpoint_id) end
end, breakpoint_pc)

local callback_id
callback_id = callbacks:add("frame", function()
    frames = frames + 1
    write_line(string.format("F,%d", frames))
    if frames >= 120 then
        if breakpoint_id then emu:clearBreakpoint(breakpoint_id) end
        callbacks:remove(callback_id)
        finish("done:P006CDevBreakpointProbe")
    end
end)
