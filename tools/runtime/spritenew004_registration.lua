-- SPRITE-NEW-BEHAVIOR-REGISTRATION-001 read-only observer.
--
-- ONE QUESTION. What puts an entry into the behaviour dispatch table at
-- `actor + 0x1B0`, and why does the authored Cui actor not receive the entry a
-- comparable retail actor does?
--
-- The static answer under test: the table is not assembled at runtime. The actor
-- constructor calls 0x0800A93C(actor+0x1B0, table), and 0x0800A93C stores that
-- `table` pointer in the block's +0x08. The dispatcher 0x0800A95A then walks the
-- block as {[+0x00] current node, [+0x04] signed byte index, [+0x08] table} and
-- reads table[0] as the count and table[1+index] as an entry, calling *(entry).
--
-- So the decisive input is whatever the constructor was handed, and for the
-- map-102 record family (factory 0x08017DA3) the chain is
--
--   0x08017DA2(record) -> 0x08017C1C(.., record+0x14, ..) -> 0x080110D8(.., record+0x14)
--     -> 0x0800A93C(actor+0x1B0, record+0x14)
--
-- which makes the table the record's own inline {count, ptr[count]} array:
-- +0x14 the count and +0x18 the first (and only) entry.
--
-- This observer measures that claim instead of assuming it, on three arms:
--   * the retail canonical image (the control, and the liveness channel);
--   * SPRITE-NEW-RUNTIME-001's image, whose new record at 0x08801F38 carries the
--     donor's +0x18 unchanged (0x08078438);
--   * the same image with that one word repointed at the record's own template.
--
-- Its channels are the installer 0x0800A93C, the dispatcher's own table-entry
-- load 0x0800A9A4 (which reaches BOTH behaviour classes, so the authored actor is
-- seen whatever class its entry names), the class-A behaviour object 0x0800A7C0,
-- the map-102 record factory 0x08017DA2 and the registry return 0x08017DB0, plus
-- a per-word movement window over every actor the dispatch reached and every
-- class-A behaviour object it built.
--
-- Read-only: it reads registers and emulated memory, writes host files only, and
-- the only emulated state it changes is the controller input register through
-- mGBA's own emu:setKeys on a named schedule.
--
-- Environment (the SPRITE-NEW launcher's own names, reused deliberately):
--   SPRITENEW001_OUT_ROOT    where outputs go
--   SPRITENEW001_STRUCTURE   the new character structure's ROM address
--   SPRITENEW001_SPRITE_ID   the new sprite id
--   SPRITENEW001_SCRIPT      a key schedule name, see SCHEDULES
--   SPRITENEW001_TICKS       frames to observe before finishing

local OUT_ROOT = os.getenv("SPRITENEW001_OUT_ROOT") or "spritenew004/out"
local STRUCTURE = tonumber(os.getenv("SPRITENEW001_STRUCTURE") or "0x088005B4")
local NEW_SPRITE_ID = tonumber(os.getenv("SPRITENEW001_SPRITE_ID") or "307")
local SCRIPT = os.getenv("SPRITENEW001_SCRIPT") or "menu"
local TICKS = tonumber(os.getenv("SPRITENEW001_TICKS") or "1800")

local ACTIVE_MAP_PTR = 0x03001980
local MAP_ENTRY_BASE = 0x0808E2E0
local MAP_ENTRY_SIZE = 0x38
local MAP_ENTRY_COUNT = 452

-- The block installer, reached from every actor constructor.
local INSTALLER = 0x0800A93C
-- The object the class-A behaviour constructor allocated: r4 = object, r5 = the
-- entry. Reached one instruction after the constructor's entry 0x0800A7A0.
local HANDLER_A_ALLOCATED = 0x0800A7C0
-- The instruction inside the dispatcher that has just loaded the table entry.
local DISPATCH_ENTRY = 0x0800A9A4
-- The map-102 record family's factory, and the registry return inside it.
local FACTORY_ENTRY = 0x08017DA2
local FACTORY_RESOLVED = 0x08017DB0

local BLOCK_FIELD = 0x1B0          -- actor + 0x1B0 is the dispatch block
local BLOCK_TABLE_FIELD = 0x08
local MAX_ENTRIES = 24
-- Record families seen in this corpus: family B (factory 0x08017DA3) keeps its
-- {count, ptr} array at +0x14; the 0x0800FD55 family keeps it at +0x18.
local TABLE_OFFSETS = { 0x14, 0x18 }

local RECORD_SPRITE_FIELD = 0x10

local SAMPLE_STRIDE = 4

local K = {
    A = 0x0001, B = 0x0002, SELECT = 0x0004, START = 0x0008,
    RIGHT = 0x0010, LEFT = 0x0020, UP = 0x0040, DOWN = 0x0080,
    R = 0x0100, L = 0x0200,
}
local HOLD = 6
local SCHEDULES = {
    -- The schedule SPRITE-NEW-RUNTIME-001 and SPRITE-NEW-RECORD-RUN-001 used to
    -- load the saved game unattended and reach map 102.
    menu = { { 180, K.START }, { 420, K.A }, { 560, K.A }, { 700, K.A }, { 840, K.A } },
    human = {},
    boot = { { 180, K.START } },
}

assert(emu ~= nil, "mGBA did not attach the emulation core")
local code = emu:getGameCode()
assert(code == "BG3E" or code == "AGB-BG3E", "unexpected game code: " .. tostring(code))

local function hex(v)
    if v == nil then return "?" end
    return string.format("0x%08X", v)
end

local function safe(fn, ...)
    local ok, value = pcall(fn, ...)
    if ok then return value end
    return nil
end

local function r8(a) return tonumber(safe(emu.read8, emu, a)) end
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
    if entry == nil or entry < MAP_ENTRY_BASE then return nil end
    local offset = entry - MAP_ENTRY_BASE
    if offset % MAP_ENTRY_SIZE ~= 0 then return nil end
    local index = math.floor(offset / MAP_ENTRY_SIZE)
    if index < 0 or index >= MAP_ENTRY_COUNT then return nil end
    return index
end

local frame = 0

local function open_log(name, header)
    local file = assert(io.open(OUT_ROOT .. "/" .. name, "w"), "cannot open " .. name)
    for _, line in ipairs(header) do
        file:write(line .. "\n")
    end
    file:flush()
    return file
end

-- --- the movement instrument -------------------------------------------------
-- Registered actors and behaviour objects are sampled every SAMPLE_STRIDE frames
-- and reported as per-word min/max, so "does it move" is a question about bytes.

local ACTOR_WINDOW_START = 0x08
local ACTOR_WINDOW_WORDS = 16
local ACTOR_EXTRA = { 0x1A0, 0x1A4, 0x1A8, 0x1AC }
local OBJECT_WINDOW_START = 0x08
local OBJECT_WINDOW_WORDS = 16

local samples = {}
local sample_order = {}

local function register_sample(kind, address, record, sprite, note)
    if address == nil or samples[address] then return end
    local words = {}
    local offsets = {}
    if kind == "behaviour" then
        for i = 0, OBJECT_WINDOW_WORDS - 1 do
            offsets[#offsets + 1] = OBJECT_WINDOW_START + 4 * i
        end
    else
        for i = 0, ACTOR_WINDOW_WORDS - 1 do
            offsets[#offsets + 1] = ACTOR_WINDOW_START + 4 * i
        end
        for _, offset in ipairs(ACTOR_EXTRA) do
            offsets[#offsets + 1] = offset
        end
    end
    for i = 1, #offsets do
        words[i] = { offset = offsets[i], address = address + offsets[i],
                     first = nil, last = nil, min = nil, max = nil }
    end
    local s = { kind = kind, address = address, record = record, sprite = sprite,
                note = note, words = words, samples = 0 }
    samples[address] = s
    sample_order[#sample_order + 1] = s
end

local function sample_all()
    for _, s in ipairs(sample_order) do
        s.samples = s.samples + 1
        for i = 1, #s.words do
            local w = s.words[i]
            local v = r32(w.address)
            if v then
                if w.first == nil then w.first = v end
                w.last = v
                if w.min == nil or v < w.min then w.min = v end
                if w.max == nil or v > w.max then w.max = v end
            end
        end
    end
end

-- --- error channel ------------------------------------------------------------
-- A breakpoint callback that raises is swallowed by the emulator and looks
-- exactly like a site that never fired. Every callback below is therefore run
-- under pcall and a failure is written to error.txt with its message.

local error_file = open_log("error.txt", {
    "# any error raised inside a breakpoint callback, with the channel that raised it",
})

local function guarded(tag, body)
    return function(info)
        local ok, err = pcall(body, info)
        if not ok then
            error_file:write(tag .. ": " .. tostring(err) .. "\n")
            error_file:flush()
        end
    end
end

-- --- 0. the block installer --------------------------------------------------

local installer_file = open_log("installer.txt", {
    "# 0x0800A93C(block, table): r0 = block, r1 = table",
    "# block is actor+0x1B0 for the authored class and actor+0x22C for the",
    "# 0x0800FD55 placement class, so the record is read as table-0x14 and table-0x18",
    "# frame block actor table count record14 sprite14 record18 sprite18 map",
})
local installer_seen = {}

safe(emu.setBreakpoint, emu, guarded("installer", function(_info)
    local block = reg("r0")
    local tbl = reg("r1")
    if block == nil or tbl == nil or installer_seen[block] then return end
    installer_seen[block] = true
    local actor = block - BLOCK_FIELD
    local count = r32(tbl)
    local record14, record18 = tbl - 0x14, tbl - 0x18
    installer_file:write(string.format(
        "%d %s %s %s %s %s %d %s %d %s\n", frame, hex(block), hex(actor),
        hex(tbl), tostring(count), hex(record14),
        r32(record14 + RECORD_SPRITE_FIELD) or -1, hex(record18),
        r32(record18 + RECORD_SPRITE_FIELD) or -1,
        tostring(map_index())))
    installer_file:flush()
    console:log("SPRITENEW004 installer block=" .. hex(block) .. " table=" ..
        hex(tbl) .. " count=" .. tostring(count) .. " frame=" .. tostring(frame))
end), INSTALLER)

-- A record whose +0x00 is a Thumb code pointer and whose +0x10 is a plausible
-- sprite id is the record a table belongs to; the family is then named by which
-- offset reproduces the table address. The parameter is NOT called `table`:
-- shadowing the Lua library of that name inside a breakpoint callback turns
-- `table.concat` into an index of a number, and the emulator swallows the error,
-- so the channel looks like a site that never fired.
local function record_for_table(tbl)
    if tbl == nil then return nil, nil end
    for _, offset in ipairs(TABLE_OFFSETS) do
        local candidate = tbl - offset
        local lead = r32(candidate)
        local candidate_sprite = r32(candidate + RECORD_SPRITE_FIELD)
        if lead ~= nil and lead >= 0x08000000 and lead < 0x08800000
           and lead % 2 == 1 and candidate_sprite ~= nil
           and candidate_sprite > 0 and candidate_sprite < 4096 then
            return candidate, candidate_sprite
        end
    end
    return nil, nil
end

-- --- 1. the dispatcher's table-entry site ------------------------------------
-- Arm this again on purpose: SPRITE-NEW-RECORD-RUN-001 reported it silent while
-- the same run's handler breakpoint fired from a return address inside this very
-- routine, which is an instrument contradiction worth re-measuring. It fires
-- here, and it is also the channel that reaches BOTH behaviour classes, so it is
-- where an actor's movement sample is registered.

local dispatch_file = open_log("dispatch.txt", {
    "# 0x0800A9A4: r4 = block, r0 = the table entry just loaded",
    "# frame block actor entry [entry] table count entries record sprite map",
})
local dispatch_seen = {}
local dispatch_hits = 0
local dispatch_last_frame = -1
local dispatch_frames = 0

safe(emu.setBreakpoint, emu, guarded("dispatch", function(_info)
    dispatch_hits = dispatch_hits + 1
    local entry = reg("r0")
    local block = reg("r4")
    if entry == nil or block == nil then return end
    if frame ~= dispatch_last_frame then
        dispatch_last_frame = frame
        dispatch_frames = dispatch_frames + 1
    end
    if dispatch_seen[block] then return end
    dispatch_seen[block] = true
    local tbl = r32(block + BLOCK_TABLE_FIELD)
    local count = tbl and r32(tbl) or nil
    local parts = {}
    if count and count >= 0 and count <= MAX_ENTRIES then
        for i = 0, count - 1 do
            parts[#parts + 1] = hex(r32(tbl + 4 + 4 * i))
        end
    end
    local record, sprite = nil, nil
    if tbl then
        record, sprite = record_for_table(tbl)
    end
    -- Built by concatenation rather than string.format: a formatting fault in a
    -- callback is swallowed by the emulator and is indistinguishable from a site
    -- that never fired, which is the failure this channel exists to avoid.
    dispatch_file:write(tostring(frame) .. " " .. hex(block) .. " " ..
        hex(block - BLOCK_FIELD) .. " " .. hex(entry) .. " " .. hex(r32(entry)) ..
        " " .. hex(tbl) .. " " .. tostring(count) .. " [" ..
        table.concat(parts, " ") .. "] " .. hex(record) .. " " ..
        tostring(sprite) .. " " .. tostring(map_index()) .. "\n")
    dispatch_file:flush()
    register_sample("actor", block - BLOCK_FIELD, record, sprite, "dispatch")
end), DISPATCH_ENTRY)

-- --- 2. the map-102 record family's factory ----------------------------------

local factory_file = open_log("factory.txt", {
    "# 0x08017DA2: r0 = the record, r1 = slot index, lr = caller",
    "# frame record index sprite caller count(+0x14) entry(+0x18) map",
})
local factory_seen = {}

safe(emu.setBreakpoint, emu, guarded("factory", function(_info)
    local record = reg("r0")
    local index = reg("r1")
    local caller = reg("lr")
    if record == nil or factory_seen[record] then return end
    factory_seen[record] = true
    factory_file:write(string.format("%d %s %s %d %s %s %s %s\n", frame,
        hex(record), tostring(index),
        r32(record + RECORD_SPRITE_FIELD) or -1, hex(caller),
        hex(r32(record + 0x14)), hex(r32(record + 0x18)), tostring(map_index())))
    factory_file:flush()
end), FACTORY_ENTRY)

local resolution_file = open_log("resolutions.txt", {
    "# 0x08017DB0: r0 = resolved structure, r4 = the record",
    "# frame record sprite structure is_new map",
})
local resolution_seen = {}

safe(emu.setBreakpoint, emu, guarded("resolved", function(_info)
    local structure = reg("r0")
    local record = reg("r4")
    if record == nil then return end
    local key = string.format("%s:%s", hex(record), hex(structure))
    if resolution_seen[key] then return end
    resolution_seen[key] = true
    local sprite = r32(record + RECORD_SPRITE_FIELD)
    resolution_file:write(string.format("%d %s %s %s %s %s\n", frame, hex(record),
        tostring(sprite), hex(structure), tostring(structure == STRUCTURE),
        tostring(map_index())))
    resolution_file:flush()
end), FACTORY_RESOLVED)

-- --- 3. the class-A behaviour object -------------------------------------------
-- 0x0800A7C0 is one instruction after the class-A constructor's entry, so a row
-- here is the engine's own statement that it built a walking-class behaviour
-- object out of the entry the dispatcher handed over. A breakpoint on the two
-- constructor ENTRIES (0x0800A7A0, 0x0800A222) is deliberately NOT armed: on
-- this build those two addresses report no hit while 0x0800A7C0, 0x0800A93C and
-- 0x0800A9A4 all fire, which is an instrument anomaly (see the record). The
-- dispatcher channel above reaches both classes regardless of it.

local allocated_file = open_log("allocated.txt", {
    "# 0x0800A7C0: r4 = the freshly allocated behaviour object, r5 = its entry",
    "# frame object passed passed-0x1C sprite map",
})
local allocated_seen = {}

safe(emu.setBreakpoint, emu, guarded("allocated", function(_info)
    local object = reg("r4")
    local passed = reg("r5")
    if object == nil or passed == nil or allocated_seen[object] then return end
    allocated_seen[object] = true
    local record = passed - 0x1C
    local sprite = r32(record + RECORD_SPRITE_FIELD)
    allocated_file:write(string.format("%d %s %s %s %d %s\n", frame, hex(object),
        hex(passed), hex(record), sprite or -1, tostring(map_index())))
    allocated_file:flush()
    register_sample("behaviour", object, record, sprite, "allocated")
end), HANDLER_A_ALLOCATED)

-- --- reporting ---------------------------------------------------------------

local function count_keys(t)
    local n = 0
    for _ in pairs(t) do n = n + 1 end
    return n
end

local function write_state(path, label)
    local file = assert(io.open(path, "w"), "cannot open " .. path)
    file:write("label=" .. label .. "\n")
    file:write("frame=" .. tostring(frame) .. "\n")
    file:write("game_code=" .. tostring(code) .. "\n")
    file:write("rom_size=" .. tostring(safe(emu.romSize, emu)) .. "\n")
    file:write(string.format("new_structure=%s\n", hex(STRUCTURE)))
    file:write(string.format("new_sprite_id=%d\n", NEW_SPRITE_ID))
    file:write(string.format("active_map_ptr=%s\n", hex(r32(ACTIVE_MAP_PTR))))
    file:write(string.format("map_index=%s\n", tostring(map_index())))
    file:write(string.format("installer_blocks=%d\n", count_keys(installer_seen)))
    file:write(string.format("dispatch_blocks=%d\n", count_keys(dispatch_seen)))
    file:write(string.format("dispatch_hits=%d\n", dispatch_hits))
    file:write(string.format("dispatch_frames=%d\n", dispatch_frames))
    file:write(string.format("factory_records=%d\n", count_keys(factory_seen)))
    file:write(string.format("resolutions=%d\n", count_keys(resolution_seen)))
    file:write(string.format("samples=%d\n", #sample_order))
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
    if finished then return end
    frame = frame + 1
    if scheduled[frame] ~= nil then emu:setKeys(scheduled[frame]) end
    if frame % SAMPLE_STRIDE == 0 then sample_all() end
    if frame % 600 == 0 then
        emu:screenshot(string.format("%s/shot-%05d.png", OUT_ROOT, frame))
    end

    if frame >= TICKS then
        finished = true

        local movement = assert(io.open(OUT_ROOT .. "/movement.txt", "w"))
        movement:write("# every actor and behaviour object the engine dispatched to,\n")
        movement:write("# first/last are the sampled values at the start and end of the window;\n")
        movement:write("# min/max are over every sample and are polluted once the object's memory\n")
        movement:write("# is reused, so first->last is the movement measurement\n")
        for _, s in ipairs(sample_order) do
            local changed = {}
            for i = 1, #s.words do
                local w = s.words[i]
                if w.min and w.max and w.max ~= w.min then
                    changed[#changed + 1] = string.format("+0x%03X:%s->%s",
                        w.offset, hex(w.first), hex(w.last))
                end
            end
            movement:write(string.format(
                "kind=%s address=%s record=%s sprite=%s tag=%s samples=%d changed=%s\n",
                s.kind, hex(s.address), hex(s.record), tostring(s.sprite),
                s.note or "-", s.samples,
                (#changed == 0 and "NONE" or table.concat(changed, " "))))
        end
        movement:close()

        local summary = assert(io.open(OUT_ROOT .. "/hits.txt", "w"))
        summary:write(string.format("installer_blocks=%d\n", count_keys(installer_seen)))
        summary:write(string.format("dispatch_blocks=%d\n", count_keys(dispatch_seen)))
        summary:write(string.format("dispatch_hits=%d\n", dispatch_hits))
        summary:write(string.format("dispatch_frames=%d\n", dispatch_frames))
        summary:write(string.format("factory_records=%d\n", count_keys(factory_seen)))
        summary:write(string.format("resolutions=%d\n", count_keys(resolution_seen)))
        summary:write(string.format("behaviour_objects=%d\n", count_keys(allocated_seen)))
        summary:write(string.format("samples=%d\n", #sample_order))
        summary:write(string.format("final_map_index=%s\n", tostring(map_index())))
        summary:close()

        write_state(OUT_ROOT .. "/state-final.txt", SCRIPT)

        installer_file:close()
        dispatch_file:close()
        factory_file:close()
        resolution_file:close()
        allocated_file:close()
        error_file:close()

        local marker = assert(io.open(OUT_ROOT .. "/done.txt", "w"))
        marker:write("done\n")
        marker:close()
        callbacks:remove(callback_id)
    end
end)

local marker = assert(io.open(OUT_ROOT .. "/armed.txt", "w"))
marker:write("armed\n")
marker:close()
console:log("SPRITENEW004 observer armed: script=" .. SCRIPT ..
    " structure=" .. hex(STRUCTURE) .. " sprite=" .. tostring(NEW_SPRITE_ID) ..
    " ticks=" .. tostring(TICKS) .. " out=" .. OUT_ROOT)
