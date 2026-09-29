/*
 * src/probes/use_selftest.c
 *
 * HOST SEMANTIC CHECK for native dispatch entry 29, 0x080007E6: the first
 * consumer of a surviving stack value for a non-stack side effect.
 *
 * It compiles src/ByteCodeInterpreter_use.c for the host and RUNS it. It proves
 * only what the ROM's disassembly already fixes, and it is not compiler
 * evidence: nothing here says anything about ADS 1.2.
 *
 * The recording callee captures BOTH arguments and also reads the counter at
 * call time, which is what makes the ordering observable: if the counter store
 * had come after the read, or the read after the call, the captured values would
 * differ.
 *
 * Built 32-bit: the routine's addressing is 32-bit and its underflow depends on
 * the wrap.
 */

#include <stdio.h>
#include <string.h>

#define USE_HOST_TEST 1
#include "ByteCodeInterpreter_use.c"

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
/* Host substitutes                                                           */
/* ------------------------------------------------------------------------- */
u32 use_host_global_base;

static u32 g_global_object[8];
static int g_calls;
static void *g_arg0;
static u32 g_arg1;
static u32 g_count_at_call;
/* Set by reset_stack to the live context, so the recording callee can read the
 * counter AT CALL TIME and make the ordering observable. */
static u32 *g_ctx_ptr;

void sub_08004380(void *target, u32 value)
{
    g_calls++;
    g_arg0 = target;
    g_arg1 = value;
    g_count_at_call = (g_ctx_ptr != NULL) ? g_ctx_ptr[0] : 0u;
}

/* ------------------------------------------------------------------------- */
#define VALUE_SLOTS 32
#define SLOT_INIT  0xDEADBEEFu

typedef struct HostStack {
    u32 pre[4];                   /* context-16 .. context-4 */
    u32 count;                    /* context + 0x00          */
    u32 values[VALUE_SLOTS];
} HostStack;

static HostStack g_stack;
static u32 g_slot;

static void reset_stack(void)
{
    memset(&g_stack, 0, sizeof(g_stack));
    g_stack.pre[0] = 0x00001000u;
    g_stack.pre[1] = 0x00002000u;
    g_stack.pre[2] = 0x00003000u;
    g_stack.pre[3] = 0x00004000u;
    memset(g_global_object, 0, sizeof(g_global_object));
    g_global_object[0x14 / 4] = 0xCAFEBABEu;
    use_host_global_base = (u32)g_global_object;
    g_slot = SLOT_INIT;
    g_ctx_ptr = &g_stack.count;
    g_calls = 0;
    g_arg0 = NULL;
    g_arg1 = 0u;
    g_count_at_call = 0u;
}

static void run(void)
{
    sub_080007E6(&g_stack.count, &g_slot);
}

