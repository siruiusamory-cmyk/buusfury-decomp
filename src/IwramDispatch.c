/*
 * src/IwramDispatch.c
 *
 * DECOMPILED SOURCE for the interrupt entry of the ARM code block the boot code
 * copies into IWRAM: the routine the machine runs when any enabled interrupt
 * fires.
 *
 *   ROM   0x087B8510..0x087B863C   ARM   300 bytes   75 instructions
 *   IWRAM 0x03000B6C..0x03000C98
 *
 * The same 4100-byte block is the subject of src/IwramBlock.c. The ROM-to-IWRAM
 * map is IWRAM X == ROM 0x087B79A4 + (X - 0x03000000), because the arm7tdmi
 * reset code at 0x080000C0 sets DMA3 up a second time with SAD = 0x087B79A4,
 * DAD = 0x03000000 and the 32-bit control word 0x84000401 (0x0401 words = 4100
 * bytes, both addresses incrementing). That map is CONFIRMED from the reset
 * code's own instructions and literal pool and is what makes this routine
 * statically known at all: it executes from IWRAM but its bytes are in the
 * cartridge.
 *
 * WHY THERE IS NO CALL SITE FOR IT
 * The Thumb routine at ROM 0x0803F3DA (a 26-byte prologue-less function whose
 * pool is at 0x0803F434..0x0803F440, not adjacent to it) loads the literal
 * 0x03000B6C and stores it into the GBA BIOS IRQ vector pointer at IWRAM
 * 0x03007FFC, which it computes as 0x03007FC0 + 0x3C. So the address is a
 * literal pool word read by exactly one instruction, and the entry is a
 * hardware vector rather than a call site. Nothing in the image calls it.
 *
 * WHAT IT DOES, in effect order
 *
 *   1. r3 = 0x04000000, then the PRE-INDEXED load `ldr r2, [r3, #0x200]!`
 *      moves r3 to 0x04000200 and reads one 32-bit word there. On this machine
 *      that word is REG_IE in its low half and REG_IF in its high half, so
 *      r2 = (IF << 16) | IE. The writeback is load-bearing: without it the four
 *      later register accesses would land on the wrong addresses.
 *   2. r1 = the 16-bit REG_IME at 0x04000208, r0 = SPSR, then
 *      `push {r0,r1,r2,r3,r4,r5,lr}` and REG_IME = 1.
 *   3. `and r1, r2, r2, lsr #16` confines the scan to the 16 bits of IE & IF.
 *      The shift is why no test above bit 15 can ever fire: the shifted
 *      operand's own high half is zero, so r1's bits 16..31 are zero by
 *      construction. That is read off the instruction, not imported from a
 *      register map.
 *   4. A 14-test priority chain. The first test is special and the rest are one
 *      shape: Acknowledge the served bit and call the handler for it.
 *   5. Acknowledge: clear the served bit in IE (except for the first test, see
 *      THE ARTIFACTS) and set it in IF, THEN store BOTH halves with ONE 32-bit
 *      store to 0x04000200, BEFORE the handler runs. On this machine a 1
 *      written to an IF bit clears that flag, which is what makes the write the
 *      acknowledgement; that hardware behaviour is INFERRED and is not stated
 *      by these instructions.
 *   6. Accumulate the served mask into the 16-bit software pending word at
 *      IWRAM 0x03000FE8 (vector-table base + 0x38): `ldrh`, `orr`, `strh`.
 *   7. SPSR-mode walk: read CPSR, clear its I bit, OR in the mode value the
 *      chain parked in ip (0x9F for the first test, 0x1F for the rest), write
 *      it to CPSR, push LR onto the mode's own stack, set LR to the odd Thumb
 *      address 0x03000C99, load the handler from the vector table and `bx r0`.
 *   8. The handler returns through the Thumb halfword 0x4720 (`bx r4`) at IWRAM
 *      0x03000C98, which continues at 0x03000C7C: pop LR, restore CPSR from the
 *      value read in step 7, then fall into the common exit.
 *   9. Exit: pop the seven registers, restore REG_IE from the saved low half,
 *      restore REG_IME, write SPSR back, `bx lr`.
 *
 * THE PRIORITY CHAIN, in test order. Each row is (test mask, byte offset the
 * entry is parked in r4, vector slot = offset/4). The masks were re-derived
 * from the test words by applying the ARM immediate rotation; the offsets are
 * the `mov r4, #imm` that precedes each test.
 *
 *   #   mask     r4     slot   bit   note
 *   1   0x0400   0x28   10     10    taken to the ORR, so the IE clear is SKIPPED
 *   2   0x0080   0x1C    7      7
 *   3   0x0040   0x18    6      6
 *   4   0x0001   0x00    0      0
 *   5   0x0002   0x04    1      1
 *   6   0x0004   0x08    2      2
 *   7   0x0008   0x0C    3      3
 *   8   0x0010   0x10    4      4
 *   9   0x0020   0x14    5      5
 *  10   0x0100   0x20    8      8
 *  11   0x0200   0x24    9      9
 *  12   0x0800   0x2C   11     11
 *  13   0x1000   0x30   12     12
 *  14   0x2000   (0x30) (13)   13    NOT served: falls into the self-branch
 *
 * THE ARTIFACTS. Each is reproduced, not repaired.
 *
 *   * The FIRST test (mask 0x0400) branches to the ORR, not to the BIC, so the
 *     served bit is NOT cleared in IE on that path. The write still sets the
 *     bit in IF. This is not a reading error: 0x1A000028 at 0x087B853C has
 *     target 0x087B85E4, and the BIC is at 0x087B85E0. Reproduced exactly.
 *   * If bit 13 is the highest pending enabled bit, control reaches the
 *     one-instruction self-branch `b 0x03000C38` (word 0xEAFFFFFE) and SPINS
 *     FOREVER. It is not served and it is not an error path: the original does
 *     this. The spin is reproduced with an unbounded loop and the self-check
 *     proves it does not terminate.
 *   * Bits 14 and 15 are tested by nothing. An interrupt whose only enabled and
 *     pending bit is 14 or 15 falls through the last test's zero result to the
 *     restore branch: it is never serviced and its flags are never touched.
 *   * Slot 13 (vector byte offset 0x34) is never selected by any path, even
 *     though bit 12 and the bit-13 test both leave 0x30 in r4.
 *
 * THE VECTOR TABLE
 * 14 words at IWRAM 0x03000FB0 (ROM 0x087B8954), every entry 0x0803F3D9 in the
 * cartridge: a Thumb pointer to 0x0803F3D8, which is the single halfword 0x4770
 * `bx lr`. At runtime ROM 0x0803F21A writes 0x03000AE0 into entry 10 and enables
 * REG_IE bit 10, so that slot is replaced before this routine can see it. The
 * table is 0x38 bytes long and the routine's software pending word is the
 * halfword immediately after it. The table is NOT reconstructed here: it is
 * data the boot image installs and runtime code rewrites, and this unit's ROM
 * extent ends at the dispatcher's `bx lr`.
 *
 * WHICH INSTRUCTIONS ARE **NOT** REPRESENTED AS C, AND WHY
 * Three machine facilities have no C spelling at all, and one return path is a
 * property of the instruction set rather than of the program. They are modelled
 * as environment calls. Each is declared here and also given a WEAK default
 * definition, so that this translation unit links on its own for the
 * modern-build verdict; the host self-check defines IWRAMDISPATCH_HOST_TEST and
 * supplies its own definitions, which is where the behaviour is measured. The
 * defaults carry no machine behaviour:
 *
 *   env_read_spsr()             `mrs r0, spsr` at 0x03000B78
 *   env_write_spsr(value)       `msr spsr_fsxc, r0` at 0x03000C90
 *   env_read_cpsr()             `mrs r5, apsr` at 0x03000C58
 *   env_enter_handler_mode(v)   `msr cpsr_c, r0` at 0x03000C64 AND the banked
 *                               stack switch it performs
 *   env_leave_handler_mode(v)   `msr cpsr_fsxc, r5` at 0x03000C80
 *   env_enter_handler(target)   `ldr r0,[r1,r4]` + the odd LR and `bx r0`
 *
 *   - SPSR has no C representation. `mrs`/`msr` move a processor status
 *     register whose banked copy belongs to the exception mode; no C object can
 *     name it, so the read and the write are environment calls and the value is
 *     carried in an ordinary local in between, exactly as the pushed word is.
 *   - The CPSR mode switch is privileged state: `msr cpsr_c, r0` changes the
 *     current mode, which swaps in a different SP (and LR) bank, and it changes
 *     the I and F interrupt-mask bits. C cannot express "change the mode this
 *     code is running in", so the switch and the stack bank it selects are one
 *     environment call. The `str lr, [sp, #-4]!` at 0x03000C68 and the
 *     `pop {lr}` at 0x03000C7C are part of that same mechanism: they write and
 *     read the handler-mode stack, and their only purpose is to preserve LR
 *     across the handler call, which is the C call ABI's own job. They emit no
 *     C statement.
 *   - `bx r0` into a Thumb handler, with LR set to the ODD address 0x03000C99
 *     so the handler returns in Thumb state to the halfword 0x4720 at IWRAM
 *     0x03000C98, which is `bx r4` and continues at 0x03000C7C: an
 *     ARM -> Thumb -> ARM interworking return that C cannot express. It is one
 *     environment call that must RETURN when the handler returns. The halfword
 *     at 0x03000C98 is an instruction of the OTHER instruction set and is not
 *     represented by any C statement here; it belongs to the same mechanism.
 *     The `add lr, pc, #0x25` and `add r4, pc, #0` that build those two
 *     addresses are likewise PC-relative materialisations of the interworking
 *     sequence, not values any C statement uses.
 *   - `push {r0,r1,r2,r3,r4,r5,lr}` / `pop {r0,r1,r2,r3,r4,r5,lr}` are
 *     represented by locals that stay live across the environment calls; the
 *     compiler's own frame performs the equivalent save and restore, and the
 *     popped r4/r5 values are dead at the `bx lr`. The pushed stack slots are
 *     not observable by the interrupted code.
 *   - `add r4, pc, #0` sets r4 to 0x03000C7C, which the Thumb island jumps
 *     back to. In C control simply resumes after the environment call.
 *   - The final `bx lr` is the C `return`.
 *
 * The register-to-local mapping is a placeholder, not evidence: the disassembly
 * fixes offsets, access widths and ordering, and the game's own names are not
 * recoverable. Statement order preserves the original's effect order (IME set
 * before the IE & IF computation, the acknowledge store before the handler, the
 * pending-word update before the mode switch, the restores after the return).
 * r5 holding the CPSR snapshot across the handler call is safe on the machine
 * because r5 is callee-saved in the ARM procedure call standard; in C the same
 * local stays live across a call by the language's own rule.
 *
 * STATUS, and these three lines are INDEPENDENT of one another.
 *   SEMANTIC.....PROVEN   the priority order, the acknowledge, the pending-word
 *                         accumulation, the restore path, all 13 reachable
 *                         slots, the skipped IE clear of the first test and
 *                         the bit-13 spin are checked by RUNNING this source;
 *                         see src/probes/iwramdispatch_selftest.c.
 *   MODERN_BUILD.PASS     arm-none-eabi-gcc 16.1.0, linked at 0x087B8510,
 *                         472 bytes emitted for this translation unit (the
 *                         reconstructed entry is 436 of them); the committed
 *                         measurement is config/lift_iwramdispatch.json. A
 *                         modern build is NOT a match: 257 of the 308 compared
 *                         bytes differ and no instruction span matches.
 *   ADS_MATCH....BLOCKED  never compiled by the tool it targets. The ADS 1.2
 *                         binaries present on this machine are licensed for a
 *                         different product (ADS12_LICENSE_UNAVAILABLE). No
 *                         byte-match claim is made.
 *
 * EVIDENCE vs PLACEHOLDER
 *   Evidence: every instruction, mask, byte offset, slot number and address
 *   above, all read from the cartridge and re-derived from its bytes; the
 *   14-entry table's contents; the install path through the Thumb routine at
 *   0x0803F3DA. Placeholder: the C types, the local names, and the environment
 *   call names. Whether the block was authored as C or as assembly is NOT
 *   established, and no library function name is claimed for this routine.
 *
 * The original may NOT be copied from 2genkidev/buusfury: that repository
 * carries no licence grant. See docs/REFERENCE_AUDIT.md.
 */

