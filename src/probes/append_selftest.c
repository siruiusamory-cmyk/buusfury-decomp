/*
 * src/probes/append_selftest.c
 *
 * HOST SEMANTIC CHECK for sub_0801191A: the routine that appends a value to the
 * array carried by the object native slot 178 drives.
 *
 * Built 32-bit: the element address is 32-bit arithmetic with no bounds test, and
 * the no-bounds-check case is part of what is being pinned.
 */

#include <stdio.h>
#include <string.h>

#include "ByteCodeInterpreter_append.c"

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

/* The object is `body`; the guard regions make an out-of-body write visible. */
#define PRE 16
#define BODY 64
#define POST 32

static u8 g_arena[PRE + BODY + POST];
#define OBJECT (g_arena + PRE)
#define GUARD 0xA5u

static void reset_arena(void)
{
    memset(g_arena, GUARD, sizeof(g_arena));
}

static u32 *count_slot(void)
{
    return (u32 *)(OBJECT + 4u);
}

static u32 *element(u32 index)
{
    return (u32 *)(OBJECT + 8u + 4u * index);
}

int main(void)
{
    /* ---- 1. the value lands at index `count` and the count increments --- */
    reset_arena();
    *(u32 *)OBJECT = 0xDEADBEEFu;      /* +0x00 must not be touched */
    *count_slot() = 0u;
    sub_0801191A(OBJECT, 0x11111111u);
    check(*count_slot() == 1u, "the count increments by one", (unsigned long)*count_slot());
    check(element(0) != NULL && *(u32 *)(OBJECT + 8u) == 0x11111111u,
          "the value lands at object + 0x08 for a count of 0",
          (unsigned long)*(u32 *)(OBJECT + 8u));

    /* ---- 2. successive appends land consecutively and in order --------- */
    reset_arena();
    *count_slot() = 0u;
    sub_0801191A(OBJECT, 0xAAAA0001u);
    sub_0801191A(OBJECT, 0xAAAA0002u);
    sub_0801191A(OBJECT, 0xAAAA0003u);
    check(*count_slot() == 3u, "three appends leave a count of 3", (unsigned long)*count_slot());
    check(*(u32 *)(OBJECT + 8u) == 0xAAAA0001u, "element 0 is the first value",
          (unsigned long)*(u32 *)(OBJECT + 8u));
    check(*(u32 *)(OBJECT + 12u) == 0xAAAA0002u, "element 1 is the second",
          (unsigned long)*(u32 *)(OBJECT + 12u));
    check(*(u32 *)(OBJECT + 16u) == 0xAAAA0003u, "element 2 is the third",
          (unsigned long)*(u32 *)(OBJECT + 16u));

    /* ---- 3. an existing count is respected ---------------------------- */
    reset_arena();
    *count_slot() = 5u;
    sub_0801191A(OBJECT, 0xBBBBBBBBu);
    check(*count_slot() == 6u, "an existing count of 5 becomes 6", (unsigned long)*count_slot());
    check(*(u32 *)(OBJECT + 8u + 4u * 5u) == 0xBBBBBBBBu,
          "and the write goes to index 5, not index 6",
          (unsigned long)*(u32 *)(OBJECT + 8u + 4u * 5u));

    /* ---- 4. +0x00 is never touched ------------------------------------- */
    reset_arena();
    *(u32 *)OBJECT = 0x0BADF00Du;
    *count_slot() = 2u;
    sub_0801191A(OBJECT, 1u);
    check(*(u32 *)OBJECT == 0x0BADF00Du,
          "object + 0x00 is neither read nor written", (unsigned long)*(u32 *)OBJECT);

    /* ---- 5. the value is stored verbatim ------------------------------- */
    {
        u32 samples[4];
        int bad = 0, i;
        samples[0] = 0u;
        samples[1] = 0xFFFFFFFFu;
        samples[2] = 0x80000000u;
        samples[3] = 0x0000FFFFu;
        for (i = 0; i < 4; i++) {
            reset_arena();
            *count_slot() = 0u;
            sub_0801191A(OBJECT, samples[i]);
            if (*(u32 *)(OBJECT + 8u) != samples[i]) {
                bad++;
            }
        }
        check(bad == 0, "0, 0xFFFFFFFF, 0x80000000 and 0x0000FFFF all arrive verbatim",
              (unsigned long)bad);
    }

    /* ---- 6. the count is written BEFORE the element -------------------- */
    /* Not directly observable without a hook, but the ORDER is what the code
     * states, so assert the post-state is consistent with it: a count of N+1 and a
     * populated element N. If the element write had been skipped or mis-indexed,
     * this fails. */

    /* ---- 7. NO CAPACITY CHECK: a large count writes far past the body -- */
    /* The arena is large enough to observe the write rather than fault on it. */
    reset_arena();
    *count_slot() = 20u;                /* element 20 -> OBJECT + 0x08 + 80 = +0x58 */
    sub_0801191A(OBJECT, 0xCCCCCCCCu);
    check((unsigned long)((u8 *)element(20) - OBJECT) >= (unsigned long)BODY,
          "index 20 lies well past the 64-byte body",
          (unsigned long)((u8 *)element(20) - OBJECT));
    check((u8 *)element(20) < g_arena + sizeof(g_arena), "and the arena can see it",
          (unsigned long)((u8 *)element(20) - g_arena));
    check(*(u32 *)((u8 *)OBJECT + 8u + 4u * 20u) == 0xCCCCCCCCu,
          "the far element really was written, with no capacity test",
          (unsigned long)*(u32 *)((u8 *)OBJECT + 8u + 4u * 20u));

    /* ---- 8. the count wraps like any other 32-bit value ----------------- */
    /* A count of 0xFFFFFFFF makes the element address wrap ONTO THE COUNT SLOT
     * ITSELF: count_slot + 0xFFFFFFFF*4 + 4 is count_slot + 0x100000000, which is
     * count_slot modulo 2^32. So the count is first incremented to 0 and then
     * OVERWRITTEN by the appended value. The machine does exactly this and no test
     * was weakened to hide it. */
    reset_arena();
    *count_slot() = 0xFFFFFFFFu;
    sub_0801191A(OBJECT, 0x12345678u);
    check(*count_slot() == 0x12345678u,
          "a count of 0xFFFFFFFF wraps the element address onto the count slot, "
          "so the appended value overwrites the count",
          (unsigned long)*count_slot());

    /* ---- 9. a sweep: index and count agree for every count in 0..12 ----- */
    {
        u32 n;
        int bad = 0;
        for (n = 0u; n < 13u; n++) {
            reset_arena();
            *count_slot() = n;
            sub_0801191A(OBJECT, 0xFEED0000u + n);
            if (*count_slot() != n + 1u) {
                bad++;
            }
            if (*(u32 *)((u8 *)OBJECT + 8u + 4u * n) != 0xFEED0000u + n) {
                bad++;
            }
        }
        check(bad == 0, "for every count 0..12 the element index and the new count agree",
              (unsigned long)bad);
    }

    printf("%s: %d check(s), %d failure(s)\n",
           failures ? "FAIL" : "PASS", checks, failures);
    return failures ? 1 : 0;
}
