	CODE16
|sub_08038886|
	PUSH     {r0, r1, r2, r4, r5, r6, r7, lr}
	ADD      r7, r2, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_080388A0|
	MOV      r0, #0x40
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080388A0|
	ADD      r0, r4, #0
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
