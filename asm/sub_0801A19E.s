	CODE16
|sub_0801A19E|
	PUSH     {lr}
	LDRB     r0, [r0, #0x14]
	LDR      r1, [pc, #0x184]
	SUB      sp, #0x7c
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	LDRB     r0, [r0, #0xc]
	LDR      r1, [pc, #0x178]
	ADD      r2, sp, #0x6c
	STR      r0, [sp, #0x6c]
	MOV      r0, sp
	BL       |inc_0x0158_0x143f2| + 0x3f40
	ADD      sp, #0x7c
	POP      {pc}
	LDR      r1, [pc, #0x160]
	PUSH     {r3, lr}
	LDR      r1, [r1]
	CMP      r1, #0
	BEQ      |sub_0801A1CE|
	MOV      r0, #0
	POP      {r3, pc}
