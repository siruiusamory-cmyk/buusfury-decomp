assert(type(rom011_marker_path) == "string")

local frame = 0
local callback_id

callback_id = callbacks:add("frame", function()
    frame = frame + 1
    if frame == 180 then
        local file = assert(io.open(rom011_marker_path, "w"))
        file:write("180")
        file:close()
        callbacks:remove(callback_id)
        callback_id = nil
        rom011_marker_path = nil
    end
end)
