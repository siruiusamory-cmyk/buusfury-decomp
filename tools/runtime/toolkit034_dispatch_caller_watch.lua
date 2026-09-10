-- TOOLKIT-034: read-only causal trace for an authored death-trigger candidate.
--
-- It captures the runtime-confirmed death callback, the descriptor trampoline,
-- the authored script cursor, and the already-proven native-178 effect without
-- assigning a broader trigger semantic. It reuses start_toolkit031_session.ps1:
-- rom011_marker_path supplies completion and TOOLKIT031_OUT supplies the CSV.

local TRAMPOLINE = 0x0800421E
local INTERPRETER = 0x08004038
local NATIVE_STACK_BREAKPOINT = 0x08003CBE
local NATIVE_STACK_HANDLER_ENTRY = 0x08003CC0
local TEXT_HANDLER = 0x08003030
local ACTOR_EVENT_FACTORY = 0x0800F866
local DEATH_CALLBACK = 0x08018950
local DESTRUCTOR_FIRST_DECISION = 0x08011A38
local DESTRUCTOR_DECREMENT = 0x08011A3E
local DESTRUCTOR_DISPATCH = 0x08011A5A
local AUTHORED_DESCRIPTOR = 0x087EA420
local AUTHORED_PAYLOAD = 0x087EA428
local AUTHORED_SCRIPT_LENGTH = 11
local AUTHORED_NATIVE_CURSOR = 0x087EA431
local NATIVE_SLOT_178 = 178
local EXPECT_TEXT = 1525
local EXPECT_X = 120
local EXPECT_Y = 105
local CANONICAL_NULL_DESCRIPTOR = 0x080555A0
local CANONICAL_CONTROL_MAP = 40
local ACTIVE_MAP_PTR = 0x03001980
local MAP_ENTRY_BASE = 0x0808E2E0
local MAP_ENTRY_SIZE = 0x38
local STACK_WINDOW_BYTES = 0x40
local MAX_FRAMES = 216000
-- A resident-alive observation window has to be proven positively, not
-- inferred from silence. Every other channel here is breakpoint-driven, so an
-- untouched living actor writes no row at all and its residency and HP go
-- unrecorded. This heartbeat re-reads the latched authored actor on a fixed
-- cadence so an alive window carries its own affirmative evidence.
local HEARTBEAT_FRAMES = 60
local EWRAM_BASE = 0x02000000
local EWRAM_SIZE = 0x00040000
-- Actor objects observed in this ticket are 4-byte aligned; the stride only
-- bounds the scan cost and is not a claim about object size or spacing.
local ACTOR_SCAN_STRIDE = 4
local SCAN_SLICE_BYTES = 0x2000

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = os.getenv("TOOLKIT031_OUT") or (exp_dir .. "toolkit034-dispatch.csv")

assert(emu and emu.setBreakpoint and emu.clearBreakpoint,
    "requires the mGBA 0.11 scripted-breakpoint API; a polling fallback cannot " ..
    "observe the indirect caller and must not be substituted")
local game_code = emu:getGameCode()
assert(game_code == "BG3E" or game_code == "AGB-BG3E",
    "unexpected game code: " .. tostring(game_code))
assert(emu:romSize() == 8388608, "unexpected ROM size")

local file = assert(io.open(log_path, "w"), "cannot open observer output")
file:write("kind,frame,map_index,pc,lr,sp,r0,r1,r2,r3,r4,r5,r6,r7,payload,attribution,stack_00,stack_04,stack_08,stack_0c,stack_10,stack_14,stack_18,stack_1c,stack_20,stack_24,stack_28,stack_2c,stack_30,stack_34,stack_38,stack_3c,f62c_saved_r4,f62c_saved_r5,f62c_saved_r6,f62c_saved_r7,f62c_caller_lr,actor,actor_descriptor,actor_x_raw,actor_y_raw,actor_hp_raw,input_raw,event_object,event_object_register,event_descriptor,event_word_00,event_word_04_raw,script_cursor,native_slot_raw,vm_stack,vm_depth_raw,vm_arg0_raw,vm_arg1_raw,vm_arg2_raw,note\n")
file:flush()

local frames = 0
local attributed_hits = 0
local interpreter_hits = 0
local authored_death_hits = 0
local canonical_death_hits = 0
local authored_script_entries = 0
local native_opcode_hits = 0
local native_handler_hits = 0
local last_authored_trampoline_frame = -1
local last_authored_script_frame = -1
local last_authored_native_frame = -1
local screenshots = {}
-- Latched from a live breakpoint register only; no EWRAM address is assumed to
-- survive a load, and the latch is re-validated against +0x228 on every read.
local authored_actor = nil
local scan_cursor = EWRAM_BASE
local heartbeat_rows = 0
local heartbeat_alive_rows = 0

