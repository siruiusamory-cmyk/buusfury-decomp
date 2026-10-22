	CODE16
|sub_08025E4E|
	LSR      r4, r0, #0x20
|loc_08025E50|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #0x34
	BNE      |sub_08025E6E|
	MOV      r0, #0x2c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08025E6E|
	ADD      r0, r4, #0
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
