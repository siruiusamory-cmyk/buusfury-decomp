	CODE16
|sub_080178C2|
	LSR      r4, r0, #0x20
	LSL      r0, r0, #8
	LSL      r0, r0, #0x14
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r7, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #0x34
	BNE      |sub_080178E4|
	MOV      r0, #0x18
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080178E4|
	ADD      r0, r4, #0
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
