# The 848 B cell-map table at `0x7198E4`

53 records of 16 B at `0x7198E4..0x719C34` (R23's still-raw run), emitted at build time by
`tools/mapcontainer/cellmap.py` through `tools/mapcontainer/generate_mapcontainer.py --block endrom`.
Before this ticket the span was one INCBIN slice; the gate now counts it as source.

## The reader, instruction by instruction

| site | halfword | instruction | what it establishes |
|---|---|---|---|
| `0x080196E8` | `4F30` | `ldr r7,[pc,#0xc0]` | literal `0x0197AC` = `0x087198E4`, the table's base |
| `0x080196EA` | `2101` | `movs r1,#1` | the value the loop writes |
| `0x080196EC` | `0102` | `lsls r2,r0,#4` | stride 16, index `r0` |
| `0x080196EE` | `58BB` | `ldr r3,[r7,r2]` | record word 0 |
| `0x080196F2` | `54E9` | `strb r1,[r5,r3]` | buffer byte `r5+word` becomes 1 |
| `0x080196FC` | `2835` | `cmp r0,#0x35` | index < `0x35`, so 53 records |
| `0x08019704` | `DBF2` | `blt #0x80196EC` | the loop covers records `r0..0x34` |

`r5` is `sp+4` (`0x080196D6`, `AD01`) and the frame is `add sp,#0x1fc` (`0x08019716`, `B07F`) then
`add sp,#8` (`0x08019718`, `B002`), so every offset indexes one `0x200`-byte block. Words 1, 2 and 3
are read at `0x080196F4` (`6853`), `0x080196FA` (`6893`) and `0x08019700` (`68D2`) and written the
same way.

## Layout

One record is four `u32` byte offsets into the consumer's `0x200`-byte block. `cellmap.fields`
refuses a record that is not 16 B and a word above `0x1FF`, and `cellmap.assert_contract` re-reads the
reader's own instructions, the literal word and its single occurrence in the image before any record
is parsed.

## The null it beats

The trivial explanation is raw bytes with no layout. Measured on the retail table: all 212 words lie
in `0x17..0x1E8`, all 212 are distinct, and the walk covers the row exactly (53 x 16 = 848 B). Against
a byte-permuted copy of the same row (`tools/mapcontainer/test_cellmap.py`), 0 of 53 records pass the
block bound, so the predicate is a property of these bytes and not of the size.

## What stays raw around it

The rows that carry more bytes have readers that name only a base address (`0x77110C` 39,940 B,
`0x75A7A4` 20,488 B, `0x72084C` 18,380 B) or a stride with no bound (`0x762270` 35,408 B at stride 36,
whose byte index reaches at most 9,216 B of the row; `0x72D6B8` 16,112 B at stride 60), and the
graphics runs are copied to VRAM verbatim by `bl 0x08049138` at a size equal to the run
(`0x72C3B8` 0x1300 B, `0x753008` 0x400 B, `0x7137D8` 0x300 B), which is an identity copy and not a
decode. None of those spans converts.
