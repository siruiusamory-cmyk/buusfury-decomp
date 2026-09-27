-- MAP-WARP-CREATE-RUNTIME-001 read-only created-transition observer.
--
-- READ-ONLY with respect to emulated state and input: it calls the emulator's
-- memory readers, and it writes only host files inside the run directory. It
-- contains none of the input- or memory-modifying API names the read-only guard
-- in tests/unit/test_mgba_capture.py greps for, and deliberately does not spell
-- them out here either, comments included.
--
-- WHY IT EXISTS. The ticket proves that a transition record CREATED through the
-- DragonByte Z Workbench - a record that does not exist in the canonical image -
-- is reached by the retail engine's own traversal, on the shipped derivative
-- (16,777,216 bytes, sha256
-- 03A30D4BACF05939FAE44161334344CF3809B5884BE7E749C857337A3E6DE78A). A changed
-- ROM is not that evidence, so the observer records, from the running emulator,
-- the route the engine itself walks, every hop of it.
--
-- THE NEW RECORD IS FOUND ONLY THROUGH THAT ROUTE. Nothing here names the
-- created record's address, nor the appended array that holds it, nor the map
-- root those hang on. The build's own addresses for them are deliberately absent
-- from this file: deriving each element through the engine's route is what makes
-- a row evidence, and a written-down address would make it an assertion. Every
-- element is derived exactly as the engine derives it:
--
--     MapEntry[map].+0x2C -> word -> root
--     root + 0x40 (count, u32), root + 0x44 (array pointer, u32)
--     array + element * 4 -> the element word -> the record it names
--
-- so a row shows that the record being read is one the engine would reach.
--
-- WHY ELEMENT 2 IS THE NEW ONE. Canonical map 40's pointer array holds TWO
-- elements (the root's own +0x40 count reads 2), and both are retail records
-- inside the original 8 MiB image. The derivative appends a THIRD element: the
-- count itself reads 3, and the word at index 2 names a record the build placed
-- above the original 8 MiB EOF, together with the array that now points at it.
-- So element index 2 is the created transition: it is the element the root's own
-- count admits only in the derivative, and the record it names lies outside the
-- canonical image. On the canonical image the same index is reported `absent`, a
-- conclusion read from the count rather than from whatever bytes happen to
-- follow the array - that is the retail control, and it is what turns "count 3"
-- in the derivative into a measurement instead of an assumption.
--
-- WHAT EACH ROW CARRIES. For elements 0, 1 and 2: the MapEntry + 0x2C source
-- word, the root word, the root's +0x40 count and +0x44 array pointer, the raw
-- element word at array + element * 4, and the record address that word resolves
-- to. For every element the count admits, the record's own live fields: the
-- destination key bytes at +0x11/+0x12 and the map the engine's own two-byte
-- MapEntry scan resolves them to, the four region endpoints as a byte run over
-- +0x08..+0x0E, the byte at +0x10, and the arrival pair - the u16 at +0x14, and
-- the two bytes at +0x16/+0x17 that form its second half.
--
-- The live-map channel is kept as well, unchanged from the reference observer:
-- the engine's own active-MapEntry pointer 0x03001980, table base 0x0808E2E0,
-- stride 0x38, with a liveness heartbeat and a change-triggered row, so a map
-- change and the exact frame it happened on are attributable.
--
-- ROW KINDS. `ROUTE` is one element of the array - elements 0 and 1 always, and
-- element 2 when the root's count does not admit it (status `absent`, the
-- canonical control). Element 2's row is `CREATED` whenever the count does admit
-- the index, so the created transition is directly greppable; its status is
-- `present` when the element word names a record inside the loaded image and
-- `unreadable` when the word is admitted by the count but is not a plausible ROM
-- address. `MAP` is a live map change, `HEARTBEAT` is liveness, and
-- `ROUTE_UNRESOLVED` is said out loud once when the route never resolves, so a
-- silent channel cannot be mistaken for a quiet one.
--
-- RUNTIME-PROVEN ADDRESSES (do NOT re-derive):
--   0x03001980 = live MapEntry pointer; table base 0x0808E2E0, stride 0x38.
-- The record route offsets come from the transition authority:
--   MapEntry + 0x2C, root + 0x40 (count) / +0x44 (array), element width 4, and
--   the record's own +0x08..+0x17 layout.
--
-- Both accepted images are observed: the canonical 8,388,608 bytes and the
-- derivative 16,777,216 bytes. Any other size is refused rather than read.

