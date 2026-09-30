/*
 * src/ByteCodeInterpreter_collectionwrite2.c
 *
 * DECOMPILED SOURCE for sub_080119BC: the routine that WRITES across the two
 * collections carried by the IWRAM object 0x03001C4C, and the one that reaches the
 * SECOND collection as a writer.
 *
 *   0x080119BC  98 bytes  48 instructions  one terminator at 0x080119E8
 *
 * It sits immediately after the first-collection append at 0x0801191A, and the two
 * are separate routines, not one routine at two offsets.
 *
 * THE ROUTINE
 *   0x080119BE  ldr  r6, [r0, #4]      count of the FIRST collection
 *   0x080119C0  adds r5, r2, #0        r5 = the VALUE (third argument)
 *   0x080119C4  adds r4, r0, #4        r4 = the first collection's count slot
 *   scan the FIRST collection FORWARD from index 0, comparing each element with r1,
 *   the KEY (second argument):
 *   0x080119CE  ldr  r3, [r3, #4]      elements[i]
 *   0x080119D0  cmp  r3, r1            equals the key?
 *   0x080119D2  beq  found
 *   0x080119DA  not found: r2 = -1
 *   0x080119E0  beq  0x080119EA        the key is absent, so go to the SECOND
 *   0x080119E6  str  r5, [r0, #4]      FOUND: elements[i] = VALUE, and the count is
 *                                      NOT touched
 *
 *   the key was absent from the first collection:
 *   0x080119EA  r2 = 0x40C
 *   0x080119EC  adds r0, r0, r2        r0 = object + 0x40C
 *   scan the SECOND collection the same way
 *   0x08011A0C  bl   0x0804FE54        REMOVE the key from the second collection
 *   0x08011A10  ldr  r0, [r4]          count of the FIRST
 *   0x08011A18  str  r1, [r4]          FIRST count = count + 1
 *   0x08011A1A  str  r5, [r0, #4]      first elements[count] = VALUE   <- APPEND
 *
 * WHAT IT IS
 *
 *     sub_080119BC(object, key, value):
 *         i = find the element EQUAL TO key in the FIRST collection
 *         if i >= 0:  first.elements[i] = value          REPLACE in place
 *         else:
 *             j = find the element EQUAL TO key in the SECOND collection
 *             if j >= 0:  remove  second.elements[j]     via sub_0804FE54
 *             append value to the FIRST collection
 *
 * So the routine is a MOVE ACROSS THE TWO COLLECTIONS, keyed on an element VALUE:
 * an entry that is only in the second collection is REMOVED from it and APPENDED to
 * the first; an entry already in the first is replaced where it stands. The SECOND
 * collection is therefore a writer TARGET only through the REMOVAL, and nothing in
 * this routine ever appends to it or changes its count except through that removal.
 *
 * THE SECOND COLLECTION IS REACHED BY A COMPUTED BASE, NOT A DISPLACEMENT
 * The routine adds 0x40C to the object base once, at 0x080119EC, and then works
 * through that register, which is why an image-wide search for stores at a
 * displacement near 0x40C finds NOTHING: the offset is folded into the base before
 * any access. That is also why the count it reads is at object + 0x40C and the
 * elements are at object + 0x410 + 4*i, the shape the reader sub_08011C70 proved.
 *
 * COMPARISON WITH THE FIRST APPEND ROUTINE sub_0801191A
 * They are NOT structurally equivalent at different offsets, and the difference is
 * real rather than assumed from their adjacency:
 *   * sub_0801191A is a GENERIC append: it takes any collection base, reads the
 *     count at base+4, appends and increments. Its callers pass many different bases
 *     - the object at 0x03001C4C, `*(r5+4)`, `*(r5)`, `*(r7+0xc)` - so it is not
 *     tied to this object or to either of its collections;
 *   * sub_080119BC is object-shaped: it hardcodes the 0x40C offset and KNOWS about
 *     both collections of this object. It never appends to a collection whose base
 *     it was not given, and it never increments the second collection's count.
 * They are therefore two members of ONE API FAMILY with DIFFERENT roles: a generic
 * append, and an object-specific keyed move.
 *
 * ORDER AND STORAGE
 *   * both scans run FORWARD from index 0, so the FIRST element equal to the key
 *     wins, which is the opposite direction from the reader's backward search;
 *   * the incoming value is stored VERBATIM, with no transformation;
 *   * the count is incremented ONLY on the append path, and only for the FIRST
 *     collection.
 *
 * NO CAPACITY CHECK, NO BOUNDS CHECK
 * Nothing compares either count against a limit before the append, and no element is
 * null checked. No guard was added.
 *
 * STATUS, and these three lines are INDEPENDENT of one another.
 *   SEMANTIC.....PROVEN   the two searches, the replace, the removal, the append and
 *                         the count rules are checked by RUNNING them; see
 *                         src/probes/collectionwrite2_selftest.c.
 *   MODERN_BUILD.PASS     it compiles and links for ARM7TDMI Thumb with the modern
 *                         toolchain; see docs/LIFT_COLLECTIONWRITE2.md.
 *   ADS_MATCH....BLOCKED  never compiled by the tool it targets. The ADS 1.2
 *                         binaries are present on this machine but the licence
 *                         present covers a different product (ADS12_LICENSE_UNAVAILABLE).
 *                         No byte-match claim is made.
 *
 * WHAT IS UNKNOWN
 *   - what the elements mean;
 *   - what sub_0804FE54 does beyond removing an entry, and whether it compacts;
 *   - what appends to the SECOND collection. This routine only removes from it, so
 *     the second collection's INSERTION path is still unfound;
 *   - the object's +0x00 field, which THIS ROUTINE DOES NOT TOUCH.
 *
 * The original file may NOT be copied from 2genkidev/buusfury: that repository
 * carries no licence grant. See docs/REFERENCE_AUDIT.md.
 */

