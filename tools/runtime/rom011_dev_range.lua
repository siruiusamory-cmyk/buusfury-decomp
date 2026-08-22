local cfg = assert(rom011_dev, "rom011_dev configuration is required")

local function write_new(path, text)
    local existing = io.open(path, "rb")
    if existing then
        existing:close()
        return false
    end
    local output = assert(io.open(path, "wb"))
    output:write(text)
    output:close()
    return true
end

local function read_all(path)
    local input = io.open(path, "rb")
    if not input then
        return nil
    end
    local text = input:read("*a")
    input:close()
    return text
end

local function json_number(value)
    if value == nil then
        return "null"
    end
    return string.format("%d", value)
end

rom009_ready_path = cfg.lua_ready_path
dofile(cfg.setup_script)

local target = nil
local range_id = nil
local arm_sequence = 1
local benchmark_frames = nil
local benchmark_finished = false
local first_hit_written = false

local function in_evidence_range(address)
    local offset = address - target
    return (offset >= 0x04 and offset <= 0x0F)
        or (offset >= 0x14 and offset <= 0x17)
end

local function capture_read(info)
    if first_hit_written or not in_evidence_range(info.address) then
        return
    end
    first_hit_written = true
    local fields = {
        '"address":' .. json_number(info.address),
        '"width":' .. json_number(info.width),
        '"access_type":' .. json_number(info.accessType),
        '"old_value":' .. json_number(info.oldValue),
        '"pc":' .. json_number(emu:readRegister("pc")),
        '"lr":' .. json_number(emu:readRegister("lr")),
        '"cpsr":' .. json_number(emu:readRegister("cpsr")),
    }
    for register = 0, 12 do
        fields[#fields + 1] = string.format(
            '"r%d":%s', register, json_number(emu:readRegister("r" .. register))
        )
    end
    fields[#fields + 1] = '"sp":' .. json_number(emu:readRegister("sp"))
    write_new(cfg.hit_path, "{" .. table.concat(fields, ",") .. "}\n")
    if not benchmark_finished then
        write_new(cfg.benchmark_path, "HIT")
    end
end

local controller_id
controller_id = callbacks:add("frame", function()
    local command_path = string.format("%s%d.txt", cfg.arm_command_prefix, arm_sequence)
    local command = read_all(command_path)
    if command then
            local next_target = assert(tonumber(command, 16), "invalid ROM-011 target command")
            if range_id ~= nil then
                assert(emu:clearBreakpoint(range_id), "old range watchpoint removal failed")
            end
            target = next_target
            assert(target % 4 == 0, "unaligned ROM-011 target")
            assert(target >= 0x02000000 and target + 0x18 <= 0x02040000,
                "ROM-011 target outside EWRAM")
            if arm_sequence == 1 then
                assert(type(rom011_cancel_clean_route) == "function",
                    "clean route cancellation closure missing")
                rom011_cancel_clean_route()
            end
            range_id = emu:setRangeWatchpoint(
                capture_read,
                target + 0x04,
                target + 0x18,
                C.WATCHPOINT_TYPE.READ
            )
            assert(range_id >= 0, "range watchpoint installation failed")
            if arm_sequence == 1 then
                write_new(cfg.setup_stopped_path, "ready")
                benchmark_frames = 0
            end
            write_new(
                string.format("%s%d.txt", cfg.range_ready_prefix, arm_sequence),
                string.format("%d", range_id)
            )
            arm_sequence = arm_sequence + 1
    end

    if benchmark_frames ~= nil and not benchmark_finished then
        benchmark_frames = benchmark_frames + 1
        if benchmark_frames == 180 then
            benchmark_finished = true
            write_new(cfg.benchmark_path, "180")
        end
    end
end)

assert(controller_id ~= nil, "ROM-011 controller callback registration failed")
