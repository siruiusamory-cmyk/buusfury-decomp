	CODE16
|sub_080286D4|
	EXPORT |sub_080286D4|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #4
	BNE      |sub_080286F2|
	MOV      r0, #0x50
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080286F2|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
