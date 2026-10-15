-- PROBE-RUNTIME-001 read-map observer. READ-ONLY.
--
-- Question it answers, one line per span: is this retail byte span ever read at
-- runtime, by which PC, and how often? Its output is evidence; it credits no
-- bytes itself.
--
-- WHAT IT ARMS
--   * one read watchpoint per span of the PROBE-RUNTIME-001 candidate list, as a
--     partition so no two watches overlap (the contract's fourth range is carved
--     around the positive control, around A5 and around A6);
--   * POSITIVE CONTROL: 0x0870F514..0x08710EF4, the AI behaviour row table,
--     which the static recon proves is read (row = 0x0870F514 + 8*selector at
--     0x0800AAA6). It must fire, or the run is VOID;
--   * NEGATIVE CONTROL: 16 bytes just above the last requested range, which no
--     recon span names. A hit there is a finding, not a failed control;
--   * the B4 IWRAM pointer 0x03001B60..0x03001B64, which has no static reader;
--   * the ADDENDUM 7 B-list breakpoints, with a per-site row cap;
--   * three liveness channels: a frame heartbeat, the script interpreter
--     0x08004038, and the animation selector 0x0800ECDA;
--   * a once-a-frame sample of the four DMA channels' control words, so the size
--     of the CPU-watch blind spot (DMA reads are invisible to a CPU watch) is
--     measured rather than asserted.
--
-- AGGREGATION
--   every hit is folded into its 4-byte granule with a hit count, the first PC
--   seen and the first frame seen. Distinct granules are capped so a long run
--   cannot exhaust memory; past the cap the span's overflow counter grows and
--   says so in the output. The per-event trace is bounded too.
--
-- HONEST LIMITS
--   * The access WIDTH is not exposed by the watchpoint callback on this build,
--     so the width column carries NA. The address series answers stride; width
--     stays unmeasured until an instruction-decoding instrument is added.
--   * The PC is sampled inside the callback, so it can be the instruction after
--     the access. The first PC per granule is what is recorded.
--   * CPU watchpoints do not see DMA or coprocessor reads of the ROM. The DMA
--     sampler measures whether the engine transfers FROM the ROM at all; where
--     it does, those reads are invisible here. A span unread under this watch is
--     therefore "not read by the CPU", never "dead".
--   * A silent watch with every liveness channel silent is UNPROVEN, not a
--     negative. The summary states which case the run is in.
--
-- READ-ONLY PROOF
--   The only emulator calls are emu:read8/16/32, emu:readRegister,
--   emu:setBreakpoint, emu:setWatchpoint, emu:setRangeWatchpoint,
--   emu:clearBreakpoint, emu:getGameCode, emu:romSize and callbacks:add. No
--   emulated memory is modified and no input is driven.
--
-- OUTPUT, all under PROBE_RUNTIME_DIR (default C:/temp/probe-runtime):
--   probe-runtime001-api.txt        the API surface, arming results, abort reason
--   probe-runtime001-watch.csv      per-4-byte-granule hits, first PC, first frame
--   probe-runtime001-events.csv     bounded per-hit trace (address, PC, frame)
--   probe-runtime001-break.csv      B-list and liveness hits with registers
--   probe-runtime001-heartbeat.csv  frame heartbeat
--   probe-runtime001-dma.csv        ROM-sourced DMA sample
--   probe-runtime001-summary.txt    counters and the instrument verdict
--   READMAP.json                    the same numbers in one machine-readable file

local OUT_DIR = os.getenv("PROBE_RUNTIME_DIR") or "C:/temp/probe-runtime"
local FRAME_LIMIT = tonumber(os.getenv("PROBE_RUNTIME_FRAMES") or "") or 300000
local FLUSH_EVERY = 1800
local EVENT_CAP = 2000
local GRANULE_CAP = 65536
local ARM_BREAKPOINTS = (os.getenv("PROBE_RUNTIME_BREAKPOINTS") or "1") ~= "0"

assert(emu ~= nil, "mGBA did not attach the emulation core")
local game_code = emu:getGameCode()
assert(game_code == "BG3E" or game_code == "AGB-BG3E",
    "unexpected game code: " .. tostring(game_code))
assert(emu:romSize() == 8388608, "unexpected ROM size")

local function out_path(name) return OUT_DIR .. "/" .. name end

