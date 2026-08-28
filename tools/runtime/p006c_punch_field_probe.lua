-- P-006C punch-field probe.
--
-- Read-only with respect to emulated memory and input.
--
-- Two anchor candidates have now been refuted at runtime: the attack-object
-- constructor 0x08029FE6 never executed across 188 A presses, and no
-- attack-object phase field at +0x08 moved across 290 A presses. Both were
-- proposed structures tested one at a time.
--
-- This probe stops proposing. Instead of watching a chosen field, it snapshots
-- the whole player object every frame and reports which offsets change on the
-- frames where A goes down. A field that belongs to the punch must change on
-- attack frames and stay quiet otherwise, so the correlation itself identifies
-- the candidate rather than a static guess.
--
-- Player object comes from the documented slot 0x03001C34 and is re-read every
-- frame, so no EWRAM address is carried across load epochs.

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")

local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p006c-fields.csv"
local tick_path = exp_dir .. "frame-tick.txt"

local EWRAM_LO = 0x02000000
local EWRAM_HI = 0x02040000
local PLAYER_SLOT = 0x03001C34
local KEY_ADDRESS = 0x03003304
local KEY_A = 0x0001

-- Watch the documented extent of an actor object. 0x2A0 covers the controller
-- at +0x238 and authoritative HP at +0x28C.
local OBJECT_BYTES = 0x2A0
local HORIZON = 18000

local function in_ewram(address, length)
    return address >= EWRAM_LO and address + length <= EWRAM_HI
end

local function wline(line)
    local log = assert(io.open(log_path, "a"))
    log:write(line .. "\n")
    log:close()
end

local function finish(status)
    local marker = io.open(done_path, "w")
    if marker then marker:write(status) marker:close() end
end

local function run()
    assert(emu ~= nil and emu:getGameCode() == "AGB-BG3E")

    wline("kind,tick,keys,a_edge,player,offset,old,new")

    local armed = assert(io.open(exp_dir .. "armed-marker.txt", "w"))
    armed:write("armed")
    armed:close()

    local tick = 0
    local stopped = false
    local previous = nil
    local previous_player = nil
    local previous_a = 0
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
                finish("done:P006CFields")
                return
            end
            if tick > HORIZON then
                stopped = true
                callbacks:remove(callback_id)
                finish("done:P006CFields")
                return
            end

            local player = emu:read32(PLAYER_SLOT)
            if not in_ewram(player, OBJECT_BYTES) then return end

            -- Reset the baseline if the object itself moved, so a relocation is
            -- never reported as a field change.
            if previous_player ~= player then
                previous_player = player
                previous = nil
                wline(string.format("OBJ,%d,0000,0,%08x,00000000,00000000,00000000",
                    tick, player))
            end

            local keys = emu:read16(KEY_ADDRESS)
            -- Bit 0 is A, active high, verified against a run in which the same
            -- mirror returned 0x0001 for A and 0x0010/0x20/0x40/0x80 elsewhere.
            local a_now = 0
            if keys % 2 == 1 then a_now = 1 end
            local a_edge = 0
            if a_now == 1 and previous_a == 0 then a_edge = 1 end
            previous_a = a_now

            local current = {}
            for offset = 0, OBJECT_BYTES - 4, 4 do
                current[offset] = emu:read32(player + offset)
            end

            if previous ~= nil then
                for offset = 0, OBJECT_BYTES - 4, 4 do
                    if previous[offset] ~= current[offset] then
                        wline(string.format(
                            "F,%d,%04x,%d,%08x,%03x,%08x,%08x",
                            tick, keys, a_edge, player, offset,
                            previous[offset], current[offset]))
                    end
                end
            end
            previous = current

            -- Record the input edge itself so presses that change no field are
            -- still visible, which is what refuted the previous two candidates.
            if a_edge == 1 then
                wline(string.format(
                    "A,%d,%04x,1,%08x,000,00000000,00000000", tick, keys, player))
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
