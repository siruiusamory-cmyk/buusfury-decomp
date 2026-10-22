	CODE16
|sub_08038CC2|
	LDRB     r2, [r5]
	CMP      r2, #1
	BNE      |loc_08038CEC|
	LDR      r1, [r4, #0x44]
	ADD      r1, #1
	STR      r1, [r4, #0x44]
	CMP      r1, #0x18
	BLT      |sub_08038CDC|
	ADD      r0, r4, #0
	BL       |loc_08038BDC|
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
