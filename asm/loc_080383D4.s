	CODE16
|loc_080383D4|
		PUSH {r3, r4, r5, r6, r7, lr}
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_080383EE|
	MOV      r0, #0x4c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080383EE|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
