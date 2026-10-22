	CODE16
|loc_08011F5A|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r7, r1, #0
	ADD      r6, r2, #0
	ADD      r5, r0, #0
	ADD      r4, r3, #0
	CMP      r0, #0
	SUB      sp, #0x6c
	BNE      |sub_08011F7A|
	MOV      r0, #8
	BL       |GBARam_Malloc|
	ADD      r5, r0, #0
	BNE      |sub_08011F7A|
	ADD      r0, r5, #0
	ADD      sp, #0x6c
	POP      {r4, r5, r6, r7, pc}
