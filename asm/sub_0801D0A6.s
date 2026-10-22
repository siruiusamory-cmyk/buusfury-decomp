	CODE16
|sub_0801D0A6|
	LSL      r0, r0, #0xc
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r2, #0
	ADD      r6, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0801D0C4|
	MOV      r0, #0xff
	ADD      r0, #0x35
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0801D0C4|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
