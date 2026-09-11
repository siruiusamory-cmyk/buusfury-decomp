-- TOOLKIT-036: does the engine FOLLOW a rewritten text pointer to a relocated
-- body, and render the full overlength authored string?
--
-- Read-only with respect to emulated memory and input: this file writes no
-- emulated memory and presses no keys, so the read-only observer guarantee
-- enforced by tests/unit/test_mgba_capture.py stays true. Breakpoints stop and
-- resume the core; they do not modify it.
--
-- WHAT IS ALREADY ESTABLISHED, and therefore NOT re-measured here:
--
--   * TOOLKIT-034 proved the on_defeat trigger family.
--   * TOOLKIT-035 proved the whole authored scene: authored enemy -> ordinary
--     combat -> defeat -> on_defeat -> authored script -> native slot 178 ->
--     text 1525 displayed. That chain is not under test again.
--
-- The ONE variable under test is text STORAGE. TOOLKIT-035's message lived in
-- text 1525's own 30-byte retail body. This build's message is 53 characters,
-- which cannot fit there, so the SDK allocated a new body in verified free ROM
-- space and rewrote the pointer-table slot that owns it. The question is
-- whether the ORIGINAL engine follows that rewritten pointer.
--
-- STATIC FACTS THIS OBSERVER IS BUILT ON (all measured, TOOLKIT-036 Phase 1):
--
--   * Text 1525's pointer-table slot is file 0x0006D4BC = ROM 0x0806D4BC.
--     Canonically it holds 0x0806BBD6, the retail body ("Match 2 Fight!",
--     30 bytes including its 0x0000 terminator).
--   * A stride-1 scan of the whole 8 MiB image found EXACTLY ONE word equal to
--     0x0806BBD6 -- that slot. Nothing else in the ROM references the body, so
--     repointing the slot moves the string completely.
--   * In the generated image the slot instead holds a pointer into the declared
--     verified-writable region [0x007EA400, 0x007EA500), i.e. 0x087EA4xx.
--
-- CHANNELS, kept separate so neither can be read as the other:
--
--   CHANNEL A - POINTER STATE. Read slot 0x0806D4BC directly and classify it as
--   RETAIL (still 0x0806BBD6) or RELOCATED (inside the verified region). This is
--   a STATIC read of the loaded image and is NOT execution evidence. It exists
--   so a negative result can distinguish "the wrong ROM was loaded" from "the
--   engine did not follow the pointer".
--
--   CHANNEL B - EXECUTION. A breakpoint at the script trampoline 0x0800421E,
--   recording r0 (the descriptor that selected it) and [r0+4] (the script root
--   about to run). Direct execution evidence: the PC was there.
--
--   CHANNEL C - THE RENDERED STRING. On each trampoline hit, follow the slot to
--   whatever body it currently names and decode that body as UTF-16LE up to its
--   terminator. This reports the string the engine would resolve THROUGH THE
--   TABLE, by the same indirection the native text routine uses. Recording the
--   decoded text, not merely the pointer, is what separates "the pointer was
--   rewritten" from "the full authored string is reachable".
--
-- HONEST FAILURE MODE. If the breakpoint API is absent the script aborts rather
-- than silently degrading to a poll: an instrument that cannot see execution
-- must not produce rows that look like a negative result.
--
-- LIVENESS / POSITIVE CONTROL. A second breakpoint on the shared script
-- interpreter 0x08004038, which dialogue and cutscenes reach constantly. If the
-- trampoline channel is silent AND liveness is silent, this instrument proved
-- NOTHING and the run must be reported as unproven, not as a negative. If
-- liveness fires while the trampoline stays silent, the negative is real.

