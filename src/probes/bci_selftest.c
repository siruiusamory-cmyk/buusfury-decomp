/*
 * src/probes/bci_selftest.c
 *
 * HOST SEMANTIC CHECK for the ByteCodeInterpreter translation unit.
 *
 * This compiles src/ByteCodeInterpreter.c for the host, substitutes the
 * absolute IWRAM state and the dispatch table with local storage, and RUNS the
 * reconstruction over synthetic bytecode with recording handlers.
 *
 * It is built with the 32-BIT host toolchain on purpose. The reconstruction
 * models a 32-bit machine and holds pointers in u32 fields, so a 64-bit host
 * truncates them and every stored context address becomes invalid. Building
 * 32-bit makes that conversion lossless and keeps the machine model honest
 * rather than papering over it.
 *
 * It proves only what the ROM's disassembly already fixes, and it is not
 * compiler evidence: nothing here says anything about ADS 1.2 code generation.
 * What it does is falsify a reconstruction whose control flow, cursor handling,
 * nesting or field writes are wrong, which no compiler run can do.
 *
 * Every assertion is tied to a named instruction in 0x08004038..0x08004160.
 * Nothing is asserted from another game's conventions.
 *
 * HOW A SYNTHETIC RUN TERMINATES: the loop stops on a NULL dispatch entry, so
 * each program ends with an opcode whose entry is NULL. `handler_stop` provides
 * a deterministic ending by clearing entry 0 and placing a 0 byte after itself.
 * Getting this wrong makes the program run off the end of the buffer, which is
 * exactly the defect an earlier revision of this file had.
 */

#include <stdio.h>
#include <string.h>

#define BCI_HOST_TEST 1
#include "ByteCodeInterpreter.c"

/* ------------------------------------------------------------------------- */
/* Host substitutes for the machine state                                     */
/* ------------------------------------------------------------------------- */
u32 bci_host_stream;
u32 bci_host_depth;
u32 bci_host_stack[64];
BciHandler bci_host_dispatch[BCI_DISPATCH_ENTRIES];

/* ------------------------------------------------------------------------- */
/* Host substitutes for the declared-not-reconstructed externals               */
/* ------------------------------------------------------------------------- */
static unsigned char g_arena[0x20000];
static unsigned       g_arena_used;
static int            g_alloc_calls;
static int            g_free_calls;
static int            g_alloc_fail;
static void          *g_last_alloc;
static void          *g_last_freed;

void *sub_0803D5B8(u32 size)
{
    void *block;
    size = (size + 7u) & ~7u;
    g_alloc_calls++;
    if (g_alloc_fail || g_arena_used + size > sizeof(g_arena)) {
        g_last_alloc = NULL;
        return NULL;
    }
    block = g_arena + g_arena_used;
    g_arena_used += size;
    g_last_alloc = block;
    return block;
}

void sub_0803D63C(void *block)
{
    g_free_calls++;
    g_last_freed = block;
}

/* The real sub_08049120 unpacks a container. This does not model the format;
 * it records that it was called and with what, which is the part the
 * interpreter's caller proves. */
static int   g_unpack_calls;
static void *g_unpack_dst;
static const void *g_unpack_src;
static unsigned g_unpack_bytes;

void sub_08049120(void *destination, const void *container)
{
    g_unpack_calls++;
    g_unpack_dst = destination;
    g_unpack_src = container;
    if (g_unpack_bytes != 0u && destination != NULL && container != NULL) {
        memcpy(destination, container, g_unpack_bytes);
    }
}

static int g_assert_calls;
static const void *g_assert_message;
static const char *g_assert_file;
static unsigned g_assert_line;

void sub_0803DF14(const void *message, const char *file, unsigned line)
{
    g_assert_calls++;
    g_assert_message = message;
    g_assert_file = file;
    g_assert_line = line;
}

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
/* Recording handlers                                                         */
/* ------------------------------------------------------------------------- */
#define MAX_CALLS 16
static int   g_calls;
static u8    g_opcode_log[MAX_CALLS];
static u32   g_cursor_log[MAX_CALLS];
static u8    g_next_byte_log[MAX_CALLS];   /* *cursor AT CALL TIME */
static BciContext *g_ctx_log[MAX_CALLS];
static u32  *g_slot_log[MAX_CALLS];

static u32   g_stream_at_entry;
static u32   g_depth_high_water;
static u32   g_stack_seen[8];
static int   g_capture_calls;

