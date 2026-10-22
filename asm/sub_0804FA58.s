	CODE16
|sub_0804FA58|
	ADD      r1, r0, #0
	LDR      r1, [r1, #4]
	MOV      r0, #1
	CMP      r1, #0
	BNE      |loc_0804FA64|
	MOV      r0, #0
|loc_0804FA64|
	BX       lr
	LSL      r0, r0, #0
	LDR      r0, [r0, #8]
	CMP      r0, #0
	BEQ      |sub_0804FA78|
	LDRB     r0, [r0, #0x10]
	CMP      r0, #0
	BNE      |sub_0804FA78|
	MOV      r0, #1
	BX       lr
