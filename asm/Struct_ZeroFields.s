	CODE16
|Struct_ZeroFields|
	MOV      r1, #0
	STRB     r1, [r0]
	STRH     r1, [r0, #2]
	STRH     r1, [r0, #4]
	STRH     r1, [r0, #6]
	BX       lr
	PUSH     {r4, r5}
	LDRH     r3, [r0, #4]
	CMP      r3, #0
	BNE      |sub_080402F0|
	MOV      r0, #0
	POP      {r4, r5}
	BX       lr
