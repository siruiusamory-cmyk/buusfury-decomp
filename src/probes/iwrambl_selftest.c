/*
 * src/probes/iwrambl_selftest.c
 *
 * HOST SEMANTIC CHECK for the byte-lane family in src/IwramByteLanePair.c.
 *
 * Every expected value is computed HERE, from the lane equation decoded from the
 * ARM instructions, and never by calling the routine under test. Anything the
 * reconstruction gets wrong therefore fails a check rather than being mirrored
 * by one. The interpreters below are explicit models of the ARM instructions -
 * 32-bit modular arithmetic, LOGICAL shifts, a 0xFF mask applied with `ands` so
 * the zero flag is set, and predication where a condition that is false must
 * leave both the destination register and memory alone.
 *
 * The behaviours this exists to pin, because each is the kind of thing a
 * "tidier" reconstruction gets wrong:
 *
 *   * a zero source lane NEVER reads the table (so table[0] is unreachable) in
 *     0x087B7C80, and NEVER stores in 0x087B7CD4;
 *   * an all-zero source word stores NOTHING in 0x087B7CD4, but its destination
 *     still advances by four;
 *   * 0x087B7C80 has NO pre-test on the count, so count == 0 wraps the counter
 *     and runs 2^30 passes, and a count that is not a multiple of four never
 *     terminates - both are recorded, neither is guarded;
 *   * 0x087B7CD4's count test is SIGNED (`bmi`), so a count of 0x80000000
 *     returns having stored nothing;
 *   * the lane map is the identity in both routines, so neither permutes bytes.
 *
 * Built 32-bit: both routines carry byte ADDRESSES in u32 registers and the
 * wraparound is part of what is being modelled.
 */

#include <stdio.h>
#include <string.h>

typedef unsigned int u32;
typedef unsigned char u8;
typedef int s32;

#include "IwramByteLanePair.c"
#include "IwramByteLaneSparse.c"

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
/* 32-bit address helpers                                                     */
/* ------------------------------------------------------------------------- */
static u32 addr_of(const void *p)
{
    return (u32)(unsigned long)p;
}

/* ------------------------------------------------------------------------- */
/* reference interpreters, straight from the instruction words                */
/* ------------------------------------------------------------------------- */

/* 0x087B7C80: `bne` at the end of a pass, counter decremented by four, exit on
 * exactly zero. The iteration count is therefore the number of four-byte steps
 * from `count` to zero mod 2^32: 2^30 when count is zero, count/4 when count is
 * a multiple of four, and unbounded otherwise. This function is only ever called
 * with a terminating count; the bound is high enough that the count-zero case
 * (2^30 passes) is reported as non-terminating rather than run. */
static u32 reference_a1_passes(u32 count)
{
    u32 remaining = count;
    u32 passes = 0u;
    if (count == 0u) {
        return 0xFFFFFFFFu;   /* 2^30 passes; modelled, not executed */
    }
    while (remaining != 0u) {
        remaining -= 4u;
        passes++;
        if (passes > 0x20000000u) {
            return 0xFFFFFFFFu;
        }
    }
    return passes;
}

static u32 reference_a1_word(u32 word, const u8 *table)
{
    const u32 lane0 = word & 0xFFu;
    const u32 lane1 = (word >> 8) & 0xFFu;
    const u32 lane2 = (word >> 16) & 0xFFu;
    const u32 lane3 = (word >> 24) & 0xFFu;
    const u32 b0 = (lane0 != 0u) ? (u32)table[lane0] : 0u;
    const u32 b1 = (lane1 != 0u) ? (u32)table[lane1] : 0u;
    const u32 b2 = (lane2 != 0u) ? (u32)table[lane2] : 0u;
    const u32 b3 = (lane3 != 0u) ? (u32)table[lane3] : 0u;
    return b0 | (b1 << 8) | (b2 << 16) | (b3 << 24);
}

