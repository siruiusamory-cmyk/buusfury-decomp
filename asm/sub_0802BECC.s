	CODE16
|sub_0802BECC|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	ADD      r7, r3, #0
	ADD      r6, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #0x44
	BNE      |sub_0802BEEA|
	MOV      r0, #0x1c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0802BEEA|
	ADD      r0, r4, #0
	ADD      sp, #0x54
	POP      {r4, r5, r6, r7, pc}
