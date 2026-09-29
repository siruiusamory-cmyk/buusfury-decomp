/*
 * src/ByteCodeInterpreter_arith.c
 *
 * DECOMPILED SOURCE for the rest of the ByteCodeInterpreter value-stack
 * arithmetic family: primary dispatch slots 8 and 9.
 *
 * The ROM preserves the original source path for this subsystem as ASCII at
 * 0x08004160:
 *
 *     T:\Source\ByteCodeInterpreter\ByteCodeInterpreter.cpp
 *
 *   0x08003D52  20 bytes  10 instructions  one terminator at 0x08003D64
 *   0x08003D66  20 bytes  10 instructions  one terminator at 0x08003D78
 *
 * The third member, slot 7 at 0x08003D3E, is reconstructed separately at
 * src/ByteCodeInterpreter_stack.c and is NOT touched here, so its committed
 * report stays byte-for-byte reproducible. The three tile
 * 0x08003D3E..0x08003D7A contiguously, twenty bytes each, and differ in exactly
 * one instruction:
 *
 *   slot 7  0x08003D3E  adds r1, r2, r1   result = deeper + top
 *   slot 8  0x08003D52  subs r1, r2, r1   result = deeper - top
 *   slot 9  0x08003D66  muls r2, r1, r2   result = top * deeper
 *
 * SCOPE: slots 8 and 9. No other arithmetic or comparison handler is
 * reconstructed, and no opcode index is given a name beyond the operation the
 * ARM instruction itself performs.
 *
 * STATUS, and these three lines are INDEPENDENT of one another.
 *   SEMANTIC.....PROVEN   the pop, the operand slots, the result placement, the
 *                         counter timing, the wrap and the underflow are checked
 *                         by RUNNING them; see src/probes/arith_selftest.c.
 *   MODERN_BUILD.PASS     they compile and link for ARM7TDMI Thumb with the
 *                         modern toolchain; see docs/LIFT_ARITH.md.
 *   ADS_MATCH....BLOCKED  never compiled by the tool they target. The ADS 1.2
 *                         binaries are present on this machine but the licence
 *                         present covers a different product, so the ARM
 *                         compilers cannot be run (ADS12_LICENSE_UNAVAILABLE).
 *                         No byte-match claim is made.
 *
 * THE SHARED STACK CONTRACT, proven by all three and stated once
 *   context+0x00          a COUNTER
 *   context+4+4*i         the values, index i in 0..count-1
 *
 *   1. the counter is read, decremented by one, and written back;
 *   2. the two operands are the TOP TWO slots: `values[count-1]` read through
 *      `[slot+4]` (the old top) and `values[count-2]` read through `[slot]`;
 *   3. the two are combined by one ALU instruction;
 *   4. the result is written to the LOWER slot, `values[count-2]`, and the upper
 *      slot is left ABANDONED above the new counter, not cleared.
 *
 * So each handler consumes two values, produces one, and moves the counter by
 * exactly -1.
 *
 * OPERAND ORDER, NOW PROVEN DIRECTLY
 * Slot 7 could not show the order because addition is commutative. Slot 8 can:
 * Thumb renders a two-source ALU op as `op Rd, Rn, Rm` and computes `Rn <op> Rm`,
 * so `subs r1, r2, r1` at 0x08003D60 computes `r2 - r1`. The register loaded
 * from the LOWER slot is `r2` and the one loaded from the top is `r1`, therefore
 *
 *     result = values[count-2] - values[count-1]
 *            = DEEPER - TOP
 *
 * The structural contract is therefore, for all three:
 *
 *     deeper stack value = FIRST source operand
 *     top stack value    = SECOND source operand
 *
 * ONE STRUCTURAL DIFFERENCE IN SLOT 9
 * Slots 7 and 8 leave the result in `r1` and store it with `str r1, [r0]`.
 * Slot 9's combining instruction is `muls r2, r1, r2`, which writes `r2`, so
 * slot 9 stores `str r2, [r0]` at 0x08003D76. The result register differs; the
 * slot written and the contract do not.
 *
 * OVERFLOW AND WRAP
 * All three are plain 32-bit operations with no saturation and no overflow
 * branch: `adds` and `subs` wrap modulo 2^32, and `muls` is the low 32 bits of
 * the product. Two 32-bit values multiplied can produce a 64-bit product, and
 * only the low half survives.
 *
 * NO UNDERFLOW CHECK, IN ANY OF THE THREE
 * A zero counter becomes 0xFFFFFFFF, the slot address becomes `context-4`, and
 * the halfword of arithmetic runs against the word immediately BELOW the context
 * object. For this pair:
 *
 *   slot 8: top = *context = 0xFFFFFFFF, deeper = the word below
 *           result = deeper - 0xFFFFFFFF = deeper + 1
 *           -> the word below the context is INCREMENTED by one
 *   slot 9: top = *context = 0xFFFFFFFF, deeper = the word below
 *           result = 0xFFFFFFFF * deeper = -deeper (mod 2^32)
 *           -> the word below the context is REPLACED by its own negation
 *
 * and neither touches a value slot. Successive underflows walk the base four
 * bytes further down each time, exactly as slot 7 does. The behaviour is
 * reproduced exactly and no guard was added, because the original performs none.
 *
 * The 32-bit address arithmetic below is deliberate: modelling it with plain
 * pointer arithmetic on a 64-bit host would not wrap, and the underflow depends
 * on the wrap.
 *
 * WHAT IS UNKNOWN
 *   - what consumes the surviving value. These handlers leave it on the stack
 *     and return;
 *   - the meaning of any opcode index. Slot 8 is proven to subtract and slot 9
 *     to multiply, from their own instructions; the slot NUMBERS are dispatch
 *     details, and no opcode table is reconstructed;
 *   - whether any caller relies on the underflow behaviour.
 *
 * The original file may NOT be copied from 2genkidev/buusfury: that repository
 * carries no licence grant. See docs/REFERENCE_AUDIT.md.
 */

