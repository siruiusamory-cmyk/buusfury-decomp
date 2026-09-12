-- TEXT-HANDLE-001: catch the producer of the packed compressed-text handle
-- that the engine consumes from runtime object +0x04.
--
-- Read-only with respect to emulated memory and input: this file writes no
-- emulated memory and presses no keys, so the read-only observer guarantee
-- enforced by tests/unit/test_mgba_capture.py stays true. Breakpoints and
-- watchpoints stop and resume the core; they do not modify it.
--
-- WHY THIS SHAPE. The ticket's phase plan allows a two-pass experiment (find
-- the object in pass A, arm a watch on it in pass B) if the tooling cannot arm
-- a watch dynamically. It can: rom011_dev_range.lua:92 installs a range
-- watchpoint from inside a live frame callback. So this is ONE pass. The
-- consumer breakpoint latches the object, and the SAME callback arms the write
-- watch on that object's +0x04. Pointer stability is therefore never assumed;
-- it is measured, and reported per capture.
--
-- STATIC FACTS RE-VERIFIED THIS PASS against the canonical image
-- (940ad5f0...), because the ticket requires re-verifying instruction
-- boundaries rather than trusting the addresses it carries:
--
--   0x08012230  push {..,lr}
--   0x08012232  mov  r5,r1          <- THE OBJECT ARRIVES IN r1, NOT r0
--   0x08012240  ldr  r0,[r5,#0x04]  <- reads the packed handle
--   0x08012242  ldr  r1,=0x087B5B64 <- the compressed-text pointer table
--   0x08012248  ldr  r0,[r1,r0]     <- table[selector]
--
--   0x080122B4  push {..,lr}
--   0x080122BA  mov  r4,r1          <- likewise r1
--   0x080122C6  ldr  r0,[r4,#0x04]
--   0x080122C8  ldr  r1,=0x087B5B64
--
-- An observer that latched r0 at these sites would have captured garbage. The
-- selector scaling in the ticket is corroborated in the same window: the
-- halfword pair 0x0680,0x0E00 at +0x14 is lsls #26 / lsrs #24, i.e. mask to
-- six bits and multiply by four -- exactly (value & 0x3F) * 4.
--
-- RULED OUT, so a later reader does not re-walk it: 0x08012394 is a
-- `str r0,[r4,#0x04]` in the constructor at 0x0801236E, but that object's
-- +0x04 holds a POINTER -- it is dereferenced at 0x080123A6 and then indexed
-- [r0,#0x60]. It is a different object family, not this handle's writer.
--
-- CHANNELS, kept separate so no one can be read as another:
--
--   A - CONSUMER (execution). Breakpoints at both consumer entries. Latch the
--       object from r1, record the handle it is about to consume, decode it.
--       This proves liveness of the text path itself.
--
--   B - PRODUCER (memory write). A write watchpoint armed dynamically on the
--       latched object's +0x04. Records writer PC, LR, SP, r0-r12, the old and
--       new values, and a stack window. This is the ticket's actual target.
--
--   C - LIVENESS (execution, positive control). The shared interpreter at
--       0x08004038. Per the mgba-runtime skill this site is known to fire only
--       rarely, so a low count proves breakpoint INSTALLATION and nothing more.
--       A silent A plus a firing C is a real negative; silent A and silent C
--       proves nothing and must be reported as "instrument unproven".

local CONSUMERS   = { 0x08012230, 0x080122B4 }
local INTERPRETER = 0x08004038

local TABLE_BASE  = 0x087B5B64   -- compressed-text pointer table
local TABLE_COUNT = 7            -- structural container gate; do NOT widen

local FIELD_OFFSET = 0x04

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = (os.getenv("TEXTHANDLE001_OUT")
    or (exp_dir .. "text-handle-001.jsonl"))

assert(emu ~= nil, "mGBA did not attach the emulation core")
assert(emu.setBreakpoint and emu.clearBreakpoint,
    "requires the mGBA 0.11 scripted-breakpoint API")
assert(emu.setRangeWatchpoint,
    "requires emu:setRangeWatchpoint; a frame poller cannot evidence the " ..
    "exact writer and must not be substituted for it")

-- The game code is BARE on the 0.11 dev build, but accept both spellings.
local game_code = emu:getGameCode()
assert(game_code == "BG3E" or game_code == "AGB-BG3E",
    "unexpected game code: " .. tostring(game_code))
assert(emu:romSize() == 8388608, "unexpected ROM size")

-- Resolve the WRITE watchpoint constant by NAME rather than assuming a
-- spelling, and fail loudly if this build has no write type at all.
local WRITE_TYPE = nil
local write_type_name = nil
do
    local t = (C and C.WATCHPOINT_TYPE) or nil
    assert(t ~= nil, "C.WATCHPOINT_TYPE is not exposed by this build")
    for _, name in ipairs({ "WRITE", "RW", "WRITE_CHANGE", "READ_WRITE" }) do
        if t[name] ~= nil then
            WRITE_TYPE = t[name]
            write_type_name = name
            break
        end
    end
    assert(WRITE_TYPE ~= nil,
        "no write watchpoint type found in C.WATCHPOINT_TYPE")
end

local file = assert(io.open(log_path, "w"),
    "cannot open output: " .. tostring(log_path))

local frames = 0
local rows = 0
local consumer_hits = 0
local writer_hits = 0
local liveness = 0

local watch_id = nil
local watched_object = nil

local function safe32(addr)
    local ok, v = pcall(function() return emu:read32(addr) end)
    if ok and v then return v end
    return nil
end

local function jnum(v)
    if v == nil then return "null" end
    return string.format("%d", v)
end

local function jhex(v)
    if v == nil then return "null" end
    return string.format('"0x%08X"', v)
end

local function jstr(s)
    if s == nil then return "null" end
    return '"' .. tostring(s):gsub('\\', '\\\\'):gsub('"', '\\"') .. '"'
end

--: Decode the packed u32 exactly as the ticket's established layout states.
--: Returned as raw components plus their byte-scaled forms, so a later reader
--: never has to re-apply the shifts and can spot a layout violation.
local function decode_handle(v)
    if v == nil then return nil end
    local selector = v & 0x3F
    local start_units = (v >> 6) & 0x7FFF
    local length_units = (v >> 21) & 0x7FF
    local d = {}
    d.selector = selector
    d.table_byte_offset = selector * 4
    d.decoded_start = start_units * 2
    d.decoded_length = length_units * 2
    d.decoded_end = d.decoded_start + d.decoded_length
    d.in_gate = (selector < TABLE_COUNT)
    if d.in_gate then
        d.container = safe32(TABLE_BASE + selector * 4)
    else
        d.container = nil
    end
    return d
end

local function handle_json(d)
    if d == nil then return "null" end
    return string.format(
        '{"selector":%s,"table_byte_offset":%s,"container":%s,' ..
        '"decoded_start":%s,"decoded_length":%s,"decoded_end":%s,' ..
        '"within_container_gate":%s}',
        jnum(d.selector), jnum(d.table_byte_offset), jhex(d.container),
        jnum(d.decoded_start), jnum(d.decoded_length), jnum(d.decoded_end),
        tostring(d.in_gate))
end

local function registers_json()
    local parts = {}
    for i = 0, 12 do
        local ok, v = pcall(function() return emu:readRegister("r" .. i) end)
        parts[#parts + 1] = string.format('"r%d":%s', i,
            (ok and v) and string.format('"0x%08X"', v) or "null")
    end
    for _, name in ipairs({ "sp", "lr", "pc", "cpsr" }) do
        local ok, v = pcall(function() return emu:readRegister(name) end)
        parts[#parts + 1] = string.format('"%s":%s', name,
            (ok and v) and string.format('"0x%08X"', v) or "null")
    end
    return "{" .. table.concat(parts, ",") .. "}"
end

--: A small stack window, so the caller chain is recoverable offline even if
--: LR alone turns out to be a veneer return.
local function stack_json(words)
    local ok, sp = pcall(function() return emu:readRegister("sp") end)
    if not (ok and sp) then return "null" end
    local parts = {}
    for k = 0, words - 1 do
        local v = safe32(sp + 4 * k)
        parts[#parts + 1] = (v ~= nil) and string.format('"0x%08X"', v) or "null"
    end
    return "[" .. table.concat(parts, ",") .. "]"
end

--: Instruction halfwords around a PC, so the writer's exact encoding is in the
--: evidence and does not have to be re-derived from the image by hand.
local function around_json(pc, halfwords)
    if pc == nil then return "null" end
    local parts = {}
    local start = pc - (halfwords // 2) * 2
    for k = 0, halfwords - 1 do
        local a = start + 2 * k
        local ok, v = pcall(function() return emu:read16(a) end)
        parts[#parts + 1] = (ok and v) and string.format('"0x%04X"', v) or "null"
    end
    return string.format('{"start":"0x%08X","halfwords":[%s]}',
        start, table.concat(parts, ","))
end

local function object_json(obj, words)
    if obj == nil then return "null" end
    local parts = {}
    for k = 0, words - 1 do
        local v = safe32(obj + 4 * k)
        parts[#parts + 1] = (v ~= nil) and string.format('"0x%08X"', v) or "null"
    end
    return "[" .. table.concat(parts, ",") .. "]"
end

local function emit(fields)
    file:write("{" .. table.concat(fields, ",") .. "}\n")
    file:flush()
    rows = rows + 1
end

emit({
    '"event":"ARMED"',
    '"frame":' .. jnum(0),
    '"write_watchpoint_type":' .. jstr(write_type_name),
    '"consumers":["0x08012230","0x080122B4"]',
    '"table_base":"0x087B5B64"',
    '"table_count":' .. jnum(TABLE_COUNT),
    '"note":' .. jstr("object latched from r1 at consumer entry, verified " ..
        "statically: 0x08012232 mov r5,r1 / 0x080122BA mov r4,r1"),
})

--: CHANNEL B. Armed dynamically once an object is known. Rearmed whenever the
--: consumer reports a DIFFERENT object, so a per-message object is followed
--: rather than assumed stable.
local function arm_write_watch(obj)
    if watch_id ~= nil then
        pcall(function() emu:clearBreakpoint(watch_id) end)
        watch_id = nil
    end
    local lo = obj + FIELD_OFFSET
    local id = emu:setRangeWatchpoint(function(info)
        writer_hits = writer_hits + 1
        local pc = nil
        local ok, v = pcall(function() return emu:readRegister("pc") end)
        if ok then pc = v end
        local newv = info and info.newValue or safe32(lo)
        local oldv = info and info.oldValue or nil
        emit({
            '"event":"FIELD-WRITE"',
            '"frame":' .. jnum(frames),
            '"hit":' .. jnum(writer_hits),
            '"object":' .. jhex(obj),
            '"field_address":' .. jhex(lo),
            '"old_value":' .. jhex(oldv),
            '"new_value":' .. jhex(newv),
            '"decoded":' .. handle_json(decode_handle(newv)),
            '"width":' .. jnum(info and info.width or nil),
            '"access_type":' .. jnum(info and info.accessType or nil),
            '"registers":' .. registers_json(),
            '"stack":' .. stack_json(16),
            '"around_pc":' .. around_json(pc, 12),
            '"object_words":' .. object_json(obj, 9),
        })
    end, lo, lo + 4, WRITE_TYPE)
    if id ~= nil and id >= 0 then
        watch_id = id
        watched_object = obj
        emit({
            '"event":"WATCH-ARMED"',
            '"frame":' .. jnum(frames),
            '"object":' .. jhex(obj),
            '"field_address":' .. jhex(lo),
            '"watch_id":' .. jnum(id),
        })
    else
        emit({
            '"event":"WATCH-FAILED"',
            '"frame":' .. jnum(frames),
            '"object":' .. jhex(obj),
            '"note":' .. jstr("setRangeWatchpoint refused the range"),
        })
    end
end

--: CHANNEL A. Both consumers, object from r1.
local function on_consumer(site)
    return function(info)
        consumer_hits = consumer_hits + 1
        local ok, obj = pcall(function() return emu:readRegister("r1") end)
        if not ok then obj = nil end
        local handle = (obj ~= nil) and safe32(obj + FIELD_OFFSET) or nil
        emit({
            '"event":"CONSUMER"',
            '"frame":' .. jnum(frames),
            '"hit":' .. jnum(consumer_hits),
            '"site":' .. jhex(site),
            '"object":' .. jhex(obj),
            '"handle":' .. jhex(handle),
            '"decoded":' .. handle_json(decode_handle(handle)),
            '"registers":' .. registers_json(),
            '"stack":' .. stack_json(12),
            '"object_words":' .. object_json(obj, 9),
        })
        --: Arm, or RE-arm on a different object. Pointer stability is measured,
        --: never assumed: every change is recorded as its own WATCH-ARMED row.
        if obj ~= nil and obj >= 0x02000000 and obj < 0x03008000 then
            if watched_object ~= obj then
                arm_write_watch(obj)
            end
        end
    end
end

for _, site in ipairs(CONSUMERS) do
    local id = emu:setBreakpoint(on_consumer(site), site)
    assert(id ~= nil and id >= 0,
        string.format("consumer breakpoint install failed at 0x%08X", site))
end

--: CHANNEL C. Installation control only; low counts are a known property.
emu:setBreakpoint(function(info)
    liveness = liveness + 1
    if liveness <= 3 or liveness % 1000 == 0 then
        emit({
            '"event":"LIVENESS"',
            '"frame":' .. jnum(frames),
            '"count":' .. jnum(liveness),
            '"site":"0x08004038"',
        })
    end
end, INTERPRETER)

callbacks:add("frame", function()
    frames = frames + 1
    --: Heartbeat, so "the observer stopped" and "the observer ran and saw
    --: nothing" stay distinguishable -- they are different failures.
    if frames % 1800 == 0 then
        emit({
            '"event":"HEARTBEAT"',
            '"frame":' .. jnum(frames),
            '"consumer_hits":' .. jnum(consumer_hits),
            '"writer_hits":' .. jnum(writer_hits),
            '"liveness":' .. jnum(liveness),
            '"watched_object":' .. jhex(watched_object),
        })
    end
end)

--: The launcher waits on this marker before loading the savestate.
local marker = assert(io.open(done_path, "w"), "cannot open marker")
marker:write("armed\n")
marker:close()

print([[TEXT-HANDLE-001 armed: 2 consumers + dynamic write watch on obj+0x04]])
print([[log: ]] .. log_path)
