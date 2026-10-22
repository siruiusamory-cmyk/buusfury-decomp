	CODE16
|sub_080134F4|
	MOV      r3, #0x1a
	LDRSH    r0, [r0, r3]
	CMP      r0, r1
	BLT      |sub_08013500|
	MOV      r0, #1
	BX       lr
