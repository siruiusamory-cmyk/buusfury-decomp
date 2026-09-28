# data/ - extracted and derived data

Empty at DECOMP-BASELINE-001 by design.

What belongs here: data tables, string pools, palettes and asset manifests that a
later ticket has extracted and *proven* - each with its provenance.

Nothing ROM-derived is committed without a ticket that confirms it. In
particular the string pool and the colour LUTs are currently `class: "ads"` in
`config/regions.json`, meaning they are still attributed to ARM Developer Suite
output rather than to an independently authored source.
