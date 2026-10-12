-- READ-ONLY: is the copy thunk's IWRAM target installed when the injected body calls it?
--
-- Measurement 1 proved the injected body runs; measurement 2 proved its copy does not land even with
-- literal arguments. The thunk at 0x08049144 is `bx pc` + `ldr pc,[pc,#-4]`, and its literal (file
-- 0x0804914C) holds 0x030007FC, an IWRAM address. If that IWRAM is not yet populated when the draw loop
-- first runs, the call jumps into unwritten memory. This observer reads that window and the thunk's own
-- bytes at two frames, plus one palette entry as a liveness datum. It writes nothing and presses nothing.

local log_file = os.getenv("TOOLKIT031_OUT")
local frames = 0
local IWRAM = 0x030007E0
local IWRAM_LEN = 0x60
local THUNK = 0x08049144
local THUNK_LEN = 12

local function note(text)
  local file = io.open(log_file, "a")
  if file then file:write(text .. "\n"); file:close() end
end

local function hex(block)
  local out = {}
  for index = 1, #block do out[#out + 1] = string.format("%02X", string.byte(block, index)) end
  return table.concat(out, " ")
end

local function sample(frame)
  local iwram = emu:readRange(IWRAM, IWRAM_LEN)
  local thunk = emu:readRange(THUNK, THUNK_LEN)
  note(string.format("IWRAM frame=%d 0x%08X [%s]", frame, IWRAM, hex(iwram)))
  note(string.format("THUNK frame=%d 0x%08X [%s]", frame, THUNK, hex(thunk)))
  note(string.format("PAL0 frame=%d [%s]", frame, hex(emu:readRange(0x05000200, 4))))
end

callbacks:add("frame", function()
  frames = frames + 1
  if frames == 2 or frames == 30 or frames == 120 then sample(frames) end
  if frames >= 120 then
    note("IWDUMP done")
    emu:exit()
  end
end)

note("IWDUMP armed")
