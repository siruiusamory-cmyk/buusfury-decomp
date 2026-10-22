	CODE16
|sub_08011998|
	ADD      r1, #1
	CMP      r3, r1
	BGT      |loc_0801198A|
	ADD      r1, r0, #0
	ADD      r0, r5, #0
	BL       |inc_0x049120_0x055620| + 0x6d34
	LDR      r0, [r5]
	LSL      r0, r0, #2
	ADD      r0, r0, r5
	STR      r7, [r0, #4]
|loc_080119AE|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #4]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, r4, r5, r6, r7, pc}
