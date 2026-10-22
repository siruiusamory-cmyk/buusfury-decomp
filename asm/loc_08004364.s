	CODE16
|loc_08004364|
	ASR      r2, r1, #3
	ADD      r0, r2, r0
	LSL      r2, r1, #0x1d
	ADD      r0, #0x50
	LDRB     r0, [r0, #5]
	LSR      r2, r2, #0x1d
	MOV      r1, #1
	LSL      r1, r2
	AND      r0, r1
	BEQ      |sub_0800437C|
	MOV      r0, #1
	BX       lr
