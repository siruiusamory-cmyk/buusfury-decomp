/*
 * src/IwramQ1814.c
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
 *   ROM   0x087B820C..0x087B83F0   ARM   484 bytes   121 instructions
 *   IWRAM 0x03000868..0x03000A4C   signed-byte resampling mixer, Q18.14 phase
 *
 * WHAT IT IS, FROM THE INSTRUCTIONS
 * A strided, fractional-position signed-byte reader with a multiply-accumulate
 * into an EXISTING destination value:
 *
 *     out[i] += D * (s8)mem[address_i]        32-bit wraparound
 *     address_i = C + floor((A + i*B) / 2^14)  (arithmetic placement)
 *
 * The position is a 64-BIT phase whose HIGH WORD IS THE BYTE ADDRESS:
 *
 *     hi = C + (A asr 14)      the address, as a 32-bit register
 *     lo = A lsl 18            the sub-byte fraction, 2^18 per byte
 *     per element:  adds lo,lo,(B lsl 18) ; adc hi,hi,(B asr 14)
 *
 * The 64-bit value is therefore P_i = (A + i*B) * 2^18 + C * 2^32 as a
 * two's-complement 64-bit quantity, and `hi` is its high word, which is exactly
 * the byte address floor(P_i / 2^32). A is the starting byte position and B the
 * per-output-sample step, BOTH IN Q18.14 (A*2^18 is A's value times 2^32, which
 * is why the low word is scaled by 2^18 rather than 2^14); C is an integer base
 * added into the high word. The scale is stated as a consequence of the shift
 * pair, not as a claim about the data.
 *
 * THE TWO SPECIALIZATIONS, AND WHY BOTH ARE REPRODUCED
 * `cmp r4, #0` with r4 = `B asr 14` selects one of two bodies. The test is
 * exactly "the increment's high word is zero", which for a 32-bit B means
 * 0 <= B <= 16383 - NOT |B| < 2^14, because a NEGATIVE B has an all-ones
 * arithmetic shift and takes the GENERAL path (B = -1 gives r4 = -1).
 *
 *   general (r4 != 0)   read the sample at `hi`, then `adds`/`adc`.
 *   carry-only (r4 == 0)
 *                       the `adc` is replaced by
 *                           adds r7, r7, r8          the fractional add
 *                           ldrsbhs r0, [r3, #1]!    HS = carry set
 *                       `ldrsbhs` is LDRSB under condition HS, PRE-indexed with
 *                       writeback. When the carry is SET it loads from r3+1 and
 *                       leaves r3 = that address. When the carry is CLEAR the
 *                       instruction has NO EFFECT AT ALL: no load, no memory
 *                       access, and no base writeback. The ARM ARM is explicit
 *                       that a failed conditional data transfer performs neither
 *                       the access nor the writeback.
 *
 * The two bodies are NOT interchangeable, and the difference is not decoration:
 * in the carry-only body a sample whose address did not move is NOT re-read, it
 * is RETAINED in r0 from the previous element. On ordinary memory the retained
 * byte is the byte that would have been read, so the two agree - but they
 * diverge when the destination OVERLAPS the sampled bytes, because the previous
 * group's `stm` has rewritten the byte the general body would read again. The
 * divergence is reproduced here and asserted in
 * src/probes/iwramq1814_selftest.c; "tidying" the two bodies into one loop
 * silently changes that case.
 *
 * TRUNCATION, NOT ROUNDING, AND THE EXACT GROUP STRUCTURE
 * There is no rounding term and no clamp: `hi` is the high word of the phase, so
 * a position that is not a whole byte is TRUNCATED toward negative infinity
 * (an arithmetic shift of a two's-complement value), which for negative
 * positions is not the same as truncation toward zero. A = -1 puts the address
 * at C - 1, not at C.
 *
 * The count dispatch is a Duff's-device structure with an asymmetry worth
 * stating exactly, because "groups of eight" gets it wrong:
 *
 *     if (n & 1) { 1 element; n -= 1; if (n == 0) return; }
 *     if (n & 2) { 2 elements; n -= 2; if (n == 0) return; }
 *     if (n & 4) { 4 elements; } else { 4 elements; 4 elements; }
 *     for (;;) { before = n; n = before - 8; if (!(before >= 8 && n != 0)) break;
 *                4 elements; 4 elements; }
 *
 * The `tst r2,#4` test SKIPS the first 4-element group when bit 2 is set, but
 * the following `subs r2,r2,#8` still subtracts EIGHT. So a count of 12 writes
 * 4 + 8 = 12 elements and a count of 4 writes 4 and then leaves on the borrow.
 * The loop test is `bhi` - unsigned higher - which is "carry set and zero
 * clear" after the `subs`. The 1-element block precedes `cmp r4, #0`, so it is
 * SHARED by both specializations and always reads its sample unconditionally.
 *
 * THE COUNT IS NOT GUARDED
 * There is no pre-test. A count of ZERO writes EIGHT destination words: the
 * first `subs r2,r2,#8` borrows, so the body has already run twice. The count is
 * used UNSIGNED - it is only ever tested for equality with zero - so a count of
 * -1 asks for 2^32 - 1 elements and does not terminate in any practical sense.
 * Both are reproduced here, not repaired.
 *
 * ARGUMENTS AND RESULT
 *   r0 = pointer to FOUR 32-bit words: A(+0) B(+4) C(+8) D(+12)
 *   r1 = destination word array, READ-MODIFY-WRITTEN (out[i] += ...)
 *   r2 = element count, 32-bit
 * No value is returned; r0 is consumed by the `ldm r0,{r3,r4,r5,r6}` and is not
 * preserved as an argument. r1 is not required to be word-aligned by any
 * instruction, but the `ldm`/`stm` pairs behave differently unaligned, so this
 * reconstruction describes the aligned case and the ROM's own alignment
 * behaviour is not modelled.
 *
 * STATUS, and these three lines are INDEPENDENT of one another.
 *   SEMANTIC.....PROVEN   the equations, both specializations, the retention,
 *                         the truncation direction, the group structure and the
 *                         edge counts are checked by RUNNING this file on the
 *                         host; see src/probes/iwramq1814_selftest.c.
 *   MODERN_BUILD.PASS     it compiles and links for arm7tdmi in ARM state with
 *                         the modern toolchain; see docs/LIFT_IWRAM_NUMERIC.md.
 *   ADS_MATCH....BLOCKED  never compiled by the tool it targets. ADS 1.2 is
 *                         present but unlicensed here (ADS12_LICENSE_UNAVAILABLE).
 *                         No byte-match claim is made.
 *
 * EVIDENCE vs PLACEHOLDER
 *   Evidence: every instruction, offset, shift, condition and register pairing
 *   above, read from the cartridge. Placeholder: the C types and the names. The
 *   names are the ROM addresses; the operation is named mathematically, not by
 *   an invented gameplay purpose.
 *
 * The original may NOT be copied from 2genkidev/buusfury: that repository
 * carries no licence grant. See docs/REFERENCE_AUDIT.md.
 */

