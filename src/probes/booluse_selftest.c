/*
 * src/probes/booluse_selftest.c
 *
 * HOST SEMANTIC CHECK for the two routines that materialise the normalised
 * boolean into the VM value stack: sub_080007B6 (flag) and sub_080007CC (not
 * flag).
 *
 * It compiles the real reader as well, because that is the routine these two
 * call, so the whole in-place transform runs rather than being stubbed.
 *
 * Built 32-bit: the addressing is 32-bit and the empty-stack case depends on the
 * wrap.
 */

#include <stdio.h>
#include <string.h>

#define BOOLUSE_HOST_TEST 1

/* The callee, reconstructed at src/ByteCodeInterpreter_flagread.c. */
#include "ByteCodeInterpreter_flagread.c"
#include "ByteCodeInterpreter_booluse.c"

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
/* The host context: a counter, then the value slots, then the bit array the
 * reader consults, reached through the object pointer.                       */
/* ------------------------------------------------------------------------- */
#define VALUE_SLOTS 16
#define OBJECT_OFFSET 0x14

typedef struct HostCtx {
    u32 count;
    u32 values[VALUE_SLOTS];
} HostCtx;

static u8 g_object[0x200];
static HostCtx g_ctx;
static u32 g_slot;

u32 booluse_host_global_base;

/* Address of the byte the reader tests for a given value. The materialisation
 * routines pass BOOLUSE_GLOBAL_BASE + 0x14 as the reader's base, so the byte
 * lives at that base plus the index arithmetic, NOT at the global base. */
static u8 *flag_byte_for(u32 value)
{
    u32 index = (value & 0x80000000u) ? ((value >> 3) | 0xE0000000u) : (value >> 3);
    return (u8 *)((u32)g_object + OBJECT_OFFSET + index + 0x50u) + 5u;
}

static void reset_all(void)
{
    memset(&g_ctx, 0, sizeof(g_ctx));
    memset(g_object, 0, sizeof(g_object));
    g_slot = 0xDEADBEEFu;
    booluse_host_global_base = (u32)g_object;
}

