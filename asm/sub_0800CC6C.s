	CODE16
|sub_0800CC6C|
	PUSH     {r4, r5, r6, r7}
	LDR      r4, [r1, #8]
	CMP      r4, #0x10
	BLT      |sub_0800CC7A|
	MOV      r0, #0
	POP      {r4, r5, r6, r7}
	BX       lr
