/*
 * src/ByteCodeInterpreter_stack.c
 *
 * DECOMPILED SOURCE for the first concrete CONSUMER of the ByteCodeInterpreter
 * value stack: primary dispatch slot 7, entry 0x08003D3E.
 *
 * The ROM preserves the original source path for this subsystem as ASCII at
 * 0x08004160:
 *
 *     T:\Source\ByteCodeInterpreter\ByteCodeInterpreter.cpp
 *
 *   0x08003D3E  20 bytes  10 instructions  one terminator at 0x08003D50
 *
 * SCOPE: this one consumer. Slots 8 and 9 are the same shape with one
 * instruction differing, and they are NOT lifted here; they are read only far
 * enough to establish the operand-order convention that this commutative
 * handler cannot show by itself. No other handler is reconstructed.
 *
 * THE VALUE STACK, as the previous ticket proved and this one consumes
 *   context+0x00          a COUNTER
 *   context+4+4*i         the values, index i in 0..count-1
 *
 * STATUS, and these three lines are INDEPENDENT of one another.
 *   SEMANTIC.....PROVEN   the pop, the operand slots, the result placement, the
 *                         counter timing and the underflow are checked by
 *                         RUNNING them; see src/probes/stack_selftest.c.
 *   MODERN_BUILD.PASS     it compiles and links for ARM7TDMI Thumb with the
 *                         modern toolchain; see docs/LIFT_STACK.md.
 *   ADS_MATCH....BLOCKED  never compiled by the tool it targets. The ADS 1.2
 *                         binaries are present on this machine but the licence
 *                         present covers a different product, so the ARM
 *                         compilers cannot be run (ADS12_LICENSE_UNAVAILABLE).
 *                         No byte-match claim is made.
 *
 * THE HANDLER, ALL TEN INSTRUCTIONS
 *   0x08003D3E  ldr  r1, [r0]        r1 = context+0x00, the counter
 *   0x08003D40  subs r1, #1          r1 = count - 1
 *   0x08003D42  str  r1, [r0]        context+0x00 = count - 1
 *   0x08003D44  lsls r1, r1, #2      r1 = (count-1) * 4
 *   0x08003D46  adds r0, r1, r0      r0 = context + (count-1)*4
 *   0x08003D48  ldr  r1, [r0, #4]    r1 = values[count-1]   <- the OLD TOP
 *   0x08003D4A  ldr  r2, [r0]        r2 = values[count-2]   <- the NEW TOP
 *   0x08003D4C  adds r1, r2, r1      r1 = values[count-2] + values[count-1]
 *   0x08003D4E  str  r1, [r0]        values[count-2] = the sum
 *   0x08003D50  bx   lr              the single exit
 *
 * WHAT IS PROVEN
 *   - it is a POP: the counter is decremented by exactly one, so the handler
 *     consumes two values and produces one, a net -1;
 *   - the counter is written back BEFORE the operand reads, so the two operand
 *     addresses are computed from the ALREADY decremented count;
 *   - the operands are the top two slots: `values[count-1]` (read through
 *     `[r0,#4]`, the old top) and `values[count-2]` (read through `[r0]`, which
 *     becomes the new top);
 *   - the RESULT IS WRITTEN TO THE LOWER SLOT, `values[count-2]`, and the upper
 *     slot `values[count-1]` is simply abandoned above the new counter. The
 *     stack therefore shrinks by one and the surviving value is the result;
 *   - the operation is 32-bit ADDITION and wraps, because `adds` is a plain
 *     32-bit add;
 *   - it makes NO calls and loads NO literals, so there is no pool and no
 *     cursor interaction: the handler NEVER READS r1's incoming value, which
 *     the first instruction overwrites before any read;
 *   - THERE IS NO UNDERFLOW CHECK. See below.
 *
 * OPERAND ORDER
 * Addition is commutative, so this handler cannot show the order by itself.
 * The convention is established by primary slot 8 at 0x08003D52, which shares
 * this handler's first eight instructions verbatim and then performs
 * `subs r1, r2, r1` at 0x08003D60: the LEFT operand is `values[count-2]`, the
 * LOWER slot, i.e. the value pushed FIRST (the deeper one), and the RIGHT
 * operand is `values[count-1]`, the top. So the convention across the trio is
 *
 *     values[count-2]  <op>  values[count-1]
 *
 * and for slot 8 that is `deeper - top`. That is ROM evidence read from the
 * sibling, not an assumption imported from another title, and slot 8 is not
 * reconstructed here.
 *
 * NO UNDERFLOW CHECK, AND WHAT ACTUALLY HAPPENS
 * With a counter of zero the handler does not stop or fault. It decrements to
 * 0xFFFFFFFF and computes `context + 0xFFFFFFFF*4`, which is `context - 4` in
 * 32-bit arithmetic. The two operand reads are then at `context-4` and
 * `context`, and the store lands at `context-4`:
 *
 *     top    = *(context - 4 + 4) = *(context)      = 0xFFFFFFFF, the new count
 *     deeper = *(context - 4)                        = the word BELOW the context
 *     result = deeper + 0xFFFFFFFF                   = deeper - 1
 *     *(context - 4) = result
 *
 * so an underflowing pop DECREMENTS THE WORD IMMEDIATELY BELOW THE CONTEXT
 * OBJECT by one, sets the counter to 0xFFFFFFFF, and leaves every value slot
 * untouched. That is recorded as the code's actual behaviour and reproduced
 * exactly. No check was added, because the original performs none, and adding
 * one would change the behaviour being reconstructed.
 *
 * The 32-bit address arithmetic below is deliberate: modelling this with
 * pointer arithmetic on a 64-bit host would not wrap, and the underflow above
 * depends on the wrap.
 *
 * WHAT IS UNKNOWN
 *   - what consumes the value afterwards. This handler leaves it on the stack
 *     and returns; the reader is another handler, not reconstructed here;
 *   - the meaning of any opcode index. Slot 7's operation is proven to be
 *     addition from its own instruction; the slot NUMBER is a dispatch detail,
 *     and no opcode table is reconstructed;
 *   - whether any caller relies on the underflow behaviour.
 *
 * The original file may NOT be copied from 2genkidev/buusfury: that repository
 * carries no licence grant. See docs/REFERENCE_AUDIT.md.
 */

