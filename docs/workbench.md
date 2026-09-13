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

Workbench owns presentation and interaction. Webfoot SDK/domain code owns ROM
semantics.
