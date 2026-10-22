/* NONMATCHING-REFERENCE: not linked; see STATUS below. */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

#define EWRAM_BASE 0x02000000
#define HEAP_START 0x02000800
#define FROM_OFFSET(offset) ((struct MallocHeader*)(EWRAM_BASE + ((offset) << 2)))
#define TO_OFFSET(block) ((u16)(((int)(block) - EWRAM_BASE) >> 2))

struct MallocHeader {
    u16 nextBlock;
    u16 size;
    u16 prevBlock;
    u8 used;
    u8 pad;
    u16 nextFree;
    u16 prevFree;
};

extern struct MallocHeader* FreeListTail;

void GBARam_Init(void) {
    struct MallocHeader* block = (struct MallocHeader*)HEAP_START;

    FreeListTail = block;
    block->nextBlock = 0;
    block->size = 0xfdfe;
    block->prevBlock = 0;
    block->used = 0;
    block->nextFree = 0;
    block->prevFree = 0;
}

void GBARam_MarkAsUsed(struct MallocHeader* block) {
    block->used = 1;
    if (block->prevFree != 0) {
        FROM_OFFSET(block->prevFree)->nextFree = block->nextFree;
    } else if (block->nextFree != 0) {
        FreeListTail = FROM_OFFSET(block->nextFree);
    } else {
        FreeListTail = 0;
    }
    if (block->nextFree != 0) {
        FROM_OFFSET(block->nextFree)->prevFree = block->prevFree;
    }
}

void GBARam_AddToFreeList(struct MallocHeader* block) {
    struct MallocHeader* head = FreeListTail;

    if (head != 0) {
        block->nextFree = TO_OFFSET(head);
        head->prevFree = TO_OFFSET(block);
    } else {
        block->nextFree = 0;
    }
    block->prevFree = 0;
    FreeListTail = block;
}

void GBARam_MergeWithNext(struct MallocHeader* dst, struct MallocHeader* src) {
    dst->size += src->size + 2;
    dst->nextBlock = src->nextBlock;
    if (src->nextBlock != 0) {
        struct MallocHeader* next = FROM_OFFSET(src->nextBlock);

        next->prevBlock = src->prevBlock;
    }
}

void GBARam_MergeWithNextFree(struct MallocHeader* dst, struct MallocHeader* src) {
    u16 srcPrev = src->prevBlock;

    dst->size += src->size + 2;
    dst->nextBlock = src->nextBlock;
    if (src->nextBlock != 0) {
        FROM_OFFSET(src->nextBlock)->prevBlock = src->prevBlock;
    }
    dst->prevFree = src->prevFree;
    if (src->prevFree != 0) {
        FROM_OFFSET(src->prevFree)->nextFree = srcPrev;
    } else {
        FreeListTail = dst;
    }
    dst->nextFree = src->nextFree;
    if (src->nextFree != 0) {
        FROM_OFFSET(src->nextFree)->prevFree = srcPrev;
    }
}

extern "C" void* GBARam_Malloc(int size) {
    struct MallocHeader* block = FreeListTail;
    struct MallocHeader* best = 0;
    int bestSize = 0x7fffffff;
    int words = (size + 3) >> 2;
    int leftover;

    while (1) {
        if (block->size < bestSize) {
            if (block->size == words) {
                GBARam_MarkAsUsed(block);
                return (u8*)block + 8;
            }
            if (block->size > words) {
                best = block;
                bestSize = block->size;
            }
        }
        if (block->nextFree == 0) {
            break;
        }
        block = FROM_OFFSET(block->nextFree);
    }

    leftover = best->size - words - 2;
    if (leftover <= 0) {
        GBARam_MarkAsUsed(best);
        return (u8*)best + 8;
    }
    {
        struct MallocHeader* split =
            (struct MallocHeader*)((u8*)best + (leftover << 2) + 8);
        u16 splitOffset = TO_OFFSET(split);

        split->nextBlock = best->nextBlock;
        if (best->nextBlock != 0) {
            FROM_OFFSET(best->nextBlock)->prevBlock = splitOffset;
        }
        split->size = words;
        split->prevBlock = TO_OFFSET(best);
        split->used = 1;
        best->nextBlock = splitOffset;
        best->size = leftover;
        return (u8*)split + 8;
    }
}

extern "C" void GBARam_Free(void* pointer) {
    struct MallocHeader* block;
    struct MallocHeader* next;
    struct MallocHeader* prev;

    if (pointer == 0) {
        return;
    }
    block = (struct MallocHeader*)((u8*)pointer - 8);
    block->used = 0;
    if (block->nextBlock != 0) {
        next = FROM_OFFSET(block->nextBlock);
        if (block->prevBlock != 0) {
            prev = FROM_OFFSET(block->prevBlock);
            if (next->used != 0) {
                if (prev->used != 0) {
                    GBARam_AddToFreeList(block);
                } else {
                    prev->size += block->size + 2;
                    prev->nextBlock = block->nextBlock;
                    if (block->nextBlock != 0) {
                        FROM_OFFSET(block->nextBlock)->prevBlock = block->prevBlock;
                    }
                }
            } else {
                if (prev->used != 0) {
                    GBARam_MergeWithNextFree(block, next);
                } else {
                    GBARam_MarkAsUsed(next);
                    prev->size += block->size + next->size + 4;
                    prev->nextBlock = next->nextBlock;
                    if (next->nextBlock != 0) {
                        FROM_OFFSET(next->nextBlock)->prevBlock = block->prevBlock;
                    }
                }
            }
        } else {
            if (next->used != 0) {
                GBARam_AddToFreeList(block);
            } else {
                GBARam_MergeWithNextFree(block, next);
            }
        }
    } else {
        if (block->prevBlock != 0) {
            prev = FROM_OFFSET(block->prevBlock);
            if (prev->used != 0) {
                GBARam_AddToFreeList(block);
            } else {
                prev->size += block->size + 2;
                prev->nextBlock = 0;
            }
        } else {
            FreeListTail = block;
            block->nextFree = 0;
            block->prevFree = 0;
        }
    }
}

extern "C" int GBARam_FreeLargest(void) {
    int total = 0;
    struct MallocHeader* block = FreeListTail;

    for (;;) {
        total += block->size * 4;
        if (block->nextFree == 0) {
            break;
        }
        block = FROM_OFFSET(block->nextFree);
    }
    return total;
}
