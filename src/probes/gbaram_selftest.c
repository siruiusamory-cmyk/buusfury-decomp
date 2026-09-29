/*
 * src/probes/gbaram_selftest.c
 *
 * Runs the GBARam.c reconstruction on the HOST so its semantics can be checked.
 *
 * This is NOT compiler evidence. It says nothing about ADS 1.2 code generation
 * and must never be cited as such. What it can do is falsify the reconstruction
 * itself: a translation unit whose C is semantically wrong cannot match the ROM
 * byte-for-byte under ANY compiler, so a behavioural failure here is a real
 * defect on the critical path, and a pass only removes one class of error.
 *
 * Build (from the repository root, MSVC):
 *     cl /nologo /W3 /std:c11 /TC /Fe:gbaram_selftest.exe ^
 *        /Fo:build\ /Fd:build\ src\probes\gbaram_selftest.c
 *
 * Exit code 0 when every check passes, 1 otherwise. Each check prints one line.
 */

#define GBARAM_HOST_TEST 1

#include <stdio.h>
#include <string.h>

/* The arena the allocator runs in. 256 KiB, large enough for the initial
 * 0xFDFE-word block at arena+0x800 plus the head slot at arena+0x3FF00, and
 * small enough that every 16-bit word index stays inside 0..65535 as it does on
 * the cartridge. */
unsigned char gbaram_arena[0x40000];

#include "GBARam.c"

#define ARENA_BYTES (sizeof gbaram_arena)

static int failures;
static int checks;

static void check(int condition, const char *what, unsigned long detail)
{
    checks++;
    if (!condition) {
        printf("  FAIL  %s (0x%lX)\n", what, detail);
        failures++;
    }
}

static int inside(const void *p)
{
    const unsigned char *q = (const unsigned char *)p;
    return q >= gbaram_arena && q < gbaram_arena + ARENA_BYTES;
}

/* Walk the free list with a hard budget: a corrupted list must not hang. */
static int list_is_consistent(unsigned long *out_nodes, unsigned long *out_words)
{
    GbaBlock *node = *GBA_LIST_HEAD;
    unsigned long nodes = 0;
    unsigned long words = 0;

    while (node != 0) {
        GbaBlock *next;
        if (!inside(node)) {
            return 0;
        }
        if (node->next != 0) {
            next = GBA_BLOCK_FROM_WORD(node->next);
            if (!inside(next) || next->prev != GBA_WORD_FROM_BLOCK(node)) {
                return 0;
            }
        }
        if (node->busy != 0) {
            return 0; /* a free-list node must not be marked in use */
        }
        words += node->size;
        nodes++;
        if (nodes > 64) {
            return 0;
        }
        node = node->next ? GBA_BLOCK_FROM_WORD(node->next) : 0;
    }
    *out_nodes = nodes;
    *out_words = words;
    return 1;
}

int main(void)
{
    void *a;
    void *b;
    void *c;
    unsigned long nodes = 0;
    unsigned long words = 0;
    unsigned long initial;
    unsigned long after_alloc;
    unsigned long after_free;
    unsigned long n;

    printf("GBARam semantic self-check (HOST, not compiler evidence)\n");
    printf("arena %lu bytes\n", (unsigned long)ARENA_BYTES);

    /* 1. init: one free node of 0xFDFE words, list consistent. */
    memset(gbaram_arena, 0, ARENA_BYTES);
    sub_0803D4D0();
    check(*GBA_LIST_HEAD == GBA_HEAP_BASE, "init: head is the heap base",
          (unsigned long)(*GBA_LIST_HEAD));
    check(GBA_HEAP_BASE->size == 0xFDFE, "init: size is 0xFDFE words",
          GBA_HEAP_BASE->size);
    check(GBA_HEAP_BASE->busy == 0, "init: node is free", GBA_HEAP_BASE->busy);
    check(list_is_consistent(&nodes, &words), "init: list is consistent", nodes);
    initial = sub_0803D712();
    check(initial == (unsigned long)0xFDFE * 4, "init: free bytes == 0xFDFE*4",
          initial);

    /* 2. allocate: payload is in bounds, distinct, and the list stays sane. */
    a = sub_0803D5B8(100);
    check(a != 0, "alloc(100) returns a payload", 0);
    check(inside(a), "alloc(100) payload is inside the arena", (unsigned long)a);
    check(((unsigned char *)a - gbaram_arena) >= 0x808,
          "alloc(100) payload is past the first header",
          (unsigned long)((unsigned char *)a - gbaram_arena));
    check(list_is_consistent(&nodes, &words), "after alloc(100): list is consistent", 0);
    after_alloc = sub_0803D712();
    check(after_alloc < initial, "after alloc(100): free bytes decreased",
          after_alloc);

    b = sub_0803D5B8(64);
    check(b != 0, "alloc(64) returns a payload", 0);
    check(inside(b), "alloc(64) payload is inside the arena", (unsigned long)b);
    check(a != b, "alloc(64) did not hand back the same payload", 0);
    check((unsigned char *)a + 100 <= (unsigned char *)b ||
          (unsigned char *)b + 64 <= (unsigned char *)a,
          "alloc(100) and alloc(64) do not overlap", 0);
    check(list_is_consistent(&nodes, &words), "after alloc(64): list is consistent", 0);

    c = sub_0803D5B8(4);
    check(c != 0, "alloc(4) returns a payload", 0);

    /* 3. free and coalesce: all three back, and the total returns to the start. */
    sub_0803D63C(a);
    check(list_is_consistent(&nodes, &words), "after free(a): list is consistent", 0);
    sub_0803D63C(b);
    check(list_is_consistent(&nodes, &words), "after free(b): list is consistent", 0);
    sub_0803D63C(c);
    check(list_is_consistent(&nodes, &words), "after free(c): list is consistent", 0);
    after_free = sub_0803D712();
    check(after_free == initial,
          "after freeing everything: free bytes are back to the initial value",
          after_free);

    /* 4. A bounded allocation run inside capacity must stay coherent.
     *
     * There is deliberately NO "returns NULL when exhausted" check: the ROM
     * dereferences `best` unconditionally after the search, so the allocator has
     * no out-of-memory path. A request larger than the largest free block reads
     * index 0. Testing for a NULL return would be testing a contract the
     * original does not have. */
    for (n = 0; n < 200; n++) {
        void *p;
        if (sub_0803D712() < 0x2000) {
            break;
        }
        p = sub_0803D5B8(1000);
        check(inside(p), "bounded alloc(1000) payload is inside the arena",
              (unsigned long)p);
        if (failures) {
            break;
        }
        if ((n % 25) == 0) {
            check(list_is_consistent(&nodes, &words),
                  "bounded allocation run: list is consistent", n);
        }
    }
    check(n >= 100, "bounded allocation run reached at least 100 allocations", n);

    /* The largest block must shrink monotonically: best-fit never picks a
     * bigger block after a smaller one was available. */
    check(sub_0803D712() < initial, "bounded run: free bytes decreased",
          sub_0803D712());

    printf("%s: %d check(s), %d failure(s)\n",
           failures ? "FAIL" : "PASS", checks, failures);
    return failures ? 1 : 0;
}
