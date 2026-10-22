	CODE16
|sub_0802CDE4|
	ADD      r0, #0xa4
	LSL      r0, r0, #0xc
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDRB     r0, [r1, #0x11]
	ADD      r6, r1, #0
	SUB      sp, #0x44
	CMP      r0, #1
	BEQ      |loc_0802CDFA|
	CMP      r0, #4
	BNE      |sub_0802CE00|
|loc_0802CDFA|
	MOV      r0, #0
	ADD      sp, #0x44
	POP      {r4, r5, r6, r7, pc}
