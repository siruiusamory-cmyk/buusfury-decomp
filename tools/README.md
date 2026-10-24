# tools

Everything here is run by the build, by the gate, or by a check. Nothing else lives in this folder.
`extract.cmd` decodes the assets from your own ROM, `rebuild.cmd` assembles and re-encodes the
image, and `python tools\gate\gate.py` proves the result against the retail sha256. CI runs
`tools/check_links.py` and `tools/lint/lints.py`, and the pre-commit hook runs the same two.

## Top level

| file | what it does | what runs it |
| --- | --- | --- |
| `README.md` | this page | - |
| `check_links.py` | fails on a markdown link that does not resolve, or on a commit id cited in a page | CI, pre-commit hook |
| `test_check_links.py` | the tests for `check_links.py` | CI |
| `testkit.py` | helpers for the ROM-gated tests: skip when the ROM is absent, assert a refusal | `behaviour/test_table.py`, `behaviour/test_names.py` |
| `incbin.bat` | cut one ROM range into a `baserom.gba_0x…_0x….extracted` slice | `extract.cmd`, `rebuild.cmd` fallbacks |
| `encode_cache.py` | the machine-wide encode store, one entry per payload and encoder | `gate/gate.py`, the emitters |
| `payload_store.py` | one packed store file per payload block, read by the emitters | `mapcontainer/`, `structured/`, `tilebank/`, `build/` |
| `emitted.py` | the generated-run registry the gate reads its emitter evidence from | `gate/gate.py`, `mapcontainer/`, `build/rawlabeled.py` |
| `intervals.py` | byte-interval helpers shared by the container generators | `mapcontainer/mapcontainer.py`, `structured/families.py` |
| `recordfamily.py` | the record-family interface (fields, serialize, round trip) the record modules implement | `mapcontainer/`, `spritecontainer/` |
| `romfile.py` | opens the private ROM copy and reads words, halfwords and bytes at file offsets | the generators, `behaviour/harness.py`, `research/` |

## compress/

| file | what it does | what runs it |
| --- | --- | --- |
| `main.cpp` | the compressor driver: reads a payload, writes the kind-1 container the assembly expects | `rebuild.cmd`, `gate/emit_all.py` |
| `CMakeLists.txt` | builds `compress.exe` from `main.cpp` and the jcalg1 MASM source | `build.cmd` |
| `build.cmd` | finds the Visual Studio cmake, builds the compressor and copies it beside the driver | `rebuild.cmd`, `build.bat` |
| `jcalg1/` | the jcalg1 r5.32 compressor and the `JCALG1_GetUncompressedSizeOfCompressedBlock` helper, MASM source plus the MIT licence | `CMakeLists.txt` |

## extract/ and assets/

| file | what it does | what runs it |
| --- | --- | --- |
| `extract/extract.py` | writes the two palettes and the six payload stores from the ROM | `extract.cmd` |
| `extract/slice_rom.py` | writes one `baserom.gba_0x…_0x….extracted` slice | `incbin.bat` |
| `assets/generate_assets.py` | decodes the eight images to PNG, then re-encodes them with grit and the compressor | `extract.cmd`, `rebuild.cmd`, `build.bat` |

## gate/

| file | what it does | what runs it |
| --- | --- | --- |
| `gate.py` | runs the lints and the census check, purges the objects, rebuilds, and proves the image digest and the byte accounting | you, and CI documents it as the gate |
| `build_cache.py` | caches the two large assembly units by a digest of their inputs | `rebuild.cmd` |
| `emit_all.py` | runs every section emitter and reports each one's exit and encode counts | `rebuild.cmd` |

## lint/

