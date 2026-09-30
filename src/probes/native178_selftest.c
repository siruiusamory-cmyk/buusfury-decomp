/*
 * src/probes/native178_selftest.c
 *
 * HOST SEMANTIC CHECK for native dispatch slot 178, 0x08003030.
 *
 * Both callees are MOCKED so their argument lists and their ORDER are observable
 * rather than inferred. Built 32-bit: the addressing wraps on a counter below
 * three, and that wrap is part of what is being checked.
 */

#include <stdio.h>
#include <string.h>

#define NATIVE178_HOST_TEST 1

typedef unsigned int u32;

/* ---- the mocks ---- */
static u32 g_first_calls;
static u32 g_first_arg0;
static u32 g_first_pair[2];
static u32 g_first_result;

static u32 g_second_calls;
static void *g_second_target;
static u32 g_second_value;

u32 sub_0802BFBC(u32 value, const u32 *pair)
{
    g_first_calls++;
    g_first_arg0 = value;
    g_first_pair[0] = pair[0];
    g_first_pair[1] = pair[1];
    /* A recognisable, value-dependent result so the forwarding is checkable. */
    return value ^ 0x5A5A5A5Au;
}

void sub_0801191A(void *target, u32 value)
{
    g_second_calls++;
    g_second_target = target;
    g_second_value = value;
}

#include "ByteCodeInterpreter_native178.c"

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

#define PRE 16
#define BODY 64
#define POST 16

static u32 g_arena[PRE + BODY + POST];
#define CONTEXT (g_arena + PRE)          /* [0] is the counter, [1..] the values */

u32 native178_host_owner;

static void reset_all(void)
{
    memset(g_arena, 0, sizeof(g_arena));
    g_first_calls = 0u;
    g_second_calls = 0u;
    g_first_arg0 = 0u;
    g_first_pair[0] = g_first_pair[1] = 0u;
    g_second_target = NULL;
    g_second_value = 0u;
    native178_host_owner = 0x03001C4Cu;
}

static void run(void)
{
    sub_08003030(CONTEXT, NULL);
}

