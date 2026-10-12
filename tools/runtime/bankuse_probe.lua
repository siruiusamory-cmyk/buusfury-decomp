-- READ-ONLY: which palette banks do the tiles of the CURRENTLY VISIBLE sprites actually use?
--
-- The static bound unions every frame and direction of every actor placed in a map, which overstates what is on
-- screen. This reads the tiles the visible OAM entries point at, straight out of OBJ VRAM, and tallies the
-- palette index of every opaque pixel, so the free banks are the ones nothing on screen reaches.
--
-- Sampling: a few named frames are measured in full, because parsing every sprite's tiles is expensive per
-- frame. Nothing is written to emulated memory and no input is pressed.

local log_file = os.getenv("TOOLKIT031_OUT")
local frames = 0
local SAMPLES = { 120, 240, 360, 480, 600 }
local VRAM = 0x06010000
local OAM = 0x07000000
local BANK = 16

local function note(text)
  local file = io.open(log_file, "a")
  if file then file:write(text .. "\n"); file:close() end
end

local function byte_at(block, index)
  return string.byte(block, index) or 0
end

local function measure(sample_frame)
  local oam = emu:readRange(OAM, 1024)
  local index_use = {}
  local entries = 0
  local sprites_8bpp, sprites_4bpp = 0, 0
  for entry = 0, 127 do
    local base = entry * 8
    local attr0 = byte_at(oam, base + 1) | (byte_at(oam, base + 2) << 8)
    local attr1 = byte_at(oam, base + 3) | (byte_at(oam, base + 4) << 8)
    local attr2 = byte_at(oam, base + 5) | (byte_at(oam, base + 6) << 8)
    local mode = (attr0 >> 8) & 3
    if mode ~= 2 then
      entries = entries + 1
      local is_8bpp = (attr0 >> 13) & 1
      local shape = (attr0 >> 14) & 3
      local size = (attr1 >> 14) & 3
      if is_8bpp == 1 then sprites_8bpp = sprites_8bpp + 1 else sprites_4bpp = sprites_4bpp + 1 end
      -- Tile footprint from the shape/size table, in 8x8 tiles.
      local dims = {
        [0] = { {1,1},{2,2},{4,4},{8,8} },
        [1] = { {2,1},{4,1},{4,2},{8,4} },
        [2] = { {1,2},{1,4},{2,4},{4,8} },
      }
      local d = dims[shape] and dims[shape][size + 1]
      if d then
        local tiles_x, tiles_y = d[1], d[2]
        local tile = attr2 & 0x3FF
        for ty = 0, tiles_y - 1 do
          for tx = 0, tiles_x - 1 do
            local unit = tile + ty * 32 + tx
            local address = VRAM + (is_8bpp == 1 and unit * 64 or unit * 32)
            local data = emu:readRange(address, is_8bpp == 1 and 64 or 32)
            for offset = 1, #data do
              local value = byte_at(data, offset)
              if is_8bpp == 1 then
                if value ~= 0 then index_use[value] = (index_use[value] or 0) + 1 end
              else
                local low = value & 0xF
                local high = (value >> 4) & 0xF
                if low ~= 0 then
                  local index = (attr2 >> 12) & 0xF
                  index_use[index * BANK + low] = (index_use[index * BANK + low] or 0) + 1
                end
                if high ~= 0 then
                  local index = (attr2 >> 12) & 0xF
                  index_use[index * BANK + high] = (index_use[index * BANK + high] or 0) + 1
                end
              end
            end
          end
        end
      end
    end
  end

  local free = {}
  for bank = 0, 15 do
    local used = 0
    for value = bank * BANK, bank * BANK + BANK - 1 do
      if index_use[value] then used = used + 1 end
    end
    if used == 0 then free[#free + 1] = bank end
  end
  local distinct = 0
  for _ in pairs(index_use) do distinct = distinct + 1 end
  note(string.format("BANKUSE frame=%d entries=%d (8bpp %d, 4bpp %d) distinct_indices=%d free_banks=[%s]",
                     sample_frame, entries, sprites_8bpp, sprites_4bpp, distinct,
                     table.concat(free, ",")))
end

callbacks:add("frame", function()
  frames = frames + 1
  for _, sample in ipairs(SAMPLES) do
    if frames == sample then
      measure(frames)
    end
  end
  if frames >= 660 then
    note("BANKUSE done")
    emu:exit()
  end
end)

note("BANKUSE armed")
