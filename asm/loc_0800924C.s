	CODE16
|loc_0800924C|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r6, r0, #0
	ADD      r7, r1, #0
	MOV      r4, #0
|loc_08009254|
	LSL      r5, r4, #2
	LDR      r0, [r6, r5]
	CMP      r0, #0
	BEQ      |loc_08009268|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08009268|
	ADD      r0, r5, r7
	LDR      r1, [r0, #0x14]
	ADD      r0, r4, #0
	LDR      r2, [r1]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, #1
	CMP      r4, #4
	STR      r0, [r6, r5]
	BLT      |loc_08009254|
	POP      {r3, r4, r5, r6, r7, pc}
