	CODE16
|sub_080279E0|
	EXPORT |sub_080279E0|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_080279F8|
	MOV      r0, #0x20
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080279F8|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
