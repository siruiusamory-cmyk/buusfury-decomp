# TOOLKIT-006 script VM evidence

## Status
Primary profile: LOGII USA revision 0, selected because its independently
verified native interpreter and fixed caller-selected corpus establish the
architecture without map archaeology. The supported corpus is the complete
static43 family below, not the whole game. Toolkit decoding and assembly now
reproduce its entire extent byte-identically. Final validation: 804 passed; independent implementation review passed.
Canonical SHA-256: 6e6c370c339ec9171cb1956adf837a0d342a197f78964882ef46c3086656ff75.

## Prior knowledge audit
Arefu/Legacy d22a556cd33dee56513d5b606b6ae8065ccc5752 is unlicensed research
reference only. No implementation copied. OpCodes.csv:1-145 and
DBZKit/Legacy/Games/BYTECODE_VM.cs:5-152 name native secondary dispatch slots,
not the outer bytecode grammar. DBZKit/Legacy/SView_Decode.cs:25-245 and
DBZKit/DBZKit/Assets/Dialog.cs:129-211 disagree about branch widths and
termination. All these names are VERIFIED_UPSTREAM leads, not ROM semantics.
Its dialogue modes have UNKNOWN canonical applicability: no profile contract
in that parser. JCALG1 modes explicitly lack lengths/decompression
(Dialog.cs:83-90,106-112). Do not enumerate a corpus using those guesses.
Existing records inspected: reverse-engineering.md:16-23,97-126,
upstream-audit.md:55-149, LOGII_TEXT_FORMAT.md:235-300 and AUTO_RE_STATE script
references. Buu map pointer census does not transfer to LOGII.
TCRF direct fetch 2026-09-06 returned HTTP 403; no evidence claimed from it.
URL: https://tcrf.net/Dragon_Ball_Z:_The_Legacy_of_Goku_II

## Canonical static verification (CONFIRMED_ROM, level 2)
Read-only canonical image, identity checked before disassembly. Capstone Thumb
inspection is local research only, not a product dependency. Private rendered
listing: build/toolkit006/interpreter.txt. ROM addresses below are GBA addresses;
file offsets are obtained with the existing GbaRomAddress helper.

Interpreter 0x080092E4 resets primary depth at object+0 and alternate depth at
object+0x44. At 0x080092FE..0x08009316 it fetches one byte, increments cursor,
indexes a word table and invokes its handler; a null handler returns. Literal
at file 0x00009320 points to dispatch table GBA 0x083B5C00. Slots 0..29 contain
29 Thumb handlers and a null at slot 17 (0x11). Slot 30 is 0x030026BC: not a
verified opcode handler. Never extend the opcode set by assuming that is END.

| Opcode | Handler fetch | Verified encoding/control | Stack |
|---|---|---|---|
| 00 | 08008F44 | one unsigned byte | push 1 |
| 01 | 08008F5A | BE 7-bit continuation signed magnitude | push 1 |
| 02 | 08008F8E | one secondary-dispatch byte | per callee UNKNOWN |
| 03 | 08008FA4 | one secondary-dispatch byte | pop 1, native call |
| 04 | 08008FC6 | no operand, logical AND | pop 2 push 1 |
| 05 | 08008FE6 | no operand, logical OR | pop 2 push 1 |
| 06 | 08009000 | no operand, negate | pop 1 push 1 |
| 07..10 | 0800900E..080090E4 | no operands, arithmetic/comparisons | pop 2 push 1 |
| 11 | null | terminate | unchanged |
| 12 | 080090FE | unsigned byte; target = post-operand cursor + byte | unchanged |
| 13 | 0800910A | same forward encoding; branch when popped value zero | pop 1 |
| 14 | 08009128 | no operand | pop 1 |
| 15..1A | 08009130..08009224 | one secondary-dispatch byte | composite UNKNOWN |
| 1B | 08009250 | no operand, transfer to alternate stack | primary pop 1, alternate push 1 |
| 1C | 0800926C | unsigned byte; target = post-operand cursor - byte when decremented alternate top nonzero; else pop alternate and fall through | alternate counter |
| 1D | 0800929A | count byte then signed-magnitude varints; count zero unsafe | push count |

Signed magnitude: low bit is sign, magnitude is remaining bits; each byte adds
7 bits big-endian until high bit clear. Negative zero is representable and must
round-trip unchanged. Do not canonicalize encoding or silently discard overflow.
No high-level types or native operation meanings established by this table.

## Corrections
OLD CLAIM: visualizer 0x12/13/1C operands are varints.
NEW EVIDENCE: handlers 0x080090FE/0x0800910A/0x0800926C each read exactly one
unsigned byte; first two add forward, last subtracts backward.
RESOLUTION: use byte displacement contracts, never visualizer branch operands.

