	CODE16
|loc_080135BC|
	LDR      r2, [pc, #0x50]
	LSL      r1, r1, #2
	ADD      r1, r1, r2
	SUB      r1, #0xff
	SUB      r1, #1
	LDR      r1, [r1, #0x38]
|loc_080135C8|
	STR      r1, [r0, #0x24]
	LDR      r2, [r0, #0x24]
	CMP      r2, r1
	BNE      |loc_080135C8|
	BX       lr
