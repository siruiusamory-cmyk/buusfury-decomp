/*
 * src/ByteCodeInterpreter_handlers.c
 *
 * DECOMPILED SOURCE for the ByteCodeInterpreter handler translation unit. The
 * ROM preserves the original source path for this subsystem as ASCII at
 * 0x08004160:
 *
 *     T:\Source\ByteCodeInterpreter\ByteCodeInterpreter.cpp
 *
 * The interpreter's own translation unit lives in src/ByteCodeInterpreter.c.
 * This file is a DIFFERENT unit for a provable reason: the two have separate
 * literal pools (this one's is at 0x08003F40, the interpreter's at 0x08004158)
 * and separate code, so they were separate objects in the original build.
 *
 * SCOPE: primary dispatch slot 2 only, entry 0x08003CBE. That is the handler
 * which reaches the 266-entry native table at 0x08055098. The other 30 primary
 * handlers and the native routines themselves are NOT reconstructed here.
 *
 *   0x08003CBE  22 bytes  10 instructions  one terminator at 0x08003CD2
 *
 * STATUS, and these three lines are INDEPENDENT of one another.
 *   SEMANTIC.....PROVEN   the handler's cursor handling, index decoding and
 *                         selection are checked by RUNNING it with recording
 *                         native routines; see src/probes/handler2_selftest.c.
 *   MODERN_BUILD.PASS     it compiles and links for ARM7TDMI Thumb with the
 *                         modern toolchain; see docs/LIFT_HANDLER2.md.
 *   ADS_MATCH....BLOCKED  never compiled by the tool it targets. The ADS 1.2
 *                         binaries are present on this machine but the licence
 *                         present covers a different product, so the ARM
 *                         compilers cannot be run (ADS12_LICENSE_UNAVAILABLE).
 *                         No byte-match claim is made.
 *
 * THE HANDLER, ALL TEN INSTRUCTIONS
 *   0x08003CBE  push {r3, lr}
 *   0x08003CC0  ldr  r3, [r1]        r3 = the cursor value from the slot
 *   0x08003CC2  ldrb r2, [r3]        r2 = ONE BYTE: the native index
 *   0x08003CC4  adds r3, #1          the cursor advances by ONE
 *   0x08003CC6  str  r3, [r1]        ... written back into the slot
 *   0x08003CC8  lsls r1, r2, #2      index * 4 -> word indexing
 *   0x08003CCA  ldr  r2, [pc, #0x274]   r2 = 0x08055098, the native table base
 *   0x08003CCC  ldr  r1, [r2, r1]    r1 = native[index]
 *   0x08003CCE  bl   0x08046AA2      the `bx r1` thunk
 *   0x08003CD2  pop  {r3, pc}        the single exit
 *
 * WHAT IS PROVEN
 *   - the handler receives r0 = context and r1 = the ADDRESS OF THE CURSOR SLOT,
 *     which is the contract the interpreter establishes at 0x0800408E/90;
 *   - it dereferences that slot, advances the cursor by exactly ONE byte, and
 *     writes it back BEFORE dispatching, so the native routine runs with the
 *     cursor already past the index byte;
 *   - the index is a SINGLE UNSIGNED BYTE, so its range is 0..255;
 *   - selection is `((void**)0x08055098)[index]`, word-indexed;
 *   - the call goes through the engine's thunk block: 0x08046AA0 is `bx r0`,
 *     0x08046AA2 `bx r1`, 0x08046AA4 `bx r2`, 0x08046AA6 `bx r3`. This handler
 *     uses `bx r1` with the selected routine in r1;
 *   - therefore the selected native routine is entered with r0 = the context,
 *     UNCHANGED. This handler never writes r0: it is context-transparent;
 *   - r1 at entry to the native routine is the routine's own address, because
 *     `bx r1` does not clear r1. That is an artifact of the thunk, not an
 *     argument. r3 holds the advanced cursor, also an artifact;
 *   - r2 holds the native table base at the call, because the indexed load at
 *     0x08003CCC does not disturb it. Whether any native routine consumes r2 is
 *     a separate question, measured below and answered no for the sample taken.
 *
 * THE HANDLER CANNOT INDEX OUT OF BOUNDS
 * The index is one byte, so it has 256 possible values, and the table has 266
 * entries. Every reachable index is therefore in range, and that is a property
 * of the two encodings rather than a check the code performs. There is no
 * bounds test in the handler and there does not need to be.
 *
 * THE NATIVE TABLE IS 266 ENTRIES, NOT 283
 * A prior claim in this repository said 283. That is refuted, and the mechanism
 * is recorded in docs/LIFT_HANDLER2.md: 283 entries at four bytes each reach
 * 0x08055504, which is INSIDE the primary dispatch table, and the primary table
 * is independently anchored and its own extent is proved. The table here is
 * bounded above by the primary table's base and below by the byte index:
 *   - index 255 reads 0x08055098 + 1020 = 0x08055494, so at least 256 entries;
 *   - the primary table base 0x080554C0 gives exactly 266;
 *   - all 266 words in that span are in-cartridge Thumb pointers, 265 distinct.
 *
 * WHAT IS UNKNOWN, AND DELIBERATELY LEFT UNKNOWN
 *   - what ANY native routine does. Not one is reconstructed, and no native
 *     index is given a name. No meaning is imported from another LoG title;
 *   - whether any native routine consumes r2. A sample of 12 was inspected for
 *     evidence about the calling convention and NONE of them read r2 before
 *     writing it, while 10 of 12 read r0. That is evidence for r0 being the
 *     argument and r2 being incidental, not proof about every entry;
 *   - why the cursor protocol differs between handlers. This one consumes one
 *     byte; the interpreter's own loop and handler 1 do not have to.
 *
 * The original file may NOT be copied from 2genkidev/buusfury: that repository
 * carries no licence grant. See docs/REFERENCE_AUDIT.md.
 */

