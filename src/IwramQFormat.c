/*
 * src/IwramQFormat.c
 *
 * DECOMPILED SOURCE for the ARM code block the boot code copies into IWRAM:
 * the block's two Q-format fixed-point transform routines.
 *
 *   ROM   0x087B80A4..0x087B810C   ARM   104 bytes   26 instructions
 *   IWRAM 0x03000700..0x03000768   3-point dot product, Q10
 *
 *   ROM   0x087B7F04..0x087B80A4   ARM   416 bytes  104 instructions
 *   IWRAM 0x03000560..0x03000700   12-term sum of products, Q10, 3 lanes
 *
 * The same 4100-byte block is the subject of src/IwramBlock.c,
 * src/IwramDispatch.c and src/IwramByteLanePair.c. The ROM-to-IWRAM map is
 * IWRAM X == ROM 0x087B79A4 + (X - 0x03000000), CONFIRMED from the reset code's
 * own DMA3 programming; see docs/LIFT_IWRAM_RUNTIME.md. The two routines are
 * adjacent in the image - 0x087B80A4 is exactly where the larger one ends - and
 * that adjacency is what puts them in one translation unit.
 *
 * THE SHARED REDUCTION IS THE FAMILY, AND ITS EXACT CONTRACT MATTERS
 * Both routines accumulate into a SIGNED 64-bit product sum with `smull`
 * (32x32 -> 64, signed) and `smlal` (signed multiply-accumulate into a 64-bit
 * register pair), and both then reduce the 64-bit sum to 32 bits with this pair
 * of instructions:
 *
 *     lsr rD, RO, #10            low word of the sum, LOGICAL right shift
 *     add rD, rD, RH, lsl #22    high word, shifted up by 22
 *
 * The result is exactly
 *
 *     (u32)(((u64)sum) >> 10)
 *
 * for every 64-bit pattern: the high word contributes its low 22 bits at result
 * bits 22..43, of which 32..43 are truncated, and bits 10..31 of the low word
 * land at result bits 0..21. That equivalence was worked out and checked on the
 * host, and it is an identity - there is no 64-bit value for which the two
 * forms differ. An earlier reading of this routine claimed the pair differed
 * from a 64-bit shift; that claim was wrong and is recorded here so it is not
 * re-derived.
 *
 * What the pair does NOT equal is an ARITHMETIC shift, `(s32)(sum >> 10)`, which
 * would sign-extend bits 54..63 of the sum down into the result's top ten bits.
 * For the negative sum with high word 0xFFFFFFFE and low word 0 the pair gives
 * 0xFF800000 where an arithmetic shift gives 0x3FFFFF80. The reconstruction
 * therefore shifts a `u64`, never an `s64`.
 *
 * The reduction appears in two spellings, and both must be recognised or a
 * pattern scan under-counts the family:
 *
 *   standalone   `lsr rD, RO, #10` then `add rD, rD, RH, lsl #22`
 *   folded       `add rD, ACC, RO, lsr #10` then `add rD, rD, RH, lsl #22`
 *
 * 0x087B80A4 uses the FOLDED spelling three times. 0x087B7F04 uses the
 * standalone spelling nine times and the folded spelling once, for its last
 * group - which is why a scan keyed on the folded form alone finds 3 of its 12
 * reductions.
 *
 * WHAT THE SCALE IS, AND WHAT IS PROVEN ABOUT IT
 * The shift discards the low TEN bits, so the arithmetic is Q10 IF the operands
 * are Q10. Nothing in either routine proves the operands are Q10: the proof
 * available from the bytes is that ten fractional bits are TRUNCATED. "Q10" as
 * a name for the data is INFERRED from the presence of `0x400`-scaled data at
 * the call sites, and is recorded as a scale, not as a fact about the values.
 * There is no `0x400` constant in either routine.
 *
 * TRUNCATION, NOT ROUNDING, and NOT a saturating operation: no rounding term is
 * added, and no clamp instruction exists. The unsigned `>> 10` of a negative
 * product therefore moves the value UP toward zero by up to 1023 units - the
 * `>>` is applied to the 64-bit two's-complement pattern, not to the magnitude.
 *
 * THE TWO ROUTINES ARE NOT THE SAME OPERATION
 * The shared element is the REDUCTION, not the whole function:
 *
 *   0x087B80A4 reduces ONCE per output word, after all three products. Its
 *   intermediate is a genuine 64-bit sum, so no intermediate wraps.
 *
 *   0x087B7F04 reduces each of the three lanes separately and then ADDS the
 *   three 32-bit reduced results to ONE accumulator. That is a different
 *   computation, not a rearrangement: the discarded low bits of one product
 *   cannot carry into another, and the three-way sum wraps mod 2^32 where the
 *   single reduction of 0x087B80A4 cannot. Its last of the four groups is a
 *   third spelling again - it adds three PRE-REDUCED 32-bit lane values
 *   together. Reproduced as written.
 *
 * Neither routine calls anything: both are leaves, and both are register-only
 * aside from their stack frame (0x087B7F04's frame is 0x30 bytes, used to stage
 * the six results before they are popped back and stored as two three-word
 * blocks; 0x087B80A4 has no frame at all and stores with `stm r0,{r4,r5,r6}`,
 * with NO writeback on r0).
 *
 * THE ARGUMENTS
 *   0x087B80A4  r0 = destination, r1 = three coefficient words, r2 = nine
 *               sample words, read as three groups of three. The sample pointer
 *               is RELOADED from r2 before each group because `ldm r2!,{r4,r5,r6}`
 *               would otherwise have consumed it; the coefficient reads use
 *               increasing offsets off r1 instead.
 *   0x087B7F04  r0 = destination, r1 = twelve coefficient words, r2 = the first
 *               three sample words. The sample pointer is reloaded from r2 before
 *               every one of the four groups, so the same three sample words are
 *               read four times against four different coefficient groups. That
 *               is a property of the instruction sequence, not a guess.
 *
 * WHO CALLS THEM
 * Through the Thumb-to-ARM veneers at ROM 0x08049180 (0x03000700) and
 * 0x08049174 (0x03000560), each with exactly ONE Thumb BL caller in the image,
 * at 0x0802F1DC and 0x0802EFD0 respectively. Both callers are in the same ROM
 * region and both pass a stack address and a context-derived pointer. Neither
 * call site resolves all four register arguments within a readable window, so
 * the register roles above come from the routines' own instructions and not from
 * the call sites. That is stated rather than glossed over.
 *
 * STATUS, and these three lines are INDEPENDENT of one another.
 *   SEMANTIC.....PROVEN   the reduction, its two spellings, the accumulation
 *                         widths and the wrapping behaviour are checked by
 *                         RUNNING them on the host; see
 *                         src/probes/iwramqformat_selftest.c.
 *   MODERN_BUILD.PASS     it compiles and links for arm7tdmi in ARM state with
 *                         the modern toolchain; see docs/LIFT_IWRAM_TRANSFORMS.md.
 *   ADS_MATCH....BLOCKED  never compiled by the tool it targets. ADS 1.2 is
 *                         present but unlicensed here
 *                         (ADS12_LICENSE_UNAVAILABLE). No byte-match claim is
 *                         made.
 *
 * EVIDENCE vs PLACEHOLDER
 *   Evidence: every instruction, offset, shift and register pairing above, read
 *   from the cartridge; the call counts and veneer literals, read from the
 *   image. Placeholder: the C types and the names. The names are the ROM
 *   addresses and the operation is named mathematically, not by an invented
 *   gameplay purpose.
 *
 * The original may NOT be copied from 2genkidev/buusfury: that repository
 * carries no licence grant. See docs/REFERENCE_AUDIT.md.
 */