local TRAMPOLINE  = 0x0800421E   -- ldr r1,[r0,#4] ; bl 0x08004038
local INTERPRETER = 0x08004038   -- shared VM loop; the liveness channel

local AUTHORED_DESCRIPTOR = 0x0808D788
local NULL_DESCRIPTOR     = 0x080555A0

--: Text 1525's owning pointer-table slot, and what canonical holds there.
local TEXT_SLOT     = 0x0806D4BC
local RETAIL_BODY   = 0x0806BBD6
local REGION_START  = 0x087EA400
local REGION_END    = 0x087EA500

local ACTIVE_MAP_PTR = 0x03001980
local MAP_ENTRY_BASE = 0x0808E2E0
local MAP_ENTRY_SIZE = 0x38

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = (os.getenv("TOOLKIT036_OUT") or (exp_dir .. "toolkit036-text.csv"))

assert(emu ~= nil, "mGBA did not attach the emulation core")
assert(emu.setBreakpoint and emu.clearBreakpoint,
    "requires the mGBA 0.11 scripted-breakpoint API; a polling fallback " ..
    "cannot see execution and must not be substituted")
local game_code = emu:getGameCode()
assert(game_code == "BG3E" or game_code == "AGB-BG3E",
    "unexpected game code: " .. tostring(game_code))
assert(emu:romSize() == 8388608, "unexpected ROM size")

local file = assert(io.open(log_path, "w"), "cannot open output: " .. tostring(log_path))
file:write("kind,frame,map_index,pc,descriptor,slot_value,body_addr,pointer_kind,text_len,text,note\n")
file:flush()

local frames = 0
local hits = 0
local liveness = 0

local function safe32(addr)
    local ok, v = pcall(function() return emu:read32(addr) end)
    if ok and v then return v end
    return nil
end

local function safe16(addr)
    local ok, v = pcall(function() return emu:read16(addr) end)
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

--: CHANNEL A. Classify the slot without interpreting it as success either way.
local function classify_pointer(slot)
    if slot == nil then return "UNREAD" end
    if slot == RETAIL_BODY then return "RETAIL" end
    if slot >= REGION_START and slot < REGION_END then return "RELOCATED" end
    return "OTHER"
end

--: CHANNEL C. Follow the slot and decode the body it names, exactly as the
--: engine's own table indirection would. ASCII-range units are emitted
--: literally; anything else becomes \xXXXX so the CSV stays readable and no
--: information is silently dropped. Bounded so a corrupt pointer cannot spin.
local function decode_body(body)
    if body == nil then return nil, nil end
    local addr = body
    local out = {}
    local units = 0
    while units < 256 do
        local unit = safe16(addr)
        if unit == nil then break end
        if unit == 0 then break end
        if unit >= 0x20 and unit < 0x7F then
            out[#out + 1] = string.char(unit)
        else
            out[#out + 1] = string.format("\\x%04X", unit)
        end
        addr = addr + 2
        units = units + 1
    end
    return table.concat(out), units
end

local function write_row(kind, pc, descriptor, note)
    local map = current_map()
    local slot = safe32(TEXT_SLOT)
    local text, units = decode_body(slot)
    --: The CSV is comma-separated and the authored string contains commas, so
    --: the text field is quoted and its own quotes doubled.
    local quoted = ""
    if text ~= nil then
        quoted = '"' .. text:gsub('"', '""') .. '"'
    end
    file:write(string.format("%s,%d,%s,%s,%s,%s,%s,%s,%s,%s,%s\n",
        kind, frames,
        map and tostring(map) or "",
        hex(pc), hex(descriptor),
        hex(slot), hex(slot),
        classify_pointer(slot),
        units and tostring(units) or "",
        quoted, note))
    file:flush()
end

--: One row at arm time: the pointer state of the image actually loaded, before
--: any play. This is what makes a later negative interpretable.
write_row("ARMED", nil, nil, "pointer state at arm time")

-- CHANNEL B + C: every entry to the script trampoline, with the descriptor that
-- selected it and the string the text slot currently resolves to.
local bp_tramp = emu:setBreakpoint(function(info)
    hits = hits + 1
    local pc = tonumber(emu:readRegister("pc"))
    local r0 = tonumber(emu:readRegister("r0"))
    local kind = "TRAMPOLINE"
    if r0 == AUTHORED_DESCRIPTOR then
        kind = "AUTHORED-BEHAVIOR"
    elseif r0 == NULL_DESCRIPTOR then
        kind = "INHERITED-NULL"
    end
    write_row(kind, pc, r0, "trampoline entry")
end, TRAMPOLINE)

-- LIVENESS: the shared interpreter. Sampled, not logged per hit -- it fires
-- constantly and the point is only to prove the instrument can see execution.
local bp_live = emu:setBreakpoint(function(info)
    liveness = liveness + 1
    if liveness == 1 or liveness % 500 == 0 then
        write_row("LIVENESS", INTERPRETER, nil,
            "shared interpreter reached x" .. tostring(liveness))
    end
end, INTERPRETER)

callbacks:add("frame", function()
    frames = frames + 1
end)

--: The launcher waits on this marker before loading the savestate.
local marker = assert(io.open(done_path, "w"), "cannot open marker")
marker:write("armed\n")
marker:close()

print([[TOOLKIT-036 text watch armed]])
print([[log: ]] .. log_path)
