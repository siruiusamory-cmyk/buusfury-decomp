/*
 * src/probes/iwramdispatch_selftest.c
 *
 * HOST SEMANTIC CHECK for src/IwramDispatch.c, the interrupt entry the boot code
 * installs at IWRAM 0x03000B6C (ROM 0x087B8510).
 *
 * It compiles the reconstruction for the HOST and RUNS it against a modelled
 * machine: a modelled REG_IE/REG_IF/REG_IME block, a modelled 14-entry vector
 * table with the software pending halfword immediately after it, and modelled
 * environment hooks for the three facilities C cannot express - SPSR, the CPSR
 * mode switch, and the ARM -> Thumb -> ARM handler call.
 *
 * Conventions the modelled machine keeps, because the assertions depend on them:
 *
 *   * REG_IE is the LOW half of the 32-bit word at 0x04000200 and REG_IF is the
 *     HIGH half, so the dispatcher's single `ldr r2, [r3, #0x200]!` /
 *     `str r2, [r3]` pair sees and writes exactly what the machine's 32-bit
 *     access at that address sees;
 *   * the modelled IF is plain storage: the test asserts on the WORD THE
 *     DISPATCHER WRITES, which is what the ROM instruction fixes. That writing
 *     a 1 to an IF bit CLEARS the hardware flag is an INFERRED hardware
 *     behaviour and is not claimed by any assertion here;
 *   * the vector entries are given DISTINCT synthetic values so that the target
 *     passed to the handler call identifies the slot. The cartridge's entries
 *     are fourteen identical words and cannot distinguish a slot; that real
 *     value is asserted from the ROM by tests/test_lift_iwramdispatch.py.
 *
 * What this exists to pin, because each is what a "tidier" reconstruction gets
 * wrong:
 *
 *   * the priority chain's ORDER, which is not numeric: 10, 7, 6, 0, 1, 2, 3,
 *     4, 5, 8, 9, 11, 12, then a spin for 13;
 *   * the acknowledge happens BEFORE the handler runs, and the pending word
 *     already carries the served mask when the handler is entered;
 *   * the FIRST test (bit 10) skips the BIC: its IE bit is NOT cleared. That is
 *     an artifact of the original and is asserted as such, not smoothed over;
 *   * the verify-restore path puts IE, IME and SPSR back;
 *   * a pending enabled bit 13 SPINS FOREVER, calls no handler and restores
 *     nothing - bounded here by a wall-clock budget;
 *   * bits 14 and 15 are tested by nothing and are never serviced.
 *
 * Built 32-bit: the model stores addresses in u32 fields, exactly as the
 * machine under reconstruction does.
 */

#include <stdio.h>
#include <string.h>

#ifdef _WIN32
#include <windows.h>   /* the only way to bound the bit-13 spin: a thread */
#endif

#define IWRAMDISPATCH_HOST_TEST 1
#include "IwramDispatch.c"

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
/* The modelled I/O block: REG_IE / REG_IF / REG_IME                          */
/* ------------------------------------------------------------------------- */
#define IO_BYTES      0x210
#define IO_IE_OFFSET  0x200
#define IO_IF_OFFSET  0x202
#define IO_IME_OFFSET 0x208

static unsigned char g_io[IO_BYTES];

static u16 io_u16(u32 offset)
{
    u16 value;
    memcpy(&value, g_io + offset, 2);
    return value;
}

static void io_set_u16(u32 offset, u16 value)
{
    memcpy(g_io + offset, &value, 2);
}

static u16 io_ie(void)  { return io_u16(IO_IE_OFFSET); }
static u16 io_if(void)  { return io_u16(IO_IF_OFFSET); }
static u16 io_ime(void) { return io_u16(IO_IME_OFFSET); }

/* ------------------------------------------------------------------------- */
/* The modelled vector table, with the pending halfword at base + 0x38        */
/* ------------------------------------------------------------------------- */
#define VECTOR_ENTRIES 14
#define VECTOR_WORDS   16        /* 14 entries, then the pending halfword */

static u32 g_vector[VECTOR_WORDS];

static u32 vec_entry(int index)
{
    u32 value;
    memcpy(&value, (unsigned char *)g_vector + 4 * index, 4);
    return value;
}

static void vec_set_entry(int index, u32 value)
{
    memcpy((unsigned char *)g_vector + 4 * index, &value, 4);
}

static u16 vec_pending(void)
{
    u16 value;
    memcpy(&value, (unsigned char *)g_vector + 0x38, 2);
    return value;
}

