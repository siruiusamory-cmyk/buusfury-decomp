	CODE16
|sub_0803E2D6|
	PUSH     {r4}
	MOV      r4, #1
	LSL      r4, r4, #0xe
	STR      r1, [r0, #0x28]
	STR      r4, [r0, #0x30]
	STRB     r2, [r0, #0x12]
	STRB     r3, [r0, #0x13]
	MOV      r1, #0x1f
	STRB     r1, [r0, #0x10]
	POP      {r4}
	BX       lr
	MOV      r1, #0
|loc_0803E2EE|
	LSL      r2, r1, #6
	ADD      r2, r2, r0
	LDRB     r3, [r2, #0x10]
	ADD      r1, #1
	LSR      r3, r3, #1
	LSL      r3, r3, #1
	STRB     r3, [r2, #0x10]
	CMP      r1, #0x10
	BLT      |loc_0803E2EE|
	BX       lr
	PUSH     {r4}
	MOV      r2, #0xf
	LSL      r3, r2, #6
	ADD      r3, r3, r0
	LDRB     r4, [r3, #0x10]
	LSL      r4, r4, #0x1f
	BEQ      |sub_0803E326|
	LDR      r3, [r3, #0x28]
	CMP      r3, r1
	BNE      |sub_0803E326|
	LSL      r1, r2, #6
	ADD      r0, r1, r0
	LDRB     r1, [r0, #0x10]
	LSR      r1, r1, #1
	LSL      r1, r1, #1
	STRB     r1, [r0, #0x10]
	POP      {r4}
	BX       lr
