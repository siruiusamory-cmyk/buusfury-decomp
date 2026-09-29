/*
 * src/probes/handler2_selftest.c
 *
 * HOST SEMANTIC CHECK for primary dispatch slot 2, entry 0x08003CBE.
 *
 * This compiles src/ByteCodeInterpreter_handlers.c for the host, substitutes the
 * native table with local storage, and RUNS the handler with recording native
 * routines. It proves only what the ROM's disassembly already fixes, and it is
 * not compiler evidence: nothing here says anything about ADS 1.2.
 *
 * The discriminators are chosen so that the WRONG implementation produces a
 * DIFFERENT OBSERVABLE, not merely a different byte count:
 *
 *   - index width: the index byte is 0x02 and the three bytes after it are
 *     0x01, 0x00, 0x00. Read as a BYTE the index is 2; read as a little-endian
 *     WORD it would be 0x102 = 258. Distinct routines are installed at both
 *     entries, so the two readings call different functions.
 *   - cursor advance: a byte read advances by one and a word read by four, so
 *     the recorder reading the slot back distinguishes them.
 *   - advance ORDER: the recorder reads the watched slot at call time, which is
 *     only the advanced value if the write-back happened before the dispatch.
 *   - context transparency: the recorder captures the r0 it was entered with,
 *     including NULL, which no write to r0 would survive.
 *
 * Built 32-bit, like the other ByteCodeInterpreter check: the handler holds the
 * cursor and the table in machine words, and a 64-bit host would truncate the
 * cursor slot pointer it hands to the table lookup.
 */

#include <stdio.h>
#include <string.h>

#define HANDLER2_HOST_TEST 1
#include "ByteCodeInterpreter_handlers.c"

/* ------------------------------------------------------------------------- */
/* Host substitutes                                                           */
/* ------------------------------------------------------------------------- */
BciNative handler2_host_native[BCI_NATIVE_ENTRIES];

/* ------------------------------------------------------------------------- */
/* Test bookkeeping                                                           */
/* ------------------------------------------------------------------------- */
static int checks;
static int failures;

static void check(int condition, const char *what, unsigned long detail)
{
    checks++;
    if (!condition) {
        failures++;
        printf("FAIL: %s (detail %lu)\n", what, detail);
    }
}

/* ------------------------------------------------------------------------- */
/* Recording native routines                                                  */
/* ------------------------------------------------------------------------- */
static int   g_calls;
static int   g_called_from;        /* which distinct routine ran          */
static void *g_ctx_seen;           /* the r0 the routine was entered with */
static u32  *g_slot_watched;       /* the cursor slot the test is watching */
static u32   g_slot_at_call;       /* its value read from INSIDE the call  */
static int   g_table_untouched;

#define RECORDER(name, id)                                   \
    static void name(BciContextRef ctx)                      \
    {                                                        \
        g_calls++;                                           \
        g_called_from = (id);                                \
        g_ctx_seen = ctx;                                    \
        if (g_slot_watched != NULL) {                        \
            g_slot_at_call = *g_slot_watched;                \
        }                                                    \
    }

RECORDER(native_2, 2)
RECORDER(native_258, 258)
RECORDER(native_0, 0)
RECORDER(native_1, 1)
RECORDER(native_171, 171)
RECORDER(native_255, 255)
RECORDER(native_unused, -1)

static BciNative g_table_snapshot[BCI_NATIVE_ENTRIES];

static void reset_all(void)
{
    u32 i;

    for (i = 0u; i < BCI_NATIVE_ENTRIES; i++) {
        handler2_host_native[i] = native_unused;
    }
    /* The distinct slots the tests rely on. */
    handler2_host_native[0] = native_0;
    handler2_host_native[1] = native_1;
    handler2_host_native[2] = native_2;
    handler2_host_native[171] = native_171;
    handler2_host_native[255] = native_255;
    handler2_host_native[258] = native_258;

    memcpy(g_table_snapshot, handler2_host_native, sizeof(g_table_snapshot));

    g_calls = 0;
    g_called_from = -1;
    g_ctx_seen = NULL;
    g_slot_watched = NULL;
    g_slot_at_call = 0u;
    g_table_untouched = 0;
}

static int table_is_untouched(void)
{
    return memcmp(g_table_snapshot, handler2_host_native, sizeof(g_table_snapshot)) == 0;
}

