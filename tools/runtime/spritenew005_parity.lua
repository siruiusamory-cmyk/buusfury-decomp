--[[ SPRITE-NEW-RUNTIME-PARITY-001 read-only observer.

Purpose: prove one production-planner-built sprite identity at runtime, and prove
that the facing it draws matches the direction it actually moves in.

Reuses the launcher's environment contract:
  SPRITENEW001_OUT_ROOT   where the logs and screenshots are written
  SPRITENEW001_STRUCTURE  the authored character structure's ROM address
  SPRITENEW001_SPRITE_ID  the authored sprite id
  SPRITENEW001_SCRIPT     key schedule name (menu, boot or human)
  SPRITENEW001_TICKS      frames to observe before finishing
plus:
  SPRITENEW005_FRAMES     comma-separated authored frame-record ROM addresses.
                          The actor whose +0x54 is one of them IS the authored one,
                          which identifies it without guessing an actor offset.

The only emulated-state change is emu:setKeys on the schedule. Nothing is written
to emulated memory; every read goes through pcall.

Logs
  resolutions.txt  frame record sprite structure is_new map
                   0x08017DB0, the map object factory's resolution site.
  walk.txt         frame actor result step_x step_y frame_record our_actor
                   0x0800A3B0, after the walk action returns. step_x/step_y are the
                   translated rect minus the actor's own rect, which IS the step the
                   engine just tested: (0,+y) down, (0,-y) up, (-x,0) left,
                   (+x,0) right. frame_record is actor+0x54 on the same frame.
  actors.txt       frame actor pos_x pos_y frame_record direction our_actor
                   sampled every SAMPLE_STRIDE frames for every actor that has
                   reached the walk action. pos_x/pos_y are actor+0x1A0/+0x1A4,
                   8.8 fixed point world pixels.
  retail.txt       frame actor result our_actor
                   every walk result, so the retail movers can be compared.
  state-final.txt  summary counts.
  shot-%05d.png    every SCREENSHOT_STRIDE frames.
--]]

local OUT_ROOT = os.getenv("SPRITENEW001_OUT_ROOT") or "spritenew005/out"
local STRUCTURE = tonumber(os.getenv("SPRITENEW001_STRUCTURE") or "0x08801C68")
local NEW_SPRITE_ID = tonumber(os.getenv("SPRITENEW001_SPRITE_ID") or "307")
local SCRIPT = os.getenv("SPRITENEW001_SCRIPT") or "menu"
local TICKS = tonumber(os.getenv("SPRITENEW001_TICKS") or "2400")

local RESOLUTION_SITE = 0x08017DB0
local DISPATCH_SITE = 0x0800A9A4
local WALK_RESULT = 0x0800A3B0

local ACTIVE_MAP_PTR = 0x03001980
local MAP_ENTRY_BASE = 0x0808E2E0
local MAP_ENTRY_SIZE = 0x38
local MAP_ENTRY_COUNT = 452

local ACTOR_POS_X = 0x1A0
local ACTOR_POS_Y = 0x1A4
local ACTOR_FRAME_FIELD = 0x54
local BLOCK_FIELD = 0x1B0

local SAMPLE_STRIDE = 4
local SCREENSHOT_STRIDE = 300
local HOLD = 6

local AUTHORED_FRAMES = {}
do
    local raw = os.getenv("SPRITENEW005_FRAMES") or ""
    local count = 0
    for piece in string.gmatch(raw, "[^,]+") do
        local value = tonumber(piece)
        if value then AUTHORED_FRAMES[value] = true; count = count + 1 end
    end
    AUTHORED_FRAME_COUNT = count
end

local function hex(value)
    if value == nil then return "?" end
    return string.format("0x%08X", value)
end

local function safe(fn, ...)
    local ok, value = pcall(fn, ...)
    if ok then return value end
    return nil
end

local function r32(a) return tonumber(safe(emu.read32, emu, a)) end

local function reg(name)
    local value = safe(emu.readRegister, emu, name)
    if value == nil then return nil end
    local number = tonumber(value)
    if number == nil and type(value) == "string" then
        number = tonumber(value, 16)
    end
    return number
end

local function map_index()
    local entry = r32(ACTIVE_MAP_PTR)
    if entry == nil or entry < MAP_ENTRY_BASE then return nil end
    local offset = entry - MAP_ENTRY_BASE
    if offset % MAP_ENTRY_SIZE ~= 0 then return nil end
    local index = math.floor(offset / MAP_ENTRY_SIZE)
    if index < 0 or index >= MAP_ENTRY_COUNT then return nil end
    return index
