	CODE16
|loc_0801064C|
	PUSH     {r4, r5, r6, lr}
	LDR      r1, [r0]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r4, r0, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r5, r0, #0
	MOV      r0, #1
	LSL      r0, r0, #9
	ADD      r6, r4, r0
	LDR      r0, [r6, #0x2c]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDRB     r0, [r5, #0x14]
	LDR      r1, [pc, #0x170]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	BL       |inc_0x153f2_0x1a3f2| + 0x1d58
	STR      r0, [r6, #0x2c]
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r4, r5, r6, pc}
