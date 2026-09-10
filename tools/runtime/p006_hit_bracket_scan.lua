-- P-006 exact hit-bracket capture. Keep a rolling full-EWRAM snapshot and
-- preserve the frames immediately before, at, and after the observed target
-- +0x1D4 event-marker transition. No load-specific EWRAM address is reused.
local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")

local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p006-hit-bracket.txt"
local EWRAM_LO = 0x02000000
local EWRAM_BYTES = 0x40000
local EWRAM_HI = EWRAM_LO + EWRAM_BYTES
local IWRAM_LO = 0x03000000
local IWRAM_BYTES = 0x8000
local TARGET_DISPATCH = 0x0804C484
local TARGET_BYTES = 0x200
local EVENT_OFFSET = 0x1D4
local HORIZON = 180

local function finish(status)
    local marker = io.open(done_path, "w")
    if marker then marker:write(status) marker:close() end
end

local function write_file(path, data)
    local file = assert(io.open(path, "wb"))
    file:write(data)
    file:close()
end

local function run()
    assert(emu ~= nil and emu:getGameCode() == "AGB-BG3E")

    local function wline(line)
        local log = assert(io.open(log_path, "a"))
        log:write(line .. "\n")
        log:close()
    end

    local function in_ewram(address, length)
        return address >= EWRAM_LO and address + length <= EWRAM_HI
    end

    local function discover_target()
        local found = {}
        for address = EWRAM_LO, EWRAM_HI - TARGET_BYTES, 4 do
            if emu:read32(address) == TARGET_DISPATCH then
                found[#found + 1] = address
            end
        end
        if #found ~= 1 then
            error("expected exactly one target dispatch match, found " .. #found)
        end
        return found[1]
    end

    local target = discover_target()
    local epoch = 1
    local previous_marker = emu:read32(target + EVENT_OFFSET)
    local previous_snapshot = emu:readRange(EWRAM_LO, EWRAM_BYTES)
    local previous_iwram = emu:readRange(IWRAM_LO, IWRAM_BYTES)
    local previous2_snapshot = previous_snapshot
    local previous2_iwram = previous_iwram
    local event_seen = false
    local post_frames = 0

    wline(string.format("EPOCH,%d,target,%08x,marker,%08x",
        epoch, target, previous_marker))
    local armed = assert(io.open(exp_dir .. "armed-marker.txt", "w"))
    armed:write("armed")
    armed:close()

    local tick = 0
    local stopped = false
    local callback_id
    callback_id = callbacks:add("frame", function()
        local ok, err = xpcall(function()
            if stopped then return end
            tick = tick + 1

            local stop_file = io.open(exp_dir .. "STOP-NOW.txt", "r")
            if stop_file then
                stop_file:close()
                stopped = true
                callbacks:remove(callback_id)
                finish("done:P006HitBracket:stopped")
                return
            end

            if not in_ewram(target, TARGET_BYTES) or
                    emu:read32(target) ~= TARGET_DISPATCH then
                target = discover_target()
                epoch = epoch + 1
                previous_marker = emu:read32(target + EVENT_OFFSET)
                previous_snapshot = emu:readRange(EWRAM_LO, EWRAM_BYTES)
                previous_iwram = emu:readRange(IWRAM_LO, IWRAM_BYTES)
                previous2_snapshot = previous_snapshot
                previous2_iwram = previous_iwram
                event_seen = false
                post_frames = 0
                wline(string.format("EPOCH,%d,target,%08x,marker,%08x",
                    epoch, target, previous_marker))
                return
            end

            local marker = emu:read32(target + EVENT_OFFSET)
            local current_snapshot = emu:readRange(EWRAM_LO, EWRAM_BYTES)
            local current_iwram = emu:readRange(IWRAM_LO, IWRAM_BYTES)
            if not event_seen and marker ~= previous_marker then
                event_seen = true
                write_file(exp_dir .. "p006-hit-before2.bin", previous2_snapshot)
                write_file(exp_dir .. "p006-hit-before.bin", previous_snapshot)
                write_file(exp_dir .. "p006-hit-event.bin", current_snapshot)
                write_file(exp_dir .. "p006-hit-iwram-before2.bin", previous2_iwram)
                write_file(exp_dir .. "p006-hit-iwram-before.bin", previous_iwram)
                write_file(exp_dir .. "p006-hit-iwram-event.bin", current_iwram)
                wline(string.format(
                    "EVENT,tick,%d,epoch,%d,target,%08x,marker,%08x>%08x",
                    tick, epoch, target, previous_marker, marker))
            elseif event_seen then
                post_frames = post_frames + 1
                if post_frames == 1 then
                    write_file(exp_dir .. "p006-hit-after1.bin", current_snapshot)
                    write_file(exp_dir .. "p006-hit-iwram-after1.bin", current_iwram)
                else
                    write_file(exp_dir .. "p006-hit-after2.bin", current_snapshot)
                    write_file(exp_dir .. "p006-hit-iwram-after2.bin", current_iwram)
                    wline(string.format("COMPLETE,tick,%d", tick))
                    stopped = true
                    callbacks:remove(callback_id)
                    finish("done:P006HitBracket")
                    return
                end
            end

            previous2_snapshot = previous_snapshot
            previous2_iwram = previous_iwram
            previous_marker = marker
            previous_snapshot = current_snapshot
            previous_iwram = current_iwram
            if tick >= HORIZON then
                wline("NO_EVENT")
                stopped = true
                callbacks:remove(callback_id)
                finish("error:P006HitBracket:no-event")
            end
        end, debug.traceback)
        if not ok then
            stopped = true
            if callback_id then callbacks:remove(callback_id) end
            wline("ERROR," .. tostring(err):gsub("\n", " "))
            finish("error:P006HitBracket")
        end
    end)
end

local ok, err = xpcall(run, debug.traceback)
if not ok then
    local log = io.open(log_path, "a")
    if log then log:write("ERROR," .. tostring(err):gsub("\n", " ") .. "\n") log:close() end
    finish("error:P006HitBracket")
end
