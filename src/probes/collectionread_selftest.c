/*
 * src/probes/collectionread_selftest.c
 *
 * HOST SEMANTIC CHECK for sub_08011C70, the virtual-dispatch search over the
 * collection.
 *
 * Each fake element carries its OWN method, so the tests identify WHICH element was
 * called rather than merely counting calls. That distinction matters: an earlier
 * revision tracked call ORDER and silently confused it with element INDEX, which
 * made two traversal assertions wrong.
 *
 * Built 32-bit.
 */

#include <stdio.h>
#include <string.h>

#include "ByteCodeInterpreter_collectionread.c"

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
/* the per-element virtual methods                                            */
/* ------------------------------------------------------------------------- */
#define MAX_CALLS 32
#define N_FAKES 8

static u32 g_calls;
static u32 g_called[N_FAKES];       /* how many times each ELEMENT was called */
static u32 g_order[MAX_CALLS];      /* the element ids in call order          */
static u32 g_arg_a[MAX_CALLS];
static u32 g_arg_b[MAX_CALLS];
static u32 g_hit_element;           /* the element whose method returns non-zero */
static u32 g_hit_value;

static u32 record_and_decide(u32 id, u32 a, u32 b)
{
    if (g_calls < MAX_CALLS) {
        g_order[g_calls] = id;
        g_arg_a[g_calls] = a;
        g_arg_b[g_calls] = b;
    }
    g_calls++;
    if (id < N_FAKES) {
        g_called[id]++;
    }
    return (id == g_hit_element) ? g_hit_value : 0u;
}

#define DEF_METHOD(n) static u32 m##n(u32 a, u32 b) { return record_and_decide(n, a, b); }
DEF_METHOD(0) DEF_METHOD(1) DEF_METHOD(2) DEF_METHOD(3)
DEF_METHOD(4) DEF_METHOD(5) DEF_METHOD(6) DEF_METHOD(7)

typedef u32 (*method_t)(u32, u32);

static method_t g_methods[N_FAKES] = { m0, m1, m2, m3, m4, m5, m6, m7 };

/* ------------------------------------------------------------------------- */
/* the fake virtual objects                                                   */
/* ------------------------------------------------------------------------- */
typedef struct Fake {
    u32 *table;                 /* the FIRST word, which is what the ROM dereferences */
    u32 table_words[16];
} Fake;

static Fake g_fakes[N_FAKES];

static void fake_init(Fake *f, method_t method)
{
    memset(f, 0, sizeof(*f));
    f->table = f->table_words;
    /* word 9 sits at table + 0x24 and holds the OFFSET, because the machine
     * computes r3 = table + table[9]. */
    f->table_words[9] = (u32)method - (u32)(void *)f->table_words;
}

/* ------------------------------------------------------------------------- */
/* the collection                                                             */
/* ------------------------------------------------------------------------- */
#define ARENA 0x1000
static u8 g_arena[ARENA];
#define OBJECT ((void *)g_arena)
#define SECOND ((void *)(g_arena + 0x408))

static u32 *count_at(void *base) { return (u32 *)((u8 *)base + 4u); }
static u32 *value_at(void *base, u32 i) { return (u32 *)((u8 *)base + 8u + 4u * i); }

static void reset_all(void)
{
    int i;
    memset(g_arena, 0, sizeof(g_arena));
    g_calls = 0u;
    memset(g_called, 0, sizeof(g_called));
    memset(g_order, 0, sizeof(g_order));
    memset(g_arg_a, 0, sizeof(g_arg_a));
    memset(g_arg_b, 0, sizeof(g_arg_b));
    g_hit_element = 0xFFFFFFFFu;      /* nothing hits by default */
    g_hit_value = 0u;
    for (i = 0; i < N_FAKES; i++) {
        fake_init(&g_fakes[i], g_methods[i]);
    }
}

/* put fake k at index i of a collection */
static void place(void *base, u32 i, u32 k)
{
    *value_at(base, i) = (u32)&g_fakes[k];
}

