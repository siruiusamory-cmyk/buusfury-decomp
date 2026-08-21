local frame = 0
local callback_id

assert(emu ~= nil, "mGBA did not attach the emulation core")
assert(emu:getGameCode() == "AGB-BG3E")
assert(emu:romSize() == 8388608)
emu:setKeys(0)

callback_id = callbacks:add("frame", function()
    frame = frame + 1
    if frame == 121 then emu:addKey(C.GBA_KEY.DOWN) end
    if frame == 241 then emu:clearKey(C.GBA_KEY.DOWN) end
    if frame == 400 then callbacks:remove(callback_id) end
end)
