	CODE16
|loc_080109AA|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r1, #0
	ADD      r6, r3, #0
	ADD      r5, r2, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_080109C8|
	MOV      r0, #9
	LSL      r0, r0, #6
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080109C8|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
