	CODE16
|sub_080134E2|
	LSL      r2, r2, #0x1f
	BEQ      |sub_080134F4|
	LDRH     r0, [r0, #0x1e]
	CMP      r0, r1
	BLT      |sub_080134F0|
	MOV      r0, #1
	BX       lr
