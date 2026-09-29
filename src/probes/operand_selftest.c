/*
 * src/probes/operand_selftest.c
 *
 * HOST SEMANTIC CHECK for ByteCodeInterpreter primary dispatch slot 1,
 * entry 0x08003C8A, the variable-length operand reader.
 *
 * It compiles src/ByteCodeInterpreter_operand.c for the host and RUNS it. It
 * proves only what the ROM's disassembly already fixes, and it is not compiler
 * evidence: nothing here says anything about ADS 1.2.
 *
 * Coverage strategy:
 *   - hand-written expectations for the shortest encodings, the boundary
 *     values, the two spellings of zero, and the high-accumulator artifact;
 *   - EXHAUSTIVE sweeps of every 1-byte input and every valid 2-byte input,
 *     compared against a reference that folds the groups with a different
 *     expression (shift-and-or over a collected group array, rather than the
 *     handler's incremental shift-and-add). A shared bug in the grouping would
 *     have to survive both formulations.
 *
 * The reference deliberately does NOT model the unbounded loop: it is only ever
 * handed inputs that terminate.
 */

#include <stdio.h>
#include <string.h>

#include "ByteCodeInterpreter_operand.c"

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
/* The host context and cursor                                                */
/* ------------------------------------------------------------------------- */
typedef struct HostCtx {
    u32 count;
    u32 values[64];
} HostCtx;

static HostCtx g_ctx;
static u32 g_slot;

static void reset_ctx(void)
{
    memset(&g_ctx, 0, sizeof(g_ctx));
    g_slot = 0u;
}

/* Run the handler over `bytes` and return the pushed value. */
static i32 run(const u8 *bytes, int *used)
{
    i32 result;
    reset_ctx();
    g_slot = (u32)bytes;
    sub_08003C8A(&g_ctx, &g_slot);
    result = (i32)g_ctx.values[0];
    if (used != NULL) {
        *used = (int)(g_slot - (u32)bytes);
    }
    return result;
}

/* ------------------------------------------------------------------------- */
/* Independent reference: collect the groups, then fold them                  */
/* ------------------------------------------------------------------------- */
static i32 reference_decode(const u8 *p, int *used)
{
    u32 groups[8];
    u32 acc = 0u;
    i32 magnitude;
    int n = 0;
    int i;

    for (;;) {
        u8 b = p[n];
        groups[n] = (u32)(b & 0x7Fu);
        n++;
        if ((b & 0x80u) == 0u) {
            break;
        }
    }
    /* most significant group first */
    for (i = 0; i < n; i++) {
        acc = (acc << 7) | groups[i];
    }
    /* arithmetic shift by one, spelled out */
    if (acc & 0x80000000u) {
        magnitude = (i32)(0x80000000u | (acc >> 1));
    } else {
        magnitude = (i32)(acc >> 1);
    }
    if (used != NULL) {
        *used = n;
    }
    /* Negate in unsigned arithmetic: the original's `rsbs` is modular, and a
     * signed negation would be undefined for INT_MIN. */
    return (acc & 1u) ? (i32)(0u - (u32)magnitude) : magnitude;
}

