	CODE16
|sub_0803BE04|
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDRH     r0, [r1, #0x12]
	ADD      r4, r1, #0
	SUB      sp, #0x18
	CMP      r0, #0
	BEQ      |sub_0803BE34|
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r4, #0x12]
	CMP      r0, #0x20
	BCC      |loc_0803BE30|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #0x24
	STRB     r0, [r4, #8]
|loc_0803BE30|
	ADD      sp, #0x18
	POP      {r4, r5, r6, pc}
