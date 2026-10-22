# END-ROM-RECON-001: the end-of-ROM census regions, their consumers, formats and residue

Recon only: nothing promoted, converted, or used to change an asm or gate number. Population 4,274 rows / 1,040,994 B. All measurements read the retail bytes directly; instruments and denominators are in the table below.

## 1. Method, instruments, denominators

| instrument | what it does here | denominator |
|---|---|---|
| `docs/research/RAW_REMAINDER.csv` | rows, bytes and class per region | 4,274 rows / 1,040,994 B (script re-summed) |
| `tools/mapcontainer/endromcontainer.py:container_offsets` + `webfoot_lz.validate_retail_termination` | the 427 emitted packed members of the end-of-ROM block (kinds 1, 2 only) | block 0x6B7E8C..0x7B79A4 |
| `generate_mapcontainer.endrom_record_extents` | the 8 promoted record families of the same block | 201,228 B in 4,170 extents |
| FORMAT-RECON-001's kind-0 detector (copied into scratch, cited) | header word 0, declared >= 16, declared payload ends inside the row, greedy non-overlapping largest-first cover | every image-grid 4-aligned offset of every row |
| per-row byte shuffle, 5 draws | null for the kind-0 detector: same row lengths, same byte histogram, order destroyed | same rows, same detector |
| `tools/research/code_xref.py:scan/loads_into/into` | 117,008 Thumb + 618 ARM pc-relative load sites | whole image |
| literal-pool channel | 4-aligned site inside 0x000158..0x071758 (P-420) whose target word lies in a row | 2,854 targeted words / 3,825 sites |
| `tools/structured/families.py:serialize`, `spritefamily.serialize_record` | family round trip on a candidate record | per call, errors quoted |
| capstone Thumb-1 | independent decode of the cited consumer windows | sites named per section |

## 2. The per-region table

| id | rows | bytes | consumer(s) (site or count; no extent in any of them) | format hypothesis | candidate cover (copy; null band) | residue | null control value |
|---|---|---|---|---|---|---|---|
| R20 0x76CCE4..0x77AE68 | 15 | 57,732 | 40 loader sites / 22 literals; tail reader 0x0803928E/0x080392E4; indexed bases 0x0876E264+36N, 0x0876DFF8+48N, 0x08770CF4+4N, 0x0877ADD8+4N | heterogeneous record run, no extent | 33,542 B; null 34,606..37,741 B | 24,190 B, undecoded | null exceeds the real cover |
| R21 0x71E274..0x72C378 | 43 | 57,604 | 182 sites / 61 literals; 0 in-range; 326 B read at constant offsets | heterogeneous record run, no extent | 27,387 B; null 26,301..41,320 B | 30,217 B, undecoded | real inside the null band |
| R22 0x6FC260..0x6FDA00 (not worked) | 4 | 6,048 | 33 sites / 16 literals; one 12 B piece record at 0x6FD9D0 | not worked | 898 B; null 774..2,452 B | 5,150 B | not a result here |
| R23 0x7122F8..0x71E258 | 41 | 48,992 | 175 sites / 66 literals; 12 B piece records 0x712FDC, 0x71370C (constructor 0x0802A81C); IWRAM descriptor block 0x71DD38; scalars 0x7198E4, 0x71DD4C, 0x71DDC8 | record run with piece records at row starts | 5,559 B; null 3,017..6,334 B | 43,433 B, undecoded | real inside the null band |
| R24 0x72C388..0x7315E8 | 8 | 21,088 | 25 sites / 11 literals; 16 B array 0x087315A8 indexed at 0x0801BF78; 0x087315D8 read at +4; descriptor 0x72C388/94 | 8 bpp pixel data 0x730000..0x730CCC + 12 B piece/frame table from 0x730CCC | 6,125 B; null 3,158..5,251 B | 14,963 B, of which the pixel data and the piece table | real above the null; format still partly undecoded |
| R25 0x75029C..0x752D4C | 5 | 10,928 | 9 sites / 5 literals | record run, no extent | 4,535 B; null 5,849..6,578 B | 6,393 B, undecoded | null exceeds the real cover |
| R26 0x752EF0..0x754910 | 8 | 6,688 | 20 sites / 9 literals | record run, no extent | 594 B; null 1,346..2,024 B | 6,094 B, undecoded | null exceeds the real cover |
| R27 0x754978..0x756A4C | 5 | 8,404 | 13 sites / 5 literals | record run, no extent | 3,435 B; null 5,010..6,395 B | 4,969 B, undecoded | null exceeds the real cover |
| R28 0x77B200..0x77C47C | 6 | 4,732 | 14 sites / 6 literals | record run, no extent | 1,128 B; null 640..2,250 B | 3,604 B, undecoded | real inside the null band |
| R29 0x75A738..0x76CCD4 | 17 | 75,164 | 79 sites / 35 literals; six field maps decoded, no extent (PATH-100-002 STEP 2); descriptor blocks 0x72083C/4C, 0x725048, 0x72A6B4, 0x72BF94/A8 | record run with field maps, no extent | 19,733 B; null 29,061..48,195 B | 55,431 B, undecoded | null exceeds the real cover |
| R30 0x74F080..0x77C5A4 (slice A lower half) | 95 | 18,842 | 224 literals / 514 sites; glyph table consumer 0x0803029E for the row at 0x757EE8 | window over promoted sub-ranges plus residue; one parsed row, the 85-entry table | 5,135 B; null 5,070..7,227 B | 13,707 B, undecoded | real inside the null band |
| R31 0x6FC238..0x7315E8 (slice B residue) | 922 | 21,136 | 252 literals / 538 sites; 6 cited rows (1,268 B) promoted; window head 0x6FC238 is a generated global-state table (consumer 0x08017C6E), not a row | window of sparse residue rows; 4 pointer tables | 24 B; null 0 B | 21,112 B, undecoded | one 24 B hit against a zero null, too small to be a format |





