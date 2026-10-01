/*
 * src/probes/iwramq1814_selftest.c
 *
 * HOST SEMANTIC CHECK for src/IwramQ1814.c.
 *
 * Every expected value is computed HERE from the equations decoded from the ARM
 * instructions, and never by calling the routine under test. Two independent
 * references are used, and they answer different questions:
 *
 *   ref_closed    the MATHEMATICAL model, in exact 64-bit arithmetic:
 *                     address_i = C + floor((A + i*B) / 2^14)
 *                     out[i]    = out_init[i] + D * (s8)mem[address_i]
 *                 computed with `long long`, so it shares no rounding, no
 *                 wraparound and no register with the reconstruction. It is only
 *                 valid where the machine's 32-bit address arithmetic does not
 *                 wrap, and the cases that use it are chosen that way.
 *
 *   ref_register  the ENCODING model: the same 64-bit phase accumulator built
 *                 from the two instruction pairs, written with a single u64 where
 *                 the routine uses a high/low register pair. It is valid for
 *                 every input, including the ones that wrap the 32-bit address.
 *
 * The behaviours this exists to pin, because each is the kind of thing a
 * "tidier" reconstruction gets wrong:
 *
 *   * a count of ZERO writes EIGHT destination words - there is no pre-test;
 *   * a count of 12 writes TWELVE, because `tst r2,#4` skips the first four and
 *     the `subs #8` subtracts eight anyway;
 *   * the destination is READ-MODIFY-WRITTEN, not stored;
 *   * the byte read is SIGNED (`ldrsb`);
 *   * the position is TRUNCATED toward negative infinity, so a negative phase
 *     reads one byte lower than truncation toward zero would;
 *   * the increment's high word is `B asr 14` (ARITHMETIC), and the carry from
 *     the low word is what moves the address in the `ldrsbhs` specialization.
 *
 * Built 32-bit: the routine carries a byte ADDRESS in a u32 register and the
 * wraparound is part of what is being modelled.
 */

#include <stdio.h>
#include <string.h>

typedef unsigned int u32;
typedef unsigned char u8;
typedef int s32;
typedef unsigned long long u64;

#include "IwramQ1814.c"

static int checks;
static int failures;

static void check(int condition, const char *what, unsigned long detail)
{
    checks++;
    if (!condition) {
        failures++;
        if (failures <= 20) {
            printf("FAIL: %s (detail %lu)\n", what, detail);
        }
    }
}

/* ------------------------------------------------------------------------- */
/* the arenas                                                                 */
/* ------------------------------------------------------------------------- */
#define ARENA 0x8000
#define PARAMS_OFF 0x0000
#define DST_OFF 0x0400
#define SAMPLE_OFF 0x1000
#define WINDOW 0x2000              /* the sample window, 8192 bytes */
#define DST_WORDS 256
#define SENTINEL 0xA5u

static u8 g_arena[ARENA];

static u32 arena_addr(void)
{
    return (u32)(unsigned long)g_arena;
}

static void put_u32(u32 address, u32 value)
{
    u8 *p = g_arena + (address - arena_addr());
    p[0] = (u8)(value & 0xFFu);
    p[1] = (u8)((value >> 8) & 0xFFu);
    p[2] = (u8)((value >> 16) & 0xFFu);
    p[3] = (u8)((value >> 24) & 0xFFu);
}

static u32 get_u32(u32 address)
{
    const u8 *p = g_arena + (address - arena_addr());
    return (u32)p[0] | ((u32)p[1] << 8) | ((u32)p[2] << 16) | ((u32)p[3] << 24);
}

static void fill_samples(u32 seed)
{
    u32 i;
    u32 state = seed | 1u;
    for (i = 0u; i < WINDOW; i++) {
        state ^= state << 13;
        state ^= state >> 17;
        state ^= state << 5;
        g_arena[SAMPLE_OFF + i] = (u8)(state & 0xFFu);
    }
}

