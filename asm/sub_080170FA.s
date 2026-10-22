	CODE16
|sub_080170FA|
	LSL      r0, r0, #0
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STRH     r4, [r3, #0x16]
	LSR      r3, r5, #1
	STR      r4, [sp, #0x220]
	LSR      r1, r6, #0x20
	STR      r2, [sp, #0x30]
	LSR      r4, r0, #0x20
|unk_0801710C|
	INCBIN	baserom.gba_0x1710c_0x1710e.extracted
	LSR      r4, r0, #0x20
	LDR      r0, [sp, #0x3c0]
	LSR      r4, r0, #0x20
	ADD      r4, r2, r4
	LSL      r0, r0, #0xc
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	PUSH     {r3, lr}
	LDR      r0, [r0, #8]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r0, [r0, #8]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, pc}
	LDRH     r0, [r0, #0xe]
	LDR      r1, [pc, #0x1c]
	LSL      r0, r0, #2
	ADD      r0, r0, r1
	SUB      r0, #0x40
	LDR      r0, [r0, #0x18]
	BX       lr
	PUSH     {r3, lr}
	LDR      r0, [r0, #8]
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, pc}
	LSL      r0, r0, #0
	LDR      r4, [r3, #0x3c]
	LSR      r3, r5, #1
