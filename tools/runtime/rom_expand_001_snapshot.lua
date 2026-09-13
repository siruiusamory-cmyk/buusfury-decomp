-- ROM-EXPAND-001 one-shot frame capture. No input or emulated-memory writes.
local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
assert(emu and emu.screenshot, "mGBA screenshot API unavailable")
emu:screenshot(exp_dir .. "rom-expand-001-current-dialogue.png")
local marker = assert(io.open(done_path, "w"))
marker:write("captured\n")
marker:close()
