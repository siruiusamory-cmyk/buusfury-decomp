# Test cost audit

LEAN-TEST-002, measured 2026-10-17 in a fresh worktree, one file per process at below-normal priority: `ids run` is passed + failed + error + skipped/xfail. Six files are red on a bare checkout because they read the build, not the sources. Whole-suite runs are CI-only.

## 1. What the tests cost

| file | ids run | passed | failed | error | skipped/xfail | pytest s | wall s |
|---|---|---|---|---|---|---|---|
| `tools/gate/test_emit_all.py` | 4 | 4 | 0 | 0 | 0 | 6.03 | 10.38 |
| `tools/gate/test_gate.py` | 22 | 22 | 0 | 0 | 0 | 0.99 | 4.40 |
| `tools/lint/test_lint.py` | 44 | 44 | 0 | 0 | 0 | 3.21 | 4.77 |
| `tools/mapcontainer/test_ainodes.py` | 5 | 5 | 0 | 0 | 0 | 2.31 | 3.94 |
| `tools/mapcontainer/test_assetdir.py` | 5 | 5 | 0 | 0 | 0 | 7.16 | 13.75 |
| `tools/mapcontainer/test_assetdir2.py` | 6 | 6 | 0 | 0 | 0 | 2.54 | 9.96 |
| `tools/mapcontainer/test_assetdir3.py` | 13 | 13 | 0 | 0 | 0 | 0.92 | 2.60 |
| `tools/mapcontainer/test_endrom.py` | 15 | 14 | 1 | 0 | 0 | 14.63 | 16.60 |
| `tools/mapcontainer/test_enemystats.py` | 5 | 5 | 0 | 0 | 0 | 0.92 | 2.62 |
| `tools/mapcontainer/test_eventindex.py` | 5 | 5 | 0 | 0 | 0 | 9.69 | 19.39 |
| `tools/mapcontainer/test_eventpool.py` | 5 | 5 | 0 | 0 | 0 | 1.14 | 2.68 |
| `tools/mapcontainer/test_globalstate.py` | 5 | 5 | 0 | 0 | 0 | 2.00 | 3.19 |
| `tools/mapcontainer/test_mapcontainer.py` | 6 | 6 | 0 | 0 | 0 | 25.74 | 27.33 |
| `tools/mapcontainer/test_maprecords.py` | 9 | 8 | 0 | 1 | 0 | 19.46 | 21.07 |
| `tools/mapcontainer/test_members_store.py` | 4 | 4 | 0 | 0 | 0 | 10.45 | 11.89 |
| `tools/mapcontainer/test_rowtable.py` | 3 | 3 | 0 | 0 | 0 | 6.72 | 8.39 |
| `tools/match/test_compare_rows.py` | 4 | 4 | 0 | 0 | 0 | 1.11 | 3.14 |
| `tools/research/test_arm_tools.py` | 18 | 18 | 0 | 0 | 0 | 1.32 | 2.88 |
| `tools/research/test_bios_block_scan.py` | 14 | 14 | 0 | 0 | 0 | 0.76 | 2.31 |
| `tools/research/test_citations_in_source.py` | 7 | 7 | 0 | 0 | 0 | 0.81 | 2.35 |
| `tools/research/test_code_band.py` | 4 | 4 | 0 | 0 | 0 | 1.25 | 2.79 |
| `tools/research/test_code_xref.py` | 7 | 7 | 0 | 0 | 0 | 0.70 | 2.31 |
| `tools/research/test_consumer_search.py` | 4 | 4 | 0 | 0 | 0 | 0.92 | 2.56 |
| `tools/research/test_fill_promote.py` | 11 | 11 | 0 | 0 | 0 | 0.74 | 2.28 |
| `tools/research/test_generate_jcalg1.py` | 23 | 23 | 0 | 0 | 0 | 1.32 | 8.29 |
| `tools/research/test_incbin_census.py` | 7 | 7 | 0 | 0 | 0 | 94.13 | 96.40 |
| `tools/research/test_jcalg1.py` | 8 | 8 | 0 | 0 | 0 | 1.29 | 3.01 |
| `tools/research/test_loader_access_trace.py` | 8 | 8 | 0 | 0 | 0 | 0.85 | 2.44 |
| `tools/research/test_packer_fit.py` | 6 | 6 | 0 | 0 | 0 | 7.08 | 8.88 |
| `tools/research/test_pointer_rows.py` | 8 | 8 | 0 | 0 | 0 | 0.60 | 2.05 |
| `tools/research/test_rawlabeled.py` | 30 | 26 | 4 | 0 | 0 | 7.77 | 12.21 |
| `tools/research/test_split_ledger.py` | 5 | 5 | 0 | 0 | 0 | 8.94 | 11.10 |
| `tools/research/test_text_tables.py` | 11 | 10 | 1 | 0 | 0 | 5.51 | 8.07 |
| `tools/research/test_thumb_annotate.py` | 3 | 3 | 0 | 0 | 0 | 0.63 | 2.05 |
| `tools/research/test_thumb_bodies.py` | 18 | 18 | 0 | 0 | 0 | 0.99 | 2.27 |
| `tools/research/test_thumb_tools.py` | 20 | 19 | 0 | 0 | 1 | 1.66 | 3.18 |
| `tools/research/test_transcribed_data.py` | 9 | 8 | 1 | 0 | 0 | 44.63 | 48.25 |
| `tools/research/test_unknown_consumer_search.py` | 5 | 5 | 0 | 0 | 0 | 0.56 | 1.91 |
| `tools/spritecontainer/test_def50.py` | 4 | 4 | 0 | 0 | 0 | 6.45 | 8.22 |
| `tools/spritecontainer/test_spritecontainer.py` | 2 | 1 | 1 | 0 | 0 | 8.22 | 12.30 |
| `tools/spritecontainer/test_spritefamily.py` | 6 | 6 | 0 | 0 | 0 | 1.79 | 3.47 |
| `tools/structured/test_structured.py` | 14 | 13 | 0 | 0 | 1 | 6.20 | 8.77 |
| `tools/symbols/test_symbols.py` | 12 | 12 | 0 | 0 | 0 | 3.44 | 5.13 |
| `tools/test_encode_cache.py` | 6 | 6 | 0 | 0 | 0 | 11.79 | 13.61 |
| `tools/tilebank/test_tilebank.py` | 11 | 9 | 0 | 0 | 2 | 15.77 | 17.11 |
| **45 files** | **441** | **428** | **8** | **1** | **4** | **351.1** | **462.3** |

