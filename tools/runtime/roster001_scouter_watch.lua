-- APPEARANCE-ROSTER-EXPANSION-001 read-only observer.
--
-- WHAT IT MEASURES. The ticket's claim is that an authored appearance at index
-- 232 is safe once the roster object the engine builds from the seen-flag array
-- grows with the table. The chain is:
--
--   authored record index >= 232
--     -> the seen flag for that index (block+0xC5+(i>>3), bit i&7)
--       -> the builder's append of one entry per set flag
--         -> the display list, whose count the canonical object keeps at +0x3B4
--           -> the engine resolving the record, and the actor it bound
--
-- The object is reached through the context stack at IWRAM 0x03000F90, which is
-- where the builder's caller hands it. Its index count is at +0x10, the display
-- count at +0x3D4 in a relocated build and +0x3B4 in the canonical one, and the
-- two tail bases at +0xB58 / +0xB60. Reading the CANONICAL display-count offset
-- as well as the grown one is what distinguishes "the object grew" from "the
-- object was left at 0xB20 and the display count was overwritten".
--
-- WHAT IT DOES NOT DO. No emulated memory is written. The only emulated-state
-- change is the controller register through mGBA's own `emu:setKeys`, bounded by
-- the schedule below, and it writes only host files inside the run directory.
--
-- LIVENESS. A silent channel is not a negative, so the report states whether the
-- frame callback ran at all, how far the game advanced, and whether the input
-- schedule was reached, beside the measurements. Input is not proof by itself:
-- PROCESS LAUNCHED, OBSERVED STOP and any causal claim stay separate levels.
--
-- Environment, set by the launcher: TOOLKIT031_OUT names the run's log file; the
-- observer writes beside it. ROSTER001_FRAME_LIMIT bounds the run so the session
-- finishes by itself. ROSTER001_DRIVE=1 presses Select, which the game's own
-- controls documentation gives as the Scouter button, and Start for the pause
-- menu, with a picture beside each step.

local OUT = os.getenv("CAPACITY001_OUT")
    or os.getenv("TOOLKIT031_OUT")
    or "roster001/run.csv"
local DIR = OUT:match("^(.*)[/\\][^/\\]*$") or "."
local LIMIT = tonumber(os.getenv("ROSTER001_FRAME_LIMIT") or "3600")
local DRIVE = os.getenv("ROSTER001_DRIVE") == "1"
-- The launcher injects this global; writing it is the arm signal.
local MARKER = rom011_marker_path

-- Game Boy Advance key bits, as mGBA numbers them.
local A, B, SELECT, START = 0x0001, 0x0002, 0x0004, 0x0008
local RIGHT, LEFT, UP, DOWN = 0x0010, 0x0020, 0x0040, 0x0080

-- The engine's state block, and the two places the roster object can be found.
local BLOCK = 0x03001068
local BITSET = BLOCK + 0xC5
local CONTEXT = 0x03000F90
local KNOWN_GOOD_SIZE = 0xB20
local GROWN_SIZE = 0xB80
local GROWN_SECOND_COUNT = 0x3D4
local GROWN_TAIL_A = 0xB58
local GROWN_TAIL_B = 0xB60
local CANONICAL_SECOND_COUNT = 0x3B4

local HOLD = 8

-- One picture per step, so an empty report still says what the screen was.
local SCHEDULE = {}
if DRIVE then
    SCHEDULE = {
        { 420, SELECT },   -- the Scouter, per the game's controls
        { 500, SELECT },
        { 520, A }, { 560, A }, { 600, RIGHT }, { 640, A }, { 680, DOWN },
        { 720, A }, { 760, LEFT }, { 800, A },
        { 900, B },        -- back out
        { 1000, START },   -- the pause menu
        { 1080, START },
        { 1120, A }, { 1180, DOWN }, { 1240, A }, { 1300, DOWN }, { 1360, A },
        { 1460, B }, { 1520, B },
    }
end

local frame, started = 0, nil
local callback_id
local input_pulses, screenshots, object_count = 0, 0, 0
-- Declared before anything reads them: a local declared later is a global here,
-- and a nil global is how an instrument dies without saying so.
local hits, arm_results, handler_errors = {}, {}, 0
local search_dumps = 0
local seen = { flag232 = false, max_index = 0 }
local objects = {}

local function dir_file(name)
    return string.format("%s/%s", DIR, name)
end

