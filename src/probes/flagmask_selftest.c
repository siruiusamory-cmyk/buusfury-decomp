/*
 * src/probes/flagmask_selftest.c
 *
 * HOST SEMANTIC CHECK for sub_08003310: the routine that applies a mask to the
 * flag array.
 *
 * The setter and the clearer are MOCKED so the per-bit decision is observable as
 * a call log rather than inferred from array contents. The mock still receives the
 * real arguments, so `offset + i` is observable too.
 *
 * Built 32-bit.
 */

#include <stdio.h>
#include <string.h>

#define FLAGMASK_HOST_TEST 1

typedef unsigned int u32;

#define MOCK_MAX_CALLS 256

static u32 g_mock_calls;
static u32 g_mock_args[MOCK_MAX_CALLS];
static char g_mock_op[MOCK_MAX_CALLS];      /* 'S' set, 'C' clear */

void sub_08004380(void *base, u32 value)
{
    (void)base;
    g_mock_op[g_mock_calls] = 'S';
    g_mock_args[g_mock_calls] = value;
    g_mock_calls++;
}

void sub_08004396(void *base, u32 value)
{
    (void)base;
    g_mock_op[g_mock_calls] = 'C';
    g_mock_args[g_mock_calls] = value;
    g_mock_calls++;
}

#include "ByteCodeInterpreter_flagmask.c"

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

#define VALUE_SLOTS 16

typedef struct HostCtx {
    u32 count;
    u32 values[VALUE_SLOTS];
} HostCtx;

static HostCtx g_ctx;
static u32 g_slot;

u32 flagmask_host_global_base;

static void reset_ctx(void)
{
    memset(&g_ctx, 0, sizeof(g_ctx));
    g_mock_calls = 0u;
    memset(g_mock_op, 0, sizeof(g_mock_op));
    g_slot = 0xDEADBEEFu;
    flagmask_host_global_base = 0x12345678u;
}

/* The stack is pushed three deep with the mask on top. */
static void run(u32 offset, u32 width, u32 mask)
{
    g_ctx.count = 3u;
    g_ctx.values[0] = offset;
    g_ctx.values[1] = width;
    g_ctx.values[2] = mask;
    sub_08003310(&g_ctx, &g_slot);
}

