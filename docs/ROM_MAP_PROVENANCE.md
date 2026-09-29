# ROM map provenance

Where every boundary in [`ROM_MAP.md`](ROM_MAP.md) came from, what it rests on,
and where this project's independent analysis agrees or disagrees with the public
reference disassembly and with the LOG1-REMAKE corpus.

Three sources of belief are used, and they are kept apart deliberately:

| Source | Meaning | How it appears in the map |
| --- | --- | --- |
| **Derived here** | Established by this project's own analysis of the ROM bytes | `provenance` names a `tools/buusfury/*` function |
| **Reproduced here** | Regenerated from source and compared byte-for-byte | `representation: "reproduced"` or `"generated"` |
| **Cited externally** | Named by another project with a citable location, then re-validated here | `provenance` names the external document, and the region is at most `medium` |

Nothing in the map is `proven` on external say-so. Where an external address is
used, this project disassembles from it and discards it if it does not decode.

---

## 1. The public reference project: what we took and what we changed

The reference is `2genkidev/buusfury` at `cc53d0cd` (see
[`REFERENCE_AUDIT.md`](REFERENCE_AUDIT.md)). It supplies a 28-region build map,
which is a different artefact from this structural map: its regions describe
*who builds the bytes*, ours describe *what the bytes are*. The baseline ticket
keeps the build model in [`BUILD_REGIONS.md`](BUILD_REGIONS.md).

### 1.1 Boundaries where we agree, for our own reasons

| Offset | Reference says | This ticket derived | Agreement |
| --- | --- | --- | --- |
| `0x000000-0x0000C0` | `Head`, header source | decoded header, valid checksum, standard logo | agree, independently |
| `0x0000C0-0x000158` | `crt0.s`, 152 bytes | entry branch target `0x080000C0`, 29 ARM instructions, literal pool referenced `0x000134-0x000158` | agree, independently |
| `0x03D4D0-0x03D740` | `GBARam.s` + 2 INCBINs | 232 bytes of Thumb + a 16-byte literal pool all four of whose words are loaded by that code | agree, independently |
| `0x049114-0x049120` | `AfterLibs`, 12 bytes | veneer reached by the reset path's tail branch; loads `0x08046AED` and BXes it | agree, independently |
| `0x05632C-0x05672C` | two palettes | both reproduced byte-identically from source `.pal` files | agree, by reproduction |
| `0x05672C-0x05792C` | `color_transforms.cpp`, 4608 bytes | bounded by two proven anchors; exactly 4608 = 18x256 | agree on bounds; the 18x256 split is **not** independently verified here |
| `0x05792C-0x06D4E0` | `strings.cpp`, 89,012 bytes | UTF-16LE pool tiled exhaustively by 1,534 ascending pointers | agree, independently |
| `0x07B89A8-0x0800000` | `<null bytes>` | 292,440 bytes, **every one `0xFF`**, zero exceptions | agree on bounds; the reference's label is **wrong** |

### 1.2 Boundaries where this ticket differs from the reference

The reference's largest regions are opaque `INCBIN` spans. Independent analysis
splits them, because the ROM itself contains structure the reference does not
name:

| This ticket's region | File extent | Bytes | Why the reference did not have it |
| --- | --- | ---: | --- |
| `codec_blob` | `0x07B79A4-0x07B89A8` | 4,100 | The reference INCBINs it inside `rest_of_the_game`. It is clean ARM code: `0x07B79A4` opens `push {r8,r9,r10,r11}` / `mov ip, #0x04000000`, and `0x07B79E4` opens a second prologue. The reset path loads `0x087B79A4` into DMA3SAD. The span ends exactly where the `0xFF` fill begins. |
| `library_signal_strings` | `0x07B71A2-0x07B79A4` | 2,050 | Same. This window holds the ARM C library's signal-name table (`Abnormal termination`, `Arithmetic exception: `, `Stack overflow`, `Out of heap memory`, ...) and the mandatory `EEPROM_V124` save-type signature at `0x07B7964`. |
| `compressed_dialogue_table` | `0x07B5B64-0x07B5B80` | 28 | Seven in-ROM pointers, all strictly ascending, whose targets are contiguous container bases ending at this table's own base. |
| `event_resource_table` + `_pool` | `0x077C5A4-0x079BF2C` | 129,416 | 522/522 in-ROM pointers; the pool ends exactly where the table begins. |
| `appearance_table` | `0x074D380-0x074E200` | 3,712 | 232 x 16; zero in-ROM pointers in the span. |
| `character_sprite_table` | `0x06B6BDC-0x06B7080` | 1,188 | 297/297 in-ROM pointers, terminated by a non-ROM word. |
| `map_entry_table` | `0x08E2E0-0x0945C0` | 25,312 | 452 x `0x38`; record 0 lays out as 8 count bytes then 12 words with word 10 = `0x080728CC`. |
| `character_base_stats` | `0x06FDA4C-0x06FDAEE` | 162 | 9 x `0x12`, no in-ROM pointers. |
| `enemy_stat_table` | `0x0711274-0x07121E0` | 3,948 | 141 x `0x1C`, mixed numeric records and pointers. |
| `item_table` | `0x03BD2F8-0x03BE3D4` | 4,316 | 83 x 52; **ends exactly** where the splash container begins. |
| `sprite_container_span` | `0x03C34D0-0x06A87A8` | 3,039,256 | Adopted as a single region at `medium` confidence; see §3. |

