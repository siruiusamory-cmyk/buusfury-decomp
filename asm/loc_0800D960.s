	CODE16
|loc_0800D960|
	PUSH     {r0, r1, r2, r4, r5, r6, r7, lr}
	ADD      r6, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #8
	BNE      |sub_0800D97C|
	MOV      r0, #0x30
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0800D97C|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
