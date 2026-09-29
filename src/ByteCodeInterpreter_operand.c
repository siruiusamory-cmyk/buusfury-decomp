/*
 * src/ByteCodeInterpreter_operand.c
 *
 * DECOMPILED SOURCE for the ByteCodeInterpreter primary dispatch slot 1,
 * entry 0x08003C8A. The ROM preserves the original source path for this
 * subsystem as ASCII at 0x08004160:
 *
 *     T:\Source\ByteCodeInterpreter\ByteCodeInterpreter.cpp
 *
 *   0x08003C8A  52 bytes  26 instructions  one terminator at 0x08003CBC
 *
 * A LEAF: it makes no calls and loads no literals. That is why it needs no
 * helper lifted with it, and why no stub or pool had to be supplied.
 *
 * SCOPE: this handler only. The neighbouring slot-2 handler is reconstructed
 * separately at src/ByteCodeInterpreter_handlers.c, and whether the two shared
 * an original translation unit is NOT established: this handler has no literal
 * pool, so pooling gives no evidence either way. The two are contiguous in the
 * ROM, which is consistent with a shared unit and is not proof of one.
 *
 * STATUS, and these three lines are INDEPENDENT of one another.
 *   SEMANTIC.....PROVEN   the decoding, the sign handling and the cursor
 *                         mutation are checked by RUNNING them, exhaustively
 *                         over every one- and two-byte input.
 *   MODERN_BUILD.PASS     it compiles and links for ARM7TDMI Thumb with the
 *                         modern toolchain; see docs/LIFT_OPERAND.md.
 *   ADS_MATCH....BLOCKED  never compiled by the tool it targets. The ADS 1.2
 *                         binaries are present on this machine but the licence
 *                         present covers a different product, so the ARM
 *                         compilers cannot be run (ADS12_LICENSE_UNAVAILABLE).
 *                         No byte-match claim is made.
 *
 * ON THE NAME "sm7"
 * "sm7" is NOT a string in the ROM. It is a project nickname and is recorded
 * here as a CANDIDATE ALIAS, not as an established name. The ROM establishes
 * the ENCODING, which is described below from the instructions themselves and
 * needs no nickname. No operand meaning is imported from another LoG title.
 *
 * THE ENCODING, read off the instructions
 *
 *   acc = 0
 *   loop:
 *     acc = acc << 7                      lsls r2,r2,#7       @ 0x08003C90
 *     b   = *cursor                       ldrb r3,[r4]        @ 0x08003C92
 *     cursor += 1                         adds r4,#1          @ 0x08003C94
 *     *cursor_slot = cursor               str  r4,[r1]        @ 0x08003C96
 *     acc += (b & 0x7F)                   lsls/lsrs/adds      @ 0x08003C98..9C
 *     if (b & 0x80) goto loop             lsls r3,r3,#0x18 ; bmi  @ 0x08003C9E..A0
 *   then:
 *     if (acc & 1) value = -(acc >> 1)    lsls/bpl/asrs/rsbs @ 0x08003CA2..A8
 *     else         value =  (acc >> 1)                        @ 0x08003CAC
 *
 *   - bit 7 of each byte is the CONTINUATION flag: set means another byte
 *     follows, and the sequence ends at the first byte with bit 7 clear;
 *   - each byte contributes its LOW SEVEN BITS;
 *   - the accumulator is shifted left by seven BEFORE each group is added, so
 *     the FIRST byte holds the MOST significant group: groups arrive
 *     most-significant-first, i.e. big-endian base-128;
 *   - bit 0 of the finished accumulator is the SIGN, and the remaining bits are
 *     the MAGNITUDE. This is sign-magnitude, NOT two's complement;
 *   - the shift that extracts the magnitude is ARITHMETIC (asrs), which is what
 *     produces the high-accumulator artifact described below.
 *
 * BYTES CONSUMED
 *   1 byte  -> accumulator bits 0..6  -> value in -63..+63
 *   2 bytes -> accumulator bits 0..13 -> value in -8191..+8191
 *   3 bytes -> accumulator bits 0..20 -> value in -1048575..+1048575
 *   4 bytes -> accumulator bits 0..27 -> value in -134217727..+134217727
 * The byte count is not carried by the value: 0x80 0x02 and 0x02 both decode
 * to +1. Leading zero groups are accepted, so **the encoding is not canonical**
 * and the same value has many spellings. Nothing trims them.
 *
 * THERE IS NO LENGTH LIMIT AND NO VALIDATION
 * The loop's only exit is a byte with bit 7 clear. Nothing counts the bytes,
 * bounds them, or checks the cursor against an end. A run of bytes with bit 7
 * set is followed indefinitely, so malformed input walks the cursor forward
 * until it happens to meet a byte with bit 7 clear. No length check has been
 * added here, because the original performs none.
 *
 * THE HIGH-ACCUMULATOR ARTIFACT
 * The magnitude is extracted with an ARITHMETIC shift of the full 32-bit
 * accumulator. While bit 31 of the accumulator is clear the result is exactly
 * sign-magnitude. Once bit 31 is set the shift keeps the sign bit, so the two
 * branches stop meaning what they say:
 *
 *   - a nominally POSITIVE encoding yields a negative value;
 *   - a nominally NEGATIVE encoding yields a positive value.
 *
 * The maximal all-ones five-group sequence 0xFF 0xFF 0xFF 0xFF 0x7F builds
 * accumulator 0xFFFFFFFF, takes the negative branch, shifts arithmetically to
 * 0xFFFFFFFF (= -1), and negates that to produce **+1**. A naive model that
 * applies sign-magnitude to the full 32-bit accumulator would predict
 * -2147483647 and be wrong. This is recorded as the code's ACTUAL behaviour,
 * not as a defect to be corrected: the reconstruction reproduces it exactly.
 *
 * WHAT IS PROVEN
 *   - entry contract: r0 = context, r1 = the ADDRESS OF THE CURSOR SLOT, which
 *     is what the interpreter establishes at 0x0800408E/90 and what slot 2 also
 *     relies on;
 *   - every byte read advances the cursor by one and writes it straight back
 *     into the slot, before the continuation test -- so a terminating byte has
 *     already been consumed when the loop exits;
 *   - the handler makes NO CALLS, so there is no ordering question between the
 *     cursor update and a call;
 *   - the decoded value is PUSHED onto a stack in the context: context+0x00 is
 *     a counter, it is incremented by one, and the value is stored at
 *     context + 4 + 4*old_counter.
 *
 * A CROSS-TICKET CONSEQUENCE
 * This handler proves context+0x00 is a COUNTER, which is a fact the
 * interpreter's own translation unit used but could not name: at 0x0800405C it
 * stores zero there, which now reads as emptying this stack. The field is named
 * `count` below on that evidence. src/ByteCodeInterpreter.c is deliberately NOT
 * edited by this ticket, so that its committed report stays byte-for-byte
 * reproducible.
 *
 * WHAT IS UNKNOWN
 *   - what the consuming code does with the pushed value. Nothing here calls
 *     anything, so nothing here observes it;
 *   - whether any caller relies on the non-canonical encodings;
 *   - what the surrounding handlers do with this stack. They are not lifted.
 *
 * The original file may NOT be copied from 2genkidev/buusfury: that repository
 * carries no licence grant. See docs/REFERENCE_AUDIT.md.
 */

