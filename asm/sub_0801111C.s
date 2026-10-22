	CODE16
|sub_0801111C|
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r1, #0
	ADD      r5, r2, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #8
	BNE      |sub_0801113C|
	MOV      r0, #0xff
	ADD      r0, #0xbd
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0801113C|
	ADD      r0, r4, #0
	ADD      sp, #8
	POP      {r4, r5, r6, pc}
