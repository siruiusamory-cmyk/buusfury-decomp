# MAP-WARPS-AND-CONNECTIONS-001 - closure

Closure record for the parent ticket. The ticket's own Objective, Context delta,
Required Work, Scope Boundaries, Ticket-Specific Validation, Required Review and
Completion Criteria, and the item-by-item closeout that maps every numbered
requirement to its committed evidence, are all retained unchanged in the working
record at [`../MAP-WARPS-AND-CONNECTIONS-001.md`](../MAP-WARPS-AND-CONNECTIONS-001.md).
Read that record for the evidence; this file exists so the archive holds a
closure for the parent, which it previously did not.

STATUS: **SHIPPED (2026-09-28).** Phase 2D complete, and Phase 2 (Map Editing)
complete with it.

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
| Baseline | `89a37ed6176db77d7d77b2f4dc660800258911f8` |
| Closeout commit | `b2536f6f00eada62a2e111b97bb077df4465ad7f` ("Ship warps and connections and complete Phase 2") |
| Merge | `af688c0d65ebd60412cedd094834e85013e5806f` (merge of `ticket/map-warps-closeout-001`) |
| Public progress impact | `UPDATED` - registry, roadmap and project status changed with the capability |

Runtime proof: a human-operated mGBA run consumed an authored transition, and the
engine's own loaded record array held the authored entry above the original
image's end. Independent review was run at the sub-pass level, and each sub-pass's
verdict and merge SHA is recorded against the numbered requirement it closed in
the working record; this parent ticket records no separate review candidate of its
own, so none is claimed here.

## Sub-passes

Eleven sub-pass records are retained at the ticket root and in this archive, and
none was deleted, squashed or rewritten. Nine of them also retain their own
evidence record at the ticket root, because deleting it is not this repository's
archival pattern; two exist only in the archive, where their closures were
written:

`MAP-WARP-FORMAT-001` · `MAP-WARP-PROJECT-AUTHORING-001` ·
`MAP-WARP-WORKBENCH-001` · `MAP-WARP-WORKBENCH-RUNTIME-001` ·
`MAP-WARP-CREATE-PROJECT-001` · `MAP-WARP-CREATE-RUNTIME-001` ·
`MAP-WARP-CREATE-WORKBENCH-001` · `MAP-WARP-CANVAS-001` ·
`MAP-WARP-RUNTIME-EDIT-001` · `MAP-WARP-FACING-TRACE-001` (archive only) ·
`MAP-WARP-STACK-REVIEW-AND-INTEGRATE-001` (archive only).

## Preserved limitations

Fail-closed limits are unchanged and carried in the working record: the 169-class
family whose stored arrival is a scene-relative delta, and a connection root shared
with another map, are both refused; unsupported forms fail closed; the unresolved
bytes `+0x13` and the low nibble of `+0x10` are preserved but not editable; the
`0x03001A34` selector's non-zero arrival-facing case is untested; there is no
transition deletion; a shadowed stale staged creation has no per-row discard action,
so Apply refuses and both values survive; and a transition the project creates is
drawn read-only on the canvas because it has no record in the image.
