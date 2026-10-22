	CODE16
|loc_080096C4|
	LSL      r3, r1, #2
	ADD      r3, r3, r0
	ADD      r3, #0x80
	STR      r2, [r3, #0x34]
	ADD      r0, #0x80
	LDR      r0, [r0, #0xc]
	LDR      r3, [pc, #0x224]
	LDR      r0, [r0, #0x3c]
	ADD      r3, #0x14
	LSL      r0, r0, #3
	ADD      r0, r0, r3
	LSL      r1, r1, #1
	LDRH     r0, [r0, r1]
	ADD      r0, r0, r2
	MOV      r2, #1
	LSL      r2, r2, #0x1a
	ADD      r1, r1, r2
	STRH     r0, [r1, #8]
	BX       lr
