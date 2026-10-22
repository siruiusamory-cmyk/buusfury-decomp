	CODE16
|loc_0801952C|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r7, r2, #0
	ADD      r6, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #0xc
	BNE      |sub_0801954A|
	MOV      r0, #0x44
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0801954A|
	ADD      r0, r4, #0
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
