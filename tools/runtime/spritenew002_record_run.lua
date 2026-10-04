-- SPRITE-NEW-RECORD-RUN-001 read-only observer.
--
-- WHAT IT DOES NOT DO. It never writes emulated memory and never touches a ROM or
-- a save on disk. The only emulated state it changes is the controller input
-- register, through mGBA's own `emu:setKeys`, and only on a named schedule. Every
-- output is a host file inside the run directory.
--
-- WHY THIS OBSERVER EXISTS. SPRITE-NEW-RUNTIME-001 put a new sibling-family
-- record on map 102 and measured that the engine built the visible actor - the
-- sprite resolved and drew - while the actor never moved. The retail records of
-- the same family on the same map do move, and the moving object was caught at
-- 0x0800A7C0 with r5 holding a pointer that is `record + 0x1C`, not the record
-- start the map object array named. That is a discrepancy between the array's own
-- pointer and the pointer the engine hands the behaviour constructor, and only
-- observation can say which of these it means:
--
--   * the engine computes `record + 0x1C` itself, in which case the 0x10 bytes
--     that follow a 0x1C-byte record are what the behaviour is made of, and a
--     record is self-contained only if its own following bytes are present; or
--   * the pointer comes from a DIFFERENT walker, over a different base, that
--     reaches a record the object array never named - in which case an authored
--     record appended to the object array alone would never be visited.
--
-- So this observer records every end of the dispatch without interpreting any of
-- them, and writes each finding to disk the moment it is made rather than at the
-- end of the budget:
--
--   1. the map object loop, at 0x08008CB0, where r6 is the record pointer the
--      array named and r5 is its slot index - with the record's own words at
--      +0x00, +0x04, +0x18 and +0x1C;
--   2. the sibling factory entry 0x08017DA2, and the instruction after it calls
--      the registry accessor (0x08017DB0), where r0 is the character structure
--      the engine resolved for that record - the identity evidence for a
--      sibling-family actor, which SPRITE-NEW-RUNTIME-001 never captured;
--   3. the behaviour constructor entry 0x0800A7A0, where r0 is the pointer the
--      engine passed and lr is the address it will return to. The caller address
--      is what identifies the dispatch site.
--   4. every MapEntry the run settles on, with +0x04 count, +0x14 array base and
--      +0x2C stream base, so the object array and the wider per-map record stream
--      can be compared as addresses rather than as stories.
--
-- It also keeps the field-window instrument from SPRITE-NEW-RUNTIME-001: it
-- samples a range of words of every behaviour object it sees and reports, per
-- word, how far it travelled, so "does this actor move" is a question about bytes
-- rather than about a picture. Sampling is every fourth frame, which is far finer
-- than the driver needs and keeps the emulator's own speed usable.
--
-- Environment (the SPRITE-NEW launcher's own names, reused deliberately so one
-- launcher serves both observers):
--   SPRITENEW001_OUT_ROOT    where outputs go
--   SPRITENEW001_STRUCTURE   the new character structure's ROM address
--   SPRITENEW001_SPRITE_ID   the new sprite id
--   SPRITENEW001_SCRIPT      a key schedule name, see SCHEDULES
--   SPRITENEW001_TICKS       frames to observe before finishing

local OUT_ROOT = os.getenv("SPRITENEW001_OUT_ROOT") or "spritenew002/out"
local STRUCTURE = tonumber(os.getenv("SPRITENEW001_STRUCTURE") or "0x088005B4")
local NEW_SPRITE_ID = tonumber(os.getenv("SPRITENEW001_SPRITE_ID") or "307")
local SCRIPT = os.getenv("SPRITENEW001_SCRIPT") or "menu"
local TICKS = tonumber(os.getenv("SPRITENEW001_TICKS") or "1500")

local ACTIVE_MAP_PTR = 0x03001980
local MAP_ENTRY_BASE = 0x0808E2E0
local MAP_ENTRY_SIZE = 0x38
local MAP_ENTRY_COUNT = 452

local MAP_OBJECT_COUNT_FIELD = 0x04
local MAP_OBJECT_ARRAY_FIELD = 0x14
local MAP_STREAM_FIELD = 0x2C

