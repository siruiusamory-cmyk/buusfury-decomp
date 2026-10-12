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
makes earlier project validation and build results stale; the Build action then
requires Validate before Build again. Unsupported search results remain
read-only and have no address- or text-based fallback.

The shipped window is titled DragonByte Z and names four primary editors on one
compact strip, in contract order: Atlas, Inspector, Maps, Graphics. Open ROM,
Open Project, Validate, Build and Run sit beside them; the Maps editor holds its
own Browse, Layout, Objects and Warps modes, the Scene editor is opened from the
placement it belongs to, and Build and Run open as dialogs. The editors are
always selectable and show their own empty state until a ROM is loaded.

## Maps editor: Layout mode

`DRAGONBYTE-Z-MAP-LAYOUT-EDITOR-001`. The Maps editor's **Browse** mode is
read-only; switching to **Layout** mode enables editing. Four shipped operations
live there, over `tools/webfoot/map_layout_edit.py` and the proven writer in
`tools/webfoot/map_layout_write.py`: one 256x256 chunk cell of a map's dominant
layer may be reassigned to another chunk **a dominant layer of the same map
already uses**; any of the map's dominant layers' chunks can be painted onto those
chunk cells; a chunk the
layer did not have can be created and its 32x32 plane painted; and the structure
section can grow a supported layer's chunk grid or activate an unused layer slot.
The
grid overlay marks each chunk cell, the chooser offers that layer's own existing
chunks as thumbnails, and a pick previews immediately in memory - no ROM file is
opened to preview. Apply commits a pick, Revert cell restores one cell to the
chunk the source ROM holds, and Reset pending edits drops the session's changes.

Saving is Save As: it writes a NEW ROM and never the source, with the emitted
image reopened and every requested cell re-read before the save is reported. The
image and the provenance document that describes it are built at temporary sibling
paths and only then moved onto the chosen destinations, so an existing file at
that path survives a failed save byte-for-byte. With no pending edits the output is
byte-identical to the source. Everything in that paragraph except the cell re-read
is the shared authored-image transaction in `tools/webfoot/authored_image.py`,
which is the path any future authored-image editor uses; only the domain half -
which replacements are legal, and what an emitted image must read back - stays
with the layout editor.

## Reopening a ROM this feature wrote

Save As writes the ROM **and a small provenance manifest beside it**
(`<rom name>.dragonbyte.json`, in the project's existing write-manifest document
shape: schema version, canonical base SHA-256 and profile id, emitted SHA-256 and
size, and every change with its offset and both byte values).

The Atlas editor's ROM open accepts a modified image only through that provenance. A
derivative is accepted when - and only when - the manifest names the supported
canonical image and a configured profile, the file's own SHA-256 matches the
manifest's declared output, every declared change is a four-byte field of a
*dominant* chunk window identified by its own `map:NNNN layer S cell C` owner, the
replacement is a non-null chunk a dominant layer of that map uses at another of
its cells,
and restoring the declared old values reproduces the canonical image exactly by
SHA-256. That last check bounds an accepted derivative to the canonical image plus
exactly its declared fields, and it needs no copy of the canonical file.

An accepted derivative is browseable and renders its edited layout, because the Maps
editor renders the *reconstructed canonical bytes* with the verified edits applied
as overrides - the same preview path the editor uses - and never parses the
derivative as if it were canonical. It is read-only: further layout editing belongs
to the canonical image it derives from. A modified image without a manifest, with a
manifest that does not match it, or with a manifest that declares anything outside
those rules is refused with the reason stated, and the canonical image itself is
still accepted by identity before any manifest is consulted.

Layers and maps outside the proven form - screen-entry planes, Map 19's terrain
field, absent slots, and dominant grids that use a single chunk and so have no
alternative - are shown READ ONLY with the reason stated, which is a state rather
than an error.

Workbench owns presentation and interaction. Webfoot SDK/domain code owns ROM
semantics.
