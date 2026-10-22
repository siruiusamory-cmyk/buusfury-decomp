	CODE16
|sub_0803DE88|
	STR      r1, [r3]
	STR      r1, [r3, #4]
	MOV      r1, #0
	STR      r1, [r3, #0xc]
	MOV      r6, #0
	MOV      r7, #0
	STR      r1, [r3, #8]
	LDR      r1, [r3, #4]
	LDRH     r4, [r1]
	CMP      r4, #0
	BNE      |sub_0803DEA6|
	MOV      r4, #1
	STR      r4, [r3, #0xc]
	POP      {r4, r5, r6, r7}
	BX       lr