typedef unsigned int u32;
typedef unsigned char u8;
typedef int s32;

/* The phase keeps 14 fractional bits of a BYTE position, and the low word of the
 * 64-bit accumulator is scaled by 2^18 so that A*2^18 == (A / 2^14) * 2^32. */
#define Q1814_FRACTION_BITS 14u
#define Q1814_LOW_SCALE_BITS 18u

/* One unrolled group is at most four destination words. */
#define Q1814_GROUP_MAX 4u

static u32 load_u32(u32 address)
{
    return *(const u32 *)(unsigned long)address;
}

static void store_u32(u32 address, u32 value)
{
    *(volatile u32 *)(unsigned long)address = value;
}

/* `ldrsb r0, [rX]`: a signed byte, sign-extended to 32 bits. */
static u32 load_s8(u32 address)
{
    return (u32)(s32)*(const signed char *)(unsigned long)address;
}

/* The 64-bit position accumulator. `hi` IS the memory address handed to ldrsb. */
typedef struct {
    u32 hi;         /* r3 : the byte address, and the high word of the phase */
    u32 lo;         /* r7 : the sub-byte fraction, 2^18 per byte */
    u32 step_hi;    /* r4 : B asr 14, the increment's high word */
    u32 step_lo;    /* r8 : B lsl 18, the increment's low word */
} q1814_phase;

/* `adds r7,r7,r8` then `adc r3,r3,r4` - a 64-bit add of the Q18.14 step. */
static void q1814_advance(q1814_phase *phase)
{
    const u32 sum = phase->lo + phase->step_lo;
    const u32 carry = (sum < phase->lo) ? 1u : 0u;

    phase->lo = sum;
    phase->hi = phase->hi + phase->step_hi + carry;
}

/* ---- the general body: the increment's high word is non-zero ---------------
 *
 * Every element READS the sample at the current address before advancing, which
 * is the instruction order `ldrsb r0,[r3]` ; `adds` ; `adc` ; `mla`.
 */
static void q1814_element_general(u32 *held, u32 coefficient, q1814_phase *phase)
{
    /* `mla rD, r6, r0, rD` - 32-bit wraparound, and the byte is SIGNED. */
    *held = *held + coefficient * load_s8(phase->hi);
    q1814_advance(phase);
}

/* ---- the carry-only body: `B asr 14 == 0` ---------------------------------
 *
 * The accumulate uses the sample ALREADY IN *sample; the fractional add follows,
 * and the address and the sample move ONLY if that add carried. When it did not
 * carry there is no memory access at all - that is the `ldrsbhs` failing its
 * condition - so the retained byte, not a fresh read, is what the next element
 * consumes. This is observable exactly when the destination overlaps the
 * sampled bytes.
 */
static void q1814_element_carry(u32 *held, u32 coefficient, q1814_phase *phase,
                                u32 *sample)
{
    const u32 previous_lo = phase->lo;
    const u32 sum = previous_lo + phase->step_lo;

    *held = *held + coefficient * *sample;
    phase->lo = sum;
    /* `ldrsbhs`: the carry is what moves the address, and when it is clear the
     * sample is NOT re-read. */
    if (sum < previous_lo) {
        phase->hi = phase->hi + 1u;
        *sample = load_s8(phase->hi);
    }
}

