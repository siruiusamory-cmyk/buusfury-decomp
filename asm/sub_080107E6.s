	CODE16
|sub_080107E6|
	LSR      r7, r0, #0x20
	STRH     r4, [r5, #0x16]
	LSR      r3, r5, #1
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	STMIA    r5!, {r2, r5, r7}
	LSR      r7, r6, #1
	STMIA    r7!, {r3, r5, r6}
	LSR      r4, r0, #0x20
	STR      r6, [sp, #0x2f0]
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, lr}
	MOV      r0, #0xff
	ADD      r0, #0xc9
	LDR      r0, [r0, r1]
	LDRB     r2, [r2]
	ADD      r4, r1, #0
	MOV      r1, #1
	EOR      r1, r2
	CMP      r0, #0
	SUB      sp, #0x18
	BEQ      |sub_08010862|
	LDRB     r0, [r4, #0x10]
	CMP      r0, r1
	BNE      |sub_08010862|
	LDRB     r0, [r4, #0x10]
	LDR      r1, [pc, #0x328]
	ADD      r5, r4, #0
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	ADD      r5, #0xff
	ADD      r5, #0xa1
	LDR      r1, [r5]
	LDMIA    r0!, {r2}
	ADD      r6, r5, #4
	ADD      r1, r1, r2
	LDR      r2, [r5, #4]
	LDR      r0, [r0]
	STR      r1, [sp]
	ADD      r0, r2, r0
	STR      r0, [sp, #4]
	ADD      r0, r1, #0
	LDR      r1, [sp, #4]
	STR      r0, [sp, #8]
	STR      r0, [sp, #0x10]
	LDR      r0, [pc, #0x300]
	SUB      r2, r5, #4
	STR      r1, [sp, #0xc]
	STR      r1, [sp, #0x14]
	SUB      r0, #0x78
	LDR      r0, [r0, #0xc]
	ADD      r1, sp, #0x10
	BL       |loc_080097EA|
	CMP      r0, #0
	BEQ      |loc_0801085E|
	LDR      r0, [sp, #0x10]
	STR      r0, [r5]
	LDR      r0, [sp, #0x14]
	STR      r0, [r6]
|loc_0801085E|
	ADD      sp, #0x18
	POP      {r4, r5, r6, pc}
