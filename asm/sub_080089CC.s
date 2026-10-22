	CODE16
|sub_080089CC|
	LDR      r0, [r0, #0x2c]
	LSL      r1, r1, #2
	ADD      r0, r0, r1
	SUB      r0, #0x40
	LDR      r0, [r0, #0x3c]
	BX       lr
