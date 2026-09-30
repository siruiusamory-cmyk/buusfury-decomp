/*
 * src/probes/collectioninsert2_selftest.c
 *
 * HOST SEMANTIC CHECK for sub_08011732, the routine that inserts into the object's
 * SECOND collection at +0x408.
 *
 * Every element carries its OWN table, and the methods recover WHICH element they
 * were called on from the pointer they receive, so element identity is observable
 * rather than inferred from call order - the mistake that made an earlier ticket's
 * traversal assertions wrong.
 *
 * Built 32-bit.
 */

#include <stdio.h>
#include <string.h>

typedef unsigned int u32;

/* ------------------------------------------------------------------------- */
/* the mocks                                                                  */
/* ------------------------------------------------------------------------- */
#define N_FAKES 6
#define MAX_EVENTS 64

/* sub_080116FC returns 0, i.e. "below arg2", for the first g_pred_zero_calls
 * calls and then a large value, so the outer loop runs a CONTROLLED number of
 * passes. A fixed return value would either skip the scan entirely or spin
 * forever. */
static u32 g_pred_zero_calls;
static u32 g_predicate_calls;

static u32 g_remove_calls;
static void *g_remove_base;
static u32 g_remove_index;
static u32 g_remove_order[MAX_EVENTS];

static u32 g_cleanup_calls;
static u32 g_global_calls;
static u32 g_global_arg;

typedef struct Fake {
    u32 *table;
    u32 table_words[16];
} Fake;

static Fake g_fakes[N_FAKES];

/* the recorded verdicts and actions, indexed by fake */
static u32 g_verdict[N_FAKES];
static u32 g_pass_seen[N_FAKES];
static u32 g_verdict_calls[N_FAKES];
static u32 g_action04[N_FAKES];
static u32 g_action14[N_FAKES];
static u32 g_action1c[N_FAKES];
static u32 g_last_pass_arg;

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

/* slot +0x18: returns the verdict, and sees the pass counter */
static u32 method_verdict(u32 element, u32 pass)
{
    int k = fake_of(element);
    g_last_pass_arg = pass;
    if (k >= 0) {
        g_verdict_calls[k]++;
        g_pass_seen[k] = pass;
        return g_verdict[k];
    }
    return 0u;
}

/* slots +0x04, +0x14 and +0x1C: record which one ran, return zero */
static u32 method_04(u32 element)
{
    int k = fake_of(element);
    if (k >= 0) { g_action04[k]++; }
    return 0u;
}

static u32 method_14(u32 element)
{
    int k = fake_of(element);
    if (k >= 0) { g_action14[k]++; }
    return 0u;
}

static u32 method_1c(u32 element)
{
    int k = fake_of(element);
    if (k >= 0) { g_action1c[k]++; }
    return 0u;
}

u32 sub_080116FC(void *object)
{
    (void)object;
    g_predicate_calls++;
    if (g_pred_zero_calls > 0u) {
        g_pred_zero_calls--;
        return 0u;
    }
    return 999u;
}

void sub_080115B0(void *object)
{
    (void)object;
    g_cleanup_calls++;
}

void sub_0803DA62(u32 value)
{
    g_global_calls++;
    g_global_arg = value;
}

/*
 * THE ARGUMENT IS THE COUNT SLOT, NOT THE COLLECTION BASE.
 * This routine passes r7, which it set to object + 4, and sub_080119BC passes
 * object + 0x40C - both are the count slot of the collection concerned. An earlier
 * revision of this mock added 4 and wrote into the ELEMENTS area instead, which
 * corrupted element 0 and made the routine dereference a garbage pointer.
 */
void sub_0804FE54(void *count_slot, u32 index)
{
    u32 *count = (u32 *)count_slot;
    g_remove_base = count_slot;
    g_remove_index = index;
    if (g_remove_calls < MAX_EVENTS) {
        g_remove_order[g_remove_calls] = index;
    }
    g_remove_calls++;
    if (*count > 0u) {
        *count = *count - 1u;
    }
}

/*
 * THE ROUTINE READS A WORD FROM A FIXED ROM ADDRESS. On the host that address is
 * not mapped, so the source redirects it behind this macro. Forgetting to define
 * the macro was the cause of a crash that took several probes to locate: the
 * routine was still dereferencing 0x08072824.
 */
#define COLLECTIONINSERT2_HOST_TEST 1

u32 collectioninsert2_host_global_word;

#include "ByteCodeInterpreter_collectioninsert2.c"

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

