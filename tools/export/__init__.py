"""Canonical Buu's Fury resource export (ASSET-EXPORT-001).

The package builds a deterministic local resource library from the canonical ROM
using the accepted post-LOGX schemas. Entry point:

    python -m tools.export.buu_resource_export --rom <ROM> --output <ROOT>

Modules:

* :mod:`tools.export.webfoot_strict` - strict exact-size container decoding.
* :mod:`tools.export.canonical` - accepted map/layer/chunk/bank/sprite/frame
  schema readers and the bounds-checked ROM reader.
* :mod:`tools.export.render` - pixel assembly and composition.
* :mod:`tools.export.naming` - deterministic numeric paths.
* :mod:`tools.export.metadata` - structural JSON/CSV output and the no-prose
  guard.
* :mod:`tools.export.png` - the deterministic RGBA PNG encoder.
"""
