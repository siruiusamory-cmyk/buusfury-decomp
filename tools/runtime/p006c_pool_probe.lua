-- P-006C attack-object pool probe.
--
-- Read-only with respect to emulated memory and input.
--
-- Run 20260827-233643-45f579b4 refuted construction-per-punch: no call of the
-- constructor 0x08029FE6 occurred across 188 A presses, while one object
-- address was reused six times. The working hypothesis is that melee attack
-- objects are POOLED, so a punch reuses an existing object rather than
-- allocating one.
--
-- An attack object is recognized by its layout, established statically:
--
--   +0x00  vtable pointer, always 0x08049DF0
--   +0x04  owner
--   +0x08  phase flag, toggled 0 -> 1 by m1 on contact
--
-- This probe enumerates every live attack object each frame and records the
-- phase field of each, so a punch shows up as a phase transition on a specific
-- object. It never assumes an address from a previous load epoch.

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")

local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p006c-pool.csv"
local tick_path = exp_dir .. "frame-tick.txt"

local EWRAM_LO = 0x02000000
local EWRAM_HI = 0x02040000
local ATTACK_VTABLE = 0x08049DF0
local OBJECT_BYTES = 0x0C
local KEY_ADDRESS = 0x03003304
local HORIZON = 18000

-- Rescan for pool membership on this interval. Objects are expected to be
-- long-lived, so a periodic rescan is enough and keeps per-frame cost low.
local RESCAN_TICKS = 15
-- Bounded only to stop a runaway scan; the observed pool is far smaller. A
-- truncated scan would silently hide objects, so the SCAN row records the
-- count actually found and the cap is set well above it.
local MAX_OBJECTS = 64

local function wline(line)
    local log = assert(io.open(log_path, "a"))
    log:write(line .. "\n")
    log:close()
end

local function discover_objects()
    local found = {}
    for address = EWRAM_LO, EWRAM_HI - OBJECT_BYTES, 4 do
        if emu:read32(address) == ATTACK_VTABLE then
            found[#found + 1] = address
            if #found >= MAX_OBJECTS then break end
        end
    end
    return found
end

local function finish(status)
    local marker = io.open(done_path, "w")
    if marker then marker:write(status) marker:close() end
end

local function run()
    assert(emu ~= nil and emu:getGameCode() == "AGB-BG3E")

    wline("kind,tick,keys,a_pressed,object,owner,phase")

    -- The first scan legitimately returns nothing: the previous capture found
    -- zero attack objects at load yet saw several appear later, so the pool is
    -- populated after the state resumes. An empty result here is recorded, not
    -- treated as an error.
    local objects = discover_objects()
    wline(string.format("SCAN,0,0000,0,00000000,00000000,%d", #objects))
    for _, address in ipairs(objects) do
        wline(string.format("FOUND,0,0000,0,%08x,%08x,%d",
            address, emu:read32(address + 4), emu:read32(address + 8)))
    end

    local armed = assert(io.open(exp_dir .. "armed-marker.txt", "w"))
    armed:write("armed")
    armed:close()

    local tick = 0
    local stopped = false
    local previous = {}
    local previous_keys = nil
    local callback_id

    callback_id = callbacks:add("frame", function()
        local ok, err = xpcall(function()
            if stopped then return end
            tick = tick + 1

            local tick_file = assert(io.open(tick_path, "w"))
            tick_file:write(tostring(tick))
            tick_file:close()

            local stop_file = io.open(exp_dir .. "STOP-NOW.txt", "r")
            if stop_file then
                stop_file:close()
                stopped = true
                callbacks:remove(callback_id)
                finish("done:P006CPool")
                return
            end
            if tick > HORIZON then
                stopped = true
                callbacks:remove(callback_id)
                finish("done:P006CPool")
                return
            end

            if tick % RESCAN_TICKS == 0 then
                objects = discover_objects()
            end

            local keys = emu:read16(KEY_ADDRESS)
            local a_pressed = keys % 2

            -- Log input independently of phase changes. An earlier version
            -- emitted a row only inside the phase-change branch below, so a
            -- capture in which the human pressed A throughout still recorded
            -- keys as zero on every row: the presses were read but never
            -- sampled into any row. Input transitions must stand alone.
            if previous_keys ~= keys then
                previous_keys = keys
                wline(string.format("K,%d,%04x,%d,00000000,00000000,0",
                    tick, keys, a_pressed))
            end

            -- Report phase changes separately, so every punch-shaped
            -- transition is preserved while idle frames stay out of the log.
            for _, address in ipairs(objects) do
                if emu:read32(address) == ATTACK_VTABLE then
                    local phase = emu:read32(address + 8)
                    if previous[address] ~= phase then
                        -- Distinguish a genuine transition from the first
                        -- sighting of a newly discovered object. The earlier
                        -- version logged both as "P", which made rescan
                        -- boundaries look like punch events.
                        local kind = "P"
                        if previous[address] == nil then kind = "NEW" end
                        previous[address] = phase
                        wline(string.format("%s,%d,%04x,%d,%08x,%08x,%d",
                            kind, tick, keys, a_pressed, address,
                            emu:read32(address + 4), phase))
                    end
                end
            end
        end, function(e)
            return tostring(e) .. "\n" .. debug.traceback(e, 2)
        end)
        if not ok then
            stopped = true
            callbacks:remove(callback_id)
            finish("error:frame:" .. err)
        end
    end)
end

local ok, err = xpcall(run, function(e)
    return tostring(e) .. "\n" .. debug.traceback(e, 2)
end)
if not ok then finish("error:init:" .. err) end
