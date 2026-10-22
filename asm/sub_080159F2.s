	CODE16
|sub_080159F2|
	LSL      r0, r0, #0
	LDR      r1, [r0, #8]
	SUB      r1, #1
	STR      r1, [r0, #8]
	BNE      |sub_08015A00|
	MOV      r0, #1
	BX       lr