typedef unsigned int u32;
typedef unsigned char u8;
typedef int s32;
typedef long long s64;
typedef unsigned long long u64;

/* The reduction discards the low ten bits of the 64-bit product sum. */
#define Q_SCALE_SHIFT 10u
/* ... and re-injects the high word's low 22 bits, which is 32 - 10. */
#define Q_HIGH_SHIFT 22u
/* Three lanes per group. */
#define Q_LANES 3u
/* 0x087B7F04's frame is 0x30 bytes and stages six results. */
#define Q_STAGED_RESULTS 6u

static u32 load_u32(u32 address)
{
    return *(const u32 *)(unsigned long)address;
}

static void store_u32(u32 address, u32 value)
{
    *(volatile u32 *)(unsigned long)address = value;
}

static void store_u32_at(u32 base, u32 byte_offset, u32 value)
{
    *(volatile u32 *)(unsigned long)(base + byte_offset) = value;
}

/* ------------------------------------------------------------------------- */
/* the two spellings of the reduction, as separate functions so that the host   */
/* check can exercise each one on its own and so that the difference between    */
/* "a 64-bit shift" and "the two instructions" is testable rather than assumed. */
/* ------------------------------------------------------------------------- */

/* `lsr rD, low, #10` ; `add rD, rD, high, lsl #22` => (low >> 10) + (high << 22)
 * as 32-bit modular arithmetic. */
