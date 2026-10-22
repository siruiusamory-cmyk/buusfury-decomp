	CODE16
|sub_08016428|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r1]
	MOV      r3, #3
	ADD      r2, r0, #0
	ADD      r2, #8
	STR      r2, [r1]
	MOV      r1, #1
	LSL      r1, r1, #0xd
	STR      r1, [r0]
	LDR      r2, [r4, #0x28]
	LSL      r3, r3, #0xa
	LSL      r2, r2, #0x17
	LSR      r2, r2, #7
	ORR      r1, r2
	STR      r1, [r0]
	LDR      r2, [r4, #0x2c]
	LSR      r1, r1, #8
	LSL      r2, r2, #0x18
	LSR      r2, r2, #0x18
	LSL      r1, r1, #8
	ORR      r1, r2
	STR      r1, [r0]
	LDR      r1, [r4, #0x10]
	LDR      r2, [r0, #4]
	LDRB     r1, [r1, #8]
	BIC      r2, r3
	LSL      r1, r1, #0x1a
	LSR      r1, r1, #0x1e
	LSL      r1, r1, #0xa
	ORR      r1, r2
	STR      r1, [r0, #4]
	LDRH     r2, [r4, #0xc]
	LSR      r1, r1, #0xa
	LSL      r1, r1, #0xa
	LSL      r2, r2, #0x16
	LSR      r2, r2, #0x16
	ORR      r1, r2
	STR      r1, [r0, #4]
	LDR      r0, [r4, #0x18]
	ASR      r1, r0, #0x1f
	LSR      r1, r1, #0x1d
	ADD      r0, r1, r0
	ASR      r5, r0, #3
	LDR      r0, [r4, #0x20]
	CMP      r0, r5
	BEQ      |loc_0801649C|
	LDRH     r0, [r4, #0xc]
	LDR      r1, [pc, #0x40]
	LSL      r2, r5, #6
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	LDR      r1, [r4, #0x24]
	ADD      r1, r1, r2
	MOV      r2, #0x40
	BL       |inc_0x049120_0x055620| + 0x18
	STR      r5, [r4, #0x20]
|loc_0801649C|
	MOV      r0, #0
	POP      {r3, r4, r5, pc}
	PUSH     {r3, lr}
	CMP      r1, #0xc
	BNE      |sub_080164B4|
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	MOV      r0, #0
	POP      {r3, pc}
