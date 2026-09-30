/*
 * src/ByteCodeInterpreter_flagmask.c
 *
 * DECOMPILED SOURCE for sub_08003310: the routine that APPLIES a mask to the
 * flag array, and the first consumer of the mask sub_080032C2 gathers.
 *
 *   0x08003310  84 bytes  40 instructions  one terminator, native dispatch entry 187
 *
 * It sits IMMEDIATELY AFTER the gather loop, which ends at 0x08003310.
 *
 * THE ROUTINE, AS THE MACHINE EXECUTES IT
 *   0x08003310  push {r3-r7, lr}
 *   0x08003312  ldr  r1, [r0]        r1 = the counter
 *   0x08003314  subs r1, #1
 *   0x08003316  lsls r2, r1, #2
 *   0x08003318  str  r1, [r0]        counter--
 *   0x0800331A  adds r2, r2, r0
 *   0x0800331C  ldr  r4, [r2, #4]    r4 = POP 1  <- THE MASK
 *   0x0800331E  subs r1, #1
 *   0x08003320  lsls r2, r1, #2
 *   0x08003322  str  r1, [r0]        counter--
 *   0x08003324  adds r2, r2, r0
 *   0x08003326  ldr  r6, [r2, #4]    r6 = POP 2  <- THE WIDTH
 *   0x08003328  subs r1, #1
 *   0x0800332A  str  r1, [r0]        counter--
 *   0x0800332C  lsls r1, r1, #2
 *   0x0800332E  adds r0, r1, r0
 *   0x08003330  ldr  r7, [r0, #4]    r7 = POP 3  <- THE BIT OFFSET
 *   0x08003332  cmp  r4, #0
 *   0x08003334  bge  0x08003338      mask >= 0 (SIGNED) -> keep it
 *   0x08003336  movs r4, #0          otherwise mask = 0
 *   0x08003338  movs r0, #1
 *   0x0800333A  lsls r0, r6          r0 = 1 << width
 *   0x0800333C  cmp  r0, r4
 *   0x0800333E  bgt  0x08003342      (1 << width) > mask -> keep it
 *   0x08003340  subs r4, r0, #1      otherwise mask = (1 << width) - 1
 *   0x08003342  movs r5, #0          i = 0
 *   0x08003344  cmp  r6, #0
 *   0x08003346  ble  0x08003364      width <= 0 (SIGNED) -> nothing to do
 *   0x08003348  ldr  r0, [pc, #0xfc] r0 = 0x08054FBC
 *   0x0800334A  adds r1, r7, r5      r1 = offset + i
 *   0x0800334C  lsls r2, r4, #0x1f   r2 = mask << 31, putting mask bit 0 in bit 31
 *   0x0800334E  ldr  r0, [r0, #0x14] r0 = *(0x08054FBC + 0x14)
 *   0x08003350  beq  0x08003358      mask bit 0 is CLEAR...
 *   0x08003352  bl   0x08004380      ...so it is not: SET
 *   0x08003356  b    0x0800335C
 *   0x08003358  bl   0x08004396      CLEAR
 *   0x0800335C  asrs r4, r4, #1      mask >>= 1
 *   0x0800335E  adds r5, #1          i++
 *   0x08003360  cmp  r5, r6
 *   0x08003362  blt  0x08003348      loop while i < width
 *   0x08003364  pop  {r3-r7, pc}
 *
 * WHAT IT DOES
 * It is the EXACT COUNTERPART OF THE GATHER. Where the gather reads a run of flag
 * bits into a mask, this WRITES a mask into a run of flag bits:
 *
 *   for i = 0 .. width-1:
 *       if bit i of mask is set  ->  SET   the flag at (offset + i)
 *       else                     ->  CLEAR the flag at (offset + i)
 *
 * So the mask does not merely gate an action: EACH BIT OF IT BECOMES THE STATE OF
 * THE CORRESPONDING FLAG BIT. That is the first concrete engine consequence of the
 * gathered mask.
 *
 * The bit under test is mask bit 0 each iteration, because `lsls r2, r4, #0x1f`
 * moves bit 0 into bit 31 and the `beq` tests the flags from that shift; `asrs r4,
 * r4, #1` then shifts the mask down so the next bit becomes bit 0. The `i`-th
 * iteration therefore acts on mask bit `i`.
 *
 * THE TWO CLAMPS, AND BOTH ARE SIGNED
 *   1. `cmp r4,#0 ; bge` - a mask that is NEGATIVE when read as signed is replaced
 *      by 0 entirely, so a mask with bit 31 set is treated as 0 rather than as a
 *      huge value;
 *   2. `cmp r0,r4 ; bgt` with `r0 = 1 << width` - if `(1 << width)` is NOT greater
 *      than the mask, the mask becomes `(1 << width) - 1`, truncating it to the
 *      width being applied.
 *
 * WIDTH 32 IS A REAL EDGE CASE AND IS REPRODUCED, NOT CORRECTED
 * ARM LSL by a register yields ZERO for an amount of 32 or more, so for a width of
 * 32 `1 << width` is 0.
 * The second clamp then computes `0 - 1`, which is 0xFFFFFFFF, EVEN FOR A MASK OF
 * 0. Shifted arithmetically (`asrs`) that stays all ones forever, so every one of
 * the 32 iterations takes the SET branch. The routine as written therefore SETS
 * the whole run for a width of 32.
 *
 * A WIDTH OF ZERO OR LESS IS SKIPPED ENTIRELY, by the `ble`, which compares the
 * width as SIGNED. The three values are still consumed.
 *
 * STACK BEHAVIOUR
 * Three values are POPPED and nothing is pushed: the counter moves by exactly -3.
 * The mask read from the stack top is NOT written back to the stack.
 *
 * ORDERING
 * All three pops happen BEFORE any flag is touched, so the stack mutation is
 * complete before the first side effect. The offset is added to the loop index
 * immediately before each call, and the flag call happens after the mask clamp.
 *
 * STATUS, and these three lines are INDEPENDENT of one another.
 *   SEMANTIC.....PROVEN   the per-bit set/clear, both clamps, the width-32 edge
 *                         case and the width-0 skip are checked by RUNNING them;
 *                         see src/probes/flagmask_selftest.c.
 *   MODERN_BUILD.PASS     it compiles and links for ARM7TDMI Thumb with the
 *                         modern toolchain; see docs/LIFT_FLAGMASK.md.
 *   ADS_MATCH....BLOCKED  never compiled by the tool it targets. The ADS 1.2
 *                         binaries are present on this machine but the licence
 *                         present covers a different product, so the ARM
 *                         compilers cannot be run (ADS12_LICENSE_UNAVAILABLE).
 *                         No byte-match claim is made.
 *
 * WHAT IS UNKNOWN
 *   - what the flags mean. No semantic name is assigned to the mask, the flags,
 *     the array or the object, and nothing is imported from another title;
 *   - how large the array is: this routine has no bounds check either, so a large
 *     offset or width writes wherever the index arithmetic points.
 *
 * The original file may NOT be copied from 2genkidev/buusfury: that repository
 * carries no licence grant. See docs/REFERENCE_AUDIT.md.
 */

