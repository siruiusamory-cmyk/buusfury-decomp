-- READ-ONLY: measurement 1. Does the entry veneer reach the injected BODY, and does the body return to
-- the resume address? Three breakpoints, each logging its arm result and its hit count, so a silent target
-- beside a firing neighbour is a real negative and all-silent means the instrument is unproven:
--   veneer 0x0800F2B2  the patched block's first instruction (liveness for the whole path)
--   body   <BODY>      the injected body's first instruction (did the veneer's bx arrive?)
--   resume 0x0800F2C0  where the body must return (did the body finish?)
--   thunk  0x08049144  measurement 2's target; armed here so one run answers both
-- Reads no emulated memory beyond the PC, writes nothing, presses nothing.

local log_file = os.getenv("TOOLKIT031_OUT")
local frames = 0
local HITS = {}
local ARMED = {}
local FIRST = {}

local function note(text)
  local file = io.open(log_file, "a")
  if file then file:write(text .. "\n"); file:close() end
end

local function arm(name, address)
  local ok, err = pcall(function()
    emu:setBreakpoint(function()
      HITS[name] = (HITS[name] or 0) + 1
      if not FIRST[name] then
        FIRST[name] = frames
        note(string.format("FIRSTHIT %s 0x%08X at frame %d", name, address, frames))
      end
    end, address)
  end)
  ARMED[name] = ok
  if not ok then note(string.format("ARM %s 0x%08X FAILED: %s", name, address, tostring(err))) end
end

local body = tonumber(os.getenv("BODY_ADDRESS") or "", 16)
arm("veneer", 0x0800F2B2)
arm("resume", 0x0800F2C0)
arm("thunk", 0x08049144)
if body then
  arm("body", body)
else
  note("BODY_ADDRESS not set: the body channel is UNARMED and its silence means nothing")
end

note(string.format("ARMED veneer=%s body=%s resume=%s thunk=%s body_address=0x%X",
                   tostring(ARMED.veneer), tostring(ARMED.body), tostring(ARMED.resume),
                   tostring(ARMED.thunk), body or 0))

callbacks:add("frame", function()
  frames = frames + 1
  if frames == 5 or frames == 30 or frames == 120 or frames == 300 then
    note(string.format("HITS frame=%d veneer=%d body=%d resume=%d thunk=%d pc=0x%08X",
                       frames, HITS.veneer or 0, HITS.body or 0, HITS.resume or 0, HITS.thunk or 0,
                       emu:currentFrame()))
  end
  if frames >= 300 then
    note(string.format("BODYCHAIN done veneer=%d body=%d resume=%d thunk=%d",
                       HITS.veneer or 0, HITS.body or 0, HITS.resume or 0, HITS.thunk or 0))
    emu:exit()
  end
end)

note("BODYCHAIN armed")
