-- FRIEND-V3-TULMA-GRAPHICS-001: read-only observer for one human-played session.
--
-- WHAT IT IS FOR. The ticket asks whether the retail engine draws the authored Tulma
-- pixels in a real encounter. A savestate restores the VRAM a previous run assembled, so a
-- state loaded into the world cannot answer it: the area has to be BUILT during the
-- session, which is why the operator boots the image, loads the saved game and plays in.
--
-- WHY IT CAPTURES EVERY SETTLED SCREEN. Deciding "the operator is now in the world" from
-- inside the observer would mean guessing which settle event is the gameplay one - the
-- publisher logo, the title and the save-select screen all settle too. Instead every screen
-- whose object-tile region has held still for DWELL_FRAMES is captured, in order, with its
-- map index; the analysis afterwards picks the gameplay frame from the sequence.
--
-- WHAT THE ANALYSIS LOOKS FOR. The full VRAM dump includes the object tile region
-- 0x06010000..0x06018000. The candidate's containers decode to known hardware tile bytes,
-- so "the engine drew the authored art" is a claim that those bytes are present in that
-- region during a settled screen - measurable, not a matter of opinion. The screenshot is
-- the second channel, for the shape and the palette together.
--
-- READ-ONLY. This file only reads emulated memory (emu:readRange) and writes host files
-- under the run directory. It performs no input and modifies no emulated state, so "the
-- engine drew this" cannot be made unfalsifiable by the instrument. The read-only guard in
-- tests/unit/test_mgba_capture.py checks exactly that, which is why the forbidden call
-- names are not spelled out here.
--
-- LIVENESS. A silent channel is not a negative (mgba-runtime skill, s8). liveness.csv
-- carries a row every HEARTBEAT_FRAMES and a final END row, so "the instrument saw
-- nothing" and "the instrument was not running" are distinguishable afterwards.
--
-- ACCEPTED IMAGES. Two shapes are legitimate for this ticket and both are accepted: the
-- content foundation this write extends (10,133,410 bytes) and the candidate it produced
-- (10,141,224 bytes). The launcher pins the exact digest; this check pins the shape, so a
-- session cannot silently run on some other image. The 0.11 dev build returns the bare game
-- code, so both spellings are accepted.

local ACTIVE_MAP_PTR = 0x03001980
local MAP_ENTRY_BASE = 0x0808E2E0
local MAP_ENTRY_SIZE = 0x38
local MAP_COUNT = 452

local VRAM_LO, VRAM_BYTES = 0x06000000, 0x18000
local OBJ_LO, OBJ_BYTES = 0x06010000, 0x8000
local PAL_LO, PAL_BYTES = 0x05000000, 0x400
local OAM_LO, OAM_BYTES = 0x07000000, 0x400

local ACCEPTED_ROM_SIZES = { [10133410] = true, [10141224] = true }

local HEARTBEAT_FRAMES = 120
local DWELL_FRAMES = 45
local MIN_GAP_FRAMES = 420
local MAX_SETTLES = 12
local MAX_FRAMES = 108000
-- Sampling the object-tile region every frame must stay cheap enough not to distort play
-- speed, so the signature strides over it rather than reading all 32768 bytes; the full
-- region is dumped from the emulator only when latching.
local SIGNATURE_STRIDE = 8

local run_dir = nil
if type(rom011_marker_path) == "string" then
    run_dir = rom011_marker_path:match("^(.*)/[^/]*$")
end
local function in_run(name)
    if run_dir then return run_dir .. "/" .. name end
    return name
end

assert(emu ~= nil, "mGBA did not attach the emulation core")
local game_code = emu:getGameCode()
assert(game_code == "BG3E" or game_code == "AGB-BG3E",
    "unexpected game code: " .. tostring(game_code))
local rom_size = emu:romSize()
assert(ACCEPTED_ROM_SIZES[rom_size],
    "unexpected ROM size: " .. tostring(rom_size))

local function safe32(addr)
    local ok, value = pcall(function() return emu:read32(addr) end)
    if ok and value then return value end
    return nil
end

local function map_index()
    local pointer = safe32(ACTIVE_MAP_PTR)
    if not pointer or pointer < MAP_ENTRY_BASE then return nil end
    local delta = pointer - MAP_ENTRY_BASE
    if delta % MAP_ENTRY_SIZE ~= 0 then return nil end
    local index = math.floor(delta / MAP_ENTRY_SIZE)
    if index < 0 or index >= MAP_COUNT then return nil end
    return index
end

local function signature(base, length, stride)
    local data = emu:readRange(base, length)
    local total = 0
    local position = 1
    while position <= #data do
        total = (total + data:byte(position) * (position % 251 + 1)) % 4294967296
        position = position + stride
    end
    return total
end

local function write_file(name, base, length)
    local handle = assert(io.open(in_run(name), "wb"))
    handle:write(emu:readRange(base, length))
    handle:close()
end

local heartbeat = assert(io.open(in_run("liveness.csv"), "w"))
heartbeat:write("frame,map,obj_signature,rom_size\n")
heartbeat:flush()

local settles = assert(io.open(in_run("settles.csv"), "w"))
settles:write("index,frame,map,obj_signature\n")
settles:flush()

local frames = 0
local previous_signature = nil
local stable_frames = 0
local last_capture_frame = -MIN_GAP_FRAMES
local captured = 0
local callback

local function finish(reason)
    settles:close()
    heartbeat:write(string.format("END,%d,%s,%d,%s\n", frames, reason,
        rom_size, tostring(game_code)))
    heartbeat:close()
    local proof = assert(io.open(in_run("proof.txt"), "w"))
    proof:write("status=COMPLETE\n")
    proof:write("reason=" .. reason .. "\n")
    proof:write("frames=" .. frames .. "\n")
    proof:write("settles_captured=" .. captured .. "\n")
    proof:write("rom_size=" .. rom_size .. "\n")
    proof:write("game_code=" .. tostring(game_code) .. "\n")
    proof:close()
    if callback then callbacks:remove(callback) end
end

local function capture(signal)
    local tag = string.format("settle-%02d", captured + 1)
    emu:screenshot(in_run(tag .. ".png"))
    write_file(tag .. "-vram.bin", VRAM_LO, VRAM_BYTES)
    write_file(tag .. "-palette.bin", PAL_LO, PAL_BYTES)
    write_file(tag .. "-oam.bin", OAM_LO, OAM_BYTES)
    settles:write(string.format("%d,%d,%s,%d\n", captured + 1, frames,
        tostring(map_index()), signal))
    settles:flush()
    captured = captured + 1
    last_capture_frame = frames
end

callback = callbacks:add("frame", function()
    frames = frames + 1

    local signal = signature(OBJ_LO, OBJ_BYTES, SIGNATURE_STRIDE)
    if previous_signature == nil then
        previous_signature = signal
        stable_frames = 0
    elseif signal == previous_signature then
        stable_frames = stable_frames + 1
    else
        stable_frames = 0
        previous_signature = signal
    end

    if frames % HEARTBEAT_FRAMES == 0 then
        heartbeat:write(string.format("%d,%s,%d,%d\n", frames,
            tostring(map_index()), signal, rom_size))
        heartbeat:flush()
    end

    if stable_frames >= DWELL_FRAMES and captured < MAX_SETTLES
        and frames - last_capture_frame >= MIN_GAP_FRAMES then
        capture(signal)
        if captured >= MAX_SETTLES then
            finish("all-settles-captured")
            return
        end
    end

    if frames >= MAX_FRAMES then
        finish("frame-limit")
    end
end)
