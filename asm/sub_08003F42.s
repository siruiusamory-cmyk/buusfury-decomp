	CODE16
|sub_08003F42|
	LSR      r5, r0, #0x20
	STRB     r0, [r7, r1]
	LSR      r5, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	LDR      r2, [r1]
	ADD      r4, r0, #0
	LDRB     r0, [r2]
	ADD      r2, #1
	STR      r2, [r1]
	LSL      r5, r0, #2
	LDR      r0, [pc, #0xd8]
	LDR      r1, [r0, r5]
	ADD      r0, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r4]
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	ADD      r0, r1, #0
	LDR      r1, [pc, #0xc4]
	LDR      r1, [r1, r5]
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r2, [r1]
	ADD      r4, r0, #0
	LDRB     r0, [r2]
	ADD      r2, #1
	STR      r2, [r1]
	LSL      r5, r0, #2
	LDR      r0, [pc, #0xa8]
	LDR      r1, [r0, r5]
	ADD      r0, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r4]
	LDR      r1, [pc, #0xa0]
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	LDR      r0, [r0]
	LDR      r1, [r1, r5]
	SUB      r0, #1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, r4, r5, pc}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r2, [r1, #4]
	ADD      r0, #0x44
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	ADD      r3, r0, #0
	LDR      r0, [r0, #0x44]
	ADD      r3, #0x44
	LSL      r0, r0, #2
	ADD      r0, r0, r3
	LDR      r2, [r0]
	SUB      r2, #1
	STR      r2, [r0]
	LDR      r0, [r1]
	BNE      |loc_08003FE0|
	ADD      r0, #2
	STR      r0, [r1]
	LDR      r0, [r3]
	SUB      r0, #1
	STR      r0, [r3]
	BX       lr
|loc_08003FE0|
	LDRB     r2, [r0]
	LDRB     r3, [r0, #1]
	LSL      r2, r2, #8
	ORR      r2, r3
	SUB      r0, r0, r2
	STR      r0, [r1]
	BX       lr
|sub_08003FEE|
|unk_08003FEE|
	INCBIN	baserom.gba_0x3fee_0x3ff8.extracted