local function safe8(address)
    local ok, value = pcall(function() return emu:read8(address) end)
    if ok and value ~= nil then return tonumber(value) end
    return nil
end

local function safe32(address)
    local ok, value = pcall(function() return emu:read32(address) end)
    if ok and value ~= nil then return tonumber(value) end
    return nil
end

-- Current HP at +0x28C is a SIGNED word (see actor_context below). safe32
-- returns the raw unsigned read, so a negative HP would compare as a very
-- large positive and be reported ALIVE. Reinterpret before any HP comparison.
local function as_signed32(value)
    if value == nil then return nil end
    if value >= 0x80000000 then return value - 0x100000000 end
    return value
end

local function safe16(address)
    local ok, value = pcall(function() return emu:read16(address) end)
    if ok and value ~= nil then return tonumber(value) end
    return nil
end

local function reg(name)
    local ok, value = pcall(function() return emu:readRegister(name) end)
    if ok and value ~= nil then return tonumber(value) end
    return nil
end

local function hex(value)
    if value == nil then return "" end
    return string.format("0x%08X", value)
end

local function current_map()
    local entry = safe32(ACTIVE_MAP_PTR)
    if not entry or entry < MAP_ENTRY_BASE then return nil end
    return (entry - MAP_ENTRY_BASE) // MAP_ENTRY_SIZE
end

local function csv(values)
    file:write(table.concat(values, ",") .. "\n")
    file:flush()
end

