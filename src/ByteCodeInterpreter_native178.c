/*
 * src/ByteCodeInterpreter_native178.c
 *
 * DECOMPILED SOURCE for native dispatch slot 178, code address 0x08003030.
 *
 *   0x08003030  64 bytes  30 instructions  one terminator at 0x0800306E
 *
 * IDENTITY, CROSS-VALIDATED STATIC AND RUNTIME
 * The native table at 0x08055098 holds 0x08003031 at slot 178, at table address
 * 0x08055360. Its Thumb bit masks off to 0x08003030, which is exactly the address
 * an independent earlier runtime capture recorded for slot 178. The two agree.
 * Exactly ONE table entry points at this address.
 *
 * The runtime capture is used ONLY as identity evidence. It says nothing about
 * what the routine does, and no semantic claim here rests on it.
 *
 * THE ROUTINE, ALL THIRTY INSTRUCTIONS
 *   0x08003030  push {lr}
 *   0x08003032  ldr  r1, [r0]         r1 = context+0x00, the counter
 *   0x08003034  sub  sp, #0xc
 *   0x08003036  subs r1, #1
 *   0x08003038  str  r1, [r0]         counter--
 *   0x0800303A  lsls r1, r1, #2
 *   0x0800303C  adds r1, r1, r0
 *   0x0800303E  ldr  r1, [r1, #4]     values[count-1]
 *   0x08003040  str  r1, [sp, #8]     -> local[1]
 *   0x08003042  ldr  r1, [r0]         POP 2
 *   0x08003044  subs r1, #1
 *   0x08003046  str  r1, [r0]         counter--
 *   0x08003048  lsls r1, r1, #2
 *   0x0800304A  adds r1, r1, r0
 *   0x0800304C  ldr  r1, [r1, #4]     values[count-2]
 *   0x0800304E  str  r1, [sp, #4]     -> local[0]
 *   0x08003050  ldr  r1, [r0]         POP 3
 *   0x08003052  subs r1, #1
 *   0x08003054  str  r1, [r0]         counter--
 *   0x08003056  lsls r1, r1, #2
 *   0x08003058  adds r0, r1, r0
 *   0x0800305A  ldr  r0, [r0, #4]     values[count-3]      <- the FIRST argument
 *   0x0800305C  add  r1, sp, #4       r1 = &local[0], a two-element array
 *   0x0800305E  bl   0x0802BFBC       sub_0802BFBC(values[count-3], local)
 *   0x08003062  adds r1, r0, #0       r1 = that call's result
 *   0x08003064  ldr  r0, [pc, #0x14c] r0 = 0x08054FBC
 *   0x08003066  ldr  r0, [r0, #0x18]  r0 = *(0x08054FBC + 0x18)
 *   0x08003068  bl   0x0801191A       sub_0801191A(that word, the result)
 *   0x0800306C  add  sp, #0xc
 *   0x0800306E  pop  {pc}             the single exit
 *
 * THE NATIVE ENTRY CONTRACT, AS THIS ROUTINE ACTUALLY USES IT
 *   r0 is the interpreter CONTEXT. The routine uses it as the base of the value
 *   stack and reads the counter at +0x00 and the values at +4+4*i, exactly as
 *   the other lifted handlers do.
 *
 *   r1 IS NEVER READ. The first instruction overwrites it. Whatever the dispatcher
 *   happens to leave in r1 - and the dispatcher evidence says it is the routine's
 *   own address, incidentally - this routine ignores it entirely. No argument
 *   meaning is assigned to r1.
 *
 * STACK BEHAVIOUR
 *   * it POPS THREE values and PUSHES NOTHING, so the counter moves by exactly -3;
 *   * the three are read top-first: values[count-1], then values[count-2], then
 *     values[count-3];
 *   * it builds a TWO-ELEMENT ARRAY ON ITS OWN FRAME, not on the VM stack:
 *     local[0] = values[count-2] and local[1] = values[count-1], so the pair goes
 *     to the first callee in REVERSE stack order, deepest-of-the-two first;
 *   * no result is pushed back, so the VM stack simply shrinks.
 *
 * THERE IS NO STACK-EMPTINESS CHECK, and that is reproduced rather than guarded.
 * With a counter below three the decrements wrap and the reads walk BELOW the
 * context object, exactly as the arithmetic family does. No guard was added.
 *
 * THE FIRST CONCRETE NON-STACK EFFECT
 * The routine makes TWO calls and returns nothing to the VM:
 *
 *     result = sub_0802BFBC(values[count-3], { values[count-2], values[count-1] })
 *     sub_0801191A(*(0x08054FBC + 0x18), result)
 *
 * The second call is the observable engine effect: it hands the first call's
 * result to an engine routine together with the object named by the table word at
 * 0x08054FBC + 0x18, which is the IWRAM address 0x03001C4C. So this handler reads
 * three VM values and drives an engine object with the computed result. Following
 * either callee further is outside this ticket: both are DECLARED, not
 * reconstructed, and both are bound at their original addresses.
 *
 * STATUS, and these three lines are INDEPENDENT of one another.
 *   SEMANTIC.....PROVEN   the three pops, the local array contents and ORDER, both
 *                         call argument lists and the absent push are checked by
 *                         RUNNING them; see src/probes/native178_selftest.c.
 *   MODERN_BUILD.PASS     it compiles and links for ARM7TDMI Thumb with the
 *                         modern toolchain; see docs/LIFT_NATIVE178.md.
 *   ADS_MATCH....BLOCKED  never compiled by the tool it targets. The ADS 1.2
 *                         binaries are present on this machine but the licence
 *                         present covers a different product (ADS12_LICENSE_UNAVAILABLE).
 *                         No byte-match claim is made.
 *
 * WHAT IS UNKNOWN
 *   - what sub_0802BFBC computes from the three values;
 *   - what sub_0801191A does with the object and the result;
 *   - what the object at 0x03001C4C is. No semantic name is assigned to it, to the
 *     handler, or to any operand, and nothing is imported from another title.
 *
 * The original file may NOT be copied from 2genkidev/buusfury: that repository
 * carries no licence grant. See docs/REFERENCE_AUDIT.md.
 */

