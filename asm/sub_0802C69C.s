|sub_0802C69C|
	EXPORT |sub_0802C69C|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	BNE      |sub_0802C6B0|
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0802C6B0|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
