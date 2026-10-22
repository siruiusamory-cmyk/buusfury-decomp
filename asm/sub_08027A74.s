	CODE16
|sub_08027A74|
	PUSH     {r4, r5, r6, r7}
	LDR      r2, [pc, #0xc4]
	LDR      r5, [r2, #4]
	LDR      r2, [pc, #0xcc]
	LDR      r4, [r2]
	CMP      r4, #0
	BNE      |sub_08027A88|
	MOV      r0, #0
	POP      {r4, r5, r6, r7}
	BX       lr
