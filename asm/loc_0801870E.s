	CODE16
|loc_0801870E|
	PUSH     {r3, r4, r5, r6, r7, lr}
	MOV      r6, #0
	CMP      r1, #0xa
	LDR      r2, [pc, #0x74]
	BEQ      |sub_08018752|
	CMP      r1, #0xb
	BNE      |loc_08018782|
	LDR      r0, [r0, #0x10]
	CMP      r0, #0
	BEQ      |loc_0801874E|
	LDR      r4, [r0, #8]
	LDRH     r5, [r0, #2]
	LDR      r7, [r0, #4]
	LDRB     r0, [r4]
	ADD      r1, r0, #1
	STRB     r1, [r4]
	CMP      r0, #0
	BNE      |loc_0801874E|
	ADD      r1, r5, #0
	LDR      r0, [r2]
	BL       |inc_0x0158_0x143f2| + 0x110f4
	LSL      r0, r0, #0x10
	ASR      r0, r0, #0x10
	STRH     r0, [r4, #2]
	LDR      r1, [pc, #0x4c]
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	ADD      r2, r5, #0
	ADD      r1, r7, #0
	BL       |inc_0x049120_0x055620| + 0x18
|loc_0801874E|
	ADD      r0, r6, #0
	POP      {r3, r4, r5, r6, r7, pc}
