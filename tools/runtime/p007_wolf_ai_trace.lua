-- P-007 wolf AI state observer.
--
-- Read-only with respect to emulated memory and input. Records, on one shared
-- gameplay tick, the wolf's behavior-controller stack alongside the world
-- position of both actors, so a state transition can be correlated with the
-- player/wolf separation that may have caused it.
--
-- Controller layout established by P-006C static decode of the primitives
-- 0x0800AA9C (push), 0x0800AA4A (replace), 0x0800AAD8 (pop):
--
--   ctrl+0x04         stack depth, push guards depth < 5
--   ctrl+0x08 + 8*i   entry i = { node_ptr, table_slot }
--   selector          = (table_slot - 0x0870F514) / 8
--
-- The wolf controller is at actor+0x238. P-006C established the player has no
-- such controller, so only the wolf's is read.
--
-- POSITION: +0x1A0 is world X and +0x1A4 is world Y, both 8.8 fixed point, per
-- docs/research/archive/P-006.md and corroborated by cand_body_bounds_0800FE78.
-- docs/runtime-capture.md records the invariant
-- u32(target+0x04) == floor(u32(target+0x1A4) / 256) + 4, which is why +0x04 is
-- the integer world Y and was retracted as an HP field.
--
-- P-007 still treats these as decision operands rather than a solved subsystem,
-- because the ticket defers authoritative world position. Deltas are logged
-- verbatim in raw fixed-point units and are not converted to pixels.

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")

local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p007-wolf-ai.csv"
local tick_path = exp_dir .. "frame-tick.txt"

local EWRAM_LO = 0x02000000
local EWRAM_HI = 0x02040000
local TARGET_DISPATCH = 0x0804C484
local PLAYER_SLOT = 0x03001C34
local KEY_ADDRESS = 0x03003304
local OBJECT_BYTES = 0x2A0
local CTRL = 0x238
local MAX_DEPTH = 5
local TABLE_LO = 0x0870F514
local HP_OFFSET = 0x28C

-- World X and Y, 8.8 fixed point. Logged in raw units; see the header note.
local POS_X = 0x1A0
local POS_Y = 0x1A4
-- Player animation-clip pointer, the P-006C accepted-punch anchor. Recorded so
-- a run can be shown to be attack-free rather than assumed to be.
local CLIP = 0x04C

-- Frame counter and its derived index. Static decode of 0x08018C24 shows a
-- decrementing halfword at +0x12 that reloads from [actor+0x50] on underflow,
-- and 0x08018C34 stores (counter >> 3) as a byte at +0x11. Logged to test
-- whether the fixed 35-tick attack is driven by this counter; no claim is made
-- that it is an AI timer rather than an animation clock.
local FRAME_CTR = 0x12
local FRAME_IDX = 0x11

local HORIZON = 40000

-- Bounded only to stop a runaway scan; the observed states hold one or two
-- wolves. A truncated scan would silently hide an actor, so the SCAN row
-- records the count actually found and this cap sits well above it.
local MAX_TARGETS = 32
-- A full EWRAM scan measured 0.102 s in P-006C, so rescanning every quarter
-- second is affordable and still catches a wolf appearing after a transition.
local RESCAN_TICKS = 15

local function in_ewram(address, length)
    return address >= EWRAM_LO and address + length <= EWRAM_HI
end