-- The map object array loop (0x08008C9E..0x08008CD6). r6 is the slot's record
-- pointer and r5 its index once 0x08008CAE has run.
local LOOP_RECORD_LOADED = 0x08008CB0
-- The sibling family's factory. 0x08017DA6 loads the record's +0x10 and
-- 0x08017DAC resolves it; 0x08017DB0 is the next instruction, with r0 holding
-- the resolved structure and r4 the record.
local FACTORY_ENTRY = 0x08017DA2
local FACTORY_RESOLVED = 0x08017DB0
-- The behaviour constructor. r0 is the pointer passed in, lr the return address.
local HANDLER_ENTRY = 0x0800A7A0
-- The instruction that observes the freshly allocated behaviour object: r4 is the
-- object and r5 the pointer the handler was given.
local HANDLER_ALLOCATED = 0x0800A7C0
-- The dispatcher that reaches the behaviour constructor. Its r0 is a per-actor
-- state block: [r0] = the current node, [r0+4] = a signed byte index, [r0+8] = a
-- pointer to a count-prefixed table of node pointers. Reading that table is what
-- turns "the engine handed over record+0x1C" into "the engine got that pointer
-- from here", which is the fact an authored record has to satisfy.
local DISPATCH_ENTRY = 0x0800A9A4
local DISPATCH_BLOCK_REGISTER = "r4"
local DISPATCH_ENTRY_REGISTER = "r0"
local DISPATCH_TABLE_FIELD = 0x08
local DISPATCH_MAX_ENTRIES = 24

local RECORD_SPRITE_FIELD = 0x10
local RECORD_PREV_FIELD = 0x18
local RECORD_BODY_FIELD = 0x1C

-- The behaviour object's live state. SPRITE-NEW-RUNTIME-001 measured the wander
-- driver at 0x0800A2A8 writing +0x10 (heading), +0x20 (target x) and +0x24
-- (target y). The window is deliberately wider than those three words: it
-- reports which words change rather than asserting which word is the position.
local BEHAVIOUR_WINDOW_START = 0x08
local BEHAVIOUR_WINDOW_WORDS = 16          -- +0x08 .. +0x47
local SAMPLE_STRIDE = 4

local K = {
    A = 0x0001, B = 0x0002, SELECT = 0x0004, START = 0x0008,
    RIGHT = 0x0010, LEFT = 0x0020, UP = 0x0040, DOWN = 0x0080,
    R = 0x0100, L = 0x0200,
}
local HOLD = 6
local SCHEDULES = {
    -- The proof schedule SPRITE-NEW-RUNTIME-001 used to load the saved game
    -- unattended, and the one scout-deriv-complete reached map 102 with.
    menu = { { 180, K.START }, { 420, K.A }, { 560, K.A }, { 700, K.A }, { 840, K.A } },
    -- Nothing is pressed; the operator plays.
    human = {},
    boot = { { 180, K.START } },
}

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
local function r16(a) return tonumber(safe(emu.read16, emu, a)) end
local function r32(a) return tonumber(safe(emu.read32, emu, a)) end

local function reg(name)
    local value = safe(emu.readRegister, emu, name)
    if value == nil then return nil end
    local n = tonumber(value)
    if n == nil and type(value) == "string" then
        n = tonumber(value, 16)
    end
    return n
end

local function map_index()
    local entry = r32(ACTIVE_MAP_PTR)
    if entry == nil or entry < MAP_ENTRY_BASE then return nil, entry end
    local offset = entry - MAP_ENTRY_BASE
    if offset % MAP_ENTRY_SIZE ~= 0 then return nil, entry end
    local index = math.floor(offset / MAP_ENTRY_SIZE)
    if index < 0 or index >= MAP_ENTRY_COUNT then return nil, entry end
    return index, entry
end

local frame = 0
local maps_seen = {}
local maps_seen_set = {}

-- --- durable log files, written as each fact is observed ---------------------

local function open_log(name, header)
    local file = assert(io.open(OUT_ROOT .. "/" .. name, "w"), "cannot open " .. name)
    for _, line in ipairs(header) do
        file:write(line .. "\n")
    end
    file:flush()
    return file
end

local slots_file = open_log("slots.txt", {
    "# the map object loop (0x08008CB0): one row per record pointer the array named",
    "# r6 = the record, r5 = its slot index",
    "# frame index record lead(+0x00) w4(+0x04) prev(+0x18) body(+0x1C) w20 w24 w28 map",
})
local factory_file = open_log("factory.txt", {
    "# the sibling factory entry 0x08017DA2: r0 = the record, r1 = slot index, lr = caller",
    "# frame record index caller calls",
})
local resolution_file = open_log("resolutions.txt", {
    "# 0x08017DB0: r0 = the character structure the engine resolved for record r4",
    "# frame record sprite_id structure is_new map",
})
local handler_file = open_log("handler.txt", {
    "# the behaviour constructor entry 0x0800A7A0: r0 = the pointer passed in,",
    "# r1 = its second argument, lr = the return address (the dispatch site)",
    "# frame passed passed_word(+0x00) second(+0x04) caller calls map",
})
local maps_file = open_log("maps.txt", {
    "# every MapEntry the run settles on, with the three fields that matter here",
    "# frame map map_entry count(+0x04) array(+0x14) stream(+0x2C)",
})

