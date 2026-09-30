/*
 * src/probes/iwramblock_selftest.c
 *
 * HOST SEMANTIC CHECK for the four runtime-installed block routines in
 * src/IwramBlock.c.
 *
 * Every check runs against a sentinel-filled arena, so the test measures not
 * only WHAT the routines copy but HOW MANY BYTES they touch. The byte counts
 * below are computed BY HAND from the ARM instructions - not from the
 * reconstruction - so an off-by-one in the reconstruction fails a check rather
 * than being mirrored by one.
 *
 * The source region is filled with a pattern whose values are all below 0x80
 * and the sentinel is 0xA5, so no copied byte can be mistaken for an untouched
 * one; a self-check asserts that property of the pattern rather than assuming
 * it.
 *
 * The behaviours this exists to pin, because each is the kind of thing a
 * "tidier" reconstruction gets wrong:
 *
 *   * the sizes are BYTES for all four routines, including the 2-byte pair;
 *   * the tail is entered by a SIZED compare, so it RUNS AT LEAST ONCE:
 *     0x087B810C/0x087B814C store 4 bytes at size 0, 0x087B81FC stores 2, and
 *     0x087B81A0's own dispatch entry cannot produce fewer than eight halfwords;
 *   * sizes that are not a whole number of units are ROUNDED UP;
 *   * 0x087B814C writes the WHOLE 32-bit r1. Masking it to a byte would turn
 *     0xDEADBEEF into 0xEFEFEFEF and is a defect, not a sanitisation;
 *   * no zero-size guard and no alignment guard is added.
 *
 * Built 32-bit: the routines model a 32-bit address space and the host passes
 * real pointers through u32 arguments.
 */

#include <stdio.h>
#include <string.h>

typedef unsigned int u32;
typedef unsigned char u8;

#include "IwramBlock.c"

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
/* the arena                                                                  */
/* ------------------------------------------------------------------------- */
#define ARENA 0x800
#define DST_OFF 0x100
#define SRC_OFF 0x400
#define MAX_SRC (ARENA - SRC_OFF)
#define SENTINEL 0xA5u

static u8 g_arena[ARENA];

static u8 *dst(void) { return g_arena + DST_OFF; }
static u8 *src(void) { return g_arena + SRC_OFF; }
static u32 dst_addr(void) { return (u32)(unsigned long)dst(); }
static u32 src_addr(void) { return (u32)(unsigned long)src(); }

static void reset_arena(void)
{
    u32 i;
    memset(g_arena, SENTINEL, sizeof(g_arena));
    /* Values 0..0x7F only, so a copied byte is never the sentinel 0xA5. */
    for (i = 0u; i < MAX_SRC; i++) {
        src()[i] = (u8)(i & 0x7Fu);
    }
}

/* The offset of the first byte the routine did NOT write. Independent of what
 * the routine claims: it is a scan of the arena for the sentinel byte. */
static u32 first_untouched(void)
{
    u32 i;
    for (i = 0u; i < ARENA - DST_OFF; i++) {
        if (dst()[i] == (u8)SENTINEL) {
            return i;
        }
    }
    return ARENA - DST_OFF;
}

/* ------------------------------------------------------------------------- */
/* byte counts computed BY HAND from the ARM instructions                      */
/* ------------------------------------------------------------------------- */
#define EXPECTED 16
static const u32 N[EXPECTED]     = { 0, 1, 2, 3, 4, 5, 7, 8, 16, 31, 32, 33, 63, 64, 65, 100 };
/* 0x087B810C / 0x087B814C: 32-byte fast path, then ceil(remaining/4) words. */
static const u32 CW_BYTES[EXPECTED] = { 4, 4, 4, 4, 4, 8, 8, 8, 16, 32, 32, 36, 64, 64, 68, 100 };
/* 0x087B81A0: 16-byte passes; the first moves 8 - ((16 - n) & 0xE)/2 halfwords,
 * so the count is rounded UP to an even number. */
static const u32 H2_BYTES[EXPECTED] = { 16, 2, 2, 4, 4, 6, 8, 8, 16, 32, 32, 34, 64, 64, 66, 100 };
/* 0x087B81FC: ceil(n/2) halfwords, at least one. */
static const u32 F2_BYTES[EXPECTED] = { 2, 2, 2, 4, 4, 6, 8, 8, 16, 32, 32, 34, 64, 64, 66, 100 };

static void bytes_of(u32 value, u8 *out, u32 width)
{
    u32 i;
    for (i = 0u; i < width; i++) {
        out[i] = (u8)(value >> (8u * i));
    }
}