/* One unrolled group. The destination words are read into registers FIRST and
 * written back only after every sample of the group has been accumulated, which
 * is the order the `ldm`/`stm` pairs impose - and which is why an aliased
 * destination cannot be observed within one group. `elements` is 1, 2 or 4. */
static void q1814_group_general(u32 destination, u32 coefficient,
                                q1814_phase *phase, u32 elements)
{
    u32 held[Q1814_GROUP_MAX];
    u32 index;

    for (index = 0u; index < elements; index++) {
        held[index] = load_u32(destination + 4u * index);
    }
    for (index = 0u; index < elements; index++) {
        q1814_element_general(&held[index], coefficient, phase);
    }
    for (index = 0u; index < elements; index++) {
        store_u32(destination + 4u * index, held[index]);
    }
}

static void q1814_group_carry(u32 destination, u32 coefficient,
                              q1814_phase *phase, u32 elements, u32 *sample)
{
    u32 held[Q1814_GROUP_MAX];
    u32 index;

    for (index = 0u; index < elements; index++) {
        held[index] = load_u32(destination + 4u * index);
    }
    for (index = 0u; index < elements; index++) {
        q1814_element_carry(&held[index], coefficient, phase, sample);
    }
    for (index = 0u; index < elements; index++) {
        store_u32(destination + 4u * index, held[index]);
    }
}

/* The shared 2/4/8 dispatch, for one of the two element forms. */
static void q1814_dispatch(u32 destination, u32 coefficient, q1814_phase *phase,
                           u32 n, u32 *sample, int carry_only)
{
    u32 index;

    if ((n & 2u) != 0u) {
        if (carry_only) {
            q1814_group_carry(destination, coefficient, phase, 2u, sample);
        } else {
            q1814_group_general(destination, coefficient, phase, 2u);
        }
        destination += 8u;              /* `stm r1!, {two}` */
        n -= 2u;
        if (n == 0u) {
            return;
        }
    }
    if ((n & 4u) != 0u) {
        /* `tst r2,#4` / `bne` jumps INTO the second group, so only FOUR elements
         * are produced here - and the `subs #8` below still subtracts eight. */
        if (carry_only) {
            q1814_group_carry(destination, coefficient, phase, 4u, sample);
        } else {
            q1814_group_general(destination, coefficient, phase, 4u);
        }
        destination += 16u;
    } else {
        for (index = 0u; index < 2u; index++) {
            if (carry_only) {
                q1814_group_carry(destination, coefficient, phase, 4u, sample);
            } else {
                q1814_group_general(destination, coefficient, phase, 4u);
            }
            destination += 16u;
        }
    }
    for (;;) {
        const u32 before = n;
        n = before - 8u;
        /* `bhi` after `subs r2,r2,#8`: carry set (no borrow) and zero clear. */
        if (!(before >= 8u && n != 0u)) {
            break;
        }
        for (index = 0u; index < 2u; index++) {
            if (carry_only) {
                q1814_group_carry(destination, coefficient, phase, 4u, sample);
            } else {
                q1814_group_general(destination, coefficient, phase, 4u);
            }
            destination += 16u;
        }
    }
}

/* 0x087B820C - 484 bytes - 121 instructions.
 *
 * r0 = { A, B, C, D }, r1 = destination words, r2 = element count. */
void sub_087B820C(u32 params, u32 destination, u32 count)
{
    const u32 a = load_u32(params + 0u);
    const u32 b = load_u32(params + 4u);
    const u32 c = load_u32(params + 8u);
    const u32 d = load_u32(params + 12u);

    q1814_phase phase;
    u32 n = count;
    u32 sample = 0u;

    /* `lsl r7, r3, #0x12` ; `add r3, r5, r3, asr #0xE` */
    phase.lo = a << Q1814_LOW_SCALE_BITS;
    phase.hi = c + (u32)((s32)a >> Q1814_FRACTION_BITS);
    /* `lsl r8, r4, #0x12` ; `asr r4, r4, #0xE` */
    phase.step_lo = b << Q1814_LOW_SCALE_BITS;
    phase.step_hi = (u32)((s32)b >> Q1814_FRACTION_BITS);

    /* The 1-element block PRECEDES `cmp r4, #0`, so both specializations share
     * it and it always reads its sample unconditionally. */
    if ((n & 1u) != 0u) {
        q1814_group_general(destination, d, &phase, 1u);
        destination += 4u;
        n -= 1u;
        if (n == 0u) {
            return;
        }
    }

    if (phase.step_hi == 0u) {
        /* The unconditional load at IWRAM 0x03000990, before any group test. */
        sample = load_s8(phase.hi);
        q1814_dispatch(destination, d, &phase, n, &sample, 1);
    } else {
        q1814_dispatch(destination, d, &phase, n, &sample, 0);
    }
}