local function note_map(index, entry)
    if index == nil or maps_seen_set[index] then return end
    maps_seen_set[index] = true
    maps_seen[#maps_seen + 1] = index
    maps_file:write(string.format("%d %d %s %d %s %s\n", frame, index, hex(entry),
        r8(entry + MAP_OBJECT_COUNT_FIELD),
        hex(r32(entry + MAP_OBJECT_ARRAY_FIELD)),
        hex(r32(entry + MAP_STREAM_FIELD))))
    maps_file:flush()
    console:log("SPRITENEW002 map=" .. tostring(index) .. " entry=" .. hex(entry) ..
        " count=" .. tostring(r8(entry + MAP_OBJECT_COUNT_FIELD)) ..
        " array=" .. hex(r32(entry + MAP_OBJECT_ARRAY_FIELD)) ..
        " stream=" .. hex(r32(entry + MAP_STREAM_FIELD)))
end

-- --- 0. the dispatcher's own table, registered first ---------------------------
-- Registered before the others on purpose. mGBA reported no hit on the routine's
-- ENTRY address 0x0800A95A even when it was the first breakpoint armed, while the
-- five armed after it all produced data, and the return address of the behaviour
-- call is 0x0800A9AA - inside that routine. So the routine is entered, but not at
-- its push. This site, 0x0800A9A4, is the instruction that has just loaded the
-- table entry into r0 and is therefore on the path to the call without depending
-- on how the routine was entered.

local dispatch_file = open_log("dispatch.txt", {
    "# the dispatcher 0x0800A95A: r0 = a per-actor state block",
    "# block  [block+0] current  [block+4] index  [block+8] table  count  entries...",
})
local dispatch_seen = {}

safe(emu.setBreakpoint, emu, function(_info)
    local entry = reg(DISPATCH_ENTRY_REGISTER)
    local block = reg(DISPATCH_BLOCK_REGISTER)
    if entry == nil or block == nil then return end
    if dispatch_seen[block] then return end
    local table = r32(block + DISPATCH_TABLE_FIELD)
    if table == nil then return end
    dispatch_seen[block] = true
    local count = r32(table)
    local parts = {}
    if count and count >= 0 and count <= DISPATCH_MAX_ENTRIES then
        for i = 0, count - 1 do
            parts[#parts + 1] = hex(r32(table + 4 + 4 * i))
        end
    end
    dispatch_file:write(string.format(
        "frame=%d entry=%s block=%s current=%s index=%s table=%s count=%s entries=%s\n",
        frame, hex(entry), hex(block), hex(r32(block)), tostring(r8(block + 4)),
        hex(table), tostring(count), table.concat(parts, " ")))
    dispatch_file:flush()
    console:log("SPRITENEW002 dispatcher entry=" .. hex(entry) .. " block=" ..
        hex(block) .. " table=" .. hex(table) .. " count=" .. tostring(count) ..
        " frame=" .. tostring(frame))
end, DISPATCH_ENTRY)


-- --- 1. the map object loop -------------------------------------------------

local slots = {}
local slot_order = {}

safe(emu.setBreakpoint, emu, function(_info)
    local record = reg("r6")
    local index = reg("r5")
    if record == nil then return end
    if slots[record] then
        slots[record].seen = slots[record].seen + 1
        return
    end
    local s = {
        record = record, index = index, frame = frame, map = map_index(),
        lead = r32(record), word4 = r32(record + 4),
        prev = r32(record + RECORD_PREV_FIELD),
        body = r32(record + RECORD_BODY_FIELD),
        word20 = r32(record + 0x20), word24 = r32(record + 0x24),
        word28 = r32(record + 0x28), seen = 1,
    }
    slots[record] = s
    slot_order[#slot_order + 1] = record
    slots_file:write(string.format("%d %s %s %s %s %s %s %s %s %s %s\n",
        s.frame, tostring(s.index), hex(s.record), hex(s.lead), hex(s.word4),
        hex(s.prev), hex(s.body), hex(s.word20), hex(s.word24), hex(s.word28),
        s.map and tostring(s.map) or "?"))
    slots_file:flush()
end, LOOP_RECORD_LOADED)

-- --- 2. the sibling factory -------------------------------------------------

local factory_calls = {}
local factory_order = {}
local resolutions = {}
local resolution_order = {}

safe(emu.setBreakpoint, emu, function(_info)
    local record = reg("r0")
    local index = reg("r1")
    local caller = reg("lr")
    if record == nil then return end
    if not factory_calls[record] then
        factory_calls[record] = { frame = frame, record = record, index = index,
                                  caller = caller, calls = 0 }
        factory_order[#factory_order + 1] = record
        factory_file:write(string.format("%d %s %s %s 0\n",
            frame, hex(record), tostring(index), hex(caller)))
        factory_file:flush()
    end
    factory_calls[record].calls = factory_calls[record].calls + 1
end, FACTORY_ENTRY)

safe(emu.setBreakpoint, emu, function(_info)
    local structure = reg("r0")
    local record = reg("r4")
    if record == nil then return end
    local key = string.format("%s:%s", hex(record), hex(structure))
    if resolutions[key] then return end
    local sprite_id = r32(record + RECORD_SPRITE_FIELD)
    local is_new = (structure == STRUCTURE)
    resolutions[key] = { frame = frame, record = record, structure = structure,
                         sprite_id = sprite_id, is_new = is_new }
    resolution_order[#resolution_order + 1] = key
    resolution_file:write(string.format("%d %s %s %s %s %s\n", frame, hex(record),
        tostring(sprite_id), hex(structure), tostring(is_new),
        tostring((map_index()))))
    resolution_file:flush()
    console:log("SPRITENEW002 factory record=" .. hex(record) ..
        " sprite=" .. tostring(sprite_id) .. " structure=" .. hex(structure) ..
        " frame=" .. tostring(frame))
end, FACTORY_RESOLVED)

-- --- 3. the behaviour constructor and its object ----------------------------

local handler_calls = {}
local handler_order = {}

safe(emu.setBreakpoint, emu, function(_info)
    local passed = reg("r0")
    local second = reg("r1")
    local caller = reg("lr")
    if passed == nil then return end
    if not handler_calls[passed] then
        local h = { frame = frame, passed = passed, second = second,
                    caller = caller, calls = 0, own_word = r32(passed),
                    map = map_index() }
        handler_calls[passed] = h
        handler_order[#handler_order + 1] = passed
        handler_file:write(string.format("%d %s %s %s %s 0 %s\n", h.frame,
            hex(h.passed), hex(h.own_word), hex(h.second), hex(h.caller),
            h.map and tostring(h.map) or "?"))
        handler_file:flush()
        console:log("SPRITENEW002 handler passed=" .. hex(passed) ..
            " caller=" .. hex(caller) .. " frame=" .. tostring(frame))
    end
    handler_calls[passed].calls = handler_calls[passed].calls + 1
end, HANDLER_ENTRY)

local behaviours = {}
local behaviour_seen = {}

safe(emu.setBreakpoint, emu, function(_info)
    local object = reg("r4")
    local passed = reg("r5")
    if object == nil or passed == nil or behaviour_seen[object] then return end
    behaviour_seen[object] = true
    local words = {}
    for i = 0, BEHAVIOUR_WINDOW_WORDS - 1 do
        words[i] = {
            address = object + BEHAVIOUR_WINDOW_START + 4 * i,
            first = nil, last = nil, min = nil, max = nil,
        }
    end
    behaviours[#behaviours + 1] = {
        object = object, passed = passed, record = passed - RECORD_BODY_FIELD,
        frame = frame, words = words, samples = 0,
    }
end, HANDLER_ALLOCATED)

local function sample_behaviours()    for _, b in ipairs(behaviours) do
        b.samples = b.samples + 1
        for i = 0, BEHAVIOUR_WINDOW_WORDS - 1 do
            local w = b.words[i]
            local v = r32(w.address)
            if v then
                if w.first == nil then
                    w.first, w.min, w.max = v, v, v
                else
                    if v < w.min then w.min = v end
                    if v > w.max then w.max = v end
                end
                w.last = v
            end
        end
    end
end

local function travelled(w)
    if w.min == nil then return nil end
    return w.max - w.min
end

-- --- reporting --------------------------------------------------------------

local function write_state(path, label)
    local file = assert(io.open(path, "w"), "cannot open " .. path)
    local index, entry = map_index()
    file:write("label=" .. label .. "\n")
    file:write("frame=" .. tostring(frame) .. "\n")
    file:write("game_code=" .. tostring(code) .. "\n")
    file:write("rom_size=" .. tostring(safe(emu.romSize, emu)) .. "\n")
    file:write(string.format("new_structure=%s\n", hex(STRUCTURE)))
    file:write(string.format("new_sprite_id=%d\n", NEW_SPRITE_ID))
    file:write(string.format("active_map_ptr=%s\n", hex(r32(ACTIVE_MAP_PTR))))
    file:write(string.format("map_index=%s\n", index and tostring(index) or "unknown"))
    file:write(string.format("map_entry=%s\n", hex(entry)))
    file:write(string.format("object_slots_seen=%d\n", #slot_order))
    file:write(string.format("factory_calls=%d\n", #factory_order))
    file:write(string.format("resolutions=%d\n", #resolution_order))
    file:write(string.format("handler_calls=%d\n", #handler_order))
    file:write(string.format("behaviour_objects=%d\n", #behaviours))
    file:close()
end

local schedule = SCHEDULES[SCRIPT] or {}
local scheduled = {}
for _, item in ipairs(schedule) do
    scheduled[item[1]] = item[2]
    scheduled[item[1] + HOLD] = 0
end

local callback_id
local finished = false
callback_id = callbacks:add("frame", function()
    -- The budget ends once. A frame callback that runs again after the logs are
    -- closed must be a no-op, not an error that hides the evidence already won.
    if finished then return end
    frame = frame + 1
    if scheduled[frame] ~= nil then emu:setKeys(scheduled[frame]) end

    local index, entry = map_index()
    note_map(index, entry)
    if frame % SAMPLE_STRIDE == 0 then sample_behaviours() end

    if frame % 600 == 0 then
        emu:screenshot(string.format("%s/shot-%05d.png", OUT_ROOT, frame))
    end
    if frame % 300 == 0 then
        write_state(string.format("%s/state-%06d.txt", OUT_ROOT, frame), SCRIPT)
    end

    if frame >= TICKS then
        finished = true
        write_state(OUT_ROOT .. "/state-final.txt", SCRIPT)

        local file = assert(io.open(OUT_ROOT .. "/behaviour.txt", "w"))
            file:write("# every behaviour object the constructor built, and which of its words moved\n")
        for n, b in ipairs(behaviours) do
            local moving = {}
            for i = 0, BEHAVIOUR_WINDOW_WORDS - 1 do
                local d = travelled(b.words[i])
                if d and d ~= 0 then
                    moving[#moving + 1] = string.format("+0x%02X:%s->%s(d=%s)",
                        BEHAVIOUR_WINDOW_START + 4 * i,
                        hex(b.words[i].min), hex(b.words[i].max), tostring(d))
                end
            end
            file:write(string.format(
                "behaviour_%d object=%s passed=%s implied_record=%s frame=%d samples=%d\n",
                n, hex(b.object), hex(b.passed), hex(b.record), b.frame, b.samples))
            file:write("  changed_words=" ..
                (#moving == 0 and "NONE" or table.concat(moving, " ")) .. "\n")
        end
        file:close()

        local summary = assert(io.open(OUT_ROOT .. "/hits.txt", "w"))
        summary:write(string.format("object_slots_seen=%d\n", #slot_order))
        summary:write(string.format("factory_calls=%d\n", #factory_order))
        summary:write(string.format("resolutions=%d\n", #resolution_order))
        summary:write(string.format("handler_calls=%d\n", #handler_order))
        summary:write(string.format("behaviour_objects=%d\n", #behaviours))
        summary:write(string.format("final_map_index=%s\n",
            tostring((map_index()))))
        summary:write("maps_seen=" .. table.concat(maps_seen, ",") .. "\n")
        summary:close()

        slots_file:close()
        factory_file:close()
        resolution_file:close()
        handler_file:close()
        maps_file:close()
        dispatch_file:close()

        local marker = assert(io.open(OUT_ROOT .. "/done.txt", "w"))
        marker:write("done\n")
        marker:close()
        callbacks:remove(callback_id)
    end
end)

local marker = assert(io.open(OUT_ROOT .. "/armed.txt", "w"))
marker:write("armed\n")
marker:close()
console:log("SPRITENEW002 observer armed: script=" .. SCRIPT ..
    " structure=" .. hex(STRUCTURE) .. " sprite=" .. tostring(NEW_SPRITE_ID) ..
    " ticks=" .. tostring(TICKS) .. " out=" .. OUT_ROOT)
