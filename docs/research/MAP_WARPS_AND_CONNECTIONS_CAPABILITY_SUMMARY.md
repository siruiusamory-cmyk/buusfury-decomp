# Editing map transitions: capability summary

What the shipped map-transition editing capability is, what it added, and the
limitations it preserves.

## What the capability is

`warps` is `shipped`. An author can list a map's existing connections and retarget
a destination, arrival and facing through the normal project and build path; can
create a transition the canonical image does not contain under the durable
identity `map:NNNN/transition:<name>`, composed over a same-map 566-class template
and built deterministically above the original ROM EOF; and can see every
supported transition drawn on the map as the region that triggers it, selecting
one with a click and moving it with a drag as one undoable gesture.

## Result

| Property | Value |
| --- | --- |
| Capability | `warps` is `shipped`, proof `runtime` |
| Registry | DragonByte Z moves **19 / 24 (79%)** to **20 / 24 - 83%** |
| Family tally | `EDIT` moves **7 / 8** to **8 / 8** (READ 5/5, AUTHOR 3/7, DELIVER 4/4) |
| Phase | Phase 2 - Map Editing - **complete** |
| Next capability | graphics import (Phase 3), chosen and **not started** |
| Baseline | `5ec2c67912477d67897dbdef1c3a2c257222f34c` |
| Closeout commit | `6c583d0548d02800243b28af63d1d10cc74953c1` ("Ship warps and connections and complete Phase 2") |
| Merge | `cdbe51c26656d7b6ae9bb832167741c8d7f19101` (merge of `record/map-warps-closeout-001`) |
| Public progress impact | `UPDATED` - registry, roadmap and project status changed with the capability |

Runtime proof: a human-operated mGBA run consumed an authored transition, and the
engine's own loaded record array held the authored entry above the original
image's end. Independent review was run at the sub-pass level, and each sub-pass's
verdict and merge SHA is recorded against the numbered requirement it closed in
the working record; this parent record records no separate review candidate of its
own, so none is claimed here.

## Preserved limitations

Fail-closed limits are unchanged and carried in the working record: the 169-class
family whose stored arrival is a scene-relative delta, and a connection root shared
with another map, are both refused; unsupported forms fail closed; the unresolved
bytes `+0x13` and the low nibble of `+0x10` are preserved but not editable; the
`0x03001A34` selector's non-zero arrival-facing case is untested; there is no
transition deletion; a shadowed stale staged creation has no per-row discard action,
so Apply refuses and both values survive; and a transition the project creates is
drawn read-only on the canvas because it has no record in the image.
