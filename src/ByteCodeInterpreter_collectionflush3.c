/*
 * src/ByteCodeInterpreter_collectionflush3.c
 *
 * DECOMPILED SOURCE for sub_0801157E: the routine that operates on the object's
 * THIRD region, the one at object + 0x208.
 *
 *   0x0801157E  50 bytes  23 instructions  one terminator at 0x080115AE
 *
 * THE ROUTINE
 *   0x08011580  adds r4, r0, #0            r4 = the object
 *   0x08011582  ldr  r0, [lit]             r0 = 0x08072824
 *   0x08011584  ldr  r0, [r0]              r0 = *(u32 *)0x08072824
 *   0x08011586  bl   0x0803DA62            a global consumer
 *   0x0801158A  movs r0, #0x41
 *   0x0801158C  lsls r0, r0, #3            r0 = 0x208
 *   0x0801158E  adds r5, r4, r0            r5 = object + 0x208   <- THE COUNT SLOT
 *   0x08011590  ldr  r4, [r5]              r4 = count
 *   0x08011592  subs r4, #1                BACKWARD from count-1
 *   0x08011594  bmi  0x080115AA            an empty count skips the loop
 *   0x08011596  lsls r0, r4, #2
 *   0x08011598  adds r0, r0, r5
 *   0x0801159A  ldr  r0, [r0, #4]          element = *(object + 0x20C + 4*i)
 *   0x0801159C  ldr  r1, [r0]              r1 = the element's table
 *   0x0801159E  ldr  r2, [r1, #0x14]       r2 = table[+0x14]
 *   0x080115A0  adds r1, r2, r1            the method
 *   0x080115A2  bl   0x08046AA2            the `bx r1` thunk: call it
 *   0x080115A6  subs r4, #1
 *   0x080115A8  bpl  0x08011596            while i >= 0
 *   0x080115AA  movs r0, #0
 *   0x080115AC  str  r0, [r5]              COUNT = 0          <- THE FLUSH
 *   0x080115AE  pop  {r3, r4, r5, pc}      the single exit
 *
 * WHAT IT IS
 *
 *     for i = third.count-1 DOWN TO 0:
 *         third.elements[i]->table[+0x14](third.elements[i])
 *     third.count = 0
 *
 * It drains the third region, calling one virtual method per element, and then sets
 * the count to zero. It never writes an element and never increments a count, so it
 * is a DRAIN, not a population path.
 *
 * THE THIRD REGION'S SHAPE, PROVEN FROM THIS ROUTINE AND NOT FROM SPACING
 *   * count at object + 0x208, 32 bits
 *   * elements at object + 0x20C + 4*i, so 32 bits wide, and each is DEREFERENCED
 *     (`ldr r1,[r0]`) and used as a table pointer, so each element is a POINTER to a
 *     virtual object - the same element type as the other two collections;
 *   * the loop runs BACKWARD, like the reader's search and unlike the keyed move's
 *     forward scan;
 *   * the method called is at table + 0x14, which is a DIFFERENT slot from the first
 *     collection's destructor at +0x04, the second's at +0x04/+0x08, and the reader's
 *     search predicate at +0x24. The slot is therefore part of the third region's
 *     identity and not shared blindly with the others.
 *
 * THIS IS THE SAME OPERATION sub_08011732 PERFORMS INLINE
 * sub_08011732 contains the identical drain-and-zero at 0x080117CA..0x08011804, and
 * sub_0801157E is the standalone form of it. That both exist is evidence the
 * operation is a routine concept rather than incidental cleanup.
 *
 * THERE IS NO POPULATION PATH, AND THAT IS THE FINDING
 * The ticket asked how entries ENTER the third region. As far as ROM evidence allows,
 * THEY DO NOT:
 *   * no instruction in the image accesses the region by an immediate displacement,
 *     so the address is always computed;
 *   * 
 *   * EIGHT SITES IN THE IMAGE BUILD THE CONSTANT 0x208, found by scanning every byte for the movs/lsls pair in all its register forms and all its decompositions. Exactly THREE of them are in the collection cluster and use it as object + 0x208 for the object at 0x03001C4C: this routine at 0x0801158A, sub_08011732 at 0x080117CA, and sub_08011B04 at 0x08011B7A. ALL THREE WRITE ZERO TO THE COUNT AND NONE OF THEM WRITES AN ELEMENT. The other five sites
 *     - 0x080344CC, 0x08034A6A, 0x0804843E, 0x0804E9AE and 0x08054492 - are in unrelated routines that build the same numeric offset for other structures, and NONE of the eight performs the append shape (read a count at +0, increment, store an element at +4). An earlier revision of this comment claimed only three routines compute 0x208; that was WRONG and is corrected here.
 *   * a search of the whole image for a STORED POINTER to the region found ZERO
 *     occurrences of object+0x204, object+0x208 or object+0x20C, so no code can reach
 *     it through a pointer either, and a generic append could not be aimed at it;
 *   * sub_08011B04 additionally bulk-fills the ARRAY at object + 0x20C with 0x200
 *     bytes through an IWRAM-INSTALLED function pointer (the `bx pc` trampoline at
 *     0x0804912C jumps to whatever is stored at 0x030007A8). Its argument order is
 *     therefore NOT statically resolvable, and that single call is the only writer of
 *     the array area that this work cannot characterise.
 * The count is consequently zero on every path that can be read, which makes the
 * drain loop DEFENSIVE: it normally has nothing to do. Whether the bulk fill writes
 * ELEMENTS (which the zeroing count would then contradict) or unrelated data sharing
 * the address range is NOT established here.
 *
 * STATUS, and these three lines are INDEPENDENT of one another.
 *   SEMANTIC.....PROVEN   the backward drain, the method slot, the termination order
 *                         and the final zeroing are checked by RUNNING them; see
 *                         src/probes/collectionflush3_selftest.c.
 *   MODERN_BUILD.PASS     it compiles and links for ARM7TDMI Thumb with the modern
 *                         toolchain; see docs/LIFT_COLLECTIONFLUSH3.md.
 *   ADS_MATCH....BLOCKED  never compiled by the tool it targets. The ADS 1.2
 *                         binaries are present on this machine but the licence
 *                         present covers a different product (ADS12_LICENSE_UNAVAILABLE).
 *                         No byte-match claim is made.
 *
 * The original file may NOT be copied from 2genkidev/buusfury: that repository
 * carries no licence grant. See docs/REFERENCE_AUDIT.md.
 */

