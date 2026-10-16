-- Ask two questions the last round could not separate, and answer them by measurement.
--
-- 1. Does `emu:readRegister("pc")` return the real program counter on this build? The
--    render observer logged 0x000001C4 for thousands of frames while the game rendered a
--    dialogue box, so either the game is wedged or the read returns a stale value.
-- 2. Do breakpoints fire at all? The observer's arm now succeeds and its channel is still
--    silent, so either the address never executes or breakpoints do not fire on this build.
--
-- HOW. This probe arms TWO addresses: the dialogue record copier, and the ARM/Thumb
-- dispatch thunk at 0x08046AA4 that both the copier route and much of the engine passes
-- through on every call, so a live game must trip it thousands of times. It samples the pc
-- every frame and reports how many DISTINCT values it saw. Distinct values above a handful
-- means the read works and the copier address simply was not executed in this scene;
-- a single constant value with a live game means the read is unreliable, which changes what
-- every earlier "silent channel" conclusion in this ticket is worth.
--
-- READ-ONLY: arms breakpoints, reads registers and memory, writes one host file.

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local out = exp_dir .. "pc.txt"

local COPIER = 0x0801227A
local DISPATCH = 0x08046AA4

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

    local copier_hits = 0
    local dispatch_hits = 0

    local ok_copier, id_copier = pcall(function()
        return emu:setBreakpoint(function() copier_hits = copier_hits + 1 end, COPIER)
    end)
    local ok_dispatch, id_dispatch = pcall(function()
        return emu:setBreakpoint(function() dispatch_hits = dispatch_hits + 1 end, DISPATCH)
    end)
    note("arm copier ok=%s id=%s", tostring(ok_copier), tostring(id_copier))
    note("arm dispatch ok=%s id=%s", tostring(ok_dispatch), tostring(id_dispatch))

    local seen = {}
    local distinct = 0
    local samples = 0
    local first = nil
    local last = nil

    local frame = 0
    local callback_id
    callback_id = callbacks:add("frame", function()
        frame = frame + 1
        local ok, pc = pcall(function() return emu:readRegister("pc") end)
        if ok and pc ~= nil then
            samples = samples + 1
            if first == nil then first = pc end
            last = pc
            if not seen[pc] then
                seen[pc] = 0
                distinct = distinct + 1
            end
            seen[pc] = seen[pc] + 1
        end
        if frame >= 240 then
            callbacks:remove(callback_id)
            note("frames=%d samples=%d distinct_pc=%d", frame, samples, distinct)
            note("first_pc=%s last_pc=%s", tostring(first), tostring(last))
            note("copier_hits=%d dispatch_hits=%d", copier_hits, dispatch_hits)
            local top = {}
            for value, count in pairs(seen) do
                top[#top + 1] = { value, count }
            end
            table.sort(top, function(a, b) return a[2] > b[2] end)
            for index = 1, math.min(6, #top) do
                note("pc 0x%08X seen %d", top[index][1], top[index][2])
            end
            log:close()
            pcall(function() emu:clearBreakpoint(id_copier) end)
            pcall(function() emu:clearBreakpoint(id_dispatch) end)
            finish("done")
        end
    end)
end

local ok, err = xpcall(run, function(problem) return tostring(problem) end)
if not ok then finish("error:" .. tostring(err)) end
