-- TOOLKIT-031: does the behavior ATTACHED to an authored placement actually
-- EXECUTE, and what triggers it?
--
-- Read-only with respect to emulated memory and input: this file writes no
-- emulated memory and presses no keys, so the read-only observer guarantee
-- enforced by tests/unit/test_mgba_capture.py stays true. Breakpoints stop and
-- resume the core; they do not modify it.
--
-- WHY THE PREVIOUS CHANNEL WAS REPLACED. TOOLKIT-030 tried to infer execution
-- from a downstream effect (a collision rectangle) and the channel turned out to
-- be non-discriminating: authored and control builds read identically because
-- the sampled region was already saturated, and the off-rect control tile read
-- set too. A saturated grid cannot separate "the script ran" from "these tiles
-- were already set", so that reading was correctly refused as evidence in either
-- direction. This observer therefore measures EXECUTION DIRECTLY -- the program
-- counter reaching the handler -- instead of inferring it from world state.
--
-- WHAT THE STATIC CENSUS ESTABLISHED (TOOLKIT-031 section 1), and why this
-- observer watches the addresses it does:
--
--   * Handler 0x0800421E has ZERO direct BL callers in the image. It is reached
--     only indirectly, through a descriptor's +0x00 word, so "who calls it" has
--     no static answer and must be measured.
--   * The placement constructor 0x0800F68C does NOT call the descriptor. At
--     0x0800F6F0/0x0800F6F4 it copies the placement's +0x14 into actor+0x228 and
--     returns. Construction stores the attachment; it does not run it.
--   * actor+0x228 has exactly one writer (that store) and four readers, of which
--     0x0804F860 is a pure getter exposed as actor-vtable slot +0x78.
--
-- So map construction is REFUTED as the trigger, and the live question is
-- whether anything ever dispatches that getter for our entity.
--
-- CHANNELS, kept separate so neither can be read as the other:
--
--   CHANNEL A - EXECUTION. A breakpoint at the script trampoline 0x0800421E.
--   On entry r0 is the descriptor, so r0 tells us WHICH attachment ran. This is
--   direct execution evidence: the PC was there.
--
--   CHANNEL B - ATTRIBUTION. On each hit, record r0 and [r0+4]. The authored
--   descriptor is 0x0808D788 with payload 0x0808D77C; the null/control
--   descriptor is 0x080555A0. Recording the descriptor rather than merely
--   counting hits is what separates "our attachment executed" from "some other
--   placement's script executed".
--
--   CHANNEL C - STRUCTURE. The TOOLKIT-030 structural read, retained unchanged
--   so this run also re-confirms the attachment is live. It is NOT execution
--   evidence and is never reported as such.
--
-- HONEST FAILURE MODE. If the breakpoint API is absent the script aborts rather
-- than silently degrading to a poll: an instrument that cannot see execution
-- must not produce rows that look like a negative result. Zero hits are only
-- meaningful once the POSITIVE CONTROL below has been observed to hit.
--
-- POSITIVE CONTROL. Map 428 slot 0 (record 0x0808D790) is the CANONICAL owner of
-- the very descriptor TOOLKIT-030 attached: same descriptor 0x0808D788, same
-- script root 0x0808D77C. If the instrument cannot observe that canonical
-- placement's behavior executing, an authored miss proves nothing about the
-- authored attachment and only proves the instrument is blind.

