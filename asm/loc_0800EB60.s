	CODE16
|loc_0800EB60|
	PUSH     {r0, r1, r2, r4, r5, r6, r7, lr}
	ADD      r6, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0800EB7C|
	MOV      r0, #0xff
	ADD      r0, #0x8d
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0800EB7C|
	ADD      r0, r4, #0
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
