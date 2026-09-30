/*
 * src/IwramByteLaneSparse.c
 *
 * DECOMPILED SOURCE for one routine of the ARM code block the boot code copies
 * into IWRAM: the byte-lane sparse store, the second member of the block's
 * byte-lane family.
 *
 *   ROM   0x087B7CD4..0x087B7D2C   ARM   88 bytes   22 instructions
 *   IWRAM 0x03000330..0x03000388
 *
 * It is a SEPARATE translation unit from src/IwramByteLanePair.c for a reason
 * that is visible in the image and not a filing convenience: the routine's IWRAM
 * address is not adjacent to the previous routine's. Eight bytes sit between
 * them at IWRAM 0x03000328, and those bytes are the literal pool of the 149-word
 * routine at 0x03000040 that precedes both - proved by the two instructions that
 * read them, `ldr r8,[pc,#0xf0]` at 0x03000230 and `ldr r8,[pc,#0xe4]` at
 * 0x03000240, both inside 0x03000040. The block's layout is therefore
 * [0x03000040 .. 0x030002D8][pool 0x03000328..0x03000330][this routine], and no
 * single contiguous translation unit contains both byte-lane transforms.
 *
 * See src/IwramByteLanePair.c for the ROM-to-IWRAM map, the shared family
 * analysis and the proof that these two routines are VARIANTS of one
 * four-byte-stride byte-lane transform rather than inverses, a pack/unpack pair
 * or a pair of permutations. The family's shared mechanics are restated only
 * where this routine's own bytes are the evidence.
 *
 * WHAT IT DOES
 *   L = 0xFF, the lane mask, from `mov r4, #0xff` (imm8 0xFF, no rotation).
 *   c = le32(context + 0x30), the byte count, compared SIGNED.
 *   D = le32(context + 0x24), the destination BYTE ADDRESS.
 *
 *   D is decremented by four BEFORE the loop and incremented by four at the top
 *   of every pass, so the first word it writes lands exactly on the address the
 *   record names, and it advances by four per source word WHETHER OR NOT it
 *   wrote anything. That is what makes this a sparse masked store: it never
 *   compacts, so a word whose lanes are all zero consumes four bytes of
 *   destination and leaves them alone.
 *
 *   for each source word w:
 *       if w == 0:                     # `cmp r3, #0` / `beq`
 *           write nothing
 *       else:
 *           for k in 0..3:             # `ands` sets Z, `strbne` is predicated
 *               if lane k of w is non-zero:
 *                   D[k] = lane k of w
 *       D += 4
 *
 *   Every store is predicated on the `ands` that produced its lane, so a zero
 *   lane is not written and a zero WORD is not written at all. Neither routine
 *   in this family permutes bytes: both lane maps are the identity.
 *
 * THE BOUNDARIES, reproduced rather than repaired
 *   * The count test is SIGNED. `subs r2, r2, #4` followed by `bmi` (word
 *     0x4A00000C, condition field 0100 = MI) is an N test, not a C test. The
 *     count is decremented once BEFORE the loop and once at the end of each
 *     pass, so the number of passes is count/4 for a count at or above four and
 *     ZERO for a count below four. A count of five or six does NOT round up to
 *     two passes.
 *   * A count at or above 0x80000004 wraps the pre-loop subtraction negative and
 *     the routine returns having done nothing; a count of 0x80000000 does NOT
 *     (0x80000000 - 4 = 0x7FFFFFFC is positive), so the wrap boundary is
 *     0x80000004 and not the sign bit.
 *   * No zero check and no alignment check is added: there is none in the
 *     original, and inventing one would reconstruct something the cartridge does
 *     not contain.
 *
 * REACHABILITY
 *   NOTHING CALLS IT. The IWRAM address 0x03000330 occurs ZERO times in the
 *   whole 8 MiB image at every byte alignment, in both the even (ARM) and the
 *   odd (Thumb) forms; no in-block BL, branch or literal-pool word in the
 *   walk-reached set names it; and fall-through is impossible because the
 *   preceding routine ends in an unconditional `bx lr` with a third routine's
 *   pool between them. Its status is INFERRED DEAD/UNREACHABLE and NOT proven
 *   dead: the one route a static census cannot see is a pointer assembled at run
 *   time from two registers, which only PC sampling could settle.
 *
 * THE CONTEXT RECORD
 *   +0x24 and +0x30 are the only fields this routine reads. What the record is
 *   and what its other fields mean is UNKNOWN here and is not guessed from
 *   another title.
 *
 * STATUS, and these three lines are INDEPENDENT of one another.
 *   SEMANTIC.....PROVEN   the lane equation, the predicated stores, the
 *                         all-zero-word silence, the signed count test and the
 *                         destination advance are checked by RUNNING them on the
 *                         host; see src/probes/iwrambl_selftest.c.
 *   MODERN_BUILD.PASS     it compiles and links for arm7tdmi in ARM state with
 *                         the modern toolchain; see docs/LIFT_IWRAM_TRANSFORMS.md.
 *   ADS_MATCH....BLOCKED  never compiled by the tool it targets. ADS 1.2 is
 *                         present but unlicensed here
 *                         (ADS12_LICENSE_UNAVAILABLE). No byte-match claim is
 *                         made.
 *
 * EVIDENCE vs PLACEHOLDER
 *   Evidence: every instruction, offset, mask, shift and branch condition above,
 *   read from the cartridge. Placeholder: the C types and the names. The name is
 *   the ROM address and the operation is named mathematically, not by an
 *   invented gameplay purpose.
 *
 * The original may NOT be copied from 2genkidev/buusfury: that repository
 * carries no licence grant. See docs/REFERENCE_AUDIT.md.
 */