/* Observations that can only be taken from inside the loop. The cursor slot is
 * a frame local of sub_08004038 and is dead once it returns, so anything read
 * through it must be read HERE, not after the call. */
static void capture(BciContext *ctx, u32 *slot)
{
    u32 i;

    (void)ctx;
    g_capture_calls++;
    if (g_capture_calls == 1) {
        g_stream_at_entry = BCI_STREAM;
    }
    if (BCI_DEPTH > g_depth_high_water) {
        g_depth_high_water = BCI_DEPTH;
    }
    for (i = 0u; i < BCI_DEPTH && i < 8u; i++) {
        g_stack_seen[i] = BCI_STACK_SLOT(i);
    }
    if (g_calls < MAX_CALLS) {
        g_opcode_log[g_calls] = *(const u8 *)(*slot - 1u);
        g_cursor_log[g_calls] = *slot;
        g_next_byte_log[g_calls] = *(const u8 *)(*slot);
        g_ctx_log[g_calls] = ctx;
        g_slot_log[g_calls] = slot;
    }
    g_calls++;
}

/* Dispatch entry 0: logs only. */
static void handler_plain(BciContext *ctx, u32 *slot)
{
    capture(ctx, slot);
}

/* Dispatch entry 1: logs, then consumes ONE inline operand byte. */
static int g_operand_seen;
static u8  g_operand_value;
static void handler_operand(BciContext *ctx, u32 *slot)
{
    g_operand_value = *(const u8 *)(*slot);
    capture(ctx, slot);
    g_operand_seen++;
    /* The cursor slot is writable and the loop honours the new value; that is
     * what makes inline operands possible at all. */
    *slot += 1u;
}

/* Dispatch entry 2: logs, then clears entry 0 so the next 0 byte terminates.
 * A program must end with a 0 byte after this handler. */
static void handler_stop(BciContext *ctx, u32 *slot)
{
    capture(ctx, slot);
    bci_host_dispatch[0] = NULL;
}

/* Dispatch entry 3: re-enters the loop, which must nest. */
static const u8 *g_nested_code;
static BciContext *g_nested_ctx;
static u8 *g_nested_stream_arg;
static int g_nested_done;
static void handler_nested(BciContext *ctx, u32 *slot)
{
    (void)ctx;
    (void)slot;
    sub_08004038(g_nested_ctx, g_nested_code, g_nested_stream_arg);
    g_nested_done = 1;
}

/* ------------------------------------------------------------------------- */
/* Reset between cases. Defined here because it touches every global above.   */
/* ------------------------------------------------------------------------- */
static void reset_all(void)
{
    memset(bci_host_dispatch, 0, sizeof(bci_host_dispatch));
    memset(bci_host_stack, 0, sizeof(bci_host_stack));
    memset(g_arena, 0, sizeof(g_arena));
    bci_host_stream = 0u;
    bci_host_depth = 0u;
    g_arena_used = 0u;
    g_alloc_calls = 0;
    g_free_calls = 0;
    g_alloc_fail = 0;
    g_last_alloc = NULL;
    g_last_freed = NULL;
    g_unpack_calls = 0;
    g_unpack_dst = NULL;
    g_unpack_src = NULL;
    g_unpack_bytes = 0u;
    g_assert_calls = 0;
    g_assert_message = NULL;
    g_assert_file = NULL;
    g_assert_line = 0u;
    g_calls = 0;
    g_capture_calls = 0;
    g_stream_at_entry = 0u;
    g_depth_high_water = 0u;
    memset(g_stack_seen, 0, sizeof(g_stack_seen));
    memset(g_opcode_log, 0, sizeof(g_opcode_log));
    memset(g_cursor_log, 0, sizeof(g_cursor_log));
    memset(g_next_byte_log, 0, sizeof(g_next_byte_log));
    g_operand_seen = 0;
    g_operand_value = 0u;
    g_nested_done = 0;
    g_nested_code = NULL;
    g_nested_ctx = NULL;
    g_nested_stream_arg = NULL;
}