static void vec_set_pending(u16 value)
{
    memcpy((unsigned char *)g_vector + 0x38, &value, 2);
}

/* ------------------------------------------------------------------------- */
/* Host substitutes for the environment                                       */
/* ------------------------------------------------------------------------- */
u32 iwramdispatch_host_io_base;
u32 iwramdispatch_host_vector_base;

/* Registered handlers: the target value the dispatcher passes identifies the
 * slot, which is how the priority order becomes observable. */
static u32 g_target[VECTOR_ENTRIES];
static int g_target_count;

static int g_calls;
static int g_last_slot;
static u32 g_target_at_call;
static int g_unknown_target;

static int g_read_spsr_calls;
static int g_write_spsr_calls;
static u32 g_spsr_read;
static u32 g_spsr_written;

static int g_read_cpsr_calls;
static u32 g_cpsr;

static int g_enter_mode_calls;
static u32 g_enter_mode_value;
static int g_leave_mode_calls;
static u32 g_leave_mode_value;

/* The modelled machine's state AT THE MOMENT the handler is entered. */
static u16 g_ie_at_call;
static u16 g_if_at_call;
static u16 g_ime_at_call;
static u16 g_pending_at_call;

u32 env_read_spsr(void)
{
    g_read_spsr_calls++;
    return g_spsr_read;
}

void env_write_spsr(u32 value)
{
    g_write_spsr_calls++;
    g_spsr_written = value;
}

u32 env_read_cpsr(void)
{
    g_read_cpsr_calls++;
    return g_cpsr;
}

void env_enter_handler_mode(u32 cpsr_value)
{
    g_enter_mode_calls++;
    g_enter_mode_value = cpsr_value;
}

void env_leave_handler_mode(u32 cpsr_value)
{
    g_leave_mode_calls++;
    g_leave_mode_value = cpsr_value;
}

/* The handler call. The installed handler in the cartridge is the single
 * halfword 0x4770 `bx lr` at 0x0803F3D8, so the modelled handler is an empty
 * body: the point of recording here is to snapshot the machine's state at the
 * instant the handler runs. */
void env_enter_handler(u32 target)
{
    int index;

    g_calls++;
    g_target_at_call = target;
    for (index = 0; index < g_target_count; index++) {
        if (g_target[index] == target) {
            break;
        }
    }
    g_last_slot = (index < g_target_count) ? index : -1;
    if (g_last_slot < 0) {
        g_unknown_target = 1;
    }
    g_ie_at_call = io_ie();
    g_if_at_call = io_if();
    g_ime_at_call = io_ime();
    g_pending_at_call = vec_pending();
}

/* ------------------------------------------------------------------------- */
/* The modelled machine's reset                                               */
/* ------------------------------------------------------------------------- */
static void reset_model(void)
{
    int index;

    memset(g_io, 0, sizeof(g_io));
    memset(g_vector, 0xEE, sizeof(g_vector));
    for (index = 0; index < VECTOR_ENTRIES; index++) {
        /* Distinct, odd (Thumb-style) targets: the cartridge's fourteen equal
         * words cannot say which slot was selected, and that is the whole
         * point of the ordering assertions. */
        g_target[index] = 0x0803F001u + 4u * (u32)index;
        vec_set_entry(index, g_target[index]);
    }
    g_target_count = VECTOR_ENTRIES;
    vec_set_pending(0u);

    iwramdispatch_host_io_base = (u32)(unsigned long)g_io;
    iwramdispatch_host_vector_base = (u32)(unsigned long)g_vector;

    g_calls = 0;
    g_last_slot = -1;
    g_target_at_call = 0u;
    g_unknown_target = 0;
    g_read_spsr_calls = 0;
    g_write_spsr_calls = 0;
    g_spsr_read = 0xA5A5A5A5u;
    g_spsr_written = 0u;
    g_read_cpsr_calls = 0;
    g_cpsr = 0x60000013u;      /* modelled CPSR: ARM state, I bit clear */
    g_enter_mode_calls = 0;
    g_enter_mode_value = 0u;
    g_leave_mode_calls = 0;
    g_leave_mode_value = 0u;
    g_ie_at_call = 0u;
    g_if_at_call = 0u;
    g_ime_at_call = 0u;
    g_pending_at_call = 0u;
}

/* The 13 bits the chain can serve, in TEST ORDER. Slot = bit for every one of
 * them, which is the property the slot assertions below pin. */
static const int REACHABLE[13] = { 10, 7, 6, 0, 1, 2, 3, 4, 5, 8, 9, 11, 12 };

