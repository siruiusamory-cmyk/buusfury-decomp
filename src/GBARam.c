/*
 * src/GBARam.c
 *
 * DECOMPILED SOURCE for the original src/GBARam.c named by the surviving build
 * lead:  tcpp -S -c -cpu ARM7TDMI -O1 src/GBARam.c
 *
 * It occupies file 0x03D4D0..0x03D740 (624 bytes: 608 of code, a 16-byte
 * literal pool) and holds eight Thumb functions.
 *
 * STATUS, and these three lines are INDEPENDENT of one another.
 *   SEMANTIC.....PROVEN   the allocator's behaviour is checked by running it:
 *                         src/probes/gbaram_selftest.c executes 230 assertions
 *                         against a real arena and all of them pass.
 *   MODERN_BUILD.PASS     it compiles and links for ARM7TDMI Thumb with the
 *                         modern toolchain; see docs/LIFT_PILOT.md.
 *   ADS_MATCH....BLOCKED  never compiled by the tool it targets. The ADS 1.2
 *                         binaries are installed on this machine but the licence
 *                         present covers a different product, so the ARM
 *                         compilers cannot be run (ADS12_LICENSE_UNAVAILABLE).
 *                         No byte-match claim is made, and none may be inferred
 *                         from the modern build: a modern GCC is not the
 *                         original compiler and its output differs (see
 *                         config/lift_gbaram.json).
 *
 * WHAT IS EVIDENCE AND WHAT IS ASSUMPTION
 * Evidence (from the canonical ROM, config/compiler_probes.json):
 *   - eight functions at 0x0803D4D0..0x0803D730, Thumb, every path terminating
 *   - one shared literal pool at 0x0803D730 holding 0x02000800, 0x03003488,
 *     0x0000FDFE, 0x7FFFFFFF
 *   - a block header read at offsets 0x00, 0x02, 0x04, 0x06, 0x08, 0x0A
 *   - the allocation returned to callers is block + 8
 *   - index arithmetic: block = (u16 << 2) + 0x02000000, and the inverse is
 *     emitted as (block + 0xFE000000) >> 2, i.e. an arithmetic shift
 * Assumption (NOT evidence, to be corrected by the first successful run):
 *   - field names. The disassembly fixes each offset and its access width; it
 *     does not say what the game called it. Names below are placeholders.
 *
 * WHAT IS EVIDENCE AND WHAT IS ASSUMPTION
 * Evidence (from the canonical ROM, config/compiler_probes.json):
 *   - eight functions at 0x0803D4D0..0x0803D730, Thumb, every path terminating
 *   - one shared literal pool at 0x0803D730 holding 0x02000800, 0x03003488,
 *     0x0000FDFE, 0x7FFFFFFF
 *   - a block header read at offsets 0x00, 0x02, 0x04, 0x06, 0x08, 0x0A
 *   - the allocation returned to callers is block + 8
 *   - index arithmetic: block = (u16 << 2) + 0x02000000, and the inverse is
 *     emitted as (block + 0xFE000000) >> 2, i.e. an arithmetic shift
 * Assumption (NOT evidence, to be corrected by the first successful run):
 *   - field names. The disassembly fixes each offset and its access width; it
 *     does not say what the game called it. Names below are placeholders.
 *
 * What RUNNING the reconstruction on the host has already settled (see
 * gbaram_selftest.c). Four defects were found this way, and none of them could
 * ever have matched the ROM:
 *   - The search in sub_0803D5B8 is BEST-FIT and 0x7FFFFFFF is its initial
 *     sentinel, not a size test. r3 is REASSIGNED to the running best size at
 *     0x0803D5E6, so `cmp r2, r3 / bge` means "not smaller than the best so
 *     far, skip". An earlier reading of this as a guard that can never fire was
 *     simply wrong: r3 is not constant across the loop.
 *   - The loop terminator is `prev == 0`, not a null pointer. Index 0 is the
 *     NULL encoding, so the advance must test the WORD before converting it.
 *     Converting first yields a valid-looking non-null pointer and the loop
 *     never terminates; the host run hung on exactly this.
 *   - Every coalesce in sub_0803D63C merges the freed block INTO the surviving
 *     neighbour, which keeps its place in the free list. Three of the six cases
 *     previously had the direction inverted, and one called sub_0803D56A with
 *     its arguments reversed; together they collapsed the free total from
 *     260,088 bytes to 172.
 *   - sub_0803D56A's store of the word at absorbed+0x04 into both of absorbed's
 *     list neighbours is CONSISTENT with the host self-check: the free total and
 *     the list invariants hold across 230 checks, so +0x00/+0x04 behave as the
 *     neighbour links used for coalescing. The field's NAME is still unknown,
 *     and behavioural consistency is not proof of the original source.
 *   - There is NO out-of-memory path: sub_0803D5B8 dereferences `best`
 *     unconditionally, so a request larger than the largest free block reads
 *     index 0. Faithful, and recorded rather than "fixed" with a null check the
 *     original does not have.
 *
 * The original file may NOT be copied from 2genkidev/buusfury: that repository
 * carries no licence grant. See docs/REFERENCE_AUDIT.md.
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

/* One heap block. 8 bytes of header; the payload starts at +8, and while the
 * block is free the payload's first four bytes double as the free-list links. */
