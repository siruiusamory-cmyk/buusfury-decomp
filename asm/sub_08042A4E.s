	CODE16
|sub_08042A4E|
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r6, [pc, #0x15c]
	MOV      r7, #0
	ADD      r5, r0, #0
	LDRB     r4, [r6, #0xe]
	STRB     r7, [r6, #0xe]
	MOV      r0, #1
	STRB     r0, [r6, #0xf]
	LDR      r0, [pc, #0x14c]
	LDR      r0, [r0]
	LDRB     r0, [r0]
	CMP      r0, #0
	BNE      |loc_08042A7A|
	ADD      r0, r5, #0
	BL       |loc_08042372|
	LDRB     r0, [r6, #2]
	CMP      r0, #1
	BEQ      |loc_08042A8E|
|loc_08042A74|
	BL       |sub_08043368|
	B        |loc_08042AA4|
|loc_08042A7A|
	MOV      r0, sp
	BL       |inc_0x042118_0x049114| + 0x16f4
	CMP      r0, #0
	BNE      |loc_08042A8E|
	LDRB     r0, [r6, #3]
	ADD      r3, sp, #0
	LDRB     r1, [r3]
	ORR      r0, r1
	STRB     r0, [r6, #3]
|loc_08042A8E|
	LDR      r1, [r6, #0x44]
	CMP      r1, #0
	BEQ      |loc_08042AA4|
	ADD      r0, r5, #0
	BL       |inc_0x046118_0x049114| + 0x98a
	BL       |loc_0804389e|
	LDRB     r0, [r6, #2]
	CMP      r0, #2
	BEQ      |loc_08042A74|
|loc_08042AA4|
	STRB     r7, [r6, #0xf]
	STRB     r4, [r6, #0xe]
	POP      {r3, r4, r5, r6, r7, pc}
