	CODE16
|sub_08033D2C|
	SUB      r3, r3, r5
	ASR      r3, r3, #5
	ADD      r5, r6, r3
	SUB      r5, #1
	MOV      r3, #1
	STR      r3, [r1, #0xc]
	LDR      r1, [r2]
	CMP      r1, r5
	BGT      |sub_08033D4C|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x24]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, r4, r5, r6, r7, pc}
