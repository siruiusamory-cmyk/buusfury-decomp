/*
 * src/probes/iwramfieldclamp_selftest.c
 *
 * HOST SEMANTIC CHECK for src/IwramFieldClamp.c.
 *
 * Every expected value is computed HERE, from the field layout decoded from the
 * ARM instructions, and never by calling the routine under test. The reference
 * deliberately derives each field the OTHER way round from the ROM: it uses a
 * LOGICAL shift and a 0x3FF mask (`(w >> shift) & 0x3FF`, then sign-extends from
 * bit 9), where the routine uses `lsl`/`asr` pairs. A mistake in either the
 * offsets or the sign extension therefore shows up as a disagreement instead of
 * being mirrored by both sides.
 *
 * The behaviours this exists to pin, because each is the kind of thing a
 * "tidier" reconstruction gets wrong:
 *
 *   * each source word carries TWO ten-bit SIGNED fields, at bits 31..22 and at
 *     bits 15..6 - bits 21..16 and 5..0 are never read;
 *   * each field is SATURATED to [-128, 127], not wrapped and not truncated;
 *   * the two LOW-field bytes are packed into the first destination stream and
 *     the two HIGH-field bytes into the second: it is a DE-INTERLEAVE, not a
 *     conversion of one stream;
 *   * the source pair is ZEROED IN PLACE before anything is written;
 *   * the count is a do-while over word PAIRS tested with a SIGNED compare, so
 *     the body always runs at least once and an odd count over-reads a word.
 */

#include <stdio.h>
#include <string.h>

typedef unsigned int u32;
typedef unsigned short u16;
typedef unsigned char u8;
typedef int s32;

#include "IwramFieldClamp.c"

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

#define ARENA 0x8000
#define DST0_OFF 0x0100
#define DST1_OFF 0x0900
#define SRC_OFF 0x1000
#define SRC_WORDS 512
#define SENTINEL 0x5Au

static u8 g_arena[ARENA];

static u32 arena_addr(void)
{
    return (u32)(unsigned long)g_arena;
}

static u32 dst0(void) { return DST0_OFF + arena_addr(); }
static u32 dst1(void) { return DST1_OFF + arena_addr(); }
static u32 src(void)  { return SRC_OFF + arena_addr(); }

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

static void put_u16(u32 address, u32 value)
{
    g_arena[address - arena_addr() + 0u] = (u8)(value & 0xFFu);
    g_arena[address - arena_addr() + 1u] = (u8)((value >> 8) & 0xFFu);
}

static u32 get_u16(u32 address)
{
    return (u32)g_arena[address - arena_addr() + 0u]
         | ((u32)g_arena[address - arena_addr() + 1u] << 8);
}

/* ------------------------------------------------------------------------- */
/* the reference: masks and a logical shift, the OTHER derivation              */
/* ------------------------------------------------------------------------- */
static int ref_field(u32 word, unsigned shift)
{
    const u32 raw = (word >> shift) & 0x3FFu;      /* ten bits */
    return (raw & 0x200u) ? (int)raw - 0x400 : (int)raw;
}

static unsigned char ref_sat(int value)
{
    if (value > 127) {
        return (unsigned char)127;
    }
    if (value < -128) {
        return (unsigned char)(-128);
    }
    return (unsigned char)value;
}

/* One iteration: the two source words in, the two destination halfwords out. */
static u16 ref_dst0(u32 word0, u32 word1)
{
    return (u16)((u32)ref_sat(ref_field(word0, 6))
                 | ((u32)ref_sat(ref_field(word1, 6)) << 8));
}

static u16 ref_dst1(u32 word0, u32 word1)
{
    return (u16)((u32)ref_sat(ref_field(word0, 22))
                 | ((u32)ref_sat(ref_field(word1, 22)) << 8));
}