static void reset_dst(u32 seed)
{
    u32 i;
    u32 state = seed | 1u;
    for (i = 0u; i < DST_WORDS; i++) {
        state = state * 1103515245u + 12345u;
        put_u32(DST_OFF + arena_addr() + 4u * i, state);
    }
}

static u32 next_random(u32 *state)
{
    u32 x = *state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    *state = x;
    return x;
}

/* ------------------------------------------------------------------------- */
/* the element count, straight from the decoded group structure               */
/* ------------------------------------------------------------------------- */
static u32 ref_elements(u32 count)
{
    u32 n = count;
    u32 total = 0u;

    if ((n & 1u) != 0u) {
        total += 1u;
        n -= 1u;
        if (n == 0u) {
            return total;
        }
    }
    if ((n & 2u) != 0u) {
        total += 2u;
        n -= 2u;
        if (n == 0u) {
            return total;
        }
    }
    total += ((n & 4u) != 0u) ? 4u : 8u;
    for (;;) {
        const u32 before = n;
        n = before - 8u;
        if (!(before >= 8u && n != 0u)) {
            break;
        }
        total += 8u;
    }
    return total;
}

/* ------------------------------------------------------------------------- */
/* reference 1: the closed mathematical form, exact 64-bit arithmetic          */
/* ------------------------------------------------------------------------- */
static u32 ref_closed_address(s32 a, s32 b, u32 c, u32 index)
{
    const long long numerator = (long long)a + (long long)(int)index * (long long)b;
    const long long quotient = numerator >> 14;      /* floor for two's complement */
    return (u32)((s32)quotient) + c;
}

/* Returns the number of elements written, and fills `out` with the CLOSED-FORM
 * result: each destination word is its initial value plus D times the signed
 * byte at the exact address. */
static u32 ref_closed_run(u32 a, u32 b, u32 c, u32 d, u32 count, u32 *out)
{
    const u32 elements = ref_elements(count);
    const s32 sa = (s32)a;
    const s32 sb = (s32)b;
    u32 i;

    for (i = 0u; i < elements; i++) {
        const u32 address = ref_closed_address(sa, sb, c, i);
        const u32 byte = (u32)(s32)*(const signed char *)(unsigned long)(address);
        out[i] = out[i] + d * byte;
    }
    return elements;
}

/* ------------------------------------------------------------------------- */
/* reference 2: the 64-bit phase accumulator as one u64                        */
/* ------------------------------------------------------------------------- */
static u32 ref_register_run(u32 a, u32 b, u32 c, u32 d, u32 count, u32 *out)
{
    const u32 elements = ref_elements(count);
    u64 phase = ((u64)(c + (u32)((s32)a >> 14)) << 32) | (u64)(a << 18);
    const u64 step = ((u64)(u32)((s32)b >> 14) << 32) | (u64)(b << 18);
    u32 i;

    for (i = 0u; i < elements; i++) {
        const u32 address = (u32)(phase >> 32);
        const u32 byte = (u32)(s32)*(const signed char *)(unsigned long)(address);
        out[i] = out[i] + d * byte;
        phase += step;
    }
    return elements;
}

/* ------------------------------------------------------------------------- */
/* driver                                                                     */
/* ------------------------------------------------------------------------- */
static u32 g_initial[DST_WORDS];

static void setup(u32 a, u32 b, u32 c, u32 d, u32 seed)
{
    u32 i;
    put_u32(PARAMS_OFF + arena_addr() + 0u, a);
    put_u32(PARAMS_OFF + arena_addr() + 4u, b);
    put_u32(PARAMS_OFF + arena_addr() + 8u, c);
    put_u32(PARAMS_OFF + arena_addr() + 12u, d);
    reset_dst(seed);
    for (i = 0u; i < DST_WORDS; i++) {
        g_initial[i] = get_u32(DST_OFF + arena_addr() + 4u * i);
    }
}

static int compare(u32 elements, const u32 *expected, const char *what,
                   unsigned long detail)
{
    u32 i;
    for (i = 0u; i < elements; i++) {
        if (get_u32(DST_OFF + arena_addr() + 4u * i) != expected[i]) {
            check(0, what, detail);
            return 0;
        }
    }
    /* and nothing past the written elements moved */
    for (i = elements; i < DST_WORDS; i++) {
        if (get_u32(DST_OFF + arena_addr() + 4u * i) != g_initial[i]) {
            check(0, what, detail);
            return 0;
        }
    }
    check(1, what, detail);
    return 1;
}

