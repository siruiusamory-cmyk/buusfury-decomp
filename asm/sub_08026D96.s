	CODE16
|sub_08026D96|
	CMP      r1, #8
	BNE      |sub_08026DA4|
	LDRH     r1, [r0, #0xc]
	CMP      r1, r2
	BEQ      |loc_08026D94|
	MOV      r0, #0
	BX       lr
