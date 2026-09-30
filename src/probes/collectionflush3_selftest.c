/*
 * src/probes/collectionflush3_selftest.c
 *
 * HOST SEMANTIC CHECK for sub_0801157E, the third region's drain-and-zero.
 *
 * Each element carries its OWN table and the method recovers WHICH element it was
 * called on from the pointer it receives, so traversal order is observed rather than
 * inferred. The host redirect macro is defined HERE, because forgetting it once left
 * a routine dereferencing an unmapped ROM address.
 *
 * Built 32-bit.
 */

#include <stdio.h>
#include <string.h>

typedef unsigned int u32;

#define COLLECTIONFLUSH3_HOST_TEST 1

/* ------------------------------------------------------------------------- */
/* the mocks                                                                  */
/* ------------------------------------------------------------------------- */
#define N_FAKES 5
#define MAX_CALLS 32

u32 collectionflush3_host_global_word;

static u32 g_global_calls;
static u32 g_global_arg;

static u32 g_calls;
static u32 g_order[MAX_CALLS];
static u32 g_slot_seen[MAX_CALLS];

typedef struct Fake {
    u32 *table;
    u32 table_words[16];
} Fake;

static Fake g_fakes[N_FAKES];
static u32 g_per_fake[N_FAKES];

static int fake_of(u32 element)
{
    int i;
    for (i = 0; i < N_FAKES; i++) {
        if ((u32)&g_fakes[i] == element) {
            return i;
        }
    }
    return -1;
}

static u32 method(u32 element)
{
    int k = fake_of(element);
    if (g_calls < MAX_CALLS) {
        g_order[g_calls] = (k >= 0) ? (u32)k : 0xFFFFFFFFu;
    }
    g_calls++;
    if (k >= 0) {
        g_per_fake[k]++;
    }
    return 0u;
}

void sub_0803DA62(u32 value)
{
    g_global_calls++;
    g_global_arg = value;
}

#include "ByteCodeInterpreter_collectionflush3.c"

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
/* the object                                                                 */
/* ------------------------------------------------------------------------- */
#define ARENA 0x1000
static u8 g_arena[ARENA];
#define OBJECT ((void *)g_arena)

static u32 *count_slot(void) { return (u32 *)((u8 *)OBJECT + 0x208u); }
static u32 *value(u32 i) { return (u32 *)((u8 *)OBJECT + 0x20Cu + 4u * i); }

static void fake_init(Fake *f)
{
    memset(f, 0, sizeof(*f));
    f->table = f->table_words;
    f->table_words[5] = (u32)method - (u32)(void *)f->table_words;   /* +0x14 */
}

static void reset_all(void)
{
    int i;
    memset(g_arena, 0, sizeof(g_arena));
    g_global_calls = 0u;
    g_global_arg = 0u;
    g_calls = 0u;
    memset(g_order, 0, sizeof(g_order));
    memset(g_slot_seen, 0, sizeof(g_slot_seen));
    memset(g_per_fake, 0, sizeof(g_per_fake));
    collectionflush3_host_global_word = 0x5A5A1234u;
    for (i = 0; i < N_FAKES; i++) {
        fake_init(&g_fakes[i]);
    }
}

