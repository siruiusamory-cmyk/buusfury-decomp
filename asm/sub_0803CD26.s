	CODE16
|sub_0803CD26|
	LSL      r0, r0, #0xc
	ADD      r6, sp, #0x1c0
	LSR      r4, r0, #0x20
	ADD      r2, #0xf4
	LSL      r0, r0, #0xc
	LDR      r2, [sp, #0x330]
	LSR      r4, r0, #0x20
	STRH     r0, [r3, #4]
	LSR      r3, r5, #1
	STMIA    r4!, {r6, r7}
	LSR      r7, r6, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	MOV      r3, #0x38
	STRB     r3, [r1, #8]
	STRB     r2, [r1, #0x11]
	STR      r2, [r0, #4]
	BX       lr
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r6, r0, #0
	LDRH     r0, [r1, #0x12]
	SUB      sp, #0x1c
	ADD      r4, r1, #0
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	LSR      r5, r0, #3
	STRB     r5, [r1, #0x11]
	LDR      r1, [r6, #4]
	CMP      r1, #0
	BNE      |loc_0803CDE6|
	CMP      r0, #0x18
	BNE      |loc_0803CDE6|
	LDR      r7, [pc, #0xf0]
	LDR      r0, [r7]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r1, #3
	LSL      r1, r1, #9
	CMP      r0, r1
	BGE      |sub_0803CD94|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
