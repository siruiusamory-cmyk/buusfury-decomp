/*
 * src/ByteCodeInterpreter_append.c
 *
 * DECOMPILED SOURCE for sub_0801191A: the routine native dispatch slot 178 drives
 * with the IWRAM object 0x03001C4C and the result of sub_0802BFBC.
 *
 *   0x0801191A  18 bytes  9 instructions  one terminator at 0x0801192A
 *
 * A LEAF: no calls and no literal pool. Nothing further had to be followed, so the
 * effect below is established by this routine alone.
 *
 * THE ROUTINE, ALL NINE INSTRUCTIONS
 *   0x0801191A  adds r0, #4        r0 = object + 4
 *   0x0801191C  adds r2, r1, #0    r2 = the incoming value
 *   0x0801191E  ldr  r1, [r0]      r1 = *(object + 4)      <- THE COUNT
 *   0x08011920  adds r3, r1, #1    r3 = count + 1
 *   0x08011922  str  r3, [r0]      *(object + 4) = count + 1
 *   0x08011924  lsls r1, r1, #2    r1 = count * 4
 *   0x08011926  adds r0, r1, r0    r0 = (object + 4) + count*4
 *   0x08011928  str  r2, [r0, #4]  *((object + 4) + count*4 + 4) = value
 *   0x0801192A  bx   lr            the single exit
 *
 * THE CONCRETE EFFECT
 * The object carries a COUNT at +0x04 and an array of 32-bit values beginning at
 * +0x08. The routine
 *
 *     APPENDS the incoming value at index `count`,
 *     then increments that count by one.
 *
 * Written out, `sub_0801191A(object, value)` performs
 *
 *     ((u32 *)object)[1] = ((u32 *)object)[1] + 1;         the count at +0x04
 *     *(u32 *)(object + 8 + 4*count) = value;              the element at +0x08+4*i
 *
 * so the value lands at `object + 0x08 + 4*count` and the new count is `count + 1`.
 * The count is READ BEFORE it is incremented, so element `count` is written and not
 * element `count+1`.
 *
 * This is the first concrete effect of the chain that starts at native slot 178:
 * that handler pops three VM values, computes one value from them, and hands it
 * here, where it is APPENDED to the object's array. The object is therefore a
 * growable-by-write collection rather than a single scalar, and the handler is a
 * producer for it.
 *
 * OBJECT-RELATIVE ACCESSES, ALL OF THEM
 *   +0x04  read then written, 32-bit: the count
 *   +0x08 + 4*count  written, 32-bit: the appended element
 *   +0x00  NOT TOUCHED. Nothing in this routine reads or writes it.
 * There is no other access in the routine.
 *
 * ORDER
 * The count is loaded first, then stored back incremented, and only then is the
 * element written. A reader of the count therefore cannot observe a count that
 * promises an element which has not been written yet, because the element write
 * follows the count write but both are complete before the routine returns and
 * nothing interrupts them.
 *
 * THERE IS NO CAPACITY CHECK
 * Nothing compares the count against a limit, and no capacity is reachable from
 * this routine at all. A large count writes far past any sane array end. That is
 * the machine's behaviour and is reproduced rather than guarded: no check was
 * added.
 *
 * THE RETURN VALUE IS NOT DEFINED
 * The routine ends with `bx lr` with r0 holding the address of the element it just
 * wrote, not a status and not a boolean. Nothing in the code establishes it, so the
 * reconstruction returns void rather than inventing a result.
 *
 * THE INCOMING CONTRACT, RE-PROVEN FROM THE CALLER
 * Native dispatch slot 178 at 0x08003030 calls this with
 *   r0 = *(0x08054FBC + 0x18), which the static layout resolves to 0x03001C4C
 *   r1 = the value returned by sub_0802BFBC
 * This routine reads r0 as the object and r1 as the value, consistently with that.
 *
 * STATUS, and these three lines are INDEPENDENT of one another.
 *   SEMANTIC.....PROVEN   the element index, the count increment, the exact
 *                         destination address and the verbatim value are checked by
 *                         RUNNING them; see src/probes/append_selftest.c.
 *   MODERN_BUILD.PASS     it compiles and links for ARM7TDMI Thumb with the modern
 *                         toolchain; see docs/LIFT_APPEND.md.
 *   ADS_MATCH....BLOCKED  never compiled by the tool it targets. The ADS 1.2
 *                         binaries are present on this machine but the licence
 *                         present covers a different product (ADS12_LICENSE_UNAVAILABLE).
 *                         No byte-match claim is made.
 *
 * WHAT IS UNKNOWN
 *   - what the object at 0x03001C4C is, and what its +0x00 field means;
 *   - what the appended values are used for, and who reads them;
 *   - whether any capacity limit exists elsewhere. No semantic name is assigned to
 *     the object, the array or the count, and nothing is imported from another
 *     title.
 *
 * The original file may NOT be copied from 2genkidev/buusfury: that repository
 * carries no licence grant. See docs/REFERENCE_AUDIT.md.
 */

typedef unsigned int u32;
typedef unsigned char u8;

/* ------------------------------------------------------------------------- */
/* 0x0801191A - 18 bytes - 9 instructions                                     */
/* ------------------------------------------------------------------------- */
void sub_0801191A(void *object, u32 value)
{
    /* r0 is advanced to +4 first, and that address is what stays live. */
    u32 *count_slot = (u32 *)((u32)object + 4u);
    u32 count = *count_slot;

    /* The count is written back BEFORE the element is stored, exactly as the
     * machine orders it. */
    *count_slot = count + 1u;

    /* 32-bit address arithmetic on purpose: this is `lsls r1, r1, #2` then
     * `adds r0, r1, r0` then `str r2, [r0, #4]`, so the element lands at
     * object + 8 + 4*count with no bounds test of any kind. */
    *(u32 *)((u8 *)count_slot + count * 4u + 4u) = value;
}

/* ------------------------------------------------------------------------- */
/* This unit has no literal pool                                              */
/* ------------------------------------------------------------------------- */
/*
 * Every instruction above is register-only: there is no `ldr rX,[pc,#N]`, so there
 * is no pool word to declare. That is asserted by the lift harness rather than
 * assumed.
 */
