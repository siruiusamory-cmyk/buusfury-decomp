	CODE16
|sub_0801C552|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	ADD      r0, r1, #0
	LDR      r1, [r4, #8]
	CMP      r1, #0
	BNE      |loc_0801C598|
	LDR      r1, [r0]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRB     r1, [r0, #0x14]
	LDR      r2, [pc, #0x150]
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	LDRB     r1, [r1]
	LSL      r2, r1, #0x1f
	LSR      r2, r2, #0x1f
	MOV      r1, #0
	CMP      r2, #0
	BEQ      |loc_0801C58E|
	ADD      r0, #0x20
|loc_0801C584|
	STRH     r1, [r0]
	LDRH     r2, [r0]
	CMP      r2, r1
	BNE      |loc_0801C584|
	B        |loc_0801C598|
|loc_0801C58E|
	ADD      r0, #0x1e
|loc_0801C590|
	STRH     r1, [r0]
	LDRH     r2, [r0]
	CMP      r2, r1
	BNE      |loc_0801C590|
|loc_0801C598|
	LDR      r0, [r4, #0xc]
	LDR      r4, [pc, #0x104]
	CMP      r0, #0
	BEQ      |loc_0801C5A8|
	ADD      r1, r0, #0
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
|loc_0801C5A8|
	MOV      r1, #0x51
	LDR      r2, [pc, #0xf8]
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	LDR      r2, [pc, #0xf4]
	LDR      r0, [r4]
	ADD      r0, r0, r2
	BL       |inc_0x03d784_0x041118| + 0xb7e
	POP      {r4, pc}
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r1, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r5, r0, #0
	LDRB     r0, [r0, #0x14]
	LDR      r6, [pc, #0xd8]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r6
	BL       |inc_0x153f2_0x1a3f2| + 0x1d3a
	MOV      r0, #0xe
	STRB     r0, [r5, #0x14]
	ADD      r0, r6, #0
	ADD      r0, #0xff
	ADD      r0, #0x51
	BL       |inc_0x153f2_0x1a3f2| + 0x1d2a
	LDRB     r0, [r5, #0x14]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r6
	BL       |inc_0x153f2_0x1a3f2| + 0x1d4a
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeca0
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x104f4
	POP      {r4, r5, r6, pc}
	AREA     CPilotTail, CODE, READONLY
	CODE16