typedef struct GbaBlock {
    u16 left;   /* 0x00 */
    u16 size;   /* 0x02, in 4-byte words */
    u16 right;  /* 0x04 */
    u8 busy;    /* 0x06 */
    u16 prev;   /* 0x08, free-list link */
    u16 next;   /* 0x0A, free-list link */
} GbaBlock;

#ifndef GBARAM_HOST_TEST
#define GBA_HEAP_BASE ((GbaBlock *)0x02000800u)
#define GBA_LIST_HEAD ((GbaBlock **)0x03003488u)

#define GBA_BLOCK_FROM_WORD(w) ((GbaBlock *)(((u32)(w) << 2) + 0x02000000u))
#define GBA_WORD_FROM_BLOCK(p) ((u16)(((int)(p) - (int)0x02000000) >> 2))
#else
/* Host build (see gbaram_selftest.c). The three absolute addresses and the
 * index origin are redirected into a real arena so the allocator can be RUN and
 * its behaviour checked. Only ADDRESS ENCODING differs: every semantic
 * operation, branch and arithmetic step below is the same code the probe build
 * compiles. The probe build takes the definitions above, token-for-token as it
 * always has, so the emitted machine code cannot depend on this block existing. */
extern unsigned char gbaram_arena[];
#define GBA_HEAP_BASE ((GbaBlock *)(gbaram_arena + 0x800))
#define GBA_LIST_HEAD ((GbaBlock **)(gbaram_arena + 0x3FF00))
#define GBA_BLOCK_FROM_WORD(w) ((GbaBlock *)(gbaram_arena + ((u32)(w) << 2)))
#define GBA_WORD_FROM_BLOCK(p) ((u16)(((u8 *)(p) - gbaram_arena) >> 2))
#endif

#define GBA_PAYLOAD(b) ((u8 *)(b) + 8)

/* 0x0803D4D0 - 24 bytes, leaf. Reset the free list to a single node at the heap
 * base: 0xFDFE words available, no children, not busy, unlinked. */
void sub_0803D4D0(void)
{
    GbaBlock *block = GBA_HEAP_BASE;

    *GBA_LIST_HEAD = block;
    block->left = 0;
    block->size = 0xFDFE;
    block->right = 0;
    block->busy = 0;
    block->prev = 0;
    block->next = 0;
}

/* 0x0803D4E8 - 56 bytes, leaf. Take a block out of the free list and mark it in
 * use, repairing the neighbours and the list head. */
void sub_0803D4E8(GbaBlock *block)
{
    block->busy = 1;

    if (block->next != 0) {
        GBA_BLOCK_FROM_WORD(block->next)->prev = block->prev;
    } else if (block->prev != 0) {
        *GBA_LIST_HEAD = GBA_BLOCK_FROM_WORD(block->prev);
    } else {
        *GBA_LIST_HEAD = 0;
    }

    if (block->prev != 0) {
        GBA_BLOCK_FROM_WORD(block->prev)->next = block->next;
    }
}

