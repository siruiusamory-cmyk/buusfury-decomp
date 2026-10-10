-- FRIEND-V3-WT-SPLIT-CONTAINER-001: the dialogue container-selector census and the
-- split-route observer. READ-ONLY: registers and memory are read, host files are
-- written inside the run directory, no emulated memory is written and no key is
-- pressed. Driving code, when a run needs it, is a SEPARATE file
-- (tools/runtime/fv3wt001_input_driver.lua) and never this one.
-- (docs/skills/mgba-runtime.md sections 7 and 8.)
--
-- WHY THE SELECTOR IS READ FROM MEMORY AND FROM THE ENGINE'S OWN INDEX, NOT DECODED.
-- Both table-load sites have the identical shape, and `emu:readRegister` is unreliable
-- from inside a frame callback on this build (the pc read returns a constant), so the
-- handle is taken from the word the `ldr` is about to load - stronger evidence than a
-- register snapshot. The four instruction words between the two sites are byte-identical:
--
--   0x08012240  ldr   r0, [r5, #4]    <- the packed handle (FIRST site's record: r5)
--   0x08012244  lsls  r0, r0, #0x1A
--   0x08012246  lsrs  r0, r0, #0x18
--   0x08012248  ldr   r0, [r1, r0]    <- BREAKPOINT A: r1 + r0*4
--
--   0x080122c6  ldr   r0, [r4, #4]    <- the packed handle (SECOND site's record: r4)
--   0x080122ca  lsls  r0, r0, #0x1A
--   0x080122cc  lsrs  r0, r0, #0x18
--   0x080122ce  ldr   r0, [r1, r0]    <- BREAKPOINT B: r1 + r0*4
--
-- A breakpoint fires BEFORE its instruction executes, so at A the handle is still in
-- memory at 0x08012240 + r5 and at B at 0x080122C6 + r4. For the same reason, at the
-- breakpoint r1 still holds the table base and r0 still holds the index, so the word the
-- engine is about to load is read32(r1 + r0*4) and that r0 IS the engine's selector.
--
-- WHY THAT MATTERS. tools/webfoot/handles.py declares the selector to be bits 0-5
-- (`value & 0x3F`), while a literal reading of the two shifts above yields bits 26-31
-- (`value >> 26`). A prior ticket's observer ("selector = handle % 64") assumed the
-- first and then read the table at `base + selector*4`, so its agreement was a
-- restatement of its own assumption, not a measurement. Here both readings are reported
-- side by side and the engine's actual r0 decides which one is real.
--
-- LIVENESS. Two channels, because the last ticket's run measured the dialogue copier
-- 0x0801227A at ZERO hits across 240 frames with a live game (build/toolkit031/
-- fv3text001-pc-01/pc.txt: copier_hits=0, dispatch_hits=5954). A savestate restores an
-- already-copied dialogue, so the copier is silent by construction there and is NOT a
-- liveness channel for a state-loaded run. The dispatch thunk 0x08046AA4 is: it fires
-- thousands of times per run on this build, measured. The copier is still armed and
-- logged, because its silence or its firing is itself a result.
--
-- THE RESOLVED CONTAINER, AND THE WORDS THE ENGINE IS ABOUT TO COPY (added by the release-2
-- run). A selector is only half the route: the next thing to prove is that the address the
-- table returns is the appended container and that the units the copier will take out of it
-- are the approved wording. So each site hit also reads the table word the `ldr` is about to
-- load, read32(r1 + r0*4) with r1 and r0 exactly as the instruction indexes them, and then
-- reads the first 40 units at the record's own decoded start inside that container. MEASURED
-- on this image: a kind-0 container carries an 8-byte header (four zero bytes then the
-- declared size as u32), so a handle's start lands at container + 8 + start - container 3
-- reads 00 00 00 00 36 FF 00 00 then "#That was weak." at +8, and the same image's handles
-- decode to text only with that +8. The raw window at container + start is therefore not
-- used as the text; the header offset is stated instead of assumed.
--
-- WHAT IT WRITES
--   route.csv       one row per 60 frames: frame, dispatch hits, site A hits, site B hits,
--                   copier hits.
--   sites.csv       the first 200 hits at A and at B: site, hit, handle, both candidate
--                   selectors, start, length, the engine's own index, and whether that
--                   index could be read, the RESOLVED container address, the first 40 units
--                   the copier will take from container + 8 + start, and the record's whole
--                   text when its length field is bounded.
--   histogram.txt   heartbeats, the engine-index histogram, the selector histogram per
--                   site per reading, and the count of hits whose selector is 7 or above.
--   copies.csv      every copier call: source register, source pointer, unit count and the
--                   first COPY_UNITS units copied from that pointer.
--   arm.txt         the arm result of each breakpoint, written once, so a failed arm can
--                   never be read as a quiet channel.
--   copies-at-60.txt  the copier source pointers seen in the first 60 frames, counted.
--   marker.txt      "armed" on injection, then the end status.
--   shot_*.png      every SHOT_EVERY frames.

local SITE_A = 0x08012248          -- record loader 0x08012230, ldr r0,[r1,r0]
local SITE_B = 0x080122CE          -- record reader 0x080122B4, ldr r0,[r1,r0]
local COPIER = 0x0801227A          -- the dialogue record copier
local DISPATCH = 0x08046AA4        -- the ARM/Thumb dispatch thunk: liveness

-- The word the next instruction loads. Measured defect, fixed: the handle loads are
-- `ldr r0,[r5,#4]` at 0x08012240 and `ldr r0,[r4,#4]` at 0x080122C6, and each site sits
-- FOUR bytes after its own load, so the record-relative offset is simply +4:
--   0x08012240 -> 0x08012244 (site A)
--   0x080122C6 -> 0x080122CA (site B)
-- The first version derived this as SITE_A + (0x08012240 - 0x08012248) = SITE_A - 8 and
-- read r5 - 8, a CODE word, then returned early when that word was not a handle. Every
-- hit was therefore suppressed and the channel looked silent. A failed read must never be
-- able to hide a hit, so the hit count is incremented before any read is attempted.
local A_WORD = 4
local B_WORD = 4

-- THE TWO READINGS, AND WHICH ONE THE RUN DECIDES. tools/webfoot/handles.py declares the
-- selector to be bits 0-5 (`value & 0x3F`); a literal reading of the instruction pair in
-- the brief, lsls #0x1A then lsrs #0x18, extracts bits 26-31. The observer therefore
-- reports both, and ALSO reads the registers the load instruction itself indexes with:
-- at the breakpoint r1 is the table base and r0 is the table index, so the word the engine
-- is about to load is read32(r1 + r0*4) and that r0 IS the engine's selector, whatever the
-- bits turn out to be. The histogram is reported under BOTH readings so neither has to be
-- taken on trust, and `histogram.txt` ends with engine_index_matches_low6/_high6 counts.
-- The primary histogram is the bits 0-5 reading, which is what the rest of the
-- toolkit uses (handles.py) and what the completed runs confirmed against the
-- engine's own index; the 26-31 reading stays as a second column so a
-- disagreement would still be visible.
local function selector_low(handle) return handle & 0x3F end
local function selector_high(handle) return (handle >> 26) & 0x3F end
local function start_of(handle) return ((handle >> 6) & 0x7FFF) * 2 end
local function length_of(handle) return ((handle >> 21) & 0x7FF) * 2 end

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")

local function knob(name, default)
    return tonumber(os.getenv(name) or "") or default
end

-- HORIZON is a hard floor of 2000 frames: the ticket asks the census to cover at least
-- that, and a shorter run would answer a different question.
local HORIZON = math.max(knob("FV3WT001_HORIZON", 2400), 2000)
local SHOT_EVERY = knob("DIALOGUE_SHOT_EVERY", 240)
local BEAT_EVERY = 60
local COPY_UNITS = 40
local SITE_ROWS = 200
local POINTER_ROWS = 400

-- The idle stop is right for an unattended run and wrong for a human one: it ends the run
-- 120 frames after the last dialogue record, so an operator who is still walking to the
-- scene when it fires loses the session. FV3WT001_IDLE_STOP=0 turns it off and leaves the
-- frame horizon as the only bound. Default stays exactly what the unattended runs measured.
local IDLE_STOP = knob("FV3WT001_IDLE_STOP", 120)

-- The container the table returns for selector 7 on the release-2 candidate: the appended
-- kind-0 container at file 0x9ABE24. Reported by name so a hit on it cannot be mistaken for
-- a hit on a retail container.
local APPENDED = 0x089ABE24

-- The live MapEntry pointer and its table, measured in this family of images. Logged with the
-- raw pointer beside it, because a scene claim should be checkable and not just asserted.
local MAP_POINTER = 0x03001980
local MAP_FIRST = 0x0808E2E0
local MAP_STRIDE = 0x38

assert(emu ~= nil, "mGBA did not attach the emulation core")
assert(emu.setBreakpoint and emu.clearBreakpoint, "requires the 0.11 breakpoint API")
local code = emu:getGameCode()
assert(code == "BG3E" or code == "AGB-BG3E", "unexpected game code: " .. tostring(code))

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

local function run()
    local route = assert(io.open(exp_dir .. "route.csv", "w"))
    route:write("frame,dispatch_hits,site_a_hits,site_b_hits,copier_hits,map_pointer,map_index\n")
    route:flush()

    local sites = assert(io.open(exp_dir .. "sites.csv", "w"))
    sites:write("site,hit,handle,selector_low6,selector_high6,start,length,engine_index,index_note,container,text40,full_text\n")
    sites:flush()

    local copies = assert(io.open(exp_dir .. "copies.csv", "w"))
    copies:write("call,frame,register,pointer,selector,units,text\n")
    copies:flush()

    local hist = assert(io.open(exp_dir .. "histogram.txt", "w"))
    hist:write("selector histogram; written again with the final counts at the end\n")
    hist:flush()

    local early = assert(io.open(exp_dir .. "copies-at-60.txt", "w"))
    early:write("pointer,count,selector\n")
    early:flush()

    local function note(format, ...)
        local text = select("#", ...) > 0 and string.format(format, ...) or format
        hist:write(text .. "\n")
        hist:flush()
    end

    local sites_at = { [SITE_A] = "A", [SITE_B] = "B" }
    local raw = assert(io.open(exp_dir .. "registers.txt", "w"))
    raw:write("site,hit,register,ok,kind,value\n")
    raw:flush()
    local raw_rows = 0
    local function dump_registers(address)
        if raw_rows >= 15 then return end
        raw_rows = raw_rows + 1
        for _, name in ipairs({ "r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7", "pc" }) do
            local ok, value = pcall(function() return emu:readRegister(name) end)
            raw:write(string.format("%s,%d,%s,%s,%s,%s\n", sites_at[address], raw_rows,
                name, tostring(ok), type(value), tostring(value)))
        end
        raw:flush()
    end
    local hits = { [SITE_A] = 0, [SITE_B] = 0 }
    local seen_handle = { [SITE_A] = 0, [SITE_B] = 0 }
    local site_rows = { [SITE_A] = 0, [SITE_B] = 0 }
    local hist_a, hist_b = {}, {}
    local over_a, over_b = 0, 0
    local max_a, max_b = -1, -1
    local index_low_a, index_high_a = {}, {}
    local index_low_b, index_high_b = {}, {}
    local index_low_agree_a, index_high_agree_a = 0, 0
    local index_low_agree_b, index_high_agree_b = 0, 0
    local index_missing_a, index_missing_b = 0, 0
    local copier_hits, dispatch_hits, pointer_rows = 0, 0, 0
    local container_hist, container_order = {}, {}
    local appended_hits = 0
    local appended_texts = {}
    local first_copier, last_copier = nil, nil
    local early_ptr, early_order = {}, {}
    local early_cutoff = false
    local copier_texts = 0

    local function reg(name)
        local ok, value = pcall(function() return emu:readRegister(name) end)
        return (ok and value) or nil
    end

    local function text_of(pointer, units)
        if not pointer or pointer < 0x08000000 then return "?" end
        local parts = {}
        for index = 0, units - 1 do
            local ok, value = pcall(function() return emu:read16(pointer + index * 2) end)
            if not ok or value == nil then break end
            if value == 0 then break end
            if value >= 0x20 and value < 0x7F then
                parts[#parts + 1] = string.char(value)
            else
                parts[#parts + 1] = string.format("<%04X>", value)
            end
        end
        return (table.concat(parts):gsub(",", ";"))
    end

    local function unit_count(pointer, units)
        if not pointer or pointer < 0x08000000 then return 0 end
        local count = 0
        for index = 0, units - 1 do
            local ok, value = pcall(function() return emu:read16(pointer + index * 2) end)
            if not ok or value == nil or value == 0 then break end
            count = count + 1
        end
        return count
    end

    local function on_site(address)
        -- COUNT FIRST. A read that fails, a record pointer that is not where it was
        -- expected, or a memory address outside the bus must never subtract a hit: the
        -- first version returned early on an unreadable word and reported a live site as
        -- silent. Everything below only enriches a hit that is already banked.
        hits[address] = hits[address] + 1
        dump_registers(address)

        local record = reg(address == SITE_A and "r5" or "r4")
        local word_address = (record or 0) + (address == SITE_A and A_WORD or B_WORD)
        -- No range guard: the observed r5 is 0x0878C918, a ROM-side word the first version's
        -- EWRAM-only guard rejected, so the guard itself was what made this unreadable. The
        -- read is attempted and its failure is recorded verbatim instead.
        local handle = nil
        local guard = "no_record_register"
        if record then
            local ok, value = pcall(function() return emu:read32(word_address) end)
            if ok and value ~= nil then
                handle = value
                guard = "read"
            else
                guard = string.format("read_failed_at_0x%08X", word_address)
            end
        end

        -- The engine's own index. MEASURED: at 0x08012248 r1 = 0x089A9CE8, the briefed
        -- container-table base, and r0 is the byte offset the ldr indexes with, so the
        -- engine's linear index is r0 / 4. Do not read a fixed slot here.
        local base = reg("r1")
        local index = nil
        if base and base >= 0x08000000 and base < 0x0A000000 then
            local r0 = reg("r0")
            if r0 and r0 % 4 == 0 and r0 < 256 then index = r0 // 4 end
        end

        local low = handle and selector_low(handle) or -1
        local high = handle and selector_high(handle) or -1

        -- THE RESOLVED CONTAINER AND THE WORDS THE COPIER WILL TAKE FROM IT. The table word
        -- the `ldr` is about to load is read32(r1 + r0*4), with r1 and r0 exactly as the
        -- instruction indexes them, so this is the address the record will be read from and
        -- not a re-derivation from the handle. The text is then read at
        -- container + 8 + start: a kind-0 container's payload begins 8 bytes in (four zero
        -- bytes then the declared size as u32), measured on this image and on container 3
        -- (00 00 00 00 36 FF 00 00, then "#That was weak."). Reading at container + start
        -- instead lands on that header, so the header offset is applied rather than assumed.
        local container = nil
        if base and index then
            local read_ok, value = pcall(function() return emu:read32(base + index * 4) end)
            if read_ok and value ~= nil then container = value end
        end
        local text40, full_text = "", ""
        if container and handle then
            local record = container + 8 + start_of(handle)
            text40 = text_of(record, COPY_UNITS)
            local units = length_of(handle) // 2
            if units > COPY_UNITS and units <= 400 then
                full_text = text_of(record, units)
            end
            if not container_hist[container] then
                container_hist[container] = 0
                container_order[#container_order + 1] = container
            end
            container_hist[container] = container_hist[container] + 1
            if container == APPENDED then
                appended_hits = appended_hits + 1
                appended_texts[#appended_texts + 1] = string.format(
                    "handle=0x%08X selector=%d index=%d start=%d length=%d text=%s",
                    handle, low, index or -1, start_of(handle), length_of(handle),
                    full_text ~= "" and full_text or text40)
            end
        end
        if handle then
            seen_handle[address] = handle
            local counts = address == SITE_A and hist_a or hist_b
            counts[low] = (counts[low] or 0) + 1
            if low >= 7 then
                if address == SITE_A then over_a = over_a + 1 else over_b = over_b + 1 end
            end
            if address == SITE_A then
                if low > max_a then max_a = low end
            else
                if low > max_b then max_b = low end
            end
        end
        if index == nil then
            if address == SITE_A then index_missing_a = index_missing_a + 1
            else index_missing_b = index_missing_b + 1 end
        else
            local by_index = address == SITE_A and index_low_a or index_low_b
            by_index[index] = (by_index[index] or 0) + 1
            if index == low then
                if address == SITE_A then index_low_agree_a = index_low_agree_a + 1
                else index_low_agree_b = index_low_agree_b + 1 end
            end
            if index == high then
                if address == SITE_A then index_high_agree_a = index_high_agree_a + 1
                else index_high_agree_b = index_high_agree_b + 1 end
            end
        end
        if site_rows[address] < SITE_ROWS then
            site_rows[address] = site_rows[address] + 1
            sites:write(string.format("%s,%d,%s,%d,%d,%d,%d,%d,%s,%s,%s,%s\n",
                sites_at[address], site_rows[address],
                handle and string.format("0x%08X", handle) or guard,
                low, high,
                handle and start_of(handle) or -1, handle and length_of(handle) or -1,
                index or -1,
                (index == nil) and "index_unreadable"
                    or (index == low) and "engine_index_matches_low6"
                    or (index == high) and "engine_index_matches_high6"
                    or "engine_index_matches_neither",
                container and string.format("0x%08X", container) or "container_unreadable",
                text40, full_text))
            sites:flush()
        end
    end

    local function on_copier()
        copier_hits = copier_hits + 1
        if not first_copier then first_copier = copier_hits end
        last_copier = copier_hits
        local source = nil
        for _, name in ipairs({ "r1", "r0", "r2", "r3" }) do
            local value = reg(name)
            if value and value >= 0x08000000 and value < 0x0A000000 then
                if unit_count(value, COPY_UNITS) > 2 then
                    source = value
                    if pointer_rows < POINTER_ROWS and copier_texts < POINTER_ROWS then
                        pointer_rows = pointer_rows + 1
                        copies:write(string.format("%d,%d,%s,0x%08X,%d,%d,%s\n",
                            copier_hits, frame, name, value, -1,
                            unit_count(value, COPY_UNITS), text_of(value, COPY_UNITS)))
                        copies:flush()
                        copier_texts = copier_texts + 1
                    end
                    break
                end
            end
        end
        if source and frame <= 60 and not early_cutoff then
            if not early_ptr[source] then
                early_ptr[source] = 0
                early_order[#early_order + 1] = source
            end
            early_ptr[source] = early_ptr[source] + 1
        end
    end

    local function on_dispatch()
        dispatch_hits = dispatch_hits + 1
    end

    local arms = {}
    local ids = {}
    local function arm(label, address, handler)
        local ok, result = pcall(function() return emu:setBreakpoint(handler, address) end)
        arms[#arms + 1] = string.format("%s 0x%08X ok=%s id=%s", label, address,
            tostring(ok), tostring(result))
        if type(result) == "number" then ids[#ids + 1] = result end
    end

    arm("site_a", SITE_A, function() on_site(SITE_A) end)
    arm("site_b", SITE_B, function() on_site(SITE_B) end)
    arm("copier", COPIER, on_copier)
    arm("dispatch", DISPATCH, on_dispatch)

    local arm_note = io.open(exp_dir .. "arm.txt", "w")
    if arm_note then
        arm_note:write(table.concat(arms, "\n") .. "\n")
        arm_note:close()
    end

    local last_hit_frame = 0
    local function any_hits() return hits[SITE_A] + hits[SITE_B] + copier_hits > 0 end

    frame = 0
    local callback_id
    callback_id = callbacks:add("frame", function()
        frame = frame + 1
        if any_hits() then last_hit_frame = frame end

        if frame % SHOT_EVERY == 0 then
            pcall(function() emu:screenshot(string.format("%sshot_%06d.png", exp_dir, frame)) end)
        end

        if frame % BEAT_EVERY == 0 then
            local pc = reg("pc")
            local map_pointer, map_index = nil, -1
            local ok_map, value = pcall(function() return emu:read32(MAP_POINTER) end)
            if ok_map and value ~= nil then
                map_pointer = value
                if value >= MAP_FIRST and value < MAP_FIRST + MAP_STRIDE * 512
                    and (value - MAP_FIRST) % MAP_STRIDE == 0 then
                    map_index = (value - MAP_FIRST) // MAP_STRIDE
                end
            end
            route:write(string.format("%d,%d,%d,%d,%d,0x%08X,%d\n", frame, dispatch_hits,
                hits[SITE_A], hits[SITE_B], copier_hits, (map_pointer or 0), map_index))
            route:flush()
            note("heartbeat frame=%d pc=0x%08X dispatch=%d site_a=%d site_b=%d copier=%d map_pointer=0x%08X map_index=%d",
                frame, (pc or 0), dispatch_hits, hits[SITE_A], hits[SITE_B], copier_hits,
                (map_pointer or 0), map_index)
        end

        if not early_cutoff and frame > 60 then
            early_cutoff = true
            for _, pointer in ipairs(early_order) do
                local handle = nil
                local ok, value = pcall(function() return emu:read32(pointer - 2) end)
                if ok then handle = value end
                early:write(string.format("0x%08X,%d,%d,%d\n", pointer, early_ptr[pointer],
                    handle and selector_low(handle) or -1,
                    handle and selector_high(handle) or -1))
            end
            early:flush()
        end

        if frame >= HORIZON
            or (IDLE_STOP > 0 and frame >= 2000 and frame > last_hit_frame + IDLE_STOP) then
            callbacks:remove(callback_id)
            for _, id in ipairs(ids) do
                pcall(function() emu:clearBreakpoint(id) end)
            end
            route:close()
            sites:close()
            copies:close()
            early:close()

            hist:write(string.format("\nframes=%d horizon=%d last_hit_frame=%d\n",
                frame, HORIZON, last_hit_frame))
            hist:write(string.format("dispatch_hits=%d site_a_hits=%d site_b_hits=%d copier_hits=%d\n",
                dispatch_hits, hits[SITE_A], hits[SITE_B], copier_hits))

            -- WHICH READING THE ENGINE USES, measured rather than decoded: the index is
            -- the r0 the instruction itself indexes with, read from r1 at the breakpoint.
            hist:write("engine_index_vs_reading\n")
            hist:write(string.format("site_a index_read=%d index_unreadable=%d agree_low6=%d agree_high6=%d\n",
                hits[SITE_A] - index_missing_a, index_missing_a, index_low_agree_a, index_high_agree_a))
            hist:write(string.format("site_b index_read=%d index_unreadable=%d agree_low6=%d agree_high6=%d\n",
                hits[SITE_B] - index_missing_b, index_missing_b, index_low_agree_b, index_high_agree_b))
            hist:write("engine_index_histogram\n")
            for index = 0, 63 do
                if index_low_a[index] or index_low_b[index] then
                    hist:write(string.format("index=%d site_a=%d site_b=%d\n", index,
                        index_low_a[index] or 0, index_low_b[index] or 0))
                end
            end

            hist:write("site_a_selector_low6_histogram\n")
            for selector = 0, 63 do
                if hist_a[selector] then
                    hist:write(string.format("A,%d,%d\n", selector, hist_a[selector]))
                end
            end
            hist:write("site_b_selector_low6_histogram\n")
            for selector = 0, 63 do
                if hist_b[selector] then
                    hist:write(string.format("B,%d,%d\n", selector, hist_b[selector]))
                end
            end
            hist:write(string.format("site_a_max_selector_low6=%d site_a_over_6=%d\n", max_a, over_a))
            hist:write(string.format("site_b_max_selector_low6=%d site_b_over_6=%d\n", max_b, over_b))
            hist:write(string.format("copier_first_call=%s copier_last_call=%s\n",
                tostring(first_copier), tostring(last_copier)))
            local last_a, last_b = seen_handle[SITE_A], seen_handle[SITE_B]
            hist:write(string.format("last_handle_a=0x%08X\nlast_handle_b=0x%08X\n", last_a, last_b))
            if last_a ~= 0 then
                hist:write(string.format("last_handle_a low6=%d high6=%d start=%d length=%d\n",
                    selector_low(last_a), selector_high(last_a), start_of(last_a), length_of(last_a)))
            end
            if last_b ~= 0 then
                hist:write(string.format("last_handle_b low6=%d high6=%d start=%d length=%d\n",
                    selector_low(last_b), selector_high(last_b), start_of(last_b), length_of(last_b)))
            end
            -- WHAT THE TABLE ACTUALLY RETURNED, and, for the appended container, every word the
            -- copier would have taken out of it. This is the route claim in one block: a
            -- selector alone says nothing until the address it resolves to is named.
            hist:write("resolved_container_histogram\n")
            for _, address in ipairs(container_order) do
                hist:write(string.format("container=0x%08X hits=%d\n", address, container_hist[address]))
            end
            hist:write(string.format("appended_container=0x%08X hits=%d\n", APPENDED, appended_hits))
            for _, line in ipairs(appended_texts) do
                hist:write("appended," .. line .. "\n")
            end
            hist:write(string.format("horizon=%d idle_stop=%d shot_every=%d\n",
                HORIZON, IDLE_STOP, SHOT_EVERY))
            hist:close()
            finish("done:frames=" .. tostring(frame))
            return
        end
    end)
end

local ok, err = xpcall(run, function(problem) return tostring(problem) end)
if not ok then finish("error:" .. tostring(err)) end
