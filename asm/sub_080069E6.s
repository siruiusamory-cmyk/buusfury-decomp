	CODE16
|sub_080069E6|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #4]
	ADD      r0, #0xff
	ADD      r0, #1
	LDR      r0, [r0, #0xc]
	LDR      r1, [r4, #8]
	CMP      r0, r1
	BNE      |loc_08006AA4|
	LDR      r0, [r4, #0xc]
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	LDR      r1, [r4, #0x1c]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r5, r0, #0
	LDR      r0, [pc, #0xa0]
	LDR      r2, [pc, #0xa0]
	LDR      r0, [r0]
	LDR      r1, [pc, #0xa0]
	LDRH     r0, [r0, #4]
	LDR      r2, [r2, #4]
	LDR      r6, [pc, #0x9c]
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x1f
	ADD      r7, r2, r1
	CMP      r0, #0
	BEQ      |sub_08006A5C|
	LDR      r0, [r4, #0xc]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x10]
	ADD      r2, r2, r1
	LDR      r1, [r4, #0x1c]
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, r5
	BGE      |sub_08006A5C|
	ADD      r1, r6, #0
	MOV      r6, #0
	ADD      r3, r6, #0
	MOV      r2, #0x40
	ADD      r0, r7, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	LDR      r0, [r4, #0xc]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r3, r2, r1
	SUB      r2, r5, #1
	LDR      r1, [r4, #0x1c]
	BL       |inc_0x046118_0x049114| + 0x98e
	LDR      r0, [r4, #4]
	ADD      r0, #0xff
	ADD      r0, #1
	STR      r6, [r0, #0x10]
	MOV      r0, #1
	POP      {r3, r4, r5, r6, r7, pc}
