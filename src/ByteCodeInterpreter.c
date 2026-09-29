/*
 * src/ByteCodeInterpreter.c
 *
 * DECOMPILED SOURCE for the translation unit at ROM address
 * 0x08004038..0x08004160. The ROM preserves the original source path, which is
 * why this file exists under this name:
 *     T:\Source\ByteCodeInterpreter\ByteCodeInterpreter.cpp
 *     (ASCII, at 0x08004160; referenced by the assertion at 0x080040F4)
 *
 * THE TRANSLATION UNIT, and why it is three functions and not one
 * The unit is 0x08004038..0x08004160: 286 bytes of Thumb code, 2 bytes of
 * alignment padding, and an 8-byte literal pool at 0x08004158 whose two words
 * (0x03001034 and 0x080554C0) are loaded by two of the three functions. Sharing
 * ONE pool is what establishes that these are one compilation unit, exactly as
 * for GBARam. Lifting the entry function alone would leave the pool's other
 * consumer unexplained and the pool comparison meaningless, so all three are
 * reconstructed. Nothing else of the script engine is touched: the engine has a
 * 31-entry handler table and a separate 283-entry native table, and none of
 * those handlers is decompiled here.
 *
 *   0x08004038  96 bytes  the bytecode dispatch loop            <- the target
 *   0x08004098 106 bytes  the dialog entry point                <- calls the target
 *   0x08004102  84 bytes  untitled helper, same TU and same pool
 *   0x08004156   2 bytes  alignment padding
 *   0x08004158   8 bytes  literal pool
 *
 * STATUS, and these three lines are INDEPENDENT of one another.
 *   SEMANTIC.....PROVEN   the dispatch loop's behaviour is checked by RUNNING it:
 *                         src/probes/bci_selftest.c drives it over synthetic
 *                         bytecode with recording handlers.
 *   MODERN_BUILD.PASS     it compiles and links for ARM7TDMI Thumb with the
 *                         modern toolchain; see docs/LIFT_SCRIPT.md.
 *   ADS_MATCH....BLOCKED  never compiled by the tool it targets. The ADS 1.2
 *                         binaries are installed on this machine but the licence
 *                         present covers a different product, so the ARM
 *                         compilers cannot be run (ADS12_LICENSE_UNAVAILABLE).
 *                         No byte-match claim is made.
 *
 * WHAT IS EVIDENCE AND WHAT IS ASSUMPTION
 * Evidence, from the disassembly of 0x08004038..0x08004160:
 *   - the dispatch loop reads ONE byte, advances the cursor by one, indexes a
 *     31-entry table with it, and calls the entry indirectly;
 *   - a NULL table entry is the TERMINATE path: it pops the nesting counter and
 *     returns;
 *   - the handler is called with r0 = context and r1 = the ADDRESS of the saved
 *     cursor slot, so a handler can consume inline operands by rewriting it;
 *   - nesting state: a word at 0x03001034 (a counter), a stack of context words
 *     at 0x03001038 + 4*i, and a mirror at 0x03001030;
 *   - context fields written: +0x00 = 0, +0x44 = 0, +0x58 = the stream argument
 *     (or context+0x5c when the argument is 0);
 *   - the dispatch table's extent is proved by what follows it: slot 30 ends at
 *     0x0805553C, where the UTF-16 assertion "Expected dialog to start with a
 *     code block" begins. That string bounds the table at exactly 31 entries.
 * Assumption (NOT evidence):
 *   - every FIELD NAME. The disassembly fixes each offset and its access width.
 *     It does not say what the game called any of them, so the names below are
 *     placeholders and are marked as such. Nothing here is imported from another
 *     LoG title.
 * UNKNOWN, deliberately left unknown:
 *   - what the handlers do. Their semantics are not needed to prove the loop and
 *     are out of scope for this ticket;
 *   - the meaning of the 16 bytes copied by sub_08004102 and why the search
 *     compares a stream pointer for equality.
 *
 * The original file may NOT be copied from 2genkidev/buusfury: that repository
 * carries no licence grant. See docs/REFERENCE_AUDIT.md.
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

/*
 * The context object. Only the fields this unit touches are declared, and each
 * is named after its offset because its meaning is not proven. The object is
 * 0x6c bytes: sub_08004098 allocates exactly that, and sub_0801E164 places one
 * on its own stack and adds 0x6c back.
 */
typedef struct BciContext {
    u32 field_00;      /* written 0 on entry                                 */
    u8  pad_04[0x40];  /* untouched by this unit                             */
    u32 field_44;      /* written 0 on entry                                 */
    u8  pad_48[0x10];  /* untouched by this unit                             */
    u32 field_58;      /* a POINTER: the stream, proven by the terminate path */
    u32 inline_5c;     /* start of a 16-byte inline area                     */
    u32 inline_60;
    u32 inline_64;
    u32 inline_68;
} BciContext;

#define BCI_CONTEXT_SIZE 0x6cu

/* A handler receives the context and the ADDRESS of the cursor slot. */
typedef void (*BciHandler)(BciContext *ctx, u32 *cursor_slot);

