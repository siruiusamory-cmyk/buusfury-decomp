-- TOOLKIT-029: runtime evidence that the SDK-authored map 10 placement is
-- loaded and INSTANTIATED by the original Buu's Fury engine.
--
-- Read-only with respect to emulated memory and input: this file contains no
-- key-writing or memory-writing calls at all, so the read-only observer
-- guarantee enforced by tests/unit/test_mgba_capture.py stays true. Any input
-- driving belongs in a separate driver script, per the standing rule that
-- observers stay read-only. (The test greps for the API names, so they are
-- deliberately not spelled out here.)
--
-- WHY THIS EXISTS. TOOLKIT-028 produced a canonical-derived ROM whose map 10
-- object array was expanded from 2 slots to 3, with the new slot pointing at an
-- authored placement body written into verified free space. That is a STATIC
-- result. Nothing in it proves the engine reads the third slot.
--
-- WHAT THE ENGINE ACTUALLY DOES (TOOLKIT-024 disassembly, verbatim loop at
-- 0x08008C9E..0x08008CD6):
--     0x08008CA2  ldrb r0,[r0,#0x04]   ; MapEntry+0x04 = unsigned byte COUNT
--     0x08008CA8  ldr  r0,[r4,#0x04]   ; loop head
--     0x08008CAC  ldr  r0,[r0,#0x14]   ; MapEntry+0x14 = pointer array base
--     0x08008CAE  ldr  r6,[r0,r1]      ; array[index] -> record body
--     0x08008CB0  ldr  r0,[r6,#0x04]   ; body+0x04 flags -> skip predicate
--     0x08008CBE  ldr  r2,[r6,#0x00]   ; body+0x00 = factory pointer
--     0x08008CC0  bl   0x08046AA4      ; __call_via veneer -> factory
-- So a third slot is consumed if and only if the count byte reads 3, and the
-- record is constructed if and only if the 0x08004784 predicate accepts its
-- flags word. The authored body copies flags (0) from canonical slot 0, so it
-- should be accepted on exactly the same terms as a canonical record.
--
-- METHOD. Poll once per frame; do NOT set breakpoints. Breakpoints on the map
-- loader would halt inside a load and change the timing of the very thing being
-- measured, and P-006C recorded that broad trap sets collapse gameplay speed.
--
-- Two independent channels are recorded, and they answer DIFFERENT questions.
-- Conflating them would be the main way to overclaim here, so they are kept in
-- separate columns and separate notes:
--
--   CHANNEL 1 - STRUCTURE THE ENGINE IS POINTED AT.
--   0x03001980 holds the live MapEntry pointer (established by ROM-007, which
--   reads it as ACTIVE_MAP_POINTER_PACKET "m3001980,4"). MapEntry index is
--   (pointer - 0x0808E2E0) / 0x38, so map 10 sits at 0x0808E510. Reading the
--   count and array base through that live pointer shows the engine is looking
--   at the EXPANDED structure. This alone does NOT prove instantiation.
--
--   CHANNEL 2 - LIVE OBJECTS ACTUALLY BUILT.
--   Scan EWRAM for objects whose stored source-record pointer is the authored
--   body 0x087EA400. A constructed placement retains a reference to the record
--   it was built from; canonical slot 0 (0x080728FC) is scanned identically as
--   an IN-RUN POSITIVE CONTROL. If the canonical control is found and the
--   authored one is not, that is a real negative and must be reported as one.
--   If NEITHER is found, the scan itself is uninformative and proves nothing -
--   that case is labelled so it can never be read as a refutation.
--
-- The control is what makes a negative result trustworthy. VERTICAL-002's
-- surviving 4-hit wolf was exactly this kind of unplanned in-run control, and
-- it is why that result could distinguish a record-level cause from a global one.

local MAP_ENTRY_BASE    = 0x0808E2E0
local MAP_ENTRY_SIZE    = 0x38
local ACTIVE_MAP_PTR    = 0x03001980
-- Target map. Map 40 (resolver key 0x01,0x0C) is the map the private savestate
-- actually loads into, which is why the authored placement was built there
-- rather than into map 10: an entity that cannot be reached cannot be observed.
local TARGET_INDEX      = 40
local AUTHORED_BODY     = 0x087EA400   -- authored placement body
local AUTHORED_ARRAY    = 0x087EA420   -- relocated 5-slot pointer array
local CANON_ARRAY       = 0x08075690   -- canonical 4-slot array
-- Canonical map 40 bodies. Slot 1 is the CLONE SOURCE, so it is the tightest
-- possible positive control: if the scan can see it but not the authored body,
-- the difference is the authoring and nothing else.
local CANON_BODY_0      = 0x08075638   -- canonical slot 1 body = clone SOURCE
local CANON_BODY_1      = 0x08075670   -- canonical slot 3 body
local PLACEMENT_FACTORY = 0x0800FD55   -- placement-family factory tag (thumb bit)

local EWRAM_LO = 0x02000000
local EWRAM_HI = 0x02040000

-- Output location. inject_mgba_lua.ps1 sets the global `rom011_marker_path`
-- before dofile()ing this script, and that path is already validated to sit
-- beneath the ignored build tree. Deriving the CSV paths from it keeps every
-- generated artifact inside the run directory without a second contract, and
-- without depending on environment variables, which do not survive UI-driven
-- injection into an already-running mGBA.
local run_dir = nil
if type(rom011_marker_path) == "string" then
    run_dir = rom011_marker_path:match("^(.*)/[^/]*$")
end
local function in_run(name)
    if run_dir then return run_dir .. "/" .. name end
    return name
end

local out = os.getenv("TOOLKIT029_OUT") or in_run("toolkit029-watch.csv")
local file = assert(io.open(out, "w"), "cannot open output: " .. tostring(out))
file:write("frame,map_index,map_entry,count,array_base,slot0,slot1,slot2,",
           "body_factory,body_flags,body_type,body_pos_low,body_pos_high,",
           "refs_authored,refs_canon0,refs_canon1,note\n")
file:flush()

local scan_out = os.getenv("TOOLKIT029_SCAN") or (out .. ".scan.csv")
local scan_file = assert(io.open(scan_out, "w"), "cannot open scan output")
scan_file:write("frame,kind,ewram_address,offset,source_record\n")
scan_file:flush()

assert(emu ~= nil, "mGBA did not attach the emulation core")
assert(emu:getGameCode() == "AGB-BG3E", "unexpected game code")
assert(emu:romSize() == 8388608, "unexpected ROM size")

local frame = 0
local last_key = nil
local seen_target = false
local scanned_on_map10 = 0

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

-- Count EWRAM words equal to each watched record pointer, and log where they
-- were found. P-006C measured a full stepped EWRAM scan at ~0.1 s, so this is
-- affordable, but it is still only run on the target map and only a bounded
-- number of times.
local function scan_for_sources(tag)
    local n_auth, n_c0, n_c1 = 0, 0, 0
    local addr = EWRAM_LO
    while addr < EWRAM_HI do
        local w = safe32(addr)
        if w == AUTHORED_BODY then
            n_auth = n_auth + 1
            scan_file:write(string.format("%d,%s,0x%08X,,0x%08X\n", frame, tag, addr, w))
        elseif w == CANON_BODY_0 then
            n_c0 = n_c0 + 1
            scan_file:write(string.format("%d,%s,0x%08X,,0x%08X\n", frame, tag, addr, w))
        elseif w == CANON_BODY_1 then
            n_c1 = n_c1 + 1
            scan_file:write(string.format("%d,%s,0x%08X,,0x%08X\n", frame, tag, addr, w))
        end
        addr = addr + 4
    end
    scan_file:flush()
    return n_auth, n_c0, n_c1
end

local function h(v) if v == nil then return "" end return string.format("0x%08X", v) end
local function d(v) if v == nil then return "" end return tostring(v) end

callbacks:add("frame", function()
    frame = frame + 1
    -- Poll at 4 Hz. The map pointer changes only on a load, so a per-frame read
    -- would produce 60x the rows for no extra evidence.
    if frame % 15 ~= 0 then return end

    local entry = safe32(ACTIVE_MAP_PTR)
    if entry == nil or entry < MAP_ENTRY_BASE then return end
    local offset = entry - MAP_ENTRY_BASE
    if offset % MAP_ENTRY_SIZE ~= 0 then return end
    local index = offset // MAP_ENTRY_SIZE
    if index < 0 or index >= 452 then return end

    local count = safe8(entry + 0x04)
    local array = safe32(entry + 0x14)
    if count == nil or array == nil then return end

    local on_target = (index == TARGET_INDEX)

    -- Emit one row per distinct (map,count,array) state. On the target map also
    -- emit while the scan budget is unspent, so the dwell is visible.
    local key = string.format("%d:%d:%08X", index, count, array)
    if key == last_key and not on_target then return end
    last_key = key

    local s0 = array ~= 0 and safe32(array) or nil
    local s1 = array ~= 0 and safe32(array + 4) or nil
    -- The AUTHORED slot is the LAST one, index count-1, because the expansion
    -- appends. Reading a fixed slot 2 was wrong: on map 40 the authored record
    -- is slot 4, and slot 2 is an untouched canonical sibling, so the decoded
    -- "body" columns described the wrong record entirely.
    local s2 = (array ~= 0 and count >= 1) and safe32(array + (count - 1) * 4) or nil

    local bf, bfl, bt, bpl, bph = nil, nil, nil, nil, nil
    local ra, rc0, rc1 = nil, nil, nil
    local note = ""

    if on_target then
        if not seen_target then
            seen_target = true
            note = note .. "first-entry-map10|"
        end
        if array == AUTHORED_ARRAY then
            note = note .. "authored-array-live|"
        elseif array == CANON_ARRAY then
            note = note .. "canonical-array-live|"
        end
        if s2 ~= nil then
            bf  = safe32(s2)
            bfl = safe32(s2 + 0x04)
            bt  = safe32(s2 + 0x08)
            local pos = safe32(s2 + 0x0C)
            if pos then
                bpl = pos & 0xFFFF
                bph = (pos >> 16) & 0xFFFF
            end
            if s2 == AUTHORED_BODY then note = note .. "slot2-is-authored-body|" end
            if bf == PLACEMENT_FACTORY then note = note .. "slot2-placement-family|" end
        end

        -- Bounded instantiation scan. 12 samples is enough to cover the load
        -- settling without turning the run into a scan loop.
        if scanned_on_map10 < 12 then
            scanned_on_map10 = scanned_on_map10 + 1
            ra, rc0, rc1 = scan_for_sources("map10")
            if ra and ra > 0 then
                note = note .. "AUTHORED-RECORD-REFERENCED-IN-EWRAM|"
            end
            if (rc0 and rc0 > 0) or (rc1 and rc1 > 0) then
                note = note .. "canonical-control-present|"
            else
                -- Without the control, absence of the authored reference is not
                -- evidence of anything. Say so in the row itself.
                note = note .. "CONTROL-ABSENT-scan-uninformative|"
            end
        end
    end

    file:write(string.format("%d,%d,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n",
        frame, index, h(entry), d(count), h(array),
        h(s0), h(s1), h(s2), h(bf), h(bfl), h(bt), d(bpl), d(bph),
        d(ra), d(rc0), d(rc1), note))
    file:flush()
end)

-- Armed marker: written only after the frame callback is installed, so its
-- presence means the observer is genuinely live rather than merely loaded.
-- inject_mgba_lua.ps1 supplies the path and waits on it (the ROM-010 fix that
-- made readiness fail-closed instead of timing-dependent).
local marker = os.getenv("TOOLKIT029_MARKER") or rom011_marker_path
if type(marker) == "string" then
    local m = io.open(marker, "w")
    if m then m:write("armed\n") m:close() end
end
