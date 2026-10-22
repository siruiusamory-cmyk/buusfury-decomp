	CODE16
|sub_0803740E|
	LDR      r0, [r4, #0x2c]
	LDR      r1, [r4, #0x30]
	MUL      r0, r5
	MUL      r1, r5
	STR      r1, [sp, #4]
	STR      r1, [sp, #0xc]
	ADD      r1, sp, #8
	STR      r0, [sp]
	STR      r1, [sp]
	MOV      r3, #0x10
	MOV      r2, sp
	ADD      r2, r2, r3
	MOV      r1, #1
	STR      r0, [sp, #8]
	ADD      r0, r4, #0
	STR      r7, [sp, #4]
	BL       |loc_080372A4|
	LDR      r0, [r4, #0x34]
	ADD      r5, #0x20
	SUB      r0, #1
	CMP      r0, r5
	BGT      |sub_0803740E|
	LDR      r0, [sp, #0x10]
	STR      r0, [r6]
	ADD      sp, #0x14
	MOV      r0, #0
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	CMP      r1, #0xb
	BEQ      |sub_08037460|
	CMP      r1, #0xc
	BNE      |loc_08037468|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #0
	POP      {r3, pc}