local ACTIVE_MAP_PTR = 0x03001980
local MAP_ENTRY_BASE = 0x0808E2E0
local MAP_ENTRY_SIZE = 0x38
local MAP_ENTRY_SOURCE_OFFSET = 0x2C
local ROOT_COUNT_OFFSET = 0x40
local ROOT_ARRAY_OFFSET = 0x44
local ELEMENT_WIDTH = 4

local RECORD_REGION_OFFSET = 0x08
local RECORD_BYTE_0X10_OFFSET = 0x10
local RECORD_KEY_HIGH_OFFSET = 0x11
local RECORD_KEY_LOW_OFFSET = 0x12
local RECORD_ARRIVAL_X_OFFSET = 0x14
local RECORD_ARRIVAL_Y_LOW_OFFSET = 0x16
local RECORD_ARRIVAL_Y_HIGH_OFFSET = 0x17

local MAP_COUNT = 452
local TARGET_MAP = 40
-- Elements 0 and 1 are the canonical pair. Element 2 is the index the derivative
-- appends, and the index the canonical count refuses.
local FIRST_ELEMENT = 0
local CREATED_ELEMENT = 2
local LAST_ELEMENT = 2

local ROM_BASE = 0x08000000
local CANONICAL_ROM_SIZE = 8388608
local EXPANDED_ROM_SIZE = 16777216

-- 120 frames is two seconds at 60fps: frequent enough that a silent channel is
-- distinguishable from a quiet one, cheap enough not to disturb play.
local HEARTBEAT_EVERY = 120
-- Bounded so a long session cannot fill the disk.
local MAX_ROWS = 40000

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

-- Both images this ticket observes are accepted; a third size would mean the
-- run is not observing either build, so it is refused rather than guessed at.
local rom_size = emu:romSize()
assert(rom_size == CANONICAL_ROM_SIZE or rom_size == EXPANDED_ROM_SIZE,
    "unexpected ROM size: " .. tostring(rom_size))
local ROM_END = ROM_BASE + rom_size

local function safe8(addr)
    local ok, v = pcall(function() return emu:read8(addr) end)
    if ok and v then return v end
    return nil
end

local function safe16(addr)
    local ok, v = pcall(function() return emu:read16(addr) end)
    if ok and v then return v end
    return nil
end

local function safe32(addr)
    local ok, v = pcall(function() return emu:read32(addr) end)
    if ok and v then return v end
    return nil
end

-- A pointer is only followed when it names a byte of the loaded image. This is
-- what keeps "the count does not admit this index" apart from "the word is
-- there but is not an address", and it stops a mirrored or open-bus read from
-- being reported as a record.
local function in_rom(pointer)
    return pointer ~= nil and pointer >= ROM_BASE and pointer < ROM_END
end

-- The live map identity, from the pointer the engine itself keeps.
local function live_map_index()
    local entry = safe32(ACTIVE_MAP_PTR)
    if entry == nil or entry < MAP_ENTRY_BASE then return nil, entry end
    local offset = entry - MAP_ENTRY_BASE
    if offset % MAP_ENTRY_SIZE ~= 0 then return nil, entry end
    local index = offset // MAP_ENTRY_SIZE
    if index >= MAP_COUNT then return nil, entry end
    return index, entry
end

-- The route's shared prefix for one map: MapEntry + 0x2C -> word -> root, with
-- the root's own count and array pointer read in the same walk. Every element
-- below hangs off this one derivation, which is why the prefix is resolved once
-- per sample rather than repeated per element.
local function route_root(map_index)
    local entry = MAP_ENTRY_BASE + map_index * MAP_ENTRY_SIZE
    local source = safe32(entry + MAP_ENTRY_SOURCE_OFFSET)
    if not in_rom(source) then return nil end
    local root = safe32(source)
    if not in_rom(root) then return nil end
    -- The count is a full 32-bit field: the engine reads +0x40 and +0x44 in one
    -- load-multiple, so reading it as a halfword would invent a second field.
    local count = safe32(root + ROOT_COUNT_OFFSET)
    local array = safe32(root + ROOT_ARRAY_OFFSET)
    if count == nil or not in_rom(array) then return nil end
    return { entry = entry, source = source, root = root, count = count,
             array = array }
