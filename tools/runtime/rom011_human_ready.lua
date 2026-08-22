assert(emu ~= nil, "mGBA did not attach the emulation core")
assert(emu:getGameCode() == "AGB-BG3E")
assert(emu:romSize() == 8388608)
