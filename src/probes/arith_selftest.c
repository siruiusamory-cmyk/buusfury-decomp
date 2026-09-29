/*
 * src/probes/arith_selftest.c
 *
 * HOST SEMANTIC CHECK for the value-stack arithmetic family's remaining two
 * members: primary dispatch slots 8 (0x08003D52, subtract) and 9 (0x08003D66,
 * multiply).
 *
 * It compiles src/ByteCodeInterpreter_arith.c for the host and RUNS both. It
 * proves only what the ROM's disassembly already fixes, and it is not compiler
 * evidence: nothing here says anything about ADS 1.2.
 *
 * The host context carries a PRE array, so the words BELOW the counter are real
 * storage belonging to this test. An underflowing pop computes `context-4` and
 * each successive underflow walks four bytes further down, so the test needs
 * that room; without it the handler writes outside the object.
 *
 * Built 32-bit: the handlers' addressing is 32-bit and the underflow depends on
 * the wrap.
 */

#include <stdio.h>
#include <string.h>

#include "ByteCodeInterpreter_arith.c"

/* ------------------------------------------------------------------------- */
/* Test bookkeeping                                                           */
/* ------------------------------------------------------------------------- */
static int checks;
static int failures;

static void check(int condition, const char *what, unsigned long detail)
{
    checks++;
    if (!condition) {
        failures++;
        printf("FAIL: %s (detail %lu)\n", what, detail);
    }
}

/* ------------------------------------------------------------------------- */
/* The host context, with real storage below the counter                       */
/* ------------------------------------------------------------------------- */
#define VALUE_SLOTS 64
#define SLOT_INIT  0xDEADBEEFu
#define PRE0_INIT  0x00001000u
#define PRE1_INIT  0x00002000u
#define PRE2_INIT  0x00003000u
#define PRE3_INIT  0x00004000u

typedef struct HostStack {
    u32 pre[4];                   /* context-16 .. context-4 */
    u32 count;                    /* context + 0x00          */
    u32 values[VALUE_SLOTS];      /* context + 0x04 + 4*i    */
} HostStack;

static HostStack g_stack;
static u32 g_slot;

typedef void (*Handler)(void *, u32 *);

static void reset_stack(void)
{
    memset(&g_stack, 0, sizeof(g_stack));
    g_stack.pre[0] = PRE0_INIT;
    g_stack.pre[1] = PRE1_INIT;
    g_stack.pre[2] = PRE2_INIT;
    g_stack.pre[3] = PRE3_INIT;
    g_slot = SLOT_INIT;
}

/* Set a stack of `count` values and run one handler over it. */
static u32 run_on(Handler handler, u32 count, u32 v0, u32 v1, u32 v2)
{
    reset_stack();
    g_stack.count = count;
    g_stack.values[0] = v0;
    g_stack.values[1] = v1;
    g_stack.values[2] = v2;
    handler(&g_stack.count, &g_slot);
    return g_slot;
}

