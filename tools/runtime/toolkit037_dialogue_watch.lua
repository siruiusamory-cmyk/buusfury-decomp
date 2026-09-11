-- TOOLKIT-037: when the player triggers ORDINARY dialogue -- an NPC talk, a
-- chest message -- which semantic text identity does the engine consume, and
-- through what mechanism?
--
-- Read-only with respect to emulated memory and input: this file writes no
-- emulated memory and presses no keys, so the read-only observer guarantee
-- enforced by tests/unit/test_mgba_capture.py stays true. Breakpoints stop and
-- resume the core; they do not modify it.
--
-- WHAT THE FIRST RUN MEASURED, and why this observer is shaped differently.
-- Run t037-map39-dialogue, ~16,200 frames on map 39, operator talking to
-- multiple NPCs and opening chests:
--
--   * The breakpoint at 0x0802BFBC -- the indexed text-TABLE reader that native
--     slot 178 uses -- fired ZERO times.
--   * Meanwhile real dialogue strings were repeatedly observed in IWRAM, e.g.
--     "Tell Piccolo and Dende That Goku's Coming Back", revealed one character
--     at a time through the word at 0x03003AE4.
--
-- So ordinary dialogue on map 39 reaches its text WITHOUT the indexed table
-- read that TOOLKIT-036's proven consumer performs. That is the hypothesis this
-- observer is built to test, and it is why the table reader is no longer the
-- primary channel.
--
-- STATIC FACTS MEASURED THIS PASS, offline against the canonical image:
--
--   * 0x03003AE4 has NO word-aligned literal anywhere in the 8 MiB image, so it
--     is not addressed directly; it is a field inside a structure.
--   * 0x03003898 has 83 word-aligned references, 12 of them in low ROM code
--     (0x08054FC0, 0x080561C4, 0x080561E0, 0x0807013C, 0x0807014C, 0x08070160,
--     0x08070168, 0x08070184, 0x08071C94, 0x080725B8, 0x080725E0, 0x08072828).
--     0x03003AE4 - 0x03003898 = 0x24C, so the live string pointer is a field at
--     +0x24C of the structure based at 0x03003898.
--   * That consumer cluster (0x08070000-0x08072FFF) is disjoint from slot 178's
--     text path (0x0802BXXX), which is consistent with a second, separate
--     dialogue mechanism rather than a variant of the proven one.
--
-- The exact routine that writes the field was NOT pinned down statically, and
-- this observer deliberately does not depend on knowing it: it watches the
-- FIELD, so whatever code writes it is caught.
--
-- CHANNELS, kept separate so none can be read as another:
--
--   CHANNEL A - DIALOGUE OBJECT STATE. Each sampled frame, read the string
--   pointer at STRUCT_BASE + STRING_OFFSET. On CHANGE, decode the body it names
--   and dump the surrounding structure words. Every transition is recorded, so
--   repeated conversations through the same slot are NOT collapsed. The first
--   run's dedupe hid exactly that and is removed.
--
--   CHANNEL B - TEXT-TABLE READER (EXECUTION). Breakpoint at 0x0802BFBC
--   retained as a CONTRAST channel, recording r0, the requested index. If
--   ordinary dialogue never trips it while channel A fills with real dialogue,
--   that separation is the finding.
--
--   CHANNEL C - LIVENESS (EXECUTION, POSITIVE CONTROL). Breakpoint at the
--   shared interpreter 0x08004038. NOTE, measured: TOOLKIT-036's own run logged
--   this exactly ONCE across a full session while its trampoline breakpoints
--   fired normally, so a low liveness count here is a known property of this
--   site and is NOT by itself evidence the instrument is dead. It proves
--   breakpoint installation, nothing more.
--
-- WHICH CHANNEL SUPPORTS WHICH CLAIM. A positive in A or B is real evidence. A
-- negative may be claimed only for B, and only while A is actively recording
-- dialogue -- that pairing is the whole experiment.

local TEXT_READER  = 0x0802BFBC   -- ldr r1,=0x0806BCE8 ; lsls r0,#2 ; ldr r4,[r1,r0]
local INTERPRETER  = 0x08004038   -- shared VM loop; installation control