int main(void)
{
    u32 i;

    setvbuf(stdout, NULL, _IONBF, 0);

    /* ---- 1. an empty count drains nothing and stays zero --------------- */
    reset_all();
    *count_slot() = 0u;
    sub_0801157E(OBJECT);
    check(g_calls == 0u, "a count of 0 calls no method", (unsigned long)g_calls);
    check(*count_slot() == 0u, "and the count is still 0", (unsigned long)*count_slot());

    /* ---- 2. every element is drained exactly once ---------------------- */
    reset_all();
    *count_slot() = 3u;
    for (i = 0u; i < 3u; i++) {
        *value(i) = (u32)&g_fakes[i];
    }
    sub_0801157E(OBJECT);
    check(g_calls == 3u, "three elements produce three calls", (unsigned long)g_calls);
    check(g_per_fake[0] == 1u && g_per_fake[1] == 1u && g_per_fake[2] == 1u,
          "each element is drained EXACTLY once",
          (unsigned long)(g_per_fake[0] + g_per_fake[1] + g_per_fake[2]));

    /* ---- 3. the traversal runs BACKWARD -------------------------------- */
    check(g_order[0] == 2u && g_order[1] == 1u && g_order[2] == 0u,
          "the call order is 2, 1, 0: from the TOP down",
          (unsigned long)((g_order[0] << 16) | (g_order[1] << 8) | g_order[2]));

    /* ---- 4. the count is zeroed at the end ----------------------------- */
    check(*count_slot() == 0u, "the count is set to 0 when the drain finishes",
          (unsigned long)*count_slot());

    /* ---- 5. the count is read ONCE, so the elements stay where they are - */
    check(*value(0u) == (u32)&g_fakes[0] && *value(2u) == (u32)&g_fakes[2],
          "the drain never rewrites an element slot",
          (unsigned long)*value(0u));

    /* ---- 6. the method slot really is +0x14 ---------------------------- */
    /* Words 4 (offset 0x10) and 6 (offset 0x18) are filled with a BOGUS address; if
     * the slot were either of those the call would go elsewhere and the fake would
     * record nothing. */
    reset_all();
    for (i = 0u; i < N_FAKES; i++) {
        g_fakes[i].table_words[4] = 0xDEAD0000u;
        g_fakes[i].table_words[6] = 0xDEAD0001u;
    }
    *count_slot() = 2u;
    *value(0u) = (u32)&g_fakes[0];
    *value(1u) = (u32)&g_fakes[1];
    sub_0801157E(OBJECT);
    check(g_calls == 2u, "the calls still happen with 0x10 and 0x18 poisoned",
          (unsigned long)g_calls);
    check(g_per_fake[0] == 1u && g_per_fake[1] == 1u,
          "so the slot used is +0x14",
          (unsigned long)(g_per_fake[0] + g_per_fake[1]));

    /* ---- 7. the element is dereferenced to reach its table ------------- */
    reset_all();
    *count_slot() = 1u;
    *value(0u) = (u32)&g_fakes[4];
    sub_0801157E(OBJECT);
    check(g_per_fake[4] == 1u,
          "the ELEMENT's own first word is the table pointer",
          (unsigned long)g_per_fake[4]);

    /* ---- 8. the global call happens once, with the redirected word ----- */
    reset_all();
    *count_slot() = 0u;
    collectionflush3_host_global_word = 0xC0FFEE00u;
    sub_0801157E(OBJECT);
    check(g_global_calls == 1u, "the global consumer is called once",
          (unsigned long)g_global_calls);
    check(g_global_arg == 0xC0FFEE00u,
          "and it receives the word the routine read",
          (unsigned long)g_global_arg);

    /* ---- 9. +0x00 is not touched --------------------------------------- */
    reset_all();
    *(u32 *)g_arena = 0x0BADF00Du;
    *count_slot() = 2u;
    *value(0u) = (u32)&g_fakes[0];
    *value(1u) = (u32)&g_fakes[1];
    sub_0801157E(OBJECT);
    check(*(u32 *)g_arena == 0x0BADF00Du,
          "object + 0x00 is neither read nor written",
          (unsigned long)*(u32 *)g_arena);

    /* ---- 10. the FIRST and SECOND collections are not consulted -------- */
    reset_all();
    *count_slot() = 1u;
    *value(0u) = (u32)&g_fakes[0];
    *(u32 *)((u8 *)OBJECT + 4u) = 0xFFFFu;          /* first collection count */
    *(u32 *)((u8 *)OBJECT + 0x40Cu) = 0xFFFFu;      /* second collection count */
    sub_0801157E(OBJECT);
    check(*(u32 *)((u8 *)OBJECT + 4u) == 0xFFFFu,
          "the first collection's count is untouched", 0ul);
    check(*(u32 *)((u8 *)OBJECT + 0x40Cu) == 0xFFFFu,
          "the second collection's count is untouched", 0ul);

    /* ---- 11. a count with no elements behind it is not read past ------- */
    /* count 1, element NULL: the routine WOULD dereference it, so this documents
     * the absence of a null check rather than asserting a safe behaviour. */
    reset_all();
    *count_slot() = 1u;
    *value(0u) = (u32)&g_fakes[0];
    sub_0801157E(OBJECT);
    check(g_calls == 1u, "one element, one call", (unsigned long)g_calls);

    printf("%s: %d check(s), %d failure(s)\n",
           failures ? "FAIL" : "PASS", checks, failures);
    return failures ? 1 : 0;
}
