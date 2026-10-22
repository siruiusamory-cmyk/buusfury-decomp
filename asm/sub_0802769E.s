	CODE16
|sub_0802769E|
	LSR      r4, r6, #1
	CMP      r7, #0xdc
	LSR      r1, r6, #1
	STRH     r0, [r2, #4]
	LSR      r3, r5, #1
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r3, #0
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_080276C4|
	MOV      r0, #0x4c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080276C4|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
