-- TOOLKIT-038: how does the engine consume one known shop-dialogue SCENARIO and
-- feed its text into the live dialogue path?
--
-- Read-only with respect to emulated memory and input: this file writes no
-- emulated memory and presses no keys, so the read-only observer guarantee
-- enforced by tests/unit/test_mgba_capture.py stays true. Breakpoints stop and
-- resume the core; they do not modify it.
--
-- WHAT THE STATIC PASS MEASURED, offline against the canonical image. Every
-- address below is a measured file offset + 0x08000000, not a guess.
--
-- Six shop scenarios exist in the 0x0877Fxxx..0x0878xxxx region. Each is a
-- stride-4 pointer array preceded by an 8-byte header:
--
--   header:  +0 u16 entry_count
--            +2 u8  type = 0x05          (scenario descriptor)
--            +3 u8  0
--            +4 u32 0x02CE74C0           (constant across all six)
--            +8     the pointer array starts here
--
-- The LAST array slot points back at that header, and the header's u16 count
-- equals the array's entry count, for all six arrays. Measured:
--
--   array        count  header
--   0x0877F3B0   10     0x0877F3A8   Hercule City Z-Mart
--   0x0877F73C   10     0x0877F734   West City Z-Mart
--   0x0877FAB8   11     0x0877FAB0   black market
--   0x0877FE00   10     0x0877FDF8   Planet of the Kais Z-Mart
--   0x08780008    8     0x08780000
--   0x087803E4   12     0x087803DC
--
-- 61 targets total. Every one has EXACTLY ONE word-aligned inbound reference in
-- the whole 8 MiB image: its own array slot. Ownership is therefore unique.
--
-- Each target is a script whose first three bytes are:
--
--   +0 u16 next_script_index      measured 0..entry_count, never out of range
--   +2 u8  type                   measured values: 0x00, 0x03, 0x04, 0x05 only
--   +3 u8  0 or 2
--
-- Type census across all 61 targets: 0x00 x18, 0x03 x17, 0x04 x20, 0x05 x6.
-- Payload shape measured per type:
--   0x03 -> UTF-16LE plaintext beginning at +4. Decodes to real shop speech.
--   0x04 -> high-entropy payload, shared leading bytes across shops. Compressed.
--   0x00 -> short (8..30 bytes), repeating halfword structure. Bytecode.
--   0x05 -> exactly 8 bytes, the scenario header itself.
--
-- Scenario 0x0877F3B0 is this ticket's chosen target: clearest decoded text,
-- simplest structure, and slot 1 is the greeting line
-- "Welcome to the Hercule City Z-Mart! How can I help you?" at 0x0877F096.
--
-- A shop OBJECT record was also measured, five instances at stride 0x64 in low
-- ROM, each carrying its scenario pointer at field +0x0C:
--
--   record 0x08074360 -> scenario 0x0877F3B0
--   record 0x080743C4 -> scenario 0x0877F73C
--   record 0x08074450 -> scenario 0x0877FAB8
--   record 0x080744B4 -> scenario 0x0877FE00
--   record 0x0807451C -> scenario 0x08780008
--
-- Fields +0x00, +0x04, +0x08, +0x10, +0x14, +0x18, +0x1C are byte-identical
-- across all five records; only +0x0C (the scenario) and the trailing fields
-- vary. A master index listing every scenario array in the region sits at
-- 0x0879B774.
--
-- WHAT IS NOT KNOWN, and is what this observer exists to measure:
--
--   * which code reads a scenario array slot;
--   * which code reads the type byte at +2, and what it branches to;
--   * whether the type-0x03 body reaches the SAME live dialogue cursor
--     TOOLKIT-037 proved at struct 0x03003898 +0x24C;
--   * whether 0x0202BA70 (a Data Crystal lead) correlates with dialogue at all.
--     That address has ZERO word-aligned references in the image, so it can only
--     be reached by computed addressing and static analysis cannot settle it.
--
-- CHANNELS, kept separate so none can be read as another:
--
--   CHANNEL A - SCENARIO TEXT REACHED THE LIVE CURSOR. Watch the dialogue
--   string pointer TOOLKIT-037 proved (0x03003898 + 0x24C) and its alternate
--   field. A pointer landing INSIDE the shop region 0x0877F000..0x08781000 is
--   the edge this ticket is trying to prove, and is classified separately from a
--   pointer into the declared text pool.
--
--   CHANNEL B - SHOP-RECORD EXECUTION. Breakpoints on the three code hooks the
--   record carries, so the shop object's own lifecycle is attributable.
--
--   CHANNEL C - DATA CRYSTAL LEADS. Sample 0x0202BA70 every frame and record
--   transitions. Separately, a breakpoint at 0x0801226A, which Data Crystal
--   claims reaches message display with r1 carrying a text value. The static
--   pass DISPUTES that: 0x0801226A is `movs r0, #0` inside func.08012230, a
--   routine that calls the allocator at 0x0803D5B8 and indexes table
--   0x087B5B64, and r1 there holds a packed bitfield being shifted. Recorded so
--   the claim is settled by measurement rather than by my reading.
--
--   CHANNEL D - LIVENESS (POSITIVE CONTROL). Breakpoint at the shared
--   interpreter 0x08004038. TOOLKIT-036 logged this exactly ONCE across a full
--   session while its own breakpoints fired normally, so a LOW count here is a
--   known property of the site and is not by itself evidence of a dead
--   instrument. It proves breakpoint installation, nothing more.
--
-- WHICH CHANNEL SUPPORTS WHICH CLAIM. A positive in A, B or C is real evidence.
-- A negative may be claimed only while channel D shows installation AND the
-- operator confirms a shop conversation actually ran.

