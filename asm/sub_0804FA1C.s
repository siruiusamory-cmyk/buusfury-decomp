	CODE16
|sub_0804FA1C|
	LDR      r0, [r0, #8]
	CMP      r0, #0
	BEQ      |sub_0804FA2C|
	LDRB     r0, [r0, #0x10]
	CMP      r0, #0
	BNE      |sub_0804FA2C|
	MOV      r0, #1
	BX       lr
