-- Bounded capability probe: measure how long a full EWRAM dispatch scan takes
-- from the Scripting prompt, and how many matches it finds, before relying on
-- that scan inside an observer's init path.
--
-- Read-only with respect to emulated memory and input. Writes one text file to
-- the ignored run directory and registers no callbacks.

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")

local exp_dir = done_path:gsub("[^/\\]+$", "")
local out_path = exp_dir .. "p006c-scan-timing.txt"

local EWRAM_LO = 0x02000000
local EWRAM_HI = 0x02040000
local TARGET_DISPATCH = 0x0804C484
local OBJECT_BYTES = 0x2A0

local function finish(status)
    local marker = io.open(done_path, "w")
    if marker then marker:write(status) marker:close() end
end

local function run()
    assert(emu ~= nil and emu:getGameCode() == "AGB-BG3E")

    local out = assert(io.open(out_path, "w"))
    out:write("game_code=" .. tostring(emu:getGameCode()) .. "\n")

    local started = os.clock()
    local matches = {}
    for address = EWRAM_LO, EWRAM_HI - OBJECT_BYTES, 4 do
        if emu:read32(address) == TARGET_DISPATCH then
            matches[#matches + 1] = address
        end
    end
    local elapsed = os.clock() - started

    out:write(string.format("scan_seconds=%.3f\n", elapsed))
    out:write(string.format("match_count=%d\n", #matches))
    for i = 1, math.min(#matches, 16) do
        out:write(string.format("match_%d=%08x\n", i, matches[i]))
    end
    out:close()

    -- The armed marker proves this probe completed its whole init path.
    local armed = assert(io.open(exp_dir .. "armed-marker.txt", "w"))
    armed:write("armed")
    armed:close()
end

local ok, err = xpcall(run, function(e)
    return tostring(e) .. "\n" .. debug.traceback(e, 2)
end)
if not ok then finish("error:init:" .. err) else finish("done:P006CScanTiming") end
