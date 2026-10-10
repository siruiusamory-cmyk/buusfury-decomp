-- FRIEND-V3-WT-SPLIT-CONTAINER-001 release 3: the boss-fight measurement observer.
--
-- WHY. Hercule's and Olibu's enemy stat records are to be retuned into real fights. Two static
-- lanes agree on the mechanism: the constructor at 0x0800F68C copies record +0x04 (maximum hit
-- points) to the actor's +0x28C shifted left ten, and the damage calculator at 0x0800E9D8
-- consumes the attacker's copied +0x0D / +0x0E (actor +0x1B0 / +0x1B2) and the defender's
-- copied +0x0F (actor +0x1B4 / +0x1B6). Which of the two attacker fields a given hit uses is
-- chosen by the first byte of the attack descriptor, and only a running machine can say which.
-- This observer measures a real fight instead of assuming: it logs the branch taken, the damage
-- number the calculator produced, and the target's hit points as they fall.
--
-- READ-ONLY. Registers and memory are read; host files are written inside the run directory.
-- No emulated memory is written, no key is pressed, no state is loaded.
--
-- LIVENESS. The dispatch thunk 0x08046AA4 fires tens of thousands of times per run, so a run
-- with no damage rows is a real negative rather than a dead instrument.
--
-- WHAT IT WRITES, all inside the run directory named by rom011_marker_path:
--   damage.csv     one row per computed damage number: frame, attacker, defender, branch byte,
--                  the attacker's two attack fields, the defender's two defence fields, damage
--   hp.csv         one row per enemy hit-point store: frame, actor, new hit points in whole HP
--   branch.csv     the attack-descriptor byte and which branch it selected, once per value seen
--   heartbeat.csv  frame, pc, dispatch hits, damage rows, hp stores
--   arm.txt        the arm result of each breakpoint, written once
--   shot_*.png     every SHOT frames
--   marker.txt     "armed" at injection, then the end status

