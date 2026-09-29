/*
 * src/probes/GBARam.c
 *
 * RECONSTRUCTION HYPOTHESIS for the original src/GBARam.c named by the
 * surviving build lead:  tcpp -S -c -cpu ARM7TDMI -O1 src/GBARam.c
 *
 * STATUS: NOT VALIDATED. No ADS 1.2 installation exists on the authoring
 * machine, so this file has never been compiled by the tool it targets. It is
 * the first hypothesis the probe harness exists to test and iterate against; it
 * is written to be plausible and structurally faithful to the disassembly, not
 * to compile correctly under a modern compiler.
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
 *   - the 0x7FFFFFFF guard in sub_0803D5B8 is compared against a value read
 *     with ldrh, so it can never be taken. Either the original field is wider
 *     than 16 bits, or the guard is a sentinel test whose form the compiler
 *     kept. UNRESOLVED.
 *   - in sub_0803D56A the two list-neighbour updates both store the word read
 *     from block[1]+0x04. Whether that field is a tree child, a relocated
 *     pointer, or a second link is UNRESOLVED.
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

#define GBA_HEAP_BASE ((GbaBlock *)0x02000800u)
#define GBA_LIST_HEAD ((GbaBlock **)0x03003488u)

#define GBA_BLOCK_FROM_WORD(w) ((GbaBlock *)(((u32)(w) << 2) + 0x02000000u))
#define GBA_WORD_FROM_BLOCK(p) ((u16)(((int)(p) - (int)0x02000000) >> 2))

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
void *sub_0803D5B8(u32 size)
{
    u32 want = (size + 3) >> 2;
    GbaBlock *best = 0;
    GbaBlock *block = *GBA_LIST_HEAD;

    while (block != 0) {
        if (block->size >= 0x7FFFFFFFu) {
            break;
        }
        if (block->size == want) {
            sub_0803D4E8(block);
            return GBA_PAYLOAD(block);
        }
        if (block->size > want) {
            best = block;
        }
        block = GBA_BLOCK_FROM_WORD(block->prev);
    }

    {
        u32 remaining = best->size - want - 2;

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
 * sub_0803D520. Return an allocation and coalesce it with its list neighbours
 * where they are free. */
void sub_0803D63C(void *payload)
{
    GbaBlock *block;
    GbaBlock *prev;
    GbaBlock *next;

    if (payload == 0) {
        return;
    }

    block = (GbaBlock *)((u8 *)payload - 8);
    block->busy = 0;

    if (block->left == 0) {
        if (block->right != 0) {
            next = GBA_BLOCK_FROM_WORD(block->right);
            if (next->busy == 0) {
                sub_0803D56A(next, block);
                return;
            }
            sub_0803D520(block);
            return;
        }
        *GBA_LIST_HEAD = block;
        block->prev = 0;
        block->next = 0;
        return;
    }

    prev = GBA_BLOCK_FROM_WORD(block->left);
    if (block->right == 0) {
        if (prev->busy == 0) {
            sub_0803D56A(prev, block);
        } else {
            sub_0803D520(block);
        }
        return;
    }

    next = GBA_BLOCK_FROM_WORD(block->right);
    if (prev->busy == 0) {
        if (next->busy != 0) {
            sub_0803D56A(prev, block);
            return;
        }
        sub_0803D4E8(next);
        prev->size = prev->size + block->size + next->size + 4;
        prev->left = next->left;
        if (next->left != 0) {
            GBA_BLOCK_FROM_WORD(next->left)->right = block->right;
        }
        return;
    }

    if (next->busy == 0) {
        prev->size = prev->size + block->size + 2;
        prev->left = block->left;
        if (block->left != 0) {
            GBA_BLOCK_FROM_WORD(block->left)->right = block->right;
        }
        return;
    }

    sub_0803D520(block);
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
