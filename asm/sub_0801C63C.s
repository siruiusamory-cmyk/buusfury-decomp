	CODE16
|sub_0801C63C|
	BX       lr
|sub_0801C63E|
	PUSH     {r4, r5, lr}
	LDRH     r0, [r1, #0x12]
	SUB      sp, #0x14
	ADD      r4, r1, #0
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	CMP      r0, #0x20
	BLS      |sub_0801C664|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      sp, #0x14
	POP      {r4, r5, pc}
