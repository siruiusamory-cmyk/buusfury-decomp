local frame = 0
local callback_id

assert(emu ~= nil, "mGBA did not attach the emulation core")
assert(emu:getGameCode() == "AGB-BG3E")
assert(emu:romSize() == 8388608)
emu:setKeys(0)

local function stop_route()
    emu:setKeys(0)
    if callback_id ~= nil then
        callbacks:remove(callback_id)
        callback_id = nil
    end
end

rom011_cancel_clean_route = stop_route

callback_id = callbacks:add("frame", function()
    frame = frame + 1
    if frame == 121 then emu:addKey(C.GBA_KEY.DOWN) end
    if frame == 241 then emu:clearKey(C.GBA_KEY.DOWN) end
    if frame == 400 then stop_route() end
end)