/* 0x0803D520 - 40 bytes, leaf. Push a block onto the head of the free list. */
void sub_0803D520(GbaBlock *block)
{
    GbaBlock *head = *GBA_LIST_HEAD;

    if (head != 0) {
        block->prev = GBA_WORD_FROM_BLOCK(head);
        head->next = GBA_WORD_FROM_BLOCK(block);
    } else {
        block->prev = 0;
    }
    block->next = 0;
    *GBA_LIST_HEAD = block;
}

/* 0x0803D548 - 34 bytes, leaf. Fold `absorbed` into `block`, adopting its one
 * child link, then unlink `absorbed`. */
void sub_0803D548(GbaBlock *block, GbaBlock *absorbed)
{
    block->size = block->size + absorbed->size + 2;
    block->left = absorbed->left;
    if (absorbed->left != 0) {
        GBA_BLOCK_FROM_WORD(absorbed->left)->right = absorbed->right;
    }
}

/* 0x0803D56A - 78 bytes, leaf. The same fold as sub_0803D548 with the full
 * free-list repair: both neighbours of `absorbed` are rewired, and the list
 * head is moved when `absorbed` was the head.
 *
 * ASSUMPTION, UNRESOLVED: the disassembly stores the word at absorbed+0x04 into
 * both neighbours, which does not read as a plain unlink. Recorded rather than
 * smoothed over. */
void sub_0803D56A(GbaBlock *block, GbaBlock *absorbed)
{
    u16 relocated = absorbed->right;

    block->size = block->size + absorbed->size + 2;
    block->left = absorbed->left;
    if (absorbed->left != 0) {
        GBA_BLOCK_FROM_WORD(absorbed->left)->right = absorbed->right;
    }

    block->next = absorbed->next;
    if (absorbed->next != 0) {
        GBA_BLOCK_FROM_WORD(absorbed->next)->prev = relocated;
    } else {
        *GBA_LIST_HEAD = block;
    }

    block->prev = absorbed->prev;
    if (absorbed->prev != 0) {
        GBA_BLOCK_FROM_WORD(absorbed->prev)->next = relocated;
    }
}

/* 0x0803D5B8 - 132 bytes, 3 exits, calls sub_0803D4E8. Allocate `words`
 * 4-byte units, best fit over the free list. A node that exactly fits is
 * returned whole; a larger node is split and its tail returned.
 *
 * ASSUMPTION, UNRESOLVED: the 0x7FFFFFFF comparison cannot be taken for a
 * 16-bit field. Kept because the disassembly emits it. */
void *sub_0803D5B8(int size)
{
    /* The ROM emits `asrs` for this shift, not `lsrs`: the value is SIGNED, so
     * the parameter, `want`, `best_size` and `remaining` are all `int`.
     * Writing `u32` here produces `lsrs` and cannot match.
     *
     * THE SEARCH IS BEST-FIT, and the 0x7FFFFFFF is its initial sentinel, not a
     * size test. Register r3 is loaded with 0x7FFFFFFF and is REASSIGNED to the
     * running best size at 0x0803D5E6, so `cmp r2, r3 / bge` means "this block
     * is not smaller than the best already found, so skip it". An earlier
     * reading of this as a guard that can never fire was wrong: r3 is not a
     * constant across the loop. Because best_size only decreases, the loop
     * finds the smallest block that is strictly larger than `want`, with an
     * exact-size hit returning immediately.
     *
     * The loop terminator is `prev == 0`, NOT a null pointer: index 0 is the
     * NULL encoding, so the advance must test the WORD before converting it.
     * Converting first yields a valid-looking non-null pointer and never
     * terminates. Running the reconstruction on the host hung on exactly this,
     * which is how it was found. */
    int want = (size + 3) >> 2;
    GbaBlock *best = 0;
    int best_size = 0x7FFFFFFF;
    GbaBlock *block = *GBA_LIST_HEAD;

    for (;;) {
        if (block->size >= best_size) {
            /* Not smaller than the best so far: fall through to the advance. */
        } else if (block->size == want) {
            sub_0803D4E8(block);
            return GBA_PAYLOAD(block);
        } else if (block->size > want) {
            best = block;
            best_size = block->size;
        }
        if (block->prev == 0) {
            break;
        }
        block = GBA_BLOCK_FROM_WORD(block->prev);
    }

    {
        /* The ROM dereferences `best` unconditionally here, so there is NO
         * out-of-memory path: a request larger than the largest free block
         * reads index 0 rather than returning NULL. Faithful, and recorded as a
         * semantic property rather than "fixed" with a null check the original
         * does not have. */
        int remaining = best->size - want - 2;

        if (remaining <= 0) {
            sub_0803D4E8(best);
            return GBA_PAYLOAD(best);
        }

        {
            GbaBlock *tail = (GbaBlock *)((u8 *)best + (remaining << 2) + 8);

            tail->left = best->left;
            if (best->left != 0) {
                GBA_BLOCK_FROM_WORD(best->left)->right = GBA_WORD_FROM_BLOCK(tail);
            }
            tail->size = want;
            tail->right = GBA_WORD_FROM_BLOCK(best);
            tail->busy = 1;
            best->left = GBA_WORD_FROM_BLOCK(tail);
            best->size = remaining;
            return GBA_PAYLOAD(tail);
        }
    }
}

