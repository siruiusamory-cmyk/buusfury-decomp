	CODE16
|sub_0800E7F6|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r2, #0
	ADD      r6, r1, #0
	ADD      r5, r3, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0800E814|
	MOV      r0, #0x89
	LSL      r0, r0, #2
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0800E814|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
