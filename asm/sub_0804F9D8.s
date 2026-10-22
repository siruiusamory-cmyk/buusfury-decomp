	CODE16
|sub_0804F9D8|
	ADD      r1, r0, #0
	LDR      r1, [r1, #4]
	MOV      r0, #1
	CMP      r1, #0
	BNE      |loc_0804F9E4|
	MOV      r0, #0
|loc_0804F9E4|
	BX       lr
	LSL      r0, r0, #0
	ADD      r1, r0, #0
	LDR      r1, [r1, #8]
	MOV      r0, #1
	CMP      r1, #0
	BNE      |loc_0804F9F4|
	MOV      r0, #0
|loc_0804F9F4|
	BX       lr
	LSL      r0, r0, #0
	ADD      r1, r0, #0
	LDR      r1, [r1, #4]
	MOV      r0, #1
	CMP      r1, #0
	BEQ      |loc_0804FA04|
	MOV      r0, #0
|loc_0804FA04|
	BX       lr
	LSL      r0, r0, #0
	LDR      r0, [r0, #8]
	CMP      r0, #0
	BEQ      |sub_0804FA18|
	LDRB     r0, [r0, #0x10]
	CMP      r0, #0
	BNE      |sub_0804FA18|
	MOV      r0, #1
	BX       lr
