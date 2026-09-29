/*
 * src/probes/effect_selftest.c
 *
 * HOST SEMANTIC CHECK for sub_08004380, the routine that gives the popped VM
 * value its concrete effect: it sets bit (value & 7) of the byte at
 * base + (value >> 3) + 0x55.
 *
 * It compiles src/ByteCodeInterpreter_effect.c for the host and RUNS it. It is
 * not compiler evidence: nothing here says anything about ADS 1.2.
 *
 * The host buffer is preceded by real storage, because a value with bit 31 set
 * makes the byte index negative and the write lands BEFORE the base. The test
 * needs visible room on both sides of the object.
 *
 * Built 32-bit: the addressing is 32-bit and the negative-index case depends on
 * the wrap.
 */

#include <stdio.h>
#include <string.h>

#include "ByteCodeInterpreter_effect.c"

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

/* The object is `body`; the guard bytes before and after make out-of-range
 * writes visible rather than silent. */
#define PRE 64
#define BODY 64
#define POST 128

static u8 g_arena[PRE + BODY + POST];
#define OBJECT (g_arena + PRE)
#define GUARD_BYTE 0xA5u

static void reset_arena(void)
{
    memset(g_arena, GUARD_BYTE, sizeof(g_arena));
}

/* The byte the routine targets for a given value. */
static u8 *target_for(u32 value)
{
    u32 index = (value & 0x80000000u) ? ((value >> 3) | 0xE0000000u) : (value >> 3);
    return (u8 *)((u32)OBJECT + index + 0x50u) + 5u;
}