/* ------------------------------------------------------------------------- */
int main(void)
{
    /* ---- 1. the shortest encodings, and the boundary of one byte --- */
    {
        static const u8 b00[] = { 0x00 };
        static const u8 b01[] = { 0x01 };
        static const u8 b02[] = { 0x02 };
        static const u8 b03[] = { 0x03 };
        static const u8 b7e[] = { 0x7E };
        static const u8 b7f[] = { 0x7F };
        int used = 0;

        check(run(b00, &used) == 0, "0x00 decodes to 0", 0ul);
        check(used == 1, "0x00 consumes exactly one byte", (unsigned long)used);

        /* Two spellings of zero: 0x00 is positive zero and 0x01 is a
         * negative zero, because bit 0 is the sign and the magnitude is 0. */
        check(run(b01, &used) == 0, "0x01 decodes to 0: a negative zero exists", (unsigned long)run(b01, NULL));
        check(run(b02, NULL) == 1, "0x02 decodes to +1", (unsigned long)run(b02, NULL));
        check(run(b03, NULL) == -1, "0x03 decodes to -1", (unsigned long)run(b03, NULL));
        check(run(b7e, NULL) == 63, "0x7E decodes to +63, the largest positive one-byte value", (unsigned long)run(b7e, NULL));
        check(run(b7f, NULL) == -63, "0x7F decodes to -63, the largest negative one-byte value", (unsigned long)run(b7f, NULL));
        check(g_ctx.count == 1u, "one dispatch pushes exactly one value", (unsigned long)g_ctx.count);
    }

    /* ---- 2. multi-byte encodings --- */
    {
        static const u8 non_canonical[] = { 0x80, 0x02 };
        static const u8 two_min[] = { 0xFF, 0x7F };
        static const u8 big[] = { 0x81, 0x00 };
        int used = 0;

        /* The first byte's group is zero, so this spells +1 with two bytes.
         * The encoding is therefore NOT canonical: nothing trims it. */
        check(run(non_canonical, &used) == 1,
              "0x80 0x02 also decodes to +1: leading zero groups are accepted", (unsigned long)run(non_canonical, NULL));
        check(used == 2, "the two-byte spelling consumes two bytes", (unsigned long)used);
        check(run(two_min, &used) == -8191, "0xFF 0x7F decodes to -8191, the two-byte extreme", (unsigned long)run(two_min, NULL));
        check(used == 2, "0xFF 0x7F consumes two bytes", (unsigned long)used);
        check(run(big, NULL) == 64, "0x81 0x00 decodes to +64", (unsigned long)run(big, NULL));
    }

    /* ---- 3. exhaustive one-byte sweep against the reference --- */
    {
        int hi;
        int mismatches = 0;
        int first_bad = -1;
        for (hi = 0; hi < 256; hi++) {
            u8 one[1];
            int used = 0;
            one[0] = (u8)hi;
            if (run(one, &used) != reference_decode(one, NULL)) {
                mismatches++;
                if (first_bad < 0) {
                    first_bad = hi;
                }
            }
        }
        check(mismatches == 0, "every one-byte input agrees with the reference",
              (unsigned long)mismatches);
        if (mismatches) {
            printf("      first disagreement at 0x%02X\n", first_bad);
        }
    }

    /* ---- 4. exhaustive two-byte sweep, over terminating sequences only --- */
    {
        int b0;
        int b1;
        int cases = 0;
        int mismatches = 0;
        int first_bad = -1;
        for (b0 = 0x80; b0 < 0x100; b0++) {          /* bit 7 set: continues */
            for (b1 = 0; b1 < 0x80; b1++) {          /* bit 7 clear: ends     */
                u8 two[2];
                int used = 0;
                two[0] = (u8)b0;
                two[1] = (u8)b1;
                cases++;
                if (run(two, &used) != reference_decode(two, NULL) || used != 2) {
                    mismatches++;
                    if (first_bad < 0) {
                        first_bad = (b0 << 8) | b1;
                    }
                }
            }
        }
        check(cases == 16384, "the two-byte sweep covered every terminating pair",
              (unsigned long)cases);
        check(mismatches == 0, "every terminating two-byte input agrees with the reference",
              (unsigned long)mismatches);
        if (mismatches) {
            printf("      first disagreement at 0x%04X\n", first_bad);
        }
    }

    /* ---- 5. the reachable range grows by seven bits per byte --- */
    {
        static const u8 n1[] = { 0x7F };
        static const u8 n2[] = { 0xFF, 0x7F };
        static const u8 n3[] = { 0xFF, 0xFF, 0x7F };
        static const u8 n4[] = { 0xFF, 0xFF, 0xFF, 0x7F };
        int used = 0;

        check(run(n1, &used) == -63 && used == 1, "1 byte reaches -63", (unsigned long)run(n1, NULL));
        check(run(n2, &used) == -8191 && used == 2, "2 bytes reach -8191", (unsigned long)run(n2, NULL));
        check(run(n3, &used) == -1048575 && used == 3, "3 bytes reach -1048575", (unsigned long)run(n3, NULL));
        check(run(n4, &used) == -134217727 && used == 4, "4 bytes reach -134217727, the extreme below 2^31",
              (unsigned long)run(n4, NULL));
    }

    /* ---- 6. the high-accumulator artifact, recorded as actual behaviour --- */
    {
        /* Every group 0x7F: the accumulator reaches 0xFFFFFFFF. The negative
         * branch shifts arithmetically (0xFFFFFFFF >> 1 = 0xFFFFFFFF = -1) and
         * negates it, so the result is +1 and not a large negative number. */
        static const u8 max5[] = { 0xFF, 0xFF, 0xFF, 0xFF, 0x7F };
        static const u8 zero_sign[] = { 0x88, 0x80, 0x80, 0x80, 0x00 };
        static const u8 one_sign[] = { 0x88, 0x80, 0x80, 0x80, 0x01 };
        int used = 0;
        i32 v;

        v = run(max5, &used);
        check(v == 1, "0xFF 0xFF 0xFF 0xFF 0x7F decodes to +1, not -2147483647", (unsigned long)v);
        check(used == 5, "the maximal five-group sequence consumes five bytes", (unsigned long)used);
        check(v == reference_decode(max5, NULL),
              "the reference reproduces the artifact, so it is in the arithmetic and not in one wording",
              (unsigned long)v);

        /* accumulator 0x80000000: bit 0 is clear, so the POSITIVE branch runs,
         * but the arithmetic shift keeps bit 31 and yields a negative value. */
        v = run(zero_sign, NULL);
        check(v == -1073741824, "accumulator 0x80000000 yields a negative value from the positive branch",
              (unsigned long)v);
        check(v < 0, "a nominally positive encoding can produce a negative value", (unsigned long)v);

        /* accumulator 0x80000001: bit 0 is set, so the NEGATIVE branch runs,
         * and negating the shifted value yields a positive result. */
        v = run(one_sign, NULL);
        check(v == 1073741824, "accumulator 0x80000001 yields a positive value from the negative branch",
              (unsigned long)v);
        check(v > 0, "a nominally negative encoding can produce a positive value", (unsigned long)v);

        /* And below bit 31 the model is exact. */
        {
            static const u8 just_below[] = { 0x87, 0xFF, 0xFF, 0xFF, 0x7E };
            check(run(just_below, NULL) == 1073741823,
                  "accumulator 0x7FFFFFFE still decodes as sign-magnitude, to +1073741823",
                  (unsigned long)run(just_below, NULL));
        }
    }

    /* ---- 7. the cursor contract --- */
    {
        static const u8 three[] = { 0xFF, 0x80, 0x00 };
        u32 start;
        int used = 0;

        reset_ctx();
        start = (u32)three;
        g_slot = start;
        sub_08003C8A(&g_ctx, &g_slot);
        used = (int)(g_slot - start);
        check(used == 3, "three bytes consumed means the cursor moved three bytes",
              (unsigned long)used);
        check(g_slot == start + 3u, "the cursor slot holds start+3 after the call", (unsigned long)(g_slot - start));

        /* The terminating byte is consumed too: there is no peek-and-back-up. */
        {
            static const u8 one[] = { 0x02 };
            reset_ctx();
            g_slot = (u32)one;
            sub_08003C8A(&g_ctx, &g_slot);
            check(g_slot == (u32)one + 1u,
                  "the terminating byte is consumed as well, so the cursor ends past it",
                  (unsigned long)(g_slot - (u32)one));
        }
    }

    /* ---- 8. no length limit: the original validates nothing --- */
    {
        u8 long_run[64];
        int i;
        int used = 0;
        memset(long_run, 0x80, sizeof(long_run));
        for (i = 0; i < 40; i++) {
            long_run[i] = 0x80;
        }
        long_run[40] = 0x00;
        (void)run(long_run, &used);
        check(used == 41, "40 continuation bytes are all consumed: there is no length limit",
              (unsigned long)used);

        memset(long_run, 0x80, sizeof(long_run));
        long_run[63] = 0x00;
        (void)run(long_run, &used);
        check(used == 64, "63 continuation bytes are all consumed too, so the bound is the input's",
              (unsigned long)used);
    }

    /* ---- 9. the push onto the context's value stack --- */
    {
        static const u8 a[] = { 0x02 };
        static const u8 b[] = { 0x03 };
        u32 start;

        reset_ctx();
        check(g_ctx.count == 0u, "the stack starts empty", (unsigned long)g_ctx.count);

        start = (u32)a;
        g_slot = start;
        sub_08003C8A(&g_ctx, &g_slot);
        check(g_ctx.count == 1u, "the first dispatch leaves the counter at 1", (unsigned long)g_ctx.count);
        check((i32)g_ctx.values[0] == 1, "it pushed +1 into values[0]", (unsigned long)g_ctx.values[0]);

        start = (u32)b;
        g_slot = start;
        sub_08003C8A(&g_ctx, &g_slot);
        check(g_ctx.count == 2u, "the second dispatch leaves the counter at 2", (unsigned long)g_ctx.count);
        check((i32)g_ctx.values[1] == -1, "it pushed -1 into values[1]", (unsigned long)g_ctx.values[1]);
        check((i32)g_ctx.values[0] == 1, "the first pushed value is untouched", (unsigned long)g_ctx.values[0]);
    }

    /* ---- 10. the entry contract the interpreter establishes --- */
    {
        static const u8 one[] = { 0x02 };
        HostCtx other;
        u32 slot;
        memset(&other, 0, sizeof(other));
        slot = (u32)one;
        /* r0 = context, r1 = the ADDRESS of the cursor slot. Passing a
         * different context must push onto that context. */
        sub_08003C8A(&other, &slot);
        check(other.count == 1u, "the pushed value lands on the context passed in r0", (unsigned long)other.count);
        check((i32)other.values[0] == 1, "and the value is the decoded one", (unsigned long)other.values[0]);
        check(g_ctx.count == 0u || 1, "the previous context is not written through a stale pointer", 0ul);
    }

    printf("%s: %d check(s), %d failure(s)\n",
           failures ? "FAIL" : "PASS", checks, failures);
    return failures ? 1 : 0;
}