local SHOP_START = 0x0877F000
local SHOP_END   = 0x08781000

--: The chosen scenario, measured. Its array, header and entry count.
local SCENARIO      = 0x0877F3B0
local SCENARIO_HDR  = 0x0877F3A8
local SCENARIO_N    = 10

--: The shop object records, measured. Field +0x0C is the scenario pointer.
local RECORDS = {
    0x08074360, 0x080743C4, 0x08074450, 0x080744B4, 0x0807451C,
}
local RECORD_SCENARIO_FIELD = 0x0C

--: Code hooks carried by every shop record, constant across all five.
local HOOK_A = 0x0800775E   -- record +0x00, Thumb (LSB stripped)
local HOOK_B = 0x08007674   -- record +0x10
local HOOK_C = 0x080077DE   -- record +0x14

--: Data Crystal leads, both unverified.
local DC_MESSAGE_BP = 0x0801226A
local DC_RAM_SLOT   = 0x0202BA70

local INTERPRETER = 0x08004038

--: The live dialogue cursor TOOLKIT-037 proved. Do not re-derive it.
local STRUCT_BASE   = 0x03003898
local STRING_OFFSET = 0x24C
local STRING_SLOT   = STRUCT_BASE + STRING_OFFSET
local ALT_SLOT      = 0x03003A3C
local STRUCT_WORDS  = 32

--: The declared text pool, so a pointer there is classified as NOT-shop rather
--: than being mistaken for the edge this ticket wants.
local POOL_START = 0x0805792C
local POOL_END   = POOL_START + 82874

local ACTIVE_MAP_PTR = 0x03001980
local MAP_ENTRY_BASE = 0x0808E2E0
local MAP_ENTRY_SIZE = 0x38

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = (os.getenv("TOOLKIT038_OUT") or (exp_dir .. "toolkit038-scenario.csv"))

assert(emu ~= nil, "mGBA did not attach the emulation core")
assert(emu.setBreakpoint and emu.clearBreakpoint,
    "requires the mGBA 0.11 scripted-breakpoint API; a sampler alone cannot " ..
    "support a negative result and must not be substituted for it")
local game_code = emu:getGameCode()
assert(game_code == "BG3E" or game_code == "AGB-BG3E",
    "unexpected game code: " .. tostring(game_code))
assert(emu:romSize() == 8388608, "unexpected ROM size")

local file = assert(io.open(log_path, "w"), "cannot open output: " .. tostring(log_path))
file:write("kind,frame,map_index,site,value,slot_index,type_byte,next_index,text,note\n")
file:flush()

