# Release artefacts

What a user receives from this project, how it is produced, and what must never
travel with it. This is the release-facing half of the documentation: the
engineering rules behind it live in [`DEVELOPMENT.md`](DEVELOPMENT.md), the
safety contract in [`ROM_SAFETY.md`](ROM_SAFETY.md) and the format in
[`project-format.md`](project-format.md).

## The two artefacts

A creator produces two different things, and confusing them is the most common
way a distribution goes wrong.

| Artefact | What it is | Who it is for |
| --- | --- | --- |
| **The built image** | the modified ROM itself, byte for byte | the author, on their own machine |
| **The patch** | a small `.bps` file that reproduces that image from the verified base ROM | everybody else |

You **distribute the patch**. The built image contains the publisher's work in
full, so it is the same legal object as the original ROM and is never uploaded,
shared or committed anywhere.

## Exporting a patch

```powershell
webfoot patch export ".\work\my-mod" --rom ".\roms\Dragon Ball Z - Buu's Fury (U).gba" --output ".\build\my-mod.bps"
```

The command line above is the shape, not a canned path: replace the ROM name with
the image you actually hold.

What the export does, in order:

1. it identifies the source image against the profile catalog and refuses
   anything that is not **exactly** the catalogued image;
2. it refuses an output path that is the source image, or that already exists;
3. it builds the project, using the same build path `webfoot build` uses;
4. it encodes the patch, applies it back in memory, and refuses to publish if the
   result is not the image that was built;
5. it reads the published file back from disk, applies it again, and only then
   reports success.

The patch records the CRC-32 of both images, so an applier refuses a source ROM
the patch was not made for, and refuses a patch whose own bytes are damaged.

To check an existing patch against a ROM without writing anything:

```powershell
webfoot patch verify ".\build\my-mod.bps" --rom ".\roms\...gba"
```

A project that builds to an image identical to its base produces no patch at all:
there is nothing to reproduce, and the command says so instead of writing an empty
one.

## What the patch contains, and what it does not

The patch is a difference, not a copy. Unchanged regions are re-read from the
source ROM on the other side of the patch, so the file is typically a small
fraction of an 8 MiB image. It cannot rebuild the image without the source ROM,
and it is the source ROM that stays with the person who owns it.

The literal bytes a patch does carry are the bytes that differ **and the bytes a
rebuild moved to a new offset**. A build that relocates a table, expands an array
or appends a chunk template writes canonical bytes at a new address, and a patch
has to reproduce them. That is inherent to every difference-based patch format,
it is a small subset of the image rather than the image, and it is why the patch
is a distribution of a modification and never a distribution of the game.

The provenance record is a short JSON document inside the patch. It names the
base profile and its SHA-256, the rebuilt image's SHA-256 and CRC-32, the project
name and format version, and the version and build of the tool that produced it.
It carries no path, no user name and no timestamp, so two exports of one project
from one build of the tool produce byte-identical files. `webfoot patch verify`
checks that record against the images it actually rebuilt and refuses a patch whose
record disagrees with its own bytes.

## Supported base ROMs

The source must be identified **VERIFIED** against `config/roms.yaml`. That is the
same gate the extract, validate and build commands use; a patch path does not get
a second, weaker identity rule. An uncatalogued image, a modified image, or an
image of the wrong revision is refused before anything is read or written.

The identity the patch records is the profile id, the image's SHA-256 and its
CRC-32. The SHA-256 is the project's own pinned base identity; the CRC-32 is what
the patch format carries for an applier.

## Version and build identity

There is one authority: `tools/webfoot/release_identity.py`.

```powershell
python -m tools.webfoot.release_identity            # the product and build identity
python -m tools.webfoot.release_identity --json     # the same, as a document for tooling
```

* `PRODUCT_VERSION` is the product version and nothing else writes it; a test
  fails if the string appears a second time in the shipped package.
* `VERSION_TUPLE` is the same version in the four-number form a Windows version
  resource requires.
* The version is deliberately a pre-release identity. v1.0 is a decision, and
  "version and build identity are visible" is one of the gates listed in
  [`ROADMAP_TO_1_0.md`](ROADMAP_TO_1_0.md).

A **checkout** reports the commit it is standing on, and whether the tree has
uncommitted changes. A **packaged** build has no repository to ask, so it reports
the identity baked in when it was packaged:

```powershell
python -m tools.webfoot.release_identity --write-record
```