/* ------------------------------------------------------------------------- */
int main(void)
{
    static u8 code[8];
    u32 slot;
    static int sentinel;

    /* ---- 1. the index is a BYTE, and selection is table[index] ----------- */
    /* Byte read -> index 2; little-endian word read -> 0x102 = 258. */
    reset_all();
    memset(code, 0, sizeof(code));
    code[0] = 0x02u;
    code[1] = 0x01u;
    code[2] = 0x00u;
    code[3] = 0x00u;
    slot = (u32)code;
    g_slot_watched = &slot;
    sub_08003CBE(&sentinel, &slot);

    check(g_calls == 1, "the native routine is called exactly once per dispatch", (unsigned long)g_calls);
    check(g_called_from == 2,
          "the index byte 0x02 selected table[2]; a WORD read would have selected table[258]",
          (unsigned long)g_called_from);
    check(g_called_from != 258, "the index was not read as a little-endian word", (unsigned long)g_called_from);

    /* ---- 2. the cursor advances by exactly one, before the dispatch ------ */
    check(slot == (u32)(code + 1),
          "the cursor slot holds cursor+1 after the call (adds r3,#1 ; str r3,[r1])",
          (unsigned long)(slot - (u32)code));
    check(g_slot_at_call == (u32)(code + 1),
          "the slot already held the ADVANCED cursor while the native routine ran",
          (unsigned long)(g_slot_at_call - (u32)code));
    check(slot != (u32)(code + 4), "the cursor did not advance by four", 0ul);

    /* ---- 3. r0 is passed through unchanged, including NULL --------------- */
    reset_all();
    memset(code, 0, sizeof(code));
    code[0] = 0x00u;
    slot = (u32)code;
    sub_08003CBE(&sentinel, &slot);
    check(g_ctx_seen == &sentinel,
          "the native routine was entered with r0 = the context, unchanged (r0 is never written)",
          0ul);

    reset_all();
    memset(code, 0, sizeof(code));
    code[0] = 0x00u;
    slot = (u32)code;
    sub_08003CBE(NULL, &slot);
    check(g_ctx_seen == NULL, "a NULL context is passed through as NULL", 0ul);

    /* ---- 4. index 0 and index 1 select their own entries ---------------- */
    reset_all();
    memset(code, 0, sizeof(code));
    code[0] = 0x00u;
    slot = (u32)code;
    sub_08003CBE(&sentinel, &slot);
    check(g_called_from == 0, "index 0 selected table[0]", (unsigned long)g_called_from);

    reset_all();
    memset(code, 0, sizeof(code));
    code[0] = 0x01u;
    slot = (u32)code;
    sub_08003CBE(&sentinel, &slot);
    check(g_called_from == 1, "index 1 selected table[1]", (unsigned long)g_called_from);

    /* ---- 5. the top of the byte range is a valid index ------------------ */
    /* 0xFF is 255 as a byte. If the index were read as a SIGNED byte, or if
     * it were sign-extended into the shift, this would index elsewhere. */
    reset_all();
    memset(code, 0, sizeof(code));
    code[0] = 0xFFu;
    slot = (u32)code;
    sub_08003CBE(&sentinel, &slot);
    check(g_called_from == 255,
          "index byte 0xFF selected table[255]: the index is UNSIGNED and not sign-extended",
          (unsigned long)g_called_from);
    check(slot == (u32)(code + 1), "a 0xFF index still advances the cursor by one",
          (unsigned long)(slot - (u32)code));

    /* ---- 6. the byte range fits the table --------------------------------- */
    /* The index has 256 possible values; the table has 266 entries. Every
     * reachable index is in range, which is why the handler needs no bound
     * test. Asserted as arithmetic, not assumed. */
    check(BCI_NATIVE_ENTRIES >= 256u,
          "the table covers every possible byte index: no out-of-bounds read is reachable",
          (unsigned long)BCI_NATIVE_ENTRIES);
    check(BCI_NATIVE_ENTRIES == 266u,
          "the native table is 266 entries, bounded by the primary table base at 0x080554C0",
          (unsigned long)BCI_NATIVE_ENTRIES);

    /* ---- 7. the handler is context-transparent --------------------------- */
    reset_all();
    memset(code, 0, sizeof(code));
    code[0] = 0x02u;
    slot = (u32)code;
    sub_08003CBE(&sentinel, &slot);
    check(table_is_untouched(), "the handler does not modify the native table", 0ul);
    check(g_calls == 1, "one dispatch, one native call", (unsigned long)g_calls);

    /* ---- 8. two consecutive dispatches advance by two bytes -------------- */
    /* A miniature of the interpreter's loop: the same slot is handed on. */
    reset_all();
    memset(code, 0, sizeof(code));
    code[0] = 0x00u;
    code[1] = 0x01u;
    slot = (u32)code;
    sub_08003CBE(&sentinel, &slot);
    check(g_called_from == 0, "first dispatch selected table[0]", (unsigned long)g_called_from);
    check(slot == (u32)(code + 1), "first dispatch left the cursor at +1",
          (unsigned long)(slot - (u32)code));
    sub_08003CBE(&sentinel, &slot);
    check(g_called_from == 1, "second dispatch selected table[1], reading byte 1",
          (unsigned long)g_called_from);
    check(slot == (u32)(code + 2), "second dispatch left the cursor at +2",
          (unsigned long)(slot - (u32)code));
    check(g_calls == 2, "two dispatches, two native calls", (unsigned long)g_calls);

    /* ---- 9. the literal pool word is the table base ---------------------- */
    check(bci_handler2_literal_pool[0] == 0x08055098u,
          "the unit's single literal word is the native table base",
          bci_handler2_literal_pool[0]);
    check(sizeof(bci_handler2_literal_pool) / sizeof(bci_handler2_literal_pool[0]) == 1u,
          "the handler's pool holds exactly one word",
          (unsigned long)(sizeof(bci_handler2_literal_pool) / sizeof(bci_handler2_literal_pool[0])));

    printf("%s: %d check(s), %d failure(s)\n",
           failures ? "FAIL" : "PASS", checks, failures);
    return failures ? 1 : 0;
}
