-- SPRITE-NEW-RECORD-RUN-001: the dispatch-table probe.
--
-- ONE QUESTION. SPRITE-NEW-RUNTIME-001's record got no behaviour, and the actor
-- that would have run it is built by 0x0800A7A0, whose caller is 0x0800A9AA -
-- inside the routine at 0x0800A95A, which walks a per-actor state block:
--
--   [block + 0x00] current node
--   [block + 0x04] a signed byte index
--   [block + 0x08] a pointer to a count-prefixed table of node pointers
--
-- and calls `*(node)` for each. So the membership of that table is the thing an
-- authored record has to earn. The main observer could not read it: arming a
-- breakpoint on this routine never reported a hit there, in any registration
-- order, while five other breakpoints in the same session all did. This probe
-- arms exactly two - the table site and a handler site as a liveness control - so
-- "no hit" cannot be read as "the breakpoint list was full".
--
-- Read-only: it reads memory and registers and writes host files only.

local OUT_ROOT = os.getenv("SPRITENEW001_OUT_ROOT") or "spritenew003/out"
local TICKS = tonumber(os.getenv("SPRITENEW001_TICKS") or "1200")

local TABLE_SITE = 0x0800A9A4      -- r4 = block, r0 = the table entry just loaded
local HANDLER_ENTRY = 0x0800A7A0   -- liveness control
local TABLE_FIELD = 0x08
local MAX_ENTRIES = 24

assert(emu ~= nil, "mGBA did not attach the emulation core")
local code = emu:getGameCode()
assert(code == "BG3E" or code == "AGB-BG3E", "unexpected game code: " .. tostring(code))

local function hex(v)
    if v == nil then return "" end
    return string.format("0x%08X", v)
end

local function safe(fn, ...)
    local ok, value = pcall(fn, ...)
    if ok then return value end
    return nil
end

local function r8(a) return tonumber(safe(emu.read8, emu, a)) end
local function r32(a) return tonumber(safe(emu.read32, emu, a)) end
local function reg(name) return tonumber(safe(emu.readRegister, emu, name)) end

local frame = 0
local blocks = {}
local block_order = {}
local handler_hits = 0

-- The block is at actor+0x1B0 (0x08011198 adds 0x1B0 before calling), so the
-- actor is recoverable from it. Sampling the actor's own fields over time is what
-- turns "does this actor move" into a measurement, and it does not need the
-- construction path, which a restored savestate skips.
local ACTOR_BLOCK_OFFSET = 0x1B0
local WINDOW_START = 0x08
local WINDOW_WORDS = 16
local SAMPLE_STRIDE = 4
local actors = {}

local table_file = assert(io.open(OUT_ROOT .. "/dispatch-table.txt", "w"))
table_file:write("# the dispatcher 0x0800A95A's own table, read at 0x0800A9A4\n")
table_file:write("# block [block+0] current [block+4] index [block+8] table count entries...\n")
table_file:flush()

safe(emu.setBreakpoint, emu, function(_info)
    local entry = reg("r0")
    local block = reg("r4")
    if entry == nil or block == nil then return end
    if blocks[block] then return end
    blocks[block] = true
    block_order[#block_order + 1] = block
    local table = r32(block + TABLE_FIELD)
    local count = table and r32(table) or nil
    local parts = {}
    if count and count >= 0 and count <= MAX_ENTRIES then
        for i = 0, count - 1 do
            parts[#parts + 1] = hex(r32(table + 4 + 4 * i))
        end
    end
    table_file:write(string.format(
        "frame=%d entry=%s block=%s actor=%s current=%s index=%s table=%s count=%s entries=%s\n",
        frame, hex(entry), hex(block), hex(block - ACTOR_BLOCK_OFFSET),
        hex(r32(block)), tostring(r8(block + 4)), hex(table), tostring(count),
        table.concat(parts, " ")))
    table_file:flush()

    local actor = block - ACTOR_BLOCK_OFFSET
    if not actors[actor] then
        local words = {}
        for i = 0, WINDOW_WORDS - 1 do
            words[i] = { address = actor + WINDOW_START + 4 * i,
                         min = nil, max = nil }
        end
        actors[actor] = { actor = actor, block = block, words = words, samples = 0 }
    end
    console:log("SPRITENEW003 table block=" .. hex(block) .. " entry=" .. hex(entry) ..
        " count=" .. tostring(count) .. " frame=" .. tostring(frame))
end, TABLE_SITE)

safe(emu.setBreakpoint, emu, function(_info)
    handler_hits = handler_hits + 1
end, HANDLER_ENTRY)

local function sample_actors()
    for _, a in pairs(actors) do
        a.samples = a.samples + 1
        for i = 0, WINDOW_WORDS - 1 do
            local w = a.words[i]
            local v = r32(w.address)
            if v then
                if w.min == nil then w.min, w.max = v, v
                else
                    if v < w.min then w.min = v end
                    if v > w.max then w.max = v end
                end
            end
        end
    end
end

local schedule = {}
local scheduled = {}

local callback_id
local finished = false
callback_id = callbacks:add("frame", function()
    if finished then return end
    frame = frame + 1
    if frame % SAMPLE_STRIDE == 0 then sample_actors() end
    if frame >= TICKS then
        finished = true
        table_file:write(string.format(
            "# summary: distinct_blocks=%d handler_entry_hits=%d frames=%d\n",
            #block_order, handler_hits, frame))
        local moving = assert(io.open(OUT_ROOT .. "/movement.txt", "w"))
        moving:write("# every actor the dispatcher touched, and which of its words moved\n")
        for _, a in pairs(actors) do
            local changed = {}
            for i = 0, WINDOW_WORDS - 1 do
                local w = a.words[i]
                if w.min and w.max and w.max ~= w.min then
                    changed[#changed + 1] = string.format("+0x%02X:%s->%s",
                        WINDOW_START + 4 * i, hex(w.min), hex(w.max))
                end
            end
            moving:write(string.format("actor=%s block=%s samples=%d changed_words=%s\n",
                hex(a.actor), hex(a.block), a.samples,
                #changed == 0 and "NONE" or table.concat(changed, " ")))
        end
        moving:close()
        table_file:close()
        local marker = assert(io.open(OUT_ROOT .. "/done.txt", "w"))
        marker:write("done\n")
        marker:close()
        callbacks:remove(callback_id)
    end
end)

local marker = assert(io.open(OUT_ROOT .. "/armed.txt", "w"))
marker:write("armed\n")
marker:close()
console:log("SPRITENEW003 probe armed: ticks=" .. tostring(TICKS) .. " out=" .. OUT_ROOT)
