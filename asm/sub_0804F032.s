	CODE16
|sub_0804F032|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0804F046|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
