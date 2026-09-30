/*
 * src/IwramByteLanePair.c
 *
 * DECOMPILED SOURCE for the ARM code block the boot code copies into IWRAM:
 * the two routines that transform a byte string four bytes at a time through a
 * 0xFF lane mask, which are the two members of the block's byte-lane family.
 *
 *   ROM   0x087B7C80..0x087B7CCC   ARM   76 bytes   19 instructions
 *   IWRAM 0x030002DC..0x03000328
 *
 *   ROM   0x087B7CD4..0x087B7D2C   ARM   88 bytes   22 instructions
 *   IWRAM 0x03000330..0x03000388
 *
 * The same 4100-byte block is the subject of src/IwramBlock.c and
 * src/IwramDispatch.c. The ROM-to-IWRAM map is
 * IWRAM X == ROM 0x087B79A4 + (X - 0x03000000), because the arm7tdmi reset code
 * at 0x080000C0 sets DMA3 up a second time with SAD = 0x087B79A4, DAD =
 * 0x03000000 and the 32-bit control word 0x84000401 (0x401 words = 4100 bytes,
 * both addresses incrementing). The copy is verbatim, so every IWRAM address in
 * the block is statically known. That map is CONFIRMED from the reset code's own
 * instructions and literal pool; see docs/LIFT_IWRAM_RUNTIME.md.
 *
 * WHY THESE TWO ARE ONE FAMILY, AND WHY THEY ARE NOT INVERSES
 * They are NOT inverses, NOT a pack/unpack pair and NOT byte permutations. What
 * they share is mechanical and exact:
 *
 *   * a four-byte stride and a `mov rX, #0xff` lane mask, with the mask applied
 *     by `ands` (`and` with the S bit, which is word bit 20 - capstone folds it
 *     into ARM_INS_AND, so the mnemonic alone cannot tell you the flags are set);
 *   * the SAME "byte 0 is special" idiom: `ands rX, mask, lane` sets Z, and the
 *     very next instruction is predicated on it (`ldrbne` in 0x087B7C80,
 *     `strbne` in 0x087B7CD4). One skips the table READ for a zero lane, the
 *     other skips the STORE;
 *   * all four lane extractions are LSR except lane 0, which is the unshifted
 *     form - there is no ASR and no ROR anywhere in either routine, so neither
 *     one is a sign-extending or rotating operation;
 *   * both lane maps are the IDENTITY: lane k of the source affects bit group k
 *     of the result and nothing else. Neither routine permutes bytes.
 *
 * The two differ in what a zero lane does and in what the second argument is.
 * 0x087B7C80 maps a NON-ZERO lane through a caller-supplied 256-byte table and
 * leaves a zero lane alone; 0x087B7CD4 takes a context record and writes a
 * non-zero lane back to the destination it names, leaving a zero lane untouched
 * in memory. So 0x087B7CD4 is a SPARSE masked store, not a compaction: it
 * advances the destination by four bytes per source word even when it stored
 * nothing.
 *
 * The only composite identity between them is trivial and is recorded rather
 * than presented as a result: with an identity table, 0x087B7C80 is the identity
 * word map, so running 0x087B7CD4 over its output into a zeroed window
 * reproduces the source byte for byte because the first routine did nothing. No
 * table can make 0x087B7C80 an inverse of 0x087B7CD4, because 0x087B7CD4 is not
 * injective: for a byte count below four it returns without reading its source
 * at all, and a zero source word writes nothing.
 *
 * WHAT 0x087B7C80 IS CALLED BY
 * Through the Thumb-to-ARM veneer at ROM 0x0804918C (`bx pc`, a flag-transparent
 * `nop`, ARM `ldr pc,[pc,#-4]`, then the literal 0x030002DC), which has three
 * Thumb BL callers, all of which set r0 = r1 = the same address with r2 = a
 * 256-byte ROM table and r3 = a byte count:
 *
 *   0x08030EBC  r2 = 0x0805672C, r3 = (a-b)*(a-b) of a pair of rectangles
 *   0x0803D99C  r2 = 0x0805672C, r3 = a field of the record the wrapper holds
 *   0x0803F9FA  r2 = 0x0805672C, r3 = a width, inside a row loop
 *
 * The table is the same 256-byte ROM table at all three sites and it is not the
 * identity. The transformation is therefore a byte-string substitution through a
 * fixed table, applied in place. WHAT THAT TABLE MEANS is UNKNOWN: this project
 * imports no opcode, container or compression-format meaning from another title,
 * and the table's own structure has not been proven. It is recorded as a
 * 256-byte byte map at 0x0805672C and nothing more.
 *
 * WHAT 0x087B7CD4 IS CALLED BY
 * NOTHING. Its IWRAM address 0x03000330 occurs ZERO times in the whole 8 MiB
 * image at every byte alignment, in both the even (ARM) and odd (Thumb) forms;
 * no in-block BL or branch reaches it; no literal-pool word in the walk-reached
 * set names it; and it cannot be reached by fall-through because 0x087B7C80 ends
 * in an unconditional `bx lr` and eight bytes of another routine's literal pool
 * follow it. Its status is INFERRED DEAD/UNREACHABLE, not proven dead: the one
 * route this census cannot see is a pointer assembled at run time from two
 * registers, which only PC sampling could settle.
 *
 * THE ARGUMENTS OF 0x087B7CD4 ARE A CONTEXT RECORD, and only two of its fields
 * are used: +0x24 is the destination byte address and +0x30 is the byte count.
 * What that record is, and what the other fields mean, is UNKNOWN here.
 *
 * BEHAVIOUR AT THE BOUNDARIES, reproduced and not repaired
 *   * 0x087B7C80 has NO pre-test on the count. The count is decremented by four
 *     at the END of each pass and the loop exits when it reaches exactly zero.
 *     So a count of zero wraps the counter through 2^32 and runs 2^30 passes,
 *     destroying 2^32 bytes of the address space; a count that is not a multiple
 *     of four never reaches zero and NEVER TERMINATES. Neither is a guard the
 *     original lacks: adding one would reconstruct something the cartridge does
 *     not contain.
 *   * 0x087B7CD4 compares its count SIGNED. `subs r2, r2, #4` followed by
 *     `bmi` (word 0x4A00000C, condition 0100 = MI) is a signed test, so a count
 *     of 0x80000000 leaves N set with C clear and the routine returns having
 *     done nothing, where an unsigned test would have run 2^29 passes. A count
 *     in [0, 3] likewise stores nothing.
 *
 * STATUS, and these three lines are INDEPENDENT of one another.
 *   SEMANTIC.....PROVEN   the lane equations, the masking and packing order, the
 *                         predicated reads and stores, the signed count test and
 *                         the counter wraparound are checked by RUNNING them on
 *                         the host; see src/probes/iwrambl_selftest.c.
 *   MODERN_BUILD.PASS     it compiles and links for arm7tdmi in ARM state with
 *                         the modern toolchain; see docs/LIFT_IWRAM_TRANSFORMS.md.
 *   ADS_MATCH....BLOCKED  never compiled by the tool it targets. The ADS 1.2
 *                         binaries are present on this machine but the licence
 *                         present covers a different product
 *                         (ADS12_LICENSE_UNAVAILABLE). No byte-match claim is
 *                         made.
 *
 * EVIDENCE vs PLACEHOLDER
 *   Evidence: every instruction, offset, shift, mask and branch condition above,
 *   all read from the cartridge; the call sites and the table address, read from
 *   the image. Placeholder: the C types and the names. The names are the ROM
 *   addresses, because the disassembly fixes offsets and access widths and the
 *   game's own names are not recoverable. The functions are named by their
 *   mathematical operation, not by an invented gameplay purpose.
 *
 * The original may NOT be copied from 2genkidev/buusfury: that repository
 * carries no licence grant. See docs/REFERENCE_AUDIT.md.
 */

