	CODE16
|sub_08016080|
	PUSH     {r4, r5}
	LDR      r2, [r0, #4]
	ADD      r2, #0xff
	ADD      r2, #1
	LDR      r2, [r2, #0xc]
	LDR      r3, [r0, #8]
	CMP      r2, r3
	BEQ      |sub_08016096|
	MOV      r0, #0
	POP      {r4, r5}
	BX       lr
