	CODE16
|sub_080073C0|
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_080073D8|
	MOV      r0, #0x18
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080073D8|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
