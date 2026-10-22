	CODE16
|loc_08009692|
	ADD      r2, r0, #0
	ADD      r2, #0xa0
	ADD      r3, r1, #0
	MOV      r1, #0xff
	ADD      r1, #1
	LDRH     r0, [r2, #2]
	LSL      r1, r3
	BIC      r0, r1
	MOV      r1, #1
	LSL      r1, r1, #0x1a
	STRH     r0, [r2, #2]
	STRH     r0, [r1]
	BX       lr
