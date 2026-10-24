# The map block's animation rows and their readers

The map block is the file range `0x179A50..0x2B8BC8`. Offsets here are file offsets; a ROM address
is `0x08000000 + offset`.

## The chain that names a row

    MapEntry +0x2C        pointer array of section roots; slot = byte at MapEntry +0x02, 1-based
    0x080089CC            ldr r0,[r0,#0x2c] / lsls r1,r1,#2 / adds r0,r0,r1 / subs r0,#0x40 / ldr r0,[r0,#0x3c]
    root +0x0C            u8 count of animation rows in the root's list
    root +0x10            u32 pointer to that many ROM addresses (stride 4)
    0x08009B94            ldr r2,[r1,#0xc]        root +0x0C, the loop bound at 0x08009BC6
    0x08009BA8            ldr r5,[r1,#0x10]       the array base
    0x08009BAE            ldr r5,[r5,r6]          array[i], r6 = 4*i
    0x08009BBC            ldrh r2,[r5,#2]         the row's vram_slot, min() at 0x08009BC0

Each `array[i]` is one animation row. The runtime copies the row pointer into an 8-byte queue entry
at `(queue+4)+8*i` (`0x08009BB4 strh r6,[r2]`, `0x08009BB8 strh r4,[r2,#2]`,
`0x08009BBA str r5,[r2,#4]`), and `0x08009CC2` advances one entry per frame.

## Family `map_anim_row`

    +0x00  u8   frame_count   read 0x08009CF0 ldrb r2,[r2]      (index bound, 0x08009CF2 cmp)
    +0x01  u8   vram_units    read 0x08009B32 ldrb r1,[r0,#1]   (copy length, <<6 at 0x08009B36)
    +0x02  u16  vram_slot     read 0x08009B34 ldrh r0,[r0,#2]   (VRAM base, <<6 at 0x08009B3C)
    +0x04  u32  frame[count]  read 0x08009B26 ldr r1,[r0,#4]    (slot for the queue's frame)
                              read 0x08009D02 ldr r1,[r1,#4]    (slot 4*frame after 0x08009CFE)

Extent is `4 + 4 * frame_count`. `frame_count` is 1..64 in the population (1, 2, 3, 4, 5, 6, 7, 8,
9, 12, 16, 18, 32 occur). `vram_units * 64` is the byte count written to VRAM; `vram_slot * 64` is
the VRAM destination (`0x08009B38 movs r1,#3 / lsls r1,r1,#0x19` = 0x06000000,
`0x08009B42 bl 0x08049138`). 431 rows / 12,824 B are anchored by a root's list, all inside the block
and outside every container, root record, layer record and dominant-family record.

## The frame a row names

    +0x00  u32  duration      read 0x08009D04 ldr r1,[r1] and 0x08009D06 strh r1,[r0,#2]
    +0x04  ...  payload       decoded into a stack buffer by 0x08009B2C bl 0x08049120 from frame+4

`0x08049120` is a Thumb veneer: `08049120 bx pc`, ARM `08049124 ldr pc,[pc,#-4]`, and the literal at
`0x049128` is `0x03000040`, whose body is the JCALG1 decoder at file `0x7B79E4`. The stream has no
length field of its own: it decodes to exactly the row's `vram_units * 64` bytes, and the copy to
VRAM (`0x08009B42 bl 0x08049138`, IWRAM `0x03000768`, file `0x7B810C`) takes that decoded buffer. So
the retail bytes are not the VRAM payload: they are its compressed stream.

The decoded payloads index a 256-entry palette (the highest index in the set is 0xFF), so each tile
is 8bpp: `vram_units` 64-byte tiles, one per 8x8 tile slot, drawn from the BG palette the scene loads
to `0x05000000` from file `0x5652C` (`0x0800657A bl 0x08049144`, 512 B).

## The resource a root names at +0x48

    root +0x48            pointer, loaded at 0x08009BF2 and passed to 0x0803D940 with a stack buffer
    0x0803D940            ldr r3,[r2] then: 0 -> ldr r2,[r2,#4] / bl 0x08046D18 (LZ, sized),
                                          1 or 2 -> bl 0x08049120 with src = r2+8 (decoder, see the frame section)
    0x0803D946            ldr r3,[r2]        the block's type word
    0x0803D95E            ldr r2,[r2,#4]     the type-0 decompressed size

A block named by `root+0x48` starts `{u32 type; u32 size; payload}`. Type 2 blocks are copied,
type 0 blocks are decompressed by `0x08046D18`; the codec of type 0 was not measured.

## What the build emits, and what stays raw

`tools/mapcontainer/animrow.py` emits 122 rows / 3,500 B as `map_anim_row` tables in the carriers
(`|map_anim_row_XXXXXXXX|`, `DCB frame_count,vram_units`, `DCW vram_slot`, `DCD frame[...]`), with
the same fields the readers load. One further row, `0x2B7E58` (28 B), is refused: its carrier is
split at interior exported labels `+1`, `+2`, `+4` and `+0x10`, and a table cannot carry them.

`tools/mapcontainer/animframe.py` carries a frame as an indexed image: it decodes the stream, writes
the `vram_units` 8x8 tiles as one `vram_units * 8` x 8 PNG row (palette file `0x5652C`), reads the
PNG back, packs the payload from the pixels, re-encodes it with the tree's oracle and requires the
retail duration word and stream back. 125 carrier tokens / 83,908 B / 477 frames are covered by
`tools/mapcontainer/animframe_manifest.csv`; 48 tokens / 2,804 B stay raw: 37 pointer or table rows
that hold no frame at all, the 28 B refused row `0x2B7E58`, and four rows whose frame crosses a
carrier boundary.

The block's record run is byte-exact and is not an outstanding conversion: the plan
`tools/mapcontainer/generate_mapcontainer.py` reads (358 `child_list_row` records / 28,288 B, plus
the root, dominant, layer, root-table and root-pointer families) is emitted by
`python tools\gate\emit_all.py`, and the gate is DIGEST MATCH with every one of those sections
reproduced.

## The 308 rows inside a `child_list_row` record

431 rows / 12,824 B are anchored by a root's list, 122 of them are free of every record and are
emitted, and exactly 308 rows / 9,296 B lie strictly inside one of the 358 `child_list_row` records.
None of the 358 has an extent equal to a row's extent, so every one of the 308 would need its record
split. The one row left over is `0x2B7E58` (28 B), refused above.

The readers prove the animation-row reading at every one of the 308: each is named by a root's
`+0x10` array and parses as `4 + 4 * frame_count` with a frame count in 1..64. The record's own parse
disagrees about the same bytes: it reads a list's pointers as the addresses of further lists, and
here those pointers name frame tables whose first word is a duration (`0x0000000A`, `0x0000003C`, ...).
A relabel would have to cut 308 records where the child-list parse yields no boundary and where the
plan has no record type that starts mid-record. No byte moves: the `child_list_row` extent is
unchanged and the runs keep reproducing the bytes.
