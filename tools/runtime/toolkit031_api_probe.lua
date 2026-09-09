-- TOOLKIT-031 capability probe: confirm the scripted-breakpoint API and the
-- identity asserts the execution observer depends on. Read-only: no memory
-- writes, no key writes.
local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log = assert(io.open(exp_dir .. "toolkit031-api-probe.txt", "w"))
log:write("emu=", tostring(emu ~= nil), "\n")
if emu then
    log:write("setBreakpoint=", tostring(emu.setBreakpoint ~= nil), "\n")
    log:write("clearBreakpoint=", tostring(emu.clearBreakpoint ~= nil), "\n")
    local ok, code = pcall(function() return emu:getGameCode() end)
    log:write("gameCode=", tostring(ok and code or "ERR"), "\n")
    local ok2, sz = pcall(function() return emu:romSize() end)
    log:write("romSize=", tostring(ok2 and sz or "ERR"), "\n")
    local ok3, rr = pcall(function() return emu:readRegister("pc") end)
    log:write("readRegister=", tostring(ok3 and rr or "ERR"), "\n")
end
log:close()
local marker = assert(io.open(done_path, "w"))
marker:write("done:TOOLKIT031ApiProbe")
marker:close()
