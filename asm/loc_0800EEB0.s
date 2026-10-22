	CODE16
|loc_0800EEB0|
	LDR      r3, [pc, #0x334]
	LDR      r2, [r0, #0x58]
	ADD      r3, #0x80
	LDRB     r1, [r3, r1]
	LSL      r1, r1, #2
	ADD      r1, r2, r1
	LDR      r1, [r1, #0x54]
	LDR      r0, [r0, #0x50]
	CMP      r1, r0
	BNE      |sub_0800EEC8|
	MOV      r0, #1
	BX       lr
