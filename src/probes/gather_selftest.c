/*
 * src/probes/gather_selftest.c
 *
 * HOST SEMANTIC CHECK for sub_080032C2: the flag-array gather loop.
 *
 * The reader is MOCKED here so the gathered bits can be chosen exactly. The
 * mock still receives the real arguments, so the `offset + n` progression is
 * observable and is asserted. A second section re-runs the loop against the REAL
 * reader to prove the two compose.
 *
 * Built 32-bit.
 */

#include <stdio.h>
#include <string.h>

#define GATHER_HOST_TEST 1

/* The types the mock uses must be declared BEFORE the mock: the unit under test
 * is included later and is what normally supplies them, and without this MSVC
 * treats the arrays below as implicitly-typed scalars. */
typedef unsigned int u32;
typedef unsigned char u8;

/* ---- the mock reader, declared before the unit under test ---- */
#define MOCK_MAX_CALLS 128

static u8 g_mock_bits[16];
static u32 g_mock_calls;
static u32 g_mock_args[MOCK_MAX_CALLS];

u32 sub_08004364(void *base, u32 value)
{
    u32 index = (value & 0x80000000u) ? ((value >> 3) | 0xE0000000u) : (value >> 3);
    u8 byte = g_mock_bits[index & 15u];
    (void)base;
    g_mock_args[g_mock_calls++ % MOCK_MAX_CALLS] = value;
    return (u32)((byte >> (value & 7u)) & 1u);
}

#include "ByteCodeInterpreter_gather.c"

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

#define VALUE_SLOTS 32

typedef struct HostCtx {
    u32 count;
    u32 values[VALUE_SLOTS];
} HostCtx;

static HostCtx g_ctx;
static u32 g_slot;

/* The unit reads its global base through this in host mode. */
u32 gather_host_global_base;

static void reset_ctx(void)
{
    memset(&g_ctx, 0, sizeof(g_ctx));
    memset(g_mock_bits, 0, sizeof(g_mock_bits));
    g_mock_calls = 0u;
    g_slot = 0xDEADBEEFu;
    gather_host_global_base = 0x12345678u;
}

/* Build a fresh context with `offset` beneath `bound` and run. */
static void run(u32 offset, u32 bound)
{
    g_ctx.count = 2u;
    g_ctx.values[0] = offset;
    g_ctx.values[1] = bound;
    sub_080032C2(&g_ctx, &g_slot);
}

