# Ghidra Workflow

## Status

TOOL-001 selected outcome **B - ADOPT WITH REQUIRED CORRECTIONS**. Ghidra is
the default static-analysis database for future ROM tickets when it is used
with the verified profile, explicit Thumb entry-point checks, and independent
evidence review. Its output is analysis evidence, not semantic truth.

The persistent local database, imported ROM copy, applications, caches, logs,
and generated reports live under ignored `build/ghidra/`. Only the small
project-side scripts in `tools/ghidra/` are tracked.

## Pinned local stack

| Component | Pin | Local detail |
|---|---|---|
| Ghidra | 12.1.2 PUBLIC, 2026-06-05 | Release ZIP SHA-256 `b62e81a0390618466c019c60d8c2f796ced2509c4c1aea4a37644a77272cf99d` |
| Java | Eclipse Temurin 21.0.11+10 LTS | Archive SHA-256 `d3625e7cadf23787ea540229544b6e2ab494b3b54da1801879e583e1dfee0a64` |
| GBA loader | [pudii/gba-ghidra-loader](https://github.com/pudii/gba-ghidra-loader) commit `9bfb2d1fe891aa78bab7093a328feb3a52318ab7` | Built for Ghidra 12.1.2; extension ZIP SHA-256 `b0ffd70d2dd075c4d70afa7137c7a39d853a908cfae001e5fbd49d0596368b15` |
| Gradle | 8.14.5 | Used only to build the loader locally |

Ghidra and Java were unpacked rather than installed system-wide. Ghidra's
settings, cache, and temp paths were redirected into `build/ghidra/user/`.
The loader build needed one compatibility-only source edit for Ghidra 12.1.2:
remove the unused `org.python.bouncycastle.util.Arrays` import from
`GBACartrHeader.java`. The pinned upstream commit and this local edit must both
be recorded if the extension is rebuilt.

Ghidra 12.1.2 includes the `support/pyghidraRun.bat` launcher. TOOL-001 used a
Java Ghidra script through `analyzeHeadless` because that was the smallest
working headless path; no separate PyGhidra package was installed.

## Safe project creation

The canonical ROM remains read-only. Always identify it, copy it to the
ignored input area, identify the copy, and re-identify the original after the
experiment:

```powershell
& '.venv\Scripts\webfoot.exe' identify 'roms\Dragon Ball Z - Buu''s Fury (U).gba'
New-Item -ItemType Directory -Force 'build\ghidra\input' | Out-Null
Copy-Item -LiteralPath 'roms\Dragon Ball Z - Buu''s Fury (U).gba' `
  -Destination 'build\ghidra\input\buus_fury_verified.gba'
& '.venv\Scripts\webfoot.exe' identify 'build\ghidra\input\buus_fury_verified.gba'
```

Both identification results must be profile
`buus_fury_usa_rev0_01c1707f`, size 8,388,608, CRC32 `01C1707F`, MD5
`3a74fce97f1ea2b28c2a50ec3df0acee`, and SHA-256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`.
Fail closed on any mismatch.

The calibration import used:

```powershell
& 'build\ghidra\apps\ghidra_12.1.2_PUBLIC\support\analyzeHeadless.bat' `
  'build\ghidra\projects' 'buus_fury_calibration' `
  -import 'build\ghidra\input\buus_fury_verified.gba' `
  -loader 'GBALoader' `
  -processor 'ARM:LE:32:v4t' -cspec 'default' `
  -max-cpu 4 -analysisTimeoutPerFile 900
```

The persistent project is
`build/ghidra/projects/buus_fury_calibration.gpr`. Open that local project for
GUI work; never place a Ghidra project beside tracked source.

After import, markup, or any other ROM-adjacent Ghidra work, re-identify the
read-only original and require the same verified profile:

```powershell
& '.venv\Scripts\webfoot.exe' identify 'roms\Dragon Ball Z - Buu''s Fury (U).gba'
```

## Validated import result

The loader selected `ARM:LE:32:v4t:default`, parsed the GBA cartridge header,
and created these blocks:

| Block | Range | Permissions / state |
|---|---|---|
| WRAMB | `0x02000000..0x0203FFFF` | RW, uninitialized |
| WRAMC | `0x03000000..0x03007FFF` | RW, uninitialized |
| IO | `0x04000000..0x040003FE` | RW, uninitialized |
| PALETTE | `0x05000000..0x050003FF` | RW, uninitialized |
| VRAM | `0x06000000..0x06017FFF` | RW, uninitialized |
| OAMOBJ | `0x07000000..0x070003FF` | RW, uninitialized |
| header | `0x08000000..0x080000BF` | R-X, initialized |
| rom | `0x080000C0..0x087FFFFF` | R-X, initialized |

The program image-base property remains zero even though the loader's ROM
blocks are correctly addressed at `0x08000000`. Use actual block addresses,
not the image-base property, for ROM-address reasoning. The IO block's concrete
end is `0x040003FE`; do not silently widen it. The loader created the
`GBA_CARTR_HEADER_08000000` data symbol and resolved the header branch to an
ARM function entry at `0x080000C0` (`TMode=0`).

Normal default auto-analysis was run with four CPUs and a 900-second per-file
limit. It timed out at 900 seconds but saved the imported program. Significant
costs included ARM Constant Reference (236.177 s), Decompiler Switch Analysis
(238.746 s), Non-Returning Functions (165.419 s), Reference (100.096 s), and
Create Address Tables (98.803 s). The log also contains repeated ARM/Thumb
context conflicts in non-target regions. Do not rerun full default analysis for
ordinary queries unless a ticket specifically needs it.

## Calibration result

Blind means normal auto-analysis before established entry-point markup.
Corrected means only the five established Thumb entries and the three known
point-query call instructions were seeded by `ApplyCalibrationMarkup.java`.

| Target | Blind result | Corrected result |
|---|---|---|
| Point query `0x080126D4` | `TMode=0`; no function or local disassembly | Boundary, field accesses, signed half-open comparisons, reverse scan, first-accept exit, and two-stage `+8` then `+4` indirect dispatch match established evidence. Parameter types remain generic. |
| Factory `0x08007674` | `TMode=1` and instructions recovered, but no function | Boundary, allocation `0x18`, calls, table reference `0x0804A09C`, descriptor retention at object `+0x14`, and descriptor byte handling match. The full common-initializer effects remain indirect. |
| Filter `0x08007768` | `TMode=0`; no function | Exact two-instruction function returns 1. |
| Action `0x080125E8` | `TMode=0`; no function | Boundary and one indirect dispatch through table offset `+4` match. Ghidra does not statically resolve that dispatch to `0x080075AC`. |
| Downstream `0x080075AC` | `TMode=0`; no function | Boundary and useful structural decompilation recovered; no callback-to-target xref was recovered. |

For the point query, Ghidra's inclusive byte body is
`0x080126D4..0x080127AD`; the final two-byte Thumb instruction starts at the
established inclusive instruction address `0x080127AC`. After seeding the three
established source instructions, entry xrefs are exactly `0x08006E4E`,
`0x08021DFE`, and `0x08021E06`. Their containing caller functions were not
recovered, so Ghidra reports `source_function=NONE`.

### Comparison classifications

- Point-query boundary, field offsets, coordinate shifts, signed bounds,
  half-open comparisons, reverse order, and first accepted exit: **MATCH**.
- Point-query parameter usage: **MATCH** structurally, with generic inferred
  types.
- Point-query two-stage callback shape: **MATCH**; concrete indirect targets:
  **PARTIAL**.
- Point-query direct callsites: blind **NOT RECOVERED**; after established
  callsite seeds **MATCH**.
- Factory boundary, allocation, direct calls, dispatch-table literal, and
  retained descriptor: **MATCH** after entry correction.
- Factory's complete initialized object semantics: **PARTIAL** because effects
  delegated to the common initializer were not reconstructed in one view.
- Filter body and return: **MATCH** after entry correction.
- Action body and indirect-dispatch shape: **MATCH** after entry correction.
- Static action-to-`0x080075AC` relationship: **NOT RECOVERED**. That relation
  remains established runtime evidence, not a Ghidra-derived claim.
- Downstream boundary and local structure: **MATCH** after entry correction;
  callback xrefs: **NOT RECOVERED**.

## Required Thumb procedure

1. Begin from a verified raw or fetch address and preserve both when the raw
   value has the Thumb bit set.
2. Check the `TMode` context and instruction alignment at the normalized fetch
   address. Never assume auto-analysis chose correctly.
3. Seed only entry points already established independently. Run
   `ApplyCalibrationMarkup.java` only after saving a blind report.
4. Treat inferred boundaries as candidates until instruction flow and other
   evidence agree. Ghidra's function body endpoints are byte-inclusive.
5. Disassemble known source call instructions when validating xrefs; seeding
   only the callee does not recover undisassembled callers.
6. Treat `FUN_08046aa2`, `FUN_08046aa4`, and `FUN_08046aa6` as indirect-call
   helpers, not as the semantic callback targets they dispatch to.
7. Keep Ghidra names conservative and evidence-qualified. Do not import
   external semantic symbol sets into the calibration project.

## Headless query

The tracked report script is read-only and emits no ROM bytes into the
repository. It reports program identity, memory blocks, function boundaries,
symbols, callers/callees, xrefs, disassembly, decompilation, and selected data
words to a caller-chosen ignored output path:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File 'tools\ghidra\run-calibration.ps1' `
  -GhidraInstallDir 'build\ghidra\apps\ghidra_12.1.2_PUBLIC' `
  -ProjectDir 'build\ghidra\projects' `
  -ProjectName 'buus_fury_calibration' `
  -ProgramName 'buus_fury_verified.gba' `
  -OutputPath 'build\ghidra\reports\calibration.txt'
```

`analyzeHeadless` can return exit code zero even when a post-script fails to
compile. The wrapper therefore also requires a freshly written report. Keep
report outputs under ignored `build/ghidra/reports/`; both the wrapper and the
Ghidra script reject output paths outside that directory. Both Ghidra scripts
also reject any program whose MD5, SHA-256, or language differs from the
canonical Buu's Fury profile and `ARM:LE:32:v4t`.

## Score and use policy

| Category | Rating |
|---|---|
| Thumb function discovery | POOR |
| Function boundaries | MIXED |
| Decompilation usefulness | EXCELLENT |
| Caller/xref accuracy | MIXED |
| Data-reference accuracy | GOOD |
| Signed comparison recovery | EXCELLENT |
| Indirect dispatch clarity | MIXED |
| Headless queryability | EXCELLENT |
| Time saved versus manual analysis | GOOD |
| Reliability for future evidence generation | MIXED |

Ghidra materially accelerates disassembly, decompilation, field-access review,
and repeatable queries once entry mode is independently anchored. It is not an
unattended function-discovery or semantic-labeling source for this ROM.

MCP preparation was not attempted. BSim is ready only as a separate, bounded
next experiment using already-known anchors, with results reviewed before any
name transfer. No broad BSim match or Data Crystal import was performed.
