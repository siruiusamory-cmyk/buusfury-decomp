/*
 * src/IwramFieldClamp.c
 *
 * DECOMPILED SOURCE for one routine of the ARM code block the boot code copies
 * into IWRAM. The block is the subject of src/IwramBlock.c, src/IwramDispatch.c,
 * src/IwramByteLanePair.c and src/IwramQFormat.c; the ROM-to-IWRAM map is
 *
 *     IWRAM X == ROM 0x087B79A4 + (X - 0x03000000)
 *
 * CONFIRMED from the reset code's own DMA3 programming (see
 * docs/LIFT_IWRAM_RUNTIME.md).
 *
 *   ROM   0x087B83F0..0x087B8484   ARM   148 bytes   37 instructions
 *   IWRAM 0x03000A4C..0x03000AE0   ten-bit field clamp and de-interleave
 *
 * WHAT IT IS, FROM THE INSTRUCTIONS
 * A bit-field conversion with saturation, fed from the source array and de
 * interleaved into two destination streams:
 *
 *   for each pair of source words (w0, w1):
 *       src[0] = 0; src[1] = 0;                       the source is DESTROYED
 *       dst0[k] = sat8(s10(w0[15:6]))  | sat8(s10(w1[15:6]))  << 8
 *       dst1[k] = sat8(s10(w0[31:22])) | sat8(s10(w1[31:22])) << 8
 *
 * Each 32-bit source word carries TWO ten-bit SIGNED fields, at bits 31..22 and
 * at bits 15..6. Bits 21..16 and 5..0 are never read by any instruction. Each
 * field is saturated to signed 8-bit [-128, 127] and packed as one byte; two
 * consecutive words' fields of the same half form one destination halfword.
 *
 * WHY THE FIELDS ARE AT THOSE OFFSETS, EXACTLY
 * The extraction is two instructions per field pair and both are the ROM's own:
 *
 *   asr r5, r4, #22                     -> s10 of bits 31..22
 *   lsl r4, r4, #16 ; asr r4, r4, #22   -> s10 of bits 15..6
 *
 * The second pair is NOT a net `>> 6`: the intermediate 32-bit `lsl #16` DISCARDS
 * bits 31..16 before the arithmetic shift, so the shift that sign-extends comes
 * from bit 15 and the result is the sign extension of a ten-bit field - exactly
 * what the one-line form below computes for both offsets.
 *
 * THE SATURATION IS TWO PREDICATED INSTRUCTIONS AND ITS ORDER MATTERS
 *   cmp r4, #0x7F  ; movgt r4, #0x7F     if (v >  127) v =  127
 *   cmn r4, #0x80  ; mvnlt r4, #0x7F     if (v < -128) v = -128
 *
 * `cmn r4,#0x80` is `r4 + 128` and `mvnlt r4,#0x7F` is `r4 = ~0x7F = -128`.
 * The upper test runs first, but the two bounds cannot both be violated, so the
 * order does not change the result; it is reproduced as written.
 *
 * THE MASKS AND THE HALFWORD STORE
 * The two LOW-field values are explicitly masked with `and rX, rX, #0xFF` before
 * the `orr`. The two HIGH-field values are NOT masked, because the `strh` that
 * consumes them keeps only the low 16 bits - so the missing mask is a property of
 * the store width, not an omission, and this file relies on the same truncation.
 *
 * THE SOURCE IS ZEROED, AND THE POINTER ADVANCES BEFORE THE FIELDS ARE USED
 *   ldm r2, {r4, r6}        two words are read
 *   stm r2!, {r8, ip}       r8 = ip = 0, written back to those same two words
 * The pair is zeroed in place and r2 advances by 8. The routine is therefore not
 * re-entrant over its input and cannot be run twice on the same buffer.
 *
 * THE COUNT IS A DO-WHILE OVER WORD PAIRS AND IS NOT ALIGNED TO THE COUNT
 *   subs r3, r3, #2 ; bgt
 * `bgt` is the SIGNED greater-than test on the ORIGINAL value, so the body runs
 * at least once whatever the count is, and one iteration consumes TWO source
 * words even when only one was asked for. A count of 3 runs twice and consumes
 * four words; a count of 0 or negative runs once. There is no clamp on the source
 * pointer, so an odd count over-reads one word and an over-large count walks off
 * the end. Both are reproduced, not repaired.
 *
 * ARGUMENTS AND RESULT
 *   r0 = first destination,  r1 = second destination,  r2 = source (destroyed),
 *   r3 = word count.
 * No value is returned.
 *
 * STATUS, and these three lines are INDEPENDENT of one another.
 *   SEMANTIC.....PROVEN   the field offsets, both saturation bounds, the
 *                         destructive zeroing and the count edge cases are
 *                         checked by RUNNING this file on the host; see
 *                         src/probes/iwramfieldclamp_selftest.c.
 *   MODERN_BUILD.PASS     it compiles and links for arm7tdmi in ARM state with
 *                         the modern toolchain; see docs/LIFT_IWRAM_NUMERIC.md.
 *   ADS_MATCH....BLOCKED  never compiled by the tool it targets. ADS 1.2 is
 *                         present but unlicensed here (ADS12_LICENSE_UNAVAILABLE).
 *                         No byte-match claim is made.
 *
 * EVIDENCE vs PLACEHOLDER
 *   Evidence: every mask, shift direction and amount, store width and condition
 *   above, read from the cartridge. The eight shift sites the ticket asked about
 *   are enumerated in docs/LIFT_IWRAM_NUMERIC.md with their amounts
 *   (22, 22, 16, 16, 22, 22, 8, 8) and the role of each; their sum is 136. The
 *   brief's "38" is a two-site pair sum from the previous census's own
 *   `same_register_opposite_shift` field - `lsl #16` + `asr #22` for the
 *   low-field extractor, printed at six of the eight sites - and not a total of
 *   the eight. Placeholder: the C types and the names. The names are the ROM
 *   addresses.
 *
 * The original may NOT be copied from 2genkidev/buusfury: that repository
 * carries no licence grant. See docs/REFERENCE_AUDIT.md.
 */

