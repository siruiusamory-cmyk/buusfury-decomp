	CODE16
|loc_08009728|
	MOV      r3, #0x29
	LSL      r3, r3, #4
	MUL      r1, r3
	ASR      r1, r1, #0xc
	ADD      r0, #0xa0
	MUL      r2, r3
	ASR      r2, r2, #0xc
	STRB     r1, [r0, #1]
	STRB     r2, [r0]
	LDR      r2, [pc, #0x1c4]
	STRB     r1, [r2, #2]
	LDRB     r0, [r0]
	STRB     r0, [r2, #3]
	BX       lr
