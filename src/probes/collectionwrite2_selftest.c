/*
 * src/probes/collectionwrite2_selftest.c
 *
 * HOST SEMANTIC CHECK for sub_080119BC, the keyed move across the two collections.
 * The removal helper is MOCKED so its arguments are observable.
 *
 * Built 32-bit.
 */

#include <stdio.h>
#include <string.h>

typedef unsigned int u32;

static u32 g_remove_calls;
static void *g_remove_base;
static u32 g_remove_index;

void sub_0804FE54(void *collection, u32 index)
{
    u32 *count = (u32 *)((unsigned char *)collection + 4u);
    g_remove_calls++;
    g_remove_base = collection;
    g_remove_index = index;
    /* a faithful-enough mock: shrink the count so the state stays coherent */
    if (*count > 0u) {
        *count = *count - 1u;
    }
}

#include "ByteCodeInterpreter_collectionwrite2.c"

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

#define ARENA 0x1000
static u8 g_arena[ARENA];
#define OBJECT ((void *)g_arena)
#define SECOND ((void *)(g_arena + 0x408))

static u32 *count_at(void *base) { return (u32 *)((u8 *)base + 4u); }
static u32 *value_at(void *base, u32 i) { return (u32 *)((u8 *)base + 8u + 4u * i); }

static void reset_all(void)
{
    memset(g_arena, 0, sizeof(g_arena));
    g_remove_calls = 0u;
    g_remove_base = NULL;
    g_remove_index = 0xFFFFFFFFu;
}

