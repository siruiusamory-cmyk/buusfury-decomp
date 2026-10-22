	CODE16
|loc_08017C1C|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #0x14
	ADD      r6, sp, #0x38
	ADD      r7, r3, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	LDMIA    r6!, {r5, r6}
	BNE      |sub_08017C3E|
	MOV      r0, #0xff
	ADD      r0, #0xd5
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08017C3E|
	ADD      r0, r4, #0
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
