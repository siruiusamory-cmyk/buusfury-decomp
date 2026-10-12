-- READ-ONLY hit census across the replaced block, in the PLAIN image.
--
-- Every address in 0x0800F2B2..0x0800F2BE gets its own breakpoint and its own counter. Code that always enters
-- at 0x0800F2B2 increments them ALL, once each per pass, so equal counts mean no mid-block entry. Any address
-- whose count EXCEEDS its predecessor's was entered late, which is the review's hypothesis made visible.

local log_file = os.getenv("TOOLKIT031_OUT")
local frames = 0
local ADDRESSES = { 0x0800F2B2, 0x0800F2B4, 0x0800F2B6, 0x0800F2B8, 0x0800F2BA, 0x0800F2BC, 0x0800F2BE }
local counts = {}
local firsts = {}

local function note(text)
  local file = io.open(log_file, "a")
  if file then file:write(text .. "\n"); file:close() end
end

for _, address in ipairs(ADDRESSES) do
  counts[address] = 0
  local ok, err = pcall(function() emu:setBreakpoint(function()
    counts[address] = counts[address] + 1
    if not firsts[address] then
      firsts[address] = frames
      note(string.format("HIT first 0x%08X at frame %d", address, frames))
    end
  end, address) end)
  if not ok then
    note(string.format("HIT arm failed 0x%08X: %s", address, tostring(err)))
  end
end

note("HIT census armed over " .. #ADDRESSES .. " address(es)")

callbacks:add("frame", function()
  frames = frames + 1
  if frames >= 600 then
    for _, address in ipairs(ADDRESSES) do
      note(string.format("HIT count 0x%08X = %d (first frame %s)", address, counts[address],
                         tostring(firsts[address])))
    end
    note("HIT census done")
    emu:exit()
  end
end)
