	CODE16
|sub_080192AE|
	LSR      r0, r6, #1
	LDR      r2, [r0, #4]
	STR      r2, [r1]
	MOV      r1, #0
	STR      r1, [r0, #4]
	BX       lr
