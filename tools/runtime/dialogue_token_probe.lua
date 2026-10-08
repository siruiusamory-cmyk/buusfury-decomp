-- WHO prices a unit as a token, and what does the engine then do with it?
--
-- READ-ONLY. It reads registers and memory, installs breakpoints and writes host
-- files inside the run directory. It writes no emulated memory and presses no
-- keys; driving is a separate file (npc_talk_driver.lua).
--
-- WHY THIS EXISTS. `dialogue_strip_probe.lua` logs the composition and advance
-- events but never the SOURCE UNIT that the token lookup was handed, so it cannot
-- answer "did the fitter price unit N as a token and the composer not?" That is
-- exactly the disagreement that broke the first token run, and the register that
-- carries the unit (r4) is not one the strip probe reads. This probe reads it.
--
-- THE FIVE CHANNELS, and what each one proves:
--
--   LOOKUP      token_lookup's entry. r4 = the unit, lr = WHO asked. A row whose
--               lr is inside the cave is the composition side; anything else is
--               the relocated line fitter. Both sides must agree on every unit.
--   TOKENPATH   the first instruction of token_advance's token branch, reached
--               only when the lookup returned an entry. r4 is still the unit
--               here. A row on this channel is the FITTER pricing a real token.
--   GLYPHADV    glyph_advance's entry, reached once per glyph inside an
--               expansion. Its row count is how many glyph advances the fitter
--               summed, which is the number the layout depends on.
--   CEXPAND     the composition cave's glyph loop, reached only when the
--               composer expands a token. a = the glyph, b = the walker, and
--               c/d are the object's live x and y.
--   COMPOSE     the game's own composer 0x0803DE50, with lr naming the caller:
--               the game's own call site or the cave's.
--   COPIER      the dialogue record copier: LIVENESS. A silent channel beside a
--               silent liveness channel proves nothing (mgba-runtime.md s.8).
--
-- SELF-TERMINATING at the frame budget, so the procedure stays: launch, do not
-- poll, wait for the marker, collect afterwards.

local COMPOSE = 0x0803DE5E
local COPIER = 0x0801227A

local BUDGET = 3000

local function addr(name)
    local raw = os.getenv(name)
    if raw == nil or raw == "" then return nil end
    local value = tonumber(raw, 16)
    assert(value ~= nil, name .. " is not hex: " .. tostring(raw))
    return value
end

local LOOKUP = addr("DIALOGUE_TOKEN_LOOKUP")
local TOKENPATH = addr("DIALOGUE_TOKEN_ADVANCE_PATH")
local GLYPHADV = addr("DIALOGUE_TOKEN_GLYPH_ADVANCE")
local CEXPAND = addr("DIALOGUE_TOKEN_COMPOSE_LOOP")
-- The composition cave's single source-consume store, `str r1,[r2,#0x14]`. The
-- game's own consume store is bypassed by an expansion, so this is the only place
-- an expanded unit's consumption can be seen.
local CONSUME = addr("DIALOGUE_TOKEN_CONSUME")

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local out = (os.getenv("TOOLKIT031_OUT") or (exp_dir .. "token-probe.csv"))

assert(emu ~= nil, "mGBA did not attach the emulation core")
assert(emu.setBreakpoint and emu.clearBreakpoint, "requires the 0.11 breakpoint API")
local code = emu:getGameCode()
assert(code == "BG3E" or code == "AGB-BG3E", "unexpected game code: " .. tostring(code))
-- The image size is a second identity check beside the launcher's exact digest
-- gate, and it is an INPUT rather than a constant because the token work runs on
-- generated-expansion images: the toolkit's own dialogue authoring emits a larger
-- image than the canonical 8 MiB, so a hardcoded size would refuse the very builds
-- this observer exists to watch.
local expected_size = tonumber(os.getenv("DIALOGUE_ROM_SIZE") or "8388608")
assert(emu:romSize() == expected_size,
       string.format("unexpected ROM size %d, expected %d", emu:romSize(), expected_size))

local header = { "frame", "event", "a", "b", "c", "d", "note" }
local file = assert(io.open(out, "w"), "cannot open " .. tostring(out))
file:write(table.concat(header, ",") .. "\n")
file:flush()

local frames = 0
local hits = {}

local function reg(n)
    local ok, v = pcall(function() return tonumber(emu:readRegister(n)) end)
    if ok then return v end
end
local function r8(a)
    local ok, v = pcall(function() return emu:read8(a) end)
    if ok then return v end
end
local function hx(v) if v == nil then return "" end return string.format("0x%08X", v) end
local function h4(v) if v == nil then return "" end return string.format("0x%04X", v) end

local function row(t)
    local parts = { tostring(frames), t.event or "" }
    for i = 3, #header do
        parts[i] = t[header[i]] ~= nil and tostring(t[header[i]]) or ""
    end
    file:write(table.concat(parts, ",") .. "\n")
    file:flush()
end

local function count(name)
    hits[name] = (hits[name] or 0) + 1
end

-- Which side of the patch asked. token_advance lives at the start of the helper
-- block and cave_compose follows it; the relocated fitter reaches the lookup only
-- through token_advance, so a return address inside that function is the FITTER
-- and one inside cave_compose is the COMPOSER. Telling them apart is the whole
-- point: the first token run had them disagree and the split rule below names
-- which one is speaking.
local TOKEN_ADVANCE_LO, TOKEN_ADVANCE_HI = 0x082ED2C8, 0x082ED30A
local CAVE_LO, CAVE_HI = 0x082ED210, 0x082ED400
local function side(lr)
    if lr == nil then return "?" end
    if lr >= TOKEN_ADVANCE_LO and lr < TOKEN_ADVANCE_HI then return "fitter" end
    if lr >= CAVE_LO and lr < CAVE_HI then return "composer" end
    return "game"
