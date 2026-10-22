	CODE16
|loc_08004838|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	CMP      r0, #0
	LDR      r5, [pc, #0x2a4]
	BNE      |sub_08004850|
	ADD      r0, r5, #0
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08004850|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
