	CODE16
|sub_0802CAFA|
	STRH     r2, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	STRB     r2, [r1, #0x11]
	BX       lr
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDRH     r0, [r1, #0x12]
	ADD      r5, r1, #0
	ADD      r0, #1
	LSL      r1, r0, #0x10
	LSR      r1, r1, #0x10
	STRH     r1, [r5, #0x12]
	LDR      r0, [r4, #8]
	ADD      r6, r0, #0
	BL       |inc_0x046118_0x049114| + 0xd40
	LDR      r1, [r4, #0x14]
	CMP      r1, r0
	BGT      |sub_0802CB4E|
	LDR      r0, [r4, #0xc]
	CMP      r0, #0
	BEQ      |loc_0802CB42|
	SUB      r0, #1
	STR      r0, [r4, #0xc]
	BNE      |loc_0802CB42|
	LDR      r0, [r4, #4]
	CMP      r0, #0
	BEQ      |loc_0802CB3A|
	ADD      r1, r0, #0
	MOV      r0, #1
	STR      r0, [r1, #0x14]
|loc_0802CB3A|
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xed20
	POP      {r4, r5, r6, pc}
|loc_0802CB42|
	LDR      r0, [r4, #0x10]
	MUL      r0, r6
	STRH     r0, [r5, #0x12]
	LDR      r0, [r4, #0x10]
	STRB     r0, [r5, #0x11]
	POP      {r4, r5, r6, pc}
