-- APPEARANCE-AUTHORING-GATE-001 read-only observer.
--
-- WHAT IT DOES NOT DO. It writes no emulated memory and touches no file outside
-- its run directory. Its only emulated-state change is the controller input
-- register, through mGBA's own `emu:setKeys`, and only when a schedule asks.
--
-- WHAT IT MEASURES. The ticket's claim is that the retail engine, with the
-- appearance table moved above canonical EOF and its three compiled count bounds
-- raised, reads the moved table and reaches the appended record. That is an
-- observation about one instruction, so it is made at the instruction:
--
--   0x08027968  ldr r0,[r6,#4]   ; the id search reads record[i].+0x04
--
-- `r6` there is `table + 16 * i`, `r4` is `i` and `r1` is the base the function
-- loaded. A hit whose base is above canonical EOF with an index at or past the
-- canonical 232, plus the record's own words, is the engine reading the new
-- record rather than a picture of it.
--
-- LIVENESS, AND WHY IT IS REPORTED AS A CASE. A silent breakpoint is not a
-- negative. Three more channels are armed, none of them about appearance
-- authoring: the roster walk's own patched bound (0x08024F92), the sprite-id
-- accessor (0x08000158) and the appearance-record consumer (0x08025E50). The
-- report states which case the run is in - nothing firing at all (the instrument
-- is unproven), liveness firing with the appearance site silent (the path was not
-- taken), or the appearance site firing - and it records whether each breakpoint
-- actually armed, because an unarmed instrument and an untaken path look
-- identical from the outside.
--
-- Environment, set by the launcher: TOOLKIT031_OUT names the run's log file; the
-- observer writes its report beside it. APPEARANCE001_FRAME_LIMIT bounds the run
-- so the session finishes by itself; APPEARANCE001_KEYS=1 drives a short
-- title/menu schedule, because a savestate taken on a menu runs no actor code.

local OUT = os.getenv("CAPACITY001_OUT")
    or os.getenv("TOOLKIT031_OUT")
    or "appearance001/toolkit031-execution.csv"
local DIR = OUT:match("^(.*)[/\\][^/\\]*$") or "."
local LIMIT = tonumber(os.getenv("APPEARANCE001_FRAME_LIMIT") or "3600")
local DRIVE = os.getenv("APPEARANCE001_KEYS") == "1"
-- The launcher injects this global; its CONTENT is the completion signal, so an
-- observer that only ever writes "armed" makes the wrapper wait for its backstop.
local MARKER = rom011_marker_path
local EXPECTED_POINTER = tonumber(os.getenv("CAPACITY001_EXPECTED_POINTER") or "")

local SEARCH_RECORD_READ = 0x08027968
local ROSTER_BOUND = 0x08024F92
local ANIMATION_ADVANCE = 0x0800DE6E
-- The table BASE-LOAD sites. A hit on one of these is the engine naming the
-- relocated table, whichever consumer it belongs to, and the register it leaves
-- the base in is read at the hit. They are the strongest evidence available
-- without needing an actor to carry the new id.
local BASE_SITES = {
    { name = "roster", address = 0x08024FA0, register = "r7" },
    { name = "panel", address = 0x08025086, register = "r1" },
    { name = "consumer", address = 0x08025E94, register = "r2" },
    { name = "constructor", address = 0x080273AC, register = "r1" },
    { name = "search", address = 0x08027962, register = "r1" },
    { name = "list", address = 0x08025380, register = "r1" },
}

-- The six reader FUNCTIONS' own entry points. None of them is named by a `bl` or
-- by a word in the image, so they are reached indirectly and their callers cannot
-- be read out statically. A count on each entry is what says WHICH game activity
-- consults the appearance table at all.
local ENTRY_SITES = {
    { name = "roster_walk", address = 0x08024F3C },
    { name = "record_panel", address = 0x08025056 },
    { name = "line_list", address = 0x08025354 },
    { name = "record_consumer", address = 0x08025E50 },
    { name = "actor_constructor", address = 0x08027390 },
    { name = "id_search", address = 0x08027948 },
}

-- The active MapEntry pointer, so the report can say which scene the run was in
-- and whether the core was running gameplay at all.
local ACTIVE_MAP_PTR = 0x03001980
local MAP_ENTRY_BASE = 0x0808E2E0
local MAP_ENTRY_SIZE = 0x38
local MAP_ENTRY_COUNT = 452

-- Re-arming is a diagnostic, not a design: if the savestate load drops the
-- breakpoints installed before it, the first run looks exactly like a run whose
-- path was never taken. Re-installing a few frames in separates the two.
local REARM_FRAMES = { 30, 120, 300 }

-- The canonical count, and the block the build places. Both are stated so the
-- observer reports what it saw rather than what it hoped for.
--
-- The register holds a GBA address, and the generated image maps file offset
-- 0x00800000 to GBA 0x08800000, so the test is on the ADDRESS window. Comparing
-- against the file-offset range is the mistake this constant exists to prevent.
local CANONICAL_COUNT = 232
local EXPANDED_FROM = 0x08800000
local EXPANDED_TO = 0x09000000

local function is_expanded(address)
    return address ~= nil and address >= EXPANDED_FROM and address < EXPANDED_TO
end

local K = { A = 0x0001, B = 0x0002, SELECT = 0x0004, START = 0x0008,
            RIGHT = 0x0010, LEFT = 0x0020, UP = 0x0040, DOWN = 0x0080 }
local HOLD = 40
-- Walk in each direction, then open the pause/status screen, which is where the
-- engine's roster walk runs. The presses are the operator's own, expressed as a
-- schedule because this run has no operator.
local SCHEDULE = { { 120, K.START }, { 300, K.R }, { 420, K.A },
                   { 540, K.R }, { 660, K.A }, { 780, K.B },
                   { 900, K.START }, { 1020, K.R }, { 1140, K.R },
                   { 1260, K.B }, { 1380, K.LEFT }, { 1500, K.A },
                   { 1620, K.A }, { 1740, K.A }, { 1860, K.A },
                   { 1980, K.A }, { 2100, K.A }, { 2220, K.A } }

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

local function reg(name) return tonumber(safe(emu.readRegister, emu, name)) end
local function r32(a) return tonumber(safe(emu.read32, emu, a)) end

local function map_index()
    local entry = r32(ACTIVE_MAP_PTR)
    if entry == nil or entry < MAP_ENTRY_BASE then return nil end
    local offset = entry - MAP_ENTRY_BASE
    if offset % MAP_ENTRY_SIZE ~= 0 then return nil end
    local index = math.floor(offset / MAP_ENTRY_SIZE)
    if index < 0 or index >= MAP_ENTRY_COUNT then return nil end
    return index
end

-- SELF-CALIBRATION. A breakpoint on an address nothing reaches and a breakpoint
-- channel that never fires look identical from the outside, so this mode removes
-- the guess: it samples the program counter from the frame callback, which is
-- known to run, then arms one breakpoint on the address it has actually seen most
-- often. A silent breakpoint after that is a statement about the channel, not
-- about the address.
local PC_PROBE = os.getenv("APPEARANCE001_PC_PROBE") == "1"
local PC_SAMPLE_UNTIL = tonumber(os.getenv("APPEARANCE001_PC_SAMPLE") or "120")
local pc_hist = {}
local pc_order = {}
local probe_pc = nil
local probe_armed = nil
local probe_hits = 0
--: A second probe on the hottest address in ROM, armed in the same run as the
--: hottest address in work RAM. If one fires and the other never does, the
--: question is the breakpoint's address space, not the game's behaviour.
local rom_probe_pc = nil
local rom_probe_hits = 0
local ROM_FLOOR = 0x08000000

local function note_pc(pc)
    if pc == nil then return end
    if pc_hist[pc] == nil then
        pc_hist[pc] = 0
        pc_order[#pc_order + 1] = pc
    end
    pc_hist[pc] = pc_hist[pc] + 1
end

local function top_pcs(limit, floor)
    local ranked = {}
    for _, pc in ipairs(pc_order) do
        if floor == nil or pc >= floor then
            ranked[#ranked + 1] = { pc = pc, count = pc_hist[pc] }
        end
    end
    table.sort(ranked, function(a, b) return a.count > b.count end)
    while #ranked > limit do table.remove(ranked) end
    return ranked
end

--: A frame boundary is usually inside the BIOS idle wait (0x000001C4 here), and a
--: scripted breakpoint there may not be installed at all. The probe therefore
--: prefers the hottest address in game memory, which is where the engine's own
--: code runs.
local GAME_MEMORY_FLOOR = 0x02000000

local function arm_probe(elapsed)
    local ranked = top_pcs(1, GAME_MEMORY_FLOOR)
    local scope = "game-memory"
    if #ranked == 0 then
        ranked = top_pcs(1)
        scope = "any-memory"
    end
    if #ranked == 0 then
        probe_armed = string.format("frame%d: no pc sampled", elapsed)
        return
    end
    probe_pc = ranked[1].pc
    local ok, handle = pcall(emu.setBreakpoint, emu, function(_info)
        probe_hits = probe_hits + 1
    end, probe_pc)
    probe_armed = string.format("frame%d: %s pc=%s sampled=%d ok=%s handle=%s",
        elapsed, scope, hex(probe_pc), ranked[1].count, tostring(ok),
        tostring(handle))
    local rom = top_pcs(1, ROM_FLOOR)
    if #rom > 0 then
        rom_probe_pc = rom[1].pc
        local rom_ok, rom_handle = pcall(emu.setBreakpoint, emu, function(_info)
            rom_probe_hits = rom_probe_hits + 1
        end, rom_probe_pc)
        probe_armed = probe_armed .. string.format(
            " | rom pc=%s sampled=%d ok=%s handle=%s", hex(rom_probe_pc),
            rom[1].count, tostring(rom_ok), tostring(rom_handle))
    end
    console:log("APPEARANCE001 pc probe armed: " .. probe_armed)
end

local frame = 0
-- Declared here, before every function that reads them: a local declared after a
-- function body is compiled as a GLOBAL reference inside it, so the summary read
-- nil for fields the callback was setting correctly.
local started = nil
local started_with_signal = nil
local shots = { [30] = true, [400] = true, [800] = true, [1500] = true,
                [2000] = true }
-- The savestate load goes through mGBA's Scripting prompt and takes seconds of
-- wall clock while the core keeps running, so a schedule counted from injection
-- time fires before the fixture resumes. The wrapper writes this signal after a
-- confirmed load.
local STATE_LOADED = DIR .. "/state-loaded.txt"
local function loaded()
    local f = io.open(STATE_LOADED, "r")
    if not f then return false end
    f:close()
    return true
end

local search = { hits = 0, expanded_hits = 0, max_index = -1, bases = {},
                 base_order = {}, records = {}, log = {} }
local roster = { hits = 0, max_index = -1, patched_bound_seen = false }
local liveness = { animation = 0, animation_first = nil }
--: Per base-load site: how many times it ran, and the bases it was seen to load.
local bases = {}
--: Per reader-function entry point: how many times the engine entered it.
local entries = {}
local arm_results = {}

local function note_base(base)
    if base == nil or search.bases[base] then return end
    search.bases[base] = true
    search.base_order[#search.base_order + 1] = base
end

local function write_found(what, details)
    local f = io.open(DIR .. "/FOUND-" .. what .. ".txt", "w")
    if not f then return end
    f:write("frame=" .. tostring(frame) .. "\n" .. details)
    f:close()
    -- A picture of the moment, so the hit carries the scene it happened in
    -- rather than leaving the operator to remember where they were.
    emu:screenshot(string.format("%s/FOUND-%s.png", DIR, what))
    console:log("APPEARANCE001 " .. what .. " at frame " .. tostring(frame))
end

-- --- the handlers ------------------------------------------------------------

local function on_search(_info)
    local index = reg("r4")
    local base = reg("r1")
    local record = reg("r6")
    if record == nil then return end
    search.hits = search.hits + 1
    note_base(base)
    if index ~= nil and index > search.max_index then search.max_index = index end
    -- The highest record index the engine ever addressed, with the base it
    -- addressed it through and the record's own four words. Index 232 is the
    -- authored record, so this is the observation the ticket is after.
    if index ~= nil and record ~= nil
            and (search.max_record == nil or index > search.max_record.index) then
        search.max_record = {
            index = index, base = base, record = record, frame = frame,
            words = { r32(record), r32(record + 4), r32(record + 8),
                      r32(record + 12) },
        }
    end
    if base ~= nil and base >= EXPANDED_FROM and base < EXPANDED_TO then
        search.expanded_hits = search.expanded_hits + 1
    end
    if index ~= nil and index >= CANONICAL_COUNT then
        local first = search.records[index] == nil
        search.records[index] = { base = base, record = record, frame = frame,
                                  word = r32(record + 4) }
        if #search.log < 40 then
            search.log[#search.log + 1] = string.format(
                "frame=%d index=%d base=%s record=%s sprite_id=%s", frame, index,
                hex(base), hex(record), tostring(search.records[index].word))
        end
        if first then
            write_found("search", string.format(
                "search_index=%d\nsearch_table_base=%s\nsearch_base_is_expanded=%s\n" ..
                "search_record=%s\nsearch_record_sprite_id=%s\n" ..
                "search_record_words=%s\n",
                index, hex(base), tostring(is_expanded(base)), hex(record),
                tostring(search.records[index].word),
                string.format("%08X %08X %08X %08X", r32(record) or 0,
                              r32(record + 4) or 0, r32(record + 8) or 0,
                              r32(record + 12) or 0)))
        end
    end
end

local function on_roster(_info)
    local index = reg("r0")
    roster.hits = roster.hits + 1
    if index ~= nil and index > roster.max_index then roster.max_index = index end
    if index ~= nil and index >= CANONICAL_COUNT then
        roster.patched_bound_seen = true
        write_found("bound", string.format(
            "bound_site=roster\nbound_index=%d\n", index))
    end
end

local function on_base(site)
    local state = bases[site.name]
    if state == nil then
        state = { hits = 0, values = {}, found = false }
        bases[site.name] = state
    end
    return function(_info)
        local base = reg(site.register)
        state.hits = state.hits + 1
        state.values[base] = (state.values[base] or 0) + 1
        if base ~= nil and is_expanded(base) and not state.found then
            state.found = true
            write_found("base-" .. site.name, string.format(
                "site=%s\naddress=%s\nregister=%s\nbase=%s\nframes=%d\n",
                site.name, hex(site.address), site.register, hex(base), frame))
        end
    end
end

local function on_animation(_info)
    liveness.animation = liveness.animation + 1
    if liveness.animation_first == nil then liveness.animation_first = frame end
end

--: A bounded event log: every entry into a reader function, with the frame and
--: the map at that moment. It is what turns "something happened once" into a
--: situation that can be re-entered on purpose.
local events = {}

local function note_event(site, extra)
    if #events >= 80 then return end
    events[#events + 1] = string.format("frame=%d map=%s site=%s %s", frame,
        tostring(map_index()), site, extra or "")
end

local function on_entry(site)
    local state = entries[site.name]
    if state == nil then
        state = { hits = 0, first = nil }
        entries[site.name] = state
    end
    return function(_info)
        state.hits = state.hits + 1
        if state.first == nil then
            state.first = frame
            write_found("entry-" .. site.name, string.format(
                "entry=%s\naddress=%s\nfirst_frame=%d\n", site.name,
                hex(site.address), frame))
        end
        if site.name == "actor_constructor" or site.name == "id_search"
                or site.name == "record_consumer" or site.name == "roster_walk" then
            note_event(site.name, string.format("arg1=%s arg2=%s",
                hex(reg("r1")), hex(reg("r2"))))
        end
    end
end

local SITES = {
    { name = "search_record_read", address = SEARCH_RECORD_READ, handler = on_search },
    { name = "roster_bound", address = ROSTER_BOUND, handler = on_roster },
    { name = "animation_advance", address = ANIMATION_ADVANCE, handler = on_animation },
}
for _, site in ipairs(BASE_SITES) do
    SITES[#SITES + 1] = { name = "base_" .. site.name, address = site.address,
                          handler = on_base(site) }
end
for _, site in ipairs(ENTRY_SITES) do
    SITES[#SITES + 1] = { name = "entry_" .. site.name, address = site.address,
                          handler = on_entry(site) }
end

local function arm_all(tag)
    for _, site in ipairs(SITES) do
        local ok, value = pcall(emu.setBreakpoint, emu, site.handler, site.address)
        arm_results[#arm_results + 1] = string.format(
            "arm %s site=%s address=%s ok=%s result=%s", tag, site.name,
            hex(site.address), tostring(ok), tostring(value))
    end
end

arm_all("start")

-- --- the report --------------------------------------------------------------

local function progress(elapsed)
    local f = io.open(DIR .. "/progress.txt", "w")
    if not f then return end
    f:write(string.format("elapsed_frames=%d\n", elapsed))
    f:write(string.format("active_map_index=%s\n", tostring(map_index())))
    f:write(string.format("search_hits=%d max_index=%d expanded_hits=%d\n",
        search.hits, search.max_index, search.expanded_hits))
    if search.max_record then
        f:write(string.format(
            "search_max_record index=%d frame=%d base=%s address=%s words=%s\n",
            search.max_record.index, search.max_record.frame,
            hex(search.max_record.base), hex(search.max_record.record),
            string.format("%08X %08X %08X %08X", search.max_record.words[1],
                          search.max_record.words[2], search.max_record.words[3],
                          search.max_record.words[4])))
    end
    for _, site in ipairs(BASE_SITES) do
        local state = bases[site.name]
        if state then
            for value, count in pairs(state.values) do
                f:write(string.format("base_value %s %s x%d\n", site.name,
                    hex(value), count))
            end
        end
    end
    f:write(string.format("roster_hits=%d max_index=%d patched_bound=%s\n",
        roster.hits, roster.max_index, tostring(roster.patched_bound_seen)))
    f:write(string.format("animation_advance_hits=%d\n", liveness.animation))
    for _, site in ipairs(BASE_SITES) do
        local state = bases[site.name]
        f:write(string.format("base %s hits=%d found=%s\n", site.name,
            state and state.hits or 0, tostring(state and state.found or false)))
    end
    for _, site in ipairs(ENTRY_SITES) do
        local state = entries[site.name]
        f:write(string.format("entry %s hits=%d first_frame=%s\n", site.name,
            state and state.hits or 0, tostring(state and state.first or nil)))
    end
    f:close()
    local ev = io.open(DIR .. "/events.txt", "w")
    if ev then
        for _, line in ipairs(events) do ev:write(line .. "\n") end
        ev:close()
    end
end

local function summarise(note)
    local f = io.open(DIR .. "/appearance001-summary.txt", "w")
    if not f then return end
    if note then f:write("note=" .. note .. "\n") end
    f:write(string.format("frames=%d\n", frame))
    f:write(string.format("frames_after_state_load=%s\n",
        tostring(started and (frame - started) or nil)))
    f:write(string.format("started_on_state_loaded_signal=%s\n",
        tostring(started_with_signal)))
    f:write(string.format("active_map_index=%s\n", tostring(map_index())))
    f:write(string.format("expected_pointer=%s\n",
        EXPECTED_POINTER and hex(EXPECTED_POINTER) or "not supplied"))
    f:write(string.format("search_hits=%d\n", search.hits))
    f:write(string.format("search_expanded_hits=%d\n", search.expanded_hits))
    f:write(string.format("search_max_index=%d\n", search.max_index))
    f:write(string.format("search_distinct_bases=%d\n", #search.base_order))
    for _, base in ipairs(search.base_order) do
        f:write(string.format("search_base %s%s\n", hex(base),
            (EXPECTED_POINTER ~= nil and base == EXPECTED_POINTER)
                and " (the declared relocated table)" or ""))
    end
    f:write(string.format("roster_hits=%d\n", roster.hits))
    f:write(string.format("roster_max_index=%d\n", roster.max_index))
    f:write(string.format("patched_bound_seen=%s\n",
        tostring(roster.patched_bound_seen)))
    f:write(string.format("liveness_animation_hits=%d\n", liveness.animation))
    f:write(string.format("liveness_animation_first_frame=%s\n",
        tostring(liveness.animation_first)))
    for _, site in ipairs(BASE_SITES) do
        local state = bases[site.name]
        if state == nil then
            f:write(string.format("base_site %s address=%s hits=0\n", site.name,
                hex(site.address)))
        else
            f:write(string.format("base_site %s address=%s hits=%d found=%s\n",
                site.name, hex(site.address), state.hits, tostring(state.found)))
            for value, count in pairs(state.values) do
                f:write(string.format("base_value %s %s x%d\n", site.name,
                    hex(value), count))
            end
        end
    end
    for _, site in ipairs(ENTRY_SITES) do
        local state = entries[site.name]
        f:write(string.format("entry_site %s address=%s hits=%d first_frame=%s\n",
            site.name, hex(site.address), state and state.hits or 0,
            tostring(state and state.first or nil)))
    end
    if PC_PROBE then
        f:write(string.format("pc_probe_distinct_pcs=%d\n", #pc_order))
        f:write(string.format("pc_probe_armed=%s\n", tostring(probe_armed)))
        f:write(string.format("pc_probe_armed_pc=%s\n", hex(probe_pc)))
        f:write(string.format("pc_probe_hits=%d\n", probe_hits))
        f:write(string.format("rom_probe_pc=%s\n", hex(rom_probe_pc)))
        f:write(string.format("rom_probe_hits=%d\n", rom_probe_hits))
        for _, item in ipairs(top_pcs(20)) do
            f:write(string.format("pc %s count=%d\n", hex(item.pc), item.count))
        end
    end
    local count = 0
    for _ in pairs(search.records) do count = count + 1 end
    f:write(string.format("records_at_or_past_canonical_count=%d\n", count))
    for index, item in pairs(search.records) do
        f:write(string.format(
            "record index=%d base=%s address=%s sprite_id=%s frame=%d\n",
            index, hex(item.base), hex(item.record), tostring(item.word),
            item.frame))
    end
    for _, line in ipairs(search.log) do f:write(line .. "\n") end
    for _, line in ipairs(arm_results) do f:write(line .. "\n") end
    f:close()

    local instrument = "nothing fired: the instrument is UNPROVEN"
    if PC_PROBE then
        if probe_hits > 0 then
            instrument = string.format(
                "breakpoint channel WORKS: %d hits on %s", probe_hits,
                hex(probe_pc))
        else
            instrument = string.format(
                "breakpoint channel SILENT on an observed-live pc %s (%d samples)",
                hex(probe_pc), probe_pc and (pc_hist[probe_pc] or 0) or 0)
        end
    elseif search.expanded_hits > 0 then
        instrument = "appearance site fired"
    elseif liveness.animation > 0 or roster.hits > 0 then
        instrument = "liveness fired, appearance search silent"
    end
    local marker = io.open(DIR .. "/done.txt", "w")
    if marker then
        marker:write("done\n" .. instrument .. "\n")
        marker:close()
    end
    -- The wrapper's completion signal: any content that is not "armed".
    if MARKER then
        local signal = io.open(MARKER, "w")
        if signal then
            signal:write("done:" .. instrument .. "\n")
            signal:close()
        end
    end
    console:log("APPEARANCE001 summary written: " .. instrument)
end

local scheduled = {}
if DRIVE then
    -- Walk the map, because the path that consults the appearance table is a map
    -- transition: hold each direction in turn for nine pulses, then tap A, and
    -- repeat. Built here rather than typed out, so the length is a parameter.
    local dirs = { K.RIGHT, K.LEFT, K.UP, K.DOWN }
    for leg = 0, 23 do
        local at = 120 + leg * 400
        for pulse = 0, 8 do
            SCHEDULE[#SCHEDULE + 1] = { at + pulse * 40, dirs[(leg % 4) + 1] }
        end
        SCHEDULE[#SCHEDULE + 1] = { at + 380, K.A }
    end
    for _, item in ipairs(SCHEDULE) do
        scheduled[item[1]] = item[2]
        scheduled[item[1] + HOLD] = 0
    end
end
local rearm = {}
for _, offset in ipairs(REARM_FRAMES) do rearm[#rearm + 1] = offset end

local callback_id
callback_id = callbacks:add("frame", function()
    frame = frame + 1
    if started == nil then
        -- `state-loaded.txt` is the capacity wrapper's confirmed-load signal. The
        -- toolkit session writes no such file, so a caller that uses it would
        -- otherwise sit here for the whole budget: fall back after a bounded wait
        -- rather than reporting an empty run as a measurement.
        if not loaded() and frame < 400 then
            return
        end
        started = frame
        started_with_signal = loaded()
    end
    local elapsed = frame - started
    if PC_PROBE then
        note_pc(reg("pc"))
        if probe_armed == nil and elapsed >= PC_SAMPLE_UNTIL then
            arm_probe(elapsed)
        end
    end
    if scheduled[elapsed] ~= nil then emu:setKeys(scheduled[elapsed]) end
    -- A scene the engine is not updating looks exactly like a scene whose code
    -- paths are cold, so the run keeps a periodic visual trail: when a hit lands,
    -- the frame it landed on has a picture beside it.
    if elapsed > 0 and elapsed % 1200 == 0 then
        emu:screenshot(string.format("%s/shot-%05d.png", DIR, elapsed))
    end
    for _, offset in ipairs(rearm) do
        if elapsed == offset then arm_all("frame" .. tostring(elapsed)) end
    end
    if elapsed >= LIMIT then
        summarise()
        callbacks:remove(callback_id)
    elseif elapsed % 300 == 0 then
        -- A human-driven session has no known end, so the counters are written
        -- while it runs instead of only when it stops.
        progress(elapsed)
    end
end)

local armed = io.open(DIR .. "/armed.txt", "w")
if armed then
    armed:write("armed\n")
    armed:close()
end
if MARKER then
    local signal = io.open(MARKER, "w")
    if signal then
        signal:write("armed\n")
        signal:close()
    end
end
console:log("APPEARANCE001 observer armed: limit=" .. tostring(LIMIT) ..
    " drive=" .. tostring(DRIVE) .. " map=" .. tostring(map_index()) ..
    " out=" .. DIR)
