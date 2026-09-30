/*
 * src/IwramBlock.c
 *
 * DECOMPILED SOURCE for the four runtime-installed block-memory routines that
 * live in the ARM code block the boot code copies into IWRAM.
 *
 *   0x087B810C  ARM  64 bytes  block copy, 4-byte units      IWRAM 0x03000768
 *   0x087B814C  ARM  84 bytes  block fill, replicated word   IWRAM 0x030007A8
 *   0x087B81A0  ARM  92 bytes  block copy, 2-byte units      IWRAM 0x030007FC
 *   0x087B81FC  ARM  16 bytes  block fill, 2-byte units      IWRAM 0x03000858
 *
 * The four tile 0x087B810C..0x087B820C with no padding and no literal pool:
 * every one is register-only, so the pool test is not applicable rather than
 * failed, and the report says which it is.
 *
 * WHY THEY ARE IN *ROM* AT 0x087B81xx AND RUN FROM IWRAM
 * The 4100 bytes at ROM 0x087B79A4..0x087B89A8 are the image of IWRAM
 * 0x03000000..0x03001004. The arm7tdmi reset code at 0x080000C0 sets up DMA3 a
 * second time with SAD = 0x087B79A4, DAD = 0x03000000 and the 32-bit control
 * word 0x84000401, i.e. 0x0401 = 1025 words = 4100 bytes, 32-bit transfers,
 * both addresses incrementing, immediate start. The block is a verbatim copy,
 * so IWRAM 0x03000000 + k holds the ROM byte at 0x087B79A4 + k for every k in
 * [0, 4100) and the content of every IWRAM address in the block is statically
 * known. Nothing else in the image writes that range.
 *
 * Each routine is reached from Thumb game code through a ROM veneer - a Thumb
 * `bx pc` followed by an ARM `ldr pc,[pc,#-4]` whose literal IS the absolute
 * IWRAM address:
 *
 *   0x08049138 -> 0x03000768   0x0804912C -> 0x030007A8
 *   0x08049144 -> 0x030007FC   0x08049168 -> 0x03000858
 *
 * The veneer jumps to the IWRAM address directly; it does not load a function
 * pointer from it, so the callee and the argument order ARE statically
 * resolvable. An earlier ticket recorded the opposite - "jumps to whatever is
 * stored at 0x030007A8 ... not statically resolvable" - and that reading was
 * wrong: 0xE51FF004 is `ldr pc,[pc,#-4]`, which puts the literal itself into
 * PC. The literal is the destination, not a slot holding one. The correction is
 * carried in docs/LIFT_IWRAM_RUNTIME.md.
 *
 * THE SHARED SHAPE
 * All four are the same generated shape, and the shape is the contract:
 *
 *   * a 32-byte fast path for the 4-byte pair and a 16-byte one for the 2-byte
 *     pair, then a tail that runs while the remaining count is
 *     signed-greater-than zero;
 *   * every count is in BYTES, including the 2-byte pair. That is what
 *     `subs r2, r2, #0x10` after eight halfword moves and `subs r2, r2, #0x2`
 *     after one halfword move both say;
 *   * the tail is reached by a SIZED compare, so it RUNS AT LEAST ONCE. A
 *     zero-size call therefore still stores one unit (16 bytes for the 2-byte
 *     copy, whose entry dispatch cannot produce fewer than eight halfwords), and
 *     a size that is not a multiple of the unit is ROUNDED UP to the next unit;
 *   * NO ZERO CHECK and NO ALIGNMENT CHECK. Neither is added here: inventing a
 *     guard would reconstruct something the ROM does not contain.
 *
 * Per routine:
 *
 *   sub_087B810C copy : copies r2 bytes; the fast path moves 32 at a time, then
 *                       the tail moves ceil(remaining/4) words.
 *   sub_087B814C fill : stores the WHOLE 32-bit value in r1, eight copies of it
 *                       per fast iteration. r1 is NEVER masked to a byte, which
 *                       is what makes this a word fill rather than a `memset`:
 *                       its callers pass a full 32-bit pattern, and the call in
 *                       sub_08011B04 passes an address (0x03002A4C). Masking
 *                       would change what the game writes. The value is
 *                       replicated into r3, r4, r5, r6, r7, r8 and ip before
 *                       the loop, which is the proof of the second argument.
 *   sub_087B81A0 copy : copies r2 bytes as halfwords. The entry dispatches
 *                       through `add pc, pc, r3, lsl #2` with r3 = (16 - r2) &
 *                       0xE, an offset in PAIRS, so the first pass moves
 *                       8 - ((16 - r2) & 0xE >> 1) halfwords and then the loop
 *                       moves 8 halfwords (16 bytes, matching
 *                       `subs r2, r2, #0x10`) while the signed remainder is
 *                       positive. r2 is rounded UP to an even number.
 *   sub_087B81FC fill : stores the low halfword of r1 and subtracts two, so it
 *                       stores ceil(r2/2) halfwords and at least one.
 *
 * WHAT THEY ARE CALLED BY, where the call is statically visible
 *   * sub_08011A4E calls 0x08049138 with r0 = &elements[i], r1 = &elements[i+1]
 *     and r2 = (count-1-i)*4: a COMPACTION copy, moving a list's tail down over
 *     a removed slot. This is a call site whose three arguments are all
 *     resolved, and it is what fixes the copy's byte-counted contract.
 *   * sub_08011B04 calls 0x0804912C five times; see that unit.
 *
 * STATUS, and these three lines are INDEPENDENT of one another.
 *   SEMANTIC.....PROVEN   the 32-byte fast path, the round-up tails, the
 *                         zero-size store, the unmasked 32-bit fill and the
 *                         halfword entry dispatch are checked by RUNNING them;
 *                         see src/probes/iwramblock_selftest.c.
 *   MODERN_BUILD.PASS     it compiles and links for arm7tdmi in ARM state with
 *                         the modern toolchain; see docs/LIFT_IWRAM_RUNTIME.md.
 *   ADS_MATCH....BLOCKED  never compiled by the tool it targets. The ADS 1.2
 *                         binaries are present on this machine but the licence
 *                         present covers a different product
 *                         (ADS12_LICENSE_UNAVAILABLE). No byte-match claim is
 *                         made.
 *
 * EVIDENCE vs PLACEHOLDER
 *   Evidence: every instruction, size and offset above, all read from the
 *   cartridge; the DMA3 register values, read from the reset code's own literal
 *   pool. Placeholder: the C types and the names. The names are the ROM
 *   addresses, because the disassembly fixes offsets and access widths and the
 *   game's own names are not recoverable. Whether the block was authored as C or
 *   as assembly is NOT established, and no ADS library function name is claimed
 *   for any routine here.
 *
 * The original may NOT be copied from 2genkidev/buusfury: that repository
 * carries no licence grant. See docs/REFERENCE_AUDIT.md.
 */

