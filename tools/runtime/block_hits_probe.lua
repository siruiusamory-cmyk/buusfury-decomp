-- READ-ONLY: does the draw-loop block at 0x0800F2B2 actually execute, and where does the loop run from?
--
-- Two breakpoints, both read-only: the block's first instruction and the loop's piece advance. Each logs
-- its arming result and its hit count, so a silent target beside a firing liveness channel is a real
-- negative rather than an unproven instrument (docs/skills/mgba-runtime.md, section 8). No emulated memory
-- is written and no input is pressed.

local log_file = os.getenv("TOOLKIT031_OUT")
local frames = 0
local hits = { block = 0, advance = 0 }
local armed = {}

local function note(text)
  local file = io.open(log_file, "a")
  if file then file:write(text .. "\n"); file:close() end
end

local function arm(name, address)
  local ok, err = pcall(function()
    emu:setBreakpoint(function()
      hits[name] = hits[name] + 1
      if hits[name] == 1 then note(string.format("HIT %s 0x%08X first at frame %d", name, address, frames)) end
    end, address)
  end)
  armed[name] = ok
  if not ok then note(string.format("ARM %s 0x%08X FAILED: %s", name, address, tostring(err))) end
end

arm("block", 0x0800F2B2)     -- the first instruction the patch replaces
arm("advance", 0x0800F2C0)   -- the piece advance the stub returns to (liveness for the loop)

note(string.format("ARMED block=%s advance=%s", tostring(armed.block), tostring(armed.advance)))

callbacks:add("frame", function()
  frames = frames + 1
  if frames == 60 or frames == 180 or frames == 240 then
    note(string.format("HITS frame=%d block=%d advance=%d", frames, hits.block, hits.advance))
    note(string.format("PC frame=%d 0x%08X", frames, emu:currentFrame()))
  end
  if frames >= 240 then
    note(string.format("BLOCKHITS done block=%d advance=%d", hits.block, hits.advance))
    emu:exit()
  end
end)

note("BLOCKHITS armed")
