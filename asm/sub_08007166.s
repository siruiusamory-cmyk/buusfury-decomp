	CODE16
|sub_08007166|
	LSR      r7, r0, #0x20
	LDR      r1, [pc, #0x50]
	LDR      r1, [r1]
	LDRH     r1, [r1, #2]
	LDRB     r0, [r0, #4]
	AND      r1, r0
	BEQ      |sub_08007178|
	MOV      r0, #1
	BX       lr
