-- FRIEND-V3-WT-SPLIT-CONTAINER-001, RELEASE 2.1: does the RUNNING GAME follow slot
-- 1083's repointed pointer and put Bulma's new scanner biography on screen?
--
-- READ-ONLY. Registers and memory are read; host files are written only inside the run
-- directory. No emulated memory is written and no key is pressed by THIS file. Driving
-- code, when a run needs it, is a separate allowlisted file loaded through
-- FV3WT001_DRIVER (tools/runtime/fv3wt001_input_driver.lua or
-- tools/runtime/npc_talk_driver.lua); the driver section at the bottom of this file does
-- nothing unless the caller names one.
--
-- WHAT THE EDIT UNDER TEST IS. Release 2.1 moves text-table slot 1083 to file
-- 0x9AC618 (release address 0x089AC618) and repoints the slot's own word at file
-- 0x6BCE8 + 1083*4. Everything else is release 2. Slot 1083 is BULMA'S BIOGRAPHY and
-- it is not a loose string: appearance record 22 binds the pair (name 1082, text 1083),
-- and the Scouter character screen draws exactly that pair, so a read of slot 1083 is
-- the biography being displayed.
--
-- WHERE THE ENGINE READS IT, measured in the disassembly rather than inferred from the
-- table layout (Ghidra, canonical baserom, addresses are GAME code and therefore do not
-- move with the edited image):
--
--   the character screen's panel routine FUN_08025056 gets its record from
--   r7 = 0x0874D380 + 16 * record_index, and then:
--
--     0x080251ac-0x080251b4   the NAME index: ldr r0,[object+0x14+4*i] then
--                             ldr r0,[r0,#4] then that record's +0x00
--     0x080251be  ldr r1,[0x08025328]     <- pool word = the text pointer table
--     0x080251c2  ldr r1,[r1,r0*4]        <- the NAME string pointer, r0 = name index
--     0x080252e6  ldrh r0,[r7,#2]         <- the TEXT index, i.e. 1083 for record 22
--     0x080252e8  ldr r1,[0x08025328]     <- same pool word
--     0x080252ec  ldr r2,[r1,r0*4]        <- BREAKPOINT B: the DESCRIPTION pointer
--
--   A breakpoint fires BEFORE its instruction, so at B r0 is the text index and r1 is
--   the table base; the word the engine is about to load is read32(r1 + r0*4), read
--   here exactly as the instruction indexes it. That word IS the address the game will
--   draw from, which is why this is the observation and not a restatement of the edit:
--   it reports the pointer the LOADED IMAGE holds, through the engine's own table base,
--   at the instant the engine fetches it.
--
--   The name load at 0x080251c2 is armed too, so the run reports the on-screen label
--   beside the biography: record 22 must read "Bulma" with the new text, and "Chi-Chi"
--   with the retail text.
--
-- LIVENESS, and why the reader site is the channel. A silent channel is not evidence of
-- absence (docs/skills/mgba-runtime.md section 8), so three channels are armed beside the
-- target, none of them about slot 1083 specifically:
--   * the character screen's constructor 0x08025620 (the entry point of the panel): it
--     firing says the screen exists in this run and its record read is being watched;
--   * the other appearance-table text reader 0x0802539E (ldrh r0,[r5,#2], whose string
--     is loaded two instructions later from the same table): it fires whenever any
--     appearance record's text is drawn, so it proves the table-read path itself is
--     live in this session;
--   * the dispatch thunk 0x08046AA4, which fires hundreds of thousands of times per run
--     on this build and is the heartbeat that says the core was executing at all.
-- The report states which of the three cases the run is in: target silent with liveness
-- silent = the instrument is unproven; target silent with liveness firing = a real
-- negative for this run and this route; target firing = the bio was fetched.
--
-- THE ROM-SIZE TRAP. An observer that names the ROM sizes it accepts throws on load when
-- the candidate changes and the launcher then reports "Lua script did not report ready",
-- which reads like an injection fault. The size is therefore not asserted against a list
-- here; it is recorded, and only the game code is asserted.
--
-- ENVIRONMENT (set by the launcher)
--   FV3WT001_HORIZON     frame bound, default 3000, floor 2000
--   FV3WT001_IDLE_STOP   frames without any hit before the run ends, default 1500;
--                        0 disables it, which is what a hand-driven session wants
--   FV3WT001_SHOT_EVERY  screenshot cadence, default 120; 0 disables screenshots
--   FV3WT001_DRIVER      path of an allowlisted input driver to dofile, or unset

local SITE_NAME = 0x080251C2   -- ldr r1,[r1,r0*4]  the on-screen name pointer
local SITE_TEXT = 0x080252EC   -- ldr r2,[r1,r0*4]  the description pointer
local SITE_LINE = 0x0802539E   -- ldrh r0,[r5,#2]   the other appearance text reader
local SITE_TEXT_ROW = 0x08025EC2 -- ldrh r0,[r0,#2] the third appearance text reader
local SITE_SCREEN = 0x08025620 -- the character screen's constructor
local LIVENESS = 0x08046AA4    -- the ARM/Thumb dispatch thunk: fires constantly

-- THE RAW STRING DRAW, so a biography shown OUTSIDE the character panel is still caught.
-- A message path that draws an appearance record's description directly does not go
-- through the panel's table load; it hands the finished string pointer to the text
-- routines below. Measured in the disassembly:
--   0x0803DADA  push {r4,r5,r6,r7,lr} / add r7,r1,#0  -> the pointer is r1 (short labels)
--   0x0803DD66  push {r0,r1,r2,r4,r5,r6,r7,lr} / ...  -> the pointer is r2 (the long,
--               wrapping draw the panel's own description call at 0x080252F2 uses)
-- A breakpoint fires BEFORE the instruction, so at 0x0803DD66 r2 is still the caller's
-- string pointer, and at 0x0803DADA r1 still is. Either one equal to the appended
-- biography body is that string being handed to the composer.
local DRAW_LONG = 0x0803DD66   -- pointer in r2
local DRAW_SHORT = 0x0803DADA  -- pointer in r1

-- The two pool words that name the same text pointer table. Read so the report can say
-- which base the engine actually used, rather than assuming the brief's number.
local POOL_A = 0x08025328
local POOL_B = 0x080256C0
local TEXT_TABLE = 0x0806BCE8  -- the value both pools are expected to hold

-- The edited site: the pointer slot and the appended string, as they exist in the image
-- under test. Reported by name so a hit on the new body cannot be confused with a hit on
-- the orphaned retail span at 0x089491E8.
local BIO_SLOT = 1083
local BIO_OLD = 0x089491E8     -- release 2's string, left in place and unreachable
local BIO_NEW = 0x089AC618     -- the appended string this release points at

-- Appearance record 22 (file 0x74D4E0) binds name 1082 and text 1083.
local APPEARANCE_BASE = 0x0874D380
local APPEARANCE_STRIDE = 16
local BULMA_RECORD = 22
local BULMA_NAME_INDEX = 1082
local BULMA_TEXT_INDEX = 1083
local SEEN_BLOCK = 0x03001068  -- appearance seen flags live in [block + 0xC5 + (i>>3)]
local SEEN_ARRAY = 0x0300112D  -- = [0x03001068 + 0xC5], measured; record 22 -> bit 6

local ACTIVE_MAP_PTR = 0x03001980
local MAP_FIRST = 0x0808E2E0
local MAP_STRIDE = 0x38

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")

local function knob(name, default)
    return tonumber(os.getenv(name) or "") or default
end

local HORIZON = math.max(knob("FV3WT001_HORIZON", 3000), 2000)
local IDLE_STOP = knob("FV3WT001_IDLE_STOP", 1500)
local SHOT_EVERY = knob("FV3WT001_SHOT_EVERY", 120)
local DRIVER = os.getenv("FV3WT001_DRIVER")

-- DECLARED HERE, BEFORE EVERY FUNCTION THAT READS IT. A breakpoint can fire during the
-- savestate load, which happens after this file is read, so a `frame` local declared
-- later in the file is still nil inside a handler and the first hit throws
-- "bad argument #3 to 'format' (number expected, got nil)" - measured, on the first run
-- of this observer, in marker.txt. Handlers must never be able to see an unset counter.
local frame = 0

assert(emu ~= nil, "mGBA did not attach the emulation core")
assert(emu.setBreakpoint and emu.clearBreakpoint, "requires the 0.11 breakpoint API")
local code = emu:getGameCode()
assert(code == "BG3E" or code == "AGB-BG3E", "unexpected game code: " .. tostring(code))
local ROM_SIZE = emu:romSize()

local done = false
local function finish(status)
    if done then return end
    done = true
    local handle = io.open(done_path, "w")
    if handle then
        handle:write(status .. "\n")
        handle:close()
    end
end

local function hex(value)
    if value == nil then return "" end
    return string.format("0x%08X", value)
end

local function safe(fn, ...)
    local ok, value = pcall(fn, ...)
    if ok then return value end
    return nil
end

local function reg(name) return tonumber(safe(emu.readRegister, emu, name)) end
local function r32(address) return safe(emu.read32, emu, address) end
local function r16(address) return safe(emu.read16, emu, address) end

-- The units the engine is about to draw, read from the pointer it just fetched. Units
-- outside printable ASCII are emitted as <XXXX> so a control unit is visible rather than
-- silently dropped, and a comma becomes a semicolon because these rows are CSV.
local function text_of(pointer, units)
    if not pointer or pointer < 0x08000000 then return "?" end
    local parts = {}
    for index = 0, units - 1 do
        local value = r16(pointer + index * 2)
        if value == nil then break end
        if value == 0 then break end
        if value >= 0x20 and value < 0x7F then
            parts[#parts + 1] = string.char(value)
        else
            parts[#parts + 1] = string.format("<%04X>", value)
        end
    end
    return (table.concat(parts):gsub(",", ";"))
end

local function run()
    local log = assert(io.open(exp_dir .. "observe.csv", "w"))
    log:write("kind,frame,detail\n")
    log:flush()

    local hits = assert(io.open(exp_dir .. "hits.csv", "w"))
    hits:write("site,hit,frame,index,slot_value,pointer_in_new,pointer_in_old,text,note\n")
    hits:flush()

    local arm = assert(io.open(exp_dir .. "arm.txt", "w"))

    local counts = { name = 0, text = 0, line = 0, screen = 0, dispatch = 0,
                     draw_long = 0, draw_short = 0 }
    local names_seen, texts_seen, records_seen = {}, {}, {}
    local name_order, text_order = {}, {}
    local first_target_frame = nil
    local target_hits = 0
    local target_rows = 0
    local index_unreadable = 0
    local base_seen = {}

    local function note(kind, format, ...)
        local text = select("#", ...) > 0 and string.format(format, ...) or format
        log:write(string.format("%s,%d,%s\n", kind, frame, text))
        log:flush()
    end

    local function map_index()
        local entry = r32(ACTIVE_MAP_PTR)
        if entry == nil or entry < MAP_FIRST then return nil end
        local offset = entry - MAP_FIRST
        if offset % MAP_STRIDE ~= 0 then return nil end
        return offset // MAP_STRIDE
    end

    -- Which table base the two consumers actually instruct against, read from the image
    -- rather than assumed from the brief.
    local pool_a, pool_b = r32(POOL_A), r32(POOL_B)

    local function seen_flag(index)
        local byte = safe(emu.read8, emu, SEEN_ARRAY + (index >> 3))
        if byte == nil then return nil end
        return (byte >> (index & 7)) & 1
    end

    -- The appearance record's own words, so a hit can be attributed to a record rather
    -- than to a register value the reader has to trust.
    local function record_words(index)
        local at = APPEARANCE_BASE + index * APPEARANCE_STRIDE
        local name_index, text_index = r16(at), r16(at + 2)
        return name_index, text_index, r32(at + 4), r32(at + 8), r32(at + 12)
    end

    local function arm_sites()
        local arms = {}
        local ids = {}
        local function arm_one(label, address, handler)
            local ok, handle = pcall(emu.setBreakpoint, emu, handler, address)
            arms[#arms + 1] = string.format("%s 0x%08X ok=%s id=%s", label, address,
                tostring(ok), tostring(handle))
            if type(handle) == "number" then ids[#ids + 1] = handle end
        end

        local function on_name()
            counts.name = counts.name + 1
            local r0, r1 = reg("r0"), reg("r1")
            local pointer = (r0 ~= nil and r1 ~= nil) and r32(r1 + r0 * 4) or nil
            local slot = r0
            local text = text_of(pointer, 40)
            names_seen[text] = (names_seen[text] or 0) + 1
            if names_seen[text] == 1 then name_order[#name_order + 1] = text end
            if target_rows < 200 then
                target_rows = target_rows + 1
                hits:write(string.format("name,%d,%d,%s,%s,%s,%s,%s,%s\n",
                    counts.name, frame, tostring(slot), hex(pointer),
                    tostring(pointer == BIO_NEW), tostring(pointer == BIO_OLD),
                    text, ""))
                hits:flush()
            end
        end

        local function on_text()
            counts.text = counts.text + 1
            local r0, r1 = reg("r0"), reg("r1")
            local slot = r0
            local pointer = nil
            local note_text = "read"
            if r0 == nil or r1 == nil then
                note_text = "register_unreadable"
            else
                if base_seen[r1] == nil then
                    base_seen[r1] = 0
                    note("table_base", "r1=0x%08X (the table the description load indexes)",
                        r1)
                end
                base_seen[r1] = base_seen[r1] + 1
                local value = r32(r1 + r0 * 4)
                if value == nil then
                    note_text = "read_failed"
                else
                    pointer = value
                end
            end

            -- The record this text belongs to: the same r7 the record load uses.
            local r7 = reg("r7")
            local record, index = nil, nil
            if r7 ~= nil and r7 >= APPEARANCE_BASE then
                local offset = r7 - APPEARANCE_BASE
                if offset % APPEARANCE_STRIDE == 0 and offset // APPEARANCE_STRIDE < 0xE8 then
                    index = offset // APPEARANCE_STRIDE
                    record = true
                end
            end
            if index == nil then index_unreadable = index_unreadable + 1 end

            local text = text_of(pointer, 240)
            texts_seen[text] = (texts_seen[text] or 0) + 1
            if texts_seen[text] == 1 then text_order[#text_order + 1] = text end
            if index ~= nil then
                if records_seen[index] == nil then
                    records_seen[index] = { pointer = pointer, text = text, frame = frame }
                    note("record_drawn", "index=%d slot=%s pointer=%s text=%s",
                        index, tostring(slot), hex(pointer), text)
                end
            end

            -- THE TARGET: the engine fetched the biography slot and is about to draw
            -- whatever pointer this image holds there.
            if slot == BULMA_TEXT_INDEX then
                target_hits = target_hits + 1
                if first_target_frame == nil then first_target_frame = frame end
                note("TARGET_SLOT_1083",
                    "frame=%d record=%s pointer=%s new_body=%s old_body=%s text=%s",
                    frame, index ~= nil and tostring(index) or "unreadable",
                    hex(pointer), tostring(pointer == BIO_NEW), tostring(pointer == BIO_OLD),
                    text)
                if target_rows < 200 then
                    target_rows = target_rows + 1
                    hits:write(string.format("text,%d,%d,%s,%s,%s,%s,%s,%s\n",
                        counts.text, frame, index ~= nil and tostring(index) or "?",
                        tostring(slot), hex(pointer), tostring(pointer == BIO_NEW),
                        tostring(pointer == BIO_OLD), text, note_text))
                    hits:flush()
                end
            end
        end

        local function on_line()
            counts.line = counts.line + 1
            if counts.line <= 200 then
                local r5 = reg("r5")
                local index = r5 and r16(r5) or nil
                hits:write(string.format("line,%d,%d,%s,%s,%s,%s,%s,%s\n",
                    counts.line, frame, tostring(index), "?", "?", "false", "false",
                    "", "other_appearance_text_reader"))
                hits:flush()
            end
        end

        local function on_screen()
            counts.screen = counts.screen + 1
            if counts.screen <= 20 then
                note("SCREEN_CONSTRUCTOR", "frame=%d appearance_screen_built", frame)
                pcall(function()
                    emu:screenshot(string.format("%sscreen_%06d.png", exp_dir, frame))
                end)
            end
        end

        local function on_dispatch() counts.dispatch = counts.dispatch + 1 end

        -- The two raw draw entries. Compared by pointer only: the composer is handed a
        -- finished string, so an equality with the appended body is the whole claim.
        local function on_draw(kind)
            return function()
                counts[kind] = counts[kind] + 1
                local pointer = (kind == "draw_long") and reg("r2") or reg("r1")
                if pointer ~= nil and (pointer == BIO_NEW or pointer == BIO_OLD) then
                    note("DRAW_" .. string.upper(kind),
                        "frame=%d pointer=%s new_body=%s old_body=%s text=%s",
                        frame, hex(pointer), tostring(pointer == BIO_NEW),
                        tostring(pointer == BIO_OLD), text_of(pointer, 240))
                end
                if counts[kind] <= 200 and target_rows < 400 then
                    local text = text_of(pointer, 48)
                    if text ~= "" and #text > 3 then
                        target_rows = target_rows + 1
                        hits:write(string.format("%s,%d,%d,%s,%s,%s,%s,%s,%s\n",
                            kind, counts[kind], frame, "?", "?", tostring(pointer == BIO_NEW),
                            tostring(pointer == BIO_OLD), text, hex(pointer)))
                        hits:flush()
                    end
                end
            end
        end

        arm_one("name_pointer", SITE_NAME, on_name)
        arm_one("text_pointer", SITE_TEXT, on_text)
        arm_one("other_text_reader", SITE_LINE, on_line)
        arm_one("third_text_reader", SITE_TEXT_ROW, on_line)
        arm_one("screen_constructor", SITE_SCREEN, on_screen)
        arm_one("dispatch_liveness", LIVENESS, on_dispatch)
        arm_one("draw_long", DRAW_LONG, on_draw("draw_long"))
        arm_one("draw_short", DRAW_SHORT, on_draw("draw_short"))

        arm:write(table.concat(arms, "\n") .. "\n")
        arm:flush()
        for _, line in ipairs(arms) do note("arm", "%s", line) end
        return ids
    end

    note("identity", "rom_size=%d game_code=%s", ROM_SIZE, tostring(code))
    note("pool_words", "0x%08X=%s 0x%08X=%s table_expected=0x%08X",
        POOL_A, hex(pool_a), POOL_B, hex(pool_b), TEXT_TABLE)
    note("appearance_22", "record=0x%08X name_index=%d text_index=%d sprite=%s portrait=%s",
        APPEARANCE_BASE + BULMA_RECORD * APPEARANCE_STRIDE,
        (select(1, record_words(BULMA_RECORD))) or -1,
        (select(2, record_words(BULMA_RECORD))) or -1,
        hex(select(3, record_words(BULMA_RECORD))),
        hex(select(4, record_words(BULMA_RECORD))))
    local text_slot_value = r32(TEXT_TABLE + BULMA_TEXT_INDEX * 4)
    note("slot_1083_word", "address=0x%08X value=%s is_new_body=%s is_old_body=%s",
        TEXT_TABLE + BULMA_TEXT_INDEX * 4, hex(text_slot_value),
        tostring(text_slot_value == BIO_NEW), tostring(text_slot_value == BIO_OLD))

    local ids = arm_sites()

    -- Rearm: the savestate load happens AFTER this file runs, and a state load can drop
    -- the breakpoints installed before it. The first run of this family looked exactly
    -- like a silent path for that reason, so the armed set is reinstalled a few frames
    -- into the run and the report says so.
    local REARM_AT = { 60, 240, 900 }
    local rearmed = 0
    local last_hit_frame = 0
    local function total_hits()
        return counts.name + counts.text + counts.line + counts.screen
    end

    frame = 0   -- the counter itself is declared at the top of the file; see there
    local callback_id
    callback_id = callbacks:add("frame", function()
        frame = frame + 1
        if total_hits() > 0 then last_hit_frame = frame end

        if frame == 1 then
            note("bulma_seen_flag", "index=%d bit6=%s byte=0x%02X at=0x%08X",
                BULMA_RECORD, tostring(seen_flag(BULMA_RECORD) == 1),
                safe(emu.read8, emu, SEEN_ARRAY + (BULMA_RECORD >> 3)) or 0xFF,
                SEEN_ARRAY + (BULMA_RECORD >> 3))
            note("map_at_load", "map_index=%s", tostring(map_index()))
        end

        for _, at in ipairs(REARM_AT) do
            if frame == at and rearmed < #REARM_AT then
                for _, id in ipairs(ids) do pcall(function() emu:clearBreakpoint(id) end) end
                ids = arm_sites()
                rearmed = rearmed + 1
                note("rearm", "frame=%d armed_set=%d", frame, rearmed)
            end
        end

        if SHOT_EVERY > 0 and frame % SHOT_EVERY == 0 then
            pcall(function()
                emu:screenshot(string.format("%sshot_%06d.png", exp_dir, frame))
            end)
        end

        if frame % 300 == 0 then
            note("heartbeat",
                "dispatch=%d name=%d text=%d line=%d screen=%d map=%s bulma_bit=%s",
                counts.dispatch, counts.name, counts.text, counts.line, counts.screen,
                tostring(map_index()), tostring(seen_flag(BULMA_RECORD) == 1))
            local beat = io.open(exp_dir .. "heartbeat.txt", "w")
            if beat then
                beat:write(string.format(
                    "frame=%d dispatch=%d name=%d text=%d line=%d screen=%d\n",
                    frame, counts.dispatch, counts.name, counts.text, counts.line,
                    counts.screen))
                beat:close()
            end
        end

        local idle = IDLE_STOP > 0 and frame > 1200 and frame > last_hit_frame + IDLE_STOP
        if frame >= HORIZON or idle then
            callbacks:remove(callback_id)
            for _, id in ipairs(ids) do pcall(function() emu:clearBreakpoint(id) end) end

            note("summary", "frames=%d horizon=%d idle_stop=%d rearm=%d",
                frame, HORIZON, IDLE_STOP, rearmed)
            note("summary_counts",
                "dispatch=%d name=%d text=%d line=%d textrow=%d screen=%d draw_long=%d " ..
                "draw_short=%d rearm=%d",
                counts.dispatch, counts.name, counts.text, counts.line, counts.line,
                counts.screen, counts.draw_long, counts.draw_short, rearmed)
            note("summary_case",
                "target_hits=%d first_target_frame=%s index_unreadable=%d",
                target_hits, tostring(first_target_frame), index_unreadable)
            local target_fired = target_hits > 0
            local liveness_fired = counts.dispatch > 0
            local case
            if target_fired then
                case = "OBSERVED: the engine fetched text slot " .. BULMA_TEXT_INDEX
            elseif liveness_fired and total_hits() > 0 then
                case = "real negative for this route: nothing fetched slot " ..
                    BULMA_TEXT_INDEX .. " while the appearance text readers fired " ..
                    "at least once and the dispatch liveness channel fired"
            elseif liveness_fired and counts.draw_long + counts.draw_short > 0 then
                case = "real negative for the fetch, but the string composer ran: " ..
                    "slot " .. BULMA_TEXT_INDEX .. " was never fetched by the " ..
                    "appearance readers in this run"
            elseif liveness_fired then
                case = "unproven instrument for the screen: the dispatch channel fired " ..
                    "but no appearance text reader and no string draw ran, so the " ..
                    "screen was never drawn"
            else
                case = "nothing fired: the instrument is unproven"
            end
            note("case", "%s", case)

            -- Which pointers were drawn, so the report carries what the screen showed
            -- rather than only whether the target appeared.
            for _, text in ipairs(text_order) do
                note("text_drawn", "x%d %s", texts_seen[text], text)
            end
            for _, text in ipairs(name_order) do
                note("name_drawn", "x%d %s", names_seen[text], text)
            end

            log:close()
            hits:close()
            finish("done:frames=" .. tostring(frame) .. " target_hits=" .. tostring(target_hits))
            return
        end
    end)
end

local ok, err = xpcall(run, function(problem) return tostring(problem) end)
if not ok then finish("error:" .. tostring(err)) end

-- DRIVING CODE, LOADED BY NAME AND ONLY WHEN THE CALLER ASKS. It lives in its own
-- allowlisted file; this observer presses nothing itself. The saver passes
-- FV3WT001_DRIVER only when the run is meant to be driven.
if ok and DRIVER and #DRIVER > 0 then
    local loaded, problem = pcall(dofile, DRIVER)
    if not loaded then
        local handle = io.open(exp_dir .. "driver-error.txt", "w")
        if handle then
            handle:write(tostring(problem) .. "\n")
            handle:close()
        end
    end
end
