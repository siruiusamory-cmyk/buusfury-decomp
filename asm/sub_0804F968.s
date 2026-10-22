	CODE16
|sub_0804F968|
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	LDR      r1, [r1, #0x2c]
	MOV      r0, #1
	CMP      r1, #0
	BNE      |loc_0804F978|
	MOV      r0, #0
|loc_0804F978|
	BX       lr
	LSL      r0, r0, #0
	ADD      r0, #0xff
	ADD      r0, #0x21
	LDRB     r0, [r0, #0xf]
	BX       lr
	LDR      r1, [pc, #0x14]
	LDR      r1, [r1]
	CMP      r1, #1
	BNE      |sub_0804F998|
	ADD      r0, #0xff
	ADD      r0, #1
	LDR      r0, [r0, #0x2c]
	CMP      r0, #1
	BNE      |sub_0804F998|
	BX       lr
