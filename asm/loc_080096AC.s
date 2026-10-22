	CODE16
|loc_080096AC|
	ADD      r0, #0xa0
	MOV      r3, #0xff
	ADD      r3, #1
	LDRH     r2, [r0, #2]
	LSL      r3, r1
	ORR      r2, r3
	ADD      r1, r2, #0
	STRH     r1, [r0, #2]
	MOV      r0, #1
	LSL      r0, r0, #0x1a
	STRH     r1, [r0]
	BX       lr
