/*
 * src/ByteCodeInterpreter_booluse.c
 *
 * DECOMPILED SOURCE for the two routines that materialise the normalised boolean
 * from sub_08004364 into the VM value stack: the unary "flag" and "not flag"
 * transforms.
 *
 *   0x080007B6  22 bytes  10 instructions  one terminator at 0x080007CA
 *   0x080007CC  26 bytes  12 instructions  one terminator at 0x080007E4
 *
 * They are adjacent, and the consumer that reads their result, sub_080007E6,
 * begins immediately after them at 0x080007E6. Each loads the same single
 * literal, 0x08054FBC.
 *
 * THE TWO ROUTINES
 *
 *   0x080007B6  push {r4, lr}
 *   0x080007B8  ldr  r1, [r0]        r1 = context+0x00, the COUNTER
 *   0x080007BA  lsls r1, r1, #2      r1 = count * 4
 *   0x080007BC  adds r4, r1, r0      r4 = context + count*4
 *   0x080007BE  ldr  r0, [pc, #0x118]  r0 = 0x08054FBC
 *   0x080007C0  ldr  r1, [r4]        r1 = the word at r4
 *   0x080007C2  ldr  r0, [r0, #0x14] r0 = *(0x08054FBC + 0x14)
 *   0x080007C4  bl   0x08004364      flag = test(r0, r1)
 *   0x080007C8  str  r0, [r4]        *(context + count*4) = flag
 *   0x080007CA  pop  {r4, pc}
 *
 *   0x080007CC  push {r4, lr}
 *   0x080007CE  ldr  r1, [r0]
 *   0x080007D0  lsls r1, r1, #2
 *   0x080007D2  adds r4, r1, r0
 *   0x080007D4  ldr  r0, [pc, #0x100]
 *   0x080007D6  ldr  r1, [r4]
 *   0x080007D8  ldr  r0, [r0, #0x14]
 *   0x080007DA  bl   0x08004364      flag = test(r0, r1)
 *   0x080007DE  movs r1, #1
 *   0x080007E0  subs r0, r1, r0      r0 = 1 - flag
 *   0x080007E2  str  r0, [r4]        *(context + count*4) = 1 - flag
 *   0x080007E4  pop  {r4, pc}
 *
 * THE DESTINATION IS THE SAME LOCATION AT BOTH SITES
 * Both compute `r4 = context + count*4` from the counter at `context+0x00`, and
 * the value stack holds `values[i]` at `context + 4 + 4*i`. So
 *
 *     context + count*4  ==  context + 4 + 4*(count-1)
 *                        ==  values[count-1]  ==  THE TOP OF THE STACK
 *
 * Both routines therefore REPLACE THE STACK TOP IN PLACE and leave the counter
 * alone: this is not a pop, and not a separate word. The two differ only in
 * whether the replacement is the flag or its inverse.
 *
 * STATUS, and these three lines are INDEPENDENT of one another.
 *   SEMANTIC.....PROVEN   the in-place replacement, the inverted variant, the
 *                         unchanged counter and the empty-stack case are checked
 *                         by RUNNING them; see src/probes/booluse_selftest.c.
 *   MODERN_BUILD.PASS     they compile and link for ARM7TDMI Thumb with the
 *                         modern toolchain; see docs/LIFT_BOOLUSE.md.
 *   ADS_MATCH....BLOCKED  never compiled by the tool they target. The ADS 1.2
 *                         binaries are present on this machine but the licence
 *                         present covers a different product, so the ARM
 *                         compilers cannot be run (ADS12_LICENSE_UNAVAILABLE).
 *                         No byte-match claim is made.
 *
 * WHAT IS PROVEN
 *   - both replace `values[count-1]`, the stack TOP, in place;
 *   - the COUNTER IS NOT CHANGED: neither routine writes `context+0x00`;
 *   - the first stores the flag, the second stores `1 - flag`, so the second is
 *     the exact inverse of the first for a 0/1 input;
 *   - both RETURN the value they stored, in r0;
 *   - both make exactly ONE call, to the reader sub_08004364, and load ONE
 *     literal;
 *   - THE STACK IS NOT CHECKED FOR BEING EMPTY. With a counter of zero the
 *     computed address is `context + 0`, so `r4` points at the COUNTER WORD
 *     ITSELF: the value read is the counter, and the store REPLACES THE COUNTER
 *     with the flag. Nothing is popped and no guard exists. That is recorded as
 *     the code's actual behaviour; no check was added.
 *
 * THE FIRST CONCRETE CONSEQUENCE, PROVEN THROUGH THE ALREADY-LIFTED CONSUMER
 * `sub_080007E6`, which begins at 0x080007E6, pops `values[count-1]` and passes
 * it to `sub_08004380`. Chained:
 *
 *     unary transform  ->  values[count-1] becomes the boolean 0 or 1
 *     sub_080007E6     ->  pops it and passes it as sub_08004380's `value`
 *     sub_08004380     ->  sets bit (value & 7) of byte base + (value >> 3) + 0x55
 *
 * With a boolean input the bit index is 0 or 1, so the boolean SELECTS WHICH BIT
 * IS SET in the first byte of the flag array: bit 0 when the tested flag was
 * clear, bit 1 when it was set. The boolean is therefore used as a BIT INDEX, not
 * as a truth value, by the first consumer downstream of it.
 *
 * WHAT IS UNKNOWN
 *   - what either bit means. No semantic name is assigned to either bit, to the
 *     array, or to the object;
 *   - whether callers rely on the fact that the counter is untouched;
 *   - what reads the array afterwards.
 *
 * The original file may NOT be copied from 2genkidev/buusfury: that repository
 * carries no licence grant. See docs/REFERENCE_AUDIT.md.
 */