typedef unsigned int u32;
typedef unsigned short u16;

/* ------------------------------------------------------------------------- */
/* Machine facilities C cannot express. Declared here; supplied at link time   */
/* by the host self-check, and given a default definition below so that this    */
/* translation unit LINKS ON ITS OWN for the modern-build verdict.             */
/* ------------------------------------------------------------------------- */
extern u32  env_read_spsr(void);
extern void env_write_spsr(u32 value);
extern u32  env_read_cpsr(void);
extern void env_enter_handler_mode(u32 cpsr_value);
extern void env_leave_handler_mode(u32 cpsr_value);
extern void env_enter_handler(u32 target);

#ifndef IWRAMDISPATCH_HOST_TEST
/* The modern-build link compiles this file alone, and the harness binds only
 * symbols it can read out of the ROM's own BL instructions - these six are not
 * among them, so without a definition the link fails with six undefined
 * references. The defaults exist ONLY to satisfy that link: they are never
 * reached by the host self-check, which defines IWRAMDISPATCH_HOST_TEST and
 * supplies its own, and that is where the behaviour is actually measured.
 * Weak linkage satisfies GCC and ADS; the guard keeps MSVC, which has no weak
 * symbols, free of a duplicate definition when the self-check includes this
 * file. */
#if defined(__GNUC__)
#define IWRAMDISPATCH_ENV_WEAK __attribute__((weak))
#elif defined(__CC_ARM) || defined(__ARMCC_VERSION)
#define IWRAMDISPATCH_ENV_WEAK __weak
#else
#define IWRAMDISPATCH_ENV_WEAK
#endif
IWRAMDISPATCH_ENV_WEAK u32  env_read_spsr(void) { return 0u; }
IWRAMDISPATCH_ENV_WEAK void env_write_spsr(u32 value) { (void)value; }
IWRAMDISPATCH_ENV_WEAK u32  env_read_cpsr(void) { return 0u; }
IWRAMDISPATCH_ENV_WEAK void env_enter_handler_mode(u32 cpsr_value) { (void)cpsr_value; }
IWRAMDISPATCH_ENV_WEAK void env_leave_handler_mode(u32 cpsr_value) { (void)cpsr_value; }
IWRAMDISPATCH_ENV_WEAK void env_enter_handler(u32 target) { (void)target; }
#endif