typedef unsigned int u32;

/* ------------------------------------------------------------------------- */
/* Symbols this unit references but does not reconstruct                      */
/* ------------------------------------------------------------------------- */
/* Both callees are declared and bound at their original addresses. */
extern u32 sub_0802BFBC(u32 value, const u32 *pair);
extern void sub_0801191A(void *target, u32 value);

/* ------------------------------------------------------------------------- */
/* Absolute machine state. Redirected by the host self-check.                 */
/* ------------------------------------------------------------------------- */
#ifndef NATIVE178_HOST_TEST

#define NATIVE178_OWNER (*(u32 *)0x08054FBCu)

#else  /* NATIVE178_HOST_TEST */

extern u32 native178_host_owner;
#define NATIVE178_OWNER (native178_host_owner)

#endif /* NATIVE178_HOST_TEST */

/* ------------------------------------------------------------------------- */
/* native dispatch slot 178 - 0x08003030 - 64 bytes - 30 instructions         */
/* ------------------------------------------------------------------------- */
void sub_08003030(void *ctx, u32 *cursor_slot)
{
    u32 *state = (u32 *)ctx;
    u32 count = state[0];
    u32 local[2];
    u32 deepest;
    u32 result;

    (void)cursor_slot;   /* never read: the first instruction overwrites r1 */

    /* Three pops, top first. 32-bit address arithmetic on purpose: a counter
     * below three wraps, exactly as the machine does. */
    count -= 1u;
    state[0] = count;
    local[1] = state[count + 1u];      /* values[count-1], the old top */

    count -= 1u;
    state[0] = count;
    local[0] = state[count + 1u];      /* values[count-2] */

    count -= 1u;
    state[0] = count;
    deepest = state[count + 1u];       /* values[count-3] */

    /* The first callee gets the deepest value and, as its second argument, the
     * two-element array in the order the machine built it. */
    result = sub_0802BFBC(deepest, local);

    /* The engine effect: the result is handed to the routine that owns the object
     * named by the table word at 0x08054FBC + 0x18. */
    sub_0801191A((void *)(NATIVE178_OWNER), result);
}

/* ------------------------------------------------------------------------- */
/* The unit's literal word, as declared data                                  */
/* ------------------------------------------------------------------------- */
const u32 bci_native178_literal_pool[1] = {
    0x08054FBCu
};