static u32 reduce_q10_standalone(u32 low, u32 high)
{
    return (low >> Q_SCALE_SHIFT) + (high << Q_HIGH_SHIFT);
}

/* `add rD, accumulator, low, lsr #10` ; `add rD, rD, high, lsl #22`, in the
 * order the instructions appear. */
static u32 reduce_q10_folded(u32 accumulator, u32 low, u32 high)
{
    u32 result = accumulator + (low >> Q_SCALE_SHIFT);
    return result + (high << Q_HIGH_SHIFT);
}

/* ------------------------------------------------------------------------- */
/* 0x087B80A4 - 104 bytes - 26 instructions                                   */
/*                                                                            */
/* r0 = destination (three words, stored with NO writeback)                    */
/* r1 = three coefficient words, read as r1[0], r1[4], r1[8] on a word grid    */
/* r2 = nine sample words, read as three groups of three                       */
/*                                                                            */
/* result[j] = (u32)((s64)sum_of_three_products >> 10)   for j in 0..2         */
/* ------------------------------------------------------------------------- */
void sub_087B80A4(u32 destination, u32 coefficients, u32 samples)
{
    u32 c0 = load_u32(coefficients + 0u);
    u32 c1 = load_u32(coefficients + 4u);
    u32 c2 = load_u32(coefficients + 8u);
    s64 product_sum;
    u32 low;
    u32 high;
    u32 result0;
    u32 result1;
    u32 result2;

    /* The three `smull`/`smlal` groups. The sample pointer is reloaded from the
     * argument before each group because `ldm r2!, {r4,r5,r6}` would otherwise
     * have advanced it past the words this routine keeps re-reading. */
    product_sum = (s64)(s32)c0 * (s32)load_u32(samples + 0u);
    product_sum += (s64)(s32)c0 * (s32)load_u32(samples + 4u);
    product_sum += (s64)(s32)c0 * (s32)load_u32(samples + 8u);
    low = (u32)product_sum;
    high = (u32)((u64)product_sum >> 32);
    result0 = reduce_q10_folded(0u, low, high);

    product_sum = (s64)(s32)c1 * (s32)load_u32(samples + 0u);
    product_sum += (s64)(s32)c1 * (s32)load_u32(samples + 4u);
    product_sum += (s64)(s32)c1 * (s32)load_u32(samples + 8u);
    low = (u32)product_sum;
    high = (u32)((u64)product_sum >> 32);
    result1 = reduce_q10_folded(0u, low, high);

    product_sum = (s64)(s32)c2 * (s32)load_u32(samples + 0u);
    product_sum += (s64)(s32)c2 * (s32)load_u32(samples + 4u);
    product_sum += (s64)(s32)c2 * (s32)load_u32(samples + 8u);
    low = (u32)product_sum;
    high = (u32)((u64)product_sum >> 32);
    result2 = reduce_q10_folded(0u, low, high);

    /* `stm r0, {r4,r5,r6}` - no `!`, so the destination register is NOT
     * advanced. */
    store_u32(destination + 0u, result0);
    store_u32(destination + 4u, result1);
    store_u32(destination + 8u, result2);
}