typedef unsigned int u32;
typedef unsigned short u16;
typedef unsigned char u8;
typedef int s32;

/* The fast paths move one 32-byte block (eight words) and one 16-byte block
 * (eight halfwords) per iteration. */
#define BLOCK_STRIDE_WORD 0x20u
#define BLOCK_STRIDE_HALF 0x10u
/* The unit widths. Every size argument is in BYTES. */
#define UNIT_WORD 4u
#define UNIT_HALFWORD 2u
/* Halfwords per pass of the 2-byte copy, and the value the entry dispatch
 * subtracts the size from. */
#define HALFWORDS_PER_PASS 8u
#define HALFWORD_DISPATCH_BASE 16u

/* ------------------------------------------------------------------------- */
/* 0x087B810C - 64 bytes - the 4-byte block copy                              */
/* r0 = destination, r1 = source, r2 = size in bytes                          */
/* ------------------------------------------------------------------------- */
void sub_087B810C(u32 destination, u32 source, u32 size)
{
    u8 *dst = (u8 *)destination;
    const u8 *src = (const u8 *)source;

    if ((s32)size >= (s32)BLOCK_STRIDE_WORD) {
        size -= BLOCK_STRIDE_WORD;               /* `sub r2, r2, #0x20` */
        do {
            u32 word;
            for (word = 0u; word < 8u; word++) {
                ((u32 *)dst)[word] = ((const u32 *)src)[word];
            }
            dst += BLOCK_STRIDE_WORD;
            src += BLOCK_STRIDE_WORD;
            size -= BLOCK_STRIDE_WORD;
        } while ((s32)size > 0);
        size += BLOCK_STRIDE_WORD;
        if (size == 0u) {
            return;                              /* `bxeq lr` */
        }
    }

    /* The tail is a do/while: it is entered by a SIZED compare and runs at
     * least once, so a size below 4 - including zero - still moves 4 bytes. */
    do {
        *(u32 *)dst = *(const u32 *)src;
        dst += UNIT_WORD;
        src += UNIT_WORD;
        size -= UNIT_WORD;
    } while ((s32)size > 0);
}