local TEXT_TABLE   = 0x0806BCE8
local TEXT_COUNT   = 1534
local POOL_START   = 0x0805792C
local POOL_SIZE    = 82874
local POOL_END     = POOL_START + POOL_SIZE

--: Relocated bodies live in the declared verified-writable region, so a pointer
--: there is just as interesting as one into the retail pool.
local REGION_START = 0x087EA400
local REGION_END   = 0x087EA500

--: The dialogue structure, measured above. The live string pointer is +0x24C.
local STRUCT_BASE   = 0x03003898
local STRING_OFFSET = 0x24C
local STRING_SLOT   = STRUCT_BASE + STRING_OFFSET
local STRUCT_WORDS  = 24          -- dumped around the string field on change

--: The first run also saw pool pointers through 0x03003A3C, a different field
--: of the same structure. Watch both rather than assuming one is canonical.
local ALT_SLOT = 0x03003A3C

local ACTIVE_MAP_PTR = 0x03001980
local MAP_ENTRY_BASE = 0x0808E2E0
local MAP_ENTRY_SIZE = 0x38

--: Sample every frame. The first run sampled every 6th and still caught the
--: typewriter reveal, but a single-frame dialogue box would have been missed,
--: and reading a handful of words per frame is far cheaper than the 8 KiB
--: IWRAM sweep that run performed.
local SAMPLE_EVERY = 1

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = (os.getenv("TOOLKIT037_OUT") or (exp_dir .. "toolkit037-dialogue.csv"))

assert(emu ~= nil, "mGBA did not attach the emulation core")
assert(emu.setBreakpoint and emu.clearBreakpoint,
    "requires the mGBA 0.11 scripted-breakpoint API; the sampler alone cannot " ..
    "support a negative result and must not be substituted for it")
local game_code = emu:getGameCode()
assert(game_code == "BG3E" or game_code == "AGB-BG3E",
    "unexpected game code: " .. tostring(game_code))
assert(emu:romSize() == 8388608, "unexpected ROM size")

local file = assert(io.open(log_path, "w"), "cannot open output: " .. tostring(log_path))
file:write("kind,frame,map_index,slot,body_addr,text_index,text_len,text,note\n")
file:flush()

local frames = 0
local rows = 0
local changes = 0
local fetches = 0
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

local function in_text_storage(v)
    if v == nil then return false end
    if v >= POOL_START and v < POOL_END then return true end
    if v >= REGION_START and v < REGION_END then return true end
    return false
end

--: Decode a UTF-16LE body up to its terminator, exactly as the engine's own
--: measuring routine walks it. ASCII-range units are emitted literally;
--: anything else becomes \xXXXX so the CSV stays readable and nothing is
--: silently dropped. Bounded so a corrupt pointer cannot spin.
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

--: Reverse-resolve a body address to its semantic text index. Built once at arm
--: time so the per-frame path is a hash lookup rather than a 1534-entry scan.
--: A body reached MID-STRING will not match, which is itself informative: the
--: typewriter reveal walks forward through one body, so only its first frame
--: resolves to an index.
local body_to_index = {}
do
    for i = 0, TEXT_COUNT - 1 do
        local body = safe32(TEXT_TABLE + i * 4)
        if body ~= nil and body_to_index[body] == nil then
            body_to_index[body] = i
        end
    end
end