local function open_out(name)
    local f, err = io.open(out_path(name), "w")
    assert(f, "cannot open " .. tostring(out_path(name)) .. ": " .. tostring(err))
    return f
end

local function hex32(v)
    if v == nil then return "" end
    local ok, s = pcall(string.format, "0x%08X", math.floor(v))
    if ok then return s end
    return ""
end

local frames = 0
local finalized = false

-- ---------------------------------------------------------------------------
-- 1. API surface first, and abort closed if the watchpoint API is absent.
-- ---------------------------------------------------------------------------

local api = open_out("probe-runtime001-api.txt")
api:write("PROBE-RUNTIME-001 api surface\n")

local function has(name)
    local ok, v = pcall(function() return emu[name] end)
    return ok and v ~= nil
end

for _, name in ipairs({ "setBreakpoint", "clearBreakpoint", "setWatchpoint",
    "setRangeWatchpoint", "read8", "read16", "read32", "readRange",
    "readRegister", "getGameCode", "romSize", "currentFrame",
    "screenshot", "loadStateFile" }) do
    local ok, v = pcall(function() return emu[name] end)
    api:write(string.format("%s=%s\n", name, tostring(ok and (v ~= nil) or ("ERR " .. tostring(v)))))
end
api:flush()

local function abort_closed(why)
    api:write("VERDICT=ABORT: " .. why .. "\n")
    api:close()
    local s = open_out("probe-runtime001-summary.txt")
    s:write("ABORT CLOSED: " .. why .. "\n")
    s:write("Nothing further was armed. No span is classified and no run data exists.\n")
    s:write("See probe-runtime001-api.txt for the exact surface found.\n")
    s:close()
    error("PROBE-RUNTIME-001: " .. why)
end

if not (has("setWatchpoint") and has("setRangeWatchpoint")) then
    abort_closed("emu.setWatchpoint or emu.setRangeWatchpoint is absent from the Lua adapter")
end

-- The script adapter's own parameter order is the one to try first: the pinned
-- 0.11 binary carries "struct::mScriptCoreAdapter.setRangeWatchpoint.callback.
-- minAddress.maxAddress.type". The type argument's spelling is not documented in
-- the binary, so each candidate is tried once, logged, and cleared; the first
-- that returns an id is the shape this run uses. If none does, the run aborts.
local SHAPES = {
    { label = "cb_min_max_read_string", call = function(cb, a, b) return emu:setRangeWatchpoint(cb, a, b, "read") end },
    { label = "cb_min_max_type2", call = function(cb, a, b) return emu:setRangeWatchpoint(cb, a, b, 2) end },
    { label = "cb_min_max_type1", call = function(cb, a, b) return emu:setRangeWatchpoint(cb, a, b, 1) end },
    { label = "cb_min_max_type4", call = function(cb, a, b) return emu:setRangeWatchpoint(cb, a, b, 4) end },
    { label = "min_max_read_string_cb", call = function(cb, a, b) return emu:setRangeWatchpoint(a, b, "read", cb) end },
}

local shape = nil
for _, cand in ipairs(SHAPES) do
    local ok, id = pcall(cand.call, function() end, 0x0870F514, 0x0870F518)
    api:write(string.format("probe %-22s ok=%s id=%s\n", cand.label, tostring(ok), tostring(id)))
    if ok and id ~= nil then
        local okc, errc = pcall(function() return emu:clearBreakpoint(id) end)
        api:write(string.format("probe %-22s cleared=%s err=%s\n", cand.label, tostring(okc), tostring(errc)))
        if not shape then shape = cand end
    end
end
if not shape then
    abort_closed("no watchpoint arming shape succeeded; see the probe lines above")
end
api:write("SHAPE=" .. shape.label .. "\n")
api:flush()

-- ---------------------------------------------------------------------------
-- 2. Spans, arming, aggregation.
-- ---------------------------------------------------------------------------