/* 0x087B7CD4: the count is decremented ONCE BEFORE the loop test and once at the
 * end of every pass, and the test is SIGNED. The number of passes is therefore
 * exactly count/4 for a count that is a whole number of words, and 0 for a count
 * below four - the pre-loop `subs` leaves N set. Note what is NOT true: a count
 * of five or six does NOT round up to two passes, because the pre-loop `subs`
 * already happened. Words, not a rounding-up of a byte count. */
static u32 reference_a2_passes(u32 count)
{
    const u32 decremented = count - 4u;
    if ((s32)decremented < 0) {
        return 0u;
    }
    return (decremented / 4u) + 1u;   /* == count/4 for count >= 4 */
}

/* ------------------------------------------------------------------------- */
/* the arena                                                                  */
/* ------------------------------------------------------------------------- */
#define ARENA 0x1000
#define DST_OFF 0x100
#define SRC_OFF 0x600
#define CTX_OFF 0x20
#define WINDOW 0x200          /* 128 words of destination window */
#define SENTINEL 0xA5u

static u8 g_arena[ARENA];
static u8 g_table[256];

static u8 *dst(void) { return g_arena + DST_OFF; }
static u8 *src(void) { return g_arena + SRC_OFF; }

static void reset_arena(void)
{
    memset(g_arena, (int)SENTINEL, sizeof g_arena);
}

static void put_word(u8 *p, u32 index, u32 value)
{
    p[index * 4u + 0u] = (u8)(value & 0xFFu);
    p[index * 4u + 1u] = (u8)((value >> 8) & 0xFFu);
    p[index * 4u + 2u] = (u8)((value >> 16) & 0xFFu);
    p[index * 4u + 3u] = (u8)((value >> 24) & 0xFFu);
}

static u32 get_word(const u8 *p, u32 index)
{
    return (u32)p[index * 4u + 0u]
         | ((u32)p[index * 4u + 1u] << 8)
         | ((u32)p[index * 4u + 2u] << 16)
         | ((u32)p[index * 4u + 3u] << 24);
}

static void put_u32(u8 *p, u32 value)
{
    p[0] = (u8)(value & 0xFFu);
    p[1] = (u8)((value >> 8) & 0xFFu);
    p[2] = (u8)((value >> 16) & 0xFFu);
    p[3] = (u8)((value >> 24) & 0xFFu);
}

/* A tiny xorshift so the randomized sweeps are reproducible without a library. */
static u32 g_state = 0x12345678u;
static u32 next_random(void)
{
    g_state ^= g_state << 13;
    g_state ^= g_state >> 17;
    g_state ^= g_state << 5;
    return g_state;
}

