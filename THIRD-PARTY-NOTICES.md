# Third-Party Notices

The Webfoot SDK and the other original code in this repository are licensed
under MPL-2.0; see [`LICENSE`](LICENSE).

**That root license does not relicense third-party material.** Each upstream
listed here keeps its own license and its own copyright holders. Where a file in
this repository incorporates or modifies third-party material, the upstream
license governs that material regardless of the root license.

This file records the upstreams that place an obligation on this repository or
that materially informed shipped code. Machine-pinned revisions for every
upstream the project consults live in [`upstreams.lock`](upstreams.lock), and
the per-upstream inspection record lives in
[`docs/upstream-audit.md`](docs/upstream-audit.md).

---

## DragonByteZ - MIT

- **Upstream:** <https://github.com/spicybung/DragonByteZ>
- **Pinned revision:** `b2691209fa873cc0c1d7aa9cdea7c1da4430afe4` (`upstreams.lock`)
- **Upstream license:** MIT, stated in the upstream root `LICENSE`.
- **Affected file in this repository:** `tools/webfoot/formats/webfoot_lz.py`

### What is incorporated

`tools/webfoot/formats/webfoot_lz.py` implements the Webfoot compression
container. Its bit grammar is a **cross-language derivative** of upstream
`src/compression.cpp` rather than an independent derivation, and the module says
so in its own docstring. Specifically, the match-length/distance ladder is
carried over from the upstream implementation: the thresholds (`0x10000`,
`0x37FF`, `0x027F`, `0x007F`) and their bias values are not derivable from first
principles and are reproduced deliberately.

The module's source-level provenance comments are the primary record of this and
are intentionally preserved. Do not remove them.

The Python implementation, its container/header handling, its encoder, its error
model, and its tests are this project's own work. Correctness was independently
verified against the canonical ROM before promotion: all 7,355 sprite containers
decode without failure, and every decoded length matches the width times height
that the referring piece record independently declares
(`docs/research/GRAPHICS_FORMAT.md`).

### Required notice

The following notice is reproduced from the upstream `LICENSE` in satisfaction
of the MIT license's condition that the copyright notice and permission notice
be included in all copies or substantial portions of the Software:

```
MIT License

Copyright (c) 2026 DragonByteZ contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## mGBA - MPL-2.0

- **Upstream:** <https://github.com/mgba-emu/mgba>
- **Version:** 0.10.5, upstream commit `26b7884bc25a5933960f3cdcd98bac1ae14d42e2`
  (pinned and documented in `tools/mgba_probe/README.md`)
- **Upstream license:** MPL-2.0, in the upstream `LICENSE`.
- **Upstream copyright:** mGBA is Copyright (c) 2013-2022 Jeffrey Pfau.
- **Affected file in this repository:**
  `tools/mgba_probe/mgba-0.10.5-log1-read-probe.patch`

### What is incorporated

The file is a unified-diff patch, not a redistribution of the mGBA tree. The
upstream checkout and any built emulator binary stay under ignored `extern/` and
`build/` and are not part of this repository.

The patch modifies these MPL-2.0-covered upstream files:

| Upstream file | Upstream copyright line |
| --- | --- |
| `include/mgba/internal/gba/gba.h` | Copyright (c) 2013-2016 Jeffrey Pfau |
| `src/debugger/gdb-stub.c` | Copyright (c) 2013-2016 Jeffrey Pfau |
| `src/gba/gba.c` | Copyright (c) 2013-2015 Jeffrey Pfau |
| `src/gba/memory.c` | Copyright (c) 2013-2016 Jeffrey Pfau |
| `src/gba/test/core.c` | Copyright (c) 2013-2016 Jeffrey Pfau |

Because it is a diff, the patch also carries unchanged upstream context lines
from those files. Both the context and the modifications to those files are
MPL-2.0-covered material.

### Licensing scope

MPL-2.0 is a file-level (weak) copyleft. The files listed above remain governed
by MPL-2.0 in both their upstream and their modified form. The root MPL-2.0
license of this repository does not supersede, relicense, or extend any
additional grant over mGBA material; it happens to be the same license, and that
coincidence changes nothing about which copyright holders govern those files.

Anyone redistributing the patch, or a build produced by applying it, is
redistributing modified MPL-2.0 Covered Software and takes on MPL-2.0's source
availability obligations for those files.

The upstream Exhibit A notice, present in the patched files themselves, is:

```
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
```

---

## BuusFuryToolkit - provenance evidence, no explicit license

- **Upstream:** <https://github.com/yoav74/BuusFuryToolkit>
- **Pinned revision:** `4353f6a23aa4ac980f1ed42a2c65bc281fa45cc7` (`upstreams.lock`)
- **Upstream license:** none identified by this project. `UNKNOWN`
  (`docs/upstream-audit.md`).
- **Affected file in this repository:** `tools/webfoot/formats/stat_tables.py`

### What was used, and what was not

No BuusFuryToolkit implementation was copied, and this project claims no
redistribution rights over any BuusFuryToolkit material. Nothing from that
upstream is vendored into this repository.

What was used is **layout and naming evidence**: the header lines of the
upstream's `Enemies.txt` and `Base Stats.txt` state field orders, and the
upstream README documents the `ROM offset + 0x08000000` addressing convention.

The corresponding behavior was independently verified against the canonical
local ROM before the module was written (DATA-001). The verified extent, record
stride, and field decode were established by reading the ROM directly - upstream
lists named offsets individually and never states where either table begins or
ends, so the bounds in this repository are this project's measurement, not the
upstream's word.

Semantics stay labelled by evidence level, per `docs/DEVELOPMENT.md`:

- `CONFIRMED` - record stride, table extent, and field decode, established from
  the canonical ROM.
- `INFERRED` - the human-readable *names* attached to individual records. Those
  come from BuusFuryToolkit's author and were not re-derived. The numbers are
  trustworthy; a name is a label of convenience.

Because the upstream has no explicit license, this repository depends on it only
as documentation consulted during research, not as a source of code or data.

---

## Game content

This repository contains no commercial ROMs, BIOS images, saves, states, memory
dumps, or extracted proprietary game assets, and none have ever been committed.
The Dragon Ball Z games and all of their content remain the property of their
respective rights holders; this project is unaffiliated with them. Supply only
game images you are legally entitled to use.