local SPANS = {
    { id = "R1_A1_selfnaming", min = 0x08072CD4, max = 0x0808E2E0,
      why = "A1 first-MiB self-naming class; also covers the A2/A3 slices inside it" },
    { id = "R2_mapresidue", min = 0x08179A50, max = 0x082B8BC8,
      why = "contract range 2; contains A10 0x0822229C" },
    { id = "R3_tableregion", min = 0x082B8BC8, max = 0x083BE3D4,
      why = "contract range 3; contains A10 0x082B7E78" },
    { id = "R4a_head", min = 0x086A88AC, max = 0x086B8028,
      why = "contract range 4 head" },
    { id = "A5_desc8", min = 0x086B8028, max = 0x086B8168,
      why = "A5 descriptor8_records closing boundary, 0x6B8028 + 40*8" },
    { id = "R4b_mid", min = 0x086B8168, max = 0x0870F514,
      why = "contract range 4, below the positive control" },
    { id = "PC_airows", min = 0x0870F514, max = 0x08710EF4,
      why = "POSITIVE CONTROL: the AI behaviour row table, proven read at 0x0800AAA6" },
    { id = "R4c_mid", min = 0x08710EF4, max = 0x0874CA24,
      why = "contract range 4; contains A7 0x0873198C, 0x08732B20, 0x08733AF7" },
    { id = "A6_74CA24", min = 0x0874CA24, max = 0x0874CBEA,
      why = "A6 the 0x74CA24 block, 482 B" },
    { id = "R4d_tail", min = 0x0874CBEA, max = 0x087B79A4,
      why = "contract range 4 tail; contains A7 0x087B753C" },
    { id = "NC_tail16", min = 0x087B79A4, max = 0x087B79B4,
      why = "NEGATIVE CONTROL: 16 B above the last requested range, named by no recon span" },
    { id = "B4_iwram_ptr", min = 0x03001B60, max = 0x03001B64,
      why = "B4 the F-E3 +0x08 IWRAM pointer, which no static site reads" },
}

local granules = {}
local granule_count = 0
local events = {}
local event_count = 0

for _, span in ipairs(SPANS) do
    span.hits = 0
    span.distinct = 0
    span.overflow = 0
    span.shape_mismatch = 0
    span.shape_samples = 0
    span.events = 0
    span.first_pc = nil
    span.first_frame = nil
    span.armed = false
end

local function find_span(id)
    for _, span in ipairs(SPANS) do
        if span.id == id then return span end
    end
    return nil
end

local function record(span, addr, value)
    span.hits = span.hits + 1
    local g = math.floor(addr / 4) * 4
    local key = span.id .. ":" .. tostring(g)
    local e = granules[key]
    -- The PC read is the expensive part of a hit, so it happens only when a
    -- recorded value actually needs it: the span's first PC, a new granule, or a
    -- free event slot.
    local need_pc = (span.first_pc == nil) or (e == nil and granule_count < GRANULE_CAP)
        or (event_count < EVENT_CAP)
    local pc = 0
    if need_pc then
        local okr, reg = pcall(function() return emu:readRegister("pc") end)
        if okr and reg then pc = math.floor(tonumber(reg) or 0) end
    end
    if span.first_pc == nil then
        span.first_pc = pc
        span.first_frame = frames
    end
    if e then
        e.n = e.n + 1
    elseif granule_count < GRANULE_CAP then
        granule_count = granule_count + 1
        granules[key] = { span = span.id, addr = g, n = 1, pc = pc, frame = frames }
        span.distinct = span.distinct + 1
    else
        span.overflow = span.overflow + 1
    end
    if event_count < EVENT_CAP then
        event_count = event_count + 1
        events[event_count] = string.format("%s,%d,0x%08X,0x%08X,%s,NA",
            span.id, frames, addr, pc, value and hex32(value) or "")
    end
end

local function make_hit(span)
    return function(a, b, c)
        if span.shape_samples < 3 then
            span.shape_samples = span.shape_samples + 1
            api:write(string.format("shape %s args=%s,%s,%s\n", span.id,
                tostring(a), tostring(b), tostring(c)))
            api:flush()
        end
        local addr, value
        if type(a) == "number" and a >= span.min and a < span.max then
            addr, value = a, b
        elseif type(b) == "number" and b >= span.min and b < span.max then
            addr, value = b, a
        else
            span.shape_mismatch = span.shape_mismatch + 1
            return
        end
        record(span, addr, value)
    end
end

for _, span in ipairs(SPANS) do
    local ok, id = pcall(shape.call, make_hit(span), span.min, span.max)
    span.armed = ok and id ~= nil
    api:write(string.format("arm %-18s 0x%08X..0x%08X ok=%s id=%s\n",
        span.id, span.min, span.max, tostring(ok), tostring(id)))
    if not span.armed then
        api:write(string.format("arm %-18s FAILED err=%s\n", span.id, tostring(id)))
    end
end
api:flush()