end

local bp_lookup
if LOOKUP then
    bp_lookup = emu:setBreakpoint(function()
        count("lookup")
        local lr = reg("lr")
        row({ event = "LOOKUP", a = reg("r4"), b = hx(lr),
              note = "unit -> lookup, caller " .. side(lr) })
    end, LOOKUP)
end

local bp_tokenpath
if TOKENPATH then
    bp_tokenpath = emu:setBreakpoint(function()
        count("tokenpath")
        row({ event = "TOKENPATH", a = reg("r4"), b = hx(reg("r0")),
              note = "the FITTER priced this unit as a token" })
    end, TOKENPATH)
end

local bp_glyphadv
if GLYPHADV then
    bp_glyphadv = emu:setBreakpoint(function()
        count("glyphadv")
        local n = hits["glyphadv"]
        -- Only the first few per expansion matter, and the walker pointer is the
        -- same one token_advance holds, so the run-length is visible in the rows.
        if n <= 400 then
            row({ event = "GLYPHADV", a = reg("r1"), b = hx(reg("r5")),
                  note = "a glyph inside an expansion" })
        end
    end, GLYPHADV)
end

local bp_cexpand
if CEXPAND then
    bp_cexpand = emu:setBreakpoint(function()
        count("cexpand")
        local obj = reg("r6")
        if hits["cexpand"] <= 400 then
            -- The walker (r5) is what the loop has already advanced past, so its
            -- low bits name which halfword of the entry is being composed; x and y
            -- come from the live text object, which is what makes the per-glyph
            -- positioning checkable rather than asserted.
            row({ event = "CEXPAND", a = hx(reg("r5")), b = hx(reg("r0")),
                  c = obj and tostring(r8(obj + 4)) or "",
                  d = obj and tostring(r8(obj + 5)) or "",
                  note = "the COMPOSER expands a token" })
        end
    end, CEXPAND)
end

local bp_consume
if CONSUME then
    bp_consume = emu:setBreakpoint(function()
        count("consume")
        local obj = reg("r4")
        local before = obj and reg("r2")
        -- r1 is the freshly advanced source cursor and r2 the text object, so the
        -- consumed unit count is (r1 in the cave's own register) - (the object's
        -- previous cursor at +0x14), which must be exactly one unit per expansion.
        row({ event = "CONSUME", a = hx(reg("r1")), b = hx(before),
              c = obj and tostring(emu:read32(obj + 0x14)) or "",
              note = "the cave consumes exactly one unit" })
    end, CONSUME)
end

local bp_compose = emu:setBreakpoint(function()
    count("compose")
    if hits["compose"] <= 60 then
        local lr = reg("lr")
        row({ event = "COMPOSE", a = reg("r1"), b = hx(lr),
              note = "glyph composed, caller " .. side(lr) })
    end
end, COMPOSE)

local bp_copier = emu:setBreakpoint(function()
    count("copier")
    row({ event = "COPIER", note = "dialogue load; liveness " .. hits["copier"] })
end, COPIER)

local cid = callbacks:add("frame", function()
    frames = frames + 1

    -- A frame heartbeat, so a stalled run is visible as a heartbeat that stops
    -- rather than as a run that is merely quiet. The Kibito fault is a freeze with
    -- no popup and a normal idle program counter, so nothing inside the emulator
    -- reports it and the detector has to be the frame count from outside.
    if frames % 120 == 0 then
        row({ event = "HEARTBEAT", a = frames, note = "frame progress" })
    end

    if frames == 5 or frames % 1200 == 0 then
        row({ event = "ROMCHECK", a = h4(emu:read16(0x0800B066)),
              b = h4(emu:read16(0x0800B068)),
              note = string.format("romSize=%d gameCode=%s",
                  emu:romSize(), tostring(emu:getGameCode())) })
    end

    -- The visible half of the proof: the same dialogue at the same frames as a
    -- control run, so a reader compares two pictures rather than reading a claim.
    if frames % 60 == 0 then
        pcall(function() emu:screenshot(string.format("%sshot_%05d.png", exp_dir, frames)) end)
    end

    if frames >= BUDGET then
        -- The marker and the exit come FIRST and are not conditional on anything
        -- that can throw: a teardown that fails must not leave the session unable
        -- to report that it finished. An earlier version removed the callback
        -- before writing the marker, that call raised, and the observer kept
        -- running and re-wrote its summary every frame for the rest of the run.
        pcall(function()
            row({ event = "SUMMARY", note = string.format(
                  "lookup=%d tokenpath=%d glyphadv=%d cexpand=%d consume=%d compose=%d copier=%d",
                  hits["lookup"] or 0, hits["tokenpath"] or 0, hits["glyphadv"] or 0,
                  hits["cexpand"] or 0, hits["consume"] or 0,
                  hits["compose"] or 0, hits["copier"] or 0) })
        end)
        local m = io.open(done_path, "w")
        if m then m:write("done:TokenProbe") m:close() end
        pcall(function()
            for _, bp in ipairs({ bp_lookup, bp_tokenpath, bp_glyphadv, bp_cexpand,
                                  bp_consume, bp_compose, bp_copier }) do
                if bp then emu:clearBreakpoint(bp) end
            end
        end)
        pcall(function() callbacks:remove(cid) end)
        os.exit(0)
    end
end)
