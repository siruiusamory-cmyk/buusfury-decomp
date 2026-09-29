/*
 * src/probes/stack_selftest.c
 *
 * HOST SEMANTIC CHECK for the first value-stack consumer: primary dispatch
 * slot 7, entry 0x08003D3E.
 *
 * It compiles src/ByteCodeInterpreter_stack.c for the host and RUNS it. It
 * proves only what the ROM's disassembly already fixes, and it is not compiler
 * evidence: nothing here says anything about ADS 1.2.
 *
 * The host context is preceded by a PRE array, so the words BELOW the counter
 * are real storage belonging to this test. That is what makes the underflow
 * observable and bounded: an underflowing pop computes `context - 4`, and each
 * successive underflow walks the base four bytes further down, so the test
 * needs that room. Without it the handler would write outside the object, which
 * in an earlier revision of this file corrupted the test's own counters.
 *
 * Built 32-bit, like the other ByteCodeInterpreter checks: the handler's
 * addressing is 32-bit and the underflow depends on the wrap.
 */

#include <stdio.h>
#include <string.h>

#include "ByteCodeInterpreter_stack.c"

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

/* pre[3] is context-4, pre[2] is context-8, pre[1] is context-12, pre[0] is
 * context-16. Distinct values make the underflow walk readable. */
#define PRE0_INIT 0x00001000u
#define PRE1_INIT 0x00002000u
#define PRE2_INIT 0x00003000u
#define PRE3_INIT 0x00004000u

typedef struct HostStack {
    u32 pre[4];                   /* context-16 .. context-4            */
    u32 count;                    /* context + 0x00, the counter        */
    u32 values[VALUE_SLOTS];      /* context + 0x04 + 4*i               */
} HostStack;

/* The context the handler is given is &g_stack.count, so `pre` is below it. */
#define CTX (&g_stack.count)

static HostStack g_stack;
static u32 g_slot;                /* the cursor slot the handler must ignore    */

static void reset_stack(void)
{
    memset(&g_stack, 0, sizeof(g_stack));
    g_stack.pre[0] = PRE0_INIT;
    g_stack.pre[1] = PRE1_INIT;
    g_stack.pre[2] = PRE2_INIT;
    g_stack.pre[3] = PRE3_INIT;
    g_slot = SLOT_INIT;
}

static u32 run(void)
{
    sub_08003D3E(CTX, &g_slot);
    return g_slot;
}