if not find_span("PC_airows").armed then
    abort_closed("the positive control span could not be armed, so no negative could be interpreted")
end

-- ---------------------------------------------------------------------------
-- 3. Breakpoints: the ADDENDUM 7 B-list plus two liveness counters.
-- ---------------------------------------------------------------------------

local bp_rows = {}
local bp_hit_rows = 0
local liveness = { interp = 0, anim = 0, heartbeat = 0 }
local sites = {}

local function bp_row(site, kind)
    local pc, r0, r1, r2, r3, r13, r14 = 0, 0, 0, 0, 0, 0, 0
    pcall(function() pc = math.floor(tonumber(emu:readRegister("pc")) or 0) end)
    pcall(function() r0 = math.floor(tonumber(emu:readRegister("r0")) or 0) end)
    pcall(function() r1 = math.floor(tonumber(emu:readRegister("r1")) or 0) end)
    pcall(function() r2 = math.floor(tonumber(emu:readRegister("r2")) or 0) end)
    pcall(function() r3 = math.floor(tonumber(emu:readRegister("r3")) or 0) end)
    pcall(function() r13 = math.floor(tonumber(emu:readRegister("r13")) or 0) end)
    pcall(function() r14 = math.floor(tonumber(emu:readRegister("r14")) or 0) end)
    bp_rows[#bp_rows + 1] = string.format("%s,%s,%d,0x%08X,0x%08X,0x%08X,0x%08X,0x%08X,0x%08X,0x%08X",
        kind, site.label, frames, pc, r0, r1, r2, r3, r13, r14)
    bp_hit_rows = bp_hit_rows + 1
end