local function write_row(kind, registers, payload, attribution, stack_words, frame_words, context, note)
    local values = {kind, tostring(frames), current_map() and tostring(current_map()) or ""}
    for _, name in ipairs({"pc", "lr", "sp", "r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7"}) do
        values[#values + 1] = hex(registers[name])
    end
    values[#values + 1] = hex(payload)
    values[#values + 1] = attribution or ""
    for index = 1, STACK_WINDOW_BYTES // 4 do values[#values + 1] = hex(stack_words[index]) end
    for index = 1, 5 do values[#values + 1] = hex(frame_words[index]) end
    for _, name in ipairs({"actor", "actor_descriptor", "actor_x_raw", "actor_y_raw", "actor_hp_raw", "input_raw", "event_object", "event_object_register", "event_descriptor", "event_word_00", "event_word_04_raw", "script_cursor", "native_slot_raw", "vm_stack", "vm_depth_raw", "vm_arg0_raw", "vm_arg1_raw", "vm_arg2_raw"}) do
        if name == "event_object_register" then
            values[#values + 1] = context[name] or ""
        else
            values[#values + 1] = hex(context[name])
        end
    end
    values[#values + 1] = note or ""
    csv(values)
end

local function in_authored_script(value)
    return value and value >= AUTHORED_PAYLOAD and
        value < AUTHORED_PAYLOAD + AUTHORED_SCRIPT_LENGTH
end

local function schedule_screenshots()
    if #screenshots > 0 then return end
    for _, delay in ipairs({1, 5, 15}) do
        screenshots[#screenshots + 1] = {
            frame = frames + delay,
            path = exp_dir .. "effect-plus" .. tostring(delay) .. ".png",
        }
    end
end

local function snapshot_registers()
    local values = {}
    for _, name in ipairs({"pc", "lr", "sp", "r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7"}) do
        values[name] = reg(name)
    end
    return values
end

local function stack_window(sp)
    local words = {}
    if sp == nil then return words end
    for offset = 0, STACK_WINDOW_BYTES - 4, 4 do
        words[offset // 4 + 1] = safe32(sp + offset)
    end
    return words
end

local function f62c_saved_frame(sp)
    -- The observed immediate LR identifies the known 0x0800F62C frame shape:
    -- it saves r4-r7/lr, reserves 0xDC bytes, and its callee trampoline saves
    -- one LR word. At trampoline-entry SP those raw saved words are +0xDC..+0xEC.
    -- This records an explicitly bounded unwind candidate only; it does not
    -- assign behavior or trigger semantics to the caller.
    if sp == nil then return {} end
    return {
        safe32(sp + 0xDC), safe32(sp + 0xE0), safe32(sp + 0xE4),
        safe32(sp + 0xE8), safe32(sp + 0xEC),
    }
end

local function actor_context(actor)
    if actor == nil then return {} end
    return {
        actor = actor,
        actor_descriptor = safe32(actor + 0x228),
        -- Actor-class world position is evidenced at +0x1A0/+0x1A4. Values are
        -- retained raw; no positional trigger condition is inferred here.
        actor_x_raw = safe32(actor + 0x1A0),
        actor_y_raw = safe32(actor + 0x1A4),
        -- P-006A confirmed signed current HP at +0x28C. Preserve the raw word;
        -- this observer does not convert its fixed-point representation.
        actor_hp_raw = safe32(actor + 0x28C),
        input_raw = safe16(0x03003304),
    }
end

local function event_object_context(registers)
    -- Object addresses are discovered only from live breakpoint registers. A
    -- candidate is attributable solely by its documented +0x1C descriptor edge;
    -- no EWRAM address survives across loads and no destructor role is named.
    for _, name in ipairs({"r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7"}) do
        local object = registers[name]
        local descriptor = object and safe32(object + 0x1C) or nil
        if descriptor == AUTHORED_DESCRIPTOR then
            return {
                event_object = object,
                event_object_register = name,
                event_descriptor = descriptor,
                -- Raw word at the first-decision/decrement/dispatch sites.
                -- Its refcount meaning remains UNKNOWN until those instructions
                -- and the captured transitions establish it.
                event_word_00 = safe32(object),
                -- 0x08011A38/3E/5A read, decrement and branch on +0x04.
                -- Keep the observed value raw in the CSV rather than promoting
                -- a field name beyond the measured instruction sequence.
                event_word_04_raw = safe32(object + 0x04),
                input_raw = safe16(0x03003304),
            }
        end
    end
    return nil
end

-- A trampoline hit alone is not enough: the descriptor and its payload must
-- both be the authored chain before a caller snapshot is evidence for it.
local bp_trampoline = emu:setBreakpoint(function()
    local registers = snapshot_registers()
    local payload = registers.r0 and safe32(registers.r0 + 4) or nil
    local attributed = registers.r0 == AUTHORED_DESCRIPTOR and payload == AUTHORED_PAYLOAD
    local words = stack_window(registers.sp)
    local f62c_words = f62c_saved_frame(registers.sp)
    if attributed then
        attributed_hits = attributed_hits + 1
        last_authored_trampoline_frame = frames
    end
    write_row("TRAMPOLINE", registers, payload,
        attributed and "AUTHORED-DESCRIPTOR-PAYLOAD" or "OTHER-OR-UNREAD",
        words, f62c_words, {},
        attributed and "dynamic indirect-caller evidence" or "trampoline liveness only")
end, TRAMPOLINE)

-- The shared interpreter breakpoint attributes the known authored cursor after
-- its trampoline; unrelated entries provide the required liveness channel.
local bp_interpreter = emu:setBreakpoint(function()
    interpreter_hits = interpreter_hits + 1
    local registers = snapshot_registers()
    local cursor, carrier
    for _, name in ipairs({"r1", "r0", "r2", "r3"}) do
        if in_authored_script(registers[name]) then
            cursor, carrier = registers[name], name
            break
        end
    end
    if frames == last_authored_trampoline_frame and cursor ~= nil then
        authored_script_entries = authored_script_entries + 1
        last_authored_script_frame = frames
        write_row("SCRIPT", registers, AUTHORED_PAYLOAD, "AUTHORED-SCRIPT", {}, {}, {
            script_cursor = cursor,
        }, "authored script cursor carried by " .. carrier)
    elseif interpreter_hits <= 20 or interpreter_hits % 500 == 0 then
        write_row("INTERPRETER", registers, nil, "LIVENESS", {}, {}, {}, "shared VM liveness only")
    end
end, INTERPRETER)

-- This is the same proven TOOLKIT-033 slot-178 attribution. The breakpoint at
-- 0x08003CBE reports the opcode-handler PC as 0x08003CC0 before its cursor
-- loads retire. Requiring the authored trampoline and script-entry frame keeps
-- an unrelated native invocation from being attributed to the authored body.
local bp_native = emu:setBreakpoint(function()
    if frames ~= last_authored_trampoline_frame or
            frames ~= last_authored_script_frame then return end
    native_opcode_hits = native_opcode_hits + 1
    local registers = snapshot_registers()
    local cursor_holder = registers.r1
    local cursor = cursor_holder and safe32(cursor_holder) or nil
    local slot = cursor and safe8(cursor) or nil
    local exact = registers.pc == NATIVE_STACK_HANDLER_ENTRY and
        cursor == AUTHORED_NATIVE_CURSOR and slot == NATIVE_SLOT_178
    if exact then last_authored_native_frame = frames end
    write_row("NATIVE-OPCODE", registers, AUTHORED_PAYLOAD,
        exact and "AUTHORED-NATIVE-SLOT-178" or "AUTHORED-NATIVE-OTHER",
        {}, {}, {script_cursor = cursor, native_slot_raw = slot},
        "live native_stack cursor and slot in authored-entry frame")
end, NATIVE_STACK_BREAKPOINT)

local bp_handler = emu:setBreakpoint(function()
    if frames ~= last_authored_native_frame then return end
    native_handler_hits = native_handler_hits + 1
    local registers = snapshot_registers()
    local stack = registers.r0
    local depth = stack and safe32(stack) or nil
    local a0 = stack and safe32(stack + 4) or nil
    local a1 = stack and safe32(stack + 8) or nil
    local a2 = stack and safe32(stack + 12) or nil
    local expected = depth and depth >= 3 and a0 == EXPECT_TEXT and
        a1 == EXPECT_X and a2 == EXPECT_Y
    write_row("NATIVE-HANDLER", registers, AUTHORED_PAYLOAD,
        expected and "AUTHORED-NATIVE-178-EXPECTED-ARGS" or
            "AUTHORED-NATIVE-178-OTHER-ARGS",
        {}, {}, {
            vm_stack = stack,
            vm_depth_raw = depth,
            vm_arg0_raw = a0,
            vm_arg1_raw = a1,
            vm_arg2_raw = a2,
        }, "native slot 178 handler entry")
    if expected then schedule_screenshots() end
end, TEXT_HANDLER)

-- 0x0800F866 is the actor vtable +0x74 event-object creation path. The actor
-- is accepted only when its live +0x228 attachment is the authored descriptor.
local bp_actor_event = emu:setBreakpoint(function()
    local registers = snapshot_registers()
    local context = actor_context(registers.r0)
    if context.actor_descriptor ~= AUTHORED_DESCRIPTOR then return end
    write_row("ACTOR-EVENT-CREATE", registers, nil, "AUTHORED-ACTOR", {}, {}, context,
        "actor vtable slot+0x74 creation-path snapshot; semantics UNKNOWN")
end, ACTOR_EVENT_FACTORY)

-- P-006A runtime-confirmed 0x08018950 as the concrete callback reached by the
-- HP<=0 path with the dying actor in r1. Keep this channel separate from the
-- later event-object destructor path: it proves a logical-death control, not
-- that every callback necessarily creates or dispatches an event object.
local bp_death_callback = emu:setBreakpoint(function()
    local registers = snapshot_registers()
    local context = actor_context(registers.r1)
    local map_index = current_map()
    local attribution
    if context.actor_descriptor == AUTHORED_DESCRIPTOR then
        attribution = "AUTHORED-ACTOR-DEATH"
        authored_death_hits = authored_death_hits + 1
    elseif map_index == CANONICAL_CONTROL_MAP and
            context.actor_descriptor == CANONICAL_NULL_DESCRIPTOR then
        attribution = "CANONICAL-NULL-ACTOR-DEATH"
        canonical_death_hits = canonical_death_hits + 1
    else
        return
    end
    write_row("DEATH-CALLBACK", registers, nil, attribution, {}, {}, context,
        "runtime-confirmed death callback entry; actor supplied by live r1")
end, DEATH_CALLBACK)

local function destructor_snapshot(kind)
    local registers = snapshot_registers()
    local context = event_object_context(registers)
    if context == nil then return end
    write_row(kind, registers, nil, "AUTHORED-EVENT-OBJECT", {}, {}, context,
        "attributed raw destructor-path snapshot; semantics UNKNOWN")
end

local bp_destructor_first = emu:setBreakpoint(function()
    destructor_snapshot("DESTRUCTOR-FIRST-DECISION")
end, DESTRUCTOR_FIRST_DECISION)
local bp_destructor_decrement = emu:setBreakpoint(function()
    destructor_snapshot("DESTRUCTOR-DECREMENT")
end, DESTRUCTOR_DECREMENT)
local bp_destructor_dispatch = emu:setBreakpoint(function()
    destructor_snapshot("DESTRUCTOR-DISPATCH")
end, DESTRUCTOR_DISPATCH)

local callback_id
callback_id = callbacks:add("frame", function()
    frames = frames + 1
    -- Re-acquire the authored actor by scanning EWRAM for an object whose
    -- +0x228 is the authored descriptor. A whole-region sweep in one frame
    -- stalls the emulator, so walk a bounded slice per frame and wrap around.
    if authored_actor == nil then
        local limit = scan_cursor + SCAN_SLICE_BYTES
        if limit > EWRAM_BASE + EWRAM_SIZE then limit = EWRAM_BASE + EWRAM_SIZE end
        local candidate = scan_cursor
        while candidate < limit do
            if safe32(candidate + 0x228) == AUTHORED_DESCRIPTOR then
                authored_actor = candidate
                break
            end
            candidate = candidate + ACTOR_SCAN_STRIDE
        end
        scan_cursor = candidate
        if scan_cursor >= EWRAM_BASE + EWRAM_SIZE then scan_cursor = EWRAM_BASE end
    end
    if frames % HEARTBEAT_FRAMES == 0 then
        -- ACTOR_EVENT_FACTORY is the event-object creation path and only runs
        -- at death, so latching there produced nothing but post-mortem rows.
        -- Re-acquire instead by scanning EWRAM for an object whose +0x228 is
        -- the authored descriptor. Read-only, and validated by the same edge
        -- every other channel here uses, so no new mechanism is assumed.
        if authored_actor ~= nil and
                safe32(authored_actor + 0x228) ~= AUTHORED_DESCRIPTOR then
            authored_actor = nil
        end
        local context = authored_actor and actor_context(authored_actor) or {}
        -- Re-validate the latch before trusting anything read through it. A
        -- stale or reused address stops matching the authored descriptor, and
        -- is recorded as such rather than reported as residency.
        local resident = authored_actor ~= nil and
            context.actor_descriptor == AUTHORED_DESCRIPTOR
        local hp = as_signed32(context.actor_hp_raw)
        local attribution
        if not resident then
            attribution = "AUTHORED-ACTOR-NOT-RESIDENT"
        elseif hp ~= nil and hp > 0 then
            attribution = "AUTHORED-ACTOR-ALIVE"
            heartbeat_alive_rows = heartbeat_alive_rows + 1
        else
            attribution = "AUTHORED-ACTOR-RESIDENT-HP-NOT-POSITIVE"
        end
        heartbeat_rows = heartbeat_rows + 1
        write_row("ACTOR-HEARTBEAT", snapshot_registers(), nil, attribution,
            {}, {}, context,
            "periodic re-read of the latched authored actor; read-only")
    end
    for _, shot in ipairs(screenshots) do
        if shot.frame == frames then
            emu:screenshot(shot.path)
            local registers = snapshot_registers()
            write_row("SCREENSHOT", registers, AUTHORED_PAYLOAD,
                "AUTHORED-EFFECT-CAPTURED", {}, {}, {},
                shot.path:gsub(",", "_"))
        end
    end
    if frames >= MAX_FRAMES then
        emu:clearBreakpoint(bp_trampoline)
        emu:clearBreakpoint(bp_interpreter)
        emu:clearBreakpoint(bp_native)
        emu:clearBreakpoint(bp_handler)
        emu:clearBreakpoint(bp_actor_event)
        emu:clearBreakpoint(bp_death_callback)
        emu:clearBreakpoint(bp_destructor_first)
        emu:clearBreakpoint(bp_destructor_decrement)
        emu:clearBreakpoint(bp_destructor_dispatch)
        local registers = snapshot_registers()
        write_row("SUMMARY", registers, nil, "SUMMARY", {}, {}, {},
            "authored_trampoline_hits=" .. tostring(attributed_hits) ..
            " interpreter_hits=" .. tostring(interpreter_hits) ..
            " authored_death_hits=" .. tostring(authored_death_hits) ..
            " canonical_death_hits=" .. tostring(canonical_death_hits) ..
            " authored_script_entries=" .. tostring(authored_script_entries) ..
            " native_opcode_hits=" .. tostring(native_opcode_hits) ..
            " native_handler_hits=" .. tostring(native_handler_hits) ..
            " heartbeat_rows=" .. tostring(heartbeat_rows) ..
            " heartbeat_alive_rows=" .. tostring(heartbeat_alive_rows))
        callbacks:remove(callback_id)
        local marker = assert(io.open(done_path, "w"))
        marker:write("done:TOOLKIT034DispatchCallerWatch")
        marker:close()
    end
end)
