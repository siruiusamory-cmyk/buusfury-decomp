	CODE16
|sub_08007856|
	LSR      r7, r0, #0x20
	PUSH     {r0, r1, r2, r4, r5, r6, r7, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #0x28
	BNE      |sub_08007874|
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08007874|
	ADD      r0, r4, #0
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
