	CODE16
|sub_0800F58C|
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |loc_0800F5A8|
	MOV      r0, #0xff
	ADD      r0, #0x95
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_0800F5A8|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_0800F5A8|
	ADD      r2, r6, #0
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |loc_0800EB60|
	ADD      r0, r4, #0
	ADD      r0, #0xff
	ADD      r0, #0x8d
	MOV      r1, #0
	STR      r1, [r0]
	LDR      r1, [pc, #0x64]
	STR      r1, [r4]
	STR      r4, [r0, #4]
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r1, #0xc
	BNE      |loc_0800F5EE|
	LDR      r0, [r4, #0x14]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [r4, #0x18]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0800F5EE|
	ADD      r0, r4, #0
	ADD      r0, #0xff
	ADD      r1, r5, #0
	ADD      r0, #0x8d
	BL       |inc_0x153f2_0x1a3f2| + 0x3fbc
	CMP      r0, #0
	BEQ      |loc_0800F602|
	SUB      r0, #1
	POP      {r4, r5, r6, pc}
|loc_0800F602|
	ADD      r2, r6, #0
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |loc_0800F40E|
	POP      {r4, r5, r6, pc}
	LDR      r2, [pc, #0x18]
	PUSH     {r3, lr}
	LDR      r2, [r2]
	CMP      r0, r2
	BNE      |sub_0800F61E|
	BL       |loc_0801155C|
	POP      {r3, pc}