typedef unsigned int u32;

/* ------------------------------------------------------------------------- */
/* Symbols this unit references but does not reconstruct                      */
/* ------------------------------------------------------------------------- */
/* The reader, reconstructed separately at src/ByteCodeInterpreter_flagread.c. */
extern u32 sub_08004364(void *base, u32 value);

/* ------------------------------------------------------------------------- */
/* Absolute machine state. Redirected by the host self-check.                 */
/* ------------------------------------------------------------------------- */
#ifndef BOOLUSE_HOST_TEST

#define BOOLUSE_GLOBAL_BASE (*(u32 *)0x08054FBCu)

#else  /* BOOLUSE_HOST_TEST */

extern u32 booluse_host_global_base;
#define BOOLUSE_GLOBAL_BASE (booluse_host_global_base)

#endif /* BOOLUSE_HOST_TEST */

/* ------------------------------------------------------------------------- */
/* 0x080007B6 - 22 bytes - 10 instructions                                    */
/* ------------------------------------------------------------------------- */
/*
 * The interpreter passes r0 = context and r1 = the address of the cursor slot.
 * Neither routine reads r1, so the parameter is present for the calling
 * convention and is provably unused.
 */
u32 sub_080007B6(void *ctx, u32 *cursor_slot)
{
    u32 *state = (u32 *)ctx;
    u32 count = state[0];

    /* 32-bit address arithmetic on purpose: this is `lsls r1, r1, #2` followed
     * by `adds r4, r1, r0`. With a zero counter the address is the context
     * itself, which is what makes the empty-stack case below observable. */
    u32 *top = (u32 *)((u32)ctx + count * 4u);
    u32 flag;

    (void)cursor_slot;   /* never read */

    flag = sub_08004364((void *)(BOOLUSE_GLOBAL_BASE + 0x14u), *top);
    *top = flag;
    return flag;
}

/* ------------------------------------------------------------------------- */
/* 0x080007CC - 26 bytes - 11 instructions                                    */
/* ------------------------------------------------------------------------- */
/*
 * The same, storing the inverse. The counter is untouched here too.
 */
u32 sub_080007CC(void *ctx, u32 *cursor_slot)
{
    u32 *state = (u32 *)ctx;
    u32 count = state[0];
    u32 *top = (u32 *)((u32)ctx + count * 4u);
    u32 inverted;

    (void)cursor_slot;   /* never read */

    inverted = 1u - sub_08004364((void *)(BOOLUSE_GLOBAL_BASE + 0x14u), *top);
    *top = inverted;
    return inverted;
}

/* ------------------------------------------------------------------------- */
/* The unit's literal word, as declared data                                  */
/* ------------------------------------------------------------------------- */
/*
 * One word at 0x080008D8, the same slot the reader and the effect routine load.
 * It is NOT adjacent to the code.
 */
const u32 bci_booluse_literal_pool[1] = {
    0x08054FBCu
};