static u32 *first_count(void) { return (u32 *)((u8 *)OBJECT + 4u); }
static u32 *first_value(u32 i) { return (u32 *)((u8 *)OBJECT + 8u + 4u * i); }
static u32 *second_count(void) { return (u32 *)((u8 *)OBJECT + 0x40Cu); }
static u32 *second_value(u32 i) { return (u32 *)((u8 *)OBJECT + 0x410u + 4u * i); }
static u32 *third_count(void) { return (u32 *)((u8 *)OBJECT + 0x208u); }
static u32 *third_value(u32 i) { return (u32 *)((u8 *)OBJECT + 0x20Cu + 4u * i); }

static void fake_init(Fake *f)
{
    memset(f, 0, sizeof(*f));
    f->table = f->table_words;
    f->table_words[1] = (u32)method_04 - (u32)(void *)f->table_words;   /* +0x04 */
    f->table_words[5] = (u32)method_14 - (u32)(void *)f->table_words;   /* +0x14 */
    f->table_words[6] = (u32)method_verdict - (u32)(void *)f->table_words; /* +0x18 */
    f->table_words[7] = (u32)method_1c - (u32)(void *)f->table_words;   /* +0x1C */
}

static void reset_all(void)
{
    int i;
    memset(g_arena, 0, sizeof(g_arena));
    g_pred_zero_calls = 0u;
    g_predicate_calls = 0u;
    g_remove_calls = 0u;
    g_remove_base = NULL;
    g_remove_index = 0xFFFFFFFFu;
    g_cleanup_calls = 0u;
    g_global_calls = 0u;
    g_last_pass_arg = 0xFFFFFFFFu;
    memset(g_remove_order, 0, sizeof(g_remove_order));
    memset(g_verdict, 0, sizeof(g_verdict));
    memset(g_pass_seen, 0, sizeof(g_pass_seen));
    memset(g_verdict_calls, 0, sizeof(g_verdict_calls));
    memset(g_action04, 0, sizeof(g_action04));
    memset(g_action14, 0, sizeof(g_action14));
    memset(g_action1c, 0, sizeof(g_action1c));
    for (i = 0; i < N_FAKES; i++) {
        fake_init(&g_fakes[i]);
    }
}