-- Return EVERY actor carrying the dispatch word, not just the first. The
-- P-006 state single-wolf.ss1 held exactly one, so earlier probes asserted a
-- single match; the P-007 acquisition state wolf-acquire.ss1 holds two, and
-- that assert aborted the capture before it armed. Two wolves is also better
-- evidence, because their acquisition can be compared against each other.
local function discover_targets()
    local found = {}
    for address = EWRAM_LO, EWRAM_HI - OBJECT_BYTES, 4 do
        if emu:read32(address) == TARGET_DISPATCH then
            found[#found + 1] = address
            if #found >= MAX_TARGETS then break end
        end
    end
    return found
end

local function read_s32(address)
    local value = emu:read32(address)
    if value >= 0x80000000 then return value - 0x100000000 end
    return value
end

-- Serialize the controller as "depth|node@selector;..." so a transition is a
-- plain string inequality between consecutive ticks.
local function read_ctrl(actor)
    if actor == 0 then return "na" end
    local ctrl = actor + CTRL
    local depth = emu:read32(ctrl + 0x04)
    if depth < 0 or depth > MAX_DEPTH then
        return string.format("bad(%d)", depth)
    end
    local parts = {}
    for i = 0, depth - 1 do
        local entry = ctrl + 0x08 + (i * 8)
        local node = emu:read32(entry)
        local slot = emu:read32(entry + 4)
        local selector = "?"
        if slot >= TABLE_LO and (slot - TABLE_LO) % 8 == 0 then
            selector = tostring((slot - TABLE_LO) / 8)
        end
        parts[#parts + 1] = string.format("%08x@%s", node, selector)
    end
    return string.format("%d|%s", depth, table.concat(parts, ";"))
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

    wline("kind,tick,keys,wolf,wolf_state,wolf_hp,wolf_x,wolf_y," ..
        "player,player_x,player_y,player_clip,dx,dy,wolf_ctr,wolf_idx")

    -- Record how many wolves this state actually holds instead of asserting a
    -- count. wolf-acquire.ss1 holds two, and the previous single-wolf assert
    -- aborted the capture at init before it could arm.
    local targets = discover_targets()
    wline(string.format("SCAN,0,0000,%08x,count=%d,0,0,0,00000000,0,0,00000000,na,na,0,0",
        0, #targets))

    local armed = assert(io.open(exp_dir .. "armed-marker.txt", "w"))
    armed:write("armed")
    armed:close()

    local tick = 0
    local stopped = false
    -- One signature per wolf address, so two wolves are tracked independently
    -- and one changing state cannot suppress the other's row.
    local prev = {}
    local rescan_at = 0
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
                finish("done:P007WolfAI")
                return
            end
            if tick > HORIZON then
                stopped = true
                callbacks:remove(callback_id)
                finish("done:P007WolfAI")
                return
            end

            -- Rescan periodically rather than only when a known wolf goes
            -- stale. An acquisition run crosses an area transition, after
            -- which the wolves are DIFFERENT objects at different addresses,
            -- so waiting for an existing pointer to fault would miss a wolf
            -- that appears while the old list is still valid. mGBA exposes no
            -- entity-lifecycle callback (alarm/crashed/frame/keysRead/reset/
            -- savedataUpdated/sleep/shutdown/start/stop), so polling is the
            -- only available mechanism.
            if tick >= rescan_at then
                targets = discover_targets()
                rescan_at = tick + RESCAN_TICKS
            end

            local player = emu:read32(PLAYER_SLOT)
            if not in_ewram(player, OBJECT_BYTES) then player = 0 end

            local keys = emu:read16(KEY_ADDRESS)
            local px, py, clip = 0, 0, 0
            if player ~= 0 then
                px = read_s32(player + POS_X)
                py = read_s32(player + POS_Y)
                clip = emu:read32(player + CLIP)
            end

            for _, target in ipairs(targets) do
                if in_ewram(target, OBJECT_BYTES)
                    and emu:read32(target) == TARGET_DISPATCH then
                    local state = read_ctrl(target)
                    local wx = read_s32(target + POS_X)
                    local wy = read_s32(target + POS_Y)
                    local hp = read_s32(target + HP_OFFSET)
                    local wctr = emu:read16(target + FRAME_CTR)
                    local widx = emu:read8(target + FRAME_IDX)

                    -- Deltas need both actors loaded. Leaving them numeric
                    -- when the player pointer is 0 would report the wolf's
                    -- absolute coordinates as a separation, which is how run
                    -- 20260828-100719-3a8e0ca3 produced apparent distances of
                    -- ~397217. Use the "na" sentinel, per
                    -- p006c_ctrl_stack.lua:67.
                    local dx, dy = "na", "na"
                    if player ~= 0 then
                        dx = tostring(px - wx)
                        dy = tostring(py - wy)
                    end

                    -- Per-wolf signature keyed by address, including the
                    -- player pointer because it changes across an area
                    -- transition (0203ceb4 -> 0202e4d0 in that same run).
                    local signature = string.format("%08x|%s|%d|%04x|%08x",
                        player, state, hp, keys, clip)
                    if prev[target] ~= signature then
                        prev[target] = signature
                        wline(string.format(
                            "S,%d,%04x,%08x,%s,%d,%d,%d,%08x,%d,%d,%08x,%s,%s,%d,%d",
                            tick, keys, target, state, hp, wx, wy,
                            player, px, py, clip, dx, dy, wctr, widx))
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
