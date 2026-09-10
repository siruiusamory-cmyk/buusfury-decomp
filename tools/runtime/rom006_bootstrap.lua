-- Deterministic ROM-006 bootstrap for mGBA 0.10.5.
-- Output is local and ignored; no ROM or emulated-memory writes are performed.

-- Output root follows the established runtime convention (`os.getenv` override
-- with a default), rather than a developer-specific absolute path. The default
-- is repository-relative and resolves against mGBA's working directory, which
-- `load_mgba_lua.ps1` inherits from its caller; run it from the repository root,
-- or set `ROM006_OUT` to an absolute path. The launcher independently validates
-- that the saved state lands directly beneath `build\rom006`.
local output_root = os.getenv("ROM006_OUT") or "build/rom006"
local output_state = output_root .. "/bootstrap.mss"
local output_screen = output_root .. "/bootstrap.png"

local pulses = {
    [1210] = C.GBA_KEY.A,
    [1810] = C.GBA_KEY.A,
    [2410] = C.GBA_KEY.A,
}
local releases = {
    [1215] = C.GBA_KEY.A,
    [1815] = C.GBA_KEY.A,
    [2415] = C.GBA_KEY.A,
}

local function begin_bootstrap(reset_core)
    assert(emu ~= nil, "mGBA did not attach the emulation core")
    assert(emu:getGameCode() == "AGB-BG3E")
    assert(emu:romSize() == 8388608)

    emu:setKeys(0)
    if reset_core then emu:reset() end

    local frame = 0
    local callback_id
    callback_id = callbacks:add("frame", function()
        frame = frame + 1
        if pulses[frame] then emu:addKey(pulses[frame]) end
        if releases[frame] then emu:clearKey(releases[frame]) end
        if frame == 2420 then
            emu:screenshot(output_screen)
            assert(emu:saveStateFile(output_state))
            console:log("ROM-006 bootstrap saved at emulated frame 2420")
            callbacks:remove(callback_id)
        end
    end)
end

if emu == nil then
    local start_callback_id
    start_callback_id = callbacks:add("start", function()
        callbacks:remove(start_callback_id)
        begin_bootstrap(false)
    end)
    console:log("ROM-006 bootstrap waiting for a ROM core")
else
    begin_bootstrap(true)
end
