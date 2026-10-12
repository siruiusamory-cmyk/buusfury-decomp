-- READ-ONLY OBJ palette census: which banks are written, and which banks any visible sprite selects.
--
-- "Static" here means two independent measurements per frame:
--   1. WRITES: read the whole 512-byte OBJ palette block and diff it against the previous frame, per 32-byte
--      bank. A bank whose bytes change was written. A bank that never changes was never written, in this scene.
--   2. USE: walk the 128 hardware OAM entries and, for every entry that is not hidden (mode 2), record which
--      palette bank its attr2 selects and whether it is 4bpp or 8bpp.
--
-- Nothing is written to emulated memory; no input is pressed.

local log_file = os.getenv("TOOLKIT031_OUT")
local frames = 0
local PAL = 0x05000200
local OAM = 0x07000000
local LIMIT = tonumber(os.getenv("PALETTE_CENSUS_FRAMES") or "900")
local ANNOUNCE = 60
local OBJ_PALETTE_FILE = 0x05652C

local changes = {}
local usage = {}
local depth = {}
for bank = 0, 15 do
  changes[bank] = 0
  usage[bank] = 0
  depth[bank] = 0
end

local function note(text)
  local file = io.open(log_file, "a")
  if file then file:write(text .. "\n"); file:close() end
end

local function byte_at(block, index)
  return string.byte(block, index) or 0
end

local function bank_of(attr2)
  return (attr2 >> 12) & 0xF
end

local previous = emu:readRange(PAL, 512)

local function frame_summary()
  local used, changed = {}, {}
  for bank = 0, 15 do
    if usage[bank] > 0 then used[#used + 1] = bank end
    if changes[bank] > 0 then changed[#changed + 1] = bank end
  end
  return table.concat(used, ","), table.concat(changed, ",")
end

callbacks:add("frame", function()
  frames = frames + 1
  local current = emu:readRange(PAL, 512)
  for bank = 0, 15 do
    local from, to = 1 + 32 * bank, 32 + 32 * bank
    if current:sub(from, to) ~= previous:sub(from, to) then
      changes[bank] = changes[bank] + 1
      if changes[bank] == 1 then
        note(string.format("PALCENSUS bank %d first written at frame %d", bank, frames))
      end
    end
  end
  previous = current

  local oam = emu:readRange(OAM, 1024)
  for entry = 0, 127 do
    local base = entry * 8
    local attr0 = byte_at(oam, base + 1) | (byte_at(oam, base + 2) << 8)
    local attr2 = byte_at(oam, base + 5) | (byte_at(oam, base + 6) << 8)
    local mode = (attr0 >> 8) & 3
    if mode ~= 2 then
      local bank = bank_of(attr2)
      usage[bank] = usage[bank] + 1
      if (attr0 >> 13) & 1 == 0 then depth[bank] = depth[bank] + 1 end
    end
  end

  if frames % ANNOUNCE == 0 then
    local used, changed = frame_summary()
    note(string.format("PALCENSUS frame=%d used_banks=[%s] ever_written=[%s]", frames, used, changed))
  end
  if frames >= LIMIT then
    local used, changed = frame_summary()
    note(string.format("PALCENSUS done frames=%d used_banks=[%s] ever_written=[%s]", frames, used, changed))
    for bank = 0, 15 do
      note(string.format("PALCENSUS bank %d: selected by visible sprites %d time(s), written %d time(s), "
                         .. "four_bpp_selections %d", bank, usage[bank], changes[bank], depth[bank]))
    end
    emu:exit()
  end
end)

note("PALCENSUS armed; watching 0x05000200 for 512 bytes and 0x07000000 for 128 entries")
