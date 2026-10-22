	CODE16
|loc_0803F540|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #0x14
	BNE      |sub_0803F55E|
	MOV      r0, #0x34
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0803F55E|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
