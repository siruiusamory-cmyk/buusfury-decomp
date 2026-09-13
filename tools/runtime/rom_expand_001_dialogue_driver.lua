-- ROM-EXPAND-001 input driver. Separate from the read-only observer by design.
-- It walks left from the deterministic fixture, then taps A to speak normally.

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")

local LEFT = 0x20
local A = 0x01
local frame = 0
local callback

callback = callbacks:add("frame", function()
    frame = frame + 1
    if frame == 1 then
        emu:setKeys(LEFT)
    elseif frame == 52 then
        emu:setKeys(0)
    elseif frame == 58 then
        emu:setKeys(A)
    elseif frame == 61 then
        emu:setKeys(0)
    elseif frame == 100 then
        -- The consumer fires before the typewriter finishes presenting the
        -- retail dialogue box; take the acceptance screenshot after it is up.
        emu:screenshot(exp_dir .. "rom-expand-001-production-dialogue.png")
    elseif frame == 180 then
        callbacks:remove(callback)
        local marker = assert(io.open(done_path, "w"))
        marker:write("done\n")
        marker:close()
    end
end)
