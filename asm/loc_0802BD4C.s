	CODE16
|loc_0802BD4C|
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #8
	BNE      |sub_0802BD6A|
	MOV      r0, #0x34
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0802BD6A|
	ADD      r0, r4, #0
	ADD      sp, #8
	POP      {r4, r5, r6, pc}
