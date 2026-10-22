	CODE16
|sub_0803043E|
	LSL      r0, r0, #0
	BHI      |loc_08030424|
	LSR      r4, r0, #0x20
	STRH     r0, [r2, #0xc]
	LSR      r5, r6, #1
	LDR      r1, [sp, #0x1e0]
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r1, #0
	MOV      r0, #0x2d
	SUB      sp, #0x2c
	BL       |inc_0x0158_0x143f2|
	ADD      r2, r0, #0
	LDR      r6, [pc, #0x80]
	MOV      r1, #5
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x11b18
	CMP      r0, #0
	BEQ      |sub_0803046E|
	MOV      r0, #1
	ADD      sp, #0x2c
	POP      {r4, r5, r6, r7, pc}
