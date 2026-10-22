	CODE16
|sub_0803F1B6|
	LSL      r0, r0, #0
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	MOV      r5, #0
	STR      r5, [r0, #4]
	STR      r5, [r4, #8]
	STR      r5, [r4]
	MOV      r2, #1
	LSL      r2, r2, #0xb
	MOV      r1, #0
	LSL      r0, r2, #0xe
	BL       |inc_0x049120_0x055620| + 0xc
	LDR      r0, [pc, #0x1c4]
	ADD      r0, r4, r0
	ADD      r6, r0, #0
	BL       |loc_0803E3E4|
	ADD      r4, #0xc
	ADD      r0, r4, #0
	BL       |sub_0803F0E6|
	LDR      r0, [pc, #0x1b8]
	MOV      r1, #0x80
	STRH     r1, [r0, #4]
	LDR      r1, [pc, #0x1b4]
	STRH     r1, [r0, #2]
	LSL      r1, r0, #0x12
	STR      r1, [r0, #0x3c]
	LDR      r1, [pc, #0x1b0]
	ADD      r2, r1, #0
	ADD      r2, #0x20
	STR      r1, [r2]
	MOV      r3, #4
	ADD      r1, r2, #0
	STRH     r3, [r1, #4]
	LDR      r1, [pc, #0x1a8]
	STRH     r1, [r2, #6]
	LDR      r1, [pc, #0x1a8]
	STR      r1, [r2, #8]
	LDR      r1, [pc, #0x1a8]
	ADD      r2, r1, #0
	ADD      r2, #0x1c
	STR      r1, [r2, #0xc]
	ADD      r1, r2, #0
	STRH     r3, [r1, #0x10]
	LDR      r1, [pc, #0x1a0]
	STRH     r1, [r2, #0x12]
	STRH     r5, [r0]
	LDR      r0, [pc, #0x19c]
	LDR      r1, [pc, #0x1a0]
	LDR      r0, [r0]
	LDR      r2, [pc, #0x1a0]
	STR      r1, [r0, #0x28]
	LDRH     r0, [r2]
	LSR      r1, r2, #0x10
	ORR      r0, r1
	STRH     r0, [r2]
	ADD      r1, r2, #0
	SUB      r1, #0xff
	LDR      r0, [pc, #0x194]
	SUB      r1, #1
	STRH     r0, [r1]
	MOV      r0, #0x80
	STRH     r0, [r1, #2]
	MOV      r1, #4
	ADD      r0, r4, #0
	BL       |loc_0803F18C|
	MOV      r1, #8
	ADD      r0, r6, #0
	BL       |loc_0803E42A|
	POP      {r4, r5, r6, pc}