/* ------------------------------------------------------------------------- */
int main(void)
{
    /* ---- 1. it is a pop: two in, one out, net -1 ------------------------- */
    reset_stack();
    g_stack.count = 2u;
    g_stack.values[0] = 5u;
    g_stack.values[1] = 7u;
    g_stack.values[2] = 0xAAAAAAAAu;
    (void)run();

    check(g_stack.count == 1u, "the counter decreases by exactly one", (unsigned long)g_stack.count);
    check(g_stack.values[0] == 12u, "the sum 5+7 lands in the LOWER slot, values[0]",
          (unsigned long)g_stack.values[0]);
    check(g_stack.values[1] == 7u,
          "the upper slot keeps the old top rather than being cleared: it is abandoned, not erased",
          (unsigned long)g_stack.values[1]);
    check(g_stack.values[2] == 0xAAAAAAAAu, "slots above the operands are untouched",
          (unsigned long)g_stack.values[2]);
    check(g_stack.pre[3] == PRE3_INIT, "a normal pop does not touch the word below the context",
          (unsigned long)g_stack.pre[3]);

    /* ---- 2. the result replaces the NEW top, not the old one ------------- */
    /* If the result had been written to values[count-1] instead, values[0]
     * would be unchanged and values[1] would hold the sum. */
    reset_stack();
    g_stack.count = 3u;
    g_stack.values[0] = 1u;
    g_stack.values[1] = 2u;
    g_stack.values[2] = 40u;
    (void)run();
    check(g_stack.count == 2u, "with three values the counter becomes two", (unsigned long)g_stack.count);
    check(g_stack.values[1] == 42u, "the sum 2+40 lands in values[1], the lower of the two operands",
          (unsigned long)g_stack.values[1]);
    check(g_stack.values[2] == 40u, "values[2] keeps the old top", (unsigned long)g_stack.values[2]);
    check(g_stack.values[0] == 1u, "the deeper value below the operands is untouched",
          (unsigned long)g_stack.values[0]);

    /* ---- 3. the cursor slot is never read -------------------------------- */
    reset_stack();
    g_stack.count = 2u;
    g_stack.values[0] = 1u;
    g_stack.values[1] = 1u;
    check(run() == SLOT_INIT,
          "the handler leaves r1 untouched: the first instruction overwrites it before any read",
          (unsigned long)run());

    /* ---- 4. 32-bit addition wraps --------------------------------------- */
    reset_stack();
    g_stack.count = 2u;
    g_stack.values[0] = 0xFFFFFFFFu;
    g_stack.values[1] = 1u;
    (void)run();
    check(g_stack.values[0] == 0u, "0xFFFFFFFF + 1 wraps to 0", (unsigned long)g_stack.values[0]);

    reset_stack();
    g_stack.count = 2u;
    g_stack.values[0] = 0x80000000u;
    g_stack.values[1] = 0x80000000u;
    (void)run();
    check(g_stack.values[0] == 0u, "0x80000000 + 0x80000000 wraps to 0", (unsigned long)g_stack.values[0]);

    reset_stack();
    g_stack.count = 2u;
    g_stack.values[0] = 0x7FFFFFFFu;
    g_stack.values[1] = 1u;
    (void)run();
    check(g_stack.values[0] == 0x80000000u, "0x7FFFFFFF + 1 is 0x80000000, with no signed saturation",
          (unsigned long)g_stack.values[0]);

    /* ---- 5. addition is commutative, so this handler shows no order ------ */
    {
        u32 forward;
        reset_stack();
        g_stack.count = 2u;
        g_stack.values[0] = 123u;
        g_stack.values[1] = 456u;
        (void)run();
        forward = g_stack.values[0];

        reset_stack();
        g_stack.count = 2u;
        g_stack.values[0] = 456u;
        g_stack.values[1] = 123u;
        (void)run();
        check(g_stack.values[0] == forward,
              "addition is commutative, so the operand ORDER cannot come from this handler: "
              "it is established by primary slot 8's subtract",
              (unsigned long)forward);
    }

    /* ---- 6. UNDERFLOW: no check, and the walked base is observable ------- */
    /* counter 0 -> 0xFFFFFFFF, base = context-4:
     *   top = base[1] = *context      = 0xFFFFFFFF, the NEW counter
     *   base[0] = base[0] + top       = pre[3] - 1
     * Each further underflow moves the base another four bytes down. */
    reset_stack();
    g_stack.count = 0u;
    g_stack.values[0] = 0x11111111u;
    g_stack.values[1] = 0x22222222u;
    (void)run();

    check(g_stack.count == 0xFFFFFFFFu,
          "an underflowing pop sets the counter to 0xFFFFFFFF instead of stopping",
          (unsigned long)g_stack.count);
    check(g_stack.pre[3] == PRE3_INIT - 1u,
          "the word immediately below the context is decremented by one", (unsigned long)g_stack.pre[3]);
    check(g_stack.pre[2] == PRE2_INIT && g_stack.pre[1] == PRE1_INIT && g_stack.pre[0] == PRE0_INIT,
          "only the first word below the context is touched", (unsigned long)g_stack.pre[2]);
    check(g_stack.values[0] == 0x11111111u && g_stack.values[1] == 0x22222222u,
          "an underflow touches no value slot at all", (unsigned long)g_stack.values[0]);

    /* That result is also the proof of the ORDERING: `top` could only be
     * 0xFFFFFFFF, the brand-new counter, if the store to the counter landed
     * before the operand reads. Had the reads come first, top would be 0. */
    check((PRE3_INIT - 1u) == (PRE3_INIT + 0xFFFFFFFFu),
          "the guard result equals guard + the NEW counter, which proves the store precedes the reads",
          (unsigned long)(PRE3_INIT - 1u));

    /* A second underflow walks the base four bytes further down. */
    (void)run();
    check(g_stack.count == 0xFFFFFFFEu, "the counter decrements again, to 0xFFFFFFFE",
          (unsigned long)g_stack.count);
    check(g_stack.pre[2] == PRE2_INIT + (PRE3_INIT - 1u),
          "the second underflow reads and writes context-8", (unsigned long)g_stack.pre[2]);
    check(g_stack.pre[3] == PRE3_INIT - 1u, "and leaves context-4 as the first underflow left it",
          (unsigned long)g_stack.pre[3]);

    /* And a third, to show the walk continues rather than settling. */
    (void)run();
    check(g_stack.count == 0xFFFFFFFDu, "the counter reaches 0xFFFFFFFD", (unsigned long)g_stack.count);
    check(g_stack.pre[1] == PRE1_INIT + (PRE2_INIT + PRE3_INIT - 1u),
          "the third underflow reads and writes context-12", (unsigned long)g_stack.pre[1]);
    check(g_stack.pre[0] == PRE0_INIT, "context-16 is still untouched after three underflows",
          (unsigned long)g_stack.pre[0]);

    /* ---- 7. an exhaustive sweep of small operands ------------------------ */
    {
        u32 a;
        u32 b;
        int mismatches = 0;
        int cases = 0;
        for (a = 0u; a < 256u; a++) {
            for (b = 0u; b < 256u; b++) {
                reset_stack();
                g_stack.count = 2u;
                g_stack.values[0] = a;
                g_stack.values[1] = b;
                (void)run();
                cases++;
                if (g_stack.values[0] != (u32)(a + b) || g_stack.count != 1u) {
                    mismatches++;
                }
            }
        }
        check(cases == 65536, "the sweep covered every operand pair in 0..255", (unsigned long)cases);
        check(mismatches == 0, "every operand pair produced the wrapped 32-bit sum",
              (unsigned long)mismatches);
    }

    /* ---- 8. a chain of pops reduces the TOP two slots each time --------- */
    /* The operands are always the top two slots, values[count-1] and
     * values[count-2], never values[0] unless the counter is 2. With three
     * values the first reduction therefore combines values[2] and values[1]. */
    reset_stack();
    g_stack.count = 3u;
    g_stack.values[0] = 10u;
    g_stack.values[1] = 20u;
    g_stack.values[2] = 30u;
    (void)run();                                  /* 20+30 -> values[1], count 2 */
    check(g_stack.count == 2u, "the first reduction leaves two values", (unsigned long)g_stack.count);
    check(g_stack.values[1] == 50u, "it combines the TOP two slots, values[2] and values[1]",
          (unsigned long)g_stack.values[1]);
    check(g_stack.values[0] == 10u, "values[0] is below the operands and untouched",
          (unsigned long)g_stack.values[0]);
    check(g_stack.values[2] == 30u, "the old top is abandoned above the new counter",
          (unsigned long)g_stack.values[2]);

    (void)run();                                  /* 10+50 -> values[0], count 1 */
    check(g_stack.count == 1u, "the second reduction leaves one value", (unsigned long)g_stack.count);
    check(g_stack.values[0] == 60u, "the running sum is now in values[0]",
          (unsigned long)g_stack.values[0]);
    check(g_stack.values[1] == 50u, "the previously surviving slot is abandoned, not cleared",
          (unsigned long)g_stack.values[1]);

    printf("%s: %d check(s), %d failure(s)\n",
           failures ? "FAIL" : "PASS", checks, failures);
    return failures ? 1 : 0;
}