/* 0x0803D63C - 214 bytes, 9 exits, calls sub_0803D4E8 / sub_0803D56A /
 * sub_0803D520. Return an allocation and coalesce it with its free neighbours.
 *
 * Every merge goes the SAME way: the freed block is absorbed INTO the surviving
 * neighbour, which keeps its place in the free list. An earlier revision had the
 * merge direction inverted in three of the six cases (unlinking and growing the
 * left neighbour instead of the right, and calling sub_0803D56A with its
 * arguments reversed). Running the reconstruction on the host caught it: the
 * free total collapsed to 172 bytes instead of returning to 260,088. */
void sub_0803D63C(void *payload)
{
    GbaBlock *block;
    GbaBlock *left;
    GbaBlock *right;

    if (payload == 0) {
        return;
    }

    block = (GbaBlock *)((u8 *)payload - 8);
    block->busy = 0;

    if (block->left == 0) {
        if (block->right == 0) {
            /* 0x0803D708: nothing on either side, so block becomes the list. */
            *GBA_LIST_HEAD = block;
            block->prev = 0;
            block->next = 0;
            return;
        }
        right = GBA_BLOCK_FROM_WORD(block->right);
        if (right->busy == 0) {
            /* 0x0803D6E8: absorbed into the free right neighbour. */
            right->size = right->size + block->size + 2;
            right->left = block->left; /* 0, so right becomes leftmost */
            return;
        }
        sub_0803D520(block);
        return;
    }

    left = GBA_BLOCK_FROM_WORD(block->left);

    if (block->right == 0) {
        /* 0x0803D6CA: only a left neighbour exists. */
        if (left->busy == 0) {
            sub_0803D56A(block, left);
            return;
        }
        sub_0803D520(block);
        return;
    }

    right = GBA_BLOCK_FROM_WORD(block->right);

    if (left->busy != 0) {
        if (right->busy != 0) {
            /* 0x0803D6C2: both neighbours are in use, so just re-list block. */
            sub_0803D520(block);
            return;
        }
        /* 0x0803D6A0: absorbed into the free right neighbour. */
        right->size = right->size + block->size + 2;
        right->left = block->left;
        if (block->left != 0) {
            GBA_BLOCK_FROM_WORD(block->left)->right = block->right;
        }
        return;
    }

    if (right->busy != 0) {
        /* 0x0803D696: block absorbs its free left neighbour. */
        sub_0803D56A(block, left);
        return;
    }

    /* 0x0803D66A: both free. The LEFT neighbour is unlinked and all three are
     * merged into the RIGHT neighbour, which stays in the list. */
    sub_0803D4E8(left);
    right->size = block->size + left->size + right->size + 4;
    right->left = left->left;
    if (left->left != 0) {
        GBA_BLOCK_FROM_WORD(left->left)->right = block->right;
    }
}

/* 0x0803D712 - 30 bytes, leaf. Total free space, in 4-byte words, walking the
 * whole free list. */
u32 sub_0803D712(void)
{
    u32 total = 0;
    GbaBlock *block = *GBA_LIST_HEAD;

    total += block->size << 2;

    while (block->next != 0) {
        block = GBA_BLOCK_FROM_WORD(block->next);
        total += block->size << 2;
    }

    return total;
}
