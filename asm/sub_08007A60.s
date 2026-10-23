	CODE16
|sub_08007A60|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r6, r2, #0
	ADD      r5, r0, #0
	ADD      r4, r1, #0
	CMP      r0, #0
	BNE      |sub_08007A7A|
	LDR      r0, [pc, #0xfc]
	BL       |GBARam_Malloc|
	ADD      r5, r0, #0
	BNE      |sub_08007A7A|
	ADD      r0, r5, #0
	POP      {r3, r4, r5, r6, r7, pc}
