	CODE16
|sub_0800C368|
	PUSH     {r3, lr}
	LDR      r0, [r0, #0x10]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, pc}
	LDR      r2, [pc, #0xcc]
	PUSH     {r4, r5, r6}
	LDR      r2, [r2, #4]
	LDR      r3, [pc, #0xcc]
	LSL      r2, r2, #0x18
	LSR      r2, r2, #0x16
	LDR      r2, [r3, r2]
	LDR      r3, [r1]
	ASR      r4, r2, #0xe
	LDR      r2, [pc, #0xa4]
	ADD      r5, r3, #0
	ADD      r5, #8
	LDR      r2, [r2, #4]
	STR      r5, [r1]
	LDR      r1, [pc, #0xb8]
	ADD      r2, #0x28
	STR      r1, [r3]
	LDR      r5, [r0, #0x14]
	LDR      r6, [r2]
	LDRH     r5, [r5]
	SUB      r5, r5, r6
	SUB      r5, #0x10
	LSL      r5, r5, #0x17
	LSR      r5, r5, #7
	ORR      r1, r5
	STR      r1, [r3]
	LDR      r5, [r0, #0x14]
	LDR      r2, [r2, #4]
	LDRH     r5, [r5, #2]
	LSR      r1, r1, #8
	LSL      r1, r1, #8
	ADD      r4, r5, r4
	SUB      r2, r4, r2
	ADD      r2, #0xf8
	LSL      r2, r2, #0x18
	LSR      r2, r2, #0x18
	ORR      r1, r2
	STR      r1, [r3]
	LDRB     r1, [r0, #8]
	LDR      r2, [r3, #4]
	MOV      r4, #3
	LSL      r1, r1, #0x1a
	LSR      r1, r1, #0x1e
	LSL      r4, r4, #0xa
	BIC      r2, r4
	LSL      r1, r1, #0xa
	ORR      r1, r2
	STR      r1, [r3, #4]
	LDRH     r0, [r0, #0xc]
	LSR      r1, r1, #0xa
	LSL      r1, r1, #0xa
	LSL      r0, r0, #0x16
	LSR      r0, r0, #0x16
	ORR      r0, r1
	STR      r0, [r3, #4]
	POP      {r4, r5, r6}
	MOV      r0, #0
	BX       lr
	CMP      r1, #4
	BLT      |sub_0800C3F4|
	MOV      r0, #2
	BX       lr
