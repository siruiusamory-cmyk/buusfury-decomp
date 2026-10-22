	CODE16
|sub_08004380|
	ASR      r2, r1, #3
	ADD      r0, r2, r0
	LSL      r3, r1, #0x1d
	ADD      r0, #0x50
	LDRB     r2, [r0, #5]
	LSR      r3, r3, #0x1d
	MOV      r1, #1
	LSL      r1, r3
	ORR      r1, r2
	STRB     r1, [r0, #5]
	BX       lr