OLD CLAIM: visualizer 0x03 has no operand; 0x15..1A have none.
NEW EVIDENCE: each handler loads byte from cursor and increments it before native
dispatch (0x08008FA6..0x08008FAC; 0x08009132..0x0800922E).
RESOLUTION: each consumes one secondary-dispatch byte.

OLD CLAIM: visualizer 0x05 is StackNot; 0x1E can be END.
NEW EVIDENCE: 0x08008FE6..0x08008FFE reduces two values using OR and Booleanizes;
0x11 is the null dispatch slot and slot 0x1E contains a RAM data address.
RESOLUTION: 0x05 logical OR; only 0x11 termination supported. 0x1E UNKNOWN.

## Corpus / text consumers / capability
The caller-selected corpus below is verified and implemented. No fixed text
consumer semantics, dialogue capability advancement or runtime evidence claimed.
Project representation and editing remain deferred.

## Entry-root family verification
CONFIRMED_ROM, level 2: caller function 0x080049FC initializes counter r6=0,
then at 0x08004A86 loads r1 from literal 0x08004C80 = 0x086D68DC.
At 0x08004A88..0x08004A92 it forms table + 16*counter, reads +4 and calls
interpreter 0x080092E4; if first result is zero it reads +8 and calls again
at 0x08004ABA. At 0x08004AE0..0x08004AE4 it increments and loops while
counter < 0x2B. Thus exactly 43 records and 86 potential entry slots.
All 86 roots are non-null, distinct in-ROM addresses on the canonical image.
Neutral slot identities are record ordinal plus field slot, not quest names.
Private caller listing: build/toolkit006/root_callers.txt:58-109.

OLD CLAIM (independent early calculation): literal 0x08004C84, table 0x086D73F8.
NEW EVIDENCE: Thumb literal helper applies Align(site+4,4), so 0x08004A86
plus encoded displacement 0x1F8 resolves 0x08004C80, value 0x086D68DC.
RESOLUTION: reviewer withdrew wrong literal; all root/corpus measurements must
use corrected table. No toolkit data had been written from the wrong value.

## Supported corpus census (independently reproduced)
All 86 roots terminate. Unique rooted bytes tile file [0x006D66C0,0x006D68DB),
539 bytes; 86 blocks, 323 instructions, no branches/shared blocks/unknown width.
The byte at 0x006D68DB is outside the rooted code; no padding semantics claimed.
Opcode census: 00=107, 01=1, 02=107, 04=16, 05=6, 11=86.
Secondary calls: 19=99, 21=8 (decimal slot IDs). Their gameplay semantics remain
UNKNOWN here; names are upstream leads. Length distribution: 3:1, 5:76, 6:1,
10:2, 15:4, 35:2. This is a complete census of this caller-selected family,
NOT all game scripts. The implemented disassemble/assemble proof now reproduces
all 539 bytes, using the typed instruction and graph representation.

## Text consumer correction and limitation
CONFIRMED_ROM level 2: native dispatch table 0x083B5D28 slot 12 raw pointer
0x080094B1/fetch 0x080094B0; slot 75 raw 0x080094CD/fetch 0x080094CC.
Both handlers load literal at file 0x000095AC = GBA 0x080E2840.
At 0x080094B4..0x080094BC, index = byte from runtime structure + 0x30;
at 0x080094D0..0x080094D8, index = that runtime byte + 0x36.
Each pushes the indexed pointer on the primary stack. These are dynamic table
references, not fixed text-ID operands. Runtime byte meaning/range UNKNOWN
in this ticket; upstream active-character naming is not promoted by a label.
Neither native slot occurs in the 86-entry candidate corpus; no fixed script
consumer of any of the 260 table indices is established by that corpus.

OLD CLAIM: LOGII_TEXT_FORMAT.md:154-157 reports zero word-aligned references to
the table base and says its address is computed.
NEW EVIDENCE: exact canonical u32 scan finds 20 file offsets:
0x4F8,0x9B0,0x1268,0x1B38,0x1D88,0x2524,0x28A8,0x3230,0x3794,0x3B10,
0x460C,0x49BC,0x4C98,0x95AC,0xCAE4,0x10F44,0x1172C,0x17A34,0x1960C,0x1A688.
Two direct VM handlers demonstrably use one of these literals.
RESOLUTION: the old zero-reference claim is superseded. The cause of that
historical measurement error is UNKNOWN. The remaining 19 hits are numeric
references only until their consumers are checked; not relocation authorization.
This corrects script-consumer evidence without reopening TOOLKIT-005 code or
its established text round-trip guarantees.