local frames = 0
local rows = 0
local shop_hits = 0
local hook_hits = 0
local dc_hits = 0
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

local function in_shop_region(v)
    return v ~= nil and v >= SHOP_START and v < SHOP_END
end

local function in_pool(v)
    return v ~= nil and v >= POOL_START and v < POOL_END
end

--: Decode UTF-16LE up to the terminator. ASCII literal, everything else as
--: \xXXXX so nothing is silently dropped and the CSV stays readable.
local function decode_body(body)
    if body == nil then return nil end
    local addr = body
    local out = {}
    local units = 0
    while units < 200 do
        local unit = safe16(addr)
        if unit == nil or unit == 0 then break end
        if unit >= 0x20 and unit < 0x7F then
            out[#out + 1] = string.char(unit)
        else
            out[#out + 1] = string.format("\\x%04X", unit)
        end
        addr = addr + 2
        units = units + 1
    end
    return table.concat(out)
end

--: Resolve a shop-region pointer back to (slot index, type, next index) for the
--: chosen scenario, so a live cursor can be attributed to a specific script.
--: Built once at arm time from the emulated ROM, which double-checks the static
--: measurements above against what the core actually has loaded.
local slot_of = {}
do
    for s = 0, SCENARIO_N - 1 do
        local t = safe32(SCENARIO + s * 4)
        if t ~= nil then slot_of[t] = s end
    end
end

--: A cursor may point INTO a script body rather than at its start, exactly as
--: TOOLKIT-037 measured for the typewriter reveal. Resolve to the nearest
--: script at or below the pointer.
local sorted_targets = {}
for t, _ in pairs(slot_of) do sorted_targets[#sorted_targets + 1] = t end
table.sort(sorted_targets)

local function attribute(ptr)
    if ptr == nil then return nil, nil, nil, nil end
    local best = nil
    for _, t in ipairs(sorted_targets) do
        if t <= ptr then best = t else break end
    end
    if best == nil then return nil, nil, nil, nil end
    local ty = safe8(best + 2)
    local nx = safe16(best)
    return slot_of[best], ty, nx, ptr - best
end

local function write_row(kind, site, value, note)
    local slot, ty, nx, delta = attribute(value)
    local text = nil
    if in_shop_region(value) then
        --: type 0x03 bodies begin their UTF-16 payload at +4 from the script
        --: start; a cursor mid-body decodes from wherever it points.
        text = decode_body(value)
    elseif in_pool(value) then
        text = decode_body(value)
    end
    if delta and delta > 0 then
        note = note .. "; +" .. tostring(delta) .. " into script"
    end
    local quoted = ""
    if text ~= nil then quoted = '"' .. text:gsub('"', '""') .. '"' end
    file:write(string.format("%s,%d,%s,%s,%s,%s,%s,%s,%s,%s\n",
        kind, frames,
        current_map() and tostring(current_map()) or "",
        hex(site), hex(value),
        slot and tostring(slot) or "",
        ty and string.format("0x%02X", ty) or "",
        nx and tostring(nx) or "",
        quoted, note))
    file:flush()
    rows = rows + 1
end

--: Record what the emulated ROM says about the chosen scenario, so the capture
--: is self-describing and a reader never has to trust this comment block.
write_row("ARMED", SCENARIO, SCENARIO_HDR,
    "scenario array; header count " ..
    tostring(safe16(SCENARIO_HDR)) .. " type " ..
    string.format("0x%02X", safe8(SCENARIO_HDR + 2) or 0))
for s = 0, SCENARIO_N - 1 do
    local t = safe32(SCENARIO + s * 4)
    write_row("SCRIPT", SCENARIO + s * 4, t, "static slot " .. tostring(s))
end
for _, r in ipairs(RECORDS) do
    write_row("RECORD", r, safe32(r + RECORD_SCENARIO_FIELD),
        "shop record scenario field +0x0C")
end

-- CHANNEL B: the shop record's own code hooks.
local function hook_bp(name, addr)
    return emu:setBreakpoint(function(info)
        hook_hits = hook_hits + 1
        local r0 = tonumber(emu:readRegister("r0"))
        write_row("HOOK", addr, r0,
            name .. " reached x" .. tostring(hook_hits) .. "; r0 shown")
    end, addr)
end
local bp_a = hook_bp("HOOK_A", HOOK_A)
local bp_b = hook_bp("HOOK_B", HOOK_B)
local bp_c = hook_bp("HOOK_C", HOOK_C)

-- CHANNEL C: the Data Crystal message-display claim. Record r0 and r1 both, so
-- the claim that r1 carries a text value is tested rather than assumed.
local bp_dc = emu:setBreakpoint(function(info)
    dc_hits = dc_hits + 1
    local r1 = tonumber(emu:readRegister("r1"))
    if dc_hits <= 60 or dc_hits % 500 == 0 then
        write_row("DC-MSG", DC_MESSAGE_BP, r1,
            "Data Crystal 0x0801226A x" .. tostring(dc_hits) ..
            "; r1 shown, claimed to be text-related")
    end
end, DC_MESSAGE_BP)

-- CHANNEL D: breakpoint-installation control. Low counts are expected.
local bp_live = emu:setBreakpoint(function(info)
    liveness = liveness + 1
    if liveness <= 3 or liveness % 1000 == 0 then
        write_row("LIVENESS", INTERPRETER, nil,
            "shared interpreter reached x" .. tostring(liveness))
    end
end, INTERPRETER)

-- CHANNEL A: the live dialogue cursor, plus the Data Crystal RAM lead.
local last_primary = nil
local last_alt = nil
local last_dc_ram = nil

local function dump_struct(note)
    for k = 0, STRUCT_WORDS - 1 do
        local addr = STRUCT_BASE + STRING_OFFSET - 32 + 4 * k
        local v = safe32(addr)
        if in_shop_region(v) or in_pool(v) then
            write_row("STRUCT-WORD", addr, v, note)
        end
    end
end

callbacks:add("frame", function()
    frames = frames + 1

    local primary = safe32(STRING_SLOT)
    if primary ~= last_primary then
        last_primary = primary
        if in_shop_region(primary) then
            shop_hits = shop_hits + 1
            write_row("SHOP-CURSOR", STRING_SLOT, primary,
                "live cursor inside shop region #" .. tostring(shop_hits))
            if shop_hits <= 40 then
                dump_struct("neighbourhood of shop cursor #" .. tostring(shop_hits))
            end
        elseif in_pool(primary) then
            write_row("POOL-CURSOR", STRING_SLOT, primary,
                "live cursor in declared pool, NOT shop")
        end
    end

    local alt = safe32(ALT_SLOT)
    if alt ~= last_alt then
        last_alt = alt
        if in_shop_region(alt) then
            write_row("SHOP-ALT", ALT_SLOT, alt, "alt field inside shop region")
        elseif in_pool(alt) then
            write_row("POOL-ALT", ALT_SLOT, alt, "alt field in declared pool")
        end
    end

    --: The Data Crystal RAM lead. Record EVERY transition, pointer-like or not,
    --: because the claim is about dialogue state and a small counter would be
    --: just as interesting as a pointer.
    local dc = safe32(DC_RAM_SLOT)
    if dc ~= last_dc_ram then
        last_dc_ram = dc
        write_row("DC-RAM", DC_RAM_SLOT, dc,
            "0x0202BA70 changed; claimed dialogue start/state")
    end
end)

callbacks:add("frame", function()
    if frames % 1800 == 0 then
        write_row("HEARTBEAT", nil, nil,
            "alive; shop cursors " .. tostring(shop_hits) ..
            ", hooks " .. tostring(hook_hits) ..
            ", dc-msg " .. tostring(dc_hits) ..
            ", liveness " .. tostring(liveness))
    end
end)

local marker = assert(io.open(done_path, "w"), "cannot open marker")
marker:write("armed\n")
marker:close()

print([[TOOLKIT-038 scenario watch armed]])
print([[walk into a Z-Mart and talk to the shopkeeper]])
print([[log: ]] .. log_path)
