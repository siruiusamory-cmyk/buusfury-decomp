-- P-008 normal-melee clip-sequence observer.
--
-- Read-only with respect to emulated memory and input.
--
-- P-006C established the accepted-punch anchor: player object +0x04C is the
-- current animation-clip pointer, idle is 0x0851C618, and the punch clips
-- observed were 0x0851C680, 0x0851C6C0, and 0x0851C6A0. An accepted punch is
-- the transition from idle into a punch clip while A is held.
--
-- This probe records the ORDERED SERIES of accepted punches so the selection
-- mechanism can be tested against three hypotheses: previous-animation
-- avoidance (no immediate repeat), a fixed cycle (repeating period), or random
-- selection (repeats at the rate chance predicts).
--
-- It does NOT try to prove or disprove a combo. External research already
-- settled that question; see docs/research/P008_MELEE_VARIANT_SELECTION.md.
--
-- The candidate RNG words are sampled ONLY as raw observations. REFERENCE.md
-- records LoG2 seeds at 0x03003890 and 0x03003894 from TASVideos, and P-007
-- saw a leaf node referencing 0x03003898. That adjacency is unproven for this
-- game, so the words are logged verbatim with no claim attached.

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")

local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p008-clips.csv"
local tick_path = exp_dir .. "frame-tick.txt"

local EWRAM_LO = 0x02000000
local EWRAM_HI = 0x02040000
local PLAYER_SLOT = 0x03001C34
local KEY_ADDRESS = 0x03003304
local OBJECT_BYTES = 0x2A0

-- Animation-clip pointer and the idle value, both from P-006C.
local CLIP = 0x04C
local IDLE_CLIP = 0x0851C618

-- Candidate RNG words, logged as raw observations only.
local RNG_A = 0x03003890
local RNG_B = 0x03003894
local RNG_C = 0x03003898

local HORIZON = 40000

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

    wline("kind,tick,keys,a_held,player,clip,prev_clip,rng_a,rng_b,rng_c")

    local armed = assert(io.open(exp_dir .. "armed-marker.txt", "w"))
    armed:write("armed")
    armed:close()

    local tick = 0
    local stopped = false
    local prev_clip = nil
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
                finish("done:P008Clips")
                return
            end
            if tick > HORIZON then
                stopped = true
                callbacks:remove(callback_id)
                finish("done:P008Clips")
                return
            end

            local player = emu:read32(PLAYER_SLOT)
            if not in_ewram(player, OBJECT_BYTES) then return end

            local keys = emu:read16(KEY_ADDRESS)
            local a_held = 0
            if keys % 2 == 1 then a_held = 1 end
            local clip = emu:read32(player + CLIP)

            -- Emit on every clip change, not only on accepted punches. A run
            -- must be able to show which clip preceded each punch, and a
            -- transition that is NOT idle-to-punch is exactly the evidence
            -- that would contradict the accepted-punch definition.
            if prev_clip ~= clip then
                local kind = "C"
                if prev_clip == IDLE_CLIP and clip ~= IDLE_CLIP
                    and a_held == 1 then
                    kind = "PUNCH"
                end
                wline(string.format(
                    "%s,%d,%04x,%d,%08x,%08x,%s,%08x,%08x,%08x",
                    kind, tick, keys, a_held, player, clip,
                    prev_clip and string.format("%08x", prev_clip) or "none",
                    emu:read32(RNG_A), emu:read32(RNG_B), emu:read32(RNG_C)))
                prev_clip = clip
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
