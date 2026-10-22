	CODE16
|sub_08019594|
	LDR      r1, [r0, #4]
	SUB      r1, #1
	STR      r1, [r0, #4]
	BNE      |sub_080195A0|
	MOV      r0, #1
	BX       lr
