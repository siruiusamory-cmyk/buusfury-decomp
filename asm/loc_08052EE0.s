	CODE16
|loc_08052EE0|
	LDR      r2, [r0]
	LDR      r3, [r1]
	LDRB     r0, [r2, #8]
	LDRB     r1, [r3, #8]
	CMP      r0, r1
	BNE      |sub_08052EFC|
	LDR      r0, [r2, #4]
	LDR      r1, [r3, #4]
	CMP      r0, r1
	BGE      |sub_08052EF8|
	MOV      r0, #1
	BX       lr