typedef unsigned char u8;
typedef unsigned int u32;
typedef signed int i32;

/* The context, as far as this handler touches it. `count` is at +0x00 and the
 * pushed values begin at +0x04. The object is larger than this declaration; it
 * is 0x6c bytes, established in src/ByteCodeInterpreter.c. */
typedef struct BciValueStack {
    u32 count;       /* +0x00 : proven a counter by this handler        */
    u32 values[1];   /* +0x04 : values[0], then +0x08, +0x0c, ...       */
} BciValueStack;

/* ------------------------------------------------------------------------- */
/* The magnitude extraction, and why it is written this way                   */
/* ------------------------------------------------------------------------- */
/* `asrs r1, r2, #1` is an ARITHMETIC shift: bit 31 is replicated. C's >> on an
 * unsigned value is logical, and on a negative signed value it is
 * implementation-defined, so the instruction is modelled explicitly rather than
 * left to the compiler's discretion. This reproduces the ARM behaviour on every
 * host, which is what makes the high-accumulator artifact testable. */
static i32 arithmetic_shift_right_1(u32 value)
{
    if (value & 0x80000000u) {
        return (i32)((value >> 1) | 0x80000000u);
    }
    return (i32)(value >> 1);
}

/* ------------------------------------------------------------------------- */
/* primary dispatch slot 1 - 0x08003C8A - 52 bytes - 26 instructions          */
/* ------------------------------------------------------------------------- */
/*
 * Reached only through the primary dispatch table: a search of every evidenced
 * function in the image finds no direct BL site targeting it, so there is no
 * direct caller to miss.
 *
 * Reads a variable-length signed value from the cursor and PUSHES it onto the
 * context's value stack.
 */
void sub_08003C8A(void *ctx, u32 *cursor_slot)
{
    BciValueStack *stack = (BciValueStack *)ctx;
    const u8 *cursor = (const u8 *)*cursor_slot;
    u32 accumulator = 0u;
    u32 value;
    u32 index;

    for (;;) {
        u8 byte;

        accumulator = (accumulator << 7);   /* the running value moves up first */
        byte = *cursor;
        cursor += 1u;
        *cursor_slot = (u32)cursor;         /* advanced per byte, before the test */
        accumulator += (u32)(byte & 0x7Fu);
        if ((byte & 0x80u) == 0u) {
            break;                          /* the only exit: no length limit */
        }
    }

    if (accumulator & 1u) {
        /* Nominal negative: arithmetic shift, then negate. Bit 31 of the
         * accumulator inverts the sign here, exactly as the original does. */
        value = (u32)(-(i32)arithmetic_shift_right_1(accumulator));
    } else {
        /* Nominal positive: the same arithmetic shift. When bit 31 is set this
         * yields a negative value, which is the original's behaviour too. */
        value = (u32)arithmetic_shift_right_1(accumulator);
    }

    index = stack->count;
    stack->count = index + 1u;
    stack->values[index] = value;
}

/* ------------------------------------------------------------------------- */
/* This unit has no literal pool                                              */
/* ------------------------------------------------------------------------- */
/*
 * Every instruction above is register-only: there is no `ldr rX,[pc,#N]`, so
 * there is no pool word to declare and no pool address to record. That is
 * asserted by the lift harness rather than assumed, because a unit that
 * silently lost its pool would otherwise look like this one.
 */
