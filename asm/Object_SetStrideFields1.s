	CODE16
|Object_SetStrideFields1|
	PUSH     {r4, r5}
	MOV      r4, #0x10
	MOV      r2, #0
	LSL      r3, r1, #0x18
	LSR      r3, r3, #0x18
|loc_0803E434|
	LSL      r1, r2, #6
	ADD      r1, r1, r0
	MOV      r5, #0x34
	STRB     r3, [r5, r1]
	LDRB     r5, [r1, #0x10]
	ADD      r2, #1
	ORR      r5, r4
	STRB     r5, [r1, #0x10]
	CMP      r2, #0x10
	BLT      |loc_0803E434|
	POP      {r4, r5}
	BX       lr
	AREA UnusedGBARam6, CODE, READONLY
	CODE16
