	CODE16
|sub_08023EF8|
	PUSH     {r3, lr}
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	ADD      r0, r1, #0
	MOV      r1, #0x38
	STRB     r1, [r0, #8]
	STRB     r2, [r0, #0x11]
	MOV      r1, #0x12
	BL       |inc_0x0158_0x143f2| + 0xeb82
	POP      {r3, pc}
	PUSH     {lr}
	LDRH     r0, [r1, #0x12]
	SUB      sp, #0x1c
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	CMP      r0, #0x80
	BCC      |sub_08023F32|
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      sp, #0x1c
	POP      {pc}
