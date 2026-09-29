/*
 * src/ByteCodeInterpreter_clear.c
 *
 * DECOMPILED SOURCE for sub_08004396: the third member of the bit-array
 * accessor trio, which CLEARS one bit.
 *
 *   0x08004396  22 bytes  11 instructions  one terminator at 0x080043AA
 *
 * It sits immediately after the setter at 0x08004380, so the reader, the setter
 * and this clearer tile 0x08004364..0x080043AC.
 *
 * This was derived on its own evidence rather than by assuming it mirrors the
 * setter: the differing instruction is `bics`, not `orrs`, and that is the whole
 * reason it clears rather than sets.
 *
 * STATUS, and these three lines are INDEPENDENT of one another.
 *   SEMANTIC.....PROVEN   the bit clear, the preservation of the other bits and
 *                         the absence of any write outside the one byte are
 *                         checked by RUNNING them; see
 *                         src/probes/clear_selftest.c.
 *   MODERN_BUILD.PASS     it compiles and links for ARM7TDMI Thumb with the
 *                         modern toolchain; see docs/LIFT_FLAGSTATE.md.
 *   ADS_MATCH....BLOCKED  never compiled by the tool it targets. The ADS 1.2
 *                         binaries are present on this machine but the licence
 *                         present covers a different product, so the ARM
 *                         compilers cannot be run (ADS12_LICENSE_UNAVAILABLE).
 *                         No byte-match claim is made.
 *
 * WHAT IS PROVEN
 *   - the INDEX SPLIT is the same as the reader's and the setter's: `asrs #3`
 *     selects the byte and the `lsls/lsrs #0x1d` pair isolates the low three
 *     bits, so the byte is at `base + (value >> 3) + 0x55`;
 *   - the BYTE-INDEX SHIFT IS ARITHMETIC, so a value with bit 31 set indexes
 *     BEFORE the base, exactly as the other two do;
 *   - it CLEARS THE BIT: `bics` computes `byte & ~(1 << (value & 7))`, which is
 *     a bit CLEAR. That single instruction is what separates it from the
 *     setter's `orrs`;
 *   - it is a READ-MODIFY-WRITE: `ldrb` reads the byte, `bics` clears the bit,
 *     `strb` writes the byte back. The other seven bits of that byte are
 *     therefore preserved;
 *   - it writes exactly ONE byte and nothing else: there is one store, and its
 *     base is the computed field address;
 *   - it makes NO calls and loads NO literals;
 *   - THERE IS NO BOUNDS CHECK and no NULL check.
 *
 * THE RETURN VALUE IS NOT DEFINED
 * The routine ends with `bx lr` with r0 still holding the computed FIELD
 * ADDRESS, not a status or a boolean. Nothing in the code establishes it, so the
 * reconstruction returns void rather than inventing a result.
 *
 * CLEARING AN ALREADY-CLEAR BIT IS A NO-OP, and clearing one bit leaves its
 * seven neighbours untouched. Both are asserted.
 *
 * WHAT IS UNKNOWN
 *   - what the bit means. No semantic name is assigned to the bit, the array or
 *     the object;
 *   - how large the array is.
 *
 * The original file may NOT be copied from 2genkidev/buusfury: that repository
 * carries no licence grant. See docs/REFERENCE_AUDIT.md.
 */

typedef unsigned int u32;
typedef unsigned char u8;

/* ------------------------------------------------------------------------- */
/* An arithmetic shift right by three, as `asrs r2, r1, #3` performs           */
/* ------------------------------------------------------------------------- */
static u32 clear_arithmetic_shift_right_3(u32 value)
{
    if (value & 0x80000000u) {
        return (value >> 3) | 0xE0000000u;
    }
    return value >> 3;
}

/* ------------------------------------------------------------------------- */
/* 0x08004396 - 22 bytes - 11 instructions                                    */
/* ------------------------------------------------------------------------- */
void sub_08004396(void *base, u32 value)
{
    u32 byte_index = clear_arithmetic_shift_right_3(value);
    u32 bit_index = value & 7u;

    /* 32-bit address arithmetic on purpose: on the target this is exactly
     * `adds r0, r2, r0` followed by `adds r0, #0x50`, and the sign-extended
     * index can point below the base. */
    u8 *field = (u8 *)((u32)base + byte_index + 0x50u);

    /* Read, clear the one bit, write back. `bics` is `r2 & ~r1`, which is what
     * makes this the clearer rather than the setter. */
    field[5] = (u8)(field[5] & (u8)~(1u << bit_index));
}

/* ------------------------------------------------------------------------- */
/* This unit has no literal pool                                              */
/* ------------------------------------------------------------------------- */
/*
 * Every instruction above is register-only: there is no `ldr rX,[pc,#N]`, so
 * there is no pool word to declare. That is asserted by the lift harness rather
 * than assumed.
 */
