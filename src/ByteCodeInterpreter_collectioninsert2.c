/*
 * src/ByteCodeInterpreter_collectioninsert2.c
 *
 * DECOMPILED SOURCE for sub_08011732: the routine that INSERTS into the object's
 * SECOND collection, at 0x03001C4C + 0x408.
 *
 *   0x08011732  216 bytes  97 instructions  one terminator at 0x08011808
 *
 * The insertion itself is at 0x0801177E..0x0801178A, and it is reached only as the
 * destination of a MIGRATION out of the first collection.
 *
 * THE ROUTINE, STRUCTURALLY
 *   while (sub_080116FC(object) < arg2)              outer condition, checked twice
 *       for i = first.count-1 DOWN TO 0:             BACKWARD over the first collection
 *           element = first.elements[i]
 *           verdict = element->table[+0x18](element, pass)
 *           if verdict == 1:
 *               element->table[+0x04](element)
 *               REMOVE i from the FIRST collection            via sub_0804FE54
 *           else if verdict == 2:
 *               element->table[+0x1C](element)
 *               APPEND element to the SECOND collection       <-- THE INSERTION
 *               REMOVE i from the FIRST collection            via sub_0804FE54
 *           else: leave the element where it is
 *       pass++
 *   sub_080115B0(object)
 *   ... a global is read and passed to sub_0803DA62 ...
 *   for i = third.count-1 DOWN TO 0:                 a THIRD collection at object+0x208
 *       element->table[+0x14](element)
 *   third.count = 0                                  the third collection is FLUSHED
 *
 * THE INSERTION, IN FULL
 *   0x0801174A  adds r0, r6, r0      r0 = object + 0x40C, the SECOND count slot
 *   0x0801177E  ldr  r0, [sp, #8]    that saved slot again
 *   0x08011780  ldr  r1, [r0]        r1 = count2
 *   0x08011782  adds r2, r1, #1
 *   0x08011784  str  r2, [r0]        count2 = count2 + 1
 *   0x08011786  lsls r1, r1, #2      r1 = count2 * 4, the OLD count
 *   0x08011788  adds r0, r1, r0
 *   0x0801178A  str  r5, [r0, #4]    second.elements[old count2] = element
 *
 * so the contract is `second.elements[count2] = element; count2++`, and the OLD
 * count is used as the index, exactly as in the first append routine.
 *
 * THE ELEMENT IS MOVED, NOT COPIED
 * The very next instructions, 0x0801178C..0x08011790, call sub_0804FE54 with the
 * FIRST collection's base and the index the inner loop is on, so the element is
 * removed from the first collection in the same breath. An element therefore exists
 * in exactly one of the two collections after this routine has run, which is what
 * makes the pair a pair rather than two independent lists.
 *
 * THIS IS THE INVERSE OF sub_080119BC
 * That routine moves an element from the SECOND collection to the FIRST when a key
 * is found. This one moves an element from the FIRST to the SECOND when the
 * element's own virtual method returns 2. Together they are the two directions of
 * one migration, and neither is reachable from the other.
 *
 * A THIRD COLLECTION EXISTS AT object + 0x208
 *   0x080117CA  movs r0, #0x41 ; lsls r0, r0, #3     r0 = 0x208
 *   0x080117CE  adds r5, r6, r0
 *   0x080117D0  ldr  r4, [r5]                        its count, at object + 0x208
 *   ... each element's table[+0x14] method is called ...
 *   0x08011804  str  r0, [r5]                        THEN ITS COUNT IS SET TO ZERO
 * Its elements therefore start at object + 0x20C and the collection is FLUSHED at
 * the end of this routine rather than migrated. That is a third state of the same
 * object, and it is recorded here rather than chased further.
 *
 * ORDERING AND DUPLICATES
 *   * the inner loop runs BACKWARD, so the LAST first-collection element is examined
 *     first, the same direction as the reader and the opposite of sub_080119BC;
 *   * there is NO duplicate check on insertion: the element is appended at the tail
 *     whether or not an equal element is already in the second collection. Duplicate
 *     prevention is therefore NOT a property of this insertion path;
 *   * the removal from the first collection happens AFTER the insertion, so if the
 *     removal were skipped the element would exist in both.
 *
 * NO CAPACITY CHECK, NO BOUNDS CHECK
 * Nothing compares count2 against a limit, and no element is null checked. No guard
 * was added.
 *
 * STATUS, and these three lines are INDEPENDENT of one another.
 *   SEMANTIC.....PROVEN   the insertion index, the count increment, the move out of
 *                         the first collection and the verdict-driven branches are
 *                         checked by RUNNING them; see
 *                         src/probes/collectioninsert2_selftest.c.
 *   MODERN_BUILD.PASS     it compiles and links for ARM7TDMI Thumb with the modern
 *                         toolchain; see docs/LIFT_COLLECTIONINSERT2.md.
 *   ADS_MATCH....BLOCKED  never compiled by the tool it targets. The ADS 1.2
 *                         binaries are present on this machine but the licence
 *                         present covers a different product (ADS12_LICENSE_UNAVAILABLE).
 *                         No byte-match claim is made.
 *
 * WHAT IS UNKNOWN
 *   - what the elements are, or what verdicts 1 and 2 mean beyond their effect;
 *   - what sub_080116FC returns, which the outer loop compares against arg2;
 *   - what sub_080115B0, sub_0803DA62 and the global at 0x08072824 do;
 *   - what appends to the THIRD collection at +0x208;
 *   - the object's +0x00 field, which THIS ROUTINE DOES NOT TOUCH.
 *
 * The original file may NOT be copied from 2genkidev/buusfury: that repository
 * carries no licence grant. See docs/REFERENCE_AUDIT.md.
 */