local TRAMPOLINE        = 0x0800421E   -- ldr r1,[r0,#4] ; bl 0x08004038
local INTERPRETER       = 0x08004038   -- the VM loop the trampoline enters

local AUTHORED_DESCRIPTOR = 0x0808D788 -- {0x0800421F, 0x0808D77C}
local AUTHORED_PAYLOAD    = 0x0808D77C
local NULL_DESCRIPTOR     = 0x080555A0 -- handler 0x0800421D, `bx lr`

local ACTIVE_MAP_PTR    = 0x03001980
local MAP_ENTRY_BASE    = 0x0808E2E0
local MAP_ENTRY_SIZE    = 0x38

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = (os.getenv("TOOLKIT031_OUT") or (exp_dir .. "toolkit031-execution.csv"))

assert(emu ~= nil, "mGBA did not attach the emulation core")
assert(emu.setBreakpoint and emu.clearBreakpoint,
    "requires the mGBA 0.11 scripted-breakpoint API; a polling fallback " ..
    "cannot see execution and must not be substituted")
-- mGBA 0.11 returns the bare 4-character code here (measured: "BG3E"),
-- not the "AGB-" prefixed form some older scripts assert on.
local game_code = emu:getGameCode()
assert(game_code == "BG3E" or game_code == "AGB-BG3E",
    "unexpected game code: " .. tostring(game_code))
assert(emu:romSize() == 8388608, "unexpected ROM size")

local file = assert(io.open(log_path, "w"), "cannot open output: " .. tostring(log_path))
file:write("kind,frame,map_index,pc,descriptor,payload,descriptor_kind,note\n")
file:flush()

local frames = 0
local hits = 0

local function safe32(addr)
    local ok, v = pcall(function() return emu:read32(addr) end)
    if ok and v then return v end
    return nil
end

local function safe8(addr)
    local ok, v = pcall(function() return emu:read8(addr) end)
    if ok and v then return v end
    return nil
end

local function hex(v)
    if v == nil then return "" end
    return string.format("0x%08X", v)
end

local function current_map()
    local entry = safe32(ACTIVE_MAP_PTR)
    if not entry or entry < MAP_ENTRY_BASE then return nil end
    return (entry - MAP_ENTRY_BASE) // MAP_ENTRY_SIZE
end

local function classify(descriptor)
    if descriptor == AUTHORED_DESCRIPTOR then return "AUTHORED-BEHAVIOR" end
    if descriptor == NULL_DESCRIPTOR then return "INHERITED-NULL" end
    if descriptor == nil then return "UNREAD" end
    return "OTHER-CANONICAL"
end

local function write_row(kind, pc, descriptor, payload, note)
    local map = current_map()
    file:write(string.format("%s,%d,%s,%s,%s,%s,%s,%s\n",
        kind, frames,
        map and tostring(map) or "",
        hex(pc), hex(descriptor), hex(payload),
        classify(descriptor), note))
    file:flush()
end

-- CHANNEL A + B: every entry to the script trampoline, with the descriptor that
-- selected it. r0 is the descriptor because the handler is invoked as
-- handler(descriptor); [r0+4] is the script root the trampoline is about to run.
local bp_tramp = emu:setBreakpoint(function(info)
    hits = hits + 1
    local pc = tonumber(emu:readRegister("pc"))
    local r0 = tonumber(emu:readRegister("r0"))
    local payload = r0 and safe32(r0 + 4) or nil
    local note
    if r0 == AUTHORED_DESCRIPTOR and payload == AUTHORED_PAYLOAD then
        note = "AUTHORED attachment reached the trampoline"
    elseif r0 == AUTHORED_DESCRIPTOR then
        note = "authored descriptor, unexpected payload"
    else
        note = "other descriptor executed"
    end
    write_row("EXEC", pc, r0, payload, note)
end, TRAMPOLINE)

-- CHANNEL D - INSTRUMENT LIVENESS. A second breakpoint on the interpreter
-- itself. The interpreter is shared: dialogue, events and cutscenes all reach
-- it, so if THIS never fires either, the instrument is not seeing execution at
-- all and no absence measured here means anything. If it fires while the
-- trampoline stays silent, then scripts ARE running and specifically the
-- placement-descriptor path is not being taken -- which is a real measurement
-- rather than a blind one. This is what makes a zero-hit trampoline
-- interpretable, and it is why the run asks for NPC dialogue: dialogue is a
-- known interpreter consumer, so it is a live check on the instrument.
local interp_hits = 0
local bp_interp = emu:setBreakpoint(function(info)
    interp_hits = interp_hits + 1
    -- Log sparsely: this fires often and the file is evidence, not a trace.
    if interp_hits <= 20 or interp_hits % 500 == 0 then
        write_row("INTERP", tonumber(emu:readRegister("pc")), nil, nil,
            "interpreter reached; liveness only, hits=" .. tostring(interp_hits))
    end
end, INTERPRETER)

local callback_id
callback_id = callbacks:add("frame", function()
    frames = frames + 1
    -- CHANNEL C: periodic structural confirmation, clearly labelled so it is
    -- never mistaken for execution evidence.
    if frames % 60 == 0 then
        -- Record the live descriptor of the LAST placement slot, so the
        -- evidence shows whether the authored/control entity was actually
        -- present for the whole run. A silent trampoline means nothing if
        -- the entity was never instantiated in the first place.
        local desc, payload = nil, nil
        local entry = safe32(ACTIVE_MAP_PTR)
        if entry and entry >= MAP_ENTRY_BASE then
            local count = safe8(entry + 0x04)
            local array = safe32(entry + 0x14)
            if count and array and count > 0 then
                local slot = safe32(array + (count - 1) * 4)
                if slot then
                    desc = safe32(slot + 0x14)
                    if desc then payload = safe32(desc + 4) end
                end
            end
        end
        write_row("STRUCT", nil, desc, payload,
            "structural sample only; not execution")
    end
    -- Bounded, but long enough that the run is ended by the wrapper's
    -- deadline rather than by the observer expiring mid-experiment.
    if frames >= 216000 then
        if bp_tramp then emu:clearBreakpoint(bp_tramp) end
        if bp_interp then emu:clearBreakpoint(bp_interp) end
        write_row("SUMMARY", nil, nil, nil,
            "trampoline_hits=" .. tostring(hits) ..
            " interpreter_hits=" .. tostring(interp_hits))
        callbacks:remove(callback_id)
        local marker = assert(io.open(done_path, "w"))
        marker:write("done:TOOLKIT031ExecutionWatch")
        marker:close()
    end
end)
