	CODE16
|sub_0800AD82|
	LSR      r3, r0, #0x20
	LSL      r7, r7, #0xf
	LSL      r0, r0, #0
|loc_0800AD88|
	LSL      r5, r4, #0
	LSL      r4, r4, #1
	LSL      r0, r0, #0
	LSL      r0, r0, #0
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	STR      r6, [sp, #0x200]
	LSR      r4, r0, #0x20
	LDMIA    r1!, {r2}
	LSR      r4, r0, #0x20
	STR      r0, [r0]
	AND      r0, r0
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	ADD      r4, #0x60
	LDRH     r1, [r4, #0x18]
	SUB      sp, #0x14
	LDR      r2, [pc, #0x2ec]
	MOV      r7, #0
	MOV      r6, #0x40
	LSL      r1, r1, #5
	ADD      r1, r1, r2
	ADD      r0, #0x80
	ADD      r5, r0, #0
	ADD      r2, sp, #4
	STR      r6, [sp, #0xc]
	STR      r6, [sp, #0x10]
	STR      r7, [sp, #4]
	STR      r7, [sp, #8]
	BL       |inc_0x049120_0x055620| + 0x3c
	LDRH     r0, [r4, #0x1a]
	LDR      r1, [pc, #0x2cc]
	STR      r6, [sp, #4]
	LSL      r0, r0, #5
	ADD      r1, r0, r1
	MOV      r0, #0x80
	STR      r0, [sp, #0xc]
	ADD      r0, r5, #0
	STR      r7, [sp, #8]
	STR      r6, [sp, #0x10]
	ADD      r2, sp, #4
	BL       |inc_0x049120_0x055620| + 0x3c
	LDRH     r0, [r4, #0x1c]
	LDR      r1, [pc, #0x2b4]
	STR      r7, [sp, #8]
	LSL      r0, r0, #5
	ADD      r1, r0, r1
	MOV      r0, #0x80
	STR      r0, [sp, #4]
	MOV      r0, #0xa0
	STR      r0, [sp, #0xc]
	ADD      r0, r5, #0
	STR      r6, [sp, #0x10]
	ADD      r2, sp, #4
	BL       |inc_0x049120_0x055620| + 0x3c
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4}
	LDR      r3, [r1]
	LDRH     r4, [r3]
	CMP      r4, #0xa
	BNE      |loc_0800AE10|
	ADD      r3, #2
	STR      r3, [r1]
	B        |loc_0800AE1C|
|loc_0800AE10|
	LDR      r4, [r0, #0x10]
	CMP      r3, r4
	BEQ      |loc_0800AE1C|
	MOV      r0, #0
|loc_0800AE18|
	POP      {r4}
	BX       lr
|loc_0800AE1C|
	LDR      r3, [r1]
	LDRH     r3, [r3]
	CMP      r3, #8
	BNE      |loc_0800AE3E|
	ADD      r3, r0, #0
	ADD      r3, #0x80
|loc_0800AE28|
	CMP      r2, #0
	BEQ      |loc_0800AE32|
	LDR      r0, [r1]
	LDRH     r0, [r0, #2]
	STRB     r0, [r3, #3]
|loc_0800AE32|
	LDR      r0, [r1]
	ADD      r0, #4
	STR      r0, [r1]
	LDRH     r0, [r0]
	CMP      r0, #8
	BEQ      |loc_0800AE28|
|loc_0800AE3E|
	LDR      r0, [r1]
	LDRH     r2, [r0]
	CMP      r2, #0x2d
	BNE      |sub_0800AE60|
	ADD      r0, #2
	STR      r0, [r1]
	LDRH     r0, [r0]
	CMP      r0, #0x20
	BNE      |loc_0800AE5C|
|loc_0800AE50|
	LDR      r0, [r1]
	ADD      r0, #2
	STR      r0, [r1]
	LDRH     r0, [r0]
	CMP      r0, #0x20
	BEQ      |loc_0800AE50|
|loc_0800AE5C|
	MOV      r0, #1
	B        |loc_0800AE18|
