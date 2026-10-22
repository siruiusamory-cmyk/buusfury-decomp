	CODE16
|loc_080135A2|
	LDRB     r3, [r0, #0xc]
	LDR      r2, [pc, #0x70]
	CMP      r3, #0
	BNE      |loc_080135AE|
	ADD      r0, r2, #0
	BX       lr
|loc_080135AE|
	ADD      r0, r0, r1
	LDRB     r0, [r0, #0xd]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r2
	BX       lr