### Six files are red on a bare checkout, because they read the build, not the sources

| file | before the build | artifact it needs | after the build |
|---|---|---|---|
| `tools/mapcontainer/test_endrom.py` | 1 failed, 14 passed | `build\endrom\*.bin`, `baserom.gba_*.extracted` | 15 passed |
| `tools/mapcontainer/test_maprecords.py` | 8 passed, 1 error | `assets\mapcontainer\payloads.store` | 9 passed |
| `tools/research/test_rawlabeled.py` | 4 failed, 26 passed | `baserom.gba_0x*_0x*.extracted` | 30 passed |
| `tools/research/test_text_tables.py` | 1 failed, 10 passed | `build/buu.map` | 11 passed |
| `tools/research/test_transcribed_data.py` | 1 failed, 8 passed | `build/output/symbols.json` | 9 passed |
| `tools/spritecontainer/test_spritecontainer.py` | 1 failed, 1 passed | `assets\spritecontainer\payloads.store` | 2 passed |

## 2. Table-drive candidates

| candidate | tests | body | converted |
|---|---|---|---|
| `test_lint.py` `refused()` answers | 11 | `assert [not] refused(<text>, <name>, <check>)` | yes |
| `test_lint.py` `refused()` findings | 5 | `found = refused(...); assert len(found) == 1; assert <fragments> in found[0]` | yes |

### Refuted: the three assetdir files are not a table-drive candidate

| file | imports | contract it pins |
|---|---|---|
| `test_assetdir.py` | `assetdir` | `asset_directory_64`: 64 records, 390,901 block bytes, first `0x2B9BB0` |
| `test_assetdir2.py` | `assetdir2` | `asset_directory_79`: 79 records, 343,010 block bytes, first `0x3195A8` |
| `test_assetdir3.py` | `assetdir3`, `generate_assetdir3` | the stream machine on a synthetic image, no ROM |
