-- Observer: one breakpoint at the hook site, logging the argument registers each time it fires.
-- Read-only. Writes only to the run directory the injected session supplies.
local frames = 0
local hits = 0
local out = io.open("hook-hits.csv", "w")
out:write("hit,frame,r0,r1,r4,sp,lr\n")
out:flush()

local function onFrame()
  frames = frames + 1
  emu:frame()
end

local function onHit()
  hits = hits + 1
  if hits <= 40 then
    out:write(string.format(
      "%d,%d,%08X,%08X,%08X,%08X,%08X\n",
      hits, frames,
      emu:read32(emu:getRegister(0, 0)),
      emu:read32(emu:getRegister(0, 1)),
      emu:read32(emu:getRegister(0, 4)),
      emu:read32(emu:getRegister(0, 13)),
      emu:read32(emu:getRegister(0, 14))
    ))
    out:flush()
  end
  return true
end

-- 0x08004892 is the displaced `adds r0,r4,#0`; the hook branch sits there.
emu:setBreakpoint(onHit, 0x08004892)
local ready = io.open("hook-ready.txt", "w")
ready:write("ready\n")
ready:close()
print("hook observer armed")
