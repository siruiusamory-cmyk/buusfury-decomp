/*
 * src/ByteCodeInterpreter_effect.c
 *
 * DECOMPILED SOURCE for sub_08004380: the routine that gives the popped VM value
 * from native dispatch entry 29 its concrete effect.
 *
 *   0x08004380  22 bytes  11 instructions  one terminator at 0x08004394
 *
 * A LEAF: no calls and no literal pool. Nothing further had to be followed, so
 * the effect below is established by this routine alone.
 *
 * THE ROUTINE, ALL ELEVEN INSTRUCTIONS
 *   0x08004380  asrs r2, r1, #3        r2 = value >> 3      (ARITHMETIC)
 *   0x08004382  adds r0, r2, r0        r0 = base + (value >> 3)
 *   0x08004384  lsls r3, r1, #0x1d     r3 = value << 29
 *   0x08004386  adds r0, #0x50         r0 = base + (value >> 3) + 0x50
 *   0x08004388  ldrb r2, [r0, #5]      r2 = the byte at +5 from there
 *   0x0800438A  lsrs r3, r3, #0x1d     r3 = value & 7
 *   0x0800438C  movs r1, #1
 *   0x0800438E  lsls r1, r3            r1 = 1 << (value & 7)
 *   0x08004390  orrs r1, r2            r1 = that bit | the byte
 *   0x08004392  strb r1, [r0, #5]      the byte at +5 := r1
 *   0x08004394  bx   lr                the single exit
 *
 * THE CONCRETE EFFECT
 * Given a base object and a value, the routine
 *
 *     SETS BIT (value & 7) OF THE BYTE AT  base + (value >> 3) + 0x55
 *
 * and changes nothing else. The two shifts are the standard bit-array split: the
 * value's low three bits select the bit within the byte and the rest selects
 * which byte. The byte is read, one bit is OR-ed in, and the byte is written
 * back, so the other seven bits of that byte are preserved.
 *
 * This is the first externally observable effect of the VM value delivered by
 * native dispatch entry 29: the caller passes `*(u32*)(0x08054FBC + 0x14)` as the
 * base and the popped stack value as the bit number, and a single bit inside that
 * object is set.
 *
 * STATUS, and these three lines are INDEPENDENT of one another.
 *   SEMANTIC.....PROVEN   the bit arithmetic, the byte address, the
 *                         read-modify-write and the negative-value behaviour are
 *                         checked by RUNNING them; see src/probes/effect_selftest.c.
 *   MODERN_BUILD.PASS     it compiles and links for ARM7TDMI Thumb with the
 *                         modern toolchain; see docs/LIFT_EFFECT.md.
 *   ADS_MATCH....BLOCKED  never compiled by the tool it targets. The ADS 1.2
 *                         binaries are present on this machine but the licence
 *                         present covers a different product, so the ARM
 *                         compilers cannot be run (ADS12_LICENSE_UNAVAILABLE).
 *                         No byte-match claim is made.
 *
 * THE SHIFT IS ARITHMETIC, AND THAT MATTERS
 * `asrs r2, r1, #3` replicates the sign bit, so a value with bit 31 set makes the
 * byte index NEGATIVE and the write lands BEFORE the base instead of after it:
 *
 *     value = 0xFFFFFFFF  ->  value >> 3 = 0xFFFFFFFF (-1), value & 7 = 7
 *                         ->  the byte written is base + 0x54, bit 7
 *     value = 0x80000000  ->  value >> 3 = 0xF0000000, value & 7 = 0
 *                         ->  a byte far BELOW the base, bit 0
 *
 * A logical shift would have placed both far ABOVE the base. The reconstruction
 * reproduces the arithmetic shift exactly, and models it explicitly rather than
 * leaving it to the compiler, because C's right shift of a negative signed value
 * is implementation-defined.
 *
 * THERE IS NO BOUNDS CHECK
 * Nothing tests the value against the object's size, and nothing tests the base
 * for NULL. Any value selects a byte, and the byte is written. No guard was
 * added, because the original performs none.
 *
 * WHAT IS UNKNOWN
 *   - what the bit MEANS. It is a bit in a byte array inside an object reachable
 *     from 0x08054FBC + 0x14; no name is assigned to the array, the object, or
 *     the bit, and nothing is imported from another title;
 *   - how large that byte array is, so which values are in range cannot be
 *     stated from this routine alone;
 *   - what reads the bit afterwards.
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
 * unsigned value is logical, so the instruction is modelled explicitly. The top
 * three bits are replicated when the sign bit is set. */
static u32 arithmetic_shift_right_3(u32 value)
{
    if (value & 0x80000000u) {
        return (value >> 3) | 0xE0000000u;
    }
    return value >> 3;
}

/* ------------------------------------------------------------------------- */
/* 0x08004380 - 22 bytes - 11 instructions                                    */
/* ------------------------------------------------------------------------- */
void sub_08004380(void *base, u32 value)
{
    u32 byte_index = arithmetic_shift_right_3(value);
    u32 bit_index = value & 7u;

    /* 32-bit address arithmetic on purpose: on the target this is exactly
     * `adds r0, r2, r0` followed by `adds r0, #0x50`, and the sign-extended
     * index can point below the base. */
    u8 *field = (u8 *)((u32)base + byte_index + 0x50u);

    /* Read, set one bit, write back: the other seven bits are preserved. */
    field[5] = (u8)(field[5] | (u8)(1u << bit_index));
}

/* ------------------------------------------------------------------------- */
/* This unit has no literal pool                                              */
/* ------------------------------------------------------------------------- */
/*
 * Every instruction above is register-only: there is no `ldr rX,[pc,#N]`, so
 * there is no pool word to declare. That is asserted by the lift harness rather
 * than assumed.
 */
