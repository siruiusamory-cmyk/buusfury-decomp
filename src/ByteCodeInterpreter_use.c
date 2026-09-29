/*
 * src/ByteCodeInterpreter_use.c
 *
 * DECOMPILED SOURCE for the first ByteCodeInterpreter routine that consumes a
 * surviving stack value for a NON-STACK side effect: native dispatch entry 29,
 * code address 0x080007E6.
 *
 * The ROM preserves the original source path for this subsystem as ASCII at
 * 0x08004160:
 *
 *     T:\Source\ByteCodeInterpreter\ByteCodeInterpreter.cpp
 *
 *   0x080007E6  24 bytes  11 instructions  one terminator at 0x080007FC
 *
 * SCOPE: this one consumer. Its callee is declared, not reconstructed.
 *
 * WHY THIS ONE
 * A mechanical scan of both proven dispatch tables found 52 functions that pop a
 * value and do NOT write a result back into the slot. This is the smallest of
 * them: 24 bytes, 11 instructions, one pop, one call, one literal, no branches.
 * It is reachable through the proven chain interpreter -> primary slot 2 ->
 * native table, and its side effect is a call that receives the popped value,
 * which is the only fully observable use available at this size.
 *
 * THE ROUTINE, ALL ELEVEN INSTRUCTIONS
 *   0x080007E6  push {r3, lr}
 *   0x080007E8  ldr  r1, [r0]        r1 = context+0x00, the counter
 *   0x080007EA  subs r1, #1          r1 = count - 1
 *   0x080007EC  str  r1, [r0]        context+0x00 = count - 1
 *   0x080007EE  lsls r1, r1, #2      r1 = (count-1) * 4
 *   0x080007F0  adds r0, r1, r0      r0 = context + (count-1)*4
 *   0x080007F2  ldr  r1, [r0, #4]    r1 = values[count-1]   <- the popped value
 *   0x080007F4  ldr  r0, [pc, #0xe0] r0 = 0x08054FBC, a global base
 *   0x080007F6  ldr  r0, [r0, #0x14] r0 = *(0x08054FBC + 0x14)
 *   0x080007F8  bl   0x08004380      sub_08004380(r0, r1)
 *   0x080007FC  pop  {r3, pc}        the single exit
 *
 * STATUS, and these three lines are INDEPENDENT of one another.
 *   SEMANTIC.....PROVEN   the pop, the absence of a write-back, the two call
 *                         arguments and the ordering are checked by RUNNING it;
 *                         see src/probes/use_selftest.c.
 *   MODERN_BUILD.PASS     it compiles and links for ARM7TDMI Thumb with the
 *                         modern toolchain; see docs/LIFT_USE.md.
 *   ADS_MATCH....BLOCKED  never compiled by the tool it targets. The ADS 1.2
 *                         binaries are present on this machine but the licence
 *                         present covers a different product, so the ARM
 *                         compilers cannot be run (ADS12_LICENSE_UNAVAILABLE).
 *                         No byte-match claim is made.
 *
 * WHAT IS PROVEN
 *   - it is a POP: the counter is decremented by exactly one and written back;
 *   - it reads exactly ONE value, `values[count-1]`, the old top;
 *   - it writes NOTHING back into the stack. There is no store to the slot, so
 *     the surviving values are untouched and the stack simply shrinks. This is
 *     what distinguishes it from the arithmetic family, which always writes the
 *     result back to the lower operand slot;
 *   - the popped value is passed to `sub_08004380` as the SECOND argument (r1),
 *     and the first argument (r0) is `*(u32*)(0x08054FBC + 0x14)` - a field of a
 *     global object reached through the routine's only literal;
 *   - ORDERING: the counter is decremented and stored BEFORE the value is read,
 *     and the value is read BEFORE the call. So the stack mutation happens first,
 *     then the side effect;
 *   - it makes exactly ONE call and never reads r1's incoming value.
 *
 * UNDERFLOW
 * With a counter of zero the routine still does not stop or fault. It decrements
 * to 0xFFFFFFFF, so the slot address becomes `context + 0xFFFFFFFF*4`, which is
 * `context - 4` in 32-bit arithmetic, and `[slot+4]` is therefore `context`
 * itself:
 *
 *     count = 0xFFFFFFFF
 *     base  = context - 4
 *     value = *(context - 4 + 4) = *(context) = 0xFFFFFFFF   <- the new counter
 *
 * Because this routine has NO store to the slot, an underflow is HARMLESS TO MEMORY: (the two words are split by the
 * line break below) the counter it just wrote and passes 0xFFFFFFFF to the
 * callee. Nothing below the context is read or written. That is a real
 * difference from the arithmetic family, whose underflow writes below the
 * context object, and it is recorded as the code's actual behaviour. No guard
 * was added.
 *
 * WHAT IS UNKNOWN
 *   - what `sub_08004380` does with the value. It is declared, not
 *     reconstructed;
 *   - what the global object at 0x08054FBC is. Its +0x14 field is passed; the
 *     object is not named and no meaning is imported from another title;
 *   - which native index this is at runtime beyond the table entry that points
 *     here. No opcode table is reconstructed and no index is named.
 *
 * The original file may NOT be copied from 2genkidev/buusfury: that repository
 * carries no licence grant. See docs/REFERENCE_AUDIT.md.
 */