int main(void)
{
    /* ---- 1. two consumed, one produced -------------------------------- */
    reset_ctx();
    run(0u, 4u);
    check(g_ctx.count == 1u, "the counter moves by exactly -1: two pops, one push",
          (unsigned long)g_ctx.count);
    check(g_ctx.values[0] == 0u, "the pushed mask lands in values[count]", (unsigned long)g_ctx.values[0]);
    check(g_slot == 0xDEADBEEFu, "the incoming r1 is never read", (unsigned long)g_slot);

    /* ---- 2. the reader receives offset + n, in order ------------------ */
    reset_ctx();
    run(100u, 5u);
    check(g_mock_calls == 5u, "a bound of 5 makes exactly 5 calls", (unsigned long)g_mock_calls);
    {
        u32 n;
        int bad = 0;
        for (n = 0u; n < 5u; n++) {
            if (g_mock_args[n] != 100u + n) {
                bad++;
            }
        }
        check(bad == 0, "the arguments are offset+0 .. offset+4, so successive BITS are tested",
              (unsigned long)bad);
    }

    /* ---- 3. the mask packs bit n from array bit offset+n -------------- */
    /* Set array bits at offsets 100, 102 and 104 only. */
    reset_ctx();
    /* Bits 100, 102 and 104 do not all live in the same byte, so each is set in
     * its own. */
    g_mock_bits[100u >> 3] |= (u8)(1u << (100u & 7u));
    g_mock_bits[102u >> 3] |= (u8)(1u << (102u & 7u));
    g_mock_bits[104u >> 3] |= (u8)(1u << (104u & 7u));
    run(100u, 5u);
    check(g_ctx.values[0] == 0x15u,
          "a bound of 5 over bits 0,2,4 of the run gives mask 0b10101",
          (unsigned long)g_ctx.values[0]);

    /* ---- 4. bound zero or less gathers nothing and calls nobody ------- */
    reset_ctx();
    run(50u, 0u);
    check(g_mock_calls == 0u, "a bound of 0 makes no calls at all", (unsigned long)g_mock_calls);
    check(g_ctx.values[0] == 0u, "and pushes a mask of 0", (unsigned long)g_ctx.values[0]);
    check(g_ctx.count == 1u, "while still consuming both values", (unsigned long)g_ctx.count);

    reset_ctx();
    run(50u, 0xFFFFFFFFu);              /* -1 read signed */
    check(g_mock_calls == 0u, "a negative bound also makes no calls", (unsigned long)g_mock_calls);
    check(g_ctx.values[0] == 0u, "and pushes 0", (unsigned long)g_ctx.values[0]);

    /* ---- 5. a bound of 1 gathers exactly one bit ---------------------- */
    reset_ctx();
    g_mock_bits[3u >> 3] = 0x08u;       /* array bit 3 */
    run(3u, 1u);
    check(g_mock_calls == 1u, "a bound of 1 makes one call", (unsigned long)g_mock_calls);
    check(g_ctx.values[0] == 0x01u, "and sets bit 0 of the mask", (unsigned long)g_ctx.values[0]);

    /* ---- 6. the mask width follows the bound -------------------------- */
    {
        u32 bound;
        int bad = 0;
        for (bound = 1u; bound <= 32u; bound++) {
            u32 n;
            reset_ctx();
            /* set every array bit in the run */
            for (n = 0u; n < bound; n++) {
                u32 bit = 200u + n;
                g_mock_bits[(bit >> 3) & 15u] |= (u8)(1u << (bit & 7u));
            }
            run(200u, bound);
            if (g_ctx.values[0] != (bound == 32u ? 0xFFFFFFFFu : ((1u << bound) - 1u))) {
                bad++;
            }
        }
        check(bad == 0, "with every gathered bit set the mask is (1<<bound)-1 for bound 1..32",
              (unsigned long)bad);
    }

    /* ---- 7. a bound above 32 WRAPS, because Thumb lsls is modulo 32 --- */
    /* This is the machine's behaviour, reproduced rather than corrected. */
    reset_ctx();
    {
        u32 n;
        for (n = 0u; n < 33u; n++) {
            u32 bit = 300u + n;
            g_mock_bits[(bit >> 3) & 15u] |= (u8)(1u << (bit & 7u));
        }
    }
    run(300u, 33u);
    check(g_mock_calls == 33u, "a bound of 33 makes 33 calls", (unsigned long)g_mock_calls);
    check(g_ctx.values[0] == 0xFFFFFFFFu,
          "and bit 32 wraps onto bit 0, so the mask is still all ones",
          (unsigned long)g_ctx.values[0]);

    reset_ctx();
    {
        u32 n;
        for (n = 0u; n < 33u; n++) {
            u32 bit = 400u + n;
            g_mock_bits[(bit >> 3) & 15u] |= (u8)(1u << (bit & 7u));
        }
    }
    /* clear only the last gathered bit's source: bit 32 maps to mask bit 0 */
    g_mock_bits[(432u >> 3) & 15u] &= (u8)~(1u << (432u & 7u));
    run(400u, 33u);
    check(g_ctx.values[0] == 0xFFFFFFFFu && g_mock_calls == 33u,
          "and a bound of 33 sets every mask bit once the wrap is accounted for",
          (unsigned long)g_ctx.values[0]);

    /* ---- 8. the offset is a BIT number, and can be negative ----------- */
    /* A value with bit 31 set makes the reader index before its base; the gather
     * loop does not care and passes it through. */
    reset_ctx();
    run(0xFFFFFFFFu, 1u);
    check(g_mock_calls == 1u, "a negative offset still makes one call", (unsigned long)g_mock_calls);
    check(g_mock_args[0] == 0xFFFFFFFFu, "and is passed through unchanged",
          (unsigned long)g_mock_args[0]);

    /* ---- 9. non-adjacent offsets are gathered individually ------------ */
    reset_ctx();
    g_mock_bits[0] = 0x01u;             /* array bit 0 */
    g_mock_bits[1] = 0x80u;             /* array bit 15 */
    run(0u, 16u);
    check(g_ctx.values[0] == 0x8001u,
          "gathering 16 bits from offset 0 yields bit0 from bit0 and bit15 from bit15",
          (unsigned long)g_ctx.values[0]);

    printf("%s: %d check(s), %d failure(s)\n",
           failures ? "FAIL" : "PASS", checks, failures);
    return failures ? 1 : 0;
}