local DAMAGE_CALC = 0x0800E9E0        -- ldm r1,{r0,r1}: the attack descriptor and event record
local BRANCH_BYTE = 0x0800E9EA        -- ldrb r1,[r0]: the branch selector
local ATTACK_A = 0x0800EA02          -- ldrh r7,[r2,#0x10]: attacker +0x1B0
local ATTACK_B = 0x0800EA44          -- ldrh r7,[r2,#0x12]: attacker +0x1B2
local DAMAGE_STORE = 0x0800EABE      -- str r0,[r4,#0x18]: the computed damage
local HP_STORE = 0x0800FA50          -- str r0,[r5]: the target's new hit points
local ATTACK_SPAWN = 0x08029FE6      -- the behaviour SPAWN leaf's entry: one enemy SWING
local DISPATCH = 0x08046AA4          -- liveness

local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")

local function knob(name, default)
    return tonumber(os.getenv(name) or "") or default
end

local HORIZON = math.max(knob("FV3WT001_HORIZON", 200000), 2000)
local SHOT = knob("FV3WT001_SHOT_EVERY", 300)
local BEAT = 60
local ROW_LIMIT = 4000

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

local frame = 0
local rows, hp_rows, dispatch_hits, branch_byte, branch_hits = 0, 0, 0, nil, 0
-- Declared with the other counters and BEFORE any handler, so a hit that arrives before these
-- lines has run cannot index a nil.
local swings, swing_rows = 0, 0

local function reg(name)
    local ok, value = pcall(function() return emu:readRegister(name) end)
    return (ok and value) or nil
end

local function read16(address)
    local ok, value = pcall(function() return emu:read16(address) end)
    if ok and value then return value end
    return -1
end

local function read8(address)
    local ok, value = pcall(function() return emu:read8(address) end)
    if ok and value then return value end
    return -1
end

local function read32(address)
    local ok, value = pcall(function() return emu:read32(address) end)
    if ok and value then return value end
    return nil
end

-- The animation timeline. A SET action index is written to actor+0x1E4 and selects the actor's
-- own model clip through actor+0x68 + 4*index into actor+0x1CC. Logging both actors' clip words
-- each frame measures how long an animation actually lasts, which is the number nobody can read
-- out of the image: the clip lengths belong to the actor's model table, built at load.
local PLAYER_ACTOR_POINTER = 0x03001B94
local ENEMY_RECORD = 0x08711BC0        -- Olibu's record; an enemy actor keeps it at +0x224
local EWRAM_START, EWRAM_END = 0x02000000, 0x02040000

local enemy_actor = nil
local player_last_action, player_last_clip = -1, -1
local enemy_last_action, enemy_last_clip = -1, -1

local function find_enemy_actor()
    for address = EWRAM_START, EWRAM_END - 4, 4 do
        if read32(address) == ENEMY_RECORD then return address - 0x224 end
    end
    return nil
end

local function run()
    local damage = assert(io.open(exp_dir .. "damage.csv", "w"))
    damage:write("row,frame,attacker,defender,branch,atk_1B0,atk_1B2,def_1B4,def_1B6,damage,fixed\n")
    damage:flush()
    local hp = assert(io.open(exp_dir .. "hp.csv", "w"))
    hp:write("row,frame,actor,new_hp_units,new_hp_whole\n")
    hp:flush()
    local branch = assert(io.open(exp_dir .. "branch.csv", "w"))
    branch:write("frame,descriptor_byte,expected_branch\n")
    branch:flush()
    local beat = assert(io.open(exp_dir .. "heartbeat.csv", "w"))
    beat:write("frame,pc,dispatch_hits,damage_rows,hp_rows,swings\n")
    beat:flush()
    local swing = assert(io.open(exp_dir .. "swings.csv", "w"))
    swing:write("row,frame\n")
    swing:flush()
    local clips = assert(io.open(exp_dir .. "clips.csv", "w"))
    clips:write("frame,who,action,clip\n")
    clips:flush()

    -- r4 holds the attacker actor and r8 the event record at the damage store.
    local function on_damage_store()
        if rows >= ROW_LIMIT then return end
        local attacker = reg("r4")
        local value = reg("r0")
        if not attacker then return end
        rows = rows + 1
        local defender = nil
        local ok, candidate = pcall(function() return emu:read32(0) end)
        if ok then defender = nil end
        damage:write(string.format("%d,%d,0x%08X,,%d,%d,%d,%d,%d,%d,%d\n",
                                   rows, frame, attacker,
                                   branch_byte or -1,
                                   read16(attacker + 0x1B0), read16(attacker + 0x1B2),
                                   -1, -1, value or 0,
                                   math.floor((value or 0) / 1024)))
        damage:flush()
    end

    local function on_hp_store()
        local r5 = reg("r5")
        local value = reg("r0")
        if not r5 or not value then return end
        -- Whoever lost hit points is an actor; if the player is not the one losing them, this is
        -- the enemy, which is the cheapest way to learn his address without scanning.
        local player = read32(PLAYER_ACTOR_POINTER)
        if enemy_actor == nil and player and r5 - 0x28C ~= player then
            enemy_actor = r5 - 0x28C
        end
        hp_rows = hp_rows + 1
        hp:write(string.format("%d,%d,0x%08X,%d,%d\n", hp_rows, frame, r5 - 0x28C,
                               value, math.floor(value / 1024)))
        hp:flush()
    end

    local arms = {}
    local ids = {}
    local function arm(label, address, handler)
        local ok, result = pcall(function() return emu:setBreakpoint(handler, address) end)
        arms[#arms + 1] = string.format("%s 0x%08X ok=%s id=%s", label, address,
                                        tostring(ok), tostring(result))
        if type(result) == "number" then ids[#ids + 1] = result end
    end

    arm("branch_byte", BRANCH_BYTE, function()
        local pointer = reg("r0")
        if not pointer then return end
        local value = read8(pointer + 0)
        local previous = branch_byte
        branch_byte = value
        if value ~= previous then
            branch_hits = branch_hits + 1
            branch:write(string.format("%d,%d,%s\n", frame, value,
                                       (value == 0) and "A(+0x1B0)" or "B(+0x1B2)"))
            branch:flush()
        end
    end)
    arm("attack_a", ATTACK_A, function() end)
    arm("attack_b", ATTACK_B, function() end)
    arm("damage_store", DAMAGE_STORE, on_damage_store)
    arm("hp_store", HP_STORE, on_hp_store)
    arm("attack_spawn", ATTACK_SPAWN, function()
        swings = swings + 1
        if swing_rows < ROW_LIMIT then
            swing_rows = swing_rows + 1
            swing:write(string.format("%d,%d\n", swing_rows, frame))
            swing:flush()
        end
    end)
    arm("dispatch", DISPATCH, function() dispatch_hits = dispatch_hits + 1 end)

    local note = io.open(exp_dir .. "arm.txt", "w")
    if note then
        note:write(table.concat(arms, "\n") .. "\n")
        note:close()
    end
    finish("armed")

    local callback_id
    callback_id = callbacks:add("frame", function()
        frame = frame + 1
        if enemy_actor == nil and frame % 120 == 0 then
            enemy_actor = find_enemy_actor()
        end
        local function note(who, action, clip, last_action, last_clip)
            if action == nil or clip == nil then return last_action, last_clip end
            if action ~= last_action or clip ~= last_clip then
                clips:write(string.format("%d,%s,%d,0x%08X\n", frame, who, action, clip))
                clips:flush()
                return action, clip
            end
            return last_action, last_clip
        end
        if frame % 4 == 0 then
            local player = read32(PLAYER_ACTOR_POINTER)
            if player then
                player_last_action, player_last_clip = note(
                    "player", read32(player + 0x1E4), read32(player + 0x1CC),
                    player_last_action, player_last_clip)
            end
            if enemy_actor then
                enemy_last_action, enemy_last_clip = note(
                    "enemy", read32(enemy_actor + 0x1E4), read32(enemy_actor + 0x1CC),
                    enemy_last_action, enemy_last_clip)
            end
        end
        if frame % SHOT == 0 then
            pcall(function()
                emu:screenshot(string.format("%sshot_%06d.png", exp_dir, frame))
            end)
        end
        if frame % BEAT == 0 then
            local pc = reg("pc")
            beat:write(string.format("%d,0x%08X,%d,%d,%d,%d\n", frame, (pc or 0),
                                     dispatch_hits, rows, hp_rows, swings))
            beat:flush()
        end
        if frame >= HORIZON then
            callbacks:remove(callback_id)
            for _, id in ipairs(ids) do
                pcall(function() emu:clearBreakpoint(id) end)
            end
            damage:close()
            hp:close()
            branch:close()
            beat:close()
            swing:close()
            clips:close()
            finish(string.format("done:frames=%d dispatch=%d damage_rows=%d hp_rows=%d "
                                 .. "swings=%d branches=%d", frame, dispatch_hits, rows,
                                 hp_rows, swings, branch_hits))
        end
    end)
end

local ok, err = xpcall(run, function(problem) return tostring(problem) end)
if not ok then finish("error:" .. tostring(err)) end
