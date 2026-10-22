	CODE16
|sub_0800773E|
	LDRB     r0, [r0, #4]
	LDRB     r1, [r1, #0x10]
	CMP      r0, r1
	BNE      |sub_0800774A|
	MOV      r0, #1
	BX       lr