--: Resolve a body that may point into the MIDDLE of a table entry, by finding
--: the nearest entry at or below it. This is what lets a typewriter-revealed
--: string still be attributed to its semantic index.
local sorted_bodies = {}
for body, _ in pairs(body_to_index) do
    sorted_bodies[#sorted_bodies + 1] = body
end
table.sort(sorted_bodies)

local function resolve_index(body)
    if body == nil then return nil, nil end
    local exact = body_to_index[body]
    if exact then return exact, 0 end
    --: Binary search for the greatest entry <= body.
    local lo, hi, best = 1, #sorted_bodies, nil
    while lo <= hi do
        local mid = (lo + hi) // 2
        if sorted_bodies[mid] <= body then
            best = sorted_bodies[mid]
            lo = mid + 1
        else
            hi = mid - 1
        end
    end
    if best == nil then return nil, nil end
    return body_to_index[best], body - best
end

local function write_row(kind, slot, body_addr, note)
    local map = current_map()
    local text, units = decode_body(body_addr)
    local index, delta = resolve_index(body_addr)
    if delta and delta > 0 then
        note = note .. "; +" .. tostring(delta) .. " into entry"
    end
    --: The CSV is comma-separated and a string may contain commas, so the text
    --: field is quoted and its own quotes doubled.
    local quoted = ""
    if text ~= nil then
        quoted = '"' .. text:gsub('"', '""') .. '"'
    end
    file:write(string.format("%s,%d,%s,%s,%s,%s,%s,%s,%s\n",
        kind, frames,
        map and tostring(map) or "",
        hex(slot), hex(body_addr),
        index and tostring(index) or "",
        units and tostring(units) or "",
        quoted, note))
    file:flush()
    rows = rows + 1
end

write_row("ARMED", STRING_SLOT, nil,
    "watching struct 0x03003898 +0x24C; no dedupe")

-- CHANNEL B: the indexed text-table reader, retained as the contrast channel.
local bp_text = emu:setBreakpoint(function(info)
    fetches = fetches + 1
    local index = tonumber(emu:readRegister("r0"))
    local body = nil
    local note = "indexed table read"
    if index ~= nil and index >= 0 and index < TEXT_COUNT then
        body = safe32(TEXT_TABLE + index * 4)
    else
        note = "index outside declared table extent"
    end
    write_row("TEXT-FETCH", TEXT_READER, body, note)
end, TEXT_READER)

-- CHANNEL C: breakpoint-installation control. Low counts are expected here.
local bp_live = emu:setBreakpoint(function(info)
    liveness = liveness + 1
    if liveness <= 3 or liveness % 1000 == 0 then
        write_row("LIVENESS", INTERPRETER, nil,
            "shared interpreter reached x" .. tostring(liveness))
    end
end, INTERPRETER)

-- CHANNEL A: the dialogue object. Report every CHANGE, never collapsing
-- repeats, so a second conversation through the same slot is still recorded.
local last_primary = nil
local last_alt = nil

local function dump_struct(note)
    for k = 0, STRUCT_WORDS - 1 do
        local addr = STRUCT_BASE + STRING_OFFSET - 16 + 4 * k
        local v = safe32(addr)
        if in_text_storage(v) then
            write_row("STRUCT-WORD", addr, v, note)
        end
    end
end

callbacks:add("frame", function()
    frames = frames + 1
    if frames % SAMPLE_EVERY ~= 0 then return end

    local primary = safe32(STRING_SLOT)
    if primary ~= last_primary then
        last_primary = primary
        if in_text_storage(primary) then
            changes = changes + 1
            write_row("DIALOGUE", STRING_SLOT, primary,
                "string pointer changed #" .. tostring(changes))
            --: On the first frame of a new string, dump the neighbourhood once
            --: so a sibling field holding the ORIGINAL body start is captured.
            if changes <= 40 then
                dump_struct("neighbourhood of change #" .. tostring(changes))
            end
        end
    end

    local alt = safe32(ALT_SLOT)
    if alt ~= last_alt then
        last_alt = alt
        if in_text_storage(alt) then
            write_row("ALT-SLOT", ALT_SLOT, alt, "alternate field changed")
        end
    end
end)

--: Heartbeat so the log distinguishes "the observer stopped" from "the observer
--: ran and saw nothing", which are different failures.
callbacks:add("frame", function()
    if frames % 1800 == 0 then
        write_row("HEARTBEAT", nil, nil,
            "alive; dialogue changes " .. tostring(changes) ..
            ", table reads " .. tostring(fetches))
    end
end)

--: The launcher waits on this marker before loading the savestate.
local marker = assert(io.open(done_path, "w"), "cannot open marker")
marker:write("armed\n")
marker:close()

print([[TOOLKIT-037 dialogue watch armed - struct field + contrast breakpoint]])
print([[log: ]] .. log_path)
