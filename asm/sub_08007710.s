	CODE16
|sub_08007710|
	ADD      r0, r7, r4
	LSL      r0, r0, #0xc
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	ADD      r0, r2, #0
	LDR      r1, [r2]
	ADD      r4, r2, #0
	MOV      r2, #0x84
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1f
	BEQ      |sub_0800773A|
	LDRB     r0, [r5, #4]
	LDRB     r1, [r4, #0x10]
	CMP      r0, r1
	BNE      |sub_0800773A|
	MOV      r0, #1
	POP      {r3, r4, r5, pc}
