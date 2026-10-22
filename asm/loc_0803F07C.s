	CODE16
|loc_0803F07C|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDRB     r0, [r0, #5]
	ADD      r7, r2, #0
	ADD      r6, r1, #0
	CMP      r0, #1
	BNE      |loc_0803F0B0|
	LDRH     r0, [r4, #8]
	CMP      r0, r7
	BLT      |sub_0803F0B2|
	MOV      r5, #0
|loc_0803F092|
	LSL      r0, r5, #1
	ADD      r0, r0, r5
	LSL      r0, r0, #5
	ADD      r0, r0, r4
	ADD      r0, #0x18
	ADD      r2, r7, #0
	ADD      r1, r6, #0
	BL       |loc_0803E152|
	ADD      r5, #1
	CMP      r5, #0xf
	BLT      |loc_0803F092|
	LDRH     r0, [r4, #8]
	SUB      r0, r0, r7
	STRH     r0, [r4, #8]
|loc_0803F0B0|
	POP      {r3, r4, r5, r6, r7, pc}