/* ------------------------------------------------------------------------- */
/* Absolute machine state. Redirected by the host self-check.                  */
/* ------------------------------------------------------------------------- */
#ifdef IWRAMDISPATCH_HOST_TEST

extern u32 iwramdispatch_host_io_base;
extern u32 iwramdispatch_host_vector_base;
#define IWRAM_DISPATCH_IO_BASE     (iwramdispatch_host_io_base)
#define IWRAM_DISPATCH_VECTOR_BASE (iwramdispatch_host_vector_base)

#else  /* IWRAMDISPATCH_HOST_TEST */

/* The pre-indexed base: 0x04000000, assembled by `mov r3, #64, #12`. */
#define IWRAM_DISPATCH_IO_BASE     (0x04000000u)
/* The routine's one literal, loaded pc-relatively from 0x03000C9C. */
#define IWRAM_DISPATCH_VECTOR_BASE (0x03000FB0u)

#endif /* IWRAMDISPATCH_HOST_TEST */

/* Byte offsets inside the machine's I/O page. */
#define IWRAM_DISPATCH_IE_OFFSET   0x200u   /* REG_IE, low half of the word      */
#define IWRAM_DISPATCH_IME_OFFSET  0x008u   /* REG_IME, halfword at +0x208       */
/* The software pending halfword, relative to the vector table base. */
#define IWRAM_DISPATCH_PENDING_OFFSET 0x038u
/* The two CPSR mode values the chain parks in ip. Each is a mode number in its
 * low five bits; the first additionally leaves the I bit set. */
