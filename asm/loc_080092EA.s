	CODE16
|loc_080092EA|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	ADD      r7, r1, #0
	ADD      r5, r2, #0
	MOV      r0, #0
	ADD      r6, r3, #0
	SUB      sp, #4
	STR      r0, [sp]
	MOV      r4, #0
|loc_080092FA|
	LSL      r0, r4, #2
	LDR      r1, [r6, r0]
	CMP      r1, r5
	BLT      |loc_08009318|
	LDR      r1, [sp, #4]
	LDR      r0, [r1, r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x10]
	ADD      r3, r2, r1
	MOV      r2, sp
	ADD      r1, r7, #0
	BL       |inc_0x046118_0x049114| + 0x98e
	CMP      r0, #0
	BNE      |loc_0800931E|
|loc_08009318|
	ADD      r4, #1
	CMP      r4, #4
	BLT      |loc_080092FA|
|loc_0800931E|
	LDR      r0, [sp]
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