typedef unsigned int u32;
typedef unsigned char u8;

#define THIRD_COUNT_OFFSET   0x208u
#define THIRD_VALUES_OFFSET  0x20Cu
#define THIRD_METHOD_SLOT    0x14u

/* ------------------------------------------------------------------------- */
/* A symbol this unit references but does not reconstruct                     */
/* ------------------------------------------------------------------------- */
extern void sub_0803DA62(u32 value);

/* ------------------------------------------------------------------------- */
/* Absolute machine state. Redirected by the host self-check.                 */
/* ------------------------------------------------------------------------- */
#ifndef COLLECTIONFLUSH3_HOST_TEST

#define FLUSH3_GLOBAL_WORD (*(u32 *)0x08072824u)

#else  /* COLLECTIONFLUSH3_HOST_TEST */

extern u32 collectionflush3_host_global_word;
#define FLUSH3_GLOBAL_WORD (collectionflush3_host_global_word)

#endif /* COLLECTIONFLUSH3_HOST_TEST */

/* ------------------------------------------------------------------------- */
/* The virtual call, taken out of the element's own table                     */
/* ------------------------------------------------------------------------- */
static u32 call_element_method(u32 element, u32 slot)
{
    u32 table = *(u32 *)element;                 /* ldr r1,[r0]        */
    u32 offset = *(u32 *)(table + slot);         /* ldr r2,[r1,#slot]  */
    /* `adds r1, r2, r1` is a 32-BIT WRAPPING add and the offsets in this image are
     * large negative values, so the add is expressed in integer arithmetic. */
    u32 method = table + offset;
    u32 (*fn)(u32) = (u32 (*)(u32))method;
    return fn(element);
}

/* ------------------------------------------------------------------------- */
/* 0x0801157E - 50 bytes - 23 instructions                                    */
/* ------------------------------------------------------------------------- */
void sub_0801157E(void *object)
{
    u8 *base = (u8 *)object;
    u32 *count_slot = (u32 *)(base + THIRD_COUNT_OFFSET);
    u32 count;

    sub_0803DA62(FLUSH3_GLOBAL_WORD);

    count = *count_slot;
    if (count != 0u) {
        u32 i = count - 1u;                      /* BACKWARD from the top */
        for (;;) {
            u32 element = *(u32 *)(base + THIRD_VALUES_OFFSET + 4u * i);
            (void)call_element_method(element, THIRD_METHOD_SLOT);
            if (i == 0u) {
                break;
            }
            i -= 1u;
        }
    }
    *count_slot = 0u;                            /* THE FLUSH */
}

/* ------------------------------------------------------------------------- */
/* The unit's literal word, as declared data                                  */
/* ------------------------------------------------------------------------- */
const u32 bci_collectionflush3_literal_pool[1] = {
    0x08072824u
};