int main(void)
{
    u32 i;
    setvbuf(stdout, NULL, _IONBF, 0);

    /* ---- 1. verdict 2 inserts into the SECOND and removes from the FIRST -- */
    reset_all();
    g_pred_zero_calls = 1u;   /* one outer pass */
    *first_count() = 2u;
    *first_value(0u) = (u32)&g_fakes[0];
    *first_value(1u) = (u32)&g_fakes[1];
    g_verdict[1] = 2u;                    /* the TOP element migrates         */
    sub_08011732(OBJECT, 1u);

    check(*second_count() == 1u, "the second collection's count is incremented",
          (unsigned long)*second_count());
    check(*second_value(0u) == (u32)&g_fakes[1],
          "and the element lands at index 0, the OLD count",
          (unsigned long)*second_value(0u));
    check(g_action1c[1] == 1u, "the element's +0x1C method ran before the insertion",
          (unsigned long)g_action1c[1]);
    check(g_remove_calls == 1u, "and the element is removed from the first collection",
          (unsigned long)g_remove_calls);
    check(g_remove_base == first_count(),
          "the removal targets the FIRST collection's count slot",
          (unsigned long)((u8 *)g_remove_base - g_arena));
    check(g_remove_index == 1u, "at the index the loop was on",
          (unsigned long)g_remove_index);
    check(*first_count() == 1u, "so the first collection shrinks",
          (unsigned long)*first_count());
    check(g_action04[1] == 0u, "and the +0x04 method did NOT run on this path",
          (unsigned long)g_action04[1]);

    /* ---- 2. verdict 1 removes from the FIRST and does NOT insert -------- */
    reset_all();
    g_pred_zero_calls = 1u;   /* one outer pass */
    *first_count() = 1u;
    *first_value(0u) = (u32)&g_fakes[2];
    g_verdict[2] = 1u;
    sub_08011732(OBJECT, 1u);
    check(g_action04[2] == 1u, "the +0x04 method runs on a verdict of 1",
          (unsigned long)g_action04[2]);
    check(*second_count() == 0u, "but NOTHING is inserted into the second collection",
          (unsigned long)*second_count());
    check(g_remove_calls == 1u, "and the element still leaves the first collection",
          (unsigned long)g_remove_calls);

    /* ---- 3. verdict 0 leaves the element alone --------------------------- */
    reset_all();
    g_pred_zero_calls = 1u;   /* one outer pass */
    *first_count() = 1u;
    *first_value(0u) = (u32)&g_fakes[3];
    g_verdict[3] = 0u;
    sub_08011732(OBJECT, 1u);
    check(*second_count() == 0u, "no insertion", (unsigned long)*second_count());
    check(g_remove_calls == 0u, "and no removal", (unsigned long)g_remove_calls);
    check(g_action04[3] == 0u && g_action1c[3] == 0u, "and no method ran for it", 0ul);

    /* ---- 4. the inner loop runs BACKWARD -------------------------------- */
    reset_all();
    g_pred_zero_calls = 1u;   /* one outer pass */
    *first_count() = 3u;
    *first_value(0u) = (u32)&g_fakes[0];
    *first_value(1u) = (u32)&g_fakes[1];
    *first_value(2u) = (u32)&g_fakes[2];
    g_verdict[2] = 2u;                    /* only the TOP migrates */
    sub_08011732(OBJECT, 1u);
    check(g_remove_index == 2u,
          "the removal index is 2, so the TOP element was examined FIRST",
          (unsigned long)g_remove_index);
    check(g_last_pass_arg == 0u, "and the pass counter handed to the method was 0",
          (unsigned long)g_last_pass_arg);

    /* ---- 5. insertion uses the OLD count as the index -------------------- */
    reset_all();
    g_pred_zero_calls = 1u;   /* one outer pass */
    *first_count() = 1u;
    *first_value(0u) = (u32)&g_fakes[0];
    *second_count() = 4u;                 /* there are already four elements  */
    g_verdict[0] = 2u;
    sub_08011732(OBJECT, 1u);
    check(*second_count() == 5u, "the second count goes from 4 to 5",
          (unsigned long)*second_count());
    check(*second_value(4u) == (u32)&g_fakes[0],
          "and the element is written at index 4, the count BEFORE the increment",
          (unsigned long)*second_value(4u));
    check(*second_value(3u) == 0u, "index 3 is untouched",
          (unsigned long)*second_value(3u));

    /* ---- 6. there is NO duplicate check --------------------------------- */
    /* The same element inserted twice is appended twice: nothing compares it
     * against what the second collection already holds. */
    reset_all();
    g_pred_zero_calls = 1u;   /* one outer pass */
    *first_count() = 2u;
    *first_value(1u) = (u32)&g_fakes[0];
    *first_value(0u) = (u32)&g_fakes[0];
    g_verdict[0] = 2u;
    sub_08011732(OBJECT, 1u);
    check(*second_count() == 2u,
          "the same element is appended TWICE: no duplicate check exists",
          (unsigned long)*second_count());

    /* ---- 7. the THIRD collection is walked and then FLUSHED ------------- */
    reset_all();
    g_pred_zero_calls = 1u;   /* one outer pass */
    *third_count() = 2u;
    *third_value(0u) = (u32)&g_fakes[4];
    *third_value(1u) = (u32)&g_fakes[5];
    sub_08011732(OBJECT, 1u);
    check(g_action14[4] == 1u && g_action14[5] == 1u,
          "the +0x14 method runs for every element of the third collection",
          (unsigned long)(g_action14[4] + g_action14[5]));
    check(*third_count() == 0u, "and the third collection's count is set to ZERO",
          (unsigned long)*third_count());

    /* ---- 8. the post-scan calls happen ---------------------------------- */
    reset_all();
    g_pred_zero_calls = 0u;   /* no scan */
    sub_08011732(OBJECT, 1u);
    check(g_cleanup_calls == 1u, "the cleanup call happens once",
          (unsigned long)g_cleanup_calls);
    check(g_global_calls == 1u, "and so does the global call",
          (unsigned long)g_global_calls);

    /* ---- 9. +0x00 is not touched ---------------------------------------- */
    reset_all();
    *(u32 *)g_arena = 0x0BADF00Du;
    g_pred_zero_calls = 0u;   /* no scan */
    sub_08011732(OBJECT, 1u);
    check(*(u32 *)g_arena == 0x0BADF00Du,
          "object + 0x00 is neither read nor written",
          (unsigned long)*(u32 *)g_arena);

    /* ---- 10. the outer condition gates the whole scan -------------------- */
    reset_all();
    g_pred_zero_calls = 0u;   /* no scan */
    *first_count() = 2u;
    *first_value(1u) = (u32)&g_fakes[0];
    g_verdict[0] = 2u;
    sub_08011732(OBJECT, 1u);
    check(*second_count() == 0u,
          "with the outer condition false nothing is ever inserted",
          (unsigned long)*second_count());
    check(g_verdict_calls[0] == 0u, "and no element is even examined",
          (unsigned long)g_verdict_calls[0]);

    printf("%s: %d check(s), %d failure(s)\n",
           failures ? "FAIL" : "PASS", checks, failures);
    return failures ? 1 : 0;
}
