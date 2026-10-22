	CODE16
|sub_0804EE22|
	LSR      r5, r6, #1
	LDR      r0, [pc, #8]
	MOV      r1, #1
	LDR      r0, [r0]
	SUB      r0, r1, r0
	BX       lr
	LSL      r0, r0, #0
	ADD      r0, #0x2c
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #4]
	LDR      r0, [r0]
	BX       lr
	LSL      r0, r0, #0
	ADD      r0, #0x2c
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #0x14]
	LDR      r0, [r0]
	LDR      r1, [r0, #0x58]
	ADD      r1, #0x54
	LDR      r1, [r1, #0x54]
	LDR      r0, [r0, #0x50]
	CMP      r1, r0
	BNE      |sub_0804EE54|
	MOV      r0, #1
	BX       lr
