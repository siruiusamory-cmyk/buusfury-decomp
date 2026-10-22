	CODE16
|sub_0802C644|
	LDR      r2, [r0, #4]
	CMP      r2, #0
	BNE      |loc_0802C64E|
	MOV      r0, #1
	BX       lr
|loc_0802C64E|
	LDRB     r2, [r0, #0x14]
	CMP      r2, #0
	BEQ      |sub_0802C668|
	CMP      r2, #1
	BNE      |loc_0802C66E|
	LDRB     r1, [r0, #0x15]
	ADD      r2, r1, #0
	ADD      r2, #0xff
	STRB     r2, [r0, #0x15]
	CMP      r1, #0
	BNE      |loc_0802C66A|
	MOV      r0, #1
	BX       lr