typedef unsigned int u32;

/* ------------------------------------------------------------------------- */
/* primary dispatch slot 7 - 0x08003D3E - 20 bytes - 10 instructions          */
/* ------------------------------------------------------------------------- */
/*
 * Reached only through the primary dispatch table: a search of every evidenced
 * function in the image finds no direct BL site targeting it.
 *
 * The interpreter calls every handler with r0 = context and r1 = the address of
 * the cursor slot. This handler never reads r1, so the parameter is present for
 * the calling convention and is provably unused.
 */
void sub_08003D3E(void *ctx, u32 *cursor_slot)
{
    u32 *state = (u32 *)ctx;
    u32 count;
    u32 *base;
    u32 top;
    u32 deeper;

    (void)cursor_slot;   /* never read: the first instruction overwrites r1 */

    /* The counter is decremented and written back BEFORE either operand is
     * read, so both addresses below are computed from the new count. */
    count = state[0];
    count -= 1u;
    state[0] = count;

    /* 32-bit address arithmetic on purpose. On the target this is exactly
     * `adds r0, r1, r0` after `lsls r1, r1, #2`; on a 64-bit host a plain
     * pointer offset would not wrap, and the underflow depends on the wrap. */
    base = (u32 *)((u32)ctx + count * 4u);

    top = base[1];       /* values[count]   -> the slot above the new counter */
    deeper = base[0];    /* values[count-1] -> the new top                     */
    base[0] = deeper + top;   /* the sum lands in the LOWER slot */
}

/* ------------------------------------------------------------------------- */
/* This unit has no literal pool                                              */
/* ------------------------------------------------------------------------- */
/*
 * Every instruction above is register-only: there is no `ldr rX,[pc,#N]`, so
 * there is no pool word to declare. That is asserted by the lift harness rather
 * than assumed, because a unit that silently lost its pool would otherwise look
 * like this one.
 */
