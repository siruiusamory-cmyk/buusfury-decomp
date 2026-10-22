	CODE16
|sub_0802821A|
	PUSH     {r3, lr}
	LDR      r1, [r0, #0x30]
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x14]
	ADD      r6, r1, #0
	CMP      r0, #0
	SUB      sp, #0x14
	BNE      |sub_08028236|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