## Other pinned upstreams and external pass
DragonByteZ b2691209fa873cc0c1d7aa9cdea7c1da4430afe4,
src/analysis.cpp:470-487,595-612: raw map script/count fields, not verified LOGII
root contracts or bytecode decoder. No map-field semantics transferred.
2genkidev/buusfury cc53d0cd2d1c167e749419187e2d92017ac07468: bounded git grep
of asm/src for script/bytecode/opcode finds credits strings in src/strings.cpp,
not an interpreter contract. Existing audit documents INCBIN boundaries.
LOGII recomp add98b5d76fb2b822be870f29fa27b22c9a95631: game.toml:19-21 matches
canonical identity; generated/README.md:1-4 says ROM-generated code is omitted.
Buu recomp 453a913a9f67916b9b358776da1c1229b09a6c80: baserom.md:11-14 specifies
a different SHA-256 than the local canonical Buu image; no offsets transferred.
No dependencies added and no fresh runtime/native instrumentation needed.

## Validation so far
First suite after activation: 716 passed, 3 failed (two obsolete ticket-heading
assertions; BOM introduced in CURRENT). Corrected ticket assertions preserving
archive traversal and removed BOM. Focused workflow tests: 15 passed.
Full existing suite after activation corrections: 719 passed, three pre-existing
unknown-marker warnings. Final implementation-focused suite: 99 passed. Final full suite: 804 passed
(652 portable unit, 152 local-ROM integration), three pre-existing marker warnings.
Independent final review passed; reviewer separately ran 85 VM tests.

## Implementation contracts and capability matrix
- Pure codec/CFG: tools/webfoot/formats/script_vm.py. No paths or filesystem I/O.
- Opcode set data: tools/webfoot/data/script_specs.py. Each opcode carries
  provenance, structural/semantic evidence and known primary stack effects.
  Alternate stack operation remains explicit in the opcode rather than an AST.
- Profile-selected root contract: config/roms.yaml and identical packaged copy.
  Loader tools/webfoot/scripts.py verifies identity and packaged metadata before
  access, rehashes bytes, bounds all roots, requires full rooted coverage and
  verifies assemble identity before returning a corpus. No project/build output.
- Native operation gameplay semantics remain UNKNOWN except the narrowly stated
  dynamic table references. Their one-byte selectors are preserved even when
  their native meanings are unknown. Unknown outer opcode width fails closed.
- Varint original encodings survive, including redundant groups and negative
  zero. More than five groups, values above signed positive 31-bit raw range and
  multi-push count zero fail closed. These bounds do not claim all overflow
  behavior is understood.
- Graph reachability follows both verified conditional edges; it is not a
  claim about dynamically executable paths. Shared blocks are represented once.
  Unreachable bytes inside an explicit generic extent remain opaque and are
  never reported as decoded code; the supported canonical corpus has none.
- Assembly verifies every typed operand encoding, length, target, provenance,
  coverage and graph before returning bytes. It does not silently regenerate
  targets from stale labels. Graph editing/growth is not a declared capability.
- Script identities use profile/family/record/slot. Blocks use deterministic
  labels, while byte offsets are provenance. No speculative gameplay aliases.
- Text reverse index returns every requested ID and its known consumers; empty
  entries mean no verified consumers in this corpus, not globally unconsumed.
  Dynamic accesses remain separate, never expanded to guessed fixed IDs.

| Subsystem | LOGII exact profile | Buu exact profile |
|---|---|---|
| Script bytecode | ROUND_TRIP: static43, 86 entries / 539 bytes only | DISCOVERED |
| Script IR | ROUND_TRIP: same bounded corpus | DISCOVERED |
| Script editing / writing | not declared | not declared |
| UI/map-name text | existing ROUND_TRIP | existing text ROUND_TRIP |
| Dialogue | DISCOVERED; corpus does not enumerate it | existing ROUND_TRIP |
| Stats | DISCOVERED, unchanged | existing ROUND_TRIP |
| Script AUTHOR_NEW | not declared | not declared |

### Remaining bounded questions
Other 18 direct interpreter caller sites are outside this root-family contract.
Map scripts, interleaved dialogue containers and compressed dialogue are not
covered. There is no claim to whole-game script enumeration. This corpus has no
branches; branch handlers were verified statically and tested synthetically,
not through a canonical branching-script corpus or fresh runtime capture.
The runtime selection byte/range for dynamic text references is UNKNOWN.
Native 19/21 meanings and all unverified native stack effects remain UNKNOWN.
No free-space, relocation, DSL, executable patching or AUTHOR_NEW work occurred.

### Use
```python
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.scripts import load_scripts, script_references, reverse_text_consumers
from tools.webfoot.formats.script_vm import assemble
corpus = load_scripts(local_rom_path, RomProfileCatalog.load("config/roms.yaml"))
bytecode = assemble(corpus.ir)
consumers = reverse_text_consumers(script_references(corpus.ir), 260)
```
`bytecode` is the declared corpus extent, never a whole-ROM replacement.
No low-level project syntax was frozen; the Python IR is the current interface.
