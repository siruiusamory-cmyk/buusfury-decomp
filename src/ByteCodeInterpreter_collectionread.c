/*
 * src/ByteCodeInterpreter_collectionread.c
 *
 * DECOMPILED SOURCE for sub_08011C70: the first reader of the collection carried
 * by the IWRAM object 0x03001C4C that the append routine sub_0801191A fills.
 *
 *   0x08011C70  88 bytes  44 instructions  one terminator at 0x08011CC8
 *
 * It is called WITH that object in r0, from at least 0x08001E1E, and it is a LEAF
 * apart from the virtual call it makes through a method pointer.
 *
 * THE ROUTINE
 *   0x08011C72  ldr  r4, [r0, #4]      r4 = *(object + 4)   <- THE COUNT
 *   0x08011C74  adds r7, r0, #0        r7 = the collection base
 *   0x08011C78  adds r5, r1, #0        r5 = arg2
 *   0x08011C76  adds r6, r2, #0        r6 = arg3
 *   0x08011C7A  subs r4, #1            i = count - 1        <- BACKWARD from the top
 *   0x08011C7C  bmi  0x08011CA0        an empty collection is skipped
 *   loop 1:
 *   0x08011C84  lsls r0, r4, #2
 *   0x08011C86  adds r0, r0, r1        (r1 = base + 4)
 *   0x08011C88  ldr  r0, [r0, #4]      element = *(base + 8 + 4*i)
 *   0x08011C8A  ldr  r1, [r0]          r1 = *(element)      <- the element's TABLE pointer
 *   0x08011C8C  ldr  r2, [r1, #0x24]   r2 = table[9]
 *   0x08011C8E  adds r3, r2, r1        r3 = table + table[9] = THE METHOD
 *   0x08011C90  adds r2, r6, #0        arg3
 *   0x08011C92  adds r1, r5, #0        arg2
 *   0x08011C94  bl   0x08046AA6        the `bx r3` thunk: call the method
 *   0x08011C98  cmp  r0, #0
 *   0x08011C9A  bne  0x08011CC8        A NON-ZERO RESULT IS RETURNED AT ONCE
 *   0x08011C9C  subs r4, #1
 *   0x08011C9E  bpl  loop 1            while i >= 0
 *   0x08011CA0  ldr  r0, [pc, #0x100]  r0 = 0x40C
 *   0x08011CA2  adds r7, r7, r0        r7 = object + 0x40C
 *   loop 2:                            THE SAME SEARCH OVER A SECOND COLLECTION
 *   0x08011CA4  ldr  r4, [r7]          count2 = *(object + 0x40C)
 *   ... the same body, elements at *(object + 0x410 + 4*i)
 *   0x08011CC6  movs r0, #0            nothing matched
 *   0x08011CC8  pop  {r3-r7, pc}       the single exit
 *
 * WHAT IT IS
 * A SEARCH over the collection, performed by VIRTUAL DISPATCH:
 *
 *     for i = count-1 down to 0:
 *         if element[i]->method(a, b) != 0:  return that value
 *     return 0
 *
 * Each ELEMENT IS A POINTER to an object whose FIRST WORD is a pointer to a
 * dispatch table, and the routine calls the method at offset +0x24 of that table,
 * passing the two incoming arguments straight through. The first element whose
 * method returns non-zero WINS and its result is returned immediately.
 *
 * THE COLLECTION LAYOUT, NOW PROVEN FROM A THIRD ROUTINE
 *   base + 0x00  not touched by this routine
 *   base + 0x04  u32 COUNT
 *   base + 0x08  u32 elements[count], each a POINTER to a virtual object
 * which is exactly the shape the append routine established, derived here from
 * independently different instructions.
 *
 * CAPACITY EVIDENCE, FOUND HERE AND NOT INFERRED
 * The routine searches a SECOND collection of the SAME SHAPE at `object + 0x408`:
 * its count is at `object + 0x40C` and its elements from `object + 0x410`. So the
 * object carries TWO collections, 0x408 bytes apart. That spacing is a measured
 * fact of this routine's own code, not an inference from adjacency.
 *
 * TRAVERSAL SEMANTICS
 *   * order: FROM THE HIGHEST INDEX DOWNWARD. The index starts at count-1 and the
 *     loop continues while it is non-negative, so the most recently appended
 *     element is tested FIRST.
 *   * element width: 32-bit pointers.
 *   * the count is READ ONLY. This reader never writes it.
 *   * count 0: `subs` makes the index -1 and the `bmi` skips the loop entirely, so
 *     an empty collection causes no call at all.
 *
 * THE VIRTUAL CALL
 * The original reaches the method through the `bx r3` thunk at 0x08046AA6, a
 * trampoline the original toolchain emitted for an indirect call. This
 * reconstruction expresses the same operation as a plain call through a function
 * pointer, which is what the trampoline achieves; the trampoline itself is a
 * code-generation artefact and no external symbol is introduced by modelling it
 * this way.
 *
 * THERE IS NO BOUNDS CHECK on the count and no null check on an element, and none
 * was added.
 *
 * STATUS, and these three lines are INDEPENDENT of one another.
 *   SEMANTIC.....PROVEN   the traversal order, the element dereference, the method
 *                         offset, the argument forwarding, the stop-on-non-zero
 *                         rule, the empty-collection skip and the second collection
 *                         are checked by RUNNING them; see
 *                         src/probes/collectionread_selftest.c.
 *   MODERN_BUILD.PASS     it compiles and links for ARM7TDMI Thumb with the modern
 *                         toolchain; see docs/LIFT_COLLECTIONREAD.md.
 *   ADS_MATCH....BLOCKED  never compiled by the tool it targets. The ADS 1.2
 *                         binaries are present on this machine but the licence
 *                         present covers a different product (ADS12_LICENSE_UNAVAILABLE).
 *                         No byte-match claim is made.
 *
 * WHAT IS UNKNOWN
 *   - what the collection holds and what its elements are. The elements are virtual
 *     objects and the method called is at a fixed table offset, but no semantic name
 *     is assigned to the element type, the method or the collection;
 *   - how large the two collections may grow. Nothing here bounds either;
 *   - what the object's +0x00 field is. THIS ROUTINE DOES NOT TOUCH IT.
 *
 * The original file may NOT be copied from 2genkidev/buusfury: that repository
 * carries no licence grant. See docs/REFERENCE_AUDIT.md.
 */

