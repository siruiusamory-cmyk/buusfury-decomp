|sub_08050714|
	EXPORT |sub_08050714|
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0805072C|
	LDR      r0, [pc, #0x28]
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0805072C|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
