-- DIALOGUE-VARIABLE-LENGTH-001: observe the retail engine consuming the
-- selector-1 compressed-dialogue container whose records were RE-LAID OUT.
--
-- This is the runtime half of the ticket. Checkpoint D proved the engine follows
-- the selector table to a container the production allocator placed above
-- canonical EOF; this probe asks the question this ticket adds: does the engine
-- honour a record whose decoded LENGTH field was re-authored, and does the
-- re-laid-out container still serve the records around it?
--
-- What it does, and what it deliberately does not:
--
--   * it READS emulated memory, installs two scripted breakpoints and takes
--     screenshots;
--   * it WRITES INPUT only in the `scripted` mode, which the tracked runner does
--     not select - the deterministic fixture stands beside the NPC and the
--     greeting is consumed on resume;
--   * it never writes emulated memory, and it never patches the ROM.
--
-- The expected relocated pointer is supplied by the runner from the derivative's
-- own provenance, so the probe ASSERTS the allocator's decision instead of
-- assuming the address it happens to expect.
--
-- Liveness: a silent consumer is not negative evidence. The observer also arms a
-- breakpoint on the shared script interpreter, so a run that records no CONSUMER
-- row still proves whether the core was executing the code path at all.

local CONSUMER = 0x08012240        -- retail compressed-dialogue consumer (Checkpoint D point)
local LIVE = 0x08004038            -- shared script interpreter (liveness channel)
local TABLE = 0x087B5B64           -- the seven-word selector table
local SELECTOR = 1                 -- the container this ticket rebuilt