/* ------------------------------------------------------------------------- */
int main(void)
{
    static const Handler SUB = sub_08003D52;
    static const Handler MUL = sub_08003D66;

    /* ---- 1. the shared contract: pop two, produce one, net -1 ----------- */
    run_on(SUB, 2u, 10u, 3u, 0u);
    check(g_stack.count == 1u, "slot 8: the counter decreases by exactly one", (unsigned long)g_stack.count);
    check(g_stack.values[0] == 7u, "slot 8: the result lands in the LOWER slot", (unsigned long)g_stack.values[0]);
    check(g_stack.values[1] == 3u, "slot 8: the upper slot is abandoned, not cleared", (unsigned long)g_stack.values[1]);

    run_on(MUL, 2u, 6u, 7u, 0u);
    check(g_stack.count == 1u, "slot 9: the counter decreases by exactly one", (unsigned long)g_stack.count);
    check(g_stack.values[0] == 42u, "slot 9: the result lands in the LOWER slot", (unsigned long)g_stack.values[0]);
    check(g_stack.values[1] == 7u, "slot 9: the upper slot is abandoned, not cleared", (unsigned long)g_stack.values[1]);

    /* ---- 2. OPERAND ORDER, proven directly by the subtract -------------- */
    /* `subs r1, r2, r1` computes r2 - r1, and r2 came from the lower slot. If
     * the order were the other way round this would be -7 instead of 7. */
    run_on(SUB, 2u, 10u, 3u, 0u);
    check(g_stack.values[0] == 7u, "slot 8 computes deeper - top, not top - deeper",
          (unsigned long)g_stack.values[0]);

    run_on(SUB, 2u, 3u, 10u, 0u);
    check(g_stack.values[0] == 0xFFFFFFF9u,
          "slot 8 with the operands swapped gives 3-10 = -7, so the order is real",
          (unsigned long)g_stack.values[0]);
    check(0xFFFFFFF9u == (u32)(3u - 10u), "and that equals the wrapped 3-10", 0ul);

    /* Slot 9 is commutative, so it cannot show the order either. */
    {
        u32 forward;
        run_on(MUL, 2u, 123u, 456u, 0u);
        forward = g_stack.values[0];
        run_on(MUL, 2u, 456u, 123u, 0u);
        check(g_stack.values[0] == forward,
              "slot 9 is commutative: the order is established by slot 8, not here",
              (unsigned long)forward);
        check(forward == 56088u, "and 123*456 is 56088", (unsigned long)forward);
    }

    /* ---- 3. zero operands ------------------------------------------------ */
    run_on(SUB, 2u, 0u, 0u, 0u);
    check(g_stack.values[0] == 0u, "slot 8: 0 - 0 is 0", (unsigned long)g_stack.values[0]);
    run_on(SUB, 2u, 5u, 0u, 0u);
    check(g_stack.values[0] == 5u, "slot 8: x - 0 is x", (unsigned long)g_stack.values[0]);
    run_on(SUB, 2u, 0u, 5u, 0u);
    check(g_stack.values[0] == 0xFFFFFFFBu, "slot 8: 0 - 5 wraps to -5", (unsigned long)g_stack.values[0]);

    run_on(MUL, 2u, 0u, 5u, 0u);
    check(g_stack.values[0] == 0u, "slot 9: 0 * 5 is 0", (unsigned long)g_stack.values[0]);
    run_on(MUL, 2u, 5u, 0u, 0u);
    check(g_stack.values[0] == 0u, "slot 9: 5 * 0 is 0", (unsigned long)g_stack.values[0]);

    /* ---- 4. signed-looking bit patterns -------------------------------- */
    run_on(SUB, 2u, 0x80000000u, 1u, 0u);
    check(g_stack.values[0] == 0x7FFFFFFFu,
          "slot 8: 0x80000000 - 1 is 0x7FFFFFFF, with no signed saturation",
          (unsigned long)g_stack.values[0]);
    run_on(SUB, 2u, 0xFFFFFFFFu, 0xFFFFFFFFu, 0u);
    check(g_stack.values[0] == 0u, "slot 8: 0xFFFFFFFF - 0xFFFFFFFF is 0",
          (unsigned long)g_stack.values[0]);
    run_on(MUL, 2u, 0xFFFFFFFFu, 2u, 0u);
    check(g_stack.values[0] == 0xFFFFFFFEu, "slot 9: -1 * 2 is -2", (unsigned long)g_stack.values[0]);

    /* ---- 5. overflow and wrap -------------------------------------------- */
    run_on(SUB, 2u, 0u, 1u, 0u);
    check(g_stack.values[0] == 0xFFFFFFFFu, "slot 8: 0 - 1 wraps to 0xFFFFFFFF",
          (unsigned long)g_stack.values[0]);

    /* 0x10000 * 0x10000 is 0x100000000, and only the low 32 bits survive. */
    run_on(MUL, 2u, 0x00010000u, 0x00010000u, 0u);
    check(g_stack.values[0] == 0u,
          "slot 9: 0x10000 * 0x10000 wraps to 0, so only the low half of the product survives",
          (unsigned long)g_stack.values[0]);

    run_on(MUL, 2u, 0x80000000u, 2u, 0u);
    check(g_stack.values[0] == 0u, "slot 9: 0x80000000 * 2 wraps to 0", (unsigned long)g_stack.values[0]);

    run_on(MUL, 2u, 0x0000FFFFu, 0x0000FFFFu, 0u);
    check(g_stack.values[0] == 0xFFFE0001u, "slot 9: 0xFFFF squared is 0xFFFE0001 in 32 bits",
          (unsigned long)g_stack.values[0]);

    /* ---- 6. count > 2: the operands are always the TOP TWO slots --------- */
    run_on(SUB, 3u, 100u, 20u, 30u);
    check(g_stack.count == 2u, "slot 8 with three values leaves two", (unsigned long)g_stack.count);
    check(g_stack.values[1] == 0xFFFFFFF6u,
          "slot 8 combines values[1] and values[2], the top two, giving 20-30",
          (unsigned long)g_stack.values[1]);
    check(g_stack.values[0] == 100u, "values[0] is below the operands and untouched",
          (unsigned long)g_stack.values[0]);
    check(g_stack.values[2] == 30u, "the old top is abandoned above the new counter",
          (unsigned long)g_stack.values[2]);

    run_on(MUL, 3u, 100u, 20u, 30u);
    check(g_stack.values[1] == 600u, "slot 9 combines the top two, giving 20*30",
          (unsigned long)g_stack.values[1]);
    check(g_stack.values[0] == 100u, "slot 9 leaves values[0] untouched",
          (unsigned long)g_stack.values[0]);

    /* ---- 7. neither handler reads the cursor slot ----------------------- */
    check(run_on(SUB, 2u, 1u, 1u, 0u) == SLOT_INIT, "slot 8 leaves r1 untouched",
          (unsigned long)run_on(SUB, 2u, 1u, 1u, 0u));
    check(run_on(MUL, 2u, 1u, 1u, 0u) == SLOT_INIT, "slot 9 leaves r1 untouched",
          (unsigned long)run_on(MUL, 2u, 1u, 1u, 0u));

    /* ---- 8. UNDERFLOW: no check, and the walked word is observable ------- */
    /* slot 8 reads top = *context = 0xFFFFFFFF (the new counter) and
     * deeper = pre[3], then computes deeper - 0xFFFFFFFF = deeper + 1. */
    reset_stack();
    g_stack.count = 0u;
    g_stack.values[0] = 0x11111111u;
    sub_08003D52(&g_stack.count, &g_slot);
    check(g_stack.count == 0xFFFFFFFFu, "slot 8 underflow sets the counter to 0xFFFFFFFF",
          (unsigned long)g_stack.count);
    check(g_stack.pre[3] == PRE3_INIT + 1u,
          "slot 8 underflow INCREMENTS the word below the context, because 0xFFFFFFFF acts as -1",
          (unsigned long)g_stack.pre[3]);
    check(g_stack.values[0] == 0x11111111u, "slot 8 underflow touches no value slot",
          (unsigned long)g_stack.values[0]);

    reset_stack();
    g_stack.count = 0u;
    sub_08003D66(&g_stack.count, &g_slot);
    check(g_stack.count == 0xFFFFFFFFu, "slot 9 underflow sets the counter to 0xFFFFFFFF",
          (unsigned long)g_stack.count);
    check(g_stack.pre[3] == (u32)(0u - PRE3_INIT),
          "slot 9 underflow replaces the word below the context with its own negation",
          (unsigned long)g_stack.pre[3]);

    /* The counter store happening BEFORE the reads is what makes top exactly
     * 0xFFFFFFFF. Had the reads come first, top would have been 0 and the
     * results above would differ. */
    check((PRE3_INIT + 1u) == (PRE3_INIT - 0xFFFFFFFFu),
          "the increment result equals deeper - the NEW counter, proving the store precedes the reads",
          (unsigned long)(PRE3_INIT + 1u));

    /* A second underflow walks the base four bytes further down. Started from a
     * fresh stack so the guard values are the known initials: with the counter
     * at 0xFFFFFFFF the base is context-8, top is context-4 (pre[3]) and deeper
     * is pre[2], so pre[2] becomes pre[2] - pre[3]. */
    reset_stack();
    g_stack.count = 0xFFFFFFFFu;
    sub_08003D52(&g_stack.count, &g_slot);
    check(g_stack.count == 0xFFFFFFFEu, "slot 8's second underflow decrements the counter again",
          (unsigned long)g_stack.count);
    check(g_stack.pre[2] == (u32)(PRE2_INIT - PRE3_INIT),
          "and it acts on context-8 with context-4 as the top, so the walk continues",
          (unsigned long)g_stack.pre[2]);
    check(g_stack.pre[3] == PRE3_INIT, "context-4 is read but not written on this step",
          (unsigned long)g_stack.pre[3]);

    /* ---- 9. exhaustive sweeps ------------------------------------------- */
    {
        u32 a;
        u32 b;
        int sub_bad = 0;
        int mul_bad = 0;
        int cases = 0;
        for (a = 0u; a < 256u; a++) {
            for (b = 0u; b < 256u; b++) {
                cases++;
                run_on(SUB, 2u, a, b, 0u);
                if (g_stack.values[0] != (u32)(a - b) || g_stack.count != 1u) {
                    sub_bad++;
                }
                run_on(MUL, 2u, a, b, 0u);
                if (g_stack.values[0] != (u32)(a * b) || g_stack.count != 1u) {
                    mul_bad++;
                }
            }
        }
        check(cases == 65536, "the sweep covered every operand pair in 0..255", (unsigned long)cases);
        check(sub_bad == 0, "slot 8 produced the wrapped difference for every pair", (unsigned long)sub_bad);
        check(mul_bad == 0, "slot 9 produced the low 32 bits of the product for every pair",
              (unsigned long)mul_bad);
    }

    /* ---- 10. the order is antisymmetric, which only a non-commutative op can
     * show. Checked across a sweep rather than on one example. */
    {
        u32 a;
        u32 b;
        int bad = 0;
        int cases = 0;
        for (a = 0u; a < 64u; a++) {
            for (b = 0u; b < 64u; b++) {
                u32 forward;
                u32 backward;
                run_on(SUB, 2u, a, b, 0u);
                forward = g_stack.values[0];
                run_on(SUB, 2u, b, a, 0u);
                backward = g_stack.values[0];
                cases++;
                if (forward != (u32)(0u - backward)) {
                    bad++;
                }
            }
        }
        check(cases == 4096, "the antisymmetry sweep covered 4096 operand pairs", (unsigned long)cases);
        check(bad == 0,
              "slot 8 is antisymmetric: sub(a,b) is always -sub(b,a), which a commutative op could not satisfy",
              (unsigned long)bad);
    }

    printf("%s: %d check(s), %d failure(s)\n",
           failures ? "FAIL" : "PASS", checks, failures);
    return failures ? 1 : 0;
}
