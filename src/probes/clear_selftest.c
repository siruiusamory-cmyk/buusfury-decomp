/*
 * src/probes/clear_selftest.c
 *
 * HOST SEMANTIC CHECK for sub_08004396, the clearer of the flag array.
 *
 * Built 32-bit: the addressing is 32-bit and the negative-index case depends on
 * the wrap.
 */

#include <stdio.h>
#include <string.h>

#include "ByteCodeInterpreter_clear.c"

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

#define PRE 64
#define BODY 256
#define POST 64

static u8 g_arena[PRE + BODY + POST];
#define OBJECT (g_arena + PRE)

static void reset_arena(void)
{
    memset(g_arena, 0, sizeof(g_arena));
}

static u8 *byte_for(u32 value)
{
    u32 index = (value & 0x80000000u) ? ((value >> 3) | 0xE0000000u) : (value >> 3);
    return (u8 *)((u32)OBJECT + index + 0x50u) + 5u;
}

int main(void)
{
    /* ---- 1. it clears exactly one bit -------------------------------- */
    reset_arena();
    *byte_for(0u) = 0xFFu;
    sub_08004396(OBJECT, 0u);
    check(*byte_for(0u) == 0xFEu, "clearing bit 0 leaves 0xFE", (unsigned long)*byte_for(0u));

    reset_arena();
    *byte_for(7u) = 0xFFu;
    sub_08004396(OBJECT, 7u);
    check(*byte_for(7u) == 0x7Fu, "clearing bit 7 leaves 0x7F", (unsigned long)*byte_for(7u));

    reset_arena();
    *byte_for(3u) = 0xFFu;
    sub_08004396(OBJECT, 3u);
    check(*byte_for(3u) == 0xF7u, "clearing bit 3 leaves 0xF7", (unsigned long)*byte_for(3u));

    /* ---- 2. the other seven bits are preserved ----------------------- */
    {
        u32 bit;
        int bad = 0;
        for (bit = 0u; bit < 8u; bit++) {
            reset_arena();
            *byte_for(0u) = 0xA5u;
            sub_08004396(OBJECT, bit);
            if (*byte_for(0u) != (u8)(0xA5u & ~(1u << bit))) {
                bad++;
            }
        }
        check(bad == 0, "each of the eight bits clears independently and the rest survive",
              (unsigned long)bad);
    }

    /* ---- 3. clearing twice, or an already-clear bit, is a no-op ------- */
    reset_arena();
    *byte_for(2u) = 0x00u;
    sub_08004396(OBJECT, 2u);
    check(*byte_for(2u) == 0x00u, "clearing an already-clear bit changes nothing",
          (unsigned long)*byte_for(2u));

    reset_arena();
    *byte_for(2u) = 0xFFu;
    sub_08004396(OBJECT, 2u);
    sub_08004396(OBJECT, 2u);
    check(*byte_for(2u) == 0xFBu, "clearing the same bit twice equals clearing it once",
          (unsigned long)*byte_for(2u));

    /* ---- 4. it writes exactly one byte -------------------------------- */
    {
        u8 before[BODY];
        int changed = 0;
        int i;
        reset_arena();
        memset(OBJECT, 0xFF, BODY);
        memcpy(before, OBJECT, BODY);
        sub_08004396(OBJECT, 9u);        /* byte 1 */
        for (i = 0; i < BODY; i++) {
            if (OBJECT[i] != before[i]) {
                changed++;
            }
        }
        check(changed == 1, "exactly one byte of the body is modified", (unsigned long)changed);
        check(OBJECT[0x55 + 1] == 0xFDu, "and it is the byte the index arithmetic names",
              (unsigned long)OBJECT[0x56]);
    }

    /* ---- 5. the byte index is value >> 3 and the bit is value & 7 ----- */
    {
        u32 value;
        int bad = 0;
        for (value = 0u; value < 512u; value++) {
            reset_arena();
            *byte_for(value) = 0xFFu;
            sub_08004396(OBJECT, value);
            if (*byte_for(value) != (u8)~(1u << (value & 7u))) {
                bad++;
            }
        }
        check(bad == 0, "every value in 0..511 cleared exactly the bit predicted",
              (unsigned long)bad);
    }

    /* ---- 6. byte boundaries ------------------------------------------- */
    reset_arena();
    *byte_for(7u) = 0x80u;
    *byte_for(8u) = 0x01u;
    sub_08004396(OBJECT, 7u);
    check(*byte_for(7u) == 0x00u, "the last bit of one byte clears", (unsigned long)*byte_for(7u));
    check(*byte_for(8u) == 0x01u, "and the next byte is untouched", (unsigned long)*byte_for(8u));
    sub_08004396(OBJECT, 8u);
    check(*byte_for(8u) == 0x00u, "then its own bit 0 clears", (unsigned long)*byte_for(8u));

    /* ---- 7. the byte-index shift is ARITHMETIC ------------------------ */
    reset_arena();
    *(OBJECT + 0x54u) = 0x80u;
    sub_08004396(OBJECT, 0xFFFFFFFFu);
    check(*(OBJECT + 0x54u) == 0x00u,
          "0xFFFFFFFF clears at object+0x54, one byte BEFORE the unsigned position", 0ul);
    check(byte_for(0xFFFFFFFFu) == OBJECT + 0x54u, "the address arithmetic agrees",
          (unsigned long)(byte_for(0xFFFFFFFFu) - OBJECT));
    check(byte_for(0x80000000u) != OBJECT + 0x10000055u,
          "0x80000000 does NOT use the logical-shift index", 0ul);

    /* ---- 8. no bounds check -------------------------------------------- */
    /* A value whose byte lies past the body is written without any test. The
     * arena is large enough to observe it rather than fault on it. */
    reset_arena();
    sub_08004396(OBJECT, 0x600u);        /* byte index 0x C0 -> OBJECT + 0x115 */
    check((unsigned long)(byte_for(0x600u) - OBJECT) >= (unsigned long)BODY,
          "0x600 targets a byte past the body", (unsigned long)(byte_for(0x600u) - OBJECT));
    check(byte_for(0x600u) < g_arena + sizeof(g_arena), "and the arena can see it",
          (unsigned long)(byte_for(0x600u) - g_arena));
    check(*byte_for(0x600u) == 0x00u, "which was modified", (unsigned long)*byte_for(0x600u));

    printf("%s: %d check(s), %d failure(s)\n",
           failures ? "FAIL" : "PASS", checks, failures);
    return failures ? 1 : 0;
}
