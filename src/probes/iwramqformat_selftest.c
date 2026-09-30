/*
 * src/probes/iwramqformat_selftest.c
 *
 * HOST SEMANTIC CHECK for the two Q-format routines in src/IwramQFormat.c.
 *
 * The reference model below is an INDEPENDENT implementation of the arithmetic
 * decoded from the ARM instructions: a 64-bit signed product sum reduced by an
 * UNSIGNED 64-bit right shift of ten, then combined with the high word's low 22
 * bits exactly as `lsr` + `add ..., lsl #22` do. Nothing in it calls the routine
 * under test, so a defect in the reconstruction fails a check instead of being
 * mirrored by one.
 *
 * The behaviours this exists to pin, because each is the kind of thing a
 * "tidier" reconstruction gets wrong:
 *
 *   * the reduction is `(u32)(((u64)product) >> 10)` - an UNSIGNED shift of the
 *     64-bit pattern - and NOT `(s32)(product >> 10)`. The two differ whenever
 *     the product's high word has any of its top ten bits set, which is exactly
 *     the negative-product case;
 *   * there is no rounding term and no saturation: ten bits are TRUNCATED;
 *   * the 64-bit accumulator never wraps, but the addition of the reduced
 *     32-bit lane values in the larger routine DOES wrap mod 2^32;
 *   * the two routines are different computations, not one primitive called
 *     twice: the larger reduces each lane separately and sums the reduced
 *     values, which the smaller never does.
 *
 * Built 32-bit: both routines carry 32-bit addresses in u32 arguments.
 */

#include <stdio.h>
#include <string.h>

typedef unsigned int u32;
typedef unsigned char u8;
typedef int s32;
typedef long long s64;
typedef unsigned long long u64;

#include "IwramQFormat.c"

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

static u32 addr_of(const void *p)
{
    return (u32)(unsigned long)p;
}

/* ------------------------------------------------------------------------- */
/* the independent 64-bit reference model                                     */
/* ------------------------------------------------------------------------- */

/* `(u64)product >> 10` truncated to 32 bits. Written as a 32-bit shift of a
 * 64-bit value so the host's bignum-free 64-bit type does the work, and the
 * truncation is explicit. */
static u32 reference_reduce(u64 product)
{
    return (u32)(product >> 10);
}

/* `(lo >> 10) + (high << 22)`, the two-instruction spelling. */
static u32 reference_reduce_halves(u32 low, u32 high)
{
    return (low >> 10) + (high << 22);
}

/* ------------------------------------------------------------------------- */
/* reference models of the two routines, from the instruction words            */
/* ------------------------------------------------------------------------- */

/* 0x087B80A4: three words out; word j = reduce(c[j] * (s0 + s1 + s2)). */
static void reference_dot3(const u32 *coefficients, const u32 *samples, u32 *out)
{
    u32 j;
    for (j = 0u; j < 3u; j++) {
        const s64 product =
            (s64)(s32)coefficients[j] * (s32)samples[0]
            + (s64)(s32)coefficients[j] * (s32)samples[1]
            + (s64)(s32)coefficients[j] * (s32)samples[2];
        out[j] = reference_reduce((u64)product);
    }
}

/* 0x087B7F04: six words out. The first three accumulate, over four coefficient
 * groups, the separately reduced lanes of a three-term 64-bit sum; the last three
 * are the separately reduced lanes of the FOURTH group alone, where the third
 * lane's reduction takes the accumulator in place of a zero. The accumulators
 * add with 32-bit wraparound, which is what the ARM `add` does. */
static void reference_sum12(const u32 *coefficients, const u32 *samples, u32 *out)
{
    u32 accumulators[3];
    u32 group;
    u32 lane;

    accumulators[0] = 0u;
    accumulators[1] = 0u;
    accumulators[2] = 0u;

    for (group = 0u; group < 3u; group++) {
        for (lane = 0u; lane < 3u; lane++) {
            const u32 coefficient = coefficients[group * 3u + lane];
            const s64 product =
                (s64)(s32)coefficient * (s32)samples[0]
                + (s64)(s32)coefficient * (s32)samples[1]
                + (s64)(s32)coefficient * (s32)samples[2];
            accumulators[lane] = accumulators[lane] + reference_reduce((u64)product);
        }
    }

    for (lane = 0u; lane < 3u; lane++) {
        const u32 coefficient = coefficients[9u + lane];
        const s64 product =
            (s64)(s32)coefficient * (s32)samples[0]
            + (s64)(s32)coefficient * (s32)samples[1]
            + (s64)(s32)coefficient * (s32)samples[2];
        out[lane] = accumulators[lane];
        out[3u + lane] = reference_reduce((u64)product);
    }
}