| file | what it does | what runs it |
| --- | --- | --- |
| `lints.py` | the naming, layout, hardware-literal, ROM and README-number checks | CI, pre-commit hook, `gate/gate.py` |
| `ASM_INDEX.csv` | one row per function start: address, kind, symbol, file | `lints.py` |
| `NAMING_LEDGER.csv` | one row per promoted name, with its evidence | `lints.py`, `recomp/export_inputs.py`, `research/name_evidence.py` |
| `NAMING_BASELINE.txt`, `NAMING_RETIRED.csv` | the address-named ratchet and the retired names | `lints.py` |
| `HARDWARE_BASELINE.txt`, `RAM_BASELINE.txt` | the admitted raw hardware and RAM literal counts | `lints.py` |
| `BF_LABELS.toml` | the recompiler label export the naming check reads | `lints.py` |
| `RESIDUAL_LEDGER.csv` | the raw-data ledger the README's identified-binary figure comes from | `lints.py` |

## build/

| file | what it does | what runs it |
| --- | --- | --- |
| `generate_jcalg1.py` | emits the packed containers the assembly still carries, from a stored payload and the tree's own compressor | `extract.cmd`, `gate/emit_all.py` |
| `opcode_stream.py` | decodes the opcode streams the map entries name and emits the runs byte-exactly | `extract.cmd`, `gate/emit_all.py` |
| `rawlabeled.py` | writes the extracted slice every tracked raw fragment names | `extract.cmd` |

## mapcontainer/ and spritecontainer/

| file | what it does | what runs it |
| --- | --- | --- |
| `mapcontainer/generate_mapcontainer.py` | extract, emit and verify the map block, sprite block, end-of-ROM, sprite-defs and asset-directory containers | `extract.cmd`, `gate/emit_all.py` |
| `mapcontainer/generate_assetdir3.py` | emits the asset-directory-3 script bank from its parse | `extract.cmd`, `gate/emit_all.py` |
| `mapcontainer/mapcontainer.py` | the container block machinery: offsets, fields, serialize, member roots | the two emitters |
| `mapcontainer/animframe.py` | carries an animation frame as an indexed PNG and proves the retail stream back | `gate/emit_all.py` |
| `mapcontainer/animrow.py` | the `map_anim_row` family: the root list, the row fields and the emitted rows | `animframe.py` |
| `mapcontainer/assetdir3.py` | the directory-3 descriptor, its consumer and its stream machine | `generate_assetdir3.py`, `rawlabeled.py` |
| `mapcontainer/assetdirectory.py` | the asset-directory PCM stream, decoded and re-encoded | `mapcontainer.py` |
| `mapcontainer/assetdir.py`, `assetdir2.py` | the two asset-directory block descriptors | `mapcontainer.py` |
| `mapcontainer/ainodes.py` | the AI-node row table and the targets its words name | `mapcontainer.py` |
| `mapcontainer/cellmap.py`, `enemystats.py`, `globalstate.py`, `glyphtable.py`, `rowtable.py` | one record family each: fields, serializer and round trip | `mapcontainer.py` |
| `mapcontainer/eventindex.py`, `eventpool.py`, `pairsprite.py` | the event index and pool, and the sprite pair table | `mapcontainer.py` |
| `mapcontainer/endrombank.py`, `endromcontainer.py`, `endromfacing.py`, `endromrecords.py` | the end-of-ROM families and their packed containers | `mapcontainer.py` |
| `mapcontainer/*_manifest.csv` | the per-container payload sizes and names the emitters check | the two emitters |
| `spritecontainer/spritecontainer.py` | the sprite family's containers | `mapcontainer.py` |
| `spritecontainer/spritefamily.py` | the sprite family's record runs | `mapcontainer.py` |
| `spritecontainer/def50.py` | the sprite-definition-5.0 arrays and cell grids | `mapcontainer.py` |
| `spritecontainer/spritecontainer_manifest.csv` | the sprite containers' payload sizes | the two emitters |

## structured/, tilebank/, text/, assetrecords/, symbols/

