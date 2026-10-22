	CODE16
|loc_080121D8|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	ADD      r7, r3, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #0x74
	BNE      |sub_080121F6|
	LDR      r0, [pc, #0x1dc]
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080121F6|
	ADD      r0, r4, #0
	ADD      sp, #0x84
	POP      {r4, r5, r6, r7, pc}
