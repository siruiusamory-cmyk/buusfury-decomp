# Build

Prerequisites: ARM Developer Suite 1.2 (`armasm`, `armcpp`, `armlink`, `fromelf`), Python 3.12 on `PATH`, grit (devkitPro), and the retail ROM as `baserom.gba` in this directory. `rebuild.cmd` defaults `ADS` to an ADS 1.2 Build 805 install beside this checkout's parent directory; set `ADS` to use another installation. `tools\assets\generate_assets.py` finds grit on `PATH`, through `GRIT`, or through `DEVKITPRO`. The ROM's sha1 must equal `baserom.sha1`; `extract.cmd` refuses anything else.

```
extract.cmd
rebuild.cmd
python tools\gate\gate.py
```

`gate.py` rebuilds from scratch, purges every object first, and prints `DIGEST MATCH` and `GATE PASS` when the image equals the retail sha256. It also accounts for every byte of the image from the source tree:

```
source=<B> of 8388608 (<%>)                          code and data built from tracked source or a byte-exact generator
raw-data=<B> (<%) cited <B> / runtime-cited <B> /
                   unreferenced <B>                  bytes the assembler still embeds from extracted slices
accounted=<B> of 8388608 (<%)                        source plus raw-data; 100 % when every byte is in one
```

`source` is the image size minus the bytes `asm/*.s` INCBINs, so it cannot drift from what the assembler reads. The raw-data split comes from `tools\research\citations_in_source.py` (`docs\research\RAW_CITATIONS.csv`): `cited` is the share a code-row citation site reaches, `runtime-cited` a carrier comment's runtime read, the rest `unreferenced`.

A carrier comment's own site list is not a channel (P-453), so 132 rows / 14,857 B stay `unreferenced`. The cited share is an upper bound while instruction boundaries are unproven. `docs\research\INCBIN_CENSUS.md` carries the per-row evidence.

The gate prints `TIMING <stage> <seconds>s misses=<n> budget=<b>s PASS|BREACH` and fails on a breach; stages are `warm` (10 s), `edit` (15 s), `cold`, `materialise` and `partial` (300 s). `python tools\gate\gate.py --cold` performs the whole cold procedure against an isolated cache. The encode cache is machine-wide at `%LOCALAPPDATA%\buusfury-decomp\encode-cache`, overridden by `BUUSFURY_ENCODE_CACHE`.

To prove that a build input drives the bytes it claims to:

```
python tools\gate\perturb_check.py --file assets\mapcontainer\payloads.store ^
  --old-hex 0000000000000000000000006901000000000000000000000000000000000000 ^
  --new-hex 0000000000000000000000006a01000000000000000000000000000000000000 ^
  --offset 0x19BC6A --before 60 --after a0
```

A binary input takes `--old-hex`/`--new-hex`, a text input `--old`/`--new`; the window must occur once. `misses base=0 edit=0 restore=0` means the cache still holds the edited payload's entry: delete that entry (named by the edited payload's sha256) and re-run.

`extract.cmd` writes the eight image payloads under `assets\generated\`, two palettes and six payload stores under `build\` and `assets\*` - all regenerated from `baserom.gba` and none tracked. `tools\assets\generate_assets.py` decodes the payloads, `rebuild.cmd` re-encodes each with grit and `tools\compress\compress.exe` and refuses an output that is not the retail extent's bytes; `tools\extract\extract.py` writes the palettes. `rebuild.cmd` makes most `baserom.gba_0x..._0x....extracted` slices through `tools\incbin.bat`, and `extract.cmd`'s last step, `tools\research\rawlabeled.py --extract`, writes the same kind of slice for every tracked raw fragment.

The map-container, sprite, end-of-ROM and structured generators write their own retail gaps and generated runs instead (thousands of PowerShell calls would otherwise be paid per rebuild). `build.bat` is the legacy build; it calls the same image generator.

Each of the 187 tile banks is `assets\tilebank\bank_NNN_XXXXXX.png`, an 8x8 8bpp tile sheet, 16 tiles across, one pixel per payload byte, palette in the PNG. `extract.cmd` writes the sheets; edit a pixel in an 8-bit indexed, non-interlaced PNG and `rebuild.cmd` re-encodes the container, refusing a size that disagrees with its manifest row. Re-running `extract.cmd` overwrites edits.

Tools: `tools\tilebank\`, `tools\mapcontainer\`, `tools\structured\` (payload libraries, generators, round-trip tests), `tools\encode_cache.py` (the machine-wide encode store), `tools\payload_store.py` (one packed file per payload block), `tools\webfoot\webfoot_lz.py` (the Webfoot container codec), `tools\gate\gate.py` and `tools\gate\perturb_check.py`, and `tools\research\rawlabeled.py` (labeled raw data, `--extract`, `--name-rows`).

Formatting and the pre-commit hook are in [CONTRIBUTING.md](CONTRIBUTING.md); the hook is opt-in with `git config core.hooksPath .githooks`.
