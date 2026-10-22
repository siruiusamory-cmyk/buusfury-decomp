	CODE16
|sub_0802C4BA|
	LSL      r0, r0, #0xc
	ADD      r6, sp, #0x1c0
	LSR      r4, r0, #0x20
	ADD      r0, #0x8c
	LSL      r0, r0, #0xc
	LDR      r2, [sp, #0x330]
	LSR      r4, r0, #0x20
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	LDR      r6, [pc, #0x1b8]
	ADD      r4, r0, #0
	LDR      r1, [r6]
	ADD      r0, #0xc
	ADD      r1, #0xff
	ADD      r1, #0xa1
	LDMIA    r1!, {r2}
	SUB      sp, #0x14
	STMIA    r0!, {r2}
	LDR      r1, [r1]
	LDR      r5, [pc, #0x1a8]
	STR      r1, [r0]
	LDR      r1, [pc, #0x1a4]
	ADD      r5, #8
	LDR      r0, [r1]
	CMP      r0, #0
	BNE      |loc_0802C4FA|
	MOV      r0, #1
	STR      r0, [r1]
	LSL      r0, r0, #0xb
	SUB      r1, r5, #4
	STR      r0, [r1]
	LDR      r0, [pc, #0x194]
	STR      r0, [r5]
|loc_0802C4FA|
	MOV      r1, #0x14
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r0, [r6]
	MOV      r7, #0
	STRB     r7, [r0, #0x11]
	LDR      r1, [pc, #0x184]
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r0, [r6]
	LDR      r1, [sp, #0x18]
	LDR      r3, [pc, #0x174]
	ADD      r1, #0xff
	ADD      r1, #0xa1
	ADD      r3, #4
	LDR      r3, [r3]
	LDMIA    r1!, {r2}
	LDR      r1, [r1]
	ADD      r2, r2, r3
	LDR      r3, [r5]
	STR      r2, [sp, #4]
	ADD      r1, r1, r3
	STR      r1, [sp, #8]
	ADD      r1, r2, #0
	LDR      r2, [sp, #8]
	ADD      r0, #0xff
	ADD      r0, #0xa1
	STR      r1, [sp, #0xc]
	STR      r2, [sp, #0x10]
	STMIA    r0!, {r1}
	LDR      r1, [sp, #0x10]
	STR      r1, [r0]
	LDR      r0, [r6]
	LDRB     r1, [r0, #8]
	ADD      r1, #0xff
	STRB     r1, [r0, #8]
	STR      r7, [r4, #8]
	STRB     r7, [r4, #0x15]
	MOV      r0, #0xff
	ADD      r0, #0x30
	STRB     r7, [r4, #0x14]
	BL       |inc_0x0158_0x143f2|
	ADD      r2, r0, #0
	LDR      r0, [pc, #0x13c]
	MOV      r1, #5
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x11b18
	STR      r0, [r4, #4]
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #4]
	ADD      r7, r1, #0
	LDR      r1, [r0]
	LDR      r2, [r1, #0x34]
	ADD      r2, r2, r1
	MOV      r1, #9
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r6, r4, #0
	ADD      r6, #0xc
	ADD      r5, r6, #4
	CMP      r0, #0
	BEQ      |sub_0802C5BA|
	LDR      r1, [pc, #0x100]
	LDR      r2, [r6]
	LDR      r0, [r1]
	ADD      r0, #0xff
	ADD      r0, #0xa1
	STMIA    r0!, {r2}
	LDR      r2, [r5]
	STR      r2, [r0]
	LDR      r0, [r1]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r1, [r7]
	ADD      r0, r7, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #9
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #1
	STRB     r0, [r4, #0x14]
	MOV      r0, #0x3c
	STRB     r0, [r4, #0x15]
	MOV      r0, #0
	POP      {r3, r4, r5, r6, r7, pc}