typedef unsigned int u32;
typedef unsigned short u16;
typedef int s32;

/* The two ten-bit fields of a source word, and the saturation bounds. */
#define FIELD_BITS 10u
#define FIELD_LOW_SHIFT 6u
#define FIELD_HIGH_SHIFT 22u
#define CLAMP_HIGH 127
#define CLAMP_LOW (-128)

static u32 load_u32(u32 address)
{
    return *(const u32 *)(unsigned long)address;
}

static void store_u32(u32 address, u32 value)
{
    *(volatile u32 *)(unsigned long)address = value;
}

static void store_u16(u32 address, u32 value)
{
    *(volatile u16 *)(unsigned long)address = (u16)value;
}

/* One ten-bit SIGNED field taken from `shift`, sign-extended to 32 bits.
 *
 * `lsl (32 - 10 - shift)` then `asr (32 - 10)` is the instruction pair the ROM
 * uses for BOTH offsets: at shift 6 it is `lsl #16 ; asr #22`, at shift 22 it is
 * the bare `asr #22`. The intermediate logical shift is what discards the bits
 * above the field, so this is not a net arithmetic shift by `32 - shift`. */
static u32 field10(u32 word, u32 shift)
{
    return (u32)((s32)(word << (32u - FIELD_BITS - shift)) >> (32u - FIELD_BITS));
}

/* `cmp #0x7F ; movgt` then `cmn #0x80 ; mvnlt` - saturate to signed 8-bit. */
static u32 clamp_s8(u32 value)
{
    s32 signed_value = (s32)value;

    if (signed_value > CLAMP_HIGH) {
        signed_value = CLAMP_HIGH;
    }
    if (signed_value < CLAMP_LOW) {
        signed_value = CLAMP_LOW;
    }
    return (u32)signed_value;
}

/* 0x087B83F0 - 148 bytes - 37 instructions.
 *
 * r0 = first destination, r1 = second destination, r2 = source, r3 = word count. */
void sub_087B83F0(u32 destination0, u32 destination1, u32 source, u32 count)
{
    u32 n = count;

    for (;;) {
        const u32 word0 = load_u32(source + 0u);
        const u32 word1 = load_u32(source + 4u);
        u32 low0;
        u32 low1;
        u32 high0;
        u32 high1;

        /* `stm r2!, {r8, ip}` with r8 = ip = 0: the source pair is zeroed in
         * place and only then is the pointer advanced. */
        store_u32(source + 0u, 0u);
        store_u32(source + 4u, 0u);
        source += 8u;

        low0 = clamp_s8(field10(word0, FIELD_LOW_SHIFT));
        low1 = clamp_s8(field10(word1, FIELD_LOW_SHIFT));
        high0 = clamp_s8(field10(word0, FIELD_HIGH_SHIFT));
        high1 = clamp_s8(field10(word1, FIELD_HIGH_SHIFT));

        /* `and ...,#0xFF` on the two low values; the two high values reach the
         * `strh` unmasked and the store width truncates them. */
        store_u16(destination0, (low0 & 0xFFu) | ((low1 & 0xFFu) << 8));
        store_u16(destination1, (high0 & 0xFFu) | ((high1 & 0xFFu) << 8));
        destination0 += 2u;
        destination1 += 2u;

        /* `subs r3,r3,#2` then `bgt` on the ORIGINAL value: a signed comparison,
         * so the branch is taken only while n > 2 in exact arithmetic and the
         * body always runs at least once. */
        if ((s32)n <= 2) {
            break;
        }
        n -= 2u;
    }
}