typedef unsigned int u32;
typedef unsigned char u8;
typedef int s32;

/* The lane mask, and the four lane positions. `mov ip, #0xff` in the first
 * routine and `mov r4, #0xff` in the second are the same imm8 with no rotation. */
#define LANE_MASK 0xFFu
#define LANE_STRIDE 4u

/* A 32-bit machine model: the routines carry byte ADDRESSES in registers, so a
 * host that widens them loses the high half and the wraparound the routines
 * depend on. Built 32-bit on purpose; see host_build_bits in the target. The
 * helpers carry a `blp_` prefix so this unit and src/IwramByteLaneSparse.c can
 * be compiled together by the host self-check without colliding. */
static u32 blp_load_u32(u32 address)
{
    return *(const u32 *)(unsigned long)address;
}

static void blp_store_u32(u32 address, u32 value)
{
    *(volatile u32 *)(unsigned long)address = value;
}

/* ------------------------------------------------------------------------- */
/* 0x087B7C80 - 76 bytes - 19 instructions                                    */
/*                                                                            */
/* r0 = destination, r1 = source, r2 = a 256-byte table, r3 = count in BYTES  */
/*                                                                            */
/* out.lane k = (in.lane k == 0) ? 0 : table[in.lane k]                       */
/*                                                                            */
/* The lane map is the IDENTITY. Every count is in BYTES and the pass stride is */
/* four. The `str` is unconditional; only the table reads are predicated.     */
/* ------------------------------------------------------------------------- */
void sub_087B7C80(u32 destination, u32 source, const u8 *table, u32 count)
{
    /* The counter is the register itself: decremented by four at the end of
     * each pass, exit on exactly zero. No pre-test is added, because the
     * original has none - a zero count therefore wraps the counter and runs
     * 2^30 passes, and a count that is not a multiple of four never reaches
     * zero and never terminates. */
    while (count != 0u) {
        const u32 word = blp_load_u32(source);
        const u32 lane0 = word & LANE_MASK;
        const u32 lane1 = (word >> 8) & LANE_MASK;
        const u32 lane2 = (word >> 16) & LANE_MASK;
        const u32 lane3 = (word >> 24) & LANE_MASK;

        /* `ands` sets Z on each lane and the following `ldrbne` is predicated on
         * it, so a zero lane never reads the table at all - not even table[0].
         * That is stated as a conditional expression rather than folded away. */
        blp_store_u32(
            destination,
            (lane0 != 0u ? (u32)table[lane0] : 0u)
            | (lane1 != 0u ? ((u32)table[lane1] << 8) : 0u)
            | (lane2 != 0u ? ((u32)table[lane2] << 16) : 0u)
            | (lane3 != 0u ? ((u32)table[lane3] << 24) : 0u));

        source += LANE_STRIDE;
        destination += LANE_STRIDE;
        count -= LANE_STRIDE;
    }
}

/*
 * The second member of the family, 0x087B7CD4, is NOT here. It is a separate
 * translation unit (src/IwramByteLaneSparse.c) because eight bytes of a THIRD
 * routine's literal pool sit between the two addresses, so no contiguous unit
 * contains both. The family analysis above still covers it.
 */