### H3. The K-089 12 B piece records

| record | fields (s8 x, s8 y, u8 w, u8 h, u32 attr, u32 gfx) | containing row |
|---|---|---|
| 0x6FD9D0 | 8, 8, 16, 16, 0x40002000, 0x086FCCD0 | R22 row 0x6FD9D0..0x6FDA00 (out of contract) |
| 0x712FDC | 8, 8, 16, 16, 0x40002000, 0x087122DC | R23 row 0x712FDC..0x71370C, first 12 B |
| 0x71370C | 8, 8, 16, 16, 0x40002000, 0x0871330C | R23 row 0x71370C..0x7137CC, first 12 B |




### H7. Boundaries

| region end | next source section | boundary reading |
|---|---|---|
| R20 0x77AE68 | `endrom_0077AE68_0077AE84.bin` generated | run end, not a structure boundary (UNKNOWN_PROVEN_R23: the tail record starts inside the run) |
| R21 0x72C378 | `endrom_0072C378_0072C388.bin` generated | no access in any traced window (UNKNOWN_PROVEN_R23) |
| R22 0x6FDA00 | `endrom_006FDA00_006FDA1C.bin` generated | section boundary |
| R23 0x71E258 | `endrom_0071E258_0071E274.bin` generated | section boundary |
| R24 0x7315E8 | `endrom_007315E8_0073198C.bin` generated | section boundary; RECON-LATE-2 measured this is NOT the end of the 0x7315A8 array |
| R25 0x752D4C | `endrom_00752D4C_00752D68.bin` generated | section boundary |
| R26 0x754910 | `endrom_00754910_00754958.bin` generated | section boundary |
| R27 0x756A4C | `endrom_00756A4C_00756A74.bin` generated | section boundary |
| R28 0x77C47C | `endrom_0077C47C_0077C48C.bin` generated | section boundary |
| R29 0x76CCD4 | `endrom_0076CCD4_0076CCE4.bin` generated | section boundary |
| R30 0x77C5A4 | `endrom_0077C5A4_0079B704.bin` generated (the 522-record event pool) | a real structure boundary, of a promoted family |
| R31 (its own last row) 0x711274 | `endrom_00711274_007122DC.bin` generated | the window's assigned rows stop before the generated section; the window end 0x7315E8 belongs to R24 |

## 5. Conversion candidates

| candidate | exact row span | existing family | byte-exact round trip measured | permissible under the contract |
|---|---|---|---|---|
| glyph-source table, 85 x 4 u16 | R30 row 0x757EE8..0x758190, 680 B | none pre-existing (the probes in H4); new family `endrom_glyph_table_85` in the ENDROM block | yes: 85/85 records re-serialize byte-exact from four parsed u16, with every value asserted inside the consumer's 0x300-byte buffer | **promoted** (source 7,347,614 -> 7,348,294, raw-data 1,040,994 -> 1,040,314, DIGEST MATCH) |
| K-089 12 B piece records | R23 rows 0x712FDC..0x71370C and 0x71370C..0x7137CC, first 12 B each, 24 B | none (no 12 B family; `endrom_44_record` is 44 B, `SiblingObjectRecord` 28 B) | not attempted: no family takes a 12 B record | blocked on a new family; consumer known (0x0802A81C), 24 B |
| 8 bpp pixel data + 12 B piece table | R24 row 0x72D6B8..0x7315A8, 0x730000..0x7315E8 | none covers the span (tilebank and sprite blocks are elsewhere) | both container builders differ at byte 0 | **not a candidate**, REPORT only: no decoded consumer and no graphics family input |
| kind-0 header-shaped covers | all regions, 108,095 B candidate | none | identity transform, 278/278 identical | **not a route**: regeneration is a copy from a ROM-read payload, and the shuffle null is not beaten |
| pointer tables | 41 rows / 476 B in the 11 contract ids | already the census `tables` route | not re-measured (out of scope) | already routed, no new work |
