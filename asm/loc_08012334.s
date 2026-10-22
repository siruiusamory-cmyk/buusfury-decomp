	CODE16
|loc_08012334|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r3, #0
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_08012350|
	LDR      r0, [pc, #0x80]
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08012350|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
