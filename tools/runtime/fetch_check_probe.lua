-- READ-ONLY fetch check, sharpened: arm and REPORT, then scan on the first frames, before anything can hang.
--
-- The previous version logged nothing after arming because it waited until frame 300 and the patched image
-- never got there. This one reports the arming result explicitly, scans at frame 2, and re-arms a breakpoint at
-- any RAM copy it finds, so "the ROM copy is not fetched" and "the breakpoint never armed" cannot be confused.

local log_file = os.getenv("TOOLKIT031_OUT")
local frames = 0
local hits = { loop = 0, block = 0, copy = 0 }
local copy_address = nil

local function note(text)
  local file = io.open(log_file, "a")
  if file then file:write(text .. "\n"); file:close() end
end

local function arm(address, name)
  -- This build takes (handler, address); the reverse order fails with "invoking failed", which reads like a
  -- silent channel and is not a negative.
  local ok, err = pcall(function() emu:setBreakpoint(function(_info)
    hits[name] = hits[name] + 1
    if hits[name] <= 2 then
      note(string.format("FETCH %s frame=%d at 0x%08X", name, frames, address))
    end
  end, address) end)
  note(string.format("FETCH armed %s at 0x%08X ok=%s%s", name, address, tostring(ok),
                     ok and "" or (" err=" .. tostring(err))))
end

arm(0x0800F1A4, "loop")
arm(0x0800F2B2, "block")

local window = emu:readRange(0x0800F2A0, 18)
local function find(base, size, step)
  local address = base
  while address < base + size do
    if emu:readRange(address, 18) == window then return address end
    address = address + step
  end
  return nil
end

callbacks:add("frame", function()
  frames = frames + 1
  if frames == 2 then
    note("FETCH scanning for a RAM copy of the block's instructions")
    local iwram = find(0x03000000, 0x8000, 2)
    note(iwram and string.format("FETCH IWRAM copy at 0x%08X", iwram) or "FETCH no IWRAM copy")
    local ewram = find(0x02000000, 0x10000, 2)
    note(ewram and string.format("FETCH EWRAM copy at 0x%08X (first 64 KiB only)", ewram)
         or "FETCH no EWRAM copy in the first 64 KiB")
    copy_address = iwram or ewram
    if copy_address then arm(copy_address, "copy") end
  end
  if frames % 240 == 0 then
    note(string.format("FETCH frame=%d loop=%d block=%d copy=%d", frames, hits.loop, hits.block, hits.copy))
  end
  if frames >= 600 then
    note(string.format("FETCH done: loop=%d block=%d copy=%d", hits.loop, hits.block, hits.copy))
    emu:exit()
  end
end)

note("FETCH probe armed")
