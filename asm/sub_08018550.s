	CODE16
|sub_08018550|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r3, #0
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0801856C|
	MOV      r0, #0x24
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0801856C|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
