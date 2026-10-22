	CODE16
|loc_08005460|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	ADD      r7, r3, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #4
	BNE      |sub_0800547E|
	MOV      r0, #0x5f
	LSL      r0, r0, #3
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0800547E|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