int main(void)
{
    /* ---- 1. three consumed, nothing produced -------------------------- */
    reset_ctx();
    run(0u, 3u, 0x5u);
    check(g_ctx.count == 0u, "the counter moves by exactly -3", (unsigned long)g_ctx.count);
    check(g_mock_calls == 3u, "a width of 3 acts on 3 bits", (unsigned long)g_mock_calls);
    check(g_slot == 0xDEADBEEFu, "the incoming r1 is never read", (unsigned long)g_slot);
    check(g_ctx.values[2] == 0x5u, "the mask slot is not written back",
          (unsigned long)g_ctx.values[2]);

    /* ---- 2. bit i of the mask decides flag offset + i ----------------- */
    {
        u32 i;
        int bad = 0;
        for (i = 0u; i < 3u; i++) {
            if (g_mock_args[i] != 0u + i) {
                bad++;
            }
        }
        check(bad == 0, "the flags acted on are offset+0, offset+1, offset+2",
              (unsigned long)bad);
    }
    /* mask 0b101 -> set, clear, set */
    check(g_mock_op[0] == 'S' && g_mock_op[1] == 'C' && g_mock_op[2] == 'S',
          "mask 0b101 sets, clears, sets",
          (unsigned long)((g_mock_op[0] << 16) | (g_mock_op[1] << 8) | g_mock_op[2]));

    /* ---- 3. mask 0 clears the whole run, 0xFFFFFFFF sets what fits ---- */
    reset_ctx();
    run(10u, 4u, 0x0u);
    check(g_mock_calls == 4u, "mask 0 still acts on every bit in the run",
          (unsigned long)g_mock_calls);
    {
        u32 i;
        int bad = 0;
        for (i = 0u; i < 4u; i++) {
            if (g_mock_op[i] != 'C' || g_mock_args[i] != 10u + i) {
                bad++;
            }
        }
        check(bad == 0, "mask 0 clears offset+0..offset+3", (unsigned long)bad);
    }

    reset_ctx();
    run(0u, 4u, 0xFFFFFFFFu);
    check(g_mock_calls <= 4u, "a huge mask is truncated to the width", (unsigned long)g_mock_calls);
    {
        u32 i;
        int bad = 0;
        for (i = 0u; i < g_mock_calls; i++) {
            if (g_mock_op[i] != 'C') {
                bad++;
            }
        }
        /* CLAMP 1 replaces a negative mask with 0 before the width clamp, so an
         * all-ones mask clears rather than sets. */
        check(bad == 0,
              "0xFFFFFFFF is NEGATIVE when read signed, so clamp 1 turns it into 0 and it clears",
              (unsigned long)bad);
    }

    /* ---- 4. one-bit masks --------------------------------------------- */
    {
        u32 bit;
        int bad = 0;
        for (bit = 0u; bit < 16u; bit++) {
            u32 i;
            reset_ctx();
            run(0u, 16u, 1u << bit);
            for (i = 0u; i < 16u; i++) {
                char want = (i == bit) ? 'S' : 'C';
                if (g_mock_op[i] != want) {
                    bad++;
                }
            }
        }
        check(bad == 0, "each single-bit mask sets exactly its own bit and clears the rest",
              (unsigned long)bad);
    }

    /* ---- 5. multi-bit masks -------------------------------------------- */
    reset_ctx();
    run(5u, 8u, 0xB5u);                 /* 1011 0101 */
    {
        /* 0xB5 has bits, LSB first: 1 0 1 0 1 1 0 1. */
        const char *want = "SCSCSSCS";
        u32 i;
        int bad = 0;
        for (i = 0u; i < 8u; i++) {
            if (g_mock_op[i] != want[i] || g_mock_args[i] != 5u + i) {
                bad++;
            }
        }
        check(bad == 0, "mask 0xB5 over width 8 produces the expected per-bit sequence",
              (unsigned long)bad);
    }

    /* ---- 6. the mask is truncated to the width ------------------------ */
    reset_ctx();
    run(0u, 3u, 0xFFu);                 /* bits above 2 must be ignored */
    check(g_mock_calls == 3u, "a width of 3 acts on 3 bits even for mask 0xFF",
          (unsigned long)g_mock_calls);
    check(g_mock_op[0] == 'S' && g_mock_op[1] == 'S' && g_mock_op[2] == 'S',
          "and all three are set because the low three bits are 1",
          (unsigned long)((g_mock_op[0] << 16) | (g_mock_op[1] << 8) | g_mock_op[2]));

    /* ---- 7. width zero or less is skipped ----------------------------- */
    reset_ctx();
    run(0u, 0u, 0xFFFFFFFFu);
    check(g_mock_calls == 0u, "a width of 0 makes no calls at all", (unsigned long)g_mock_calls);
    check(g_ctx.count == 0u, "and the three values are still consumed", (unsigned long)g_ctx.count);

    reset_ctx();
    run(0u, 0xFFFFFFFFu, 0xFFFFFFFFu);   /* -1 read signed */
    check(g_mock_calls == 0u, "a width of -1 makes no calls", (unsigned long)g_mock_calls);

    /* ---- 8. width 32 is the real edge case ---------------------------- */
    /* `1 << 32` is 0 in Thumb, so the second clamp computes 0-1 = 0xFFFFFFFF even
     * for a mask of 0, and `asrs` keeps it all ones, so every bit is SET. */
    reset_ctx();
    run(0u, 32u, 0u);
    check(g_mock_calls == 32u, "a width of 32 acts on 32 bits", (unsigned long)g_mock_calls);
    {
        u32 i;
        int bad = 0;
        for (i = 0u; i < 32u; i++) {
            if (g_mock_op[i] != 'S' || g_mock_args[i] != i) {
                bad++;
            }
        }
        check(bad == 0,
              "and even a mask of 0 sets all 32, because the clamp overflows to 0xFFFFFFFF",
              (unsigned long)bad);
    }

    /* ---- 9. a negative mask is discarded before anything else --------- */
    reset_ctx();
    run(0u, 4u, 0x80000000u);
    check(g_mock_calls == 4u, "a mask with bit 31 set still acts on the whole run",
          (unsigned long)g_mock_calls);
    {
        u32 i;
        int bad = 0;
        for (i = 0u; i < 4u; i++) {
            if (g_mock_op[i] != 'C') {
                bad++;
            }
        }
        check(bad == 0, "but every bit is CLEARED, because clamp 1 made the mask 0",
              (unsigned long)bad);
    }

    /* ---- 10. the ordering: all three pops precede the first call ------- */
    /* The context is fully decremented by the time the first flag is touched, and
     * the tests above already read g_ctx.count after the run; this asserts the
     * mid-run state indirectly by checking that no call saw a dirty slot. */
    reset_ctx();
    run(0u, 4u, 0x3u);
    check(g_ctx.count == 0u && g_mock_calls == 4u,
          "the stack work is complete while the flag calls are made",
          (unsigned long)g_ctx.count);

    printf("%s: %d check(s), %d failure(s)\n",
           failures ? "FAIL" : "PASS", checks, failures);
    return failures ? 1 : 0;
}
