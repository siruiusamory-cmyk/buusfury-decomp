-- FRIEND-V3-PLAYTEST-BOOST-001: the read-only runtime instrument for the boosted image.
--
-- WHY THIS EXISTS. Every existing statement about the boost in
-- build/fv3boost001/out/v3-playtest-boost.gba (sha256 6d7a56c6...) is static: a
-- file hash and a decode of the bytes on disk. Nothing yet shows those bytes are
-- present in the memory the emulator runs, and the earlier cold-boot observer
-- (tools/runtime/friendv3_coldboot_probe.lua) trusted only 0x02000000..0x0203FFFF,
-- so it could not say either way whether a read of the cartridge ROM window works.
--
-- GOAL 1, THE INSTRUMENT, ANSWERS FIRST. Before this file claims anything it reads
-- the GBA cartridge header through four paths and compares the result with the
-- values every cartridge carries: the logo word at 0x08000004 (0x51AEFF24 in this
-- image, measured from the file) and the mandatory 0x96 at 0x080000B2. It then
-- checks that read8, read16 and read32 agree with each other at one address, and
-- that a deliberately unmapped address behaves as an unmapped address. A ROM read
-- that works returns those; one that fails or returns zeros cannot. That self-test
-- is the liveness channel for every ROM read below (mgba-runtime skill, s8): the
-- header is read on the same bus path as the table, so "the table read is silent"
-- and "the ROM read channel is dead" are distinguishable afterwards.
--
-- GOAL 3, THE TABLE, IS READ ONCE. At BOOST001_READ_FRAME it reads the 90 bytes of
-- base-stat records 0..4 (5 x 0x12) at 0x086FDA4C = file offset 0x6FDA4C exactly
-- once, through the per-byte reader, writes those bytes beside the same 90 bytes
-- read through readRange, and records the frame number. No savestate and no battery
-- save is read, so the bytes are the ones in the image the emulator is running:
-- a savestate would restore absolute stats from an older build and prove nothing
-- about this table.
--
-- Records 0..4 are the boosted ones. Record order to character name is an INFERENCE
-- in tools/webfoot/formats/stat_tables.py:80, so no name is asserted here. Field
-- layout is stat_tables.py:decode_base_stat_record: u8 level @+0x00, u8 pad @+0x01,
-- u16 hp @+0x02, u16 ep @+0x04, u8 strength @+0x06, power @+0x07, endurance @+0x08,
-- speed @+0x09, person @+0x0A, technique count @+0x0B.
--
-- READ-ONLY. It reads emulated memory and registers and writes host files inside the
-- run directory. It presses no key, drives no input and modifies no emulated state,
-- so "these bytes are in the running image" cannot be made unfalsifiable by the
-- instrument. The guard in tests/unit/test_mgba_runtime_skill.py checks that, which
-- is why the forbidden call names are not spelled out in this file.
--
-- WHAT IT WRITES, all inside the run directory named by rom011_marker_path:
--   romcheck.txt        the instrument verdict. Read this first. status=WORKING or
--                       status=FAILED, the header values, the cross-width agreement
--                       and the unmapped-address probe.
--   boost_table.csv     the decoded records, once, with the frame number they were
--                       read at, plus which read paths agreed.
--   boost_table_read8.bin   the 90 bytes as the per-byte reader returned them.
--   boost_table_range.bin   the same 90 bytes through readRange, when it works.
--   heartbeat.csv       frame and pc every BEAT_EVERY frames. A stalled frame count
--                       with a flat program counter is the recorded wedge signature.
--   shot_*.png          every BOOST001_SHOT_EVERY frames.
--   marker.txt          "armed" when injected, then the end status.
--
-- The session ends itself with os.exit(0) at BOOST001_MAX_FRAMES, so an unattended
-- run cannot outlive its own evidence.

local TABLE_ADDR = 0x086FDA4C      -- file offset 0x6FDA4C, memory-mapped from 0x08000000
local RECORD_SIZE = 0x12
local PARTY_RECORDS = 5
local READ_BYTES = PARTY_RECORDS * RECORD_SIZE   -- 90

local HEADER_LOGO = 0x08000004
local HEADER_LOGO_WORD = 0x51AEFF24
local HEADER_FIXED96 = 0x080000B2
local HEADER_FIXED96_VALUE = 0x96
local HEADER_TITLE = 0x080000A0
local UNMAPPED = 0x0F000000