That writes `tools/webfoot/_build_identity.py`, which is ignored by git and is
regenerated by the packaging scripts on every build, so a scripted release cannot
report a commit from an earlier build. A package built without it reports the
build as unknown rather than inventing a commit; the read never starts a process,
because a packaged build that shelled out to `git` could find an unrelated
repository through its working directory and record a commit that did not produce
it.

## Packaging the application

The current state, stated plainly: the desktop surfaces in this repository
(`tools/webfoot/workbench`, the two randomizers) are engineering and reference
tools. They demonstrate the SDK and the workflow, and they are not the future
DragonByte Z application, which is being built as its own product over the same
SDK. This section therefore describes the reusable packaging foundation that
exists, and says which part of a final release it does not yet cover.

What exists and is checked:

| Concern | Where it lives |
| --- | --- |
| the release definition of a public executable | `tools/quality/public_release.py`, one product list, checked by `python -m tools.quality.public_release` |
| a packaging template that names a real entry script and real data files | the same guard, which fails on a definition that names something absent |
| one version source, and an archive named from the product's own version | `tools/webfoot/release_identity.py` and the release tests |
| a census of a staged package directory | `python -m tools.quality.package_content <directory>` |
| the byte probe that searches a built executable for the canonical image | `scripts/randomizer-release.ps1`, run by each packaging script |
| build identity baked into a package | `scripts/build-*.ps1`, before PyInstaller runs |

The census is the portable half of the release-content check. It reports every
ROM, save or save state in a staged directory **by its extension**, every machine
path or user name in a text file, and every declared resource that is not staged,
and it prints what it cannot see along with what it found:

```powershell
python -m tools.quality.package_content .\dist\My-Product-release --require tools/webfoot/data/roms.yaml
```

It cannot see inside a compressed PyInstaller executable. That limit is printed
with every report, and it is why the packaging-time byte probe exists as well: a
clean census is not by itself the claim that an executable is free of private
bytes.

What a final DragonByte Z release still needs, and does not have yet: the
application's own package definition, its entry point, its visible About and
version surface, and the resource list its packaged build must carry. Those belong
to the new application, and its packaging is deferred to it rather than
approximated by shipping an engineering surface under the product's name.

### The owner-run release gate

PyInstaller does not cross-compile to win64, and the byte probe needs the
canonical image, so a frozen Windows build cannot run in the Linux CI job. CI
proves the portable facts above; the executable itself is an owner-run gate, run
in this order, with the artifact digests recorded alongside the release:

```powershell
pwsh scripts/build-<product>.ps1 -Clean      # bakes the build identity, freezes the executable
pwsh scripts/smoke-<product>-packaged.ps1    # drives the real executable, not a fixture
pwsh scripts/package-<product>.ps1           # stages, probes and archives
```

Do not claim byte-identical **executable** bytes. PyInstaller's archive carries
per-entry timestamps, the PE carries build metadata, and the toolchain is floored
rather than pinned, so the container is not reproducible and nothing here claims it
is. What is reproducible is the product content: the same verified base ROM, the
same project and the same toolkit produce a byte-identical image, and the same
input pair produces a byte-identical patch from one build of the tool, because an
exported patch names the tool build that produced it while a built image does not.

## First-run prerequisites

* A legally obtained ROM, kept outside version control. The ignored `roms\`
  directory is the usual place, and the canonical image is never modified.
* For the desktop editor, the assembled atlas at `build\atlas\atlas.jsonl`; it
  refuses every ROM without one. `webfoot atlas regenerate` produces it from a
  local ROM.
* An emulator (mGBA) for the Run action only. It is never required to build.

A packaged application does not require a repository checkout, a Python
installation, `uv` or a virtual environment. A source checkout does: see
[`../README.md`](../README.md) for the developer setup.

## What must never be committed or distributed

* the canonical ROM, any derivative ROM, and any generated image;
* saves (`.sav`), save states (`.ss*`), and emulator state of any kind;
* extracted graphics, which are the publisher's artwork;
* any build output: `build/`, `dist/`, `*.spec`, `*.exe`, `*.bps`;
* a package that has not been censused and probed.

The first four groups are ignored by git and screened three independent ways: the
tree-wide public-surface screen, the release-definition guard, and the
packaging-time byte probe. `tools/quality/package_content.py` is the fourth, for a
staged directory; run it before calling a package a release.