local function note(name, text)
    local f = io.open(dir_file(name), "w")
    if not f then return end
    f:write(text)
    f:close()
end

-- The roster object is passed on the context stack. Its own slot 1 is dispatched
-- while it is there, so sampling that word each frame catches it.
local function sample_object()
    local obj = emu:read32(CONTEXT)
    if obj == 0 or obj < 0x02000000 or obj > 0x03008000 then return end
    if objects[obj] then return end
    local count = emu:read32(obj + 0x10)
    if count > 0x1000 then return end
    local entry = { address = obj, count = count,
                    grown = emu:read32(obj + GROWN_SECOND_COUNT),
                    canonical = emu:read32(obj + CANONICAL_SECOND_COUNT),
                    tail_a = emu:read32(obj + GROWN_TAIL_A),
                    tail_b = emu:read32(obj + GROWN_TAIL_B) }
    -- The first entry is an appearance index when the object is the list.
    entry.first_index = emu:read32(obj + 0x14)
    objects[obj] = entry
    object_count = object_count + 1
end

local function report_lines()
    local lines = {}
    lines[#lines + 1] = string.format("frames=%d started=%s limit=%d",
        frame, tostring(started), LIMIT)
    lines[#lines + 1] = string.format(
        "liveness frame_callback=ran input_pulses=%d screenshots=%d handler_errors=%d " ..
        "search_dumps=%d", input_pulses, screenshots, handler_errors, search_dumps)
    -- The seen flag for the authored index: one bit, inside the saved record.
    for _, index in ipairs({ 231, 232, 233, 239 }) do
        local byte = emu:read8(BITSET + (index >> 3))
        local bit = (byte >> (index & 7)) & 1
        lines[#lines + 1] = string.format(
            "flag index=%d byte_addr=0x%08X value=0x%02X set=%s",
            index, BITSET + (index >> 3), byte, tostring(bit == 1))
    end
    lines[#lines + 1] = string.format("block_count_word_at_0xE4=%d",
        emu:read32(BLOCK + 0xE4))
    for address, entry in pairs(objects) do
        lines[#lines + 1] = string.format(
            "object=0x%08X entries=%d first_index=%d grown_display=0x%08X " ..
            "canonical_display=0x%08X tail_a=0x%08X tail_b=0x%08X",
            address, entry.count, entry.first_index, entry.grown,
            entry.canonical, entry.tail_a, entry.tail_b)
    end
    for _, line in ipairs(arm_results) do lines[#lines + 1] = "arm " .. line end
    lines[#lines + 1] = string.format("builder_hits=%d", #hits)
    for _, line in ipairs(hits) do lines[#lines + 1] = "hit " .. line end
    lines[#lines + 1] = string.format(
        "expected grown_display=0x%X canonical_display=0x%X tail_a=0x%X tail_b=0x%X",
        GROWN_SECOND_COUNT, CANONICAL_SECOND_COUNT, GROWN_TAIL_A, GROWN_TAIL_B)
    return lines
end

local function write_report(tag)
    note("report.txt", table.concat(report_lines(), "\n") .. "\n")
    note("report-" .. tag .. ".txt", table.concat(report_lines(), "\n") .. "\n")
end

local function journal() write_report("live") end

local function report()
    write_report("final")
    note("done.txt", "done\n")
end

-- --- the roster object's own instructions ------------------------------------
--
-- Three sites inside the builder and its flag writer, because the claim is about
-- what those instructions do once the count passes the canonical 232:
--
--   0x08024F8E  str r0,[r3,#4]   the append. r0 is the appearance index being
--                                appended, r1 is object+0x10 and r3 is
--                                object+0x14+4*count, so the base is r1-0x10 and
--                                the store lands at r3+4.
--   0x08024F92  cmp r0,#0xE8     the loop bound, whose immediate the build raises.
--   0x08025E90  strb r2,[r1,#5]  the seen-flag write, with the index in r5.
local function safe(fn, ...)
    local ok, value = pcall(fn, ...)
    if ok then return value end
    return nil
end

local function reg(name) return tonumber(safe(emu.readRegister, emu, name)) end
local function hex(v) return v and string.format("0x%08X", v) or "nil" end

local function record(site, text)
    if #hits >= 60 then return end
    hits[#hits + 1] = string.format("frame=%d site=%s %s", frame, site, text)
end

local APPEND_STORE = 0x08024F8E
local ROSTER_BOUND = 0x08024F92
local FLAG_WRITE = 0x08025E90

local function guarded(body)
    -- A handler that raises stops the whole script, which is how an instrument
    -- goes quiet without saying so. Every body is counted and contained.
    return function()
        local ok = pcall(body)
        if not ok then handler_errors = handler_errors + 1 end
    end
end

local function on_append()
    local index, base_plus, target = reg("r0"), reg("r1"), reg("r3")
    if index == nil or base_plus == nil or target == nil then return end
    local base = base_plus - 0x10
    record("append", string.format(
        "index=%d object=%s store=%s grown_display=%s canonical_display=%s",
        index, hex(base), hex(target + 4), hex(base + GROWN_SECOND_COUNT),
        hex(base + CANONICAL_SECOND_COUNT)))
end

local function on_bound() record("roster_bound", "bound=232 canonical") end

local function on_flag()
    local index = reg("r5")
    record("flag_write", string.format("index=%s past_canonical=%s",
        tostring(index), tostring(index ~= nil and index >= 232)))
end

for _, site in ipairs({
    { name = "append", address = APPEND_STORE, handler = guarded(on_append) },
    { name = "roster_bound", address = ROSTER_BOUND, handler = guarded(on_bound) },
    { name = "flag_write", address = FLAG_WRITE, handler = guarded(on_flag) },
}) do
    local ok = pcall(emu.setBreakpoint, emu, site.handler, site.address)
    arm_results[#arm_results + 1] = string.format("site=%s address=%s ok=%s",
        site.name, hex(site.address), tostring(ok))
end

-- --- who does the search look up, and what do they carry? --------------------
--
-- The search at 0x08027948 is handed the object's embedded component pointer,
-- which is the object plus 0x5C. So the object is r0 - 0x5C, and dumping its words
-- shows what an actor actually carries where the search reads. That is the
-- measurement the reachability question needs: which sprite a real actor resolves
-- from, and therefore which sprite id an authored record would have to bind.
local SEARCH_ENTRY = 0x08027948
local SEARCH_DUMPS = 12

local function on_search_input()
    local component = reg("r0")
    if component == nil or component < 0x02000000 then return end
    if search_dumps >= SEARCH_DUMPS then return end
    search_dumps = search_dumps + 1
    local object = component - 0x5C
    local words = {}
    for i = 0, 31 do
        words[#words + 1] = string.format("%08X", emu:read32(object + i * 4))
    end
    local lines = io.open(dir_file("search-objects.txt"), search_dumps == 1 and "w" or "a")
    if lines then
        lines:write(string.format("frame=%d object=%08X component=%08X second=%s\n",
            frame, object, component, hex(reg("r1"))))
        lines:write("  words=" .. table.concat(words, " ") .. "\n")
        lines:close()
    end
end

local ok_search = pcall(emu.setBreakpoint, emu, guarded(on_search_input), SEARCH_ENTRY)
arm_results[#arm_results + 1] = string.format("site=search_entry address=%s ok=%s",
    hex(SEARCH_ENTRY), tostring(ok_search))

callback_id = callbacks:add("frame", function()
    frame = frame + 1
    if started == nil then
        -- The launcher loads the savestate after this script is read, so the
        -- schedule is timed from the first frame the game is actually running.
        if frame < 400 then return end
        started = frame
    end
    local elapsed = frame - started
    for _, step in ipairs(SCHEDULE) do
        if elapsed == step[1] then
            emu:setKeys(step[2])
            input_pulses = input_pulses + 1
            emu:screenshot(string.format("%s/press-%05d.png", DIR, elapsed))
            screenshots = screenshots + 1
        elseif elapsed == step[1] + HOLD then
            emu:setKeys(0)
        end
    end
    sample_object()
    if elapsed % 200 == 0 and elapsed > 0 then journal() end
    if elapsed % 400 == 0 and elapsed > 0 then
        emu:screenshot(string.format("%s/at-%05d.png", DIR, elapsed))
        screenshots = screenshots + 1
        note("progress.txt", string.format(
            "elapsed=%d objects=%d inputs=%d\n",
            elapsed, object_count, input_pulses))
    end
    if elapsed >= LIMIT then
        report()
        callbacks:remove(callback_id)
    end
end)

note("armed.txt", "armed\n")
if MARKER then
    local signal = io.open(MARKER, "w")
    if signal then
        signal:write("armed\n")
        signal:close()
    end
end
