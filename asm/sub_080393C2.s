	CODE16
|sub_080393C2|
	LSL      r0, r0, #0
	STMIA    r1!, {r4, r6}
	LSR      r4, r0, #0x20
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	ADD      r6, sp, #0x200
	LSR      r7, r6, #1
	LSR      r0, r4, #0x1d
	LSL      r0, r0, #0xc
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_080393EC|
	MOV      r0, #8
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080393EC|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