typedef unsigned int u32;
typedef unsigned char u8;
typedef int s32;

/* The lane mask and the pass stride: `mov r4, #0xff`, four bytes per word. */
#define LANE_MASK 0xFFu
#define LANE_STRIDE 4u

/* A 32-bit machine model: the routine carries a byte ADDRESS in a register, so a
 * host that widens it loses the high half of the context's pointer field. Built
 * 32-bit on purpose; see host_build_bits in the target registry. The helper
 * names carry a `bls_` prefix so that this unit and src/IwramByteLanePair.c can
 * be compiled together by the host self-check without colliding. */
static u32 bls_load_u32(u32 address)
{
    return *(const u32 *)(unsigned long)address;
}

static void bls_store_u8(u32 address, u8 value)
{
    *(volatile u8 *)(unsigned long)address = value;
}

/* ------------------------------------------------------------------------- */
/* 0x087B7CD4 - 88 bytes - 22 instructions                                    */
/*                                                                            */
/* r0 = context record: +0x24 destination byte address, +0x30 byte count       */
/* r1 = source                                                                 */
/* ------------------------------------------------------------------------- */
void sub_087B7CD4(u32 context, u32 source)
{
    u32 count = bls_load_u32(context + 0x30u);
    u32 destination = bls_load_u32(context + 0x24u) - LANE_STRIDE;

    /* `subs r2, r2, #4` / `bmi`: a SIGNED test on the wrapped counter. The
     * decrement happens before the first test, which is why a count of five or
     * six yields ONE pass rather than two. */
    count -= LANE_STRIDE;
    while ((s32)count >= 0) {
        u32 word;
        u32 lane;

        destination += LANE_STRIDE;
        word = bls_load_u32(source);
        source += LANE_STRIDE;

        /* `cmp r3, #0` / `beq`: an all-zero source word stores NOTHING, although
         * the destination advanced above. */
        if (word == 0u) {
            count -= LANE_STRIDE;
            continue;
        }

        lane = word & LANE_MASK;
        if (lane != 0u) {
            bls_store_u8(destination + 0u, (u8)lane);
        }
        lane = (word >> 8) & LANE_MASK;
        if (lane != 0u) {
            bls_store_u8(destination + 1u, (u8)lane);
        }
        lane = (word >> 16) & LANE_MASK;
        if (lane != 0u) {
            bls_store_u8(destination + 2u, (u8)lane);
        }
        lane = (word >> 24) & LANE_MASK;
        if (lane != 0u) {
            bls_store_u8(destination + 3u, (u8)lane);
        }

        count -= LANE_STRIDE;
    }
}