| file | what it does | what runs it |
| --- | --- | --- |
| `structured/generate_structured.py` | extract, emit and verify the eight structured families | `extract.cmd`, `gate/emit_all.py` |
| `structured/families.py` | the families' layouts, serializers and round trip | `generate_structured.py`, `build/opcode_stream.py` |
| `tilebank/generate_tilebank.py` | extract, emit and verify the 187-container tile-bank block | `extract.cmd`, `gate/emit_all.py` |
| `tilebank/tilebank.py` | the tile bank's decode and encode | `generate_tilebank.py` |
| `tilebank/pngsheet.py` | one PNG sheet per tile bank, and back | `generate_tilebank.py` |
| `tilebank/tilebank_manifest.csv` | the tile banks' extents and sizes | `generate_tilebank.py` |
| `text/strings_table.py` | builds `build/strings.cpp` from the string tables | `gate/emit_all.py` |
| `text/strings_layout.json` | the string-table layout the builder reads | `strings_table.py` |
| `assetrecords/records_table.py` | emits the end-of-ROM and music record tables | `gate/emit_all.py` |
| `assetrecords/*_layout.json` | the record layouts those tables are emitted from | `records_table.py` |
| `symbols/generate_symbols.py` | emits the link's symbol list from the assembler and linker output | `rebuild.cmd` |

## webfoot/

| file | what it does | what runs it |
| --- | --- | --- |
| `webfoot_lz.py` | the Webfoot packer's decoder, and a validator for a packed extent | `mapcontainer/`, `build/` |

## research/

These are the readers the gate and the build import. `function_bounds.py` is also run on its own, by
the gate, as the census check.

| file | what it does | what runs it |
| --- | --- | --- |
| `function_bounds.py` | decides which exported address starts a function and which is an interior block, and checks the census | `gate/gate.py --check` |
| `FUNCTION_BOUNDS.csv`, `FUNCTION_ENTRY_ALLOW.csv` | the census and the allow list with a reason per entry | `function_bounds.py`, `lints.py` |
| `incbin_census.py` | splits the raw-data bytes into the regions the gate accounts for | `citations_in_source.py` |
| `citations_in_source.py` | measures the cited, runtime-cited and unreferenced share of the raw data | `gate/gate.py` |
| `code_xref.py` | finds the code sites that name an address in a range | `citations_in_source.py`, `rawlabeled.py` |
| `loader_access_trace.py` | what the code does with a pointer into a range: field offsets, stride and index use | `rawlabeled.py` |
| `unknown_consumer_search.py` | the widened consumer search for a range the census still calls unproven | `loader_access_trace.py` |
| `name_evidence.py` | the hardware accesses and literals of one function, used as naming evidence | `function_bounds.py` |
| `class_tables.py` | the class tables the image stores at `[object+0]`: each table's slots, its next stored table and the rows that install it, written and checked from the image | you, and the naming audit |
| `CLASS_TABLES.csv` | one header row per class table and one row per slot, with the target each slot reaches | `class_tables.py`, `name_evidence.py` |
| `bios_block_scan.py` | self-delimiting blocks and uniform fill runs in an image | `generate_jcalg1.py` |
| `jcalg1.py` | the JCALG1 body decoder | `generate_jcalg1.py` |
| `rawlabeled_3bbe70_bounds.txt` | the ten-byte record boundaries the carrier split cites | cited by `incbin_census.py` |

## behaviour/

| file | what it does | what runs it |
| --- | --- | --- |
| `harness.py` | runs one transcribed function from a private image copy on crafted registers and memory, and records its stores and calls | the two test files below |
| `test_table.py`, `test_names.py` | the behaviour tests 82 naming-ledger rows cite | pytest, and `lint/lints.py` checks that every cited test exists |

## recomp/

| file | what it does | what runs it |
| --- | --- | --- |
| `export_inputs.py` | derives the recompiler's entry list from the census, the labels and the image's own targets | `research/function_bounds.py`, `test_export_inputs.py` |
| `RECOMP_INPUTS.toml` | that entry list, checked by the tool | `export_inputs.py --check` |
| `RUNTIME_LABELS.csv` | the runtime-recorded labels the export adds | `export_inputs.py` |
| `test_export_inputs.py` | the tests for the export | pytest |
