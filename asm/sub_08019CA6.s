	CODE16
|sub_08019CA6|
	PUSH     {r4, lr}
	LDR      r1, [r0, #0x18]
	STR      r1, [r0, #0x14]
	LDRB     r3, [r1, #2]
	LDRB     r4, [r1, #3]
	LDRH     r0, [r0, #0xc]
	LDR      r1, [r1, #8]
	MUL      r3, r4
	ADD      r2, r3, #0
	LDR      r3, [pc, #0x64]
	LSL      r0, r0, #5
	ADD      r0, r0, r3
	BL       |inc_0x049120_0x055620| + 0x18
	POP      {r4, pc}
	PUSH     {r3, lr}
	ADD      r3, r1, #0
	MOV      r1, #0
	CMP      r3, #0xb
	BEQ      |sub_08019CE6|
	CMP      r3, #0xc
	BEQ      |loc_08019CEC|
	CMP      r3, #0x11
	BEQ      |loc_08019CDA|
	CMP      r3, #0x12
	BNE      |loc_08019CFC|
|loc_08019CDA|
	LDR      r3, [r0, #0x1c]
	CMP      r3, r2
	BNE      |loc_08019CE2|
	STR      r1, [r0, #0x1c]
|loc_08019CE2|
	MOV      r0, #0
	POP      {r3, pc}
