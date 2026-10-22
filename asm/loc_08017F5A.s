	CODE16
|loc_08017F5A|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r7, r3, #0
	ADD      r6, r1, #0
	ADD      r5, r2, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #0x24
	BNE      |sub_08017F7A|
	MOV      r0, #0x6c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08017F7A|
	ADD      r0, r4, #0
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