/* Pairs that distinguish the order. (first, second) means both bits are pending
 * with IE == IF and the FIRST one must be the handler that runs. */
static const int WINNER[9] = { 10, 10, 7, 7, 6, 0, 5, 9, 11 };
static const int LOSER[9]  = {  7,  0, 6, 0, 0, 1, 8, 11, 12 };

/* ------------------------------------------------------------------------- */
/* The bit-13 spin, bounded by a wall-clock budget                            */
/* ------------------------------------------------------------------------- */
#ifdef _WIN32
static volatile int g_spin_returned;

static DWORD WINAPI spin_thread(LPVOID unused)
{
    (void)unused;
    sub_087B8510();
    g_spin_returned = 1;
    return 0;
}
#endif

/* ------------------------------------------------------------------------- */
int main(void)
{
    int i;

    setvbuf(stdout, NULL, _IONBF, 0);

    /* ===================================================================== */
    /* 0. the model is the shape the assertions assume                        */
    /* ===================================================================== */
    reset_model();
    check(VECTOR_ENTRIES == 14 && vec_entry(13) != 0u,
          "the modelled table has 14 entries", (unsigned long)vec_entry(13));
    {
        int distinct = 1;
        for (i = 0; i < VECTOR_ENTRIES && distinct; i++) {
            int j;
            for (j = i + 1; j < VECTOR_ENTRIES; j++) {
                if (vec_entry(i) == vec_entry(j)) {
                    distinct = 0;
                    break;
                }
            }
        }
        check(distinct, "every modelled entry is distinct, so a slot is identifiable",
              (unsigned long)g_target[0]);
    }
    vec_set_pending(0x1234u);
    check(vec_pending() == 0x1234u && vec_entry(13) == g_target[13],
          "the pending halfword at +0x38 does not overlap entry 13",
          (unsigned long)vec_pending());

    /* ===================================================================== */
    /* 1. the no-pending path takes the restore branch, with no handler       */
    /* ===================================================================== */
    reset_model();
    io_set_u16(IO_IE_OFFSET, 0x0000u);
    io_set_u16(IO_IF_OFFSET, 0x0000u);
    /* A non-zero, non-one IME: the saved value has to be distinguishable both
     * from the 1 the routine writes into it at entry and from zero. */
    io_set_u16(IO_IME_OFFSET, 0x0004u);
    sub_087B8510();
    check(g_calls == 0, "no pending bit: no handler is called", (unsigned long)g_calls);
    check(g_enter_mode_calls == 0 && g_leave_mode_calls == 0,
          "no pending bit: the CPSR mode switch is never reached",
          (unsigned long)g_enter_mode_calls);
    check(g_read_spsr_calls == 1 && g_write_spsr_calls == 1 && g_spsr_written == g_spsr_read,
          "no pending bit: SPSR is still read and restored",
          (unsigned long)g_spsr_written);
    check(io_ie() == 0x0000u, "no pending bit: IE is restored",
          (unsigned long)io_ie());
    check(io_ime() == 0x0004u, "no pending bit: IME is restored to the value read at entry",
          (unsigned long)io_ime());
    check(vec_pending() == 0u, "no pending bit: nothing is recorded in the pending word",
          (unsigned long)vec_pending());
    check(io_if() == 0x0000u, "no pending bit: IF is untouched",
          (unsigned long)io_if());

    /* ===================================================================== */
    /* 2. bits 14 and 15 are tested by nothing: never serviced                 */
    /* ===================================================================== */
    reset_model();
    io_set_u16(IO_IE_OFFSET, 0x4000u);
    io_set_u16(IO_IF_OFFSET, 0x4000u);
    io_set_u16(IO_IME_OFFSET, 0x0000u);
    sub_087B8510();
    check(g_calls == 0, "a pending enabled bit 14 calls no handler", (unsigned long)g_calls);
    check(vec_pending() == 0u, "a pending enabled bit 14 records nothing",
          (unsigned long)vec_pending());
    check(io_ie() == 0x4000u, "a pending enabled bit 14 leaves IE exactly as it was",
          (unsigned long)io_ie());

    reset_model();
    io_set_u16(IO_IE_OFFSET, 0x8000u);
    io_set_u16(IO_IF_OFFSET, 0x8000u);
    sub_087B8510();
    check(g_calls == 0, "a pending enabled bit 15 calls no handler", (unsigned long)g_calls);

    /* ===================================================================== */
    /* 3. IE without its IF flag is not serviced: the scan is IE & IF         */
    /* ===================================================================== */
    reset_model();
    io_set_u16(IO_IE_OFFSET, 0x0080u);
    io_set_u16(IO_IF_OFFSET, 0x0000u);
    sub_087B8510();
    check(g_calls == 0, "IE set with IF clear is not serviced", (unsigned long)g_calls);
    check(io_ie() == 0x0080u && io_if() == 0x0000u,
          "IE set with IF clear leaves both registers as they were",
          (unsigned long)io_ie());

    reset_model();
    io_set_u16(IO_IE_OFFSET, 0x0000u);
    io_set_u16(IO_IF_OFFSET, 0x0080u);
    sub_087B8510();
    check(g_calls == 0, "IF set with IE clear is not serviced", (unsigned long)g_calls);
    check(vec_pending() == 0u, "IF set with IE clear records nothing",
          (unsigned long)vec_pending());

    /* ===================================================================== */
    /* 4. every reachable slot: offset/4, the acknowledge, the pending word,  */
    /*    the mode value, and the restore                                     */
    /* ===================================================================== */
    for (i = 0; i < 13; i++) {
        u32 mask = 1u << REACHABLE[i];
        int bit = REACHABLE[i];

        reset_model();
        io_set_u16(IO_IE_OFFSET, (u16)mask);
        io_set_u16(IO_IF_OFFSET, (u16)mask);
        io_set_u16(IO_IME_OFFSET, 0x0006u);

        sub_087B8510();

        check(g_calls == 1, "one pending bit calls exactly one handler",
              (unsigned long)((bit << 8) | g_calls));
        check(g_last_slot == bit, "the slot selected is offset/4 for this bit",
              (unsigned long)((bit << 8) | (g_last_slot & 0xFF)));
        check(g_unknown_target == 0, "the handler target is an entry of the modelled table",
              (unsigned long)g_target_at_call);
        check(g_enter_mode_calls == 1 && g_leave_mode_calls == 1,
              "the handler-mode switch is entered once and left once",
              (unsigned long)((g_enter_mode_calls << 8) | g_leave_mode_calls));
        check((g_enter_mode_value & 0x1Fu) == 0x1Fu,
              "the mode value's low five bits are the mode the chain selected",
              (unsigned long)g_enter_mode_value);
        check(((g_enter_mode_value & 0x80u) != 0u) == (bit == 10),
              "only the bit-10 slot is entered with the I bit left set",
              (unsigned long)g_enter_mode_value);
        check(g_leave_mode_value == g_cpsr,
              "the CPSR snapshot is restored unchanged after the handler",
              (unsigned long)g_leave_mode_value);

        /* The acknowledge, observed AT CALL TIME. */
        if (bit == 10) {
            check((g_ie_at_call & (u16)mask) != 0u,
                  "bit 10 SKIPS the BIC: its IE flag is NOT cleared (the artifact)",
                  (unsigned long)g_ie_at_call);
        } else {
            check((g_ie_at_call & (u16)mask) == 0u,
                  "the served bit is cleared in IE BEFORE the handler runs",
                  (unsigned long)g_ie_at_call);
        }
        check((g_if_at_call & (u16)mask) != 0u,
              "the served bit is set in IF BEFORE the handler runs",
              (unsigned long)g_if_at_call);
        check(g_pending_at_call == (u16)mask,
              "the pending word already carries the served mask at call time",
              (unsigned long)g_pending_at_call);
        check(g_ime_at_call == 1u,
              "REG_IME is 1 while the handler runs", (unsigned long)g_ime_at_call);

        /* After the return. */
        check(io_ie() == (u16)mask, "IE is restored from the saved low half",
              (unsigned long)io_ie());
        check(io_ime() == 0x0006u,
              "IME is restored to the value read at entry, not left at the 1 written at entry",
              (unsigned long)io_ime());
        check(vec_pending() == (u16)mask, "the pending word keeps the served mask after the return",
              (unsigned long)vec_pending());
        check(g_write_spsr_calls == 1 && g_spsr_written == 0xA5A5A5A5u,
              "SPSR is written back with the value read at entry",
              (unsigned long)g_spsr_written);
    }
    check(g_last_slot <= 12, "no path ever selected slot 13", (unsigned long)g_last_slot);

    /* ===================================================================== */
    /* 5. the priority ORDER, on the pairs that distinguish it                */
    /* ===================================================================== */
    for (i = 0; i < 9; i++) {
        u32 win = 1u << WINNER[i];
        u32 lose = 1u << LOSER[i];
        u32 both = win | lose;

        reset_model();
        io_set_u16(IO_IE_OFFSET, (u16)both);
        io_set_u16(IO_IF_OFFSET, (u16)both);
        io_set_u16(IO_IME_OFFSET, 0x0000u);

        sub_087B8510();

        check(g_calls == 1 && g_last_slot == WINNER[i],
              "with two bits pending, the earlier test in the chain wins",
              (unsigned long)((WINNER[i] << 16) | (LOSER[i] << 8) | (g_last_slot & 0xFF)));
        check(g_pending_at_call == (u16)win,
              "only the SERVED bit is recorded in the pending word, not every pending bit",
              (unsigned long)g_pending_at_call);
        if (WINNER[i] == 10) {
            check(g_ie_at_call == (u16)both,
                  "a win by bit 10 leaves IE entirely unchanged",
                  (unsigned long)g_ie_at_call);
        } else {
            check(g_ie_at_call == (u16)(both & ~win),
                  "only the served bit is cleared in IE; the loser's IE bit survives",
                  (unsigned long)g_ie_at_call);
        }
        check(g_if_at_call == (u16)(both | win),
              "the IF word written keeps the loser's flag and adds the served one",
              (unsigned long)g_if_at_call);
        check((g_if_at_call & (u16)lose) != 0u,
              "the losing bit's IF flag is not cleared by this pass",
              (unsigned long)g_if_at_call);
        check(io_ie() == (u16)both && vec_pending() == (u16)win,
              "the exit restores IE and keeps the accumulated pending mask",
              (unsigned long)io_ie());
    }

    /* ===================================================================== */
    /* 6. the pending word ACCUMULATES, it is not assigned                    */
    /* ===================================================================== */
    reset_model();
    vec_set_pending(0x0002u);
    io_set_u16(IO_IE_OFFSET, 0x0080u);
    io_set_u16(IO_IF_OFFSET, 0x0080u);
    sub_087B8510();
    check(g_pending_at_call == 0x0082u,
          "the pending word is ORed, so a previous bit survives at call time",
          (unsigned long)g_pending_at_call);
    check(vec_pending() == 0x0082u,
          "and it still carries both bits after the return",
          (unsigned long)vec_pending());

    reset_model();
    vec_set_pending(0x0002u);
    io_set_u16(IO_IE_OFFSET, 0x0004u);
    io_set_u16(IO_IF_OFFSET, 0x0004u);
    sub_087B8510();
    check(vec_pending() == 0x0006u,
          "a second, different bit accumulates into the same word",
          (unsigned long)vec_pending());

    /* ===================================================================== */
    /* 7. bit 13 SPINS FOREVER                                                */
    /* ===================================================================== */
#ifdef _WIN32
    {
        HANDLE thread;
        DWORD waited;

        reset_model();
        io_set_u16(IO_IE_OFFSET, 0x2000u);
        io_set_u16(IO_IF_OFFSET, 0x2000u);
        io_set_u16(IO_IME_OFFSET, 0x0000u);
        g_spin_returned = 0;

        thread = CreateThread(NULL, 0, spin_thread, NULL, 0, NULL);
        check(thread != NULL, "the bit-13 probe thread starts", (unsigned long)GetLastError());
        if (thread != NULL) {
            waited = WaitForSingleObject(thread, 400);
            check(waited == WAIT_TIMEOUT && g_spin_returned == 0,
                  "bit 13 does not return within the budget: the self-branch SPINS",
                  (unsigned long)waited);
            check(g_calls == 0, "the bit-13 spin calls no handler", (unsigned long)g_calls);
            check(g_enter_mode_calls == 0 && g_leave_mode_calls == 0,
                  "the bit-13 spin never enters or leaves the handler mode",
                  (unsigned long)g_enter_mode_calls);
            check(g_write_spsr_calls == 0,
                  "the bit-13 spin never restores the SPSR: it never reaches the exit path",
                  (unsigned long)g_write_spsr_calls);
            check(io_if() == 0x2000u && vec_pending() == 0u && io_ie() == 0x2000u,
                  "the bit-13 spin acknowledges nothing and records nothing",
                  (unsigned long)vec_pending());
            TerminateThread(thread, 1);
            CloseHandle(thread);
        }
    }
#else
    printf("NOTE: bit 13's spin is not bounded on this host; see tests/test_lift_iwramdispatch.py\n");
#endif

    printf("%s: %d check(s), %d failure(s)\n",
           failures ? "FAIL" : "PASS", checks, failures);
    return failures ? 1 : 0;
}