/* ------------------------------------------------------------------------- */
/* 0x087B814C - 84 bytes - the 4-byte block fill                              */
/* r0 = destination, r1 = the 32-bit value to replicate, r2 = size in bytes    */
/* ------------------------------------------------------------------------- */
void sub_087B814C(u32 destination, u32 value, u32 size)
{
    u8 *dst = (u8 *)destination;

    if ((s32)size >= (s32)BLOCK_STRIDE_WORD) {
        size -= BLOCK_STRIDE_WORD;
        do {
            u32 word;
            for (word = 0u; word < 8u; word++) {
                ((u32 *)dst)[word] = value;      /* r1 replicated, NOT masked */
            }
            dst += BLOCK_STRIDE_WORD;
            size -= BLOCK_STRIDE_WORD;
        } while ((s32)size > 0);
        size += BLOCK_STRIDE_WORD;
        if (size == 0u) {
            return;
        }
    }

    do {
        *(u32 *)dst = value;
        dst += UNIT_WORD;
        size -= UNIT_WORD;
    } while ((s32)size > 0);
}

/* ------------------------------------------------------------------------- */
/* 0x087B81A0 - 92 bytes - the 2-byte block copy                              */
/* r0 = destination, r1 = source, r2 = size in bytes                          */
/* ------------------------------------------------------------------------- */
void sub_087B81A0(u32 destination, u32 source, u32 size)
{
    u8 *dst = (u8 *)destination;
    const u8 *src = (const u8 *)source;
    u32 pass;

    /* `rsb r3, r2, #0x10` / `and r3, r3, #0xe` / `add pc, pc, r3, lsl #2`.
     * r3 is a byte offset that is always a multiple of eight, so it indexes
     * the eight halfword moves directly; the entry therefore performs
     * 8 - ((16 - size) & 0xE) / 2 of them. size = 0 enters at the first move
     * and copies all eight halfwords. */
    pass = HALFWORDS_PER_PASS
         - (((HALFWORD_DISPATCH_BASE - size) & 0xEu) >> 1);
    while (pass != 0u) {
        *(u16 *)dst = *(const u16 *)src;
        dst += UNIT_HALFWORD;
        src += UNIT_HALFWORD;
        pass -= 1u;
    }

    /* `subs r2, r2, #0x10` / `bgt`: eight more halfwords per further pass. */
    size -= BLOCK_STRIDE_HALF;
    while ((s32)size > 0) {
        pass = HALFWORDS_PER_PASS;
        while (pass != 0u) {
            *(u16 *)dst = *(const u16 *)src;
            dst += UNIT_HALFWORD;
            src += UNIT_HALFWORD;
            pass -= 1u;
        }
        size -= BLOCK_STRIDE_HALF;
    }
}

/* ------------------------------------------------------------------------- */
/* 0x087B81FC - 16 bytes - the 2-byte block fill                              */
/* r0 = destination, r1 = the value whose LOW HALFWORD is stored,             */
/* r2 = size in bytes                                                         */
/* ------------------------------------------------------------------------- */
void sub_087B81FC(u32 destination, u32 value, u32 size)
{
    u8 *dst = (u8 *)destination;

    do {
        *(u16 *)dst = (u16)value;
        dst += UNIT_HALFWORD;
        size -= UNIT_HALFWORD;
    } while ((s32)size > 0);
}