int main(void)
{
    static u32 expected[DST_WORDS];
    u32 state = 0x2468ACE0u;
    u32 i;

    memset(g_arena, (int)SENTINEL, sizeof g_arena);
    fill_samples(0x1234u);

    /* ===================================================================== */
    /* 1. the closed form and the encoding model agree on non-wrapping inputs  */
    /* ===================================================================== */
    for (i = 0u; i < 4000u; i++) {
        const u32 a = (next_random(&state) & 0x003FFFFFu) | 0x00008000u;
        const u32 b = (next_random(&state) & 0x0003FFFFu) | 0x00004000u;
        const u32 c = (u32)(SAMPLE_OFF + arena_addr() + (WINDOW / 2u));
        const u32 d = next_random(&state);
        const u32 count = next_random(&state) % 33u;
        const u32 elements = ref_elements(count);
        u32 k;

        setup(a, b, c, d, state);
        for (k = 0u; k < DST_WORDS; k++) {
            expected[k] = g_initial[k];
        }
        ref_closed_run(a, b, c, d, count, expected);
        sub_087B820C(PARAMS_OFF + arena_addr(), DST_OFF + arena_addr(), count);
        compare(elements, expected, "closed form agrees on a positive phase",
                ((unsigned long)a << 8) ^ b);
    }

    /* Negative A: the truncation direction is observable here. */
    for (i = 0u; i < 4000u; i++) {
        const u32 a = (next_random(&state) & 0x003FFFFFu) | 0xFFF08000u;
        const u32 b = (next_random(&state) & 0x0003FFFFu) | 0x00004000u;
        const u32 c = (u32)(SAMPLE_OFF + arena_addr() + (WINDOW / 2u) + 0x400u);
        const u32 d = next_random(&state);
        const u32 count = next_random(&state) % 33u;
        const u32 elements = ref_elements(count);
        u32 k;

        setup(a, b, c, d, state);
        for (k = 0u; k < DST_WORDS; k++) {
            expected[k] = g_initial[k];
        }
        ref_closed_run(a, b, c, d, count, expected);
        sub_087B820C(PARAMS_OFF + arena_addr(), DST_OFF + arena_addr(), count);
        compare(elements, expected, "closed form agrees on a negative phase",
                ((unsigned long)a << 8) ^ b);
    }

    /* ===================================================================== */
    /* 2. the encoding model agrees for EVERY input, including wrapping        */
    /* ===================================================================== */
    for (i = 0u; i < 12000u; i++) {
        const u32 a = next_random(&state);
        /* bound |B| so the walk stays inside the sample window, and let it be
         * negative so the address can move backward as well as forward */
        const u32 b = (next_random(&state) & 0x3FFFFu) - 0x20000u;
        /* C compensates A's integer part so the FIRST address is the window
         * centre whatever A is - a wild A is still a valid case, and this keeps
         * it inside real storage rather than faulting the host */
        const u32 c = (u32)(SAMPLE_OFF + arena_addr() + (WINDOW / 2u))
                      - (u32)((s32)a >> 14);
        const u32 d = next_random(&state);
        const u32 count = next_random(&state) % 41u;
        const u32 elements = ref_elements(count);
        u32 k;

        setup(a, b, c, d, state);
        for (k = 0u; k < DST_WORDS; k++) {
            expected[k] = g_initial[k];
        }
        ref_register_run(a, b, c, d, count, expected);
        sub_087B820C(PARAMS_OFF + arena_addr(), DST_OFF + arena_addr(), count);
        compare(elements, expected, "encoding model agrees for wrapped phases",
                ((unsigned long)a << 8) ^ b);
    }

    /* ===================================================================== */
    /* 3. the increment's high word selects a specialization                   */
    /* ===================================================================== */
    /* B = +-16384 is the first value whose `asr #14` is non-zero, so the two
     * bodies are exercised either side of it. */
    {
        static const u32 steps[8] = { 0u, 1u, 0x3FFFu, 0x4000u, 0x4001u,
                                      0xFFFFC000u, 0xFFFFBFFFu, 0x8000u };
        u32 s;
        for (s = 0u; s < 8u; s++) {
            for (i = 0u; i <= 40u; i++) {
                const u32 a = 0x00012345u;
                const u32 b = steps[s];
                const u32 c = (u32)(SAMPLE_OFF + arena_addr() + (WINDOW / 2u));
                const u32 d = 0x00010001u;
                const u32 elements = ref_elements(i);
                u32 k;

                setup(a, b, c, d, 0x99u + i);
                for (k = 0u; k < DST_WORDS; k++) {
                    expected[k] = g_initial[k];
                }
                ref_register_run(a, b, c, d, i, expected);
                sub_087B820C(PARAMS_OFF + arena_addr(), DST_OFF + arena_addr(), i);
                compare(elements, expected, "both specializations of the step",
                        ((unsigned long)s << 16) | i);
            }
        }
        /* The selection itself: `cmp r4, #0` with r4 = B asr 14. */
        check(((s32)0x4000u >> 14) != 0,
              "B = +0x4000 makes the increment's high word NON-zero (general body)",
              0u);
        check(((s32)0x3FFFu >> 14) == 0,
              "B = +0x3FFF makes it ZERO (the ldrsbhs specialization)", 0u);
        check(((s32)0xFFFFC000u >> 14) == -1,
              "B = -0x4000 makes it -1, so the address moves BACKWARD", 0u);
    }

    /* ===================================================================== */
    /* 4. the count edge cases, stated and measured                            */
    /* ===================================================================== */
    {
        u32 count;
        for (count = 0u; count <= 40u; count++) {
            const u32 a = 0u;
            const u32 b = 0x4000u;
            const u32 c = (u32)(SAMPLE_OFF + arena_addr() + (WINDOW / 2u));
            const u32 elements = ref_elements(count);
            u32 k;
            setup(a, b, c, 0x00000003u, count);
            for (k = 0u; k < DST_WORDS; k++) {
                expected[k] = g_initial[k];
            }
            ref_register_run(a, b, c, 0x00000003u, count, expected);
            sub_087B820C(PARAMS_OFF + arena_addr(), DST_OFF + arena_addr(), count);
            compare(elements, expected, "the count dispatch writes the right count",
                    count);
        }
        check(ref_elements(0u) == 8u,
              "count 0 writes EIGHT words: there is no pre-test and the first "
              "`subs r2,r2,#8` borrows", (unsigned long)ref_elements(0u));
        check(ref_elements(1u) == 1u && ref_elements(2u) == 2u
                  && ref_elements(3u) == 3u && ref_elements(4u) == 4u
                  && ref_elements(5u) == 5u && ref_elements(6u) == 6u
                  && ref_elements(7u) == 7u,
              "counts 1..7 write exactly their own value", 0u);
        check(ref_elements(12u) == 12u && ref_elements(20u) == 20u,
              "count 12 and 20 write twelve and twenty, not eight and sixteen",
              0u);
        check(12u % 8u == 4u,
              "the asymmetry is reachable: 12 has bit 2 set, so the first "
              "4-group is SKIPPED while 8 is still subtracted", 0u);
    }

    /* ===================================================================== */
    /* 5. the read-modify-write and the signed byte                            */
    /* ===================================================================== */
    {
        /* A destination that is already 0xFFFFFFFF plus 1 must be 0, not 1. */
        u32 k;
        const u32 c = (u32)(SAMPLE_OFF + arena_addr() + (WINDOW / 2u));
        setup(0u, 0u, c, 1u, 0x11u);
        for (k = 0u; k < DST_WORDS; k++) {
            put_u32(DST_OFF + arena_addr() + 4u * k, 0xFFFFFFFFu);
        }
        *((u8 *)(g_arena + (c - arena_addr()))) = 1u;
        sub_087B820C(PARAMS_OFF + arena_addr(), DST_OFF + arena_addr(), 1u);
        check(get_u32(DST_OFF + arena_addr()) == 0u,
              "the destination is READ-MODIFY-WRITTEN: 0xFFFFFFFF + 1 wraps to 0",
              (unsigned long)get_u32(DST_OFF + arena_addr()));

        /* The byte is SIGNED: 0xFF must subtract 1, not add 255. */
        setup(0u, 0u, c, 1u, 0x22u);
        for (k = 0u; k < DST_WORDS; k++) {
            put_u32(DST_OFF + arena_addr() + 4u * k, 100u);
        }
        *((u8 *)(g_arena + (c - arena_addr()))) = 0xFFu;
        sub_087B820C(PARAMS_OFF + arena_addr(), DST_OFF + arena_addr(), 1u);
        check(get_u32(DST_OFF + arena_addr()) == 99u,
              "`ldrsb` reads a SIGNED byte: 0xFF contributes -1, not +255",
              (unsigned long)get_u32(DST_OFF + arena_addr()));
    }

    /* ===================================================================== */
    /* 6. every one of the 256 byte values, against the closed form            */
    /* ===================================================================== */
    for (i = 0u; i < 256u; i++) {
        u32 k;
        const u32 c = (u32)(SAMPLE_OFF + arena_addr() + (WINDOW / 2u));
        const u32 elements = ref_elements(6u);
        setup(0x00000000u, 0x00004000u, c, 0x01020304u, i);
        for (k = 0u; k < DST_WORDS; k++) {
            expected[k] = g_initial[k];
        }
        /* the byte must be in memory BEFORE the reference reads it */
        *((u8 *)(g_arena + (c - arena_addr()))) = (u8)i;
        ref_closed_run(0u, 0x00004000u, c, 0x01020304u, 6u, expected);
        sub_087B820C(PARAMS_OFF + arena_addr(), DST_OFF + arena_addr(), 6u);
        compare(elements, expected, "all 256 signed byte values", i);
    }

    /* ===================================================================== */
    /* 7. the phase is truncated toward negative infinity                      */
    /* ===================================================================== */
    /* A = -1 with B = 0 is the discriminating case: exact arithmetic gives
     * floor(-1 / 2^14) = -1, so the address is C - 1, while truncation toward
     * zero would leave it at C. */
    {
        const u32 c = (u32)(SAMPLE_OFF + arena_addr() + (WINDOW / 2u));
        u32 k;
        setup(0xFFFFFFFFu, 0u, c, 1u, 0x33u);
        for (k = 0u; k < DST_WORDS; k++) {
            put_u32(DST_OFF + arena_addr() + 4u * k, 0u);
        }
        *((u8 *)(g_arena + (c - arena_addr() - 1u))) = 7u;   /* C - 1 */
        *((u8 *)(g_arena + (c - arena_addr()))) = 9u;        /* C     */
        sub_087B820C(PARAMS_OFF + arena_addr(), DST_OFF + arena_addr(), 1u);
        check(get_u32(DST_OFF + arena_addr()) == 7u,
              "A = -1 puts the address at C-1: floor(-1/2^14) = -1, NOT 0",
              (unsigned long)get_u32(DST_OFF + arena_addr()));
    }

    /* ===================================================================== */
    /* 8. the two specializations differ when the destination ALIASES the      */
    /*    sampled bytes - the retained sample of `ldrsbhs`                      */
    /* ===================================================================== */
    /* With the sample base pointing AT the first destination word, a group's
     * `stm` rewrites a byte that the NEXT group would read again. The general
     * body reads again; the carry-only body keeps the byte in r0 because the
     * `ldrsbhs` failed its condition, and that is a different result. */
    {
        const u32 dst_addr = DST_OFF + arena_addr();
        u32 k;

        /* --- the general body (B asr 14 == 1) READS again ---------------- */
        /* B = 0x4000 walks the address one byte per element, so the four reads
         * land on the four bytes of the first destination word. */
        setup(0u, 0x00004000u, dst_addr, 1u, 0x77u);
        put_u32(dst_addr + 0u, 0x03020140u);
        for (k = 1u; k < DST_WORDS; k++) {
            put_u32(dst_addr + 4u * k, 0u);
        }
        sub_087B820C(PARAMS_OFF + arena_addr(), dst_addr, 4u);
        check(get_u32(dst_addr + 0u) == 0x03020180u
                  && get_u32(dst_addr + 4u) == 0x00000001u
                  && get_u32(dst_addr + 8u) == 0x00000002u
                  && get_u32(dst_addr + 12u) == 0x00000003u,
              "general body: the four reads are the four BYTES 0x40,0x01,0x02,0x03",
              (unsigned long)get_u32(dst_addr + 4u));

        /* --- the carry-only body (B asr 14 == 0) RETAINS ------------------ */
        setup(0u, 0u, dst_addr, 1u, 0x78u);
        put_u32(dst_addr + 0u, 0x03020140u);
        for (k = 1u; k < DST_WORDS; k++) {
            put_u32(dst_addr + 4u * k, 0u);
        }
        sub_087B820C(PARAMS_OFF + arena_addr(), dst_addr, 4u);
        check(get_u32(dst_addr + 0u) == 0x03020180u
                  && get_u32(dst_addr + 4u) == 0x00000040u
                  && get_u32(dst_addr + 8u) == 0x00000040u
                  && get_u32(dst_addr + 12u) == 0x00000040u,
              "carry body: B = 0 never carries, so the SAME byte 0x40 is reused "
              "four times and the address never moves",
              (unsigned long)get_u32(dst_addr + 4u));

        /* --- the retention ACROSS groups, which is the discriminating case - */
        /* Two 4-element groups; the first rewrites the byte at the sample base
         * from 0x40 to 0xC0. A re-reading implementation would use 0xC0 for the
         * second group and produce 0x102 * 0xC0 = 0xC180 there. */
        setup(0u, 0u, dst_addr, 0x00000102u, 0x79u);
        put_u32(dst_addr + 0u, 0x00000040u);
        for (k = 1u; k < DST_WORDS; k++) {
            put_u32(dst_addr + 4u * k, 0u);
        }
        sub_087B820C(PARAMS_OFF + arena_addr(), dst_addr, 8u);
        check(get_u32(dst_addr + 0u) == 0x000040C0u,
              "group 1: 0x40 + 0x102 * 0x40 = 0x40C0, and the byte at the base "
              "is now 0xC0", (unsigned long)get_u32(dst_addr + 0u));
        check(get_u32(dst_addr + 16u) == 0x00004080u,
              "group 2 STILL uses the retained 0x40, giving 0x4080", 
              (unsigned long)get_u32(dst_addr + 16u));
        check(get_u32(dst_addr + 16u) != 0x0000C180u,
              "and NOT 0x102 * 0xC0 = 0xC180, which is what re-reading the byte "
              "would give: the `ldrsbhs` did not fire and did not re-read",
              (unsigned long)get_u32(dst_addr + 16u));
    }

    /* ===================================================================== */
    /* 9. the specialization selector is B asr 14 == 0, i.e. 0 <= B <= 16383   */
    /* ===================================================================== */
    check(((s32)0x00000000u >> 14) == 0 && ((s32)0x00003FFFu >> 14) == 0,
          "B in [0, 16383] selects the carry-only body", 0u);
    check(((s32)0x00004000u >> 14) == 1,
          "B = 16384 is the first GENERAL value", 0u);
    check(((s32)0xFFFFFFFFu >> 14) == -1,
          "B = -1 is NON-zero, so a negative step takes the GENERAL body: the "
          "selector is not |B| < 2^14", 0u);
    check(((s32)0xFFFFC000u >> 14) == -1,
          "B = -16384 has a zero low word and a -1 high word, so the address "
          "decrements by exactly one per element", 0u);

    printf("%s: %d check(s), %d failure(s)\n",
           failures ? "FAIL" : "PASS", checks, failures);
    return failures ? 1 : 0;
}
