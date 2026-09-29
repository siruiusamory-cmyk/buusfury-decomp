/*
 * src/ByteCodeInterpreter_flagread.c
 *
 * DECOMPILED SOURCE for sub_08004364: the reader of the bit array that
 * sub_08004380 sets. It answers "is bit (value & 7) of the byte at
 * base + (value >> 3) + 0x55 set?" with a boolean.
 *
 *   0x08004364  28 bytes  14 instructions  two terminators
 *
 * A LEAF: no calls and no literal pool. It sits immediately before the setter at
 * 0x08004380, and the clearer at 0x08004396 sits immediately after it, so the
 * three tile 0x08004364..0x080043AC as one bit-array accessor trio.
 *
 * THE ROUTINE, ALL FOURTEEN INSTRUCTIONS
 *   0x08004364  asrs r2, r1, #3        r2 = value >> 3      (ARITHMETIC)
 *   0x08004366  adds r0, r2, r0        r0 = base + (value >> 3)
 *   0x08004368  lsls r2, r1, #0x1d     r2 = value << 29
 *   0x0800436A  adds r0, #0x50         r0 = base + (value >> 3) + 0x50
 *   0x0800436C  ldrb r0, [r0, #5]      r0 = the byte at +5
 *   0x0800436E  lsrs r2, r2, #0x1d     r2 = value & 7
 *   0x08004370  movs r1, #1
 *   0x08004372  lsls r1, r2            r1 = 1 << (value & 7)
 *   0x08004374  ands r0, r1            r0 = byte & mask
 *   0x08004376  beq  0x0800437C        when the masked bit is zero...
 *   0x08004378  movs r0, #1            ...otherwise return 1
 *   0x0800437A  bx   lr
 *   0x0800437C  movs r0, #0            return 0
 *   0x0800437E  bx   lr
 *
 * STATUS, and these three lines are INDEPENDENT of one another.
 *   SEMANTIC.....PROVEN   the index split, the boolean result and the fact that
 *                         nothing is written are checked by RUNNING them; see
 *                         src/probes/flagread_selftest.c.
 *   MODERN_BUILD.PASS     it compiles and links for ARM7TDMI Thumb with the
 *                         modern toolchain; see docs/LIFT_FLAGREAD.md.
 *   ADS_MATCH....BLOCKED  never compiled by the tool it targets. The ADS 1.2
 *                         binaries are present on this machine but the licence
 *                         present covers a different product, so the ARM
 *                         compilers cannot be run (ADS12_LICENSE_UNAVAILABLE).
 *                         No byte-match claim is made.
 *
 * WHAT IS PROVEN
 *   - the INDEX SPLIT is identical to the setter's: `asrs #3` selects the byte
 *     and the `lsls/lsrs #0x1d` pair isolates the low three bits. The byte read
 *     is therefore at `base + (value >> 3) + 0x55`, the same byte the setter
 *     writes;
 *   - the BYTE-INDEX SHIFT IS ARITHMETIC, so a value with bit 31 set indexes
 *     BEFORE the base, exactly as the setter does;
 *   - it TESTS THE BIT FOR SET: `ands` masks the byte with `1 << (value & 7)`
 *     and the routine branches on whether the result is zero;
 *   - the RETURN VALUE IS A NORMALISED BOOLEAN, `0` or `1`. It is not the masked
 *     byte, so a caller cannot see which bit was masked;
 *   - it WRITES NOTHING. There is no store anywhere in the routine, so the byte
 *     it tests is left exactly as it was. That is what makes it a reader rather
 *     than the setter or the clearer;
 *   - it makes NO calls and loads NO literals;
 *   - THERE IS NO BOUNDS CHECK and no NULL check.
 *
 * THE FIRST OBSERVABLE CONSEQUENCE
 * Three call sites consume the boolean, and all three prove that the bit is
 * treated as a predicate:
 *
 *   0x080007C4  `bl sub_08004364` then `str r0, [r4]`
 *               -> the boolean is MATERIALISED into a word slot: (bit set)?1:0
 *   0x080007DA  `bl sub_08004364` then `movs r1,#1 ; subs r0, r1, r0 ; str r0, [r4]`
 *               -> the INVERTED boolean is materialised: (bit clear)?1:0
 *   0x080032EE  `bl sub_08004364` then `cmp r0,#0 ; beq ... ; movs r0,#1 ; lsls r0,r4 ; orrs r6,r0`
 *               -> the boolean GATES setting a bit in a packed local word, i.e.
 *                  a gather loop that copies set bits out of the array
 *
 * So the bit's first concrete consequence is that it becomes a 0/1 value in an
 * engine slot, and one caller deliberately inverts it. That is as far as this
 * ticket follows it.
 *
 * WHAT THE BIT MEANS IS STILL UNKNOWN
 *   - no semantic name is assigned to the flag, the array or the object;
 *   - how large the array is is unknown, so which values are in range cannot be
 *     stated;
 *   - what reads the materialised word afterwards is not followed;
 *   - nothing is imported from another LoG title.
 *
 * The original file may NOT be copied from 2genkidev/buusfury: that repository
 * carries no licence grant. See docs/REFERENCE_AUDIT.md.
 */

typedef unsigned int u32;
typedef unsigned char u8;

/* ------------------------------------------------------------------------- */
/* An arithmetic shift right by three, as `asrs r2, r1, #3` performs           */
/* ------------------------------------------------------------------------- */
/* C's >> on a negative signed value is implementation-defined and >> on an
 * unsigned value is logical, so the instruction is modelled explicitly. */
static u32 flagread_arithmetic_shift_right_3(u32 value)
{
    if (value & 0x80000000u) {
        return (value >> 3) | 0xE0000000u;
    }
    return value >> 3;
}

/* ------------------------------------------------------------------------- */
/* 0x08004364 - 28 bytes - 14 instructions                                    */
/* ------------------------------------------------------------------------- */
/*
 * Returns 1 when the bit is set and 0 when it is clear. It reads the byte and
 * never writes it.
 */
u32 sub_08004364(void *base, u32 value)
{
    u32 byte_index = flagread_arithmetic_shift_right_3(value);
    u32 bit_index = value & 7u;

    /* 32-bit address arithmetic on purpose: on the target this is exactly
     * `adds r0, r2, r0` followed by `adds r0, #0x50`, and the sign-extended
     * index can point below the base. */
    const u8 *field = (const u8 *)((u32)base + byte_index + 0x50u);

    /* The byte is only read. `ands` then discards everything but the one bit. */
    u32 masked = (u32)field[5] & (1u << bit_index);

    if (masked == 0u) {
        return 0u;      /* 0x0800437C */
    }
    return 1u;          /* 0x08004378 */
}

/* ------------------------------------------------------------------------- */
/* This unit has no literal pool                                              */
/* ------------------------------------------------------------------------- */
/*
 * Every instruction above is register-only: there is no `ldr rX,[pc,#N]`, so
 * there is no pool word to declare. That is asserted by the lift harness rather
 * than assumed.
 */
