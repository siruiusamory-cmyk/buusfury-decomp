	CODE16
|sub_0803DAC8|
	ADD      r2, r7, #0
	ADD      r0, r6, #0
	LDR      r3, [r6, #0x20]
	BL       |inc_0x046118_0x049114| + 0x98e
	SUB      r5, #1
	CMP      r5, #0
	BGT      |loc_0803DAB6|
	POP      {r3, r4, r5, r6, r7, pc}