local function arm_site(addr, label, cap, kind)
    local site = { addr = addr, label = label, cap = cap, kind = kind, hits = 0 }
    sites[#sites + 1] = site
    local ok, id = pcall(function()
        return emu:setBreakpoint(function()
            site.hits = site.hits + 1
            if kind == "LV" then
                if site.hits == 1 or site.hits % 500 == 0 then
                    if site.logged == nil then site.logged = 0 end
                    if site.logged < 20 then
                        site.logged = site.logged + 1
                        bp_row(site, kind)
                    end
                end
            elseif site.hits <= cap then
                bp_row(site, kind)
            end
        end, addr)
    end)
    site.armed = ok and id ~= nil
    api:write(string.format("bp %-24s 0x%08X armed=%s id=%s\n", label, addr, tostring(site.armed), tostring(id)))
    api:flush()
    return site
end

-- Liveness FIRST, so a stall caused by the B-list still leaves liveness evidence.
arm_site(0x08004038, "liveness_script_interpreter", 20, "LV")
arm_site(0x0800ECDA, "liveness_animation_selector", 20, "LV")

if ARM_BREAKPOINTS then
    arm_site(0x080089CE, "B3_r32_index_read", 120, "B")
    arm_site(0x08008B30, "B3_me_walk", 120, "B")
    arm_site(0x08008A02, "B12_me_walk", 120, "B")
    arm_site(0x08013DDC, "B4_fe3_record_loop", 120, "B")
    arm_site(0x080141CC, "B5_desc8_bound", 120, "B")
    arm_site(0x08004A88, "B6_74ca24_base", 120, "B")
    arm_site(0x0800ECE4, "B11_def50_ptr_a", 120, "B")
    arm_site(0x0800ECEA, "B11_def50_ptr_b", 120, "B")
    arm_site(0x08011F56, "B_bank_index_read", 120, "B")
    arm_site(0x0803FBEC, "B7_string_reader_a", 60, "B")
    arm_site(0x080415A6, "B7_string_reader_b", 60, "B")
end
local armed_count = 0
for _, site in ipairs(sites) do
    if site.armed then armed_count = armed_count + 1 end
end
local armed_spans = 0
for _, span in ipairs(SPANS) do
    if span.armed then armed_spans = armed_spans + 1 end
end
api:write(string.format("ARMED breakpoints=%d/%d spans=%d/%d frames_callback=pending\n",
    armed_count, #sites, armed_spans, #SPANS))
api:flush()

local function lv_hits(label)
    for _, site in ipairs(sites) do
        if site.label == label then return site.hits end
    end
    return 0
end

-- ---------------------------------------------------------------------------
-- 4. DMA blind-spot sampler, aggregated by channel.
-- ---------------------------------------------------------------------------

local dma = {}
for c = 0, 3 do
    dma[c] = { rom_arms = 0, first_frame = nil, first_src = nil }
end
local dma_rows = 0

local function sample_dma()
    for c = 0, 3 do
        local base = 0x040000B0 + 12 * c
        local ok_s, src = pcall(function() return emu:read32(base) end)
        local ok_c, cnt = pcall(function() return emu:read16(base + 10) end)
        if ok_s and ok_c and src and cnt and cnt >= 0x8000
            and src >= 0x08000000 and src < 0x0A000000 then
            dma[c].rom_arms = dma[c].rom_arms + 1
            if dma[c].first_frame == nil then
                dma[c].first_frame = frames
                dma[c].first_src = src
                if dma_rows < 20 then
                    dma_rows = dma_rows + 1
                    api:write(string.format("dma ch%d frame=%d src=0x%08X cnt=0x%04X\n",
                        c, frames, src, cnt))
                    api:flush()
                end
            end
        end
    end
end

-- ---------------------------------------------------------------------------
-- 5. Frame callback, heartbeat, periodic flush.
-- ---------------------------------------------------------------------------

local heartbeat = open_out("probe-runtime001-heartbeat.csv")
heartbeat:write("frame,watch_hits,interp_hits,anim_hits,granules\n")
heartbeat:flush()

local function write_watch_csv()
    local f = open_out("probe-runtime001-watch.csv")
    f:write("span,file_offset,address,hits,first_pc,first_frame\n")
    local rows = {}
    for _, e in pairs(granules) do rows[#rows + 1] = e end
    table.sort(rows, function(x, y)
        if x.span ~= y.span then return x.span < y.span end
        return x.addr < y.addr
    end)
    for _, e in ipairs(rows) do
        f:write(string.format("%s,0x%06X,0x%08X,%d,0x%08X,%d\n",
            e.span, e.addr - 0x08000000, e.addr, e.n, e.pc, e.frame))
    end
    f:close()
end

local function write_events_csv()
    local f = open_out("probe-runtime001-events.csv")
    f:write("span,frame,address,pc,value,width\n")
    for i = 1, event_count do f:write(events[i] .. "\n") end
    f:close()
end

local function write_break_csv()
    local f = open_out("probe-runtime001-break.csv")
    f:write("kind,site,frame,pc,r0,r1,r2,r3,r13,r14\n")
    for i = 1, #bp_rows do f:write(bp_rows[i] .. "\n") end
    f:close()
end

local function control_hits(span)
    return span and span.hits or 0
end

local function overall_verdict()
    local pc = find_span("PC_airows")
    if control_hits(pc) > 0 then
        return "INSTRUMENT PROVEN: the positive control fired"
    end
    if lv_hits("liveness_script_interpreter") > 0 or lv_hits("liveness_animation_selector") > 0 then
        return "POSITIVE CONTROL SILENT while a liveness channel fired: either the control span was not read in this run, or the armed watchpoint type is not the read type (see the shape probe in the api file)"
    end
    return "UNPROVEN: the positive control and every liveness channel are silent; a silent watch here proves nothing"
end

local function write_summary()
    local s = open_out("probe-runtime001-summary.txt")
    s:write("PROBE-RUNTIME-001 summary, single run\n")
    s:write("frames=" .. tostring(frames) .. "\n")
    s:write("watchpoint shape=" .. shape.label .. "\n")
    s:write("granules tracked=" .. tostring(granule_count) .. " cap=" .. tostring(GRANULE_CAP) .. "\n")
    s:write("events logged=" .. tostring(event_count) .. " cap=" .. tostring(EVENT_CAP) .. "\n")
    s:write("liveness: interpreter=" .. tostring(lv_hits("liveness_script_interpreter"))
        .. " animation=" .. tostring(lv_hits("liveness_animation_selector"))
        .. " heartbeats=" .. tostring(liveness.heartbeat) .. "\n")
    for _, span in ipairs(SPANS) do
        s:write(string.format("%-18s hits=%-8d distinct=%-6d overflow=%-6d shape_mismatch=%-6d first_pc=%s first_frame=%s armed=%s\n",
            span.id, span.hits, span.distinct, span.overflow, span.shape_mismatch,
            hex32(span.first_pc), tostring(span.first_frame), tostring(span.armed)))
    end
    for _, site in ipairs(sites) do
        s:write(string.format("bp %-26s hits=%d armed=%s\n", site.label, site.hits, tostring(site.armed)))
    end
    for c = 0, 3 do
        s:write(string.format("dma ch%d rom_arms=%d first_frame=%s first_src=%s\n",
            c, dma[c].rom_arms, tostring(dma[c].first_frame), hex32(dma[c].first_src)))
    end
    s:write("VERDICT=" .. overall_verdict() .. "\n")
    s:write("Blind spot: DMA and coprocessor reads of the ROM are invisible to a CPU watch. "
        .. "Every span with 0 hits is NOT READ BY THE CPU, never 'dead'.\n")
    s:write("Width is not exposed by the watchpoint callback: the width column is NA, and the "
        .. "address series answers stride.\n")
    s:close()
end

local function write_readmap()
    local f = open_out("READMAP.json")
    local parts = {}
    parts[#parts + 1] = "{"
    parts[#parts + 1] = string.format('  "contract": "PROBE-RUNTIME-001", "frames": %d, "shape": "%s",\n', frames, shape.label)
    parts[#parts + 1] = string.format('  "liveness": {"script_interpreter": %d, "animation_selector": %d, "heartbeats": %d},\n',
        lv_hits("liveness_script_interpreter"), lv_hits("liveness_animation_selector"), liveness.heartbeat)
    parts[#parts + 1] = string.format('  "verdict": "%s",\n', overall_verdict())
    parts[#parts + 1] = '  "spans": [\n'
    for i, span in ipairs(SPANS) do
        local result
        if span.hits > 0 then
            result = "READ"
        elseif lv_hits("liveness_script_interpreter") == 0
            and lv_hits("liveness_animation_selector") == 0
            and control_hits(find_span("PC_airows")) == 0 then
            result = "VOID"
        else
            result = "NOT READ BY THE CPU"
        end
        parts[#parts + 1] = string.format(
            '    {"id": "%s", "min": "0x%08X", "max": "0x%08X", "result": "%s", "granules": %d, "hits": %d, "granule_overflow": %d, "first_pc": %s, "first_frame": %s, "why": "%s"}%s\n',
            span.id, span.min, span.max, result, span.distinct, span.hits, span.overflow,
            span.first_pc and hex32(span.first_pc) or "null",
            span.first_frame and tostring(span.first_frame) or "null",
            span.why, i < #SPANS and "," or "")
    end
    parts[#parts + 1] = '  ],\n'
    parts[#parts + 1] = '  "dma_rom_arms": [' .. string.format("%d, %d, %d, %d", dma[0].rom_arms, dma[1].rom_arms, dma[2].rom_arms, dma[3].rom_arms) .. '],\n'
    parts[#parts + 1] = string.format('  "note": "A span with 0 hits is NOT READ BY THE CPU. DMA and coprocessor reads are invisible to a CPU watch. Width is not exposed by this API."\n')
    parts[#parts + 1] = "}"
    f:write(table.concat(parts))
    f:close()
end

local function finalize(why)
    if finalized then return end
    finalized = true
    write_watch_csv()
    write_events_csv()
    write_break_csv()
    write_summary()
    write_readmap()
    api:write("FINALIZED " .. why .. " frames=" .. tostring(frames) .. " verdict=" .. overall_verdict() .. "\n")
    api:flush()
    if rom011_marker_path and #rom011_marker_path > 0 then
        local okm, m = pcall(io.open, rom011_marker_path, "w")
        if okm and m then
            m:write("done:ProbeRuntime001ReadMap")
            m:close()
        end
    end
end

local frame_cb
frame_cb = callbacks:add("frame", function()
    frames = frames + 1
    if frames % 300 == 0 then
        liveness.heartbeat = liveness.heartbeat + 1
        local total = 0
        for _, span in ipairs(SPANS) do total = total + span.hits end
        heartbeat:write(string.format("%d,%d,%d,%d,%d\n", frames, total,
            lv_hits("liveness_script_interpreter"), lv_hits("liveness_animation_selector"), granule_count))
        heartbeat:flush()
    end
    sample_dma()
    if frames % FLUSH_EVERY == 0 then
        write_watch_csv()
        write_events_csv()
        write_summary()
    end
    if frames >= FRAME_LIMIT then
        finalize("frame limit reached")
    end
end)

api:write("READY frames_callback=" .. tostring(frame_cb ~= nil) .. "\n")
api:flush()
