	CODE16
|sub_08039122|
	LSR      r3, r5, #1
	ADD      r5, sp, #0x340
	LSR      r7, r6, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	BVS      |sub_080391EC|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r1, #0
	ADD      r6, r2, #0
	ADD      r5, r3, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_08039152|
	MOV      r0, #0x9f
	LSL      r0, r0, #2
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08039152|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