typedef unsigned char u8;
typedef unsigned int u32;

/* The context is opaque here on purpose: this handler never dereferences it and
 * never writes r0, so it does not need to know its shape. That is a proven
 * property, not a simplification. */
typedef void *BciContextRef;

/* A native routine: entered with r0 = the context, returns nothing. */
typedef void (*BciNative)(BciContextRef ctx);

/* ------------------------------------------------------------------------- */
/* Symbols this unit references but does not reconstruct                      */
/* ------------------------------------------------------------------------- */
/* The engine's `bx rN` thunk block at 0x08046AA0. 0x08046AA2 is `bx r1`, and
 * the declaration below mirrors the register state the original establishes:
 * the context stays in r0 and the routine is in r1. */
extern void sub_08046AA2(BciContextRef ctx, BciNative routine);

/* ------------------------------------------------------------------------- */
/* The native dispatch table                                                  */
/* ------------------------------------------------------------------------- */
#define BCI_NATIVE_ENTRIES 266u

#ifndef HANDLER2_HOST_TEST

#define BCI_NATIVE_TABLE ((BciNative *)(0x08055098u))
/* Through the thunk, exactly as 0x08003CCE does. */
#define BCI_CALL_NATIVE(ctx, routine) (sub_08046AA2((ctx), (routine)))

#else  /* HANDLER2_HOST_TEST */

extern BciNative handler2_host_native[BCI_NATIVE_ENTRIES];
#define BCI_NATIVE_TABLE (handler2_host_native)
/* The host has no ARM thunk; calling the routine directly is the same operation
 * and the self-check observes the arguments either way. */
#define BCI_CALL_NATIVE(ctx, routine) ((routine)((ctx)))

#endif /* HANDLER2_HOST_TEST */

/* ------------------------------------------------------------------------- */
/* primary dispatch slot 2 - 0x08003CBE - 22 bytes - 10 instructions          */
/* ------------------------------------------------------------------------- */
/*
 * Reached ONLY through the primary dispatch table: a search of every evidenced
 * function in the image finds no direct BL site targeting it. The interpreter
 * dispatches it indirectly through `bx r2`, which is why a direct-call census
 * returns nothing and that absence is the expected result rather than a gap.
 *
 * The index byte is read from `*cursor_slot`, the slot is advanced by one and
 * written back, and then `native[index]` is called with the context untouched.
 */
void sub_08003CBE(BciContextRef ctx, u32 *cursor_slot)
{
    const u8 *cursor = (const u8 *)*cursor_slot;
    u8 index = *cursor;
    BciNative routine;

    /* Advanced BEFORE the dispatch, so the native routine sees a cursor that is
     * already past its own index byte (adds r3,#1 then str r3,[r1]). */
    cursor += 1u;
    *cursor_slot = (u32)cursor;

    routine = BCI_NATIVE_TABLE[index];
    BCI_CALL_NATIVE(ctx, routine);
}

/* ------------------------------------------------------------------------- */
/* The unit's literal word, as declared data                                  */
/* ------------------------------------------------------------------------- */
/*
 * The handler's pool sits at 0x08003F40 and holds one word, loaded at
 * 0x08003CCA by the code above. Four other primary handlers (slots 21, 22, 23
 * and 24) load from the same slot, which is what groups them into one unit.
 */
const u32 bci_handler2_literal_pool[1] = {
    0x08055098u   /* the 266-entry native dispatch table */
};