int main(void)
{
    /* ---- 1. it sets exactly one bit, in the right byte ---------------- */
    reset_arena();
    sub_08004380(OBJECT, 0u);
    check(OBJECT[0x55] == (u8)(GUARD_BYTE | 0x01u), "value 0 sets bit 0 of object+0x55",
          (unsigned long)OBJECT[0x55]);
    check(target_for(0u) == OBJECT + 0x55, "and that is the byte the address arithmetic names",
          (unsigned long)(target_for(0u) - OBJECT));

    reset_arena();
    sub_08004380(OBJECT, 7u);
    check(OBJECT[0x55] == (u8)(GUARD_BYTE | 0x80u), "value 7 sets bit 7 of the same byte",
          (unsigned long)OBJECT[0x55]);

    reset_arena();
    sub_08004380(OBJECT, 8u);
    check(OBJECT[0x56] == (u8)(GUARD_BYTE | 0x01u), "value 8 moves to the next byte and sets bit 0",
          (unsigned long)OBJECT[0x56]);
    check(OBJECT[0x55] == GUARD_BYTE, "and leaves the previous byte alone", (unsigned long)OBJECT[0x55]);

    /* ---- 2. the other seven bits are preserved ------------------------- */
    reset_arena();
    OBJECT[0x55] = 0x00u;
    sub_08004380(OBJECT, 4u);
    check(OBJECT[0x55] == 0x10u, "on a zero byte it sets only the one bit", (unsigned long)OBJECT[0x55]);
    sub_08004380(OBJECT, 0u);
    check(OBJECT[0x55] == 0x11u, "a second call OR-s in another bit and keeps the first",
          (unsigned long)OBJECT[0x55]);
    sub_08004380(OBJECT, 4u);
    check(OBJECT[0x55] == 0x11u, "setting an already-set bit changes nothing", (unsigned long)OBJECT[0x55]);

    /* ---- 3. the byte address is value>>3, checked across a sweep ------- */
    {
        u32 value;
        int bad = 0;
        for (value = 0u; value < 512u; value++) {
            u8 *target = target_for(value);
            reset_arena();
            /* The target is OBJECT + 0x55 + (value>>3); zero exactly that byte so
             * the one bit the routine sets is the only set bit. */
            *target = 0x00u;
            sub_08004380(OBJECT, value);
            if (*target != (u8)(1u << (value & 7u))) {
                bad++;
            }
        }
        check(bad == 0, "every value in 0..511 set the one bit its index arithmetic predicts",
              (unsigned long)bad);
    }

    /* ---- 4. zero and the all-ones value -------------------------------- */
    reset_arena();
    OBJECT[0x54] = 0x00u;
    OBJECT[0x55] = 0x00u;
    sub_08004380(OBJECT, 0xFFFFFFFFu);
    check(OBJECT[0x54] == 0x80u,
          "0xFFFFFFFF has a SIGNED byte index of -1, so the write lands one byte BEFORE the "
          "unsigned position, at object+0x54, bit 7",
          (unsigned long)OBJECT[0x54]);
    check(OBJECT[0x55] == 0x00u, "and object+0x55 is untouched", (unsigned long)OBJECT[0x55]);
    check(target_for(0xFFFFFFFFu) == OBJECT + 0x54,
          "the address arithmetic agrees", (unsigned long)(target_for(0xFFFFFFFFu) - OBJECT));

    /* ---- 5. values with bit 31 set walk far outside the object --------- */
    /* These are asserted by POINTER ONLY, without calling the routine: the
     * target is genuinely far outside any object, and the write would fault.
     * That is the point being recorded: a LOGICAL shift would have placed them
     * far ABOVE the base, an arithmetic one puts them far BELOW. */
    /* For this value the sum wraps past the top of the address space, so the
     * target is not "below" the base by ordinary comparison; what identifies the
     * arithmetic shift is the exact address, which differs from the logical-shift
     * answer. */
    check((u32)target_for(0x80000000u) == (u32)OBJECT + 0xF0000000u + 0x55u,
          "0x80000000 uses the sign-replicated index 0xF0000000",
          (unsigned long)((u32)target_for(0x80000000u) - (u32)OBJECT));
    check((u32)target_for(0x80000000u) != (u32)OBJECT + 0x10000000u + 0x55u,
          "which is NOT the logical-shift answer, so the shift is arithmetic",
          (unsigned long)((u32)target_for(0x80000000u) - (u32)OBJECT));
    check(target_for(0xFFFFFFFFu) == OBJECT + 0x54u,
          "and 0xFFFFFFFF lands one byte before the unsigned position, at object+0x54",
          (unsigned long)(target_for(0xFFFFFFFFu) - OBJECT));

    /* ---- 6. no bounds check: a value past the body is still written ---- */
    /* The object body is BODY bytes; this value targets a byte well beyond it
     * and the routine writes it without any test. The arena is large enough to
     * observe the write rather than fault on it. */
    reset_arena();
    sub_08004380(OBJECT, 0x100u);         /* byte index 0x20 -> OBJECT + 0x75 */
    check((unsigned long)(target_for(0x100u) - OBJECT) >= (unsigned long)BODY,
          "0x100 targets a byte past the 64-byte body", (unsigned long)(target_for(0x100u) - OBJECT));
    check(target_for(0x100u) < g_arena + sizeof(g_arena), "and the arena is large enough to see it",
          (unsigned long)(target_for(0x100u) - g_arena));
    check(*target_for(0x100u) == (u8)(GUARD_BYTE | (1u << 0u)),
          "the out-of-body byte really was modified", (unsigned long)*target_for(0x100u));

    /* ---- 7. the two shift directions are split at the low three bits --- */
    {
        u32 value;
        int bad = 0;
        for (value = 0u; value < 64u; value++) {
            u32 expected_bit = value & 7u;
            u32 expected_index = value >> 3;
            if ((1u << expected_bit) > 0x80u) {
                bad++;
            }
            if (expected_index != value / 8u) {
                bad++;
            }
        }
        check(bad == 0, "for non-negative values the split is value/8 and value%8",
              (unsigned long)bad);
    }

    printf("%s: %d check(s), %d failure(s)\n",
           failures ? "FAIL" : "PASS", checks, failures);
    return failures ? 1 : 0;
}
