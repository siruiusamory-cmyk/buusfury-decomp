	CODE16
|loc_0803AEA8|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r7, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #0xc
	BNE      |sub_0803AEC6|
	MOV      r0, #0x20
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0803AEC6|
	ADD      r0, r4, #0
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
