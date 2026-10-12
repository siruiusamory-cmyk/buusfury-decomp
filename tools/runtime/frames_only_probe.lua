-- Frames-only observer: proves whether the emulator advances at all, with no other logic that could error.
local log_file = os.getenv("TOOLKIT031_OUT")
local frames = 0
local function note(text)
  local file = io.open(log_file, "a")
  if file then file:write(text .. "\n"); file:close() end
end
note("FRAMES-ONLY probe armed")
callbacks:add("frame", function()
  frames = frames + 1
  if frames % 120 == 0 then
    note(string.format("FRAME %d pc=0x%08X", frames, emu:currentFrame()))
  end
  if frames >= 1200 then
    note(string.format("FRAMES-ONLY done at %d", frames))
    emu:exit()
  end
end)
