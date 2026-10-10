-- FRIEND-V3-WT-SPLIT-CONTAINER-001: ONE narrow measurement that decides whether the
-- emulated GBA can reach a container appended past the end of the image file.
--
-- WHY. The ticket's split proof appends a new container at the end of the 10,141,220-byte
-- image and writes its runtime pointer into container-table slot 7. That container lands at
-- file offset >= 10,141,220. The image's ROM header declares 8,388,608 bytes of cart ROM,
-- so the appended region may be outside the cart window the CPU can address. This probe
-- reads three things and nothing else:
--
--   1. the pointer stored in table slot 7 at 0x089A9D04, AFTER the state has loaded;
--   2. the bytes at that pointer;
--   3. the bytes just past the declared cart size, where the append would land.
--
-- All three are emulated-memory reads. A wrong answer here costs one short run and sets
-- the whole split design, so it is measured rather than reasoned about.
--
-- READ-ONLY. No breakpoint, no emulated write, no key. Two host files in the run directory.

local CARTRIDGE = 8388608               -- the size the ROM header declares
local SLOT7 = 0x089A9D04                -- container-table slot 7
local TABLE = 0x089A9CE8                -- container-table base

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")

assert(emu ~= nil, "mGBA did not attach the emulation core")
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
    local log = assert(io.open(exp_dir .. "map.txt", "w"))
    local function note(format, ...)
        log:write(string.format(format, ...) .. "\n")
        log:flush()
    end

    note("romSize=%s declared_cart=%d", tostring(emu:romSize()), CARTRIDGE)

    local function word(address)
        local ok, value = pcall(function() return emu:read32(address) end)
        return (ok and value) or nil
    end

    local function units(address, count)
        local parts = {}
        for index = 0, count - 1 do
            local ok, value = pcall(function() return emu:read16(address + index * 2) end)
            if not ok or value == nil then break end
            if value == 0 then break end
            if value >= 0x20 and value < 0x7F then
                parts[#parts + 1] = string.char(value)
            else
                parts[#parts + 1] = string.format("<%04X>", value)
            end
        end
        return (table.concat(parts))
    end

    -- The state is loaded by the bootstrap AFTER the observer's dofile, so these reads are
    -- taken late in the frame callback, once the state is definitely in memory.
    local frame = 0
    local callback_id
    callback_id = callbacks:add("frame", function()
        frame = frame + 1
        if frame ~= 30 then return end

        note("slot7=0x%s", string.format("%08X", word(SLOT7) or 0))
        for slot = 0, 8 do
            local value = word(TABLE + slot * 4)
            note("slot%d=0x%s", slot, value and string.format("%08X", value) or "unreadable")
        end

        -- Where the append would land, both relative to the file and on the CPU bus.
        local append_file = 10141220
        local append_addr = 0x08000000 + append_file
        note("append_file_offset=%d append_rom_address=0x%s", append_file,
            string.format("%08X", append_addr))
        note("append_addr_readable=%s", tostring(word(append_addr) ~= nil))

        -- The highest addressable byte if the cart window is the declared 8 MiB.
        local top = 0x08000000 + CARTRIDGE - 4
        note("declared_cart_top_word_addr=0x%s value=0x%s", string.format("%08X", top),
            string.format("%08X", word(top) or 0))
        local over = 0x08000000 + CARTRIDGE
        note("first_word_past_declared_cart=0x%s value=0x%s", string.format("%08X", over),
            string.format("%08X", over and word(over) or 0))

        -- A live container, slot 1, as a positive control on the read method.
        local live = word(TABLE + 4)
        note("slot1=0x%s units=%s", live and string.format("%08X", live) or "nil",
            live and units(live, 16) or "?")

        callbacks:remove(callback_id)
        log:close()
        finish("done")
    end)
end

local ok, err = xpcall(run, function(problem) return tostring(problem) end)
if not ok then finish("error:" .. tostring(err)) end