int main(void)
{
    u32 i;
    /* Unbuffered, so a crash still shows how far the run got. */
    setvbuf(stdout, NULL, _IONBF, 0);
    printf("start\n");

    printf("section 1\n");
    /* ---- 1. an empty collection makes no call at all ------------------- */
    reset_all();
    *count_at(OBJECT) = 0u;
    *count_at(SECOND) = 0u;
    check(sub_08011C70(OBJECT, 7u, 9u) == 0u, "nothing matches, so it returns 0", 0ul);
    check(g_calls == 0u, "and an empty collection causes NO call", (unsigned long)g_calls);

    printf("section 2\n");
    /* ---- 2. traversal is BACKWARD: the TOP element is called FIRST ----- */
    reset_all();
    *count_at(OBJECT) = 3u;
    *count_at(SECOND) = 0u;
    place(OBJECT, 0u, 0u);          /* element 0 is fake 0 */
    place(OBJECT, 1u, 1u);
    place(OBJECT, 2u, 2u);          /* element 2, the TOP, is fake 2 */
    (void)sub_08011C70(OBJECT, 0u, 0u);
    check(g_calls == 3u, "all three elements are tested", (unsigned long)g_calls);
    check(g_order[0] == 2u && g_order[1] == 1u && g_order[2] == 0u,
          "the call order is element 2, then 1, then 0: FROM THE TOP DOWNWARD",
          (unsigned long)((g_order[0] << 16) | (g_order[1] << 8) | g_order[2]));

    printf("section 3\n");
    /* ---- 3. the count is the number of elements tested ----------------- */
    reset_all();
    *count_at(OBJECT) = 5u;
    *count_at(SECOND) = 0u;
    for (i = 0u; i < 5u; i++) {
        place(OBJECT, i, i);
    }
    (void)sub_08011C70(OBJECT, 0u, 0u);
    check(g_calls == 5u, "a count of 5 tests exactly 5 elements", (unsigned long)g_calls);
    check(g_order[0] == 4u, "starting at element 4", (unsigned long)g_order[0]);
    check(g_order[4] == 0u, "and ending at element 0", (unsigned long)g_order[4]);

    printf("section 4\n");
    /* ---- 4. the incoming arguments are forwarded unchanged ------------- */
    reset_all();
    *count_at(OBJECT) = 1u;
    *count_at(SECOND) = 0u;
    place(OBJECT, 0u, 0u);
    (void)sub_08011C70(OBJECT, 0x12345678u, 0x9ABCDEF0u);
    check(g_arg_a[0] == 0x12345678u, "arg a reaches the method unchanged",
          (unsigned long)g_arg_a[0]);
    check(g_arg_b[0] == 0x9ABCDEF0u, "arg b reaches the method unchanged",
          (unsigned long)g_arg_b[0]);

    printf("section 5\n");
    /* ---- 5. a non-zero result stops the search AT ONCE ----------------- */
    reset_all();
    *count_at(OBJECT) = 4u;
    *count_at(SECOND) = 0u;
    for (i = 0u; i < 4u; i++) {
        place(OBJECT, i, i);
    }
    g_hit_element = 3u;             /* the TOP element, called first */
    g_hit_value = 0xCAFEBABEu;
    check(sub_08011C70(OBJECT, 0u, 0u) == 0xCAFEBABEu,
          "the non-zero result is returned", 0ul);
    check(g_calls == 1u, "and the search STOPS at the first element tested",
          (unsigned long)g_calls);

    printf("section 6\n");
    /* ---- 6. reaching a lower element costs the calls above it ---------- */
    reset_all();
    *count_at(OBJECT) = 4u;
    *count_at(SECOND) = 0u;
    for (i = 0u; i < 4u; i++) {
        place(OBJECT, i, i);
    }
    g_hit_element = 1u;             /* third in a top-down traversal */
    g_hit_value = 0xDEADBEEFu;
    check(sub_08011C70(OBJECT, 0u, 0u) == 0xDEADBEEFu, "the hit is returned", 0ul);
    check(g_calls == 3u, "element 1 is reached on the THIRD call going top-down",
          (unsigned long)g_calls);
    check(g_order[0] == 3u && g_order[1] == 2u && g_order[2] == 1u,
          "and the order is 3, 2, 1",
          (unsigned long)((g_order[0] << 16) | (g_order[1] << 8) | g_order[2]));

    printf("section 7\n");
    /* ---- 7. the SECOND collection is searched after the first ---------- */
    reset_all();
    *count_at(OBJECT) = 2u;
    *count_at(SECOND) = 1u;
    place(OBJECT, 0u, 0u);
    place(OBJECT, 1u, 1u);
    place(SECOND, 0u, 2u);
    g_hit_element = 2u;
    g_hit_value = 0x5A5A5A5Au;
    check(sub_08011C70(OBJECT, 0u, 0u) == 0x5A5A5A5Au,
          "a hit in the SECOND collection is found and returned", 0ul);
    check(g_calls == 3u, "two calls in the first collection then one in the second",
          (unsigned long)g_calls);
    check(g_order[2] == 2u, "and the last call is the second collection's element",
          (unsigned long)g_order[2]);

    printf("section 8\n");
    /* ---- 8. the second collection is at +0x408, not +0x40C ------------- */
    reset_all();
    *count_at(OBJECT) = 0u;
    *count_at(SECOND) = 1u;
    place(SECOND, 0u, 0u);
    g_hit_element = 0u;
    g_hit_value = 0x77777777u;
    check(sub_08011C70(OBJECT, 0u, 0u) == 0x77777777u,
          "with the first collection empty the second is still searched", 0ul);
    check(g_calls == 1u, "and only the second collection is touched",
          (unsigned long)g_calls);

    printf("section 9\n");
    /* ---- 9. the count is NOT modified ---------------------------------- */
    reset_all();
    *count_at(OBJECT) = 3u;
    *count_at(SECOND) = 2u;
    for (i = 0u; i < 3u; i++) {
        place(OBJECT, i, i);
    }
    /* The second collection's elements MUST be placed too: a count with nothing
     * behind it makes the search dereference a null element. That is exactly how
     * the first revision of this check crashed. */
    place(SECOND, 0u, 4u);
    place(SECOND, 1u, 5u);
    (void)sub_08011C70(OBJECT, 0u, 0u);
    check(*count_at(OBJECT) == 3u, "the first collection's count is untouched",
          (unsigned long)*count_at(OBJECT));
    check(*count_at(SECOND) == 2u, "and so is the second's",
          (unsigned long)*count_at(SECOND));

    printf("section 10\n");
    /* ---- 10. +0x00 of the object is never written ---------------------- */
    reset_all();
    *(u32 *)g_arena = 0x0BADF00Du;
    *count_at(OBJECT) = 1u;
    *count_at(SECOND) = 0u;
    place(OBJECT, 0u, 0u);
    (void)sub_08011C70(OBJECT, 0u, 0u);
    check(*(u32 *)g_arena == 0x0BADF00Du,
          "object + 0x00 is not written by the reader",
          (unsigned long)*(u32 *)g_arena);

    printf("section 11\n");
    /* ---- 11. an element is dereferenced to reach its table ------------- */
    /* If the element were treated as the table itself rather than as a pointer to
     * it, the call would go somewhere else and the element method would not run. */
    reset_all();
    *count_at(OBJECT) = 1u;
    *count_at(SECOND) = 0u;
    place(OBJECT, 0u, 5u);
    (void)sub_08011C70(OBJECT, 0u, 0u);
    check(g_called[5] == 1u, "the ELEMENT's own table is used via its first word",
          (unsigned long)g_called[5]);

    printf("%s: %d check(s), %d failure(s)\n",
           failures ? "FAIL" : "PASS", checks, failures);
    return failures ? 1 : 0;
}