end

-- The same two-byte scan the engine's own lookup performs over the MapEntry
-- table: +0x00 and +0x01 compared separately against the record's two bytes.
local function resolve_key(high, low)
    for index = 0, MAP_COUNT - 1 do
        local base = MAP_ENTRY_BASE + index * MAP_ENTRY_SIZE
        if safe8(base) == high and safe8(base + 1) == low then
            return index
        end
    end
    return nil
end

local function hex8(value)
    if value == nil then return nil end
    return string.format("%02x", value)
end

local function hex16(value)
    if value == nil then return nil end
    return string.format("%04x", value)
end

local function hex32(value)
    if value == nil then return nil end
    return string.format("0x%08X", value)
end

-- The record's own live fields, read only through the address the engine's route
-- resolved. The region is logged as its raw byte run so a reader can see that
-- nothing was masked, aligned or reordered on the way into the CSV.
local function record_fields(record)
    local parts = {}
    for i = 0, 7 do
        parts[#parts + 1] = hex8(safe8(record + RECORD_REGION_OFFSET + i)) or ""
    end
    return {
        region = table.concat(parts),
        byte_0x10 = hex8(safe8(record + RECORD_BYTE_0X10_OFFSET)),
        arrival_14 = hex16(safe16(record + RECORD_ARRIVAL_X_OFFSET)),
        arrival_16 = hex8(safe8(record + RECORD_ARRIVAL_Y_LOW_OFFSET)),
        arrival_17 = hex8(safe8(record + RECORD_ARRIVAL_Y_HIGH_OFFSET)),
    }
end

-- One element of the array. The element word is read ONLY when the root's own
-- count admits the index: past the count there is no element, and reading
-- whatever follows the array would fabricate a record address out of unrelated
-- bytes. `absent` is therefore a conclusion from the count, not from a read.
local function sample_element(root_route, element)
    local sample = { element = element, status = "unresolved", element_ptr = nil,
                     record = nil, key_hi = nil, key_lo = nil, key_map = nil,
                     fields = nil }
    if root_route == nil then return sample end
    if element >= root_route.count then
        sample.status = "absent"
        return sample
    end
    local word = root_route.array + element * ELEMENT_WIDTH
    if word < ROM_BASE or word + ELEMENT_WIDTH > ROM_END then
        sample.status = "unreadable"
        return sample
    end
    local pointer = safe32(word)
    sample.element_ptr = pointer
    if not in_rom(pointer) then
        sample.status = "unreadable"
        return sample
    end
    sample.status = "present"
    sample.record = pointer
    sample.key_hi = safe8(pointer + RECORD_KEY_HIGH_OFFSET)
    sample.key_lo = safe8(pointer + RECORD_KEY_LOW_OFFSET)
    if sample.key_hi ~= nil and sample.key_lo ~= nil then
        sample.key_map = resolve_key(sample.key_hi, sample.key_lo)
    end
    sample.fields = record_fields(pointer)
    return sample
end

local create_path = in_run("create-watch.csv")
local create_file = assert(io.open(create_path, "w"), "cannot open create-watch.csv")
create_file:write(
    "kind,frame,map_index,map_entry_ptr,element,status,source,root,root_count," ..
    "array,element_ptr,record,key_hi,key_lo,key_resolves_to,region_hex," ..
    "byte_0x10,arrival_14,arrival_16,arrival_17,note\n")
create_file:flush()

local function cell(value)
    if value == nil then return "" end
    return tostring(value)
end

local rows = 0
-- Values are joined positionally, so a column can never drift from its header
-- through a formatting-arity mistake, and a nil is always an empty cell rather
-- than a dropped one. Notes stay comma-free so every row is exactly as wide as
-- the header.
local function emit(kind, frame, map_index, entry, element, status, root_route,
                    sample, note)
    if rows >= MAX_ROWS then return end
    local fields = sample and sample.fields or nil
    create_file:write(table.concat({
        kind,
        tostring(frame),
        cell(map_index),
        cell(hex32(entry)),
        cell(element),
        cell(status),
        cell(root_route and hex32(root_route.source) or nil),
        cell(root_route and hex32(root_route.root) or nil),
        cell(root_route and tostring(root_route.count) or nil),
        cell(root_route and hex32(root_route.array) or nil),
        cell(sample and hex32(sample.element_ptr) or nil),
        cell(sample and hex32(sample.record) or nil),
        cell(sample and hex8(sample.key_hi) or nil),
        cell(sample and hex8(sample.key_lo) or nil),
        cell(sample and sample.key_map or nil),
        cell(fields and fields.region or nil),
        cell(fields and fields.byte_0x10 or nil),
        cell(fields and fields.arrival_14 or nil),
        cell(fields and fields.arrival_16 or nil),
        cell(fields and fields.arrival_17 or nil),
        cell(note),
    }, ",") .. "\n")
    create_file:flush()
    rows = rows + 1
end

local function emit_element(frame, map_index, entry, root_route, sample, base_note)
    local kind = "ROUTE"
    local note = base_note
    if sample.element == CREATED_ELEMENT then
        note = note .. ";element 2 is the created-transition index"
        if sample.status == "present" or sample.status == "unreadable" then
            kind = "CREATED"
        end
    end
    if sample.status == "absent" then
        note = note .. ";not read - root_count " .. tostring(root_route.count) ..
            " does not admit the index"
    end
    emit(kind, frame, map_index, entry, sample.element, sample.status, root_route,
        sample, note)
end

local frame = 0
local last_map = nil
local last_signature = nil
local unresolved_reported = false

callbacks:add("frame", function()
    frame = frame + 1

    local map_index, entry = live_map_index()
    local changed = (map_index ~= nil and map_index ~= last_map)

    -- The route is sampled on the first frames that read it, on every map
    -- change, and on every heartbeat. The route words live in ROM, so a
    -- difference between two samples would itself be a finding; the signature is
    -- what turns that difference into rows instead of letting it pass unnoticed.
    -- Re-sampling on a map change keeps the claim attributable to the frame the
    -- change was observed on, and a heartbeat sample bounds how long a silent
    -- change could stay unrecorded.
    local sample_due = (last_signature == nil) or changed
        or (frame % HEARTBEAT_EVERY == 0)
    local root_route, samples, signature = nil, nil, nil
    if sample_due then
        root_route = route_root(TARGET_MAP)
        samples = {}
        local parts = {}
        for index = FIRST_ELEMENT, LAST_ELEMENT do
            local sample = sample_element(root_route, index)
            samples[index] = sample
            parts[#parts + 1] = sample.status .. ":" .. cell(hex32(sample.record))
        end
        if root_route ~= nil then
            signature = cell(hex32(root_route.root)) .. "/" ..
                tostring(root_route.count) .. "/" ..
                cell(hex32(root_route.array)) .. "/" .. table.concat(parts, "|")
        end
    end

    if root_route ~= nil and signature ~= last_signature then
        local note
        if last_signature == nil then
            note = "first route sample via MapEntry+0x2C -> root+0x44"
        elseif changed then
            note = "route re-sampled on map change from=" .. tostring(last_map)
        else
            note = "route changed since the previous sample"
        end
        for index = FIRST_ELEMENT, LAST_ELEMENT do
            emit_element(frame, map_index, entry, root_route, samples[index], note)
        end
        last_signature = signature
    elseif root_route == nil and (not unresolved_reported) and frame >= 600 then
        -- Ten seconds in and the route still does not resolve: say so once, so a
        -- silent channel is distinguishable from a resolved one.
        emit("ROUTE_UNRESOLVED", frame, map_index, entry, nil, nil, nil, nil,
            "map " .. TARGET_MAP .. " elements " .. FIRST_ELEMENT .. ".." ..
            LAST_ELEMENT .. " did not resolve through MapEntry+0x2C -> root+0x44")
        unresolved_reported = true
    end

    if changed then
        local note
        if last_map == nil then
            note = "first observed map"
        else
            note = "from=" .. tostring(last_map)
        end
        emit("MAP", frame, map_index, entry, nil, nil, root_route, nil, note)
        last_map = map_index
    elseif frame % HEARTBEAT_EVERY == 0 then
        emit("HEARTBEAT", frame, map_index, entry, nil, nil, nil, nil, "")
    end

    if frame == 1 and type(rom011_marker_path) == "string" then
        local mk = io.open(rom011_marker_path, "w")
        if mk then mk:write("armed\n") mk:close() end
    end
end)
