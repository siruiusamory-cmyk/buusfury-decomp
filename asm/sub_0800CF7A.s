	CODE16
|sub_0800CF7A|
	ADD      r3, r1, #0
	LDR      r1, [pc, #0x224]
	PUSH     {r4, r5}
	LDR      r1, [r1, #4]
	ADD      r2, r1, #0
	LDR      r1, [r3]
	ADD      r2, #0x28
	ADD      r4, r1, #0
	ADD      r4, #8
	STR      r4, [r3]
	LDR      r3, [r0, #0x20]
	LDR      r3, [r3, #0x10]
	STR      r3, [r1]
	LDR      r4, [r0, #0x24]
	LDR      r5, [r2]
	SUB      r4, r4, r5
	LDR      r5, [pc, #0x20c]
	LSL      r4, r4, #0x17
	LSR      r4, r4, #7
	AND      r3, r5
	ORR      r3, r4
	STR      r3, [r1]
	LDR      r4, [r0, #0x28]
	LDR      r2, [r2, #4]
	LSR      r3, r3, #8
	SUB      r2, r4, r2
	LSL      r2, r2, #0x18
	LSR      r2, r2, #0x18
	LSL      r3, r3, #8
	ORR      r2, r3
	STR      r2, [r1]
	LDRB     r2, [r0, #8]
	LDR      r3, [r1, #4]
	MOV      r4, #3
	LSL      r2, r2, #0x1a
	LSR      r2, r2, #0x1e
	LSL      r4, r4, #0xa
	BIC      r3, r4
	LSL      r2, r2, #0xa
	ORR      r2, r3
	STR      r2, [r1, #4]
	LDRH     r0, [r0, #0x16]
	LSR      r2, r2, #0xa
	LSL      r2, r2, #0xa
	LSL      r0, r0, #0x16
	LSR      r0, r0, #0x16
	ORR      r0, r2
	STR      r0, [r1, #4]
	POP      {r4, r5}
	MOV      r0, #0
	BX       lr
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r1, #0
	ADD      r5, r2, #0
	ADD      r4, r0, #0
	ADD      r0, #0xc
	BL       |inc_0x153f2_0x1a3f2| + 0x3fbc
	CMP      r0, #0
	BEQ      |loc_0800CFF6|
	SUB      r0, #1
	POP      {r4, r5, r6, pc}
|loc_0800CFF6|
	CMP      r6, #4
	BNE      |sub_0800D010|
	LDRH     r1, [r4, #0x14]
	ASR      r0, r5, #1
	CMP      r0, r1
	BNE      |sub_0800D00C|
	LSL      r0, r5, #0x1f
	LSR      r0, r0, #0x1f
	STR      r0, [r4, #0x1c]
	MOV      r0, #1
	POP      {r4, r5, r6, pc}
