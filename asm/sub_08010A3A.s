	CODE16
|sub_08010A3A|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r7, r2, #0
	ADD      r6, r1, #0
	ADD      r5, r0, #0
	ADD      r4, r3, #0
	CMP      r0, #0
	SUB      sp, #0x24
	BNE      |sub_08010A5C|
	MOV      r0, #0x55
	LSL      r0, r0, #3
	BL       |GBARam_Malloc|
	ADD      r5, r0, #0
	BNE      |sub_08010A5C|
	ADD      r0, r5, #0
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