end

-- The engine's own direction index, read off the frame record the actor selected:
-- the frame record pointer is one of the authored 24, and the authored set is
-- handed over in authored frame order so the slot is the index in that list.
local FRAME_SLOTS = {}
do
    local raw = os.getenv("SPRITENEW005_FRAMES") or ""
    local position = 0
    for piece in string.gmatch(raw, "[^,]+") do
        local value = tonumber(piece)
        if value then FRAME_SLOTS[value] = position; position = position + 1 end
    end
end

local frame = 0
local finished = false
local resolutions = 0
local new_resolutions = 0
local walk_calls = 0
local walk_accepts = 0
local our_walk_calls = 0
local our_walk_accepts = 0
local samples = 0
local actors = {}
local actor_order = {}
local maps_seen = {}
local current_map = nil

local function open_log(name, header)
    local file = io.open(OUT_ROOT .. "/" .. name, "w")
    if not file then return nil end
    for _, line in ipairs(header) do file:write(line .. "\n") end
    file:flush()
    return file
end

local error_file = open_log("error.txt",
    { "# any error raised inside a breakpoint callback, with the channel" })
local resolution_file = open_log("resolutions.txt", {
    "# 0x08017DB0: r0 = resolved structure, r4 = the record",
    "# frame record sprite structure is_new map",
})
local walk_file = open_log("walk.txt", {
    "# 0x0800A3B0: r0 = the walk action's result, r4 = behaviour object, r5 = actor",
    "# frame actor result step_x step_y frame_record our_actor",
})
local actor_file = open_log("actors.txt", {
    "# actor+0x1A0/+0x1A4 world position (8.8 fixed point), +0x54 the drawn frame",
    "# frame actor pos_x pos_y frame_record direction our_actor",
})
local retail_file = open_log("retail.txt", {
    "# every walk result, so the retail movers can be compared",
    "# frame actor result our_actor",
})

