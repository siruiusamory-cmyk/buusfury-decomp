	CODE16
|sub_0802426E|
	PUSH     {r3, lr}
	MOV      r3, #1
	LSL      r3, r3, #0x1a
	LDRH     r1, [r3]
	LSR      r2, r3, #0x12
	BIC      r1, r2
	STRH     r1, [r3]
	CMP      r0, #0
	BEQ      |loc_0802428C|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0802428C|
	POP      {r3, pc}
	PUSH     {r4, r5, lr}
	SUB      sp, #0x34
	ADD      r5, r0, #0
	MOV      r2, #0x38
	MOV      r1, #0x88
	MOV      r0, sp
	MOV      r4, sp
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x4f3e
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0x6594
	LDR      r1, [pc, #0x34]
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	MOV      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x34
	POP      {r4, r5, pc}
	PUSH     {r3, lr}
	CMP      r2, #1
	BNE      |sub_080242D2|
	MOV      r0, #1
	BL       |inc_0x03d784_0x041118| + 0xf2
	MOV      r0, #1
	POP      {r3, pc}