int main(void)
{
    int k;
    u32 i;

    setvbuf(stdout, NULL, _IONBF, 0);

    /* ---- 0. the sentinel is not a value the source pattern can produce ---- */
    reset_arena();
    for (i = 0u; i < MAX_SRC; i++) {
        if (src()[i] == (u8)SENTINEL) {
            break;
        }
    }
    check(i == MAX_SRC,
          "the source pattern never contains the sentinel byte",
          (unsigned long)i);

    /* ===================================================================== */
    /* 1. the 4-byte copy: exact payload, exact extent                        */
    /* ===================================================================== */
    for (k = 0; k < EXPECTED; k++) {
        u32 n = N[k];
        reset_arena();
        sub_087B810C(dst_addr(), src_addr(), n);
        check(first_untouched() == CW_BYTES[k],
              "copy: written byte count matches the hand-computed ARM value",
              (unsigned long)((k << 16) | first_untouched()));
        for (i = 0u; i < CW_BYTES[k]; i++) {
            if (dst()[i] != src()[i]) {
                break;
            }
        }
        check(i == CW_BYTES[k],
              "copy: every written byte equals the source byte",
              (unsigned long)((k << 16) | i));
    }

    reset_arena();
    sub_087B810C(dst_addr(), src_addr(), 5u);
    check(first_untouched() == 8u,
          "copy: 5 bytes is rounded UP to 8, it is not truncated to 5",
          (unsigned long)first_untouched());
    reset_arena();
    sub_087B810C(dst_addr(), src_addr(), 0u);
    check(first_untouched() == 4u,
          "copy: size 0 still moves one word - the tail has NO zero guard",
          (unsigned long)first_untouched());
    check(dst()[0] == src()[0] && dst()[3] == src()[3],
          "copy: and the word it moves comes from the source",
          (unsigned long)dst()[0]);
    reset_arena();
    sub_087B810C(dst_addr(), src_addr(), 32u);
    check(first_untouched() == 32u, "copy: size 32 writes exactly 32 bytes",
          (unsigned long)first_untouched());
    reset_arena();
    sub_087B810C(dst_addr(), src_addr(), 31u);
    check(first_untouched() == 32u,
          "copy: size 31 takes the TAIL and writes 32 - the two paths agree",
          (unsigned long)first_untouched());

    /* ===================================================================== */
    /* 2. the 4-byte fill: exact extent, and the value is NOT masked          */
    /* ===================================================================== */
    for (k = 0; k < EXPECTED; k++) {
        u32 n = N[k];
        u32 v = 0xDEADBEEFu;
        u8 bytes[4];
        bytes_of(v, bytes, 4u);
        reset_arena();
        sub_087B814C(dst_addr(), v, n);
        check(first_untouched() == CW_BYTES[k],
              "fill: written byte count matches the hand-computed ARM value",
              (unsigned long)((k << 16) | first_untouched()));
        for (i = 0u; i < CW_BYTES[k]; i++) {
            if (dst()[i] != bytes[i & 3u]) {
                break;
            }
        }
        check(i == CW_BYTES[k],
              "fill: every written byte is the matching byte of the WORD",
              (unsigned long)((k << 16) | i));
    }

    reset_arena();
    sub_087B814C(dst_addr(), 0xDEADBEEFu, 8u);
    check(dst()[0] == 0xEFu && dst()[1] == 0xBEu && dst()[2] == 0xADu && dst()[3] == 0xDEu,
          "fill: the 32-bit value is stored whole - it is NOT masked to a byte",
          (unsigned long)((dst()[0] << 24) | (dst()[1] << 16) | (dst()[2] << 8) | dst()[3]));
    reset_arena();
    sub_087B814C(dst_addr(), 0x11111111u, 8u);
    check(dst()[0] == 0x11u && dst()[3] == 0x11u,
          "fill: a byte-replicated value still goes out as a word",
          (unsigned long)dst()[0]);
    reset_arena();
    sub_087B814C(dst_addr(), 0x04030201u, 36u);
    check(dst()[0] == 1u && dst()[1] == 2u && dst()[2] == 3u && dst()[3] == 4u,
          "fill: the fast path stores the value byte for byte",
          (unsigned long)dst()[0]);
    check(dst()[32] == 1u && dst()[35] == 4u,
          "fill: the TAIL stores the same value",
          (unsigned long)dst()[32]);
    reset_arena();
    sub_087B814C(dst_addr(), 0x04030201u, 0u);
    check(first_untouched() == 4u,
          "fill: size 0 still stores one word - no zero guard",
          (unsigned long)first_untouched());

    /* ===================================================================== */
    /* 3. the 2-byte copy: the dispatch entry and the byte-counted passes      */
    /* ===================================================================== */
    for (k = 0; k < EXPECTED; k++) {
        u32 n = N[k];
        reset_arena();
        sub_087B81A0(dst_addr(), src_addr(), n);
        check(first_untouched() == H2_BYTES[k],
              "copy2: written byte count matches the hand-computed ARM value",
              (unsigned long)((k << 16) | first_untouched()));
        for (i = 0u; i < H2_BYTES[k]; i++) {
            if (dst()[i] != src()[i]) {
                break;
            }
        }
        check(i == H2_BYTES[k],
              "copy2: every written byte equals the source byte",
              (unsigned long)((k << 16) | i));
    }

    /* The dispatch must enter at the RIGHT halfword: whatever the size, the
     * first halfword written is the first halfword of the source. */
    for (k = 0; k < 16; k++) {
        reset_arena();
        sub_087B81A0(dst_addr(), src_addr(), (u32)k);
        check(dst()[0] == src()[0] && dst()[1] == src()[1],
              "copy2: the dispatch entry always starts at source offset 0",
              (unsigned long)((k << 8) | dst()[0]));
    }

    reset_arena();
    sub_087B81A0(dst_addr(), src_addr(), 0u);
    check(first_untouched() == 16u,
          "copy2: size 0 still copies EIGHT halfwords - no zero guard",
          (unsigned long)first_untouched());
    reset_arena();
    sub_087B81A0(dst_addr(), src_addr(), 3u);
    check(first_untouched() == 4u,
          "copy2: 3 bytes is rounded UP to two halfwords",
          (unsigned long)first_untouched());
    reset_arena();
    sub_087B81A0(dst_addr(), src_addr(), 17u);
    check(first_untouched() == 18u,
          "copy2: 17 bytes rounds up to 18 and then one more pass runs",
          (unsigned long)first_untouched());
    reset_arena();
    sub_087B81A0(dst_addr(), src_addr(), 32u);
    check(first_untouched() == 32u,
          "copy2: size 32 is two passes of eight halfwords, exactly",
          (unsigned long)first_untouched());

    /* ===================================================================== */
    /* 4. the 2-byte fill: ceil(n/2) halfwords, at least one                   */
    /* ===================================================================== */
    for (k = 0; k < EXPECTED; k++) {
        u32 n = N[k];
        u32 v = 0xBEEF1234u;
        u8 bytes[2];
        bytes_of(v, bytes, 2u);
        reset_arena();
        sub_087B81FC(dst_addr(), v, n);
        check(first_untouched() == F2_BYTES[k],
              "fill2: written byte count matches the hand-computed ARM value",
              (unsigned long)((k << 16) | first_untouched()));
        for (i = 0u; i < F2_BYTES[k]; i++) {
            if (dst()[i] != bytes[i & 1u]) {
                break;
            }
        }
        check(i == F2_BYTES[k],
              "fill2: only the LOW halfword of the value is stored",
              (unsigned long)((k << 16) | i));
    }
    reset_arena();
    sub_087B81FC(dst_addr(), 0xBEEF1234u, 4u);
    check(dst()[0] == 0x34u && dst()[1] == 0x12u,
          "fill2: the stored halfword is the LOW half of r1",
          (unsigned long)((dst()[1] << 8) | dst()[0]));
    check(first_untouched() == 4u, "fill2: size 4 stores exactly two halfwords",
          (unsigned long)first_untouched());
    reset_arena();
    sub_087B81FC(dst_addr(), 0xBEEF1234u, 0u);
    check(first_untouched() == 2u,
          "fill2: size 0 still stores one halfword - no zero guard",
          (unsigned long)first_untouched());
    reset_arena();
    sub_087B81FC(dst_addr(), 0xBEEF1234u, 5u);
    check(first_untouched() == 6u, "fill2: 5 bytes rounds UP to three halfwords",
          (unsigned long)first_untouched());

    /* ===================================================================== */
    /* 5. nothing below the destination is touched, and a big size stops       */
    /* ===================================================================== */
    reset_arena();
    sub_087B810C(dst_addr(), src_addr(), 100u);
    check(g_arena[DST_OFF - 1] == (u8)SENTINEL && g_arena[0] == (u8)SENTINEL,
          "copy: the arena BELOW the destination is untouched",
          (unsigned long)g_arena[DST_OFF - 1]);
    reset_arena();
    sub_087B814C(dst_addr(), 0xDEADBEEFu, 100u);
    check(g_arena[DST_OFF + 100] == (u8)SENTINEL,
          "fill: the first byte past the rounded size is untouched",
          (unsigned long)g_arena[DST_OFF + 100]);

    printf("%s: %d check(s), %d failure(s)\n",
           failures ? "FAIL" : "PASS", checks, failures);
    return failures ? 1 : 0;
}