typedef unsigned int u32;
typedef unsigned char u8;

#define COLLECTION_COUNT_OFFSET  4u
#define COLLECTION_VALUES_OFFSET 8u
#define SECOND_COLLECTION_OFFSET 0x408u

/* ------------------------------------------------------------------------- */
/* A symbol this unit references but does not reconstruct                     */
/* ------------------------------------------------------------------------- */
/* The removal helper, bound at its original address. */
extern void sub_0804FE54(void *collection, u32 index);

/* ------------------------------------------------------------------------- */
/* the forward keyed scan, shared by both collections                         */
/* ------------------------------------------------------------------------- */
/*
 * Returns the index of the FIRST element equal to `key`, or -1. The two scans in
 * the original are the same code shape at two bases, so they are one helper here.
 */
static int find_by_value(const void *base, u32 key)
{
    u32 count = *(const u32 *)((const u8 *)base + COLLECTION_COUNT_OFFSET);
    u32 i;

    for (i = 0u; i < count; i++) {
        u32 element = *(const u32 *)((const u8 *)base
                                     + COLLECTION_VALUES_OFFSET + 4u * i);
        if (element == key) {
            return (int)i;
        }
    }
    return -1;
}

/* ------------------------------------------------------------------------- */
/* 0x080119BC - 162 bytes - 81 instructions                                   */
/* ------------------------------------------------------------------------- */
void sub_080119BC(void *object, u32 key, u32 value)
{
    int index = find_by_value(object, key);

    if (index >= 0) {
        /* REPLACE in place; the count is deliberately untouched. */
        *(u32 *)((u8 *)object + COLLECTION_VALUES_OFFSET + 4u * (u32)index) = value;
        return;
    }

    /* Absent from the first collection: take it out of the second, if it is there,
     * then append it to the first. */
    index = find_by_value((const u8 *)object + SECOND_COLLECTION_OFFSET, key);
    if (index >= 0) {
        sub_0804FE54((u8 *)object + SECOND_COLLECTION_OFFSET, (u32)index);
    }

    {
        u32 count = *(u32 *)((u8 *)object + COLLECTION_COUNT_OFFSET);
        *(u32 *)((u8 *)object + COLLECTION_VALUES_OFFSET + 4u * count) = value;
        *(u32 *)((u8 *)object + COLLECTION_COUNT_OFFSET) = count + 1u;
    }
}

/* ------------------------------------------------------------------------- */
/* The unit's literal word, as declared data                                  */
/* ------------------------------------------------------------------------- */
const u32 bci_collectionwrite2_literal_pool[1] = {
    0x0000040Cu
};