typedef unsigned int u32;

/* ------------------------------------------------------------------------- */
/* The shared preamble, written once because it is byte-identical in both      */
/* ------------------------------------------------------------------------- */
/*
 * Returns the address of the slot for the NEW counter, having already stored
 * that counter. Reproducing the shared seven instructions as a helper keeps the
 * two handlers readable; the original has them inline in each, and the
 * comparison in config/lift_arith.json measures the inlined form.
 */
static u32 *arith_pop_slot(void *ctx)
{
    u32 *state = (u32 *)ctx;
    u32 count = state[0];

    count -= 1u;
    state[0] = count;

    /* 32-bit address arithmetic on purpose. */
    return (u32 *)((u32)ctx + count * 4u);
}

/* ------------------------------------------------------------------------- */
/* primary dispatch slot 8 - 0x08003D52 - 20 bytes - 10 instructions          */
/* ------------------------------------------------------------------------- */
/*
 * `subs r1, r2, r1`: the deeper operand minus the top. This is the handler that
 * proves the operand order for the whole family.
 */
void sub_08003D52(void *ctx, u32 *cursor_slot)
{
    u32 *base;
    u32 top;
    u32 deeper;

    (void)cursor_slot;   /* never read: the first instruction overwrites r1 */

    base = arith_pop_slot(ctx);
    top = base[1];       /* values[count]   -> the old top    */
    deeper = base[0];    /* values[count-1] -> the new top    */
    base[0] = deeper - top;
}

/* ------------------------------------------------------------------------- */
/* primary dispatch slot 9 - 0x08003D66 - 20 bytes - 10 instructions          */
/* ------------------------------------------------------------------------- */
/*
 * `muls r2, r1, r2`: the top times the deeper. Multiplication is commutative,
 * so this handler does not show the order either; slot 8 does. Note the result
 * register is r2, not r1.
 */
void sub_08003D66(void *ctx, u32 *cursor_slot)
{
    u32 *base;
    u32 top;
    u32 deeper;

    (void)cursor_slot;   /* never read: the first instruction overwrites r1 */

    base = arith_pop_slot(ctx);
    top = base[1];       /* values[count]   -> the old top    */
    deeper = base[0];    /* values[count-1] -> the new top    */
    base[0] = top * deeper;
}

/* ------------------------------------------------------------------------- */
/* This unit has no literal pool                                              */
/* ------------------------------------------------------------------------- */
/*
 * Every instruction in both handlers is register-only: there is no
 * `ldr rX,[pc,#N]`, so there is no pool word to declare. That is asserted by the
 * lift harness rather than assumed.
 */