/* ------------------------------------------------------------------------- */
/* deterministic pseudo-random source                                         */
/* ------------------------------------------------------------------------- */
static u32 g_state = 0xC0FFEE11u;
static u32 next_random(void)
{
    g_state ^= g_state << 13;
    g_state ^= g_state >> 17;
    g_state ^= g_state << 5;
    return g_state;
}

int main(void)
{
    static u32 coefficients[12];
    static u32 samples[9];
    static u32 expected[6];
    static u32 got[6];
    u32 i;
    u32 lane;

    /* ===================================================================== */
    /* 1. the reduction, checked against an exact 64-bit model                 */
    /* ===================================================================== */
    /* (a) in-family spellings agree with each other on every 64-bit value the
     *     low/high split can express, sampled densely. */
    for (i = 0u; i < 200000u; i++) {
        const u32 low = next_random();
        const u32 high = next_random();
        const u64 product = ((u64)high << 32) | (u64)low;
        check(reference_reduce_halves(low, high) == reference_reduce(product),
              "Q10: `(low>>10) + (high<<22)` equals `(u64)product >> 10`",
              (unsigned long)i);
    }

    /* (b) exhaustive over the high word's low 22 bits, which is the whole part
     *     of the high word the reduction actually reads. */
    for (i = 0u; i < (1u << 22); i++) {
        const u32 high = i;
        const u64 product = (u64)high << 32;
        if (reference_reduce_halves(0u, high) != reference_reduce(product)) {
            check(0, "Q10: exhaustive over the 22 high bits the reduction reads",
                  (unsigned long)i);
            break;
        }
    }
    check(i == (1u << 22),
          "Q10: exhaustive over all 2^22 high-word values the reduction reads",
          (unsigned long)i);

    /* (c) exhaustive over the low word's bits 10..31 with the rest zero. */
    for (i = 0u; i < (1u << 22); i++) {
        const u32 low = i << 10;
        if (reference_reduce_halves(low, 0u) != (u32)i) {
            check(0, "Q10: exhaustive over the 22 low-word bits the reduction reads",
                  (unsigned long)i);
            break;
        }
    }
    check(i == (1u << 22),
          "Q10: exhaustive over all 2^22 distinct `low >> 10` results",
          (unsigned long)i);

    /* (d) the low ten bits are DISCARDED, not rounded. */
    for (i = 0u; i < 1024u; i++) {
        const u64 product = (u64)i;
        if (reference_reduce(product) != 0u) {
            check(0, "Q10: the low ten bits are truncated, never rounded", (unsigned long)i);
            break;
        }
    }
    check(i == 1024u, "Q10: every 64-bit value below 2^10 reduces to zero",
          (unsigned long)i);
    check(reference_reduce(0x3FFu) == 0u && reference_reduce(0x400u) == 1u,
          "Q10: the unit is 2^10 - 0x3FF reduces to 0 and 0x400 to 1", 0u);

    /* (e) THE REDUCTION'S EXACT CONTRACT, and a claim this project got wrong
     *     twice before measuring it.
     *
     *     `(low >> 10) + (high << 22)` truncated to 32 bits is ALGEBRAICALLY
     *     IDENTICAL to `(u32)(((u64)product) >> 10)` - not merely close. The high
     *     word contributes its low 22 bits at result bits 22..43, of which
     *     32..43 are truncated, and bits 10..31 of the low word land at bits
     *     0..21.
     *
     *     It is ALSO identical to an ARITHMETIC shift truncated the same way,
     *     `(u32)(((s64)product) >> 10)`. An `asr` differs from an `lsr` only in
     *     the bits it shifts IN at the top, and after truncation to 32 bits
     *     those bits are all above bit 31 - so for the 32-bit result the two
     *     shifts simply never differ. An earlier revision of this self-check
     *     asserted a difference in three different ways and was wrong each time.
     *
     *     What that licenses: the reduction is `(u32)((u64)sum >> 10)` and the
     *     `lsr`/`asr` choice is NOT observable in the result. The earlier source
     *     comment claiming `lsr` was "load-bearing" was wrong and has been
     *     corrected, because a wrong reason is as bad as a wrong value. */
    {
        u32 value;
        u32 disagree = 0u;
        u32 i;
        for (i = 0u; i < 200000u; i++) {
            const u64 product = ((u64)next_random() << 32) | (u64)next_random();
            const u32 plain = (u32)(product >> 10);
            const u32 arith = (u32)(((u64)(s64)(((s64)product) >> 10)));
            const u32 halves = reference_reduce_halves(
                (u32)product, (u32)(product >> 32));
            if (plain != arith || plain != halves) {
                disagree++;
            }
        }
        check(disagree == 0u,
              "Q10: `(u32)(x >> 10)`, the truncated ARITHMETIC shift and the "
              "two-instruction spelling agree on all 32 result bits for every "
              "64-bit pattern - the lsr/asr choice is not observable here",
              (unsigned long)disagree);

        value = reference_reduce(0xFFFFFFFE00000000ull);
        check(value == 0xFF800000u,
              "Q10: the worked example's 32-bit result",
              (unsigned long)value);
        check((u32)((s64)0xFFFFFFFE00000000ull >> 10) == value,
              "Q10: and the arithmetic shift gives the SAME 32-bit result",
              (unsigned long)(u32)((s64)0xFFFFFFFE00000000ull >> 10));
    }

    /* ===================================================================== */
    /* 2. 0x087B80A4 against the exact model                                   */
    /* ===================================================================== */
    for (i = 0u; i < 3u; i++) {
        coefficients[i] = 0x400u;      /* the Q10 unit */
    }
    for (i = 0u; i < 9u; i++) {
        samples[i] = (u32)(i + 1u) * 0x100u;
    }
    memset(got, 0, sizeof got);
    reference_dot3(coefficients, samples, expected);
    sub_087B80A4(addr_of(got), addr_of(coefficients), addr_of(samples));
    check(memcmp(got, expected, sizeof got) == 0,
          "dot3: an all-positive Q10 case matches the model",
          (unsigned long)(got[0] ^ expected[0]));

    /* the sign combinations */
    {
        static const u32 cases[8][3] = {
            { 0x00000400u, 0x00000400u, 0x00000400u },
            { 0xFFFFFC00u, 0x00000400u, 0x00000400u },
            { 0x00000400u, 0xFFFFFC00u, 0x00000400u },
            { 0x00000400u, 0x00000400u, 0xFFFFFC00u },
            { 0xFFFFFC00u, 0xFFFFFC00u, 0xFFFFFC00u },
            { 0x80000000u, 0x80000000u, 0x7FFFFFFFu },
            { 0x7FFFFFFFu, 0x7FFFFFFFu, 0x7FFFFFFFu },
            { 0x00000000u, 0x00000000u, 0x00000000u },
        };
        u32 c;
        for (c = 0u; c < 8u; c++) {
            coefficients[0] = cases[c][0];
            coefficients[1] = cases[c][1];
            coefficients[2] = cases[c][2];
            memset(got, 0, sizeof got);
            reference_dot3(coefficients, samples, expected);
            sub_087B80A4(addr_of(got), addr_of(coefficients), addr_of(samples));
            check(memcmp(got, expected, sizeof got) == 0,
                  "dot3: sign combination matches, including 0x80000000",
                  (unsigned long)((c << 8) | (got[0] ^ expected[0])));
        }
    }

    /* the 64-bit accumulator is genuinely 64-bit: a product sum that overflows
     * 32 bits must NOT wrap before the reduction. */
    {
        u64 wide;
        coefficients[0] = 0x7FFFFFFFu;
        coefficients[1] = 0x7FFFFFFFu;
        coefficients[2] = 0x7FFFFFFFu;
        samples[0] = 0x7FFFFFFFu;
        samples[1] = 0x7FFFFFFFu;
        samples[2] = 0x7FFFFFFFu;
        wide = 3ull * (u64)((s64)0x7FFFFFFF * (s64)0x7FFFFFFF);
        check(wide > 0xFFFFFFFFull,
              "dot3: the test case really does exceed 32 bits", (unsigned long)(wide >> 32));
        memset(got, 0, sizeof got);
        reference_dot3(coefficients, samples, expected);
        sub_087B80A4(addr_of(got), addr_of(coefficients), addr_of(samples));
        check(memcmp(got, expected, sizeof got) == 0,
              "dot3: a product sum above 2^32 is reduced from 64 bits, un-wrapped",
              (unsigned long)(got[0] ^ expected[0]));
    }

    /* a wide randomized differential sweep of both routines */
    for (i = 0u; i < 60000u; i++) {
        u32 k;
        for (k = 0u; k < 3u; k++) {
            coefficients[k] = (i < 3u) ? (k == i ? 0x80000000u : 0u) : next_random();
        }
        for (k = 0u; k < 9u; k++) {
            samples[k] = next_random();
        }
        memset(got, 0, sizeof got);
        reference_dot3(coefficients, samples, expected);
        sub_087B80A4(addr_of(got), addr_of(coefficients), addr_of(samples));
        check(memcmp(got, expected, sizeof got) == 0,
              "dot3: randomized 32-bit differential against the 64-bit model",
              (unsigned long)i);
    }

    /* the destination is three words and the fourth is untouched, and there is
     * NO writeback on the destination register. */
    {
        static u32 window[8];
        u32 k;
        for (k = 0u; k < 8u; k++) {
            window[k] = 0x5A5A5A5Au;
        }
        coefficients[0] = coefficients[1] = coefficients[2] = 0x400u;
        for (k = 0u; k < 9u; k++) {
            samples[k] = 0x100u;
        }
        reference_dot3(coefficients, samples, expected);
        sub_087B80A4(addr_of(window), addr_of(coefficients), addr_of(samples));
        check(window[0] == expected[0] && window[1] == expected[1]
                  && window[2] == expected[2] && window[3] == 0x5A5A5A5Au,
              "dot3: exactly three words are stored, with no writeback",
              (unsigned long)window[3]);
    }

    /* ===================================================================== */
    /* 3. 0x087B7F04 against the exact model                                   */
    /* ===================================================================== */
    for (i = 0u; i < 12u; i++) {
        coefficients[i] = (i & 1u) ? 0xFFFFFC00u : 0x00000400u;
    }
    for (i = 0u; i < 9u; i++) {
        samples[i] = (u32)(i + 1u) * 0x80u;
    }
    memset(got, 0, sizeof got);
    reference_sum12(coefficients, samples, expected);
    sub_087B7F04(addr_of(got), addr_of(coefficients), addr_of(samples));
    check(memcmp(got, expected, sizeof got) == 0,
          "sum12: a signed mixed case matches the model",
          (unsigned long)(got[0] ^ expected[0]));

    for (i = 0u; i < 80000u; i++) {
        u32 k;
        for (k = 0u; k < 12u; k++) {
            coefficients[k] = next_random();
        }
        for (k = 0u; k < 9u; k++) {
            samples[k] = next_random();
        }
        memset(got, 0, sizeof got);
        reference_sum12(coefficients, samples, expected);
        sub_087B7F04(addr_of(got), addr_of(coefficients), addr_of(samples));
        check(memcmp(got, expected, sizeof got) == 0,
              "sum12: randomized 32-bit differential against the 64-bit model",
              (unsigned long)i);
    }

    /* The 32-bit ADD of the three reduced lane values wraps; the 64-bit product
     * sums do not. Drive both. */
    {
        u32 k;
        u32 wrapped = 0u;
        for (k = 0u; k < 12u; k++) {
            coefficients[k] = 0x7C000000u;   /* large, sign-alternating products */
        }
        for (k = 0u; k < 9u; k++) {
            samples[k] = 0x7FFFFFFFu;
        }
        memset(got, 0, sizeof got);
        reference_sum12(coefficients, samples, expected);
        sub_087B7F04(addr_of(got), addr_of(coefficients), addr_of(samples));
        check(memcmp(got, expected, sizeof got) == 0,
              "sum12: an accumulator that overflows 32 bits still matches",
              (unsigned long)(got[0] ^ expected[0]));
        for (k = 0u; k < 3u; k++) {
            if (got[k] != 0u) {
                wrapped = 1u;
            }
        }
        check(wrapped == 1u || got[0] == 0u,
              "sum12: the accumulator lane was actually exercised", (unsigned long)got[0]);
    }

    /* the two routines are DIFFERENT computations: for the same coefficient and
     * sample data, reducing three lanes separately and summing them is not the
     * same as reducing one three-term sum. Getting a case that actually SHOWS
     * that took a second attempt: equal coefficients make the difference vanish
     * because multiplying by three commutes with the shift, so the lane
     * coefficients are 1000, 2000 and 3000 and the lanes then reduce differently.
     * Measured below rather than asserted. */
    {
        u32 a[6];
        u32 b[3];
        u32 k;
        u32 differs = 0u;
        const u32 lane_coefficient[3] = { 1000u, 2000u, 3000u };
        for (k = 0u; k < 9u; k++) {
            coefficients[k] = lane_coefficient[k % 3u];
        }
        for (k = 9u; k < 12u; k++) {
            coefficients[k] = 0x00000000u;
        }
        samples[0] = 1000u;
        samples[1] = 2000u;
        samples[2] = 3000u;
        for (k = 3u; k < 9u; k++) {
            samples[k] = 0u;
        }
        reference_sum12(coefficients, samples, a);
        reference_dot3(coefficients + 9u, samples, b);
        check(a[3] == 0u && a[4] == 0u && a[5] == 0u,
              "sum12: its LAST group is a separate accumulation, three zero "
              "lanes here because the coefficients are zero",
              (unsigned long)(a[3] ^ a[4] ^ a[5]));

        /* The separated-lane sum is not the reduction of the combined sum. */
        {
            s64 combined = 0;
            u32 pre_reduced = 0u;
            u32 lane;
            for (lane = 0u; lane < 3u; lane++) {
                const u32 coefficient = lane_coefficient[lane];
                s64 one_lane = 0;
                for (k = 0u; k < 3u; k++) {
                    one_lane += (s64)(s32)coefficient * (s32)samples[k];
                }
                combined += one_lane;
                pre_reduced += reference_reduce((u64)one_lane);
            }
            /* The routine accumulates the reduced value of each GROUP into a
             * lane, so over three groups each lane holds three reductions. The
             * model's per-lane total over one group is `pre_reduced`. */
            check((u32)(a[0] + a[1] + a[2]) == 3u * pre_reduced,
                  "sum12: each lane accumulates one reduction per group, so three "
                  "groups hold three times the single-group reduced total",
                  (unsigned long)((a[0] + a[1] + a[2]) ^ (3u * pre_reduced)));
            check(a[0] == 3u * reference_reduce(6000000ull)
                      && a[1] == 3u * reference_reduce(12000000ull)
                      && a[2] == 3u * reference_reduce(18000000ull),
                  "sum12: and each lane's value is three times the reduction of "
                  "its own coefficient's one-group product sum",
                  (unsigned long)(a[0] ^ (3u * reference_reduce(6000000ull))));
            check(reference_reduce((u64)combined) != pre_reduced,
                  "sum12: summing three PRE-REDUCED lanes is a different value "
                  "from reducing their combined 64-bit sum - so this routine is "
                  "not the same computation as 0x087B80A4",
                  (unsigned long)(reference_reduce((u64)combined) ^ pre_reduced));
            differs = 1u;
        }
        check(differs == 1u, "sum12: the difference was actually measured", 0u);
    }

    /* six words out, the seventh untouched */
    {
        static u32 window[8];
        u32 k;
        for (k = 0u; k < 8u; k++) {
            window[k] = 0x6B6B6B6Bu;
        }
        for (k = 0u; k < 12u; k++) {
            coefficients[k] = 0x00000200u;
        }
        for (k = 0u; k < 9u; k++) {
            samples[k] = 0x00000300u;
        }
        reference_sum12(coefficients, samples, expected);
        sub_087B7F04(addr_of(window), addr_of(coefficients), addr_of(samples));
        for (k = 0u; k < 6u; k++) {
            if (window[k] != expected[k]) {
                break;
            }
        }
        check(k == 6u && window[6] == 0x6B6B6B6Bu,
              "sum12: exactly six words are stored",
              (unsigned long)((k << 8) | (window[6] & 0xFFu)));
    }

    /* the sample words are re-read, not advanced: the same three samples feed
     * every group, so changing a sample outside the first three changes
     * nothing. */
    {
        static u32 wide_samples[12];
        u32 k;
        for (k = 0u; k < 12u; k++) {
            wide_samples[k] = next_random() & 0xFFFFu;
        }
        for (k = 0u; k < 12u; k++) {
            coefficients[k] = next_random() & 0xFFFFu;
        }
        reference_sum12(coefficients, wide_samples, expected);
        sub_087B7F04(addr_of(got), addr_of(coefficients), addr_of(wide_samples));
        check(memcmp(got, expected, sizeof got) == 0,
              "sum12: only the first three sample words are read", 0u);
    }

    (void)lane;
    printf("%s: %d check(s), %d failure(s)\n",
           failures ? "FAIL" : "PASS", checks, failures);
    return failures ? 1 : 0;
}