/* ------------------------------------------------------------------------- */
int main(void)
{
    static BciContext ctx;
    static BciContext ctx_outer;
    static BciContext ctx_inner;
    static u8 code[64];
    static u8 nested_code[8];
    static u32 stream_words[4];

    /* ---- 1. the cursor advances by one per dispatch, BEFORE the call ------ */
    reset_all();
    memset(&ctx, 0, sizeof(ctx));
    memset(code, 0, sizeof(code));
    code[0] = 0u;   /* entry 0: plain    */
    code[1] = 0u;   /* entry 0: plain    */
    code[2] = 0u;   /* entry 0: plain    */
    code[3] = 2u;   /* entry 2: stop     */
    code[4] = 0u;   /* entry 0, now NULL */
    bci_host_dispatch[0] = handler_plain;
    bci_host_dispatch[2] = handler_stop;
    sub_08004038(&ctx, code, NULL);

    check(g_calls == 4, "four dispatches: three plain then the stopper", (unsigned long)g_calls);
    check(g_opcode_log[0] == 0u, "dispatch 1 consumed byte 0", g_opcode_log[0]);
    check(g_opcode_log[1] == 0u, "dispatch 2 consumed byte 1", g_opcode_log[1]);
    check(g_opcode_log[2] == 0u, "dispatch 3 consumed byte 2", g_opcode_log[2]);
    check(g_opcode_log[3] == 2u, "dispatch 4 consumed byte 3", g_opcode_log[3]);
    check(g_cursor_log[0] == (u32)(code + 1),
          "the cursor is advanced BEFORE the handler runs (adds r1,#1 and str r1,[sp,#4] at 0x08004068)",
          (unsigned long)(g_cursor_log[0] - (u32)code));
    check(g_cursor_log[1] == (u32)(code + 2), "the cursor advances by exactly one byte per dispatch",
          (unsigned long)(g_cursor_log[1] - (u32)code));
    check(g_next_byte_log[0] == 0u, "the cursor slot points at the next undecoded byte", g_next_byte_log[0]);
    check(g_ctx_log[0] == &ctx, "the handler receives the context (adds r0,r4,#0 at 0x08004090)", 0ul);
    check(g_slot_log[0] != NULL, "the handler receives the ADDRESS of the cursor slot", 0ul);
    check(g_slot_log[0] == g_slot_log[1] && g_slot_log[1] == g_slot_log[3],
          "one cursor slot is handed to every handler in a run (adds r1,r6,#0 at 0x0800408E)", 0ul);

    /* ---- 2. a handler can consume inline operands ------------------------- */
    /* The discriminating shape: code[1] is the inline OPERAND and code[2] is the
     * stopper. If the handler failed to advance the cursor, the loop would read
     * code[1] as an opcode (entry 0, a plain handler) and take one extra
     * dispatch, so g_calls would be 3 and the stopper would land at index 2. */
    reset_all();
    memset(&ctx, 0, sizeof(ctx));
    memset(code, 0, sizeof(code));
    code[0] = 1u;      /* entry 1: operand                                    */
    code[1] = 0x00u;   /* its inline operand: a VALID but unwanted opcode     */
    code[2] = 2u;      /* entry 2: stop, reached only if the operand skipped  */
    code[3] = 0x00u;   /* entry 0, now NULL: terminates                       */
    bci_host_dispatch[0] = handler_plain;
    bci_host_dispatch[1] = handler_operand;
    bci_host_dispatch[2] = handler_stop;
    sub_08004038(&ctx, code, NULL);

    check(g_operand_seen == 1, "the operand-consuming handler ran exactly once", (unsigned long)g_operand_seen);
    check(g_operand_value == 0x00u, "the handler saw the byte after the opcode as its operand", g_operand_value);
    check(g_calls == 2, "the loop did NOT dispatch the operand byte as an opcode", (unsigned long)g_calls);
    check(g_opcode_log[1] == 2u, "the second dispatch read byte 2, not byte 1", (unsigned long)g_opcode_log[1]);
    check(g_cursor_log[1] == (u32)(code + 3),
          "a handler rewrite of *slot moves the loop by exactly the amount it wrote",
          (unsigned long)(g_cursor_log[1] - (u32)code));

    /* ---- 3. entry state: fields, stream mirror, and the depth push -------- */
    reset_all();
    memset(&ctx, 0, sizeof(ctx));
    memset(code, 0, sizeof(code));
    ctx.field_00 = 0xFFFFFFFFu;
    ctx.field_44 = 0xFFFFFFFFu;
    ctx.field_58 = 0xFFFFFFFFu;
    code[0] = 2u;
    code[1] = 0u;
    bci_host_dispatch[2] = handler_stop;
    sub_08004038(&ctx, code, (u8 *)stream_words);

    check(ctx.field_00 == 0u, "context+0x00 is zeroed on entry (str r0,[r4] at 0x0800405C)", ctx.field_00);
    check(ctx.field_44 == 0u, "context+0x44 is zeroed on entry (str r0,[r4,#0x44] at 0x08004060)", ctx.field_44);
    check(ctx.field_58 == (u32)stream_words,
          "context+0x58 receives the stream argument (str r2,[r4,#0x58] at 0x08004054)", ctx.field_58);
    check(g_stream_at_entry == (u32)stream_words,
          "the global mirror receives the same value (str r2,[r5] at 0x08004058)", g_stream_at_entry);
    check(g_depth_high_water == 1u, "entry increments the nesting counter exactly once",
          (unsigned long)g_depth_high_water);
    check(g_stack_seen[0] == (u32)&ctx,
          "entry stores the context at stack[old counter] (str r4,[r0,#4] at 0x08004048)",
          (unsigned long)g_stack_seen[0]);
    check(bci_host_depth == 0u, "the TERMINATE path decrements the counter back to zero",
          (unsigned long)bci_host_depth);

    /* ---- 4. a NULL stream argument defaults to context+0x5c --------------- */
    reset_all();
    memset(&ctx, 0, sizeof(ctx));
    memset(code, 0, sizeof(code));
    code[0] = 2u;
    code[1] = 0u;
    bci_host_dispatch[2] = handler_stop;
    sub_08004038(&ctx, code, NULL);
    check(ctx.field_58 == (u32)((u8 *)&ctx + 0x5Cu),
          "a NULL stream argument becomes context+0x5c (adds r2,r4,#0 then adds r2,#0x5c at 0x0800404E)",
          (unsigned long)(ctx.field_58 - (u32)&ctx));

    /* ---- 5. nesting: the terminate path mirrors the CALLER's +0x58 -------- */
    reset_all();
    memset(&ctx_outer, 0, sizeof(ctx_outer));
    memset(&ctx_inner, 0, sizeof(ctx_inner));
    memset(code, 0, sizeof(code));
    memset(nested_code, 0, sizeof(nested_code));
    code[0] = 3u;            /* entry 3: re-enter */
    code[1] = 2u;            /* entry 2: stop     */
    code[2] = 0u;
    nested_code[0] = 2u;     /* entry 2: stop     */
    nested_code[1] = 0u;
    g_nested_code = nested_code;
    g_nested_ctx = &ctx_inner;
    g_nested_stream_arg = (u8 *)stream_words;
    bci_host_dispatch[2] = handler_stop;
    bci_host_dispatch[3] = handler_nested;
    sub_08004038(&ctx_outer, code, (u8 *)stream_words);

    check(g_nested_done == 1, "the nested run returned to its handler", 0ul);
    check(g_depth_high_water == 2u, "the nested run pushed the counter to 2", (unsigned long)g_depth_high_water);
    check(g_stack_seen[0] == (u32)&ctx_outer, "stack[0] holds the outer context while nested", (unsigned long)g_stack_seen[0]);
    check(g_stack_seen[1] == (u32)&ctx_inner, "stack[1] holds the nested context", (unsigned long)g_stack_seen[1]);
    check(ctx_inner.field_58 == (u32)stream_words, "the inner run received the stream argument", ctx_inner.field_58);
    check(bci_host_depth == 0u, "both nesting levels have been popped", (unsigned long)bci_host_depth);

    /* ---- 6. the dispatch table's extent, and NULL as the terminator ------- */
    check(BCI_DISPATCH_ENTRIES == 31u,
          "the table has 31 entries, bounded by the assertion string at 0x0805553C",
          (unsigned long)BCI_DISPATCH_ENTRIES);
    reset_all();
    memset(&ctx, 0, sizeof(ctx));
    memset(code, 0, sizeof(code));
    code[0] = 29u;
    code[1] = 30u;
    code[2] = 17u;    /* the NULL slot: the game's own terminator */
    code[3] = 0xFFu;  /* outside the table; must never be read */
    bci_host_dispatch[29] = handler_plain;
    bci_host_dispatch[30] = handler_plain;
    sub_08004038(&ctx, code, NULL);
    check(g_calls == 2, "a NULL entry ends the run before an out-of-range byte is read", (unsigned long)g_calls);
    check(g_opcode_log[0] == 29u, "slot 29 dispatched", g_opcode_log[0]);
    check(g_opcode_log[1] == 30u, "slot 30, the last in-range entry, dispatched", g_opcode_log[1]);

    /* ---- 7. sub_08004098: type 0 runs the body at record+3 --------------- */
    reset_all();
    memset(&ctx, 0, sizeof(ctx));
    {
        static u8 dialog[8];
        const u8 *holder = dialog;
        BciContext *returned;
        memset(dialog, 0, sizeof(dialog));
        dialog[2] = 0u;   /* type 0  */
        dialog[3] = 2u;   /* body: stop */
        dialog[4] = 0u;
        bci_host_dispatch[2] = handler_stop;
        returned = sub_08004098(&ctx, &holder, NULL);
        check(returned == &ctx, "sub_08004098 returns the context it was given", 0ul);
        check(g_calls == 1, "type 0 ran the loop exactly once", (unsigned long)g_calls);
        check(g_cursor_log[0] == (u32)(dialog + 4),
              "the body started at record+3 (adds r1,r0,#3 at 0x080040EA)",
              (unsigned long)(g_cursor_log[0] - (u32)dialog));
        check(g_assert_calls == 0, "type 0 does not assert", (unsigned long)g_assert_calls);
    }

    /* ---- 8. sub_08004098: type 4 unpacks, runs the buffer, frees it ------ */
    reset_all();
    memset(&ctx, 0, sizeof(ctx));
    {
        static u8 dialog[0x900];
        const u8 *holder = dialog;
        BciContext *returned;
        memset(dialog, 0, sizeof(dialog));
        dialog[2] = 4u;   /* type 4 */
        dialog[4] = 2u;   /* unpacked body: stop */
        dialog[5] = 0u;
        g_unpack_bytes = 4u;
        bci_host_dispatch[2] = handler_stop;
        returned = sub_08004098(&ctx, &holder, NULL);
        check(returned == &ctx, "type 4 returns the context", 0ul);
        check(g_alloc_calls == 1, "type 4 allocates exactly once (movs r0,#0x6c is not taken here)", (unsigned long)g_alloc_calls);
        check(g_unpack_calls == 1, "type 4 unpacks exactly once", (unsigned long)g_unpack_calls);
        check(g_unpack_src == (const void *)(dialog + 4),
              "the unpack source is record+4 (adds r1,r0,#4 at 0x080040CE)",
              (unsigned long)((const u8 *)g_unpack_src - dialog));
        check(g_unpack_dst == g_last_alloc, "the unpack destination is the fresh allocation", 0ul);
        check(g_free_calls == 1, "type 4 frees the buffer afterwards", (unsigned long)g_free_calls);
        check(g_last_freed == g_unpack_dst, "the freed pointer is the unpack destination", 0ul);
        check(g_calls == 1, "type 4 ran the loop once over the unpacked buffer", (unsigned long)g_calls);
    }

    /* ---- 9. sub_08004098: a NULL context is allocated -------------------- */
    reset_all();
    {
        static u8 dialog[8];
        const u8 *holder = dialog;
        BciContext *returned;
        memset(dialog, 0, sizeof(dialog));
        dialog[2] = 0u;
        dialog[3] = 2u;
        dialog[4] = 0u;
        bci_host_dispatch[2] = handler_stop;
        returned = sub_08004098(NULL, &holder, NULL);
        check(returned != NULL, "a NULL context is allocated rather than dereferenced", 0ul);
        check(g_alloc_calls == 1, "exactly one allocation happened", (unsigned long)g_alloc_calls);
        check(g_last_alloc == returned, "the allocated block IS the returned context", 0ul);
    }

    /* ---- 10. sub_08004098: a failed allocation returns NULL -------------- */
    reset_all();
    {
        static u8 dialog[8];
        const u8 *holder = dialog;
        BciContext *returned;
        memset(dialog, 0, sizeof(dialog));
        dialog[2] = 0u;
        g_alloc_fail = 1;
        returned = sub_08004098(NULL, &holder, NULL);
        check(returned == NULL, "a failed allocation returns NULL", 0ul);
        check(g_calls == 0, "no dispatch happens after a failed allocation (bne at 0x080040AC)", (unsigned long)g_calls);
    }

    /* ---- 11. sub_08004098: any other type asserts with file and line ----- */
    reset_all();
    memset(&ctx, 0, sizeof(ctx));
    {
        static u8 dialog[8];
        const u8 *holder = dialog;
        memset(dialog, 0, sizeof(dialog));
        dialog[2] = 9u;
        (void)sub_08004098(&ctx, &holder, NULL);
        check(g_assert_calls == 1, "an unknown dialog type asserts exactly once", (unsigned long)g_assert_calls);
        check(g_assert_message == (const void *)0x0805553Cu,
              "the assertion message is the string at 0x0805553C", (unsigned long)g_assert_message);
        check(g_assert_line == 60u, "the assertion reports line 60 (movs r2,#0x3c at 0x080040F4)", (unsigned long)g_assert_line);
        check(g_assert_file != NULL &&
              strcmp(g_assert_file, "T:\\Source\\ByteCodeInterpreter\\ByteCodeInterpreter.cpp") == 0,
              "the assertion names this unit's original source path", 0ul);
        check(g_calls == 0, "an unknown type does not run the loop", (unsigned long)g_calls);
        check(ctx.field_00 == 0u && ctx.field_44 == 0u, "fields are zeroed even on the failing path", 0ul);
    }

    /* ---- 12. sub_08004102: a zero counter skips the mirror --------------- */
    reset_all();
    memset(&ctx, 0, sizeof(ctx));
    bci_host_stream = 0x12345678u;
    sub_08004102(&ctx);
    check(bci_host_stream == 0x12345678u,
          "with a zero counter the mirror is skipped (beq at 0x0800410A)", bci_host_stream);

    /* ---- 13. sub_08004102: a first match copies and re-points ------------ */
    reset_all();
    memset(&ctx, 0, sizeof(ctx));
    memset(stream_words, 0, sizeof(stream_words));
    stream_words[0] = 0x11111111u;
    stream_words[1] = 0x22222222u;
    stream_words[2] = 0x33333333u;
    stream_words[3] = 0x44444444u;
    ctx.field_58 = (u32)stream_words;
    bci_host_depth = 1u;
    bci_host_stack[0] = (u32)&ctx;
    sub_08004102((BciContext *)stream_words);
    check(ctx.inline_5c == 0x11111111u, "a first match copies word 0 into context+0x5c", ctx.inline_5c);
    check(ctx.inline_60 == 0x22222222u, "word 1 into context+0x60", ctx.inline_60);
    check(ctx.inline_64 == 0x33333333u, "word 2 into context+0x64", ctx.inline_64);
    check(ctx.inline_68 == 0x44444444u, "word 3 into context+0x68", ctx.inline_68);
    check(ctx.field_58 == (u32)((u8 *)&ctx + 0x5Cu),
          "the match is re-pointed at its own inline area (adds r3,r1,#0 then adds r3,#0x5c at 0x08004134)",
          (unsigned long)(ctx.field_58 - (u32)&ctx));
    check(bci_host_stream == ctx.field_58, "the final mirror is the top context's +0x58", bci_host_stream);

    /* ---- 14. sub_08004102: later matches share the FIRST match's area ---- */
    reset_all();
    memset(&ctx, 0, sizeof(ctx));
    memset(&ctx_outer, 0, sizeof(ctx_outer));
    memset(stream_words, 0, sizeof(stream_words));
    stream_words[0] = 0xAAAABBBBu;
    ctx.field_58 = (u32)stream_words;          /* stack[0]: the first match */
    ctx_outer.field_58 = (u32)stream_words;    /* stack[1]: a later match   */
    bci_host_depth = 2u;
    bci_host_stack[0] = (u32)&ctx;
    bci_host_stack[1] = (u32)&ctx_outer;
    sub_08004102((BciContext *)stream_words);
    check(ctx_outer.field_58 == (u32)((u8 *)&ctx + 0x5Cu),
          "a later match points at the FIRST match's area, not its own (str r3,[r1,#0x58] at 0x08004138)",
          (unsigned long)(ctx_outer.field_58 - (u32)&ctx_outer));
    check(ctx_outer.inline_5c == 0u, "a later match does not copy the words itself", ctx_outer.inline_5c);
    check(ctx.inline_5c == 0xAAAABBBBu, "the first match copied the words", ctx.inline_5c);

    /* ---- 15. the pool words and the context size ------------------------- */
    check(bci_literal_pool[0] == 0x03001034u, "pool word 0 is the nesting counter address", bci_literal_pool[0]);
    check(bci_literal_pool[1] == 0x080554C0u, "pool word 1 is the dispatch table address", bci_literal_pool[1]);
    check(sizeof(BciContext) == 0x6Cu,
          "the context layout is exactly the 0x6c bytes the caller allocates",
          (unsigned long)sizeof(BciContext));

    printf("%s: %d check(s), %d failure(s)\n",
           failures ? "FAIL" : "PASS", checks, failures);
    return failures ? 1 : 0;
}
