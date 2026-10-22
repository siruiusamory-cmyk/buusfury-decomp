	CODE16
|sub_08033D82|
	LSL      r0, r0, #0xc
	PUSH     {r3, lr}
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	ADD      r0, r1, #0
	MOV      r1, #0x38
	STRB     r1, [r0, #8]
	STRB     r2, [r0, #0x11]
	MOV      r1, #0x13
	BL       |inc_0x0158_0x143f2| + 0xeb82
	POP      {r3, pc}
	PUSH     {r4, r5, r6, r7, lr}
	LDRH     r0, [r1, #0x12]
	SUB      sp, #0x3c
	ADD      r4, r1, #0
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	CMP      r0, #0x20
	BCC      |sub_08033DC0|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
