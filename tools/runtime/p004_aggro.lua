-- P-004 aggro driver: B-taps fire ki blasts; player already faces the
-- wolves in this state. No directional input required.
local frame = 0
local callback_id

assert(emu ~= nil, "mGBA did not attach the emulation core")
assert(emu:getGameCode() == "AGB-BG3E")
emu:setKeys(0)

callback_id = callbacks:add("frame", function()
    frame = frame + 1
    if frame == 60 or frame == 61 then emu:addKey(C.GBA_KEY.B) end
    if frame == 62 or frame == 63 then emu:clearKey(C.GBA_KEY.B) end
    if frame == 160 or frame == 161 then emu:addKey(C.GBA_KEY.B) end
    if frame == 162 or frame == 163 then emu:clearKey(C.GBA_KEY.B) end
    if frame == 260 or frame == 261 then emu:addKey(C.GBA_KEY.B) end
    if frame == 262 or frame == 263 then emu:clearKey(C.GBA_KEY.B) end
    if frame == 400 then
        emu:setKeys(0)
        callbacks:remove(callback_id)
    end
end)