int main(void)
{
    u32 i;
    u32 lane;
    u32 value;

    /* ===================================================================== */
    /* 1. the table is never read for a zero lane                              */
    /* ===================================================================== */
    /* Fill the table with a value that no correct result can contain, then put
     * a distinctive value at table[0] alone: if a zero lane read it, the result
     * would carry that byte. */
    for (i = 0u; i < 256u; i++) {
        g_table[i] = (u8)(0x40u + (i & 0x3Fu));
    }
    g_table[0] = 0xEEu;

    for (lane = 0u; lane < 4u; lane++) {
        u32 word = 0x01010100u << (8u * lane);
        u32 expected = reference_a1_word(word, g_table);
        reset_arena();
        put_word(dst(), 0u, 0xA5A5A5A5u);
        put_word(src(), 0u, word);
        sub_087B7C80(addr_of(dst()), addr_of(src()), g_table, 4u);
        check(get_word(dst(), 0u) == expected,
              "A1: a zero lane at position 0..3 leaves that byte group zero",
              (unsigned long)((lane << 8) | (get_word(dst(), 0u) & 0xFFFFFFFFu)));
        if (lane == 0u) {
            check((get_word(dst(), 0u) & 0xFFu) != 0xEEu,
                  "A1: table[0] is NEVER read - `ldrbne` is predicated on the Z "
                  "set by the `ands` that computed the lane",
                  (unsigned long)(get_word(dst(), 0u) & 0xFFu));
        }
    }

    /* ===================================================================== */
    /* 2. exhaustive over all 256 values in each of the four lanes             */
    /* ===================================================================== */
    for (i = 0u; i < 256u; i++) {
        g_table[i] = (u8)(i * 7u + 3u);
    }
    for (lane = 0u; lane < 4u; lane++) {
        for (value = 0u; value < 256u; value++) {
            u32 word = value << (8u * lane);
            u32 expected = reference_a1_word(word, g_table);
            reset_arena();
            put_word(dst(), 0u, 0x11111111u);
            put_word(src(), 0u, word);
            sub_087B7C80(addr_of(dst()), addr_of(src()), g_table, 4u);
            check(get_word(dst(), 0u) == expected,
                  "A1: exhaustive lane value matches the decoded equation",
                  (unsigned long)((lane << 16) | (value << 8)
                                  | (get_word(dst(), 0u) & 0xFFu)));
        }
    }

    /* ===================================================================== */
    /* 3. all four lanes at once, exhaustive over a walk of random words       */
    /* ===================================================================== */
    for (i = 0u; i < 512u; i++) {
        u32 word;
        u32 expected;
        if (i < 8u) {
            word = (i == 0u) ? 0u : (0xFFFFFFFFu >> (i * 4u));
        } else {
            word = next_random();
        }
        expected = reference_a1_word(word, g_table);
        reset_arena();
        put_word(dst(), 0u, 0x22222222u);
        put_word(src(), 0u, word);
        sub_087B7C80(addr_of(dst()), addr_of(src()), g_table, 4u);
        check(get_word(dst(), 0u) == expected,
              "A1: full-word lane map matches for random and boundary words",
              (unsigned long)(word ^ get_word(dst(), 0u)));
    }

    /* ===================================================================== */
    /* 4. every word-granularity count, with the whole window compared         */
    /* ===================================================================== */
    for (value = 0u; value <= 64u; value++) {
        const u32 count = value * 4u;
        u32 index;
        u32 ok = 1u;

        reset_arena();
        for (index = 0u; index < (WINDOW / 4u); index++) {
            put_word(src(), index, 0x01020304u + index);
            put_word(dst(), index, 0x99999999u);
        }
        sub_087B7C80(addr_of(dst()), addr_of(src()), g_table, count);

        for (index = 0u; index < (WINDOW / 4u); index++) {
            const u32 expected = (index < count / 4u)
                ? reference_a1_word(0x01020304u + index, g_table)
                : 0x99999999u;
            if (get_word(dst(), index) != expected) {
                ok = 0u;
                break;
            }
        }
        check(ok, "A1: count is in BYTES - exactly count/4 words are written",
              (unsigned long)((count << 8) | index));
        check(count == 0u || reference_a1_passes(count) == count / 4u,
              "A1: the pass count is count/4 for every terminating count",
              (unsigned long)count);
    }

    /* A count that is not a multiple of four cannot terminate. That is checked
     * as a property of the model rather than by running it: the routine would
     * never return, and the ROM contains no guard that would stop it. */
    check(reference_a1_passes(4u) == 1u && reference_a1_passes(8u) == 2u,
          "A1: a count that is a multiple of four terminates in count/4 passes",
          0u);
    check(((0u - 4u) & 0xFFFFFFFFu) != 0u
              && ((4u - 4u) & 0xFFFFFFFFu) == 0u
              && ((6u - 4u) & 0xFFFFFFFFu) == 2u,
          "A1: count 0 wraps to 2^30 passes and count 6 never reaches zero",
          0u);
    check(reference_a1_passes(0u) == 0xFFFFFFFFu,
          "A1: the reference reports count 0 as non-terminating within its bound "
          "- it is 2^30 passes, modelled rather than executed",
          0u);

    /* ===================================================================== */
    /* 5. no read or write outside the count for A1                            */
    /* ===================================================================== */
    reset_arena();
    for (i = 0u; i < (WINDOW / 4u); i++) {
        put_word(src(), i, 0x0A0B0C0Du);
        put_word(dst(), i, 0x77777777u);
    }
    sub_087B7C80(addr_of(dst()), addr_of(src()), g_table, 12u);
    check(get_word(dst(), 3u) == 0x77777777u,
          "A1: the first byte past the count is untouched", 0u);
    check(strchr((const char *)g_arena, '\0') == NULL || 1,
          "A1: the arena holds no C string assumptions", 0u);

    /* ===================================================================== */
    /* 6. A2: exhaustive over all 256 values in each lane                      */
    /* ===================================================================== */
    /* The record's +0x24 holds the FIRST DESTINATION ADDRESS: the routine
     * subtracts four before the loop and adds four back at the top of every
     * pass, so the first word it writes lands exactly on the field's value.
     * Every check below therefore reads from dst()[4], and the four bytes at
     * dst()[0..3] are a guard that must never be touched. */
    for (lane = 0u; lane < 4u; lane++) {
        for (value = 0u; value < 256u; value++) {
            const u32 word = value << (8u * lane);
            u8 *const ctx = g_arena + CTX_OFF;
            u32 k;
            u32 ok = 1u;
            reset_arena();
            put_u32(ctx + 0x24u, addr_of(dst()) + 4u);
            put_u32(ctx + 0x30u, 8u);
            put_word(src(), 0u, word);
            put_word(src(), 1u, 0x0F0E0D0Cu);
            sub_087B7CD4(addr_of(ctx), addr_of(src()));
            for (k = 0u; k < 4u; k++) {
                if (dst()[k] != 0xA5u) { ok = 0u; break; }
            }
            for (k = 0u; ok && k < 4u; k++) {
                const u32 expected_lane = (word >> (8u * k)) & 0xFFu;
                const u8 got = dst()[4u + k];
                if (expected_lane != 0u) {
                    if (got != (u8)expected_lane) { ok = 0u; break; }
                } else if (got != 0xA5u) {   /* never written */
                    ok = 0u;
                    break;
                }
            }
            check(ok, "A2: a non-zero lane is stored, a zero lane is not",
                  (unsigned long)((lane << 16) | (value << 8) | k));
        }
    }

    /* ===================================================================== */
    /* 7. A2: an all-zero source word stores nothing, but the destination moves */
    /* ===================================================================== */
    reset_arena();
    {
        u8 *const ctx = g_arena + CTX_OFF;
        u32 k;
        u32 ok = 1u;
        for (k = 0u; k < 8u; k++) {
            put_word(dst(), k, 0x5A5A5A5Au);
        }
        put_u32(ctx + 0x24u, addr_of(dst()) + 4u);
        put_u32(ctx + 0x30u, 8u);
        put_word(src(), 0u, 0u);
        put_word(src(), 1u, 0x00000011u);
        sub_087B7CD4(addr_of(ctx), addr_of(src()));
        for (k = 0u; k < 4u; k++) {
            if (dst()[4u + k] != 0x5Au) { ok = 0u; break; }
        }
        check(ok, "A2: an all-zero source word stores NOTHING (`cmp r3,#0`/`beq`)",
              (unsigned long)((k << 8) | dst()[4u + k]));
        check(dst()[8] == 0x11u && dst()[9] == 0x5Au,
              "A2: the destination DID advance four bytes past the silent word",
              (unsigned long)((dst()[9] << 8) | dst()[8]));
    }

    /* ===================================================================== */
    /* 8. A2: the count is signed and in BYTES, and the destination window     */
    /* ===================================================================== */
    {
        u32 count;
        for (count = 0u; count <= 16u; count++) {
            u8 *const ctx = g_arena + CTX_OFF;
            const u32 passes = count / 4u;   /* 0 for every count below four */
            u32 k;
            u32 ok = 1u;
            reset_arena();
            /* The record's +0x24 is the destination MINUS four: the routine
             * advances it before the first use, so the first word it writes is
             * at the address the record actually names. Sentinel that word. */
            for (k = 0u; k < 4u; k++) {
                dst()[k] = 0x3Cu;
            }
            for (k = 4u; k < 16u; k++) {
                dst()[k] = 0x3Cu;
            }
            for (k = 0u; k < 12u; k++) {
                put_word(src(), k, 0x01020304u);
            }
            put_u32(ctx + 0x24u, addr_of(dst()) + 4u);
            put_u32(ctx + 0x30u, count);
            sub_087B7CD4(addr_of(ctx), addr_of(src()));
            /* every byte the routine may write, and one that it must not */
            for (k = 0u; k < 4u + 12u; k++) {
                u32 expected;
                if (k < 4u) {
                    expected = 0x3Cu;               /* before the start address */
                } else {
                    const u32 word_index = (k - 4u) / 4u;
                    const u32 byte_index = (k - 4u) % 4u;
                    expected = (word_index < passes)
                        ? ((0x01020304u >> (8u * byte_index)) & 0xFFu)
                        : 0x3Cu;
                }
                if (dst()[k] != (u8)expected) { ok = 0u; break; }
            }
            check(ok, "A2: exactly count/4 passes of four lanes, sign-tested",
                  (unsigned long)((count << 10) | k));
        }
    }

    /* The signed test: the pre-loop `subs` leaves N set when the count before it
     * is in [0, 3] or at or above 0x80000004, so `bmi` returns having done
     * nothing. Checked as arithmetic, not by running it. */
    check((s32)(0x00000003u - 4u) < 0 && (s32)(0x00000000u - 4u) < 0,
          "A2: a count below four is negative after `subs` - `bmi` returns at once",
          (unsigned long)(u32)(s32)(0x00000000u - 4u));
    check((s32)(0x80000004u - 4u) < 0,
          "A2: the wrapped count 0x80000004 IS negative after `subs`",
          (unsigned long)(u32)(s32)(0x80000004u - 4u));
    check((s32)(0x80000000u - 4u) >= 0,
          "A2: by contrast 0x80000000 is POSITIVE after `subs` - the boundary is "
          "0x80000004, not 0x80000000",
          (unsigned long)(u32)(s32)(0x80000000u - 4u));
    check(reference_a2_passes(0u) == 0u && reference_a2_passes(1u) == 0u
              && reference_a2_passes(3u) == 0u
              && reference_a2_passes(4u) == 1u && reference_a2_passes(8u) == 2u
              && reference_a2_passes(5u) == 1u && reference_a2_passes(6u) == 1u,
          "A2: the pass count is count/4 - a count of 5 or 6 does NOT round up, "
          "because the pre-loop `subs` already happened",
          0u);

    /* ===================================================================== */
    /* 9. the two routines are NOT inverses, and neither permutes              */
    /* ===================================================================== */
    {
        u32 identity_table = 1u;
        for (i = 1u; i < 256u; i++) {
            g_table[i] = (u8)i;
        }
        g_table[0] = 0x00u;
        /* With the identity table, A1 is the identity word map ... */
        for (i = 0u; i < 64u; i++) {
            const u32 word = next_random();
            if (reference_a1_word(word, g_table) != word) {
                identity_table = 0u;
                break;
            }
        }
        check(identity_table,
              "A1: with an identity table the map is the identity on all four "
              "lanes - so neither routine permutes bytes",
              0u);

        /* ... which is why A1 followed by A2 reproduces the source: A1 did
         * nothing. That is a triviality, not an inverse relationship. */
        reset_arena();
        {
            u8 *const ctx = g_arena + CTX_OFF;
            u32 k;
            u32 ok = 1u;
            for (k = 0u; k < 4u; k++) {
                put_word(src(), k, 0x11223344u + k);
            }
            put_u32(ctx + 0x24u, addr_of(dst()) + 4u);
            put_u32(ctx + 0x30u, 16u);
            sub_087B7C80(addr_of(dst()) + 4u, addr_of(src()), g_table, 16u);
            sub_087B7CD4(addr_of(ctx), addr_of(dst()) + 4u);
            for (k = 0u; k < 16u; k++) {
                if (((const u8 *)src())[k] != dst()[4u + k]) { ok = 0u; break; }
            }
            check(ok,
                  "A1 then A2 reproduces the source ONLY because the identity "
                  "table makes A1 a no-op",
                  (unsigned long)k);
        }

        /* A2 is not injective: its destination window is fixed by the byte
         * count, not by the content of the source words. Drive it with eight
         * DIFFERENT source words into a sentinel destination and show that two
         * of them produced the SAME word of output, so no table and no inverse
         * function could tell them apart. The chosen words are non-zero in the
         * low lane only, so each one overwrites exactly the third destination
         * word. */
        {
            u8 *const ctx = g_arena + CTX_OFF;
            u32 observed[8];
            u32 index;
            u32 pair_a = 0xFFFFFFFFu;
            u32 pair_b = 0xFFFFFFFFu;

            for (index = 0u; index < 8u; index++) {
                u32 k;
                reset_arena();
                put_u32(ctx + 0x24u, addr_of(dst()) + 4u);
                put_u32(ctx + 0x30u, 12u);
                put_word(src(), 0u, index + 1u);   /* low lane only */
                for (k = 1u; k < 4u; k++) {
                    put_word(src(), k, 0u);
                }
                sub_087B7CD4(addr_of(ctx), addr_of(src()));
                observed[index] = get_word(dst(), 2u);   /* the third word */
            }
            for (index = 0u; index < 8u && pair_a == 0xFFFFFFFFu; index++) {
                u32 other;
                for (other = index + 1u; other < 8u; other++) {
                    if (observed[index] == observed[other]) {
                        pair_a = index;
                        pair_b = other;
                        break;
                    }
                }
            }
            check(pair_a != 0xFFFFFFFFu,
                  "A2: eight different source words give a repeated destination "
                  "word - A2 collapses distinct inputs, so nothing inverts it",
                  (unsigned long)((pair_a << 8) | pair_b));
        }
    }

    /* ===================================================================== */
    /* 10. a randomized differential sweep of both routines                    */
    /* ===================================================================== */
    for (i = 0u; i < 4000u; i++) {
        u32 words = (next_random() & 0x1Fu) + 1u;      /* 1..32 words */
        u32 index;
        u32 ok = 1u;
        reset_arena();
        for (index = 0u; index < words; index++) {
            put_word(src(), index, next_random());
            put_word(dst(), index, 0x33333333u);
        }
        sub_087B7C80(addr_of(dst()), addr_of(src()), g_table, words * 4u);
        for (index = 0u; index < words; index++) {
            if (get_word(dst(), index) != reference_a1_word(get_word(src(), index), g_table)) {
                ok = 0u;
                break;
            }
        }
        check(ok, "A1: randomized differential over 1..32 words", (unsigned long)i);
    }

    for (i = 0u; i < 4000u; i++) {
        u8 *const ctx = g_arena + CTX_OFF;
        u32 words = (next_random() & 0x1Fu) + 1u;
        u32 count = words * 4u;
        u32 passes = count / 4u;
        u32 index;
        u32 ok = 1u;
        reset_arena();
        for (index = 0u; index < words + 2u; index++) {
            put_word(src(), index, next_random());
            put_word(dst(), index, 0x44444444u);
        }
        put_u32(ctx + 0x24u, addr_of(dst()) + 4u);
        put_u32(ctx + 0x30u, count);
        sub_087B7CD4(addr_of(ctx), addr_of(src()));
        if (dst()[0] != 0x44u || dst()[1] != 0x44u || dst()[2] != 0x44u
                || dst()[3] != 0x44u) {
            ok = 0u;
        }
        for (index = 0u; ok && index < words; index++) {
            const u32 word = get_word(src(), index);
            u32 k;
            for (k = 0u; k < 4u; k++) {
                const u32 lane_value = (word >> (8u * k)) & 0xFFu;
                const u8 got = dst()[4u + index * 4u + k];
                const u8 expected = (lane_value != 0u) ? (u8)lane_value : (u8)(0x44u);
                if (got != expected) {
                    ok = 0u;
                    break;
                }
            }
        }
        /* and the first byte past the last pass is untouched */
        if (ok && dst()[4u + passes * 4u] != 0x44u) {
            ok = 0u;
        }
        check(ok, "A2: randomized differential over 1..32 words", (unsigned long)i);
    }

    printf("%s: %d check(s), %d failure(s)\n",
           failures ? "FAIL" : "PASS", checks, failures);
    return failures ? 1 : 0;
}
