-- ROM-CAPACITY-AND-ALLOCATION-001 Checkpoint D: observe the retail engine
-- consuming the selector-1 compressed-dialogue container that the PRODUCTION
-- allocator placed above canonical EOF.
--
-- This is the runtime half of Checkpoint D. Its claim is narrow on purpose: it
-- shows the engine dereferencing the address the allocator chose, not that every
-- address through 16 MiB works.
--
-- What it does, and what it deliberately does not:
--
--   * it READS emulated memory, installs two scripted breakpoints and takes
--     screenshots;
--   * it WRITES INPUT (the fixture stands beside the NPC, and the retail
--     conversation has to be triggered normally) - which is why it is a fresh
--     file rather than an extension of the read-only ROM-EXPAND-001 observer;
--   * it never writes emulated memory, and it never patches the ROM.
--
-- The expected relocated pointer is supplied by the runner from the derivative's
-- own provenance, so the probe ASSERTS the allocator's decision instead of
-- assuming the address it happens to expect. A run whose pointer does not match
-- still records the row; the runner fails on the mismatch.
--
-- Liveness: a silent consumer is not negative evidence. The observer also arms a
-- breakpoint on the shared script interpreter, so a run that records no CONSUMER
-- row still proves whether the core was executing the code path at all.

local CONSUMER = 0x08012240        -- retail compressed-dialogue consumer
local LIVE = 0x08004038            -- shared script interpreter (liveness channel)
local TABLE = 0x087B5B64           -- the seven-word selector table
local TARGET_HANDLE = 0x02002641   -- the goku-greeting packed handle

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = os.getenv("CAPACITY001_OUT") or (exp_dir .. "capacity001-dialogue.csv")
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

local function hex(v)
    return v and string.format("0x%08X", v) or ""
end

local function row(kind, pc, handle, selector, pointer, note)
    file:write(string.format("%s,%s,%s,%s,%s,%s\n", kind, hex(pc), hex(handle),
        selector and tostring(selector) or "", hex(pointer), note))
    file:flush()
end

-- The breakpoint sits immediately before the packed-handle load. r5 is the
-- ROM-resident dialog record; reading r5+4 mirrors the consumer's next
-- instruction and keeps the raw handle distinct from the decoded fields.
emu:setBreakpoint(function(info)
    local r5 = tonumber(emu:readRegister("r5"))
    local handle = r5 and emu:read32(r5 + 4) or nil
    local selector = handle and (handle % 64) or nil
    local pointer = selector and emu:read32(TABLE + selector * 4) or nil
    hits = hits + 1
    local is_target = (handle == TARGET_HANDLE and selector == 1)
    local note
    if is_target and pointer == expected then
        note = "target expanded selector consumed"
        target_seen = true
        -- Two shots, because the box is not up the instant the handle is read:
        -- the engine still has to fetch and decompress the container (17,932
        -- bytes here) before it draws anything. Measured: at +8 frames the screen
        -- is still bare world, so an +8-only capture looks like the relocation
        -- had no visible effect at all.
        screenshots[#screenshots + 1] = { frame = frames + 8, hit = hits, tag = "early" }
        screenshots[#screenshots + 1] = { frame = frames + 45, hit = hits,
                                          tag = "dialogue-box" }
    elseif is_target then
        note = string.format("target handle with unexpected pointer %s", hex(pointer))
    else
        note = "other compressed-dialogue handle"
    end
    row("CONSUMER", CONSUMER, handle, selector, pointer, note)
end, CONSUMER)

local live = 0
emu:setBreakpoint(function(info)
    live = live + 1
    if live == 1 then
        row("LIVENESS", LIVE, nil, nil, nil, "shared interpreter reached")
    end
end, LIVE)

-- Two modes, because there are two honest ways to reach a conversation:
--
--   * `human` (default here): the operator plays. The probe only observes, arms
--     both breakpoints, and screenshots each time the target selector is
--     consumed. It never writes input, so nothing about the trigger is scripted.
--   * `scripted`: the probe drives LEFT then A from the deterministic fixture,
--     held until the runner signals the savestate has loaded.
--
-- Choosing between them is the runner's job, through CAPACITY001_MODE.
local MODE = os.getenv("CAPACITY001_MODE") or "human"
local LEFT = 0x20
local A = 0x01
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

-- The frame callback below runs in BOTH modes. The screenshot scheduling is
-- deliberately outside the mode branch: a human session is exactly when the
-- on-screen dialogue box is the evidence, and an earlier version skipped it,
-- recording the machine row but no picture of what the player saw.
callback = callbacks:add("frame", function()
    frames = frames + 1
    for _, shot in ipairs(screenshots) do
        if frames == shot.frame then
            local path = exp_dir .. "capacity001-consumer-" .. tostring(shot.hit) ..
                "-" .. shot.tag .. ".png"
            emu:screenshot(path)
            row("SCREENSHOT", nil, nil, nil, nil, path)
        end
    end

    if MODE == "human" then
        -- Observation only, and the operator owns the session: the probe records
        -- the marker on the first target hit so the evidence collector has an
        -- answer, then keeps watching for further hits rather than ending a live
        -- session underneath the person playing it.
        if target_seen then write_marker("target-seen") end
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
    if gameplay == 1 then
        emu:setKeys(LEFT)
    elseif gameplay == 52 then
        emu:setKeys(0)
    elseif gameplay == 58 then
        emu:setKeys(A)
    elseif gameplay == 61 then
        emu:setKeys(0)
    elseif gameplay == 190 then
        emu:screenshot(exp_dir .. "capacity001-dialogue.png")
        row("SCREENSHOT", nil, nil, nil, nil, exp_dir .. "capacity001-dialogue.png")
    elseif gameplay == 260 then
        finish(target_seen and "target-seen" or "target-not-seen")
    end
end)

row("ARMED", nil, nil, nil, emu:read32(TABLE + 4),
    "selector 1 pointer at arm time; expected " .. hex(expected))
local marker = assert(io.open(done_path, "w"), "cannot open marker")
marker:write("armed\n")
marker:close()
print([[CAPACITY-001 expanded-dialogue probe armed]])