int main(void)
{
    setvbuf(stdout, NULL, _IONBF, 0);

    /* ---- 1. a key present in the FIRST collection is REPLACED in place -- */
    reset_all();
    *count_at(OBJECT) = 3u;
    *value_at(OBJECT, 0u) = 0xAAu;
    *value_at(OBJECT, 1u) = 0xBBu;
    *value_at(OBJECT, 2u) = 0xCCu;
    sub_080119BC(OBJECT, 0xBBu, 0x1234u);
    check(*value_at(OBJECT, 1u) == 0x1234u, "the matching element is overwritten",
          (unsigned long)*value_at(OBJECT, 1u));
    check(*count_at(OBJECT) == 3u, "the count is NOT changed by a replace",
          (unsigned long)*count_at(OBJECT));
    check(g_remove_calls == 0u, "and nothing is removed", (unsigned long)g_remove_calls);
    check(*value_at(OBJECT, 0u) == 0xAAu && *value_at(OBJECT, 2u) == 0xCCu,
          "the other elements are untouched", (unsigned long)*value_at(OBJECT, 0u));

    /* ---- 2. the FIRST match wins, scanning FORWARD --------------------- */
    reset_all();
    *count_at(OBJECT) = 3u;
    *value_at(OBJECT, 0u) = 0x55u;
    *value_at(OBJECT, 1u) = 0x55u;
    *value_at(OBJECT, 2u) = 0x55u;
    sub_080119BC(OBJECT, 0x55u, 0x9999u);
    check(*value_at(OBJECT, 0u) == 0x9999u,
          "the FIRST match is the one replaced", (unsigned long)*value_at(OBJECT, 0u));
    check(*value_at(OBJECT, 1u) == 0x55u && *value_at(OBJECT, 2u) == 0x55u,
          "later matches are left alone", (unsigned long)*value_at(OBJECT, 1u));

    /* ---- 3. absent from the first but present in the SECOND ------------ */
    reset_all();
    *count_at(OBJECT) = 1u;
    *value_at(OBJECT, 0u) = 0x01u;
    *count_at(SECOND) = 2u;
    *value_at(SECOND, 0u) = 0x77u;
    *value_at(SECOND, 1u) = 0x88u;
    sub_080119BC(OBJECT, 0x88u, 0xABCDu);
    check(g_remove_calls == 1u, "the key is REMOVED from the second collection",
          (unsigned long)g_remove_calls);
    check(g_remove_base == SECOND, "and the removal targets the second collection",
          (unsigned long)((u8 *)g_remove_base - g_arena));
    check(g_remove_index == 1u, "at the index where the key was found",
          (unsigned long)g_remove_index);
    check(*count_at(OBJECT) == 2u, "and the value is APPENDED to the first collection",
          (unsigned long)*count_at(OBJECT));
    check(*value_at(OBJECT, 1u) == 0xABCDu, "at the first collection's new tail",
          (unsigned long)*value_at(OBJECT, 1u));
    check(*value_at(OBJECT, 0u) == 0x01u, "leaving the first collection's head alone",
          (unsigned long)*value_at(OBJECT, 0u));

    /* ---- 4. absent from BOTH: no removal, straight append -------------- */
    reset_all();
    *count_at(OBJECT) = 2u;
    *value_at(OBJECT, 0u) = 0x10u;
    *value_at(OBJECT, 1u) = 0x20u;
    *count_at(SECOND) = 1u;
    *value_at(SECOND, 0u) = 0x30u;
    sub_080119BC(OBJECT, 0xFEEDu, 0x5150u);
    check(g_remove_calls == 0u, "nothing is removed when the key is in neither",
          (unsigned long)g_remove_calls);
    check(*count_at(OBJECT) == 3u, "the value is still appended to the first",
          (unsigned long)*count_at(OBJECT));
    check(*value_at(OBJECT, 2u) == 0x5150u, "at index 2",
          (unsigned long)*value_at(OBJECT, 2u));
    check(*count_at(SECOND) == 1u,
          "and the SECOND collection's count is NOT incremented by this routine",
          (unsigned long)*count_at(SECOND));

    /* ---- 5. an empty first collection appends at index 0 --------------- */
    reset_all();
    *count_at(OBJECT) = 0u;
    *count_at(SECOND) = 0u;
    sub_080119BC(OBJECT, 0u, 0xBEEFu);
    check(*count_at(OBJECT) == 1u, "an empty collection takes the value as its first",
          (unsigned long)*count_at(OBJECT));
    check(*value_at(OBJECT, 0u) == 0xBEEFu, "at index 0",
          (unsigned long)*value_at(OBJECT, 0u));

    /* ---- 6. the value is stored VERBATIM ------------------------------- */
    {
        static const u32 samples[4] = { 0u, 0xFFFFFFFFu, 0x80000000u, 0x0000FFFFu };
        int bad = 0, i;
        for (i = 0; i < 4; i++) {
            reset_all();
            *count_at(OBJECT) = 0u;
            *count_at(SECOND) = 0u;
            sub_080119BC(OBJECT, 1u, samples[i]);
            if (*value_at(OBJECT, 0u) != samples[i]) {
                bad++;
            }
        }
        check(bad == 0, "0, 0xFFFFFFFF, 0x80000000 and 0x0000FFFF arrive verbatim",
              (unsigned long)bad);
    }

    /* ---- 7. the SECOND collection's count is untouched on the replace path */
    reset_all();
    *count_at(OBJECT) = 1u;
    *value_at(OBJECT, 0u) = 0x42u;
    *count_at(SECOND) = 4u;
    sub_080119BC(OBJECT, 0x42u, 0x1u);
    check(*count_at(SECOND) == 4u,
          "a replace in the first collection leaves the second entirely alone",
          (unsigned long)*count_at(SECOND));

    /* ---- 8. +0x00 is not touched -------------------------------------- */
    reset_all();
    *(u32 *)g_arena = 0x0BADF00Du;
    *count_at(OBJECT) = 0u;
    *count_at(SECOND) = 0u;
    sub_080119BC(OBJECT, 3u, 4u);
    check(*(u32 *)g_arena == 0x0BADF00Du,
          "object + 0x00 is neither read nor written",
          (unsigned long)*(u32 *)g_arena);

    printf("%s: %d check(s), %d failure(s)\n",
           failures ? "FAIL" : "PASS", checks, failures);
    return failures ? 1 : 0;
}
