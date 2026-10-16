-- FRIEND-V3-PLAYTEST-BOOST-001: read the inventory block live while the operator equips.
--
-- WHY. The Bandana's id is already measured (126, through the gear table the renderer
-- names). What is still unknown is how an item is stored once it is held, which is what a
-- grant has to write. The fastest honest way to see that is to watch the inventory RAM
-- while the operator equips the bandana on a completed save.
--
-- READ-ONLY. It reads emulated memory and registers and writes host files inside the run
-- directory. It presses no key, writes no emulated memory and modifies no emulated state,
-- so the operator's own play is what produces the state being read.
--
-- WHAT IT WRITES, inside the run directory named by rom011_marker_path:
--   inventory.csv    a row every BEAT frames: frame and the u32 count at 0x0300114C.
--   snapshot_<n>.txt a full dump of the window, written only when it CHANGES: the count, a
--                    per-row `first`/`second` summary, and the raw 1024 bytes. THE RAW LINE
--                    IS THE AUTHORITATIVE RECORD. The summary was written under an earlier
--                    8-byte-slot reading of the inventory; the entry is in fact one 4-byte
--                    word, the top nibble a wearer index and the low 28 bits an item id, so
--                    the summary pairs adjacent entries and must be re-read from the raw line.
--   heartbeat.csv    frame and pc every BEAT frames, so a stalled frame count is visible.
--   marker.txt       "armed", then the end status.

local COUNT = 0x0300114C
local WINDOW = 0x03001068
local WINDOW_BYTES = 0x400

local function knob(name, default)
    return tonumber(os.getenv(name) or "") or default
end

local MAX_FRAMES = knob("INV001_MAX_FRAMES", 36000)
local BEAT_EVERY = knob("INV001_BEAT_EVERY", 30)
local SNAP_LIMIT = knob("INV001_SNAP_LIMIT", 400)

local marker_path = rom011_marker_path
assert(type(marker_path) == "string" and #marker_path > 0, "marker path not provided")
local run_dir = marker_path:gsub("[^/\\]+$", "")
local function in_run(name) return run_dir .. name end

assert(emu ~= nil, "mGBA did not attach the emulation core")
local code = emu:getGameCode()
assert(code == "BG3E" or code == "AGB-BG3E", "unexpected game code: " .. tostring(code))

local function status(text)
    local handle = io.open(marker_path, "w")
    if handle then handle:write(text) handle:close() end
end

local function u8(address)
    local ok, value = pcall(function() return emu:read8(address) end)
    if ok then return value end
end

local function hex_bytes(address, length)
    local parts = {}
    for index = 0, length - 1 do
        local value = u8(address + index)
        if value == nil then return nil end
        parts[#parts + 1] = string.format("%02X", value)
    end
    return table.concat(parts, " ")
end

local function read_count()
    local lo, hi = u8(COUNT), u8(COUNT + 1)
    if lo == nil or hi == nil then return nil end
    return lo + hi * 256
end

local inventory = assert(io.open(in_run("inventory.csv"), "w"))
inventory:write("frame,count\n")
inventory:flush()
local heartbeat = assert(io.open(in_run("heartbeat.csv"), "w"))
heartbeat:write("frame,pc\n")
heartbeat:flush()

local snapshots = 0
local last_hex = nil
local frames = 0
local callback
callback = callbacks:add("frame", function()
    frames = frames + 1

    if frames % BEAT_EVERY == 0 then
        local count = read_count()
        local ok, pc = pcall(function() return emu:readRegister("pc") end)
        inventory:write(string.format("%d,%s\n", frames, count ~= nil and tostring(count) or "?"))
        inventory:flush()
        heartbeat:write(string.format("%d,0x%08X\n", frames, (ok and pc) or 0))
        heartbeat:flush()

        local blob = hex_bytes(WINDOW, WINDOW_BYTES)
        if blob ~= nil and blob ~= last_hex then
            last_hex = blob
            snapshots = snapshots + 1
            local handle = io.open(in_run(string.format("snapshot_%04d.txt", snapshots)), "w")
            if handle then
                handle:write(string.format("frame=%d count=%s\n", frames,
                    count ~= nil and tostring(count) or "?"))
                for slot = 0, 24 do
                    local base = COUNT + 4 + slot * 8
                    local lo, hi = u8(base), u8(base + 1)
                    local lo2, hi2 = u8(base + 4), u8(base + 5)
                    if lo and lo2 then
                        handle:write(string.format(
                            "slot %2d @%08X first=%04X second=%04X\n",
                            slot, base, lo + hi * 256, lo2 + hi2 * 256))
                    end
                end
                handle:write("entries: one 4-byte word each, from the raw line below\n")
                handle:write("raw " .. blob .. "\n")
                handle:close()
            end
        end
    end

    if frames >= MAX_FRAMES or snapshots >= SNAP_LIMIT then
        inventory:close()
        heartbeat:close()
        status(string.format("done:frames=%d snapshots=%d", frames, snapshots))
        pcall(function() callbacks:remove(callback) end)
    end
end)

status("armed")
