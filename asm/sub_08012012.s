	CODE16
|sub_08012012|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r7, r3, #0
	ADD      r6, r2, #0
	ADD      r5, r0, #0
	ADD      r4, r1, #0
	CMP      r0, #0
	SUB      sp, #0x1c
	BNE      |sub_08012032|
	MOV      r0, #8
	BL       |GBARam_Malloc|
	ADD      r5, r0, #0
	BNE      |sub_08012032|
	ADD      r0, r5, #0
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
