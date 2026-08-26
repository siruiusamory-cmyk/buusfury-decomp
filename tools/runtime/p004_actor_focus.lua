-- P-004 dynamic actor-focus capture: full-object temporal dumps of
-- dynamically captured HURT-path actor pointers + punch edge labels.
-- Actor pointers arrive via p004-actor-focus-ptr.txt (written by the
-- GDB side at each flinch-wrapper stop). No hard-coded wolf identity.
local done_path = rom011_marker_path
assert(done_path and #done_path > 0, "marker path not provided")
local exp_dir = done_path:gsub("[^/\\]+$", "")
local log_path = exp_dir .. "p004-actor-focus.csv"
local ptr_path = exp_dir .. "p004-actor-focus-ptr.txt"
local HORIZON = 108000
local COALESCE = 25
local OBJ_WORDS = 128          -- 0x200 bytes per object dump
local FULL_EVERY = 60

local SLOT_ADDR = 0x0203D504   -- correlation only (reused-slot watch)
local ACTORSLOT = 0x03003488   -- engine actor-slot word (correlation)

local function finish(status)
    local d = io.open(done_path, "w")
    if d then d:write(status) d:close() end
end

local function run()
    local function wline(s)
        local lg = assert(io.open(log_path, "a"))
        lg:write(s .. "\n")
        lg:close()
    end

    assert(emu ~= nil and emu:getGameCode() == "AGB-BG3E")

    local armed = assert(io.open(exp_dir .. "armed-marker.txt", "w"))
    armed:write("armed")
    armed:close()

    local tracked = {}   -- array of object addresses
    local seen = {}      -- set of tracked addresses
    local refs = {}      -- addr -> rolling word image
    local lastptr = ""
    local t, pid, preva, lastedge = 0, 0, 0, -1000

    local function on_frame()
        -- full per-frame body (see bottom for error-trapped dispatch)
        local function body()
        t = t + 1
        local stopf = io.open(exp_dir .. "STOP-NOW.txt", "r")
        if stopf then
            stopf:close()
            finish("done:ActorFocus")
            return
        end
        if t > HORIZON then finish("done:ActorFocus") return end

        local pf = io.open(ptr_path, "r")
        if pf then
            local content = pf:read("*a")
            pf:close()
            if content ~= lastptr and #content > 0 then
                lastptr = content
                for addr in content:gmatch("(%x+)") do
                    local n = tonumber(addr, 16)
                    if n and n >= 0x02000000 and n < 0x02040000
                        and not seen[n] and #tracked < 4 then
                        seen[n] = true
                        tracked[#tracked + 1] = n
                        refs[n] = nil
                        wline(string.format("TRACK,%d,%x,%d",
                            t, n, os.time()))
                    end
                end
            end
        end

        local k = emu:read16(0x03003304)
        if (k & 1) == 1 and (preva & 1) == 0 and (t - lastedge) > COALESCE then
            pid = pid + 1
            lastedge = t
            local ptr = emu:read32(0x03001C34)
            local px, py = 0, 0
            if ptr ~= 0 then
                px = emu:read32(ptr + 0x1A0)
                py = emu:read32(ptr + 0x1A4)
            end
            wline(string.format("PUNCH,%d,%d,%d,px%x,py%x",
                pid, t, os.time(), px, py))
        end
        preva = k

        local parts = {
            string.format("T,%d,k%x,as%x,s0%x,s74%x",
                t, k, emu:read32(ACTORSLOT),
                emu:read32(SLOT_ADDR), emu:read32(SLOT_ADDR + 0x74)),
        }
        for _, base in ipairs(tracked) do
            local ref = refs[base]
            if ref == nil then
                ref = {}
                local hex = {}
                for i = 0, OBJ_WORDS - 1 do
                    ref[i] = emu:read32(base + i * 4)
                    hex[i + 1] = string.format("%08x", ref[i])
                end
                refs[base] = ref
                wline(string.format("SEED,%d,%x,%s", t, base,
                    table.concat(hex)))
            else
                local ch = {}
                for i = 0, OBJ_WORDS - 1 do
                    local v = emu:read32(base + i * 4)
                    if ref[i] ~= v then
                        ch[#ch + 1] =
                            string.format("%x:%x>%x", base + i * 4, ref[i], v)
                        ref[i] = v
                    end
                end
                if #ch > 0 then
                    wline(string.format("OBJ,%d,%x,%s", t, base,
                        table.concat(ch, ",")))
                end
                if t % FULL_EVERY == 0 then
                    local hex = {}
                    for i = 0, OBJ_WORDS - 1 do
                        hex[i + 1] =
                            string.format("%08x", emu:read32(base + i * 4))
                    end
                    wline(string.format("FULL,%d,%x,%s", t, base,
                        table.concat(hex)))
                end
            end
        end
        wline(table.concat(parts, ","))
        end
        local ok2, err2 = xpcall(body, function(e)
            return tostring(e) .. "\n" .. debug.traceback(e, 2)
        end)
        if not ok2 then finish("error:frame:" .. err2) end
    end
    callbacks:add("frame", on_frame)
end

local ok, err = xpcall(run, function(e) return tostring(e) end)
if not ok then finish("error:" .. tostring(err)) end
