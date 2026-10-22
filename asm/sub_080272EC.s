	CODE16
|sub_080272EC|
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_08027306|
	MOV      r0, #0xff
	ADD      r0, #0x99
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08027306|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