#define IWRAM_DISPATCH_MODE       0x1Fu
#define IWRAM_DISPATCH_MODE_I     0x9Fu

/* ------------------------------------------------------------------------- */
/* 0x087B8510 - 300 bytes - 75 instructions - the interrupt entry              */
/* No arguments, no return value: it is entered from the hardware vector and   */
/* returns to the instruction the interrupted code was executing.              */
/* ------------------------------------------------------------------------- */
void sub_087B8510(void)
{
    u32 r0;
    u32 r1;
    u32 r2;
    u32 r3;
    u32 r4;
    u32 r5;
    u32 ip;

    /* What the entry `push` stores, and what the exit `pop` brings back. */
    u32 saved_spsr;
    u32 saved_ime;
    u32 saved_word;
    u32 saved_io;

    /* 0x03000B6C  mov r3, #64, #12  ->  r3 = 0x04000000 */
    r3 = IWRAM_DISPATCH_IO_BASE;

    /* 0x03000B70  ldr r2, [r3, #0x200]!  ->  r3 = 0x04000200,
     * r2 = one 32-bit word = (REG_IF << 16) | REG_IE. */
    r3 = r3 + IWRAM_DISPATCH_IE_OFFSET;
    r2 = *(volatile u32 *)r3;

    /* 0x03000B74  ldrh r1, [r3, #8]  ->  REG_IME */
    r1 = (u32)*(volatile u16 *)(r3 + IWRAM_DISPATCH_IME_OFFSET);

    /* 0x03000B78  mrs r0, spsr  (environment: SPSR has no C representation) */
    r0 = env_read_spsr();

    /* 0x03000B7C  push {r0, r1, r2, r3, r4, r5, lr}
     * Modelled by these locals: a local stays live across the environment
     * calls by the language's own rule. The popped r4/r5 are dead at the
     * return, so only the four values the exit path reads are kept. */
    saved_spsr = r0;
    saved_ime = r1;
    saved_word = r2;
    saved_io = r3;

    /* 0x03000B80  mov r0, #1
     * 0x03000B84  strh r0, [r3, #8]  ->  REG_IME = 1 */
    *(volatile u16 *)(r3 + IWRAM_DISPATCH_IME_OFFSET) = 1u;

    /* 0x03000B88  and r1, r2, r2, lsr #16  ->  r1 = IE & IF, bits 16..31 zero
     * by construction. */
    r1 = r2 & (r2 >> 16);

    /* 0x03000B8C  mov ip, #0x9f
     * 0x03000B90  mov r4, #0x28 */
    ip = IWRAM_DISPATCH_MODE_I;
    r4 = 0x28u;

    /* 0x03000B94  ands r0, r1, #64, #28  ->  0x0400, bit 10.
     * 0x03000B98  bne 0x03000C40  ->  the ORR, NOT the BIC at 0x03000C3C.
     * This is why the first serviced bit is the one bit whose IE flag is not
     * cleared. Reproduced, not repaired. */
    r0 = r1 & 0x0400u;
    if (r0 != 0u) {
        goto iwram_dispatch_acknowledge_if_only;
    }

    /* 0x03000B9C  mov ip, #0x1f */
    ip = IWRAM_DISPATCH_MODE;

    /* 0x03000BA0  mov r4, #0x1c
     * 0x03000BA4  ands r0, r1, #0x80          bit 7
     * 0x03000BA8  bne 0x03000C3C */
    r4 = 0x1cu;
    r0 = r1 & 0x0080u;
    if (r0 != 0u) {
        goto iwram_dispatch_acknowledge;
    }

    /* 0x03000BAC  mov r4, #0x18
     * 0x03000BB0  ands r0, r1, #0x40          bit 6
     * 0x03000BB4  bne 0x03000C3C */
    r4 = 0x18u;
    r0 = r1 & 0x0040u;
    if (r0 != 0u) {
        goto iwram_dispatch_acknowledge;
    }

    /* 0x03000BB8  mov r4, #0
     * 0x03000BBC  ands r0, r1, #1             bit 0
     * 0x03000BC0  bne 0x03000C3C */
    r4 = 0x00u;
    r0 = r1 & 0x0001u;
    if (r0 != 0u) {
        goto iwram_dispatch_acknowledge;
    }

    /* 0x03000BC4  mov r4, #4
     * 0x03000BC8  ands r0, r1, #2             bit 1
     * 0x03000BCC  bne 0x03000C3C */
    r4 = 0x04u;
    r0 = r1 & 0x0002u;
    if (r0 != 0u) {
        goto iwram_dispatch_acknowledge;
    }

    /* 0x03000BD0  mov r4, #8
     * 0x03000BD4  ands r0, r1, #4             bit 2
     * 0x03000BD8  bne 0x03000C3C */
    r4 = 0x08u;
    r0 = r1 & 0x0004u;
    if (r0 != 0u) {
        goto iwram_dispatch_acknowledge;
    }

    /* 0x03000BDC  mov r4, #0xc
     * 0x03000BE0  ands r0, r1, #8             bit 3
     * 0x03000BE4  bne 0x03000C3C */
    r4 = 0x0cu;
    r0 = r1 & 0x0008u;
    if (r0 != 0u) {
        goto iwram_dispatch_acknowledge;
    }

    /* 0x03000BE8  mov r4, #0x10
     * 0x03000BEC  ands r0, r1, #0x10          bit 4
     * 0x03000BF0  bne 0x03000C3C */
    r4 = 0x10u;
    r0 = r1 & 0x0010u;
    if (r0 != 0u) {
        goto iwram_dispatch_acknowledge;
    }

    /* 0x03000BF4  mov r4, #0x14
     * 0x03000BF8  ands r0, r1, #0x20          bit 5
     * 0x03000BFC  bne 0x03000C3C */
    r4 = 0x14u;
    r0 = r1 & 0x0020u;
    if (r0 != 0u) {
        goto iwram_dispatch_acknowledge;
    }

    /* 0x03000C00  mov r4, #0x20
     * 0x03000C04  ands r0, r1, #64, #30       bit 8 (0x100)
     * 0x03000C08  bne 0x03000C3C */
    r4 = 0x20u;
    r0 = r1 & 0x0100u;
    if (r0 != 0u) {
        goto iwram_dispatch_acknowledge;
    }

    /* 0x03000C0C  mov r4, #0x24
     * 0x03000C10  ands r0, r1, #128, #30      bit 9 (0x200)
     * 0x03000C14  bne 0x03000C3C */
    r4 = 0x24u;
    r0 = r1 & 0x0200u;
    if (r0 != 0u) {
        goto iwram_dispatch_acknowledge;
    }

    /* 0x03000C18  mov r4, #0x2c
     * 0x03000C1C  ands r0, r1, #128, #28      bit 11 (0x800)
     * 0x03000C20  bne 0x03000C3C */
    r4 = 0x2cu;
    r0 = r1 & 0x0800u;
    if (r0 != 0u) {
        goto iwram_dispatch_acknowledge;
    }

    /* 0x03000C24  mov r4, #0x30
     * 0x03000C28  ands r0, r1, #64, #26       bit 12 (0x1000)
     * 0x03000C2C  bne 0x03000C3C */
    r4 = 0x30u;
    r0 = r1 & 0x1000u;
    if (r0 != 0u) {
        goto iwram_dispatch_acknowledge;
    }

    /* 0x03000C30  ands r0, r1, #128, #26      bit 13 (0x2000)
     * 0x03000C34  beq 0x03000C84  ->  nothing pending: restore and return */
    r0 = r1 & 0x2000u;
    if (r0 == 0u) {
        goto iwram_dispatch_restore_and_return;
    }

    /* 0x03000C38  b 0x03000C38  ->  word 0xEAFFFFFE, a branch to itself.
     * The original SPINS FOREVER on a pending enabled bit 13. There is no
     * guard here and none may be added: this is the machine's behaviour. */
    for (;;) {
        /* deliberately empty: the branch has no side effect */
    }

    /* --------------------------------------------------------------------- */
    /* 0x03000C3C  bic r2, r2, r0  - clear the served bit in IE               */
    /* --------------------------------------------------------------------- */
iwram_dispatch_acknowledge:
    r2 = r2 & ~r0;

    /* --------------------------------------------------------------------- */
    /* 0x03000C40  orr r2, r2, r0, lsl #16  - set the served bit in IF        */
    /* Reached by fall-through from the BIC and directly by the first test.   */
    /* --------------------------------------------------------------------- */
iwram_dispatch_acknowledge_if_only:
    r2 = r2 | (r0 << 16);

    /* 0x03000C44  str r2, [r3]  - ONE 32-bit store writes both halves, BEFORE
     * the handler runs. */
    *(volatile u32 *)r3 = r2;

    /* 0x03000C48  ldr r1, [pc, #0x4c]  ->  the literal 0x03000FB0 */
    r1 = IWRAM_DISPATCH_VECTOR_BASE;

    /* 0x03000C4C  ldrh r5, [r1, #0x38]  ->  the software pending halfword */
    r5 = (u32)*(volatile u16 *)(r1 + IWRAM_DISPATCH_PENDING_OFFSET);

    /* 0x03000C50  orr r5, r5, r0  - ACCUMULATE the served mask */
    r5 = r5 | r0;

    /* 0x03000C54  strh r5, [r1, #0x38] */
    *(volatile u16 *)(r1 + IWRAM_DISPATCH_PENDING_OFFSET) = (u16)r5;

    /* 0x03000C58  mrs r5, apsr  (environment: the CPSR is not a C object) */
    r5 = env_read_cpsr();

    /* 0x03000C5C  bic r0, r5, #0x80  - clear the I bit
     * 0x03000C60  orr r0, r0, ip     - OR in the mode the chain selected
     *                                  (0x9f for bit 10, 0x1f otherwise) */
    r0 = (r5 & ~0x80u) | ip;

    /* 0x03000C64  msr cpsr_c, r0  (environment: a privileged mode switch with
     * a banked SP; C cannot change the mode this code runs in) */
    env_enter_handler_mode(r0);

    /* 0x03000C68  str lr, [sp, #-4]!  - handler-mode stack, no C statement
     * 0x03000C6C  add lr, pc, #0x25   - lr = 0x03000C99, ODD: Thumb return
     * 0x03000C74  add r4, pc, #0     - r4 = 0x03000C7C, the resume address
     * 0x03000C70  ldr r0, [r1, r4]   - the handler for the selected slot */
    r0 = *(volatile u32 *)(r1 + r4);

    /* 0x03000C78  bx r0  (environment: ARM -> Thumb -> ARM interworking; the
     * handler returns through the Thumb halfword 0x4720 at IWRAM 0x03000C98).
     * Control resumes at 0x03000C7C when it returns. */
    env_enter_handler(r0);

    /* 0x03000C7C  pop {lr}
     * 0x03000C80  msr cpsr_fsxc, r5  - restore the CPSR snapshot taken above */
    env_leave_handler_mode(r5);

    /* --------------------------------------------------------------------- */
    /* 0x03000C84  the common exit, reached by fall-through from the restore  */
    /* and directly by the last test's `beq`.                                 */
    /* --------------------------------------------------------------------- */
iwram_dispatch_restore_and_return:
    /* 0x03000C84  pop {r0, r1, r2, r3, r4, r5, lr} */
    r0 = saved_spsr;
    r1 = saved_ime;
    r2 = saved_word;
    r3 = saved_io;

    /* 0x03000C88  strh r2, [r3]  - restore REG_IE from the saved LOW half */
    *(volatile u16 *)r3 = (u16)r2;

    /* 0x03000C8C  strh r1, [r3, #8]  - restore REG_IME */
    *(volatile u16 *)(r3 + IWRAM_DISPATCH_IME_OFFSET) = (u16)r1;

    /* 0x03000C90  msr spsr_fsxc, r0  (environment) */
    env_write_spsr(r0);

    /* 0x03000C94  bx lr  - the C return */
}

/* ------------------------------------------------------------------------- */
/* The unit's literal pool, as declared data                                  */
/* ------------------------------------------------------------------------- */
/*
 * One word at ROM 0x087B8640, loaded at 0x03000C48 by `ldr r1, [pc, #0x4c]`.
 * The four bytes between the code and it, 0x087B863C..0x087B8640, are the
 * Thumb halfword 0x4720 the handler returns through; they are not part of this
 * translation unit's code. The same word is materialised by the compiler in
 * the body above, because IWRAM_DISPATCH_VECTOR_BASE is an address constant.
 */
const u32 iwram_dispatch_literal_pool[1] = {
    0x03000FB0u
};