**The disagreements are additive, not contradictory.** Every offset the reference
calls a boundary is still a boundary here, except where it is not a boundary at
all (§1.3). This ticket adds internal structure; it does not move the reference's
edges.

### 1.3 Boundaries where the reference is wrong or unsupported

| Claim | Finding |
| --- | --- |
| `0x7B89A8-0x800000` is `<null bytes>` | **Wrong.** All 292,440 bytes are `0xFF`. Zero non-conforming bytes. The range is also **not** free space (§1.4). |
| The four compressed assets are "JCALG1" | **Unsupported naming.** Their 8-byte prologue is `kind = 1` at `+0x00` and `declared_size` at `+0x04` - the same container shape the LOG1-REMAKE corpus independently decoded for sprite and chunk data. This project reproduced all four byte-for-byte with the reference's own compressor, which proves the *bytes*, not the format's name. The map therefore classifies them `compressed_asset` and does not name a codec. |
| The engine's code is one opaque span | **Not established and actively unhelpful.** See §3. |

### 1.4 The FF tail is not free space

`0xFF` fill was measured, and it is the largest constant run in the image. It is
**not** evidence of unuse. The LOG1-REMAKE corpus
(`docs/research/BUU_VERIFIED_CAPACITY.md:14,54`) measured 516 pointer-shaped
little-endian words targeting this range and explicitly refused to promote it;
only a carved 256-byte window elsewhere (`[0x7EA400,0x7EA500)`) is confirmed free.
The region's `notes` field says so, and a test asserts the wording stays.

---

## 2. Disagreement with the LOG1-REMAKE corpus: the transfer at `0x7B79A4`

The corpus (`docs/reverse-engineering.md:689-692`) states that the reset path
DMA-copies **4,100 bytes** from ROM `0x087B79A4` to IWRAM `0x03000000`, and that
the packed-decoder entry `0x087B79E4` therefore lands at IWRAM `0x03000040`.

This ticket's own disassembly of the reset path disagrees about the *transfer
size*, and agrees about everything that matters:

| | Corpus | This ticket |
| --- | --- | --- |
| DMA3 source | `0x087B79A4` | `0x087B79A4` - **same** |
| DMA3 destination | `0x03000000` | `0x03000000` - **same** |
| Transfer count written | 1,025 | 1,025 - **same** |
| Control word | not stated | `DMA3CNT = 0x84000401`, so `CNT_L = 0x0401` and `CNT_H = 0x8400` |
| Implied transfer size | 4,100 bytes (1,025 x 4) | 2,050 bytes (1,025 x 2) |
| Implied ROM span | `[0x7B79A4, 0x7B89A8)` | `[0x7B71A2, 0x7B79A4)` |

The disagreement is about the interpretation of `CNT_H = 0x8400`, whose bit 8 is
the transfer-size flag and whose bits 11-10 are source address control. Under the
GBATEK layout `0x8400` means *16-bit transfers with source decrement*; under a
32-bit incrementing reading the span would end exactly at the `0xFF` fill, which
is a striking coincidence in the corpus's favour.

**This ticket does not claim either reading.** It records the register values as
facts and establishes the *region* by content instead:

- `0x07B79A4` is the first byte of clean ARM code (`push {r8,r9,r10,r11}`), so it
  is a real boundary regardless of the transfer size;
- `0x07B89A8` is the first byte of the `0xFF` fill, so it is a real boundary too;
- the span between them is exactly 4,100 bytes.

The region is therefore `high`, not `proven`, and the `notes` field states the
open question. Resolving it needs either a runtime DMA observation or a
higher-confidence reading of the ARM immediate encoding, and belongs to a later
ticket.

---

## 3. Why 53% of the ROM is still `unknown`

This is the single most important limitation of this map, and it is a measured
property of the cartridge rather than a gap in effort.

`python -m buusfury rommap` reports `unknown` for 4,554,062 bytes (54.3%). That is
not a failure to look: it is what the evidence supports.

**Thumb data is nearly indistinguishable from Thumb code on this cartridge.**
Measured with capstone:

| Sample | Thumb decodes | ARM decodes | Entropy |
| --- | --- | --- | ---: |
| the UTF-16LE text pool at `0x05792C` | whole window | whole window | 6.0 |
| the pointer table at `0x06BCE8` | whole window | whole window | 6.2 |
| the MapEntry content stream at `0x0728CC` | 192 of 4,096 B | 192 of 4,096 B | 5.5 |
| known engine code at `0x000158` | 1,952 of 4,096 B, 19 local branches | 52 B | 6.2 |
| known engine code at `0x03D740` | 4,096 of 4,096 B, 148 local branches | 40 B | 6.8 |

