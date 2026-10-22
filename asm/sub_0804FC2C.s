	CODE16
|sub_0804FC2C|
	LDR      r1, [r0, #0x34]
	LDR      r0, [r0, #0x3c]
	CMP      r1, r0
	BGE      |sub_0804FC38|
	MOV      r0, #1
	BX       lr
