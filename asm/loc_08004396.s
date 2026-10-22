	CODE16
|loc_08004396|
	ASR      r2, r1, #3
	ADD      r0, r2, r0
	LSL      r3, r1, #0x1d
	ADD      r0, #0x50
	LDRB     r2, [r0, #5]
	LSR      r3, r3, #0x1d
	MOV      r1, #1
	LSL      r1, r3
	BIC      r2, r1
	STRB     r2, [r0, #5]
	BX       lr
	ASR      r2, r1, #3
	ADD      r0, r2, r0
	LSL      r3, r1, #0x1d
	ADD      r0, #0x50
	LDRB     r2, [r0, #5]
	LSR      r3, r3, #0x1d
	MOV      r1, #1
	LSL      r1, r3
	EOR      r2, r1
	STRB     r2, [r0, #5]
	BX       lr