int main(void)
{
    /* ---- 1. it replaces the TOP slot in place, and does not pop --------- */
    reset_all();
    g_ctx.count = 3u;
    g_ctx.values[0] = 0u;
    g_ctx.values[1] = 0u;
    g_ctx.values[2] = 5u;             /* the top */
    *flag_byte_for(5u) = 0x20u;       /* value 5 tests BIT 5, so the mask is 0x20 */

    sub_080007B6(&g_ctx, &g_slot);
    check(g_ctx.count == 3u, "the counter is unchanged: this is not a pop", (unsigned long)g_ctx.count);
    check(g_ctx.values[2] == 1u, "the TOP slot now holds the flag", (unsigned long)g_ctx.values[2]);
    check(g_ctx.values[0] == 0u && g_ctx.values[1] == 0u, "the other slots are untouched", 0ul);
    check(g_slot == 0xDEADBEEFu, "the incoming r1 is never read", (unsigned long)g_slot);

    /* ---- 2. a clear bit gives 0, and the second routine inverts --------- */
    reset_all();
    g_ctx.count = 2u;
    g_ctx.values[1] = 5u;
    *flag_byte_for(5u) = 0x00u;       /* bit 5 clear */
    sub_080007B6(&g_ctx, &g_slot);
    check(g_ctx.values[1] == 0u, "a clear bit stores 0", (unsigned long)g_ctx.values[1]);
    check(g_ctx.count == 2u, "and the counter is still unchanged", (unsigned long)g_ctx.count);

    reset_all();
    g_ctx.count = 2u;
    g_ctx.values[1] = 5u;
    *flag_byte_for(5u) = 0x00u;
    sub_080007CC(&g_ctx, &g_slot);
    check(g_ctx.values[1] == 1u, "the second routine stores 1 - flag, so a clear bit gives 1",
          (unsigned long)g_ctx.values[1]);
    check(g_ctx.count == 2u, "and it too leaves the counter alone", (unsigned long)g_ctx.count);

    reset_all();
    g_ctx.count = 2u;
    g_ctx.values[1] = 5u;
    *flag_byte_for(5u) = 0x20u;       /* bit 5 set */
    sub_080007CC(&g_ctx, &g_slot);
    check(g_ctx.values[1] == 0u, "and a set bit gives 0 from the inverted routine",
          (unsigned long)g_ctx.values[1]);

    /* ---- 3. the two are exact inverses over a sweep --------------------- */
    {
        u32 bit;
        int bad = 0;
        for (bit = 0u; bit < 8u; bit++) {
            u32 plain;
            u32 inverted;
            /* The value selects which bit is tested, so it must vary with the
             * bit being set, not stay at zero. */
            reset_all();
            g_ctx.count = 2u;
            g_ctx.values[1] = bit;
            *flag_byte_for(bit) = (u8)(1u << bit);
            sub_080007B6(&g_ctx, &g_slot);
            plain = g_ctx.values[1];
            reset_all();
            g_ctx.count = 2u;
            g_ctx.values[1] = bit;
            *flag_byte_for(bit) = (u8)(1u << bit);
            sub_080007CC(&g_ctx, &g_slot);
            inverted = g_ctx.values[1];
            if (plain != 1u || inverted != 0u) {
                bad++;
            }
        }
        check(bad == 0, "for each of the eight bits the first returns 1 and the inverted one 0",
              (unsigned long)bad);
    }

    /* ---- 4. both RETURN what they stored ------------------------------- */
    reset_all();
    g_ctx.count = 1u;
    g_ctx.values[0] = 0u;
    *flag_byte_for(0u) = 0x01u;
    check(sub_080007B6(&g_ctx, &g_slot) == 1u, "the first returns the stored value",
          (unsigned long)g_ctx.values[0]);
    reset_all();
    g_ctx.count = 1u;
    g_ctx.values[0] = 0u;
    *flag_byte_for(0u) = 0x01u;
    check(sub_080007CC(&g_ctx, &g_slot) == 0u, "the inverted one returns what it stored",
          (unsigned long)g_ctx.values[0]);

    /* ---- 5. the EMPTY STACK case: the counter word itself is replaced --- */
    /* count 0 -> r4 = context + 0, so the word read and written is the counter.
     * Nothing is popped and there is no guard. */
    reset_all();
    g_ctx.count = 0u;
    *flag_byte_for(0u) = 0x01u;       /* test(0) would return 1 */
    sub_080007B6(&g_ctx, &g_slot);
    check(g_ctx.count == 1u,
          "with an empty stack the COUNTER WORD is read as the value and then replaced by the flag",
          (unsigned long)g_ctx.count);
    check(g_ctx.values[0] == 0u, "and no value slot is touched", (unsigned long)g_ctx.values[0]);

    reset_all();
    g_ctx.count = 0u;
    *flag_byte_for(0u) = 0x01u;       /* test(0) returns 1, so 1 - 1 = 0 */
    sub_080007CC(&g_ctx, &g_slot);
    check(g_ctx.count == 0u, "the inverted routine replaces the counter with 1 - flag",
          (unsigned long)g_ctx.count);

    /* ---- 6. the value read is the raw slot, whatever it holds ---------- */
    /* The reader normalises, but the routine stores only 0 or 1, so any stored
     * value is one of those. Checked across a sweep. */
    {
        u32 v;
        int bad = 0;
        for (v = 0u; v < 64u; v++) {
            reset_all();
            g_ctx.count = 1u;
            g_ctx.values[0] = v;
            sub_080007B6(&g_ctx, &g_slot);
            if (g_ctx.values[0] > 1u) {
                bad++;
            }
        }
        check(bad == 0, "no input produces anything but 0 or 1 in the slot", (unsigned long)bad);
    }

    /* ---- 7. the consequence: the boolean becomes a BIT INDEX ---------- */
    /* The already-lifted consumer sub_080007E6 pops the slot and passes it to
     * sub_08004380, which sets bit (value & 7). A 0 or 1 therefore selects bit 0
     * or bit 1 of the array's first byte. Asserted here as arithmetic on the
     * materialised value, which is what the consumer will do with it. */
    {
        u32 bit;
        int bad = 0;
        for (bit = 0u; bit < 8u; bit++) {
            u32 stored;
            reset_all();
            g_ctx.count = 1u;
            g_ctx.values[0] = bit;
            *flag_byte_for(bit) = (u8)(1u << bit);
            sub_080007B6(&g_ctx, &g_slot);
            stored = g_ctx.values[0];
            /* the consumer's effect on the materialised boolean */
            if ((stored & 7u) != stored || (stored >> 3) != 0u) {
                bad++;
            }
        }
        check(bad == 0,
              "a 0/1 slot indexes byte 0 and selects bit 0 or bit 1 when the consumer uses it",
              (unsigned long)bad);
    }

    printf("%s: %d check(s), %d failure(s)\n",
           failures ? "FAIL" : "PASS", checks, failures);
    return failures ? 1 : 0;
}