typedef unsigned int u32;

/* ------------------------------------------------------------------------- */
/* Symbols this unit references but does not reconstruct                      */
/* ------------------------------------------------------------------------- */
/* The callee. It receives the popped value in r1 and a global field in r0. */
extern void sub_08004380(void *target, u32 value);

/* ------------------------------------------------------------------------- */
/* Absolute machine state. Redirected by the host self-check.                 */
/* ------------------------------------------------------------------------- */
#ifndef USE_HOST_TEST

/* The routine's only literal: a global base at the end of its own pool. */
#define USE_GLOBAL_BASE (*(u32 *)0x08054FBCu)

#else  /* USE_HOST_TEST */

extern u32 use_host_global_base;
#define USE_GLOBAL_BASE (use_host_global_base)

#endif /* USE_HOST_TEST */

/* ------------------------------------------------------------------------- */
/* native dispatch entry 29 - 0x080007E6 - 24 bytes - 11 instructions         */
/* ------------------------------------------------------------------------- */
/*
 * The interpreter's handler contract passes r0 = context and r1 = the address of
 * the cursor slot. This routine never reads r1, so the parameter is present for
 * the calling convention and is provably unused.
 */
void sub_080007E6(void *ctx, u32 *cursor_slot)
{
    u32 *state = (u32 *)ctx;
    u32 count;
    u32 *base;
    u32 value;
    u32 target;

    (void)cursor_slot;   /* never read: the first instruction overwrites r1 */

    /* Pop: the counter is decremented and written back BEFORE the value is
     * read, and nothing is written back afterwards. */
    count = state[0];
    count -= 1u;
    state[0] = count;

    /* 32-bit address arithmetic on purpose: on the target this is exactly
     * `lsls r1, r1, #2` followed by `adds r0, r1, r0`, and the underflow
     * depends on that wrap. */
    base = (u32 *)((u32)ctx + count * 4u);
    value = base[1];

    /* The routine's only literal is the base of a global object; its +0x14
     * field becomes the callee's first argument. */
    target = *(u32 *)(USE_GLOBAL_BASE + 0x14u);

    sub_08004380((void *)target, value);
}

/* ------------------------------------------------------------------------- */
/* The unit's literal pool, as declared data                                  */
/* ------------------------------------------------------------------------- */
/*
 * One word at 0x080008D8, loaded at 0x080007F4. It is NOT adjacent to the code:
 * the routine ends at 0x080007FE and the pool sits 0xDA bytes later.
 */
const u32 bci_use_literal_pool[1] = {
    0x08054FBCu
};