int main(void)
{
    /* ---- 1. three pops, nothing pushed -------------------------------- */
    reset_all();
    CONTEXT[0] = 3u;
    CONTEXT[1] = 0x11111111u;     /* values[0], the deepest */
    CONTEXT[2] = 0x22222222u;     /* values[1] */
    CONTEXT[3] = 0x33333333u;     /* values[2], the top */
    run();
    check(CONTEXT[0] == 0u, "the counter moves by exactly -3", (unsigned long)CONTEXT[0]);
    check(g_first_calls == 1u, "the first callee is called once", (unsigned long)g_first_calls);
    check(g_second_calls == 1u, "the second callee is called once", (unsigned long)g_second_calls);

    /* ---- 2. which value goes where ------------------------------------ */
    check(g_first_arg0 == 0x11111111u,
          "the first callee's first argument is values[count-3], the DEEPEST of the three",
          (unsigned long)g_first_arg0);
    check(g_first_pair[0] == 0x22222222u,
          "the local array's element 0 is values[count-2], the middle value",
          (unsigned long)g_first_pair[0]);
    check(g_first_pair[1] == 0x33333333u,
          "and element 1 is values[count-1], the old top", (unsigned long)g_first_pair[1]);

    /* ---- 3. the pair is REVERSED relative to VM order ----------------- */
    check(g_first_pair[0] == 0x22222222u && g_first_pair[1] == 0x33333333u,
          "so the pair is handed over deepest-of-the-two first, not top-first",
          (unsigned long)(g_first_pair[0] << 16 | g_first_pair[1] & 0xFFFF));

    /* ---- 4. the second call forwards the first's result and the owner -- */
    check(g_second_value == (0x11111111u ^ 0x5A5A5A5Au),
          "the second callee receives the FIRST call's return value",
          (unsigned long)g_second_value);
    check(g_second_target == (void *)0x03001C4Cu,
          "and its first argument is *(0x08054FBC + 0x18), i.e. the IWRAM object",
          (unsigned long)g_second_target);

    /* ---- 5. the incoming r1 is never read ------------------------------ */
    reset_all();
    CONTEXT[0] = 3u;
    {
        u32 sentinel = 0xDEADBEEFu;
        sub_08003030(CONTEXT, &sentinel);
        check(sentinel == 0xDEADBEEFu, "the incoming r1 is untouched",
              (unsigned long)sentinel);
    }

    /* ---- 6. the values are left in place; the stack only shrinks ------- */
    reset_all();
    CONTEXT[0] = 3u;
    CONTEXT[1] = 1u;
    CONTEXT[2] = 2u;
    CONTEXT[3] = 3u;
    run();
    check(CONTEXT[1] == 1u && CONTEXT[2] == 2u && CONTEXT[3] == 3u,
          "no value slot is written: the consumed slots are abandoned, not cleared",
          (unsigned long)CONTEXT[1]);

    /* ---- 7. three pops are always three pops, whatever the count ------- */
    reset_all();
    CONTEXT[0] = 7u;
    CONTEXT[5] = 0xAAAA0005u;
    CONTEXT[6] = 0xBBBB0006u;
    CONTEXT[7] = 0xCCCC0007u;
    run();
    check(CONTEXT[0] == 4u, "with a count of 7 the counter lands on 4", (unsigned long)CONTEXT[0]);
    check(g_first_arg0 == 0xAAAA0005u, "and the deepest of the three tops is forwarded",
          (unsigned long)g_first_arg0);
    check(g_first_pair[1] == 0xCCCC0007u, "with the top in the pair's second slot",
          (unsigned long)g_first_pair[1]);

    /* ---- 8. NO STACK GUARD: a count below three wraps ------------------ */
    /* count 1 -> 0 -> 0xFFFFFFFF -> 0xFFFFFFFE, so two of the three reads walk
     * BELOW the context object. Nothing is written there. */
    reset_all();
    CONTEXT[0] = 1u;
    CONTEXT[1] = 0x0BADC0DEu;        /* values[0], read by the FIRST pop */
    /* POP 2 reads state[count+1] with count == 0xFFFFFFFF, so the +1 WRAPS to 0
     * and it re-reads the counter. POP 3 then reads state[-1], i.e. the word
     * immediately BELOW the context, which is g_arena[PRE-1]. */
    g_arena[PRE - 1] = 0xF1F1F1F1u;
    run();
    check(CONTEXT[0] == 0xFFFFFFFEu, "a count of 1 wraps to 0xFFFFFFFE",
          (unsigned long)CONTEXT[0]);
    check(g_first_calls == 1u, "and both callees still run", (unsigned long)g_first_calls);
    check(g_first_pair[0] == 0xFFFFFFFFu,
          "the second read wraps onto the counter itself",
          (unsigned long)g_first_pair[0]);
    check(g_first_arg0 == 0xF1F1F1F1u,
          "and the third read lands on the word immediately below the context",
          (unsigned long)g_first_arg0);
    check(g_arena[PRE - 1] == 0xF1F1F1F1u,
          "and nothing below the context is WRITTEN", (unsigned long)g_arena[PRE - 1]);

    reset_all();
    CONTEXT[0] = 0u;                /* a completely empty stack */
    run();
    check(CONTEXT[0] == 0xFFFFFFFDu, "an empty stack wraps three times",
          (unsigned long)CONTEXT[0]);
    check(g_first_calls == 1u && g_second_calls == 1u,
          "and the engine effect still happens", (unsigned long)g_first_calls);

    /* ---- 9. the literal is the owner table --------------------------------- */
    check(bci_native178_literal_pool[0] == 0x08054FBCu,
          "the unit's single literal is the owner table", bci_native178_literal_pool[0]);

    printf("%s: %d check(s), %d failure(s)\n",
           failures ? "FAIL" : "PASS", checks, failures);
    return failures ? 1 : 0;
}