local function register_actor(actor)
    if not actor or actor == 0 then return end
    if actors[actor] then return end
    actors[actor] = true
    actor_order[#actor_order + 1] = actor
end

local function guarded(label, fn)
    return function(info)
        -- Breakpoints stay armed after the observation window ends, so every
        -- callback checks this flag before touching a log the finisher closed.
        if finished then return end
        local ok, err = pcall(fn, info)
        if not ok and error_file then
            error_file:write(label .. " frame " .. tostring(frame) .. ": "
                .. tostring(err) .. "\n")
            error_file:flush()
        end
    end
end

local function direction_of(frame_record)
    local slot = FRAME_SLOTS[frame_record]
    if slot == nil then return "-" end
    return tostring(slot % 4)
end

local function sample_all()
    local index = map_index()
    if index ~= nil then maps_seen[index] = true; current_map = index end
    samples = samples + 1
    for _, actor in ipairs(actor_order) do
        local x = r32(actor + ACTOR_POS_X)
        local y = r32(actor + ACTOR_POS_Y)
        local selected = r32(actor + ACTOR_FRAME_FIELD)
        local ours = selected ~= nil and AUTHORED_FRAMES[selected] == true
        actor_file:write(string.format("%d %s %s %s %s %s %d\n", frame, hex(actor),
            hex(x), hex(y), hex(selected), direction_of(selected), ours and 1 or 0))
    end
    if actor_file then actor_file:flush() end
end

safe(emu.setBreakpoint, emu, guarded("resolution", function()
    local structure = reg("r0")
    local record = reg("r4")
    local sprite = record and r32(record + 0x10) or nil
    resolutions = resolutions + 1
    if structure == STRUCTURE then new_resolutions = new_resolutions + 1 end
    if resolution_file then
        resolution_file:write(string.format("%d %s %s %s %d %s\n", frame,
            hex(record), sprite and tostring(sprite) or "-", hex(structure),
            structure == STRUCTURE and 1 or 0, tostring(map_index() or "-")))
        resolution_file:flush()
    end
end), RESOLUTION_SITE)

safe(emu.setBreakpoint, emu, guarded("dispatch", function()
    local block = reg("r4")
    if block and block > BLOCK_FIELD then register_actor(block - BLOCK_FIELD) end
end), DISPATCH_SITE)

safe(emu.setBreakpoint, emu, guarded("walk", function()
    local result = reg("r0")
    local object = reg("r4")
    local actor = reg("r5")
    register_actor(actor)
    local selected = actor and r32(actor + ACTOR_FRAME_FIELD) or nil
    local ours = selected ~= nil and AUTHORED_FRAMES[selected] == true
    local x1 = object and r32(object + 0x28) or nil
    local y1 = object and r32(object + 0x2C) or nil
    local x2 = object and r32(object + 0x38) or nil
    local y2 = object and r32(object + 0x3C) or nil
    walk_calls = walk_calls + 1
    if result == 1 then walk_accepts = walk_accepts + 1 end
    if ours then
        our_walk_calls = our_walk_calls + 1
        if result == 1 then our_walk_accepts = our_walk_accepts + 1 end
    end
    if walk_file then
        walk_file:write(string.format("%d %s %s %s %s %s %d\n", frame, hex(actor),
            tostring(result), tostring(x2 and x1 and (x2 - x1) or "-"),
            tostring(y2 and y1 and (y2 - y1) or "-"), hex(selected), ours and 1 or 0))
        walk_file:flush()
    end
    if retail_file then
        retail_file:write(string.format("%d %s %s %d\n", frame, hex(actor),
            tostring(result), ours and 1 or 0))
        retail_file:flush()
    end
end), WALK_RESULT)

local key_names = { START = 8, A = 1 }
local plan = {
    menu = { { 180, "START" }, { 420, "A" }, { 560, "A" }, { 700, "A" }, { 840, "A" } },
    boot = { { 180, "START" } },
    human = {},
}
local scheduled = {}
for _, item in ipairs(plan[SCRIPT] or {}) do
    scheduled[item[1]] = key_names[item[2]]
    scheduled[item[1] + HOLD] = 0
end

local callback_id
callback_id = callbacks:add("frame", function()
    frame = frame + 1
    if scheduled[frame] ~= nil then emu:setKeys(scheduled[frame]) end
    if frame % SAMPLE_STRIDE == 0 then sample_all() end
    if frame % SCREENSHOT_STRIDE == 0 then
        emu:screenshot(string.format("%s/shot-%05d.png", OUT_ROOT, frame))
    end
    if frame >= TICKS then
        finished = true
        local summary = open_log("state-final.txt", {})
        if summary then
            summary:write("frame=" .. tostring(frame) .. "\n")
            summary:write("new_structure=" .. hex(STRUCTURE) .. "\n")
            summary:write("new_sprite_id=" .. tostring(NEW_SPRITE_ID) .. "\n")
            summary:write("map_index=" .. tostring(current_map or "-") .. "\n")
            summary:write("resolutions=" .. tostring(resolutions) .. "\n")
            summary:write("new_resolutions=" .. tostring(new_resolutions) .. "\n")
            summary:write("actors_tracked=" .. tostring(#actor_order) .. "\n")
            for _, actor in ipairs(actor_order) do
                summary:write("actor=" .. hex(actor) .. "\n")
            end
            summary:write("samples=" .. tostring(samples) .. "\n")
            summary:write("walk_calls=" .. tostring(walk_calls) .. "\n")
            summary:write("walk_accepts=" .. tostring(walk_accepts) .. "\n")
            summary:write("our_walk_calls=" .. tostring(our_walk_calls) .. "\n")
            summary:write("our_walk_accepts=" .. tostring(our_walk_accepts) .. "\n")
            for map, _ in pairs(maps_seen) do
                summary:write("map_seen=" .. tostring(map) .. "\n")
            end
            summary:write("authored_frames=" .. tostring(AUTHORED_FRAME_COUNT) .. "\n")
            summary:flush()
        end
        for _, file in ipairs({ actor_file, walk_file, resolution_file, retail_file }) do
            if file then file:close() end
        end
        local done = io.open(OUT_ROOT .. "/done.txt", "w")
        if done then done:write("done\n"); done:close() end
        callbacks:remove(callback_id)
    end
end)

local armed = io.open(OUT_ROOT .. "/armed.txt", "w")
if armed then armed:write("armed\n"); armed:close() end
console:log("spritenew005 parity observer armed; structure " .. hex(STRUCTURE)
    .. " sprite " .. tostring(NEW_SPRITE_ID) .. " authored frames "
    .. tostring(AUTHORED_FRAME_COUNT) .. " schedule " .. SCRIPT)
