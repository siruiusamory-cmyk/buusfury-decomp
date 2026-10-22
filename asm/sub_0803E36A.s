	CODE16
|sub_0803E36A|
	LSR      r3, r0, #0x20
	LSR      r0, r5, #1
	LSL      r0, r0, #0xc
	ASR      r3, r4, #1
	LSL      r0, r0, #0
	LSL      r7, r7, #0x1f
	LSL      r0, r0, #0
	PUSH     {r4, r5}
	MOV      r4, #0
	LSL      r5, r4, #6
	ADD      r5, r5, r0
	LDRB     r5, [r5, #0x10]
	LSL      r5, r5, #0x1f
	BNE      |sub_0803E39E|
	LSL      r4, r4, #6
	ADD      r0, r4, r0
	MOV      r4, #1
	LSL      r4, r4, #0xe
	STR      r1, [r0, #0x28]
	STR      r4, [r0, #0x30]
	STRB     r2, [r0, #0x12]
	STRB     r3, [r0, #0x13]
	MOV      r1, #0x1f
	STRB     r1, [r0, #0x10]
	POP      {r4, r5}
	BX       lr
