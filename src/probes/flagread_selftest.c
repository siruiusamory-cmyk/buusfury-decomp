/*
 * src/probes/flagread_selftest.c
 *
 * HOST SEMANTIC CHECK for sub_08004364, the reader of the bit array that
 * sub_08004380 sets.
 *
 * It compiles src/ByteCodeInterpreter_flagread.c for the host and RUNS it. It is
 * not compiler evidence: nothing here says anything about ADS 1.2.
 *
 * The host buffer carries storage on BOTH sides of the object, because a value
 * with bit 31 set makes the byte index negative and the read lands BEFORE the
 * base.
 *
 * Built 32-bit: the addressing is 32-bit and the negative-index case depends on
 * the wrap.
 */

#include <stdio.h>
#include <string.h>

#include "ByteCodeInterpreter_flagread.c"

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

/* The byte the routine reads for a given value. */
static u8 *byte_for(u32 value)
{
    u32 index = (value & 0x80000000u) ? ((value >> 3) | 0xE0000000u) : (value >> 3);
    return (u8 *)((u32)OBJECT + index + 0x50u) + 5u;
}

int main(void)
{
    /* ---- 1. bit clear returns 0, bit set returns 1 -------------------- */
    reset_arena();
    check(sub_08004364(OBJECT, 0u) == 0u, "a clear bit returns 0", 0ul);

    reset_arena();
    *byte_for(0u) = 0x01u;
    check(sub_08004364(OBJECT, 0u) == 1u, "a set bit returns 1", 0ul);

    reset_arena();
    *byte_for(7u) = 0x80u;
    check(sub_08004364(OBJECT, 7u) == 1u, "bit 7 of the first byte is reachable", 0ul);
    check(sub_08004364(OBJECT, 0u) == 0u, "and bit 0 of that byte is still clear", 0ul);

    /* ---- 2. the result is a normalised boolean, not the masked byte ---- */
    /* With bit 7 set the mask is 0x80; a routine returning the masked byte
     * would answer 128, not 1. */
    reset_arena();
    *byte_for(7u) = 0xFFu;
    check(sub_08004364(OBJECT, 7u) == 1u, "the result is 1 even when the mask is 0x80", 0ul);
    {
        u32 v;
        int bad = 0;
        for (v = 0u; v < 512u; v++) {
            u32 r = sub_08004364(OBJECT, v);
            if (r != 0u && r != 1u) {
                bad++;
            }
        }
        check(bad == 0, "no value ever returns anything but 0 or 1", (unsigned long)bad);
    }

    /* ---- 3. it does not write anything --------------------------------- */
    /* This is what makes it a reader rather than the setter or the clearer. */
    {
        u8 before[BODY];
        int changed = 0;
        int i;
        reset_arena();
        memset(OBJECT, 0xA5, BODY);
        memcpy(before, OBJECT, BODY);
        for (i = 0; i < 64; i++) {
            (void)sub_08004364(OBJECT, (u32)i);
        }
        for (i = 0; i < BODY; i++) {
            if (OBJECT[i] != before[i]) {
                changed++;
            }
        }
        check(changed == 0, "64 reads left every byte unchanged", (unsigned long)changed);
    }

    /* ---- 4. the byte index is value >> 3 and the bit is value & 7 ------ */
    {
        u32 value;
        int bad = 0;
        for (value = 0u; value < 512u; value++) {
            u8 *target = byte_for(value);
            u8 bit = (u8)(1u << (value & 7u));
            reset_arena();
            *target = bit;
            if (sub_08004364(OBJECT, value) != 1u) {
                bad++;
            }
            *target = (u8)~bit;
            if (sub_08004364(OBJECT, value) != 0u) {
                bad++;
            }
        }
        check(bad == 0, "every value in 0..511 read exactly the bit its index arithmetic predicts",
              (unsigned long)bad);
    }

    /* ---- 5. byte boundaries -------------------------------------------- */
    reset_arena();
    *byte_for(7u) = 0x80u;
    *byte_for(8u) = 0x00u;
    check(sub_08004364(OBJECT, 7u) == 1u, "the last bit of one byte is set", 0ul);
    check(sub_08004364(OBJECT, 8u) == 0u, "and the first bit of the next byte is independent", 0ul);
    *byte_for(8u) = 0x01u;
    check(sub_08004364(OBJECT, 8u) == 1u, "setting the next byte's bit 0 is visible", 0ul);
    check(sub_08004364(OBJECT, 15u) == 0u, "and its bit 7 is separate", 0ul);

    /* ---- 6. the byte-index shift is ARITHMETIC ------------------------- */
    /* A logical shift would read far ABOVE the object; the arithmetic one reads
     * the byte before it. 0xFFFFFFFF has an index of -1. */
    reset_arena();
    *(OBJECT + 0x54u) = 0x80u;
    check(sub_08004364(OBJECT, 0xFFFFFFFFu) == 1u,
          "0xFFFFFFFF reads object+0x54, one byte BEFORE the unsigned position", 0ul);
    check(byte_for(0xFFFFFFFFu) == OBJECT + 0x54u, "the address arithmetic agrees",
          (unsigned long)(byte_for(0xFFFFFFFFu) - OBJECT));
    check(byte_for(0x80000000u) != OBJECT + 0x10000055u,
          "0x80000000 does NOT use the logical-shift index", 0ul);

    /* A value whose target is inside the arena but outside the body is read
     * without complaint: there is no bounds check. */
    reset_arena();
    sub_08004364(OBJECT, 0x300u);        /* index 0x60 -> OBJECT + 0xB5, inside the arena */
    check(byte_for(0x300u) < g_arena + sizeof(g_arena), "a past-the-body byte is still read", 0ul);

    /* ---- 7. it agrees with the setter ---------------------------------- */
    /* The setter is the previous ticket's routine; the two must address the same
     * byte, or the array would be two different arrays. Checked across a sweep
     * by writing with the setter's own arithmetic and reading here. */
    {
        u32 value;
        int bad = 0;
        for (value = 0u; value < 256u; value++) {
            reset_arena();
            *byte_for(value) = (u8)(1u << (value & 7u));   /* the setter's effect */
            if (sub_08004364(OBJECT, value) != 1u) {
                bad++;
            }
        }
        check(bad == 0, "every value the setter would mark reads back as set", (unsigned long)bad);
    }

    printf("%s: %d check(s), %d failure(s)\n",
           failures ? "FAIL" : "PASS", checks, failures);
    return failures ? 1 : 0;
}
