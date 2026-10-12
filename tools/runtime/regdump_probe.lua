-- READ-ONLY register dump at the piece advance, patched versus plain, on the same piece.
--
-- The block ends at 0x0800F2BE and the advance starts at 0x0800F2C0. Dumping the live registers there says what
-- the stub actually left behind: r6 (the composed OAM word 1), r3 (retail leaves the tile), r1 (the OAM entry),
-- r0 (the piece pointer the advance reads), lr (the running tile cursor) and CPSR. Comparing the two images at
-- the same piece index is the whole point: the first divergence names the cause.

local log_file = os.getenv("TOOLKIT031_OUT")
local frames = 0
local dumps = 0
local LIMIT = 12

local function note(text)
  local file = io.open(log_file, "a")
  if file then file:write(text .. "\n"); file:close() end
end

local function reg(name)
  local ok, value = pcall(emu.readRegister, emu, name)
  return ok and tonumber(value) or nil
end

local function hex(value)
  return value and string.format("0x%08X", value) or "nil"
end

local ok, err = pcall(function() emu:setBreakpoint(function()
  if dumps >= LIMIT then return end
  dumps = dumps + 1
  note(string.format("DUMP %d frame=%d r0=%s r1=%s r2=%s r3=%s r4=%s r5=%s r6=%s r7=%s lr=%s sp=%s cpsr=%s",
                     dumps, frames, hex(reg("r0")), hex(reg("r1")), hex(reg("r2")), hex(reg("r3")),
                     hex(reg("r4")), hex(reg("r5")), hex(reg("r6")), hex(reg("r7")), hex(reg("lr")),
                     hex(reg("sp")), hex(reg("cpsr"))))
end, 0x0800F2C0) end)
note("DUMP probe armed at 0x0800F2C0 ok=" .. tostring(ok) .. (ok and "" or (" err=" .. tostring(err))))

callbacks:add("frame", function()
  frames = frames + 1
  if frames >= 600 then
    note(string.format("DUMP done at frame %d with %d sample(s)", frames, dumps))
    emu:exit()
  end
end)
