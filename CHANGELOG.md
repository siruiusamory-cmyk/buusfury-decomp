# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed

- `docs/` is a reader's guide now. [docs/README.md](docs/README.md) says what the game's code is
  organised into, how to build it, how names are chosen and where to look next; the pages that were
  records of investigation rounds, censuses and play sessions have left the tree. The repository's
  history still carries them.
- `tools/` holds only what the build, the gate and the checks run, and [tools/README.md](tools/README.md)
  lists every entry with what it does and what runs it. The build's own scripts are under
  `tools/build/`; the tables and baselines a check reads live beside that check, under `tools/lint/`,
  `tools/research/` and `tools/recomp/`.
- The compressor is compiled from its own source. The jcalg1 MASM source (MIT) is vendored under
  `tools/compress/jcalg1/`, `tools/compress/build.cmd` builds it with the Visual Studio toolchain,
  and `rebuild.cmd` calls that when the binary is absent.

### Removed

- The committed `tools/compress/compress.exe`, which was the only compiled file the tree tracked.
- The research scripts that neither the build nor a check runs, their tests, and the census tables
  and process pages that no check reads. Each is still in the repository's history.

### Added

- `tools/README.md`, the one page that says what every remaining tool does and what runs it.
- `docs/README.md`, the entry point to the reader pages.

### Building

- The build needs Visual Studio or Build Tools 2022 with the C++ workload (`cl.exe`, `ml.exe`) and
  CMake 3.17 or newer, in addition to ARM Developer Suite 1.2, Python 3.12, grit and your own ROM.
  Use Visual Studio's `cmake.exe`; an MSYS2 build has no Visual Studio generator.