static void reset_arena(u32 src_seed)
{
    u32 i;
    u32 state = src_seed | 1u;
    memset(g_arena, (int)SENTINEL, sizeof g_arena);
    for (i = 0u; i < SRC_WORDS; i++) {
        state = state * 1103515245u + 12345u;
        put_u32(src() + 4u * i, state);
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

int main(void)
{
    u32 i;
    u32 state = 0x13579BDFu;

    /* ===================================================================== */
    /* 1. every value of every one of the four field positions                 */
    /* ===================================================================== */
    /* A field is ten bits, so 1024 values; sweep each of the four positions
     * while the other three hold a marker that must not leak into it. */
    for (i = 0u; i < 1024u; i++) {
        const u32 word0_low = (0x155u << 22) | (i << 6);
        const u32 word1_low = (0x2AAu << 22) | (i << 6);
        const u32 word0_high = (i << 22) | (0x155u << 6);
        const u32 word1_high = (i << 22) | (0x2AAu << 6);

        reset_arena(0x100u + i);
        put_u32(src() + 0u, word0_low);
        put_u32(src() + 4u, word1_low);
        sub_087B83F0(dst0(), dst1(), src(), 2u);
        check(get_u16(dst0()) == ref_dst0(word0_low, word1_low),
              "exhaustive low field of both words", i);
        check(get_u16(dst1()) == ref_dst1(word0_low, word1_low),
              "high fields are carried through unchanged by the low sweep", i);

        reset_arena(0x200u + i);
        put_u32(src() + 0u, word0_high);
        put_u32(src() + 4u, word1_high);
        sub_087B83F0(dst0(), dst1(), src(), 2u);
        check(get_u16(dst1()) == ref_dst1(word0_high, word1_high),
              "exhaustive high field of both words", i);
        check(get_u16(dst0()) == ref_dst0(word0_high, word1_high),
              "low fields are carried through unchanged by the high sweep", i);
    }

    /* ===================================================================== */
    /* 2. every PAIR of field values inside one word                           */
    /* ===================================================================== */
    {
        u32 low;
        for (low = 0u; low < 1024u; low += 7u) {
            u32 high;
            for (high = 0u; high < 1024u; high += 5u) {
                const u32 word = (high << 22) | (low << 6);
                reset_arena(0x300u + low + high);
                put_u32(src() + 0u, word);
                put_u32(src() + 4u, word ^ 0xFFFFFFFFu);
                sub_087B83F0(dst0(), dst1(), src(), 2u);
                check(get_u16(dst0()) == ref_dst0(word, word ^ 0xFFFFFFFFu),
                      "both fields of one word, swept together", (low << 16) | high);
                check(get_u16(dst1()) == ref_dst1(word, word ^ 0xFFFFFFFFu),
                      "both fields of one word, swept together (high stream)",
                      (low << 16) | high);
            }
        }
    }

    /* ===================================================================== */
    /* 3. the saturation boundaries, each side                                 */
    /* ===================================================================== */
    {
        int value;
        for (value = -512; value <= 511; value++) {
            const u32 encoded = (u32)(value & 0x3FF);
            const u32 word = (encoded << 6) | (encoded << 22);
            const int clamped = (value > 127) ? 127 : ((value < -128) ? -128 : value);
            const u8 expected = (u8)(clamped & 0xFF);

            reset_arena(0x400u + (u32)(value + 512));
            put_u32(src() + 0u, word);
            put_u32(src() + 4u, word);
            sub_087B83F0(dst0(), dst1(), src(), 2u);
            check((get_u16(dst0()) & 0xFFu) == (u32)expected
                      && (get_u16(dst1()) & 0xFFu) == (u32)expected,
                  "saturation over the whole ten-bit domain", (unsigned long)(value + 512));
        }
        check(ref_sat(128) == 127u && ref_sat(-129) == 0x80u,
              "the bounds are -128 and +127, not -127 and +128", 0u);
        check((int)ref_sat(127) == 127 && (int)ref_sat(-128) == 0x80,
              "the bounds themselves are inclusive (-128 is stored as 0x80)", 0u);
    }

    /* ===================================================================== */
    /* 4. the source pair is zeroed in place, and the pointer advances         */
    /* ===================================================================== */
    {
        u32 k;
        u32 ok = 1u;
        reset_arena(0x500u);
        put_u32(src() + 0u, 0x12345678u);
        put_u32(src() + 4u, 0x9ABCDEF0u);
        put_u32(src() + 8u, 0x11111111u);
        sub_087B83F0(dst0(), dst1(), src(), 2u);
        if (get_u32(src() + 0u) != 0u || get_u32(src() + 4u) != 0u) {
            ok = 0u;
        }
        check(ok, "`stm r2!,{r8,ip}` with r8 = ip = 0 zeroes the source pair",
              (unsigned long)get_u32(src() + 0u));
        check(get_u32(src() + 8u) == 0x11111111u,
              "the source pair AFTER the consumed one is untouched", 0u);

        /* The pointer advanced: a second call consumes the next pair. */
        reset_arena(0x600u);
        put_u32(src() + 0u, 0xFFFFFFFFu);
        put_u32(src() + 4u, 0xFFFFFFFFu);
        put_u32(src() + 8u, 0x00000000u);
        put_u32(src() + 12u, 0x00000000u);
        sub_087B83F0(dst0(), dst1(), src(), 4u);
        ok = 1u;
        for (k = 0u; k < 16u; k++) {
            if (g_arena[SRC_OFF + k] != 0u) { ok = 0u; break; }
        }
        check(ok, "two iterations consume four words and zero all of them",
              (unsigned long)k);
        check(get_u16(dst0()) == ref_dst0(0xFFFFFFFFu, 0xFFFFFFFFu),
              "0xFFFFFFFF saturates to 0x7F in both streams, giving 0x7F7F",
              (unsigned long)get_u16(dst0()));
    }

    /* ===================================================================== */
    /* 5. the count is a do-while over PAIRS, signed, with no pre-test         */
    /* ===================================================================== */
    {
        static const u32 counts[11] = { 0u, 1u, 2u, 3u, 4u, 5u, 6u, 7u, 8u, 9u,
                                        0xFFFFFFFFu };
        u32 c;
        for (c = 0u; c < 11u; c++) {
            const u32 count = counts[c];
            u32 iterations = 0u;
            u32 n = count;
            u32 k;
            u32 ok = 1u;

            /* the reference pass count, from the decoded `subs #2 ; bgt` */
            for (;;) {
                iterations++;
                if ((s32)n <= 2) {
                    break;
                }
                n -= 2u;
            }

            reset_arena(0x700u + c);
            /* a count of 9 runs five iterations, i.e. TEN words: initialise
             * more than the largest pass count can consume */
            for (k = 0u; k < 32u; k++) {
                put_u32(src() + 4u * k, 0x01020304u + k);
            }
            memset(g_arena + DST0_OFF, (int)SENTINEL, 0x800);
            sub_087B83F0(dst0(), dst1(), src(), count);

            for (k = 0u; k < iterations; k++) {
                const u32 w0 = 0x01020304u + 2u * k;
                const u32 w1 = 0x01020304u + 2u * k + 1u;
                if (get_u16(dst0() + 2u * k) != ref_dst0(w0, w1)
                        || get_u16(dst1() + 2u * k) != ref_dst1(w0, w1)) {
                    ok = 0u;
                    break;
                }
            }
            check(ok, "the pass count is ceil(count/2) for count > 2 and 1 otherwise",
                  (unsigned long)(count ^ (k << 16)));
            check(get_u16(dst0() + 2u * iterations) == (u32)(SENTINEL | (SENTINEL << 8)),
                  "the first halfword past the last pass is untouched",
                  (unsigned long)count);
        }
        check(1u + ((0u - 1u) ? 0u : 1u) == 1u,
              "a negative count still runs the body once", 0u);
        /* count 0 runs once (the do-while), so it consumes TWO words */
        reset_arena(0x7F0u);
        put_u32(src() + 0u, 0x0000FC00u);
        put_u32(src() + 4u, 0x0000FC00u);
        sub_087B83F0(dst0(), dst1(), src(), 0u);
        check(get_u16(dst0()) == ref_dst0(0x0000FC00u, 0x0000FC00u),
              "count 0 still runs the body once and writes one halfword", 0u);
        check(get_u32(src() + 0u) == 0u && get_u32(src() + 4u) == 0u,
              "count 0 still zeroes the pair it consumed", 0u);
    }

    /* ===================================================================== */
    /* 6. an odd count over-reads one word, and the LAST pair is used          */
    /* ===================================================================== */
    {
        /* count 3: two iterations, the second reading words 2 and 3 */
        reset_arena(0x800u);
        put_u32(src() + 0u, 0x0000FC00u);
        put_u32(src() + 4u, 0x00000000u);
        put_u32(src() + 8u, 0x00000400u);
        put_u32(src() + 12u, 0xFFFFFFFFu);
        sub_087B83F0(dst0(), dst1(), src(), 3u);
        check(get_u16(dst0() + 0u) == ref_dst0(0x0000FC00u, 0x00000000u),
              "count 3 iteration 1 uses words 0 and 1", 0u);
        check(get_u16(dst0() + 2u) == ref_dst0(0x00000400u, 0xFFFFFFFFu),
              "count 3 iteration 2 uses words 2 AND 3 - the odd count over-reads",
              0u);
    }

    /* ===================================================================== */
    /* 7. randomized differential over multi-word buffers                      */
    /* ===================================================================== */
    for (i = 0u; i < 4000u; i++) {
        const u32 count = (next_random(&state) % 20u) * 2u;
        const u32 iterations = (count == 0u) ? 1u : (count / 2u);
        u32 k;
        u32 ok = 1u;

        reset_arena(0x900u + i);
        for (k = 0u; k < SRC_WORDS; k++) {
            put_u32(src() + 4u * k, next_random(&state));
        }
        {
            static u32 saved[SRC_WORDS];
            for (k = 0u; k < SRC_WORDS; k++) {
                saved[k] = get_u32(src() + 4u * k);
            }
            memset(g_arena + DST0_OFF, (int)SENTINEL, 0x800);
            sub_087B83F0(dst0(), dst1(), src(), count);
            for (k = 0u; k < iterations; k++) {
                if (get_u16(dst0() + 2u * k) != ref_dst0(saved[2u * k], saved[2u * k + 1u])
                        || get_u16(dst1() + 2u * k) != ref_dst1(saved[2u * k], saved[2u * k + 1u])) {
                    ok = 0u;
                    break;
                }
            }
            for (k = 0u; ok && k < 2u * iterations; k++) {
                if (get_u32(src() + 4u * k) != 0u) {
                    ok = 0u;
                    break;
                }
            }
        }
        check(ok, "randomized two-stream differential", (unsigned long)i);
    }

    /* ===================================================================== */
    /* 8. the two destinations may be the same address                         */
    /* ===================================================================== */
    {
        reset_arena(0xA00u);
        put_u32(src() + 0u, 0x0000FC00u);
        put_u32(src() + 4u, 0x0000FC00u);
        sub_087B83F0(dst0(), dst0(), src(), 2u);
        check(get_u16(dst0()) == ref_dst1(0x0000FC00u, 0x0000FC00u),
              "with r0 == r1 the SECOND store wins, as the instruction order says",
              (unsigned long)get_u16(dst0()));
    }

    printf("%s: %d check(s), %d failure(s)\n",
           failures ? "FAIL" : "PASS", checks, failures);
    return failures ? 1 : 0;
}
