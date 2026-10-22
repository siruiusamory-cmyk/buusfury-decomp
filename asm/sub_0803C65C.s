	CODE16
|sub_0803C65C|
	LDR      r1, [r1, #4]
	LDRH     r1, [r1, #0x12]
	CMP      r1, #0x18
	BCC      |sub_0803C66E|
	LDR      r0, [r0, #0x10]
	CMP      r0, #0
	BNE      |sub_0803C66E|
	MOV      r0, #1
	BX       lr