-- Before: 0x02002641 (selector 1, decoded start 0x132, decoded length 32)
-- After:  0x04802641 (same start, decoded length 72)
local TARGET_HANDLE = 0x04802641
-- The record that followed the greeting in the same container. Before the edit
-- it was 0x0A002A41 (start 0x152, length 0xA0); the displacement moved its start
-- by 40 decoded bytes, so its re-authored handle is 0x0A002F41. Observing it is
-- the runtime neighbour control; if the session never reaches it, the container
-- semantic control in the ROM-gated test stands in for it and the run says so.
local NEIGHBOUR_HANDLE = 0x0A002F41

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = os.getenv("CAPACITY001_OUT") or (exp_dir .. "varlen001-dialogue.csv")
local expected_raw = os.getenv("CAPACITY001_EXPECTED_POINTER")
assert(expected_raw and #expected_raw > 0, "CAPACITY001_EXPECTED_POINTER not provided")
local expected = tonumber(expected_raw)

assert(emu and emu.setBreakpoint and emu.clearBreakpoint,
    "requires mGBA 0.11 scripted breakpoints")
local code = emu:getGameCode()
assert(code == "BG3E" or code == "AGB-BG3E", "unexpected game code: " .. tostring(code))
assert(emu:romSize() == 16777216, "expected the 16 MiB generated image")

local file = assert(io.open(log_path, "w"), "cannot open observer output")
file:write("kind,pc,handle,selector,table_entry,note\n")
file:flush()
local frames = 0
local screenshots = {}
local hits = 0
local target_seen = false
local neighbour_seen = false
local other_container_record_seen = false

local function hex(v)
    return v and string.format("0x%08X", v) or ""
end

local function row(kind, pc, handle, selector, pointer, note)
    file:write(string.format("%s,%s,%s,%s,%s,%s\n", kind, hex(pc), hex(handle),
        selector and tostring(selector) or "", hex(pointer), note))
    file:flush()
end

--: The frame at which the settled screenshot has been taken, so the human-mode
--: marker waits for the reveal to finish instead of stopping the run early.
local settle_frame = nil
--: A consumer hit whose decoded string has not been read yet: `{ object, frame }`.
local pending = nil

-- ONE breakpoint, at the address Checkpoint D already proved on this title:
-- `0x08012240 ldr r0,[r5,#4]`, immediately before the packed-handle load. r5 is
-- the ROM-resident dialog record, so r5+4 is the handle the engine read, and r6
-- is the destination object the consumer is about to fill.
--
-- The decoded string is NOT read here: at this instant the copy has not happened
-- yet. The object pointer is stashed and the string is read from the frame
-- callback a couple of frames later, where `object + 8` holds exactly the bytes
-- the engine materialised for display - a machine-checkable statement about the
-- widened length that does not depend on a screenshot landing on the right frame.
-- An earlier attempt put a SECOND breakpoint after the copy (0x08012268) and the
-- session never reached the greeting at all; one breakpoint, at the proven
-- address, is both the shape that works and the one already established here.
emu:setBreakpoint(function(info)
    local r5 = tonumber(emu:readRegister("r5"))
    local handle = r5 and emu:read32(r5 + 4) or nil
    local selector = handle and (handle % 64) or nil
    local pointer = selector and emu:read32(TABLE + selector * 4) or nil
    hits = hits + 1
    local correct_pointer = (pointer == expected)
    local note
    if handle == TARGET_HANDLE and selector == SELECTOR and correct_pointer then
        note = "target expanded selector consumed; widened decoded length honoured"
        if not target_seen then
            target_seen = true
            -- Three shots. The box reveals text progressively and the authored
            -- line is 36 characters, so +45 was measured mid-reveal on the first
            -- run: it showed the line only as far as "worst for". +8 is the
            -- measurement that the box is not up the instant the handle is read,
            -- +45 the reveal in progress, +120 the settled box.
            screenshots[#screenshots + 1] = { frame = frames + 8, hit = hits,
                                              tag = "early" }
            screenshots[#screenshots + 1] = { frame = frames + 45, hit = hits,
                                              tag = "dialogue-box" }
            screenshots[#screenshots + 1] = { frame = frames + 120, hit = hits,
                                              tag = "settled" }
            settle_frame = frames + 130
        end
    elseif handle == NEIGHBOUR_HANDLE and selector == SELECTOR and correct_pointer then
        note = "neighbour re-authored record consumed"
        if not neighbour_seen then
            neighbour_seen = true
            screenshots[#screenshots + 1] = { frame = frames + 45, hit = hits,
                                              tag = "neighbour" }
        end
    elseif selector == SELECTOR and correct_pointer then
        note = "other record from the rebuilt container"
        other_container_record_seen = true
    elseif handle == TARGET_HANDLE or handle == NEIGHBOUR_HANDLE then
        note = string.format("target handle with unexpected pointer %s", hex(pointer))
    else
        note = "other compressed-dialogue handle"
    end
    row("CONSUMER", CONSUMER, handle, selector, pointer, note)

    local object = tonumber(emu:readRegister("r6"))
    if object then
        pending = { object = object, frame = frames + 2, handle = handle,
                    selector = selector, pointer = pointer }
    end
end, CONSUMER)

--: Read `object + 8` once the consumer has finished writing the copied span into
--: it. Runs outside the breakpoint callback on purpose: the read is 512 bounded
--: halfword probes, and a long callback sits inside the emulator's own step.
local function flush_pending()
    if not pending or frames < pending.frame then return end
    local held = pending
    pending = nil
    local halfwords = {}
    for index = 0, 511 do
        local ok, unit = pcall(function() return emu:read16(held.object + 8 + index * 2) end)
        if not ok or unit == nil or unit == 0 then break end
        halfwords[#halfwords + 1] = string.format("%04X", unit)
    end
    local ascii = {}
    for _, unit in ipairs(halfwords) do
        local byte = tonumber(unit, 16) % 256
        local glyph = "."
        if byte >= 32 and byte < 127 then
            glyph = (string.char(byte):gsub(",", ";"))
        end
        ascii[#ascii + 1] = glyph
    end
    row("STRING", CONSUMER, held.handle, held.selector, held.pointer,
        string.format("decoded_bytes=%d hex=%s ascii=%s",
            #halfwords * 2, table.concat(halfwords), table.concat(ascii)))
end

local live = 0
emu:setBreakpoint(function(info)
    live = live + 1
    if live == 1 then
        row("LIVENESS", LIVE, nil, nil, nil, "shared interpreter reached")
    end
end, LIVE)

-- Three modes, because there is more than one honest way to reach a conversation:
--
--   * `human` (the default, and what the tracked runner selects): the operator
--     plays. The probe only observes, arms both breakpoints, and screenshots
--     each time the target record is consumed. It never writes input. Measured:
--     the fixture resumes in front of the NPC and the greeting is consumed with
--     no input, but only on some loads.
--   * `tap`: stand still and press A every 45 frames. The deterministic trigger,
--     because the fixture already stands in front of the NPC.
--   * `scripted`: drives LEFT then A from the deterministic fixture, held until
--     the runner signals the savestate has loaded. Measured NOT to reach the
--     greeting: the walk takes the player out of range.
--
-- Choosing between them is the runner's job, through CAPACITY001_MODE.
local MODE = os.getenv("CAPACITY001_MODE") or "human"
local LEFT = 0x20
local A = 0x01

-- mGBA exposes two key APIs and this repository uses BOTH: the tracked
-- `rom006_bootstrap.lua` presses keys with `emu:addKey(C.GBA_KEY.A)` and
-- `emu:clearKey`, while `p008_mash_driver.lua` uses the plural mask form
-- `emu:addKeys(1 << index)`. Measured: the plural mask form produced no input at
-- all in this vehicle - 300 frames of held LEFT moved the player nowhere and two
-- runs rendered byte-identical frames - so the single-key form is selected with
-- `VARLEN001_KEYAPI=single`. The default stays the plural mask the capacity
-- probe shipped with.
local KEYAPI = os.getenv("VARLEN001_KEYAPI") or "mask"

local function key_code(name, mask)
    if C and C.GBA_KEY and C.GBA_KEY[name] ~= nil then return C.GBA_KEY[name] end
    return mask
end

local function press(name, mask)
    if KEYAPI == "single" and emu.addKey then
        emu:addKey(key_code(name, mask))
    else
        emu:addKeys(mask)
    end
end

local function release(name, mask)
    if KEYAPI == "single" and emu.clearKey then
        emu:clearKey(key_code(name, mask))
    else
        emu:clearKeys(mask)
    end
end

local loaded_path = exp_dir .. "state-loaded.txt"
local loaded = false
local gameplay = 0
local waited = 0
local WAIT_FRAMES = 3600          -- 60 s at 60 fps, then give up and say so
local callback
local marker_written = false

local function write_marker(note)
    if marker_written then return end
    marker_written = true
    local marker = assert(io.open(done_path, "w"))
    marker:write(note .. "\n")
    marker:close()
end

local function finish(note)
    if callback then callbacks:remove(callback) end
    row("RESULT", nil, nil, nil, nil, note)
    write_marker(note)
end

-- A periodic picture, in every mode. A run that records no dialogue at all is
-- only interpretable if it also says what the screen was doing; measured here,
-- the automatic trigger is timing-dependent, so the screen is the instrument
-- that separates "the trigger never fired" from "the probe saw nothing".
local PERIODIC_SHOT = 600

-- The state load, done by the PROBE at a fixed frame.
--
-- Measured: the fixture resumes in front of the NPC and the greeting is consumed
-- with no input, but through the tracked chain's UI-automation load that happened
-- on one run out of five - the load is confirmed from the Scripting pane while
-- the core keeps running, so when it lands is not deterministic. `VARLEN001_STATE`
-- names the SAME hash-verified copy the runner already placed in the run
-- directory, and loading it from the probe at a fixed frame makes the fixture
-- deterministic again. This is a deviation from the UI-load step and it is
-- recorded as one: the bytes loaded are identical, only the caller differs.
local SELF_STATE = os.getenv("VARLEN001_STATE")
local SELF_LOAD_FRAME = tonumber(os.getenv("VARLEN001_LOAD_FRAME") or "") or 600
--: `VARLEN001_QUIET` suppresses the heartbeat, the periodic screenshots and the
--: self-load, leaving exactly the Checkpoint D observation shape. Measured: the
--: fixture's automatic greeting was consumed once in the plain shape and not in
--: the instrumented one, so the plain shape is kept available rather than
--: assumed equivalent.
local QUIET = os.getenv("VARLEN001_QUIET")
local self_loaded = false
--: Sweep mode. `VARLEN001_SWEEP` re-loads the same state repeatedly at a fixed
--: frame interval, so ONE run samples many points in the game's own tick stream
--: instead of the single point an ordinary run gets. Measured: the fixture's
--: automatic greeting fired on one run in sixteen and the UI-automation load
--: lands at a different frame every time, so the discriminating variable - if
--: there is one - is where in the tick stream the load lands. This samples it.
local SWEEP = os.getenv("VARLEN001_SWEEP")
local sweep_next = tonumber(os.getenv("VARLEN001_LOAD_FRAME") or "") or 180
local sweep_step = tonumber(os.getenv("VARLEN001_LOAD_STEP") or "") or 180
local sweep_last = tonumber(os.getenv("VARLEN001_LOAD_LAST") or "") or 4200

-- The frame callback below runs in BOTH modes. The screenshot scheduling is
-- deliberately outside the mode branch: a human session is exactly when the
-- on-screen dialogue box is the evidence.
callback = callbacks:add("frame", function()
    frames = frames + 1
    if SELF_STATE and not QUIET and not self_loaded and frames == SELF_LOAD_FRAME then
        self_loaded = true
        local ok, loaded_ok = pcall(function() return emu:loadStateFile(SELF_STATE) end)
        row("STATE", nil, nil, nil, nil,
            string.format("probe self-loaded frame=%d ok=%s result=%s path=%s",
                frames, tostring(ok), tostring(loaded_ok), SELF_STATE))
    end
    if SELF_STATE and SWEEP and frames >= sweep_next and sweep_next <= sweep_last then
        local at = sweep_next
        sweep_next = sweep_next + sweep_step
        local ok, loaded_ok = pcall(function() return emu:loadStateFile(SELF_STATE) end)
        row("STATE", nil, nil, nil, nil,
            string.format("sweep self-load frame=%d ok=%s result=%s path=%s",
                at, tostring(ok), tostring(loaded_ok), SELF_STATE))
    end
    -- Heartbeat: a run that records no consumer row and no liveness row is only
    -- evidence of anything if the core was executing at all. One row every 300
    -- frames distinguishes "the session never reached the greeting" from "the
    -- emulator was not running".
    flush_pending()
    if not QUIET and frames % 300 == 0 then
        row("HEARTBEAT", nil, nil, nil, nil,
            string.format("frame=%d mode=%s loaded=%s", frames, MODE,
                tostring(loaded)))
    end
    if not QUIET and frames % PERIODIC_SHOT == 0 then
        local path = exp_dir .. "varlen001-periodic-" .. tostring(frames) .. ".png"
        emu:screenshot(path)
        row("SCREENSHOT", nil, nil, nil, nil, path)
    end
    for _, shot in ipairs(screenshots) do
        if frames == shot.frame then
            local path = exp_dir .. "varlen001-consumer-" .. tostring(shot.hit) ..
                "-" .. shot.tag .. ".png"
            emu:screenshot(path)
            row("SCREENSHOT", nil, nil, nil, nil, path)
        end
    end

    if MODE == "human" then
        -- Observation only, and the operator owns the session: the probe records
        -- the marker once the settled screenshot exists so the evidence collector
        -- has an answer, then keeps watching for further hits rather than ending a
        -- live session underneath the person playing it.
        if target_seen and settle_frame and frames >= settle_frame then
            write_marker("target-seen")
        end
        return
    end

    if not loaded then
        waited = waited + 1
        local probe = io.open(loaded_path, "r")
        if probe then
            probe:close()
            loaded = true
            row("STATE", nil, nil, nil, nil, "savestate load signalled after " ..
                tostring(waited) .. " frames")
        elseif waited >= WAIT_FRAMES then
            finish("no-state-load")
        end
        return
    end

    gameplay = gameplay + 1
    if MODE == "route" then
        -- A configurable input schedule, so reaching the NPC is an experiment
        -- rather than a probe edit. `VARLEN001_ROUTE` is a comma-separated list of
        -- `KEY:FRAMES` steps (or `SCREEN` / `WAIT:FRAMES`); every step starts by
        -- releasing every key, so a step cannot inherit the previous hold. Each
        -- step is photographed at its midpoint.
        --
        -- Reaching the NPC is needed because the fixture resumes beside it but the
        -- greeting is an interaction: measured, the player CAN walk (RIGHT, UP and
        -- DOWN scroll the camera) while LEFT is blocked at this spot.
        local MASK = { A = 0x01, B = 0x02, SELECT = 0x04, START = 0x08,
                       RIGHT = 0x10, LEFT = 0x20, UP = 0x40, DOWN = 0x80 }
        local ORDER = { "A", "B", "SELECT", "START", "RIGHT", "LEFT", "UP", "DOWN" }
        local route = {}
        if os.getenv("VARLEN001_ROUTE") then
            for token in os.getenv("VARLEN001_ROUTE"):gmatch("[^,]+") do
                route[#route + 1] = token
            end
        end
        local span = 60
        local base = 30
        local total = span * #route
        if gameplay >= base and gameplay < base + total then
            local index = math.floor((gameplay - base) / span) + 1
            local token = route[index]
            local phase = (gameplay - base) % span
            if phase == 0 then
                for _, name in ipairs(ORDER) do release(name, MASK[name]) end
                local kind, count = token:match("^(%u+):(%d+)$")
                if kind and MASK[kind] then
                    press(kind, MASK[kind])
                end
                row("INPUT", nil, nil, nil, nil,
                    string.format("step %d/%d token=%s", index, #route, token))
            end
            if phase == span // 2 then
                -- `token` carries a colon (`LEFT:40`), which a Windows filename
                -- cannot, so the first attempt silently wrote no file for those
                -- steps. The index is what identifies the step anyway.
                local path = exp_dir .. string.format("varlen001-route-%02d.png",
                    index)
                emu:screenshot(path)
                row("SCREENSHOT", nil, nil, nil, nil, path)
            end
        elseif gameplay >= base + total then
            for _, name in ipairs(ORDER) do release(name, MASK[name]) end
            finish(target_seen and "target-seen" or "route-done")
        end
        return
    end
    if MODE == "keytest" then
        -- POSITIVE CONTROL inside the fixture: START opens the pause menu in this
        -- game, so if the screen does not change, no input is reaching the core
        -- in the loaded state - which is a different finding from "the player
        -- cannot walk", and the two need separating before any more trigger
        -- attempts are worth making.
        --
        -- `VARLEN001_PRESTART` presses START from gameplay 1, i.e. as soon as the
        -- state-load signal appears, and `VARLEN001_PRELATCH` holds A from before
        -- that, to test whether a key set BEFORE the fixture lands survives the
        -- load.
        if os.getenv("VARLEN001_PRELATCH") then
            press("A", A)
        end
        -- Log what each name resolves to. `emu:addKey` takes a GBA_KEY INDEX, not
        -- a mask, so a name that does not exist in `C.GBA_KEY` silently falls back
        -- to the mask value and becomes a different (or invalid) key.
        if gameplay == 5 then
            row("KEYCODE", nil, nil, nil, nil, string.format(
                "A=%s START=%s LEFT=%s RIGHT=%s UP=%s DOWN=%s",
                tostring(key_code("A", A)), tostring(key_code("START", 0x08)),
                tostring(key_code("LEFT", LEFT)), tostring(key_code("RIGHT", 0x10)),
                tostring(key_code("UP", 0x40)), tostring(key_code("DOWN", 0x80))))
        end
        -- Sweep the four directions one at a time, photographing after each, so a
        -- direction that moves the player is visible by comparing frames.
        if gameplay == 30 then
            emu:screenshot(exp_dir .. "varlen001-key-030-before.png")
            row("SCREENSHOT", nil, nil, nil, nil, "before any direction")
        elseif gameplay == 40 then
            press("LEFT", LEFT)
        elseif gameplay == 100 then
            release("LEFT", LEFT)
        elseif gameplay == 110 then
            emu:screenshot(exp_dir .. "varlen001-key-110-left.png")
            row("SCREENSHOT", nil, nil, nil, nil, "after LEFT")
        elseif gameplay == 120 then
            press("RIGHT", 0x10)
        elseif gameplay == 180 then
            release("RIGHT", 0x10)
        elseif gameplay == 190 then
            emu:screenshot(exp_dir .. "varlen001-key-190-right.png")
            row("SCREENSHOT", nil, nil, nil, nil, "after RIGHT")
        elseif gameplay == 200 then
            press("UP", 0x40)
        elseif gameplay == 260 then
            release("UP", 0x40)
        elseif gameplay == 270 then
            emu:screenshot(exp_dir .. "varlen001-key-270-up.png")
            row("SCREENSHOT", nil, nil, nil, nil, "after UP")
        elseif gameplay == 280 then
            press("DOWN", 0x80)
        elseif gameplay == 340 then
            release("DOWN", 0x80)
        elseif gameplay == 350 then
            emu:screenshot(exp_dir .. "varlen001-key-350-down.png")
            row("SCREENSHOT", nil, nil, nil, nil, "after DOWN")
        elseif gameplay == 400 then
            finish(target_seen and "target-seen" or "keytest-done")
        end
        return
    end
    if MODE == "boot" then
        -- POSITIVE CONTROL for the key API, and the reason it is needed: three
        -- probe-side key channels left the player exactly where it was and two
        -- runs rendered byte-identical frames, which is consistent with BOTH "no
        -- input reaches the core" and "the fixture's state inhibits input". A
        -- fresh boot separates them: a title screen always accepts input, so if A
        -- there changes nothing, no key reaches the core in this vehicle at all.
        --
        -- The reset is deliberately LATE (frame 1200). The tracked runner loads the
        -- fixture state through the Scripting console a few hundred frames in, and
        -- resetting after that wipes it, so the boot this control watches is the
        -- only thing running.
        if gameplay == 1200 then
            emu:reset()
            row("RESET", nil, nil, nil, nil,
                "core reset at frame 1200 for the input positive control")
            if os.getenv("VARLEN001_HOLD") then
                press("LEFT", LEFT)
                row("INPUT", nil, nil, nil, nil, "holding LEFT from frame 1200")
            end
        elseif gameplay > 1200 and not os.getenv("VARLEN001_HOLD")
                and (gameplay - 1200) % 40 == 0 then
            press("A", A)
        elseif gameplay > 1200 and not os.getenv("VARLEN001_HOLD")
                and (gameplay - 1200) % 40 == 8 then
            release("A", A)
        end
        -- Measured: from a fresh boot the game AUTO-PLAYS its intro narration
        -- through the very consumer under test, with no input at all, so the core
        -- of this ticket's runtime question can be observed deterministically.
        -- The observation therefore runs long enough for the intro to reach the
        -- tournament scene, and tags every shot with its frame number.
        if gameplay > 1200 and (gameplay - 1200) % 1000 == 0 then
            local path = exp_dir .. "varlen001-boot-" .. tostring(gameplay) .. ".png"
            emu:screenshot(path)
            row("SCREENSHOT", nil, nil, nil, nil, path)
        end
        if gameplay == 21200 then
            release("A", A)
            release("LEFT", LEFT)
            finish(target_seen and "target-seen" or "boot-done")
        end
        return
    end
    if MODE == "hold" then
        -- DIAGNOSTIC, not the proof: hold LEFT for 300 frames and photograph the
        -- start and the end. If the player has moved, the emulator's key API
        -- reaches the core; if the two frames are identical, no Lua-side input is
        -- delivered in this vehicle and the operator step cannot be scripted.
        if gameplay == 1 then
            press("LEFT", LEFT)
        elseif gameplay == 10 then
            emu:screenshot(exp_dir .. "varlen001-hold-010.png")
            row("SCREENSHOT", nil, nil, nil, nil, exp_dir .. "varlen001-hold-010.png")
        elseif gameplay == 300 then
            emu:screenshot(exp_dir .. "varlen001-hold-300.png")
            row("SCREENSHOT", nil, nil, nil, nil, exp_dir .. "varlen001-hold-300.png")
        elseif gameplay == 310 then
            release("LEFT", LEFT)
            finish(target_seen and "target-seen" or "hold-done")
        end
        return
    end
    if MODE == "tap" then
        -- `tap`: stand still and press A on a varying interval, holding it four
        -- frames. The fixture resumes in front of the NPC, so A is the
        -- deterministic way to open the conversation; no walking, because walking
        -- moved the player out of range in the measured scripted attempt.
        --
        -- The keys go through `emu:addKeys` / `emu:clearKeys`, which is the pair
        -- the proven P-008 driver uses, with the same GBA_KEY indices this file
        -- computes its masks from (A = 1 << 0, LEFT = 1 << 5). An earlier version
        -- used `emu:setKeys`, which is NOT that pair: measured, it produced no
        -- movement and no menu, so every scripted trigger silently did nothing.
        local phase = gameplay % 45
        if phase == 0 then
            press("A", A)
        elseif phase == 4 then
            release("A", A)
        end
        return
    end
    if gameplay == 1 then
        press("LEFT", LEFT)
    elseif gameplay == 52 then
        release("LEFT", LEFT)
    elseif gameplay == 58 then
        press("A", A)
    elseif gameplay == 61 then
        release("A", A)
    elseif gameplay == 190 then
        emu:screenshot(exp_dir .. "varlen001-dialogue.png")
        row("SCREENSHOT", nil, nil, nil, nil, exp_dir .. "varlen001-dialogue.png")
    elseif gameplay == 260 then
        release("A", A)
        release("LEFT", LEFT)
        finish(target_seen and "target-seen" or "target-not-seen")
    end
end)

row("ARMED", nil, nil, nil, emu:read32(TABLE + SELECTOR * 4),
    "selector " .. tostring(SELECTOR) .. " pointer at arm time; expected " .. hex(expected))
local marker = assert(io.open(done_path, "w"), "cannot open marker")
marker:write("armed\n")
marker:close()
print([[DIALOGUE-VARIABLE-LENGTH-001 widened-dialogue probe armed]])
