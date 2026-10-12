-- READ-ONLY: prove the runtime palette writer landed, by reading OBJ palette RAM and the OAM banks.
--
-- Writes nothing to emulated memory and presses no input. At named frames it appends, for each palette
-- bank, the 16 halfwords of that bank plus which banks the visible OAM entries select, so the run's log
-- alone shows whether the appended Cell palettes replaced a bank and whether a Cell piece selected it.

local log_file = os.getenv("TOOLKIT031_OUT")
local frames = 0
local PALETTE = 0x05000200
local OAM = 0x07000000
local SAMPLES = { 2, 30, 90, 180 }
local BANK = 16

local function note(text)
  local file = io.open(log_file, "a")
  if file then file:write(text .. "\n"); file:close() end
end

local function halfword(block, index)
  local low = string.byte(block, index * 2 + 1) or 0
  local high = string.byte(block, index * 2 + 2) or 0
  return low | (high << 8)
end

local function measure(frame)
  local palette = emu:readRange(PALETTE, 512)
  for bank = 0, 15 do
    local entries = {}
    for slot = 1, 16 do
      entries[#entries + 1] = string.format("%04X", halfword(palette, bank * BANK + slot - 1))
    end
    note(string.format("PAL frame=%d bank=%d [%s]", frame, bank, table.concat(entries, " ")))
  end
  local oam = emu:readRange(OAM, 1024)
  local selected = {}
  for entry = 0, 127 do
    local base = entry * 8
    local attr0 = string.byte(oam, base + 1) or 0
    local attr2 = string.byte(oam, base + 5) or 0
    local mode = (attr0 >> 8) & 3
    if mode ~= 2 then
      local bank = (attr2 >> 4) & 0xF
      selected[bank] = (selected[bank] or 0) + 1
    end
  end
  local list = {}
  for bank = 0, 15 do
    if selected[bank] then list[#list + 1] = string.format("%d:%d", bank, selected[bank]) end
  end
  note(string.format("OAM frame=%d visible_banks=%s", frame, table.concat(list, ",")))
end

callbacks:add("frame", function()
  frames = frames + 1
  for _, sample in ipairs(SAMPLES) do
    if frames == sample then measure(frames) end
  end
  if frames >= 240 then
    note("PALDUMP done")
    emu:exit()
  end
end)

note("PALDUMP armed")
