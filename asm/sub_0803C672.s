	CODE16
|sub_0803C672|
	LSL      r0, r0, #0
	STMIA    r4!, {r4, r6}
	LSR      r7, r6, #1
	ADD      r0, r1, #0
	LDR      r1, [pc, #0xc4]
	PUSH     {r3, lr}
	LDR      r2, [r1]
	CMP      r2, #0
	BEQ      |loc_0803C688|
	LDRB     r1, [r2, #0x10]
	STRB     r1, [r0, #0x10]
|loc_0803C688|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r5, r1, #0
	ADD      r5, #0xff
	ADD      r5, #0xa1
	LDR      r0, [r5]
	ADD      r4, r1, #0
	LDR      r1, [r5, #4]
	SUB      sp, #0x14
	ASR      r0, r0, #8
	ASR      r1, r1, #8
	STR      r1, [sp, #8]
	STR      r1, [sp, #0x10]
	STR      r0, [sp, #4]
	STR      r0, [sp, #0xc]
	LDRB     r0, [r4, #0x10]
	LDR      r1, [pc, #0x8c]
	ADD      r6, r5, #4
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	LDR      r1, [r0]
	LDR      r0, [r0, #4]
	LDR      r2, [sp, #0xc]
	LSL      r1, r1, #1
	STR      r1, [sp]
	ADD      r7, r2, r1
	LDR      r1, [sp, #0x10]
	LSL      r0, r0, #1
	STR      r0, [sp, #4]
	ADD      r0, r1, r0
	STR      r0, [sp, #4]
	STR      r0, [sp, #8]
	STR      r7, [sp]
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x48]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [sp, #8]
	LSL      r2, r7, #8
	LSL      r0, r0, #8
	STR      r0, [sp, #4]
	STR      r2, [sp]
	LDR      r2, [r4]
	ADD      r0, r4, #0
	LDR      r3, [r2, #0x54]
	MOV      r1, sp
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BEQ      |sub_0803C71C|
	LDR      r0, [sp]
	STR      r0, [r5]
	LDR      r0, [sp, #4]
	STR      r0, [r6]
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x48]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
