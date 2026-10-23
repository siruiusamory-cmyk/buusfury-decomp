	CODE16
|sub_08038AD8|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r7, r3, #0
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #0x14
	BNE      |sub_08038AF8|
	MOV      r0, #0x64
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08038AF8|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
