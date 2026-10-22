	CODE16
|loc_08042372|
	PUSH     {r1, r2, r3, r4, r5, r6, r7, lr}
	MOV      r3, sp
	ADD      r2, sp, #4
	ADD      r1, sp, #8
	MOV      r5, #0
	BL       |inc_0x042118_0x049114| + 0x2076
	ADD      r3, sp, #0
	LDR      r6, [pc, #0x2dc]
	LDRB     r0, [r3, #8]
	ADD      r4, r6, #0
	ADD      r4, #0x30
	MOV      r7, #1
	CMP      r0, #0
	BEQ      |loc_080423FE|
	LDRB     r0, [r3, #8]
	STRH     r0, [r6, #0x14]
	LDRB     r0, [r3, #4]
	STRH     r0, [r6, #0x16]
	LDRB     r0, [r6, #9]
	CMP      r0, #0
	BEQ      |sub_080423E8|
	STRB     r7, [r6, #0xa]
	LDRB     r0, [r6, #6]
	LDRB     r1, [r3, #4]
	ORR      r0, r1
	BEQ      |sub_080423D4|
	MOV      r0, #0
|loc_080423AA|
	ADD      r3, sp, #0
	LDRB     r2, [r3, #8]
	ADD      r1, r7, #0
	LSL      r1, r0
	AND      r2, r1
	BEQ      |loc_080423C4|
	LDRB     r2, [r4]
	ORR      r1, r2
	STRB     r1, [r4]
	LDRH     r1, [r6, #0x32]
	LSL      r2, r0, #1
	ADD      r2, r2, r6
	STRH     r1, [r2, #0x34]
|loc_080423C4|
	ADD      r0, #1
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	CMP      r0, #4
	BCC      |loc_080423AA|
	MOV      r1, #1
	MOV      r0, #0x31
	B        |loc_080423F6|
