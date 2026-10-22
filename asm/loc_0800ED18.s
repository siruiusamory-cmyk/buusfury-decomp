	CODE16
|loc_0800ED18|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x14]
	ADD      r5, r1, #0
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	STR      r5, [r4, #0x14]
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x9c]
	ADD      r5, r2, #0
	ADD      r0, #0x88
	LDRB     r1, [r0, r1]
	LDR      r0, [r4, #0x58]
	LSL      r1, r1, #2
	ADD      r2, r0, r1
	LDR      r2, [r2, #0x54]
	STR      r2, [r4, #0x50]
	LDR      r0, [r0, #0x50]
	CMP      r0, #0
	BEQ      |loc_0800ED5E|
	LDR      r0, [r0, r1]
	STR      r0, [r4, #0x4c]
|loc_0800ED5E|
	LDR      r0, [r4, #0x14]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [pc, #0x84]
	STR      r0, [r4, #0x14]
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	STRB     r5, [r4, #0x11]
	POP      {r3, r4, r5, pc}