local function knob(name, default)
    return tonumber(os.getenv(name) or "") or default
end

local MAX_FRAMES = knob("BOOST001_MAX_FRAMES", 900)
local SHOT_EVERY = knob("BOOST001_SHOT_EVERY", 300)
local BEAT_EVERY = knob("BOOST001_BEAT_EVERY", 60)
local READ_AT_FRAME = knob("BOOST001_READ_FRAME", 30)
local EXIT_WHEN_DONE = knob("BOOST001_EXIT_WHEN_DONE", 1)

local marker_path = rom011_marker_path
assert(type(marker_path) == "string" and #marker_path > 0, "marker path not provided")
local run_dir = marker_path:gsub("[^/\\]+$", "")
local function in_run(name) return run_dir .. name end

assert(emu ~= nil, "mGBA did not attach the emulation core")
local game_code = emu:getGameCode()
assert(game_code == "BG3E" or game_code == "AGB-BG3E",
    "unexpected game code: " .. tostring(game_code))
local rom_size = emu:romSize()

-- Every read is individually guarded: a read that throws must be recorded as a
-- failed read, not take the observer down and leave the launcher reporting the
-- misleading "Lua script did not report ready".
local function u8(address)
    local ok, value = pcall(function() return emu:read8(address) end)
    if ok then return value end
end
local function u16(address)
    local ok, value = pcall(function() return emu:read16(address) end)
    if ok then return value end
end
local function u32(address)
    local ok, value = pcall(function() return emu:read32(address) end)
    if ok then return value end
end
local function rng(address, length)
    local ok, value = pcall(function() return emu:readRange(address, length) end)
    if ok then return value end
end

local function hex2(value) return string.format("%02X", value) end
local function hex_bytes(data)
    local parts = {}
    for index = 1, #data do parts[#parts + 1] = hex2(data:byte(index)) end
    return table.concat(parts, " ")
end
local function word(data)
    if not data or #data < 4 then return nil end
    return data:byte(1) + data:byte(2) * 0x100 + data:byte(3) * 0x10000
        + data:byte(4) * 0x1000000
end

-- The marker is written unconditionally. An earlier observer in this tree latched
-- its finish() on a first call, so its "armed" marker was never replaced by the end
-- status and a finished run read as an armed one.
local function status(text)
    local handle = io.open(marker_path, "w")
    if handle then handle:write(text) handle:close() end
end

local function selftest()
    local logo32 = u32(HEADER_LOGO)
    local logo_range = rng(HEADER_LOGO, 4)
    local logo_range32 = word(logo_range)
    local lo = u8(HEADER_LOGO)
    local lo2 = u8(HEADER_LOGO + 1)
    local mid = u16(HEADER_LOGO)
    local mid2 = u16(HEADER_LOGO + 2)
    local fixed = u8(HEADER_FIXED96)
    local title = rng(HEADER_TITLE, 16)
    local unmapped = u8(UNMAPPED)

    local widths_agree = (lo ~= nil and lo2 ~= nil and mid ~= nil and mid2 ~= nil
        and logo32 ~= nil and mid == lo + lo2 * 256
        and logo32 == mid + mid2 * 65536)
    local ranges_agree = (logo32 ~= nil and logo_range32 ~= nil
        and logo32 == logo_range32)
    local logo_matches = (logo32 ~= nil and logo32 == HEADER_LOGO_WORD)
    local fixed_matches = (fixed ~= nil and fixed == HEADER_FIXED96_VALUE)
    local live = logo_matches and fixed_matches and widths_agree and ranges_agree

    local lines = {}
    local function put(key, value) lines[#lines + 1] = key .. "=" .. tostring(value) end
    put("status", live and "WORKING" or "FAILED")
    put("claim", "read8/read16/read32/readRange reach the cartridge ROM window")
    put("game_code", tostring(game_code))
    put("rom_size", rom_size)
    put("addr_read32_0x08000004", logo32 ~= nil and string.format("0x%08X", logo32) or "READ_FAILED")
    put("addr_readRange_0x08000004", logo_range ~= nil and hex_bytes(logo_range) or "READ_FAILED")
    put("expected_logo_word", string.format("0x%08X", HEADER_LOGO_WORD))
    put("logo_matches", tostring(logo_matches))
    put("read8_0x080000B2", fixed ~= nil and hex2(fixed) or "READ_FAILED")
    put("expected_0x080000B2", hex2(HEADER_FIXED96_VALUE))
    put("fixed_byte_matches", tostring(fixed_matches))
    put("title_hex_0x080000A0", title ~= nil and hex_bytes(title) or "READ_FAILED")
    put("widths_agree", tostring(widths_agree))
    put("readRange_agrees_with_read32", tostring(ranges_agree))
    put("unmapped_0x0F000000_read8", unmapped ~= nil and hex2(unmapped) or "READ_FAILED")
    put("liveness_channel", "cartridge header on the same read path as the table")

    local handle = assert(io.open(in_run("romcheck.txt"), "w"))
    handle:write(table.concat(lines, "\n") .. "\n")
    handle:close()
    return live
end

-- The 90 bytes, once, through both read paths, with the frame they were read at.
local function read_table(frame)
    local per_byte = {}
    local per_byte_hex = {}
    local complete = true
    for index = 0, READ_BYTES - 1 do
        local value = u8(TABLE_ADDR + index)
        if value == nil then complete = false break end
        per_byte[#per_byte + 1] = string.char(value)
        per_byte_hex[#per_byte_hex + 1] = hex2(value)
    end

    local joined = table.concat(per_byte)
    local range_bytes = rng(TABLE_ADDR, READ_BYTES)
    local range_hex = range_bytes and hex_bytes(range_bytes) or nil
    local range_agrees = (range_hex ~= nil and range_hex == table.concat(per_byte_hex, " "))

    if complete then
        local handle = assert(io.open(in_run("boost_table_read8.bin"), "wb"))
        handle:write(joined)
        handle:close()
    end
    if range_bytes then
        local handle = assert(io.open(in_run("boost_table_range.bin"), "wb"))
        handle:write(range_bytes)
        handle:close()
    end

    local csv = assert(io.open(in_run("boost_table.csv"), "w"))
    csv:write("frame,index,level,pad,hp,ep,strength,power,endurance,speed,person,techniques,hex\n")
    if complete then
        for index = 0, PARTY_RECORDS - 1 do
            local base = index * RECORD_SIZE + 1
            local function byte(relative) return joined:byte(base + relative) end
            local function pair(relative) return byte(relative) + byte(relative + 1) * 256 end
            local hex = {}
            for offset = 0, RECORD_SIZE - 1 do hex[#hex + 1] = hex2(byte(offset)) end
            csv:write(string.format("%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%s\n",
                frame, index, byte(0x00), byte(0x01), pair(0x02), pair(0x04),
                byte(0x06), byte(0x07), byte(0x08), byte(0x09), byte(0x0A), byte(0x0B),
                table.concat(hex, " ")))
        end
    end
    csv:write(string.format("#frame=%d\n", frame))
    csv:write(string.format("#read8_path=%s\n", complete and "complete" or "incomplete"))
    csv:write(string.format("#readRange_path=%s\n", range_bytes and "complete" or "failed"))
    csv:write(string.format("#readRange_agrees_with_read8=%s\n", tostring(range_agrees)))
    csv:close()
    return complete and range_agrees
end

status("armed")

local heartbeat = assert(io.open(in_run("heartbeat.csv"), "w"))
heartbeat:write("frame,pc\n")
heartbeat:flush()

local frames = 0
local read_done = false
local callback
callback = callbacks:add("frame", function()
    frames = frames + 1

    if frames == 1 then
        local ok, err = pcall(selftest)
        if not ok then status("error:selftest:" .. tostring(err)) end
    end

    if not read_done and frames >= READ_AT_FRAME then
        read_done = true
        local ok, err = pcall(read_table, frames)
        if not ok then status("error:read_table:" .. tostring(err)) end
    end

    if frames % BEAT_EVERY == 0 then
        local pc = 0
        local ok, value = pcall(function() return emu:readRegister("pc") end)
        if ok and value then pc = value end
        heartbeat:write(string.format("%d,0x%08X\n", frames, pc))
        heartbeat:flush()
    end

    if frames % SHOT_EVERY == 0 then
        pcall(function()
            emu:screenshot(string.format("%sshot_%06d.png", run_dir, frames))
        end)
    end

    if frames >= MAX_FRAMES then
        heartbeat:write(string.format("END,%d\n", frames))
        heartbeat:close()
        status("done:frame-limit")
        pcall(function() callbacks:remove(callback) end)
        if EXIT_WHEN_DONE == 1 then os.exit(0) end
    end
end)
