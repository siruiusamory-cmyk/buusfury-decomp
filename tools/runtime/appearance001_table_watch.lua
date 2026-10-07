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
local SPRITE_ACCESSOR = 0x08000158
local RECORD_CONSUMER = 0x08025E50
-- The animation frame advance, once per animating actor per frame. It is the
-- liveness channel that a loaded, idle scene still executes: if this is silent,
-- the run was not in gameplay and says nothing about the appearance path.
local ANIMATION_ADVANCE = 0x0800DE6E

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
local CANONICAL_COUNT = 232
local EXPANDED_FROM = 0x00800000
local EXPANDED_TO = 0x01000000

local K = { A = 0x0001, B = 0x0002, SELECT = 0x0004, START = 0x0008,
            RIGHT = 0x0010, LEFT = 0x0020, UP = 0x0040, DOWN = 0x0080 }
local HOLD = 40
-- Walk in each direction, then open the pause/status screen, which is where the
-- engine's roster walk runs. The presses are the operator's own, expressed as a
-- schedule because this run has no operator.
local SCHEDULE = { { 120, K.START }, { 240, K.A }, { 360, K.A },
                   { 500, K.RIGHT }, { 620, K.LEFT }, { 740, K.DOWN },
                   { 860, K.UP }, { 1000, K.START }, { 1120, K.A },
                   { 1240, K.A } }

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

local frame = 0
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
local liveness = { accessor = 0, accessor_first = nil, consumer = 0,
                   consumer_first = nil, animation = 0, animation_first = nil }
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
        if first and base ~= nil and base >= EXPANDED_FROM and base < EXPANDED_TO then
            write_found("search", string.format(
                "search_index=%d\nsearch_table_base=%s\nsearch_record=%s\n" ..
                "search_record_sprite_id=%s\nsearch_record_words=%s\n",
                index, hex(base), hex(record),
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

local function on_accessor(_info)
    liveness.accessor = liveness.accessor + 1
    if liveness.accessor_first == nil then liveness.accessor_first = frame end
end

local function on_consumer(_info)
    liveness.consumer = liveness.consumer + 1
    if liveness.consumer_first == nil then liveness.consumer_first = frame end
end

local function on_animation(_info)
    liveness.animation = liveness.animation + 1
    if liveness.animation_first == nil then liveness.animation_first = frame end
end

local SITES = {
    { name = "search_record_read", address = SEARCH_RECORD_READ, handler = on_search },
    { name = "roster_bound", address = ROSTER_BOUND, handler = on_roster },
    { name = "sprite_accessor", address = SPRITE_ACCESSOR, handler = on_accessor },
    { name = "record_consumer", address = RECORD_CONSUMER, handler = on_consumer },
    { name = "animation_advance", address = ANIMATION_ADVANCE, handler = on_animation },
}

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

local function summarise(note)
    local f = io.open(DIR .. "/appearance001-summary.txt", "w")
    if not f then return end
    if note then f:write("note=" .. note .. "\n") end
    f:write(string.format("frames=%d\n", frame))
    f:write(string.format("frames_after_state_load=%s\n",
        tostring(started and (frame - started) or nil)))
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
    f:write(string.format("liveness_accessor_hits=%d\n", liveness.accessor))
    f:write(string.format("liveness_accessor_first_frame=%s\n",
        tostring(liveness.accessor_first)))
    f:write(string.format("liveness_consumer_hits=%d\n", liveness.consumer))
    f:write(string.format("liveness_consumer_first_frame=%s\n",
        tostring(liveness.consumer_first)))
    f:write(string.format("liveness_animation_hits=%d\n", liveness.animation))
    f:write(string.format("liveness_animation_first_frame=%s\n",
        tostring(liveness.animation_first)))
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
    if search.expanded_hits > 0 then
        instrument = "appearance site fired"
    elseif liveness.animation > 0 or liveness.accessor > 0
            or liveness.consumer > 0 or roster.hits > 0 then
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
    for _, item in ipairs(SCHEDULE) do
        scheduled[item[1]] = item[2]
        scheduled[item[1] + HOLD] = 0
    end
end
local rearm = {}
for _, offset in ipairs(REARM_FRAMES) do rearm[#rearm + 1] = offset end

local started = nil
local callback_id
callback_id = callbacks:add("frame", function()
    frame = frame + 1
    if started == nil then
        if not loaded() then
            -- The load never arrived: say so rather than run a schedule against
            -- whatever the core was showing before it.
            if frame > LIMIT then
                summarise("state-loaded.txt never appeared")
                callbacks:remove(callback_id)
            end
            return
        end
        started = frame
    end
    local elapsed = frame - started
    if scheduled[elapsed] ~= nil then emu:setKeys(scheduled[elapsed]) end
    for _, offset in ipairs(rearm) do
        if elapsed == offset then arm_all("frame" .. tostring(elapsed)) end
    end
    if elapsed >= LIMIT then
        summarise()
        callbacks:remove(callback_id)
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
