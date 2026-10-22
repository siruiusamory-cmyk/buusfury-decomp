	CODE16
|loc_08004098|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r2, #0
	ADD      r6, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_080040B2|
	MOV      r0, #0x6c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080040B2|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
