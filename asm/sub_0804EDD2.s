	CODE16
|sub_0804EDD2|
	LSL      r0, r0, #0
	LSR      r0, r2, #0x1e
	LSL      r0, r0, #0xc
	MOV      r2, #0xa3
	LSL      r2, r2, #2
	ADD      r1, r1, r2
	LDR      r0, [r0, #0x10]
	LDR      r1, [r1]
	LSL      r0, r0, #0xa
	CMP      r1, r0
	BGE      |sub_0804EDEC|
	MOV      r0, #1
	BX       lr
