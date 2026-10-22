	CODE16
|sub_0804EE5A|
	LSL      r0, r0, #0xc
	ADD      r1, #0xff
	ADD      r1, #0xc1
	LDR      r1, [r1, #0x24]
	LDR      r0, [r0, #0xc]
	CMP      r1, r0
	BNE      |sub_0804EE6C|
	MOV      r0, #1
	BX       lr