typedef unsigned int u32;
typedef unsigned char u8;

#define FIRST_COUNT_OFFSET   0x04u
#define FIRST_VALUES_OFFSET  0x08u
#define SECOND_COUNT_OFFSET  0x40Cu
#define THIRD_COUNT_OFFSET   0x208u

/* ------------------------------------------------------------------------- */
/* Symbols this unit references but does not reconstruct                      */
/* ------------------------------------------------------------------------- */
extern u32 sub_080116FC(void *object);            /* the outer-loop predicate  */
extern void sub_080115B0(void *object);           /* the post-scan call       */
extern void sub_0803DA62(u32 value);              /* the global consumer      */
extern void sub_0804FE54(void *collection, u32 index);   /* the removal helper */

/* ------------------------------------------------------------------------- */
/* Absolute machine state. Redirected by the host self-check.                 */
/* ------------------------------------------------------------------------- */
/*
 * The routine reads one word from a fixed address before its global call. On the
 * host that address is not mapped, so it is redirected rather than dereferenced.
 */
#ifndef COLLECTIONINSERT2_HOST_TEST

#define INSERT2_GLOBAL_WORD (*(u32 *)0x08072824u)

#else  /* COLLECTIONINSERT2_HOST_TEST */

extern u32 collectioninsert2_host_global_word;
#define INSERT2_GLOBAL_WORD (collectioninsert2_host_global_word)

#endif /* COLLECTIONINSERT2_HOST_TEST */

/* ------------------------------------------------------------------------- */
/* The virtual calls, taken out of the element's own table                    */
/* ------------------------------------------------------------------------- */
/*
 * The original reaches each method through the `bx r1`/`bx r2` thunks in the block
 * at 0x08046AA0..0x08046AA6, trampolines the original toolchain emitted for
 * indirect calls. Expressing them as calls through a function pointer is what those
 * trampolines achieve, and no external symbol is introduced by doing so.
 */
static u32 call_method_1(u32 element, u32 slot)
{
    u32 table = *(u32 *)element;                     /* ldr r1,[r0]           */
    u32 offset = *(u32 *)(table + slot);             /* ldr r2,[r1,#slot]     */
    /* The machine computes `adds r1, r2, r1`, a 32-BIT WRAPPING add, and the
     * offsets in this image are large negative values. Adding them through a
     * pointer type would be pointer-overflow, so the add is expressed in the same
     * 32-bit arithmetic the instruction performs. */
    u32 method = table + offset;
    u32 (*fn)(u32) = (u32 (*)(u32))method;
    return fn(element);
}

static u32 call_method_2(u32 element, u32 slot, u32 arg)
{
    u32 table = *(u32 *)element;
    u32 offset = *(u32 *)(table + slot);
    u32 method = table + offset;
    u32 (*fn)(u32, u32) = (u32 (*)(u32, u32))method;
    return fn(element, arg);
}

/* ------------------------------------------------------------------------- */
/* 0x08011732 - 216 bytes - 97 instructions                                   */
/* ------------------------------------------------------------------------- */
void sub_08011732(void *object, u32 arg2)
{
    u8 *base = (u8 *)object;
    u32 pass = 0u;
    u32 *second_count = (u32 *)(base + SECOND_COUNT_OFFSET);

    while (sub_080116FC(object) < arg2) {
        u32 *first_count = (u32 *)(base + FIRST_COUNT_OFFSET);
        u32 i;
        u32 count = *first_count;

        if (count != 0u) {
            i = count - 1u;
            for (;;) {
                u32 element = *(u32 *)(base + FIRST_VALUES_OFFSET + 4u * i);
                u32 verdict = call_method_2(element, 0x18u, pass);

                if (verdict == 1u) {
                    (void)call_method_1(element, 0x04u);
                    sub_0804FE54(first_count, i);
                } else if (verdict == 2u) {
                    u32 slot;
                    (void)call_method_1(element, 0x1Cu);

                    /* THE INSERTION: append at the OLD count, then increment. */
                    slot = *second_count;
                    *second_count = slot + 1u;
                    *(u32 *)((u8 *)second_count + slot * 4u + 4u) = element;

                    /* and the element LEAVES the first collection */
                    sub_0804FE54(first_count, i);
                }

                if (pass >= 0xBu && sub_080116FC(object) >= arg2) {
                    break;
                }
                if (i == 0u) {
                    break;
                }
                i -= 1u;
            }
        }

        pass += 1u;
        if (!(sub_080116FC(object) < arg2)) {
            break;
        }
    }

    sub_080115B0(object);
    sub_0803DA62(INSERT2_GLOBAL_WORD);

    /* The THIRD collection, flushed rather than migrated. */
    {
        u32 *third_count = (u32 *)(base + THIRD_COUNT_OFFSET);
        u32 count = *third_count;

        if (count != 0u) {
            u32 i = count - 1u;
            for (;;) {
                u32 element = *(u32 *)((u8 *)third_count + 4u + 4u * i);
                (void)call_method_1(element, 0x14u);
                if (i == 0u) {
                    break;
                }
                i -= 1u;
            }
        }
        *third_count = 0u;
    }
}

/* ------------------------------------------------------------------------- */
/* The unit's literal words, as declared data                                 */
/* ------------------------------------------------------------------------- */
const u32 bci_collectioninsert2_literal_pool[2] = {
    0x0000040Cu,
    0x08072824u
};
