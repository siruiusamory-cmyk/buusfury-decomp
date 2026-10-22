	CODE16
|sub_0802A9A8|
	PUSH     {r4, lr}
	LDR      r1, [r0, #0x34]
	STR      r1, [r0, #0x30]
	LDRB     r3, [r1, #2]
	LDRB     r4, [r1, #3]
	LDRH     r0, [r0, #0xc]
	LDR      r1, [r1, #8]
	MUL      r3, r4
	ADD      r2, r3, #0
	LDR      r3, [pc, #0x4c]
	LSL      r0, r0, #5
	ADD      r0, r0, r3
	BL       |inc_0x049120_0x055620| + 0x18
	POP      {r4, pc}
	ADD      r2, r1, #0
	MOV      r1, #0
	CMP      r2, #0xb
	PUSH     {r3, lr}
	BEQ      |sub_0802A9E2|
	CMP      r2, #0xc
	BNE      |loc_0802A9E8|
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	MOV      r0, #0
	POP      {r3, pc}
