/*
 * src/ByteCodeInterpreter_gather.c
 *
 * DECOMPILED SOURCE for sub_080032C2: the routine that reads a run of bits out
 * of the flag array and packs them into one mask, pushed back onto the VM stack.
 *
 *   0x080032C2  78 bytes  38 instructions  one terminator at 0x0800330E
 *
 * A LEAF apart from its single call to the already-lifted reader sub_08004364,
 * and it loads one literal, 0x08054FBC.
 *
 * THE ROUTINE, AS THE MACHINE EXECUTES IT
 *   0x080032C2  push {r3-r7, lr}
 *   0x080032C4  adds r5, r0, #0        r5 = context
 *   0x080032C6  ldr  r0, [r0]          r0 = the counter
 *   0x080032C8  movs r6, #0            r6 = 0, THE ACCUMULATOR MASK
 *   0x080032CA  subs r0, #1
 *   0x080032CC  lsls r1, r0, #2
 *   0x080032CE  str  r0, [r5]          counter = count-1        <- POP 1
 *   0x080032D0  adds r1, r1, r5
 *   0x080032D2  ldr  r7, [r1, #4]      r7 = values[count-1]     <- THE BOUND
 *   0x080032D4  subs r0, #1
 *   0x080032D6  str  r0, [r5]          counter = count-2        <- POP 2
 *   0x080032D8  lsls r0, r0, #2
 *   0x080032DA  adds r0, r0, r5
 *   0x080032DC  ldr  r0, [r0, #4]      r0 = values[count-2]     <- THE BIT OFFSET
 *   0x080032DE  movs r4, #0            r4 = 0, the loop index n
 *   0x080032E0  cmp  r7, #0
 *   0x080032E2  str  r0, [sp]          spill the offset
 *   0x080032E4  ble  0x08003302        bound <= 0 -> no bits gathered
 *   0x080032E6  ldr  r0, [sp]          the offset
 *   0x080032E8  adds r1, r0, r4        r1 = OFFSET + n
 *   0x080032EA  ldr  r0, [pc, #0x15c]  r0 = 0x08054FBC
 *   0x080032EC  ldr  r0, [r0, #0x14]   r0 = *(0x08054FBC + 0x14)
 *   0x080032EE  bl   0x08004364        flag = test(r0, offset + n)
 *   0x080032F2  cmp  r0, #0
 *   0x080032F4  beq  0x080032FC        not set -> this bit stays 0
 *   0x080032F6  movs r0, #1
 *   0x080032F8  lsls r0, r4            r0 = 1 << n
 *   0x080032FA  orrs r6, r0            mask |= 1 << n
 *   0x080032FC  adds r4, #1            n++
 *   0x080032FE  cmp  r4, r7
 *   0x08003300  blt  0x080032E6        loop while n < bound
 *   0x08003302  ldr  r0, [r5]          r0 = the counter
 *   0x08003304  adds r1, r0, #1
 *   0x08003306  lsls r0, r0, #2
 *   0x08003308  adds r0, r0, r5
 *   0x0800330A  str  r1, [r5]          counter = count+1        <- PUSH
 *   0x0800330C  str  r6, [r0, #4]      values[count] = mask    <- THE MASK IS PUSHED
 *   0x0800330E  pop  {r3-r7, pc}
 *
 * WHAT IT DOES
 * It is a TWO-INTO-ONE reduction over the FLAG ARRAY rather than over the two
 * operands. It pops a BOUND from the top and a BIT OFFSET from beneath it, then
 * for n = 0 .. bound-1 tests the array bit at `offset + n` and sets bit n of a
 * mask when that flag is set. It finally PUSHES the mask as a new stack value.
 *
 * THE OFFSET IS ADDED TO BEFORE THE TEST, and that is the detail worth keeping:
 * the value passed to the reader is `offset + n`, not `n`. The reader splits it
 * into `(offset+n) >> 3` and `(offset+n) & 7`, so successive iterations test
 * successive BITS starting at the caller's offset. The offset is therefore a
 * BIT NUMBER in the flag array, not a byte index and not a pointer.
 *
 * LOOP BOUNDS
 *   - the loop runs while `n < bound`, with n starting at 0, so it gathers
 *     exactly `bound` bits for a positive bound;
 *   - a bound of zero or less is skipped entirely by the `ble`, producing a mask
 *     of 0 with no call to the reader at all;
 *   - there is NO upper clamp, and the shift is REGISTER-controlled, so a bound
 *     above 32 does NOT wrap. ARM7TDMI `LSL` by a register yields ZERO for an
 *     amount of 32 or more, so every iteration at n >= 32 ORs in nothing and
 *     only bits 0..31 of the mask can ever be set. A bound above 32 therefore
 *     gathers the first 32 bits and ignores the rest.
 *
 * THE RESULTING MASK AND WHERE IT GOES
 * The mask is `sum over n in 0..min(bound,32)-1 of (flag[offset+n] ? 1 << n : 0)`,
 * so bit n of the mask is the array bit at `offset + n`, and no bit above 31 can
 * ever be set. The routine then PUSHES it: it
 * increments the counter and stores the mask at `values[count]`. The mask does
 * not leave the VM here. It becomes the new stack top, to be consumed by
 * whatever pops it next, which is as far as this ticket follows it.
 *
 * The net stack effect is TWO CONSUMED, ONE PRODUCED, so the counter moves by
 * exactly -1.
 *
 * NO BOUNDS CHECK, NO NULL CHECK, NO SIZE KNOWLEDGE
 * Nothing tests the offset or the bound against the array's size, and the array
 * size is not reachable from this routine at all: both are runtime values. No
 * guard was added.
 *
 * WHAT IS UNKNOWN
 *   - what the gathered mask means. No semantic name is assigned to it, to the
 *     bits, or to the array;
 *   - how large the array is. The bounds here are runtime values, so this
 *     routine gives no static limit;
 *   - what pops the mask.
 *
 * The original file may NOT be copied from 2genkidev/buusfury: that repository
 * carries no licence grant. See docs/REFERENCE_AUDIT.md.
 */

