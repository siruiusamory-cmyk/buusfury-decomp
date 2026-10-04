-- SPRITE-NEW-RUNTIME-001 read-only observer and minimal input driver.
--
-- WHAT IT DOES NOT DO. It never writes emulated memory. It never touches a ROM
-- or a save on disk. The only emulated state it changes is the controller input
-- register, through mGBA's own `emu:setKeys`, and only when a schedule asks for
-- it. Everything it produces is a host file inside the run directory.
--
-- HOW IT PROVES THE IDENTITY RESOLVED. It does not infer rendering from a
-- picture alone and it does not scan EWRAM hoping to find the right object. It
-- installs one breakpoint at 0x0800F6B4, the instruction the engine executes
-- immediately AFTER `bl 0x08000158` returns inside the placement constructor:
--
--   0x0800F6AE  ldr  r0,[r5,#0x10]   ; the placement's sprite id
--   0x0800F6B0  bl   0x08000158      ; the registry accessor
--   0x0800F6B4  ...                  ; r0 = the resolved character structure
--
-- so each hit yields, without any interpretation, the placement record (r5), the
-- sprite id it asked for, the actor object being built (r4), and the structure
-- the engine resolved (r0). A hit whose structure equals the new identity's
-- address is the engine's own record that it resolved an identity the retail
-- image does not contain. The actor pointer from that hit is then read on every
-- later tick, so the selected animation, the selected frame record and the
-- composition size are followed over time rather than sampled once.
--
-- It also reports the active MapEntry each tick (pointer 0x03001980 against the
-- declared MapEntry run 0x0808E2E0, 0x38 stride, 452 records), so the run can
-- state which map it was looking at instead of guessing from a screenshot.
--
-- Environment, set by the launcher:
--   SPRITENEW001_OUT_ROOT    where outputs go
--   SPRITENEW001_STRUCTURE   the new character structure's ROM address
--   SPRITENEW001_SPRITE_ID   the new sprite id, so a hit can name its placement
--   SPRITENEW001_SCRIPT      a key schedule name, see SCHEDULES
--   SPRITENEW001_TICKS       frames to observe before finishing

local OUT_ROOT = os.getenv("SPRITENEW001_OUT_ROOT") or "spritenew001/out"
local STRUCTURE = tonumber(os.getenv("SPRITENEW001_STRUCTURE") or "0x088005B4")
local NEW_SPRITE_ID = tonumber(os.getenv("SPRITENEW001_SPRITE_ID") or "307")
local SCRIPT = os.getenv("SPRITENEW001_SCRIPT") or "human"
local TICKS = tonumber(os.getenv("SPRITENEW001_TICKS") or "3600")

local CONSTRUCTOR_AFTER_RESOLVE = 0x0800F6B4
local ACTIVE_MAP_PTR = 0x03001980
local MAP_ENTRY_BASE = 0x0808E2E0
local MAP_ENTRY_SIZE = 0x38
local MAP_ENTRY_COUNT = 452

local PLACEMENT_SPRITE_ID = 0x10
local ACTOR_ANIMATION_FIELD = 0x50
local ACTOR_FRAME_FIELD = 0x54
local ACTOR_FRAME_CACHE_FIELD = 0x30
local ACTOR_FRAME_SIZE_FIELD = 0x48
local ACTOR_FRAMEBUF_FIELD = 0x40
local ACTOR_STRUCTURE_FIELD = 0x58
-- The compositor reads the actor's screen x/y here (0x0800EF7C), so a spawned
-- actor's own position can be reported instead of inferred from a picture.
local ACTOR_SCREEN_X_FIELD = 0x6C
local ACTOR_SCREEN_Y_FIELD = 0x70

local K = {
    A = 0x0001, B = 0x0002, SELECT = 0x0004, START = 0x0008,
    RIGHT = 0x0010, LEFT = 0x0020, UP = 0x0040, DOWN = 0x0080,
    R = 0x0100, L = 0x0200,
}
local HOLD = 6
local SCHEDULES = {
    -- Observe only; the operator plays. This is the mode the proof uses.
    human = {},
    -- Boot to the title screen and stop, to see what a fresh boot shows.
    boot = { { 180, K.START } },
    -- Title then confirms, for the "press Start, choose the saved game" path.
    menu = { { 180, K.START }, { 420, K.A }, { 560, K.A }, { 700, K.A }, { 840, K.A } },
}

assert(emu ~= nil, "mGBA did not attach the emulation core")
local code = emu:getGameCode()
assert(code == "BG3E" or code == "AGB-BG3E", "unexpected game code: " .. tostring(code))

local function hex(v)
    if v == nil then return "" end
    return string.format("0x%08X", v)
end

local function safe(fn, ...)
    local ok, value = pcall(fn, ...)
    if ok then return value end
    return nil
end

local function r8(a) return tonumber(safe(emu.read8, emu, a)) end
local function r16(a) return tonumber(safe(emu.read16, emu, a)) end
local function r32(a) return tonumber(safe(emu.read32, emu, a)) end

local function map_index()
    local entry = r32(ACTIVE_MAP_PTR)
    if entry == nil or entry < MAP_ENTRY_BASE then return nil, entry end
    local offset = entry - MAP_ENTRY_BASE
    if offset % MAP_ENTRY_SIZE ~= 0 then return nil, entry end
    local index = math.floor(offset / MAP_ENTRY_SIZE)
    if index < 0 or index >= MAP_ENTRY_COUNT then return nil, entry end
    return index, entry
end

-- --- the resolution evidence ------------------------------------------------

local frame = 0
local hits = 0
local matched = {}          -- actor pointers built from the new identity
local matched_set = {}
local hit_log = {}
local shots = {}            -- { frame = ..., tag = ... } pending screenshots
local frames = 0
local maps_seen = {}        -- every distinct map index, in the order first seen
local maps_seen_set = {}
local pending_maps = {}

local function note_map(index)
    if index and not maps_seen_set[index] then
        maps_seen_set[index] = true
        maps_seen[#maps_seen + 1] = index
        pending_maps[#pending_maps + 1] = { index = index, frame = frame }
    end
end

local function note_hit(placement, sprite_id, actor, structure)
    hits = hits + 1
    local is_new = (structure == STRUCTURE)
    local actor_sprite = placement and r32(placement + PLACEMENT_SPRITE_ID) or nil
    hit_log[#hit_log + 1] = string.format(
        "frame=%d hit=%d is_new_identity=%s placement=%s placement_sprite_id=%s " ..
        "requested_sprite_id=%s actor=%s structure=%s",
        frame, hits, tostring(is_new), hex(placement),
        tostring(actor_sprite), tostring(sprite_id), hex(actor), hex(structure))
    if is_new then
        if not matched_set[actor] then
            matched_set[actor] = true
            matched[#matched + 1] = actor
        end
        -- Written the instant it happens, so the operator and the collector can
        -- both see that the run has already proved its point without waiting for
        -- the frame budget to expire.
        local found = io.open(OUT_ROOT .. "/FOUND.txt", "w")
        if found then
            found:write(string.format(
                "frame=%d\nnew_sprite_id=%d\nstructure=%s\nactor=%s\n" ..
                "placement=%s\nplacement_sprite_id=%s\nmap_index=%s\n",
                frame, NEW_SPRITE_ID, hex(structure), hex(actor), hex(placement),
                tostring(actor_sprite), tostring((map_index()))))
            found:close()
        end
        console:log("SPRITENEW001 NEW IDENTITY RESOLVED at frame " ..
            tostring(frame) .. " actor=" .. hex(actor))
        -- Two shots: the actor is built before it is drawn, and the first one can
        -- land while the map is still settling.
        shots[#shots + 1] = { frame = frame + 20, tag = "resolve" }
        shots[#shots + 1] = { frame = frame + 90, tag = "settled" }
    end
end

safe(emu.setBreakpoint, emu, function(_info)
    local actor = tonumber(safe(emu.readRegister, emu, "r4"))
    local placement = tonumber(safe(emu.readRegister, emu, "r5"))
    local structure = tonumber(safe(emu.readRegister, emu, "r0"))
    local sprite_id = placement and r32(placement + PLACEMENT_SPRITE_ID) or nil
    note_hit(placement, sprite_id, actor, structure)
end, CONSTRUCTOR_AFTER_RESOLVE)

-- MAP-OBJECT (sibling) NPCs, and the one question this exists to answer: which of
-- them actually WALKS. Map 102's park objects are the sibling family, built by
-- 0x0800A7A0. At 0x0800A7C0 r4 is the freshly allocated actor and r5 the ROM
-- object record, and the constructor copies the record's +0x08..+0x0F halfwords
-- straight to actor+0x48 - so actor+0x48 is the NPC's own x and +0x4A its y. That
-- is a measured layout, not an inferred one, and it makes "does this NPC move" a
-- question about bytes rather than about a picture.
-- WHAT IS WATCHED, AND WHY IT IS A WINDOW RATHER THAN A GUESS. An earlier
-- revision read actor+0x48 as the NPC's position and concluded that map 102's
-- objects never move. That offset came from a DIFFERENT actor class and the
-- conclusion was an artifact of the instrument, not a fact about the game. So
-- this version makes no claim about which word is the position: it samples a
-- window of the actor's own fields once per frame and reports, per word, how far
-- it travelled. Whichever words change are the live state, and the code that
-- drives them can then be read with the field identified instead of assumed.
local SIBLING_AFTER_ALLOC = 0x0800A7C0
local SIBLING_WINDOW_START = 0x08
local SIBLING_WINDOW_WORDS = 12          -- +0x08 .. +0x37
local siblings = {}
local sibling_seen = {}
safe(emu.setBreakpoint, emu, function(_info)
    local actor = tonumber(safe(emu.readRegister, emu, "r4"))
    local record = tonumber(safe(emu.readRegister, emu, "r5"))
    if actor == nil or record == nil or sibling_seen[actor] then return end
    sibling_seen[actor] = true
    local words = {}
    for i = 0, SIBLING_WINDOW_WORDS - 1 do
        words[i] = {
            address = actor + SIBLING_WINDOW_START + 4 * i,
            first = nil, last = nil, min = nil, max = nil,
        }
    end
    local record_words = {}
    for i = 0, 11 do
        record_words[i] = r32(record + 4 * i)
    end
    siblings[#siblings + 1] = {
        actor = actor, record = record, words = words,
        record_words = record_words, samples = 0,
    }
end, SIBLING_AFTER_ALLOC)

local function sample_siblings()
    for _, s in ipairs(siblings) do
        s.samples = s.samples + 1
        for i = 0, SIBLING_WINDOW_WORDS - 1 do
            local w = s.words[i]
            local v = r32(w.address)
            if v then
                if w.first == nil then
                    w.first, w.min, w.max = v, v, v
                else
                    if v < w.min then w.min = v end
                    if v > w.max then w.max = v end
                end
                w.last = v
            end
        end
    end
end

local function travelled(w)
    if w.min == nil then return nil end
    return w.max - w.min
end

-- The PLAYER path, for the run whose controlled actor is the character rather
-- than a map placement. 0x0801713C is entered with r0 naming the 24-byte party
-- record, and the very next instruction reads that record's u16 +0x0E as the
-- sprite id. Logging the record and the id names exactly which party entry the
-- engine resolved, which is what turns "the player is the controlled actor" into
-- a measured statement instead of an assumption. It is also what a map with no
-- placement records at all leaves as the only actor.
local PARTY_SPRITE_ID_FIELD = 0x0E
local party_log = {}
local party_seen = {}
safe(emu.setBreakpoint, emu, function(_info)
    local record = tonumber(safe(emu.readRegister, emu, "r0"))
    if record == nil then return end
    local sprite_id = r16(record + PARTY_SPRITE_ID_FIELD)
    local key = string.format("%s:%s", hex(record), tostring(sprite_id))
    if party_seen[key] then return end
    party_seen[key] = true
    party_log[#party_log + 1] = string.format(
        "frame=%d party_record=%s party_sprite_id=%s is_new_identity=%s map_index=%s",
        frame, hex(record), tostring(sprite_id),
        tostring(sprite_id == NEW_SPRITE_ID), tostring((map_index())))
    console:log("SPRITENEW001 party resolve frame=" .. tostring(frame) ..
        " record=" .. hex(record) .. " sprite=" .. tostring(sprite_id))
    if sprite_id == NEW_SPRITE_ID then
        local found = io.open(OUT_ROOT .. "/FOUND.txt", "w")
        if found then
            found:write(string.format(
                "frame=%d\nnew_sprite_id=%d\nparty_record=%s\nmap_index=%s\n" ..
                "resolved_by=party_path\n",
                frame, NEW_SPRITE_ID, hex(record), tostring((map_index()))))
            found:close()
        end
        shots[#shots + 1] = { frame = frame + 20, tag = "player-resolve" }
        shots[#shots + 1] = { frame = frame + 90, tag = "player-settled" }
    end
end, 0x0801713C)

-- --- reporting --------------------------------------------------------------

local function write_state(path, label)
    local file = assert(io.open(path, "w"), "cannot open " .. path)
    local index, entry = map_index()
    file:write("label=" .. label .. "\n")
    file:write("frame=" .. tostring(frame) .. "\n")
    file:write("game_code=" .. tostring(code) .. "\n")
    file:write("rom_size=" .. tostring(safe(emu.romSize, emu)) .. "\n")
    file:write(string.format("new_structure=%s\n", hex(STRUCTURE)))
    file:write(string.format("new_sprite_id=%d\n", NEW_SPRITE_ID))
    file:write(string.format("active_map_ptr=%s\n", hex(r32(ACTIVE_MAP_PTR))))
    file:write(string.format("map_index=%s\n", index and tostring(index) or "unknown"))
    file:write(string.format("map_entry=%s\n", hex(entry)))
    file:write(string.format("constructor_hits=%d\n", hits))
    file:write(string.format("actors_using_new_identity=%d\n", #matched))
    file:write(string.format("map_object_npcs=%d\n", #siblings))
    for n, s in ipairs(siblings) do
        local moving = {}
        for i = 0, SIBLING_WINDOW_WORDS - 1 do
            local d = travelled(s.words[i])
            if d and d ~= 0 then
                moving[#moving + 1] = string.format(
                    "+0x%02X:%s->%s(d=%s)", SIBLING_WINDOW_START + 4 * i,
                    hex(s.words[i].min), hex(s.words[i].max), tostring(d))
            end
        end
        file:write(string.format(
            "npc_%d actor=%s record=%s samples=%d record_words=%s\n",
            n, hex(s.actor), hex(s.record), s.samples,
            table.concat({ s.record_words[0] and hex(s.record_words[0]) or "",
                           s.record_words[1] and hex(s.record_words[1]) or "",
                           s.record_words[2] and hex(s.record_words[2]) or "",
                           s.record_words[3] and hex(s.record_words[3]) or "",
                           s.record_words[4] and hex(s.record_words[4]) or "",
                           s.record_words[5] and hex(s.record_words[5]) or "",
                           s.record_words[6] and hex(s.record_words[6]) or "",
                           s.record_words[7] and hex(s.record_words[7]) or "" }, " ")))
        file:write(string.format("  changed_words=%s\n",
            #moving == 0 and "NONE" or table.concat(moving, " ")))
    end
    for n, actor in ipairs(matched) do
        file:write(string.format(
            "actor_%d=%s structure=%s animation=%s frame=%s cached_frame=%s " ..
            "frame_bytes=%s framebuf=%s screen_x=%s screen_y=%s\n",
            n, hex(actor),
            hex(r32(actor + ACTOR_STRUCTURE_FIELD)),
            hex(r32(actor + ACTOR_ANIMATION_FIELD)),
            hex(r32(actor + ACTOR_FRAME_FIELD)),
            hex(r32(actor + ACTOR_FRAME_CACHE_FIELD)),
            tostring(r32(actor + ACTOR_FRAME_SIZE_FIELD)),
            hex(r32(actor + ACTOR_FRAMEBUF_FIELD)),
            tostring(r32(actor + ACTOR_SCREEN_X_FIELD)),
            tostring(r32(actor + ACTOR_SCREEN_Y_FIELD))))
    end
    file:close()
    console:log("SPRITENEW001 state " .. path .. " frame=" .. tostring(frame) ..
        " map=" .. tostring(index) .. " hits=" .. tostring(hits) ..
        " new_identity_actors=" .. tostring(#matched))
end

local schedule = SCHEDULES[SCRIPT] or {}
local scheduled = {}
for _, item in ipairs(schedule) do
    scheduled[item[1]] = item[2]
    scheduled[item[1] + HOLD] = 0
end

local callback_id
callback_id = callbacks:add("frame", function()
    frame = frame + 1
    if scheduled[frame] ~= nil then emu:setKeys(scheduled[frame]) end

    note_map((map_index()))
    sample_siblings()

    for i = #shots, 1, -1 do
        if shots[i].frame <= frame then
            emu:screenshot(string.format("%s/evt-%04d-%s.png", OUT_ROOT, frame,
                shots[i].tag))
            table.remove(shots, i)
        end
    end

    -- A screenshot every ten seconds and a state report every five, so a long
    -- human session stays a sequence without filling the disk.
    if frame % 600 == 0 then
        emu:screenshot(string.format("%s/shot-%05d.png", OUT_ROOT, frame))
    end
    if frame % 300 == 0 then
        write_state(string.format("%s/state-%06d.txt", OUT_ROOT, frame), SCRIPT)
    end
    if frame >= TICKS then
        write_state(OUT_ROOT .. "/state-final.txt", SCRIPT)
        local summary = assert(io.open(OUT_ROOT .. "/hits.txt", "w"))
        summary:write(string.format("constructor_hits=%d\n", hits))
        summary:write(string.format("actors_using_new_identity=%d\n", #matched))
        summary:write(string.format("final_map_index=%s\n",
            tostring((map_index()))))
        summary:write("maps_seen=" .. table.concat(maps_seen, ",") .. "\n")
        summary:write(string.format("party_resolutions=%d\n", #party_log))
        for _, line in ipairs(party_log) do summary:write(line .. "\n") end
        for _, entry in ipairs(pending_maps) do
            summary:write(string.format("map_first_seen map=%d frame=%d\n",
                entry.index, entry.frame))
        end
        for _, line in ipairs(hit_log) do summary:write(line .. "\n") end
        summary:close()
        local marker = assert(io.open(OUT_ROOT .. "/done.txt", "w"))
        marker:write("done\n")
        marker:close()
        callbacks:remove(callback_id)
    end
end)

local marker = assert(io.open(OUT_ROOT .. "/armed.txt", "w"))
marker:write("armed\n")
marker:close()
console:log("SPRITENEW001 observer armed: script=" .. SCRIPT ..
    " structure=" .. hex(STRUCTURE) .. " sprite=" .. tostring(NEW_SPRITE_ID) ..
    " ticks=" .. tostring(TICKS) .. " out=" .. OUT_ROOT)
