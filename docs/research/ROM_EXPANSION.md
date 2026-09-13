# Generated ROM expansion capacity

## Scope

ROM-EXPAND-001 asks one bounded question: can the Buu's Fury retail engine
consume an existing compressed-dialogue container after its authoritative table
pointer is moved into generated ROM expansion space? This is tooling behavior,
not a claim about unused bytes in the canonical retail ROM.

## Platform evidence

GBATEK documents the GBA Game Pak ROM/FlashROM window as
`0x08000000..0x09FFFFFF` (32 MiB). Within that window the SDK's existing typed
conversion is `GBA_ROM_BASE + file_offset`; consequently file offset
`0x00800000` is ROM address `0x08800000`. The experiment uses a deterministic
16 MiB image: a conservative power-of-two policy within that documented
window, not a claim that every cartridge or flash device has been physically
tested. See [GBATEK, Game Pak](https://rust-console.github.io/gbatek-gbaonly/#gamepak-rom) and
`tools/webfoot/binary.py`.

Real cartridge/flash hardware remains untested. The runtime result below is
specific to mGBA 0.11 development build and does not make a hardware claim.

## Runtime experiment: CONFIRMED / LEVEL 4

Input: the immutable canonical Buu's Fury ROM, 8,388,608 bytes, SHA-256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`.

Selector 1 originally points at `0x087A04F0` (file `0x007A04F0`) and occupies
16,856 bytes through the next table entry. Replacing the decoded 0x20-byte
record `Good luck, Goku!` with `Nice work, Goku!` preserved the decoded length
but rebuilt to 17,932 bytes, an in-place overflow of 1,076 bytes.

The generated image is 16 MiB, pads from canonical EOF with `0xFF`, stores the
complete rebuilt container at file `0x00800000`, and changes only selector 1's
word in the table at file `0x007B5B68` to `0x08800000`. The packed handle
`0x02002641`, dialogue record, decoded start `0x132`, decoded length `0x20`,
and six other container pointers remain unchanged. Static decode of the
relocated bytes recovers the authored record and all other decoded bytes match.

Tracked mGBA observation captured the retail consumer at `0x08012240` reading
the same packed handle, selector 1, and relocated pointer `0x08800000`. A
snapshot from the deterministic fixture visibly shows `Nice work, Goku!` in the
normal retail dialogue box. The production build path regenerated a byte-for-
byte identical image, SHA-256
`3ccbef45940e8f5c27d3f88839639eb04d9cc50f8d942f18bc850872628724cb`.

## Allocation model

`generated_expansion` in the profile is a distinct generated-image declaration:
output size, padding byte, and evidence. It is not stored in `free_regions`, so
the canonical atlas remains an 8 MiB retail atlas. At build time the shared
allocator receives this appended region explicitly with the generated image
size, and its existing reservations and overlap checks apply normally.

The write plan always verifies the canonical source hash and source size first,
then deterministically materializes padding before validating any appended
write. Output must be a separate non-existent path; no path can alias the
canonical input.