typedef unsigned int u32;

/* ------------------------------------------------------------------------- */
/* Symbols this unit references but does not reconstruct                      */
/* ------------------------------------------------------------------------- */
/* The setter and the clearer, reconstructed at src/ByteCodeInterpreter_effect.c
 * and src/ByteCodeInterpreter_clear.c. */
extern void sub_08004380(void *base, u32 value);
extern void sub_08004396(void *base, u32 value);

/* ------------------------------------------------------------------------- */
/* Absolute machine state. Redirected by the host self-check.                 */
/* ------------------------------------------------------------------------- */
#ifndef FLAGMASK_HOST_TEST

#define FLAGMASK_GLOBAL_BASE (*(u32 *)0x08054FBCu)

#else  /* FLAGMASK_HOST_TEST */

extern u32 flagmask_host_global_base;
#define FLAGMASK_GLOBAL_BASE (flagmask_host_global_base)

#endif /* FLAGMASK_HOST_TEST */

/* ------------------------------------------------------------------------- */
/* The Thumb shifts the routine performs, modelled explicitly                  */
/* ------------------------------------------------------------------------- */
/* `lsls r0, r6` where r6 is the width. ARM LSL by a register uses the bottom
 * byte of the amount, and AN AMOUNT OF 32 OR MORE YIELDS ZERO. That is not C's
 * behaviour: `1u << 32` is undefined, and MSVC on x86 masks the amount to five
 * bits and yields 1 instead. The width-32 edge case below turns on exactly this
 * difference, so the instruction is modelled rather than left to the language. */
static u32 flagmask_thumb_lsls_1(u32 amount)
{
    if (amount >= 32u) {
        return 0u;
    }
    return 1u << amount;
}

/* `asrs r4, r4, #1`, which replicates the sign bit. */
static u32 flagmask_arithmetic_shift_right_1(u32 value)
{
    if (value & 0x80000000u) {
        return (value >> 1) | 0x80000000u;
    }
    return value >> 1;
}

/* ------------------------------------------------------------------------- */
/* 0x08003310 - 84 bytes - 40 instructions                                    */
/* ------------------------------------------------------------------------- */
/*
 * The interpreter passes r0 = context and r1 = the cursor slot. This routine
 * never reads r1.
 */
void sub_08003310(void *ctx, u32 *cursor_slot)
{
    u32 *state = (u32 *)ctx;
    u32 count = state[0];
    u32 mask;
    u32 width;
    u32 offset;
    u32 i;
    void *base;

    (void)cursor_slot;   /* never read */

    /* POP 1: the top is the mask. */
    count -= 1u;
    state[0] = count;
    mask = state[count + 1u];

    /* POP 2: the width. */
    count -= 1u;
    state[0] = count;
    width = state[count + 1u];

    /* POP 3: the bit offset. */
    count -= 1u;
    state[0] = count;
    offset = state[count + 1u];

    /* CLAMP 1, SIGNED: a "negative" mask is discarded entirely. */
    if ((int)mask < 0) {
        mask = 0u;
    }

    /* CLAMP 2: truncate to the width being applied. At a width of 32 the modelled
     * `lsls` gives zero, so this computes 0 - 1 = 0xFFFFFFFF. */
    if (!(flagmask_thumb_lsls_1(width) > mask)) {
        mask = flagmask_thumb_lsls_1(width) - 1u;
    }

    /* A width of zero or less is skipped entirely; the three values are still
     * consumed above. */
    if ((int)width <= 0) {
        return;
    }

    base = (void *)(FLAGMASK_GLOBAL_BASE + 0x14u);

    for (i = 0u; i < width; i++) {
        /* The machine tests mask bit 0, having shifted it into bit 31, and then
         * shifts the mask down. */
        if ((mask & 1u) != 0u) {
            sub_08004380(base, offset + i);      /* SET   */
        } else {
            sub_08004396(base, offset + i);      /* CLEAR */
        }
        mask = flagmask_arithmetic_shift_right_1(mask);
    }
}

/* ------------------------------------------------------------------------- */
/* The unit's literal word, as declared data                                  */
/* ------------------------------------------------------------------------- */
const u32 bci_flagmask_literal_pool[1] = {
    0x08054FBCu
};
