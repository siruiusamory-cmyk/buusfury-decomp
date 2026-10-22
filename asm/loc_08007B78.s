	CODE16
|loc_08007B78|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r6, r1, #0
	ADD      r5, r2, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_08007B92|
	LDR      r0, [pc, #0x2dc]
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08007B92|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
