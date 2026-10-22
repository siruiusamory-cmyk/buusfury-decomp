	CODE16
|sub_08018696|
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	BL       |inc_0x0158_0x143f2| + 0x116c0
	LDR      r0, [r4, #0x10]
	CMP      r0, #0
	BEQ      |loc_080186D2|
	LDR      r4, [r0, #8]
	LDRH     r5, [r0, #2]
	LDR      r6, [r0, #4]
	LDRB     r0, [r4]
	ADD      r1, r0, #1
	STRB     r1, [r4]
	CMP      r0, #0
	BNE      |loc_080186D2|
	LDR      r0, [pc, #0xd4]
	ADD      r1, r5, #0
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x110f4
	LSL      r0, r0, #0x10
	ASR      r0, r0, #0x10
	STRH     r0, [r4, #2]
	LDR      r1, [pc, #0xc8]
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	ADD      r2, r5, #0
	ADD      r1, r6, #0
	BL       |inc_0x049120_0x055620| + 0x18
|loc_080186D2|
	POP      {r4, r5, r6, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	LDR      r0, [r0, #0x10]
	CMP      r0, #0
	BEQ      |loc_08018706|
	LDR      r4, [r0, #8]
	LDRB     r0, [r4]
	ADD      r0, #0xff
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	STRB     r0, [r4]
	BNE      |loc_08018706|
	LDRH     r0, [r4, #2]
	LDR      r1, [pc, #0x98]
	CMP      r0, r1
	BEQ      |loc_08018706|
	MOV      r3, #2
	LDR      r0, [pc, #0x94]
	LDRSH    r1, [r4, r3]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
	MOV      r0, #0
	MVN      r0, r0
	STRH     r0, [r4, #2]
|loc_08018706|
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0x11410
	POP      {r3, r4, r5, pc}