/* ------------------------------------------------------------------------- */
int main(void)
{
    /* ---- 1. it is a pop that reads exactly one value -------------------- */
    reset_stack();
    g_stack.count = 3u;
    g_stack.values[0] = 0xAAAA0000u;
    g_stack.values[1] = 0xBBBB0000u;
    g_stack.values[2] = 0xCCCC0000u;
    run();

    check(g_stack.count == 2u, "the counter decreases by exactly one", (unsigned long)g_stack.count);
    check(g_arg1 == 0xCCCC0000u, "the value passed is values[count-1], the OLD TOP",
          (unsigned long)g_arg1);
    check(g_calls == 1, "exactly one call happens", (unsigned long)g_calls);

    /* ---- 2. nothing is written back to the stack ------------------------ */
    /* This is what separates it from the arithmetic family, which always
     * writes its result into the lower operand slot. */
    check(g_stack.values[0] == 0xAAAA0000u, "values[0] is untouched: no result replaces it",
          (unsigned long)g_stack.values[0]);
    check(g_stack.values[1] == 0xBBBB0000u, "values[1] is untouched", (unsigned long)g_stack.values[1]);
    check(g_stack.values[2] == 0xCCCC0000u,
          "the consumed slot still holds its old value: it is abandoned, not cleared",
          (unsigned long)g_stack.values[2]);
    check(g_stack.pre[3] == 0x00004000u, "the word below the context is not written",
          (unsigned long)g_stack.pre[3]);

    /* ---- 3. the two call arguments -------------------------------------- */
    check(g_arg0 == (void *)0xCAFEBABEu,
          "r0 is the +0x14 field of the object at the routine's literal",
          (unsigned long)g_arg0);
    check(g_arg1 == 0xCCCC0000u, "r1 is the popped stack value", (unsigned long)g_arg1);

    /* ---- 4. ordering: counter stored, then value read, then the call ---- */
    /* The callee reads the counter at call time. It must already be the
     * decremented value, and the value it received must be the one that was in
     * the slot before the decrement. */
    check(g_count_at_call == 2u,
          "the counter was already decremented when the callee ran, so the store precedes the call",
          (unsigned long)g_count_at_call);
    check(g_count_at_call + 1u == 3u,
          "and its pre-call value was the pre-decrement count", (unsigned long)g_count_at_call);

    /* ---- 5. successive pops read successive values ---------------------- */
    reset_stack();
    g_stack.count = 3u;
    g_stack.values[0] = 10u;
    g_stack.values[1] = 20u;
    g_stack.values[2] = 30u;
    run();
    check(g_arg1 == 30u && g_stack.count == 2u, "the first pop reads the top, 30",
          (unsigned long)g_arg1);
    run();
    check(g_arg1 == 20u && g_stack.count == 1u, "the second pop reads the new top, 20",
          (unsigned long)g_arg1);
    run();
    check(g_arg1 == 10u && g_stack.count == 0u, "the third pop reads 10 and empties the stack",
          (unsigned long)g_arg1);
    check(g_calls == 3, "three pops called out three times", (unsigned long)g_calls);
    check(g_stack.values[0] == 10u && g_stack.values[2] == 30u,
          "and every consumed slot still holds its original value", (unsigned long)g_stack.values[0]);

    /* ---- 6. the cursor slot is never read ------------------------------- */
    reset_stack();
    g_stack.count = 1u;
    g_stack.values[0] = 7u;
    run();
    check(g_slot == SLOT_INIT, "the incoming r1 is untouched: the first instruction overwrites it",
          (unsigned long)g_slot);

    /* ---- 7. UNDERFLOW: no check, and no memory is touched below --------- */
    /* count 0 -> 0xFFFFFFFF, base = context-4, and [slot+4] is context itself,
     * so the value read is the brand-new counter. Nothing is written below the
     * context because this routine has no store to the slot. */
    reset_stack();
    g_stack.count = 0u;
    g_stack.values[0] = 0x11111111u;
    run();

    check(g_stack.count == 0xFFFFFFFFu, "an underflow sets the counter to 0xFFFFFFFF",
          (unsigned long)g_stack.count);
    check(g_arg1 == 0xFFFFFFFFu,
          "and the value passed is that new counter, read through [slot+4] == context",
          (unsigned long)g_arg1);
    check(g_calls == 1, "the call still happens on underflow", (unsigned long)g_calls);
    check(g_stack.pre[3] == 0x00004000u,
          "the word below the context is NOT written: this routine has no store to the slot",
          (unsigned long)g_stack.pre[3]);
    check(g_stack.pre[2] == 0x00003000u && g_stack.pre[1] == 0x00002000u && g_stack.pre[0] == 0x00001000u,
          "and no other word below the context is touched", (unsigned long)g_stack.pre[2]);
    check(g_stack.values[0] == 0x11111111u, "no value slot is touched on underflow",
          (unsigned long)g_stack.values[0]);

    /* A second underflow walks the base four bytes further down, so this time
     * it reads pre[3] rather than the counter. Still nothing is written. */
    run();
    check(g_stack.count == 0xFFFFFFFEu, "the second underflow decrements the counter again",
          (unsigned long)g_stack.count);
    check(g_arg1 == 0x00004000u,
          "and now the value read is context-8's neighbour, pre[3], because the base walked down",
          (unsigned long)g_arg1);
    check(g_stack.pre[3] == 0x00004000u, "which is still not written", (unsigned long)g_stack.pre[3]);

    /* ---- 8. zero and boundary values pass through unchanged ------------- */
    reset_stack();
    g_stack.count = 2u;
    g_stack.values[0] = 0u;
    g_stack.values[1] = 0xFFFFFFFFu;
    run();
    check(g_arg1 == 0xFFFFFFFFu, "a 0xFFFFFFFF value is passed through unchanged",
          (unsigned long)g_arg1);
    check(g_stack.count == 1u, "and the counter still decrements by one", (unsigned long)g_stack.count);

    reset_stack();
    g_stack.count = 2u;
    g_stack.values[0] = 0u;
    g_stack.values[1] = 0u;
    run();
    check(g_arg1 == 0u, "a zero value is passed through unchanged", (unsigned long)g_arg1);

    /* The routine does not interpret the value at all: it is neither sign
     * extended nor masked, so every bit pattern arrives intact. */
    {
        u32 pattern;
        int bad = 0;
        static const u32 samples[] = {
            0x00000001u, 0x80000000u, 0x7FFFFFFFu, 0x0000FFFFu, 0xFFFF0000u, 0xDEADBEEFu
        };
        for (pattern = 0u; pattern < sizeof(samples) / sizeof(samples[0]); pattern++) {
            reset_stack();
            g_stack.count = 1u;
            g_stack.values[0] = samples[pattern];
            run();
            if (g_arg1 != samples[pattern]) {
                bad++;
            }
        }
        check(bad == 0, "every bit pattern arrives intact, with no sign extension or masking",
              (unsigned long)bad);
    }

    /* ---- 9. the literal is the global base ------------------------------ */
    check(bci_use_literal_pool[0] == 0x08054FBCu,
          "the unit's single literal word is the global base", bci_use_literal_pool[0]);
    check(sizeof(bci_use_literal_pool) / sizeof(bci_use_literal_pool[0]) == 1u,
          "the pool holds exactly one word",
          (unsigned long)(sizeof(bci_use_literal_pool) / sizeof(bci_use_literal_pool[0])));

    printf("%s: %d check(s), %d failure(s)\n",
           failures ? "FAIL" : "PASS", checks, failures);
    return failures ? 1 : 0;
}
