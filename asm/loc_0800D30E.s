	CODE16
|loc_0800D30E|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r7, r2, #0
	ADD      r6, r3, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #0x34
	BNE      |sub_0800D32E|
	MOV      r0, #0x80
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0800D32E|
	ADD      r0, r4, #0
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
