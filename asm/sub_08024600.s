	CODE16
|sub_08024600|
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [pc, #0xac]
	ADD      r4, r1, #0
	LDR      r0, [r5]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x24]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |sub_08024626|
	MOV      r2, #0x10
	ADD      r0, r4, #0
	LDR      r1, [r5, #4]
	BL       |inc_0x049120_0x055620| + 0x24
	MOV      r0, #0x10
	POP      {r3, r4, r5, pc}