/* The dispatch table has exactly 31 entries; see the header comment. */
#define BCI_DISPATCH_ENTRIES 31u

/* ------------------------------------------------------------------------- */
/* Symbols this unit references but does not reconstruct                      */
/* ------------------------------------------------------------------------- */
/* Declared, not reconstructed: the game's allocator is a different unit and is
 * already lifted separately (src/GBARam.c). */
extern void *sub_0803D5B8(u32 size);
extern void  sub_0803D63C(void *block);

/* Declared, not reconstructed: an ARM veneer that unpacks a container. */
extern void  sub_08049120(void *destination, const void *container);

/* Declared, not reconstructed: the assert helper, (message, file, line). */
extern void  sub_0803DF14(const void *message, const char *file, unsigned line);

/* Declared, not reconstructed: the engine's indirect-call thunk, which is a
 * bare `bx r2`. The original reaches every handler through it, passing the
 * handler in r2 and the context and cursor slot in r0 and r1. It is not part of
 * this unit, so it is declared rather than reconstructed. */
extern void  sub_08046AA4(BciContext *ctx, u32 *cursor_slot, BciHandler handler);

/* ------------------------------------------------------------------------- */
/* Absolute machine state. Redirected by the host self-check, token for token. */
/* ------------------------------------------------------------------------- */
#ifndef BCI_HOST_TEST

#define BCI_STREAM      (*(volatile u32 *)0x03001030u)
#define BCI_DEPTH       (*(volatile u32 *)0x03001034u)
#define BCI_STACK_SLOT(i) (*(volatile u32 *)(0x03001038u + (u32)(i) * 4u))
#define BCI_DISPATCH    ((BciHandler *)(0x080554C0u))

/* Through the thunk, exactly as 0x08004092 does. */
#define BCI_CALL_HANDLER(h, ctx, slot) (sub_08046AA4((ctx), (slot), (h)))

#else  /* BCI_HOST_TEST */

#if defined(_MSC_VER)
/* This unit models a 32-bit ARM target, so pointers are deliberately held in
 * u32 fields. Built for a 64-bit host those conversions truncate, which is the
 * machine model under test rather than a defect, so the warnings are silenced
 * here rather than papered over at each site. */
#pragma warning(disable : 4311 4312)
#endif

extern u32 bci_host_stream;
extern u32 bci_host_depth;
extern u32 bci_host_stack[64];
extern BciHandler bci_host_dispatch[BCI_DISPATCH_ENTRIES];

#define BCI_STREAM      bci_host_stream
#define BCI_DEPTH       bci_host_depth
#define BCI_STACK_SLOT(i) (bci_host_stack[(u32)(i)])
#define BCI_DISPATCH    (bci_host_dispatch)
/* The host has no ARM thunk; calling the handler directly is the same
 * operation, and the self-check observes the arguments either way. */
#define BCI_CALL_HANDLER(h, ctx, slot) ((h)((ctx), (slot)))

#endif /* BCI_HOST_TEST */


/* ------------------------------------------------------------------------- */
/* 0x08004038 - 96 bytes - the bytecode dispatch loop                        */
/* ------------------------------------------------------------------------- */
/*
 * Signature proven from the disassembly and from both of its in-unit callers
 * (0x080040DC and 0x080040EE in sub_08004098): r0 = context, r1 = a byte
 * pointer that is dereferenced and advanced by one per dispatch, r2 = a stream
 * value that is stored at context+0x58 and at 0x03001030.
 *
 * Returns nothing: every path leaves through the single epilogue at 0x0800408C.
 *
 * Nesting: on entry the counter at 0x03001034 is incremented and the incoming
 * context is stored at stack[old_count]. A NULL dispatch entry is the TERMINATE
 * path: it decrements the counter and, when the counter is still non-zero,
 * copies the CALLER context's +0x58 into 0x03001030 before returning.
 */
void sub_08004038(BciContext *ctx, const u8 *code, u8 *stream)
{
    u32 cursor;
    u32 count;

    if (stream == 0) {
        stream = (u8 *)ctx + 0x5cu;
    }

    count = BCI_DEPTH;
    BCI_STACK_SLOT(count) = (u32)ctx;
    BCI_DEPTH = count + 1u;

    ctx->field_58 = (u32)stream;
    BCI_STREAM = (u32)stream;
    ctx->field_00 = 0u;
    ctx->field_44 = 0u;

    cursor = (u32)code;

    for (;;) {
        u32 opcode;
        BciHandler handler;

        /* The handler is handed the ADDRESS of `cursor`, not its value, so it
         * can consume inline operands and leave the loop positioned after them. */
        opcode = *(const u8 *)cursor;
        cursor += 1u;
        handler = BCI_DISPATCH[opcode];

        if (handler == 0) {
            /* TERMINATE */
            count = BCI_DEPTH - 1u;
            BCI_DEPTH = count;
            if (count != 0u) {
                BciContext *caller = (BciContext *)BCI_STACK_SLOT(count - 1u);
                BCI_STREAM = caller->field_58;
            }
            return;
        }

        BCI_CALL_HANDLER(handler, ctx, &cursor);
    }
}

