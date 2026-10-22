	CODE16
|sub_08006168|
	MOV      r1, #2
	STRB     r1, [r0, #3]
	LDR      r1, [pc, #0x118]
	LDR      r1, [r1, #4]
	STR      r1, [r0, #0xc]
	LDR      r3, [r2, #0x20]
	LDR      r4, [r2, #0x24]
	STR      r3, [r0, #4]
	STR      r4, [r0, #8]
	LDR      r1, [r2, #0x1c]
|loc_0800617C|
	BL       |inc_0x03d784_0x041118| + 0x356
	POP      {r4, pc}
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x100]
	PUSH     {r3, lr}
	LDR      r0, [r0]
	MOV      r2, #9
	LDRH     r0, [r0, #4]
	AND      r0, r2
	BEQ      |sub_080061AE|
	MOV      r2, #0xff
	LDR      r0, [r1, #4]
	ADD      r2, #0xd
	LDR      r2, [r2, r0]
	LDR      r3, [r1, #8]
	CMP      r2, r3
	BNE      |sub_080061AE|
	LDR      r2, [r0]
	LDR      r3, [r2, #0x20]
	ADD      r3, r3, r2
	LDR      r2, [r1, #0x28]
	BL       |inc_0x046118_0x049114| + 0x98e
	POP      {r3, pc}