typedef unsigned int u32;

/* ------------------------------------------------------------------------- */
/* ARM7TDMI register-controlled LSL, modelled explicitly                      */
/* ------------------------------------------------------------------------- */
/*
 * `lsls r0, r4` at 0x080032F8 is a REGISTER-controlled logical left shift: the
 * amount is a runtime value, not an immediate, so the architectural rule has to
 * be written out rather than left to the host language.
 *
 * THE ARM7TDMI RULE (ARMv4T), which is what this machine implements:
 *
 *     amount  0        -> the value is UNCHANGED
 *     amount  1 .. 31  -> a normal left shift
 *     amount  >= 32    -> the result is ZERO
 *
 * C DOES NOT IMPLEMENT THAT. `1u << amount` with an amount of 32 or more is
 * UNDEFINED BEHAVIOUR, and MSVC on x86 masks the amount to five bits, so
 * `1u << 32` yields 1 and `1u << 33` yields 2 - the opposite of the machine,
 * which yields 0 for both. Leaving it to the language would make the host check
 * disagree with the ROM for every bound above 32.
 *
 * The amount is taken as a plain unsigned count, so 255 is simply "32 or more".
 */
static u32 gather_thumb_lsl_1(u32 amount)
{
    if (amount >= 32u) {
        return 0u;
    }
    return 1u << amount;      /* amount is now provably 0..31 */
}

/* ------------------------------------------------------------------------- */
/* Symbols this unit references but does not reconstruct                      */
/* ------------------------------------------------------------------------- */
/* The reader, reconstructed at src/ByteCodeInterpreter_flagread.c. */
extern u32 sub_08004364(void *base, u32 value);

/* ------------------------------------------------------------------------- */
/* Absolute machine state. Redirected by the host self-check.                 */
/* ------------------------------------------------------------------------- */
#ifndef GATHER_HOST_TEST

#define GATHER_GLOBAL_BASE (*(u32 *)0x08054FBCu)

#else  /* GATHER_HOST_TEST */

extern u32 gather_host_global_base;
#define GATHER_GLOBAL_BASE (gather_host_global_base)

#endif /* GATHER_HOST_TEST */

/* ------------------------------------------------------------------------- */
/* 0x080032C2 - 78 bytes - 38 instructions                                    */
/* ------------------------------------------------------------------------- */
/*
 * The interpreter passes r0 = context and r1 = the cursor slot. This routine
 * never reads r1.
 */
void sub_080032C2(void *ctx, u32 *cursor_slot)
{
    u32 *state = (u32 *)ctx;
    u32 count = state[0];
    u32 bound;
    u32 offset;
    u32 mask = 0u;
    u32 n;

    (void)cursor_slot;   /* never read */

    /* POP 1: the top is the bound. */
    count -= 1u;
    state[0] = count;
    bound = ((u32 *)ctx)[(count * 4u) / 4u + 1u];

    /* POP 2: the next value down is the bit offset. */
    count -= 1u;
    state[0] = count;
    offset = ((u32 *)ctx)[(count * 4u) / 4u + 1u];

    /* The bound is compared as a SIGNED value by the `ble`. */
    if ((int)bound > 0) {
        for (n = 0u; n < bound; n++) {
            if (sub_08004364((void *)(GATHER_GLOBAL_BASE + 0x14u), offset + n) != 0u) {
                /* The ARM7TDMI register LSL, not C's shift: for n >= 32 this ORs
                 * in nothing, so only bits 0..31 of the mask can ever be set. */
                mask |= gather_thumb_lsl_1(n);
            }
        }
    }

    /* PUSH: the mask becomes the new top. */
    {
        u32 *top = (u32 *)((u32)ctx + count * 4u);
        state[0] = count + 1u;
        top[1] = mask;
    }
}

/* ------------------------------------------------------------------------- */
/* The unit's literal word, as declared data                                  */
/* ------------------------------------------------------------------------- */
const u32 bci_gather_literal_pool[1] = {
    0x08054FBCu
};
