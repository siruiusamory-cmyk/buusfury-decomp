	CODE16
|sub_0802C782|
	LSR      r4, r0, #0x20
	LDR      r4, [r5, #0x6c]
	LSR      r3, r7, #1
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	STRH     r0, [r3, #4]
	LSR      r3, r5, #1
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r3, #0
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0802C7AC|
	MOV      r0, #0x4c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0802C7AC|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
