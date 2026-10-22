	CODE16
|loc_0803362A|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	LDR      r2, [r0, #0x44]
	LDR      r0, [r0, #0x38]
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [pc, #0x210]
	LDR      r0, [r0, #0xc]
	STR      r0, [r4, #0x20]
	MOV      r0, #0x78
	STR      r0, [r4, #0x18]
	MOV      r0, #0x10
	STR      r0, [r4, #0x1c]
	MOV      r0, #8
	STRB     r0, [r4, #0x15]
	ADD      r4, #0x14
	CMP      r5, #0
	BEQ      |loc_0803365A|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x356
|loc_0803365A|
	LDR      r1, [pc, #0x1f4]
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x30
	POP      {r3, r4, r5, pc}
