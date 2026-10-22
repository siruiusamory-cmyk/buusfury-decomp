	CODE16
|sub_0804FA44|
	LDR      r0, [r0, #8]
	CMP      r0, #0
	BEQ      |sub_0804FA54|
	LDRB     r0, [r0, #0x10]
	CMP      r0, #0
	BNE      |sub_0804FA54|
	MOV      r0, #1
	BX       lr
