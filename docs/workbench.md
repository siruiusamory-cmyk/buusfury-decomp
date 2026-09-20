# Webfoot Workbench architecture

Workbench is an optional PySide6 client over the production SDK:

```text
Atlas search
-> Inspector
-> semantic dialogue target resolution
-> dialogue authoring API
-> project representation
-> validate_project
-> build_project
-> generated ROM
```

For mapped dialogue records, the Inspector keeps retail text, the saved project
override, and unsaved editor contents separate. Typing performs lightweight SDK
validation only. Apply or Revert persists the normal project representation and
makes earlier project validation and build results stale; the Build tab then
requires Validate before Build again. Unsupported search results remain
read-only and have no address- or text-based fallback.

The shipped window is titled DragonByte Z and has eight tabs, in contract order:
Atlas, Inspector, Maps, Map, Map Browser, Graphics, Build, Launch. Only Atlas is
enabled until a ROM is opened; the read-only Map Browser sits between the Map
authoring workspace and Graphics.

## Map Browser: Edit Layout

`DRAGONBYTE-Z-MAP-LAYOUT-EDITOR-001`. The Map Browser stays read-only until its
**Edit Layout** mode is switched on. That mode edits exactly one thing, through
`tools/webfoot/map_layout_edit.py` and the proven writer in
`tools/webfoot/map_layout_write.py`: one 256x256 chunk cell of a map's dominant
layer may be reassigned to another chunk **that same layer already uses**. The
grid overlay marks each chunk cell, the chooser offers that layer's own existing
chunks as thumbnails, and a pick previews immediately in memory - no ROM file is
opened to preview. Apply commits a pick, Revert cell restores one cell to the
chunk the source ROM holds, and Reset pending edits drops the session's changes.

Saving is Save As: it writes a NEW ROM and never the source, with the emitted
image reopened and every requested cell re-read before the save is reported. With
no pending edits the output is byte-identical to the source. Layers and maps
outside the proven form - screen-entry planes, Map 19's terrain field, absent
slots, and dominant grids that use a single chunk and so have no alternative -
are shown READ ONLY with the reason stated, which is a state rather than an error.
The Map Browser still identifies images by SHA-256 and refuses a non-canonical
one, so a ROM this feature has already written cannot be re-opened in the browser;
re-open validation is programmatic (the emitted file is re-read and re-rendered)
and, for a person, the emitted ROM is played in an emulator.

Workbench owns presentation and interaction. Webfoot SDK/domain code owns ROM
semantics.
