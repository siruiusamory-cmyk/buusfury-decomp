	CODE16
|sub_0802C630|
	LDRB     r1, [r0, #0x15]
	ADD      r2, r1, #0
	ADD      r2, #0xff
	STRB     r2, [r0, #0x15]
	CMP      r1, #0
	BNE      |sub_0802C640|
	MOV      r0, #1
	BX       lr
