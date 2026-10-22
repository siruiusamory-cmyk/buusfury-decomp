	CODE16
|Record_InitFields|
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	STRB     r2, [r1, #0x11]
	BX       lr
	PUSH     {r3, lr}
	LDRH     r2, [r1, #0x12]
	ADD      r2, #1
	LSL      r2, r2, #0x10
|loc_0800DE74|
	LSR      r2, r2, #0x10
	STRH     r2, [r1, #0x12]
	LDRB     r3, [r0, #4]
	LSR      r2, r3
	LDR      r3, [r1, #0x50]
	LDR      r3, [r3]
	CMP      r3, r2
	BGT      |sub_0800DE90|
	LDR      r2, [r0]
	LDR      r3, [r2, #0x24]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
