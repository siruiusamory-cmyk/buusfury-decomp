# ROM-011 mGBA native read probe

This directory tracks the narrow LOG1 instrumentation applied to upstream mGBA
`0.10.5` commit `26b7884bc25a5933960f3cdcd98bac1ae14d42e2`. The full upstream checkout and
generated executable remain ignored under `extern/` and `build/`.

## Architecture

The patch adds one probe state to the GBA core. Normal disarmed EWRAM reads pay
one predicted branch. An arm request names dynamic object X, load epoch,
descriptor, and exact factory identity. Only CPU instruction reads with a real
cycle counter are eligible; DMA and debugger/view reads are excluded.

Eligible CPU accesses use mGBA's bus-aligned physical span for half-open overlap
against `[X+0x04,X+0x10)` and `[X+0x14,X+0x18)`. The event still retains the
instruction's original logical address and width plus the exact physical
overlap. `LDM` transfers are covered separately because mGBA does not route
them through `GBALoad32`.

First match copies fixed CPU/event fields, disarms before returning, and pauses
through the already-attached GDB stub. Formatting happens only when Python asks
for `qLog1ProbeEvent`; acknowledgement is explicit. No generic debugger memory
shim, watchpoint list scan, socket call, allocation, logging, or formatting runs
on an ordinary memory read.

Control packets are project-specific GDB queries:

- `qLog1ProbeArm:<sequence>,<X>,<epoch>,<descriptor>,<factory_raw>,<factory_fetch>,<profile_sha256>`
- `qLog1ProbeDisarm:<sequence>`
- `qLog1ProbeEvent`
- `qLog1ProbeAck:<event_id>`

The SDL frontend retains upstream `--gdb` and `--savestate` command-line startup.
No Lua scripting or Windows UI automation is part of the native workflow.
The patch also balances `SocketSubsystemInit`/`SocketSubsystemDeinit` inside the
GDB stub. This is required by the standalone Windows SDL frontend; Qt happens
to initialize Winsock elsewhere, while SDL does not.

## Build

Prerequisites:

- clean upstream checkout at the exact commit above
- Visual Studio 2022 C++ Build Tools and CMake for `-CoreOnly`
- an isolated official MSYS2 x64 tree at ignored `build/rom011/deps/msys64`
- MSYS2 MinGW64 packages: GCC, CMake, Ninja, pkgconf, SDL2, libepoxy, libpng,
  and zlib

Run:

```powershell
.\tools\mgba_probe\build.ps1
```

The helper verifies the source commit and patch, configures a static non-LTO
SDL build with scripting, Qt, Discord RPC, and unrelated optional integrations
disabled, builds `mgba-sdl.exe`, verifies version output, and writes the exact
compiler/CMake/package versions, runtime DLL path, build options, patch hash,
and executable hash to an ignored manifest beside the executable. `-CoreOnly`
uses MSVC, omits SDL, and separately compiles the modified GDB transport.

The commercial ROM, saves, and states are never build inputs. Runtime launch
still verifies their configured hashes before making ignored working copies.