/* ------------------------------------------------------------------------- */
/* 0x087B7F04 - 416 bytes - 104 instructions                                  */
/*                                                                            */
/* r0 = destination (six words, two `stm r0!, {r4,r5,r6}` blocks)             */
/* r1 = twelve coefficient words, read consecutively (post-increment)         */
/* r2 = the first three sample words, re-read for each of the four groups     */
/*                                                                            */
/* r[0..2] accumulate the three separately-REDUCED lanes of each group;        */
/* r[3..5] accumulate the three lanes of the LAST group only, with wrap.      */
/* ------------------------------------------------------------------------- */
void sub_087B7F04(u32 destination, u32 coefficients, u32 samples)
{
    u32 result[Q_STAGED_RESULTS];   /* the six staged words, popped back in two blocks */
    u32 single;                     /* the `ldr r3, [r1], #4` coefficient walk */
    u32 matrix;                     /* `mov lr, r2` - reloaded before every group */
    u32 group;
    u32 lane;
    u32 word;
    s64 product_sum;
    u32 low;
    u32 high;

    result[0] = 0u;
    result[1] = 0u;
    result[2] = 0u;

    /* ---- groups 1..3: one 64-bit product sum per lane, each reduced on its own,
     * then the three reduced 32-bit lane values added into one accumulator per
     * lane. The sample pointer is RELOADED from the argument before every group
     * (`mov lr, r2`), which is what makes the same three sample words feed all
     * four groups; the coefficient pointer is walked with `ldr r3, [r1], #4`, so
     * it advances across the groups while the sample pointer resets. ---- */
    for (group = 0u; group < 3u; group++) {
        for (lane = 0u; lane < Q_LANES; lane++) {
            single = load_u32(coefficients);
            coefficients += 4u;

            matrix = samples;
            word = load_u32(matrix);
            product_sum = (s64)(s32)word * (s32)single;
            matrix += 4u;
            word = load_u32(matrix);
            product_sum += (s64)(s32)word * (s32)single;
            matrix += 4u;
            word = load_u32(matrix);
            product_sum += (s64)(s32)word * (s32)single;

            low = (u32)product_sum;
            high = (u32)((u64)product_sum >> 32);
            result[lane] = reduce_q10_standalone(low, high) + result[lane];
        }
    }

    /* ---- the last group: the folded reduction, whose THIRD lane adds the
     * reduction into the accumulator in place of a zero (`add r6, r6, fp, lsr
     * #10` where the earlier three read `lsr r6, fp, #10`), and then one more
     * 32-bit add. Reproduced as the instructions have it, not normalised. ---- */
    for (lane = 0u; lane < Q_LANES; lane++) {
        single = load_u32(coefficients);
        coefficients += 4u;

        matrix = samples;
        word = load_u32(matrix);
        product_sum = (s64)(s32)word * (s32)single;
        matrix += 4u;
        word = load_u32(matrix);
        product_sum += (s64)(s32)word * (s32)single;
        matrix += 4u;
        word = load_u32(matrix);
        product_sum += (s64)(s32)word * (s32)single;

        low = (u32)product_sum;
        high = (u32)((u64)product_sum >> 32);
        result[3u + lane] = reduce_q10_folded(0u, low, high);
    }

    /* ---- `pop` the six staged words, then two `stm r0!, {r4,r5,r6}` blocks. The
     * first block's writeback is observable in r0 and the second one's is not. ---- */
    store_u32_at(destination, 0u, result[0]);
    store_u32_at(destination, 4u, result[1]);
    store_u32_at(destination, 8u, result[2]);
    store_u32_at(destination, 12u, result[3]);
    store_u32_at(destination, 16u, result[4]);
    store_u32_at(destination, 20u, result[5]);
}
