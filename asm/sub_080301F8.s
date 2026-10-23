|sub_080301F8|
	EXPORT |sub_080301F8|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_08030210|
	MOV      r0, #0x24
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08030210|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