typedef unsigned int u32;
typedef unsigned char u8;

/* ------------------------------------------------------------------------- */
/* the virtual method offset, from `ldr r2, [r1, #0x24]`                      */
/* ------------------------------------------------------------------------- */
#define COLLECTION_METHOD_OFFSET 0x24u
#define COLLECTION_COUNT_OFFSET  4u
#define COLLECTION_VALUES_OFFSET 8u
#define SECOND_COLLECTION_OFFSET 0x408u

/* ------------------------------------------------------------------------- */
/* One virtual call on one element                                            */
/* ------------------------------------------------------------------------- */
/*
 * r3 = table + table[9] is the method address and the two incoming arguments are
 * passed through, so the original is a call through a function pointer taken out of
 * the element's table.
 */
static u32 call_element_method(u32 element, u32 a, u32 b)
{
    u32 *table = *(u32 **)element;                       /* ldr r1,[r0]      */
    u32 offset = *(u32 *)((u8 *)table + COLLECTION_METHOD_OFFSET);
    u32 (*method)(u32, u32) = (u32 (*)(u32, u32))((u8 *)table + offset);
    return method(a, b);                                 /* the `bx r3` thunk */
}

/* ------------------------------------------------------------------------- */
/* The search over ONE collection                                             */
/* ------------------------------------------------------------------------- */
static u32 search_collection(void *base, u32 a, u32 b)
{
    u32 count = *(u32 *)((u8 *)base + COLLECTION_COUNT_OFFSET);
    u32 i;

    if (count == 0u) {
        return 0u;              /* the `subs`/`bmi` pair skips the loop entirely */
    }

    i = count - 1u;             /* BACKWARD from the most recent element */
    for (;;) {
        u32 element = *(u32 *)((u8 *)base + COLLECTION_VALUES_OFFSET + 4u * i);
        u32 result = call_element_method(element, a, b);

        if (result != 0u) {
            return result;      /* the first non-zero result wins, at once */
        }
        if (i == 0u) {
            break;
        }
        i -= 1u;
    }
    return 0u;
}

/* ------------------------------------------------------------------------- */
/* 0x08011C70 - 88 bytes - 44 instructions                                    */
/* ------------------------------------------------------------------------- */
u32 sub_08011C70(void *object, u32 a, u32 b)
{
    u32 result = search_collection(object, a, b);

    if (result != 0u) {
        return result;
    }
    /* The same search over the SECOND collection, 0x408 bytes further on. */
    return search_collection((u8 *)object + SECOND_COLLECTION_OFFSET, a, b);
}

/* ------------------------------------------------------------------------- */
/* The unit's literal words, as declared data                                 */
/* ------------------------------------------------------------------------- */
/*
 * Two words, both small constants rather than addresses: 0x0000040C, the offset to
 * the second collection, and the count clamp helper's literals. They are NOT
 * adjacent to the code.
 */
const u32 bci_collectionread_literal_pool[1] = {
    0x0000040Cu
};