ARM decoding IS discriminative (data hits an NV-condition word within about 16
words), which is why the ARM-classified regions are trustworthy. Thumb is not:
roughly 94% of arbitrary halfwords are valid encodings, so both a text pool and a
pointer table "decode" end to end, and a conditional branch appears by chance in
about 6% of halfwords.

Two consequences, both deliberate:

1. **The windowed classifier is capped at `medium`.** It may label a window
   `code`, but never at `high`. A test asserts no heuristic region claims `high`.
2. **The rigorous code signal is recursive reachability.** A byte is `code` at
   `high` only if it was reached by following control flow from a known entry
   point and decoded cleanly. That yields 9,684 bytes of `confirmed` executable
   coverage - a **lower bound**, not an estimate.

The lower bound is small because this engine dispatches through vtables and
native-slot tables (`0x08055098`, `0x0804B2C8`, `0x0804C484`, ...), which static
control flow cannot follow without knowing each table's extent. Following those is
the natural next step and is not attempted here.

### 3.1 The large declared span

`sprite_container_span` (`0x03C34D0-0x06A87A8`, 3,039,256 bytes, 36.2% of the ROM)
is adopted as a single region at `medium` confidence. It is not a measurement: it
is the externally-declared container span, and both of its ends coincide with
anchors this ticket did derive (the splash container before it, the character
sprite table after it). Re-deriving the individual container boundaries inside it
was out of scope and is left explicitly undone rather than guessed at.

---

## 4. Provenance of each anchor, one line each

| Region | Bounds established by |
| --- | --- |
| `rom_header` | decoded header: valid checksum, standard logo, declared fields |
| `reset_code`, `reset_literals` | entry branch target; 29 decoded ARM instructions; literal-pool displacements |
| `gbaram_code`, `gbaram_literals` | clean Thumb decode; every pool word loaded by that code; pool end = next anchor |
| `intro_asset`, `splash_asset`, `dialogbox_assets` | container headers self-declaring 0x9600 / 0x2800; reproduced byte-identically |
| `corner_images`, `background_palette`, `object_palette` | reproduced byte-identically from source assets; corners end flush at the palette |
| `titlescreen_data` | bounded by two reproduced anchors; 10 of its 26 words point into ROM and four point exactly at the four corner images |
| `colour_lut_block` | bounded by the object palette (reproduced) and the text pool (tiled) |
| `text_string_pool`, `text_pointer_table` | 1,534 ascending pointers; exhaustive tiling; every unit's high byte zero |
| `item_use_pool`, `item_table` | external extent; **end** confirmed by the splash container starting there |
| `sprite_container_span` | external declared span; both ends confirmed by neighbours |
| `character_sprite_table` | 297/297 in-ROM pointers, terminated by a non-ROM word |
| `character_base_stats`, `enemy_stat_table`, `appearance_table`, `static40_*` | external extents; arithmetic re-verified; pointer density re-measured |
| `map_entry_table` | 452 x `0x38`; computed end matches the external boundary exactly; record 0 matches the documented `+0x2C` root |
| `event_resource_pool`, `event_resource_table` | 522/522 in-ROM pointers; pool ends where the table begins |
| `compressed_dialogue_table` | 7/7 in-ROM pointers, strictly ascending, contiguous targets |
| `library_signal_strings` | reset path's DMA3 source address; ARM C library signal strings and `EEPROM_V124` inside |
| `codec_blob` | clean ARM prologues at `+0x000` and `+0x040`; span ends exactly at the `0xFF` fill |
| `opaque_tail_padding` | 292,440 bytes, all `0xFF`, zero exceptions |
| `code_candidate_span_*` | external entry points, each re-validated by disassembly; bounds chosen, not derived |

---

## 5. Claims from the corpus that this map must not be read as supporting

Recorded so a later ticket does not cite this map as evidence for them. Each was
refuted or left unresolved by the corpus itself; none has been re-tested here.

- **`0x08046AA4` is a point query.** Refuted; it is a `bx r2` thunk.
- **`0x087B7970` is a library table.** Withdrawn.
- **`0x08711274` has a settled record count.** Unresolved (141 vs a max selector of
  149). This map claims an extent from the 141 x `0x1C` reading and says so.
- **Cross-profile offset transfer.** The mstan recomp image is a different
  cartridge; no offset transfers.
- **`0x0800938C` and `dest+0x94/+0x98`.** A live disagreement between the corpus
  documents and the project memory store. Not settled, and not needed here.

---

## 6. Reproducing this provenance

```powershell
python -m buusfury rommap --rom <baserom> --write config/rom_map.json `
                          --functions config/functions.json --docs docs/ROM_MAP.md
python -m buusfury fixed  --rom <baserom>
python -m pytest tests -q
```

Every claim above is either in `config/rom_map.json` (with an `evidence` list per
region) or asserted by `tests/test_rom_map.py`.