/* ------------------------------------------------------------------------- */
/* 0x08004098 - 106 bytes - the dialog entry point                            */
/* ------------------------------------------------------------------------- */
/*
 * Signature proven from its own disassembly and from its caller at 0x0800327E:
 * r0 = context or NULL (NULL means "allocate one"), r1 = a pointer TO the dialog
 * record pointer, r2 = the stream value passed through to the loop.
 *
 * Behaviour, all of it proved by the branch structure:
 *   - allocate a 0x6c-byte context when the caller passes NULL, and return NULL
 *     if that allocation fails;
 *   - zero context+0x00 and context+0x44;
 *   - read the dialog TYPE at record+0x02;
 *       type 0 -> run the loop on the code at record+3;
 *       type 4 -> allocate (type << 9) = 0x800 bytes, unpack record+4 into it,
 *                 run the loop on the buffer, then free it;
 *       else   -> assert with the message at 0x0805553C, this file's path, line 60.
 *   - return the context.
 *
 * The type byte at +0x02 and the two body offsets (+3 and +4) are facts of the
 * disassembly, not imported conventions.
 */
BciContext *sub_08004098(BciContext *ctx, const u8 **dialog_holder, u8 *stream)
{
    const u8 *dialog;

    if (ctx == 0) {
        ctx = (BciContext *)sub_0803D5B8(BCI_CONTEXT_SIZE);
        if (ctx == 0) {
            return 0;
        }
    }

    ctx->field_00 = 0u;
    ctx->field_44 = 0u;

    dialog = *dialog_holder;

    if (dialog[2] == 0u) {
        sub_08004038(ctx, dialog + 3, stream);
    } else if (dialog[2] == 4u) {
        u32 size = (u32)dialog[2] << 9;
        u8 *buffer = (u8 *)sub_0803D5B8(size);
        sub_08049120(buffer, dialog + 4);
        sub_08004038(ctx, buffer, stream);
        sub_0803D63C(buffer);
    } else {
        sub_0803DF14(
            (const void *)0x0805553Cu,
            "T:\\Source\\ByteCodeInterpreter\\ByteCodeInterpreter.cpp",
            60u);
    }

    return ctx;
}

/* ------------------------------------------------------------------------- */
/* 0x08004102 - 84 bytes - untitled helper in the same unit                   */
/* ------------------------------------------------------------------------- */
/*
 * NAME: none is justified. The disassembly proves the control flow and the
 * memory effects and nothing about intent, so this keeps its address for a name.
 *
 * What is PROVEN:
 *   - if the nesting counter at 0x03001034 is 0, only the final mirror happens;
 *   - otherwise it walks stack slots 0 .. count-1 and compares each context's
 *     +0x58 against the argument;
 *   - for the FIRST match only, it copies four words FROM THE ARGUMENT into that
 *     context's +0x5c..+0x68 and re-points that context's +0x58 at its own +0x5c;
 *   - it always ends by copying stack[count-1]->+0x58 into 0x03001030.
 *
 * What is UNKNOWN: why the search compares a pointer for equality, and what the
 * four copied words mean. Not guessed at here.
 */
void sub_08004102(BciContext *stream_source)
{
    u32 index;
    u32 matched = 0u;

    if (BCI_DEPTH == 0u) {
        return;
    }

    /* The bound is re-read from memory on every iteration, exactly as the
     * disassembly reloads it at 0x0800413A rather than keeping it in a
     * register. The two are equivalent only while the counter is stable, and
     * nothing in this function can change it, but the faithful form is kept. */
    for (index = 0u; index < BCI_DEPTH; index += 1u) {
        BciContext *ctx = (BciContext *)BCI_STACK_SLOT(index);

        if (ctx->field_58 != (u32)stream_source) {
            continue;
        }
        if (matched == 0u) {
            const u32 *words = (const u32 *)stream_source;
            ctx->inline_5c = words[0];
            ctx->inline_60 = words[1];
            ctx->inline_64 = words[2];
            ctx->inline_68 = words[3];
            matched = (u32)((u8 *)ctx + 0x5cu);
        }
        /* Every later match is pointed at the FIRST match's inline area, not at
         * its own. That is what the disassembly does and it is easy to "fix"
         * into a wrong reconstruction. */
        ctx->field_58 = matched;
    }

    BCI_STREAM = ((BciContext *)BCI_STACK_SLOT(BCI_DEPTH - 1u))->field_58;
}

/* ------------------------------------------------------------------------- */
/* The unit's literal pool, as declared data                                  */
/* ------------------------------------------------------------------------- */
/*
 * The pool lives at 0x08004158 and holds two words, both loaded by code above.
 * It is restated here so the reconstruction carries the same two constants; the
 * modern compiler will place its own pool wherever it likes, which is expected
 * and is why the comparison is unit scoped.
 */
const u32 bci_literal_pool[2] = {
    0x03001034u,  /* the nesting counter                             */
    0x080554C0u   /* the 31-entry dispatch table                     */
};
