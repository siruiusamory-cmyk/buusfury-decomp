	CODE16
|sub_0803893E|
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r3, [pc, #0x120]
	LDR      r4, [r0, #0x10]
	LDR      r3, [r3, #4]
	LDR      r2, [r1]
	ADD      r3, #0x28
	LDR      r5, [r3]
	SUB      sp, #8
	SUB      r4, r4, r5
	LDR      r5, [r0, #0x14]
	LDR      r3, [r3, #4]
	STR      r4, [sp]
	SUB      r3, r5, r3
	STR      r3, [sp, #4]
	ADD      r5, r3, #0
	LDR      r3, [r0, #0x30]
	MOV      lr, r4
	LDR      r6, [r3, #4]
	MOV      r3, #0
	STR      r6, [r2]
	LDR      r7, [r0, #0x30]
	LDRSB    r7, [r7, r3]
	ADD      r3, r4, r7
	LDR      r7, [pc, #0x110]
	LSL      r3, r3, #0x17
	LSR      r3, r3, #7
	AND      r6, r7
	ORR      r3, r6
	STR      r3, [r2]
	LDR      r6, [r0, #0x30]
	LSR      r3, r3, #8
	LDRB     r6, [r6, #1]
	LSL      r3, r3, #8
	MOV      r7, #3
	ADD      r6, r5, r6
	LSL      r6, r6, #0x18
	LSR      r6, r6, #0x18
	ORR      r3, r6
	STR      r3, [r2]
	LDRH     r3, [r0, #0xc]
	LDR      r6, [r2, #4]
	LSL      r7, r7, #0xa
	ADD      r3, #0x20
	LSL      r3, r3, #0x16
	LSR      r6, r6, #0xa
	LSL      r6, r6, #0xa
	LSR      r3, r3, #0x16
	ORR      r6, r3
	STR      r6, [r2, #4]
	LDRB     r3, [r0, #8]
	BIC      r6, r7
	LSL      r3, r3, #0x1a
	LSR      r3, r3, #0x1e
	LSL      r3, r3, #0xa
	ORR      r3, r6
	STR      r3, [r2, #4]
	LDR      r6, [r0, #0x2c]
	ADD      r2, #8
	ADD      r6, #0x30
	LDR      r3, [r6, #4]
	MOV      ip, r3
	STR      r3, [r2]
	MOV      r3, #0
	LDRSB    r7, [r6, r3]
	MOV      r3, ip
	ADD      lr, r7
	LDR      r7, [pc, #0xbc]
	AND      r3, r7
	MOV      r7, lr
	LSL      r7, r7, #0x17
	LSR      r7, r7, #7
	ORR      r3, r7
	STR      r3, [r2]
	LDRB     r6, [r6, #1]
	LSR      r3, r3, #8
	LSL      r3, r3, #8
	ADD      r6, r5, r6
	LSL      r6, r6, #0x18
	LSR      r6, r6, #0x18
	ORR      r3, r6
	STR      r3, [r2]
	LDRH     r3, [r0, #0xc]
	LDR      r6, [r2, #4]
	MOV      r7, #3
	ADD      r3, #0x20
	LSL      r3, r3, #0x16
	LSR      r6, r6, #0xa
	LSL      r6, r6, #0xa
	LSR      r3, r3, #0x16
	ORR      r3, r6
	STR      r3, [r2, #4]
	LDRB     r6, [r0, #8]
	LSL      r7, r7, #0xa
	BIC      r3, r7
	LSL      r6, r6, #0x1a
	LSR      r6, r6, #0x1e
	LSL      r6, r6, #0xa
	ORR      r3, r6
	STR      r3, [r2, #4]
	LDR      r3, [r0, #0x28]
	ADD      r2, #8
	CMP      r3, #0
	BNE      |loc_08038A5C|
	LDR      r6, [pc, #0x5c]
	LDR      r3, [r6, #4]
	MOV      ip, r3
	STR      r3, [r2]
	MOV      r3, #0
	LDRSB    r7, [r6, r3]
	MOV      r3, ip
	ADD      r4, r4, r7
	LDR      r7, [pc, #0x60]
	LSL      r4, r4, #0x17
	LSR      r4, r4, #7
	AND      r3, r7
	ORR      r3, r4
	STR      r3, [r2]
	LDRB     r4, [r6, #1]
	LSR      r3, r3, #8
	LSL      r3, r3, #8
	ADD      r4, r5, r4
	LSL      r4, r4, #0x18
	LSR      r4, r4, #0x18
	ORR      r3, r4
	STR      r3, [r2]
	LDRH     r3, [r0, #0xc]
	LDR      r4, [r2, #4]
	LSR      r4, r4, #0xa
	LSL      r3, r3, #0x16
	LSR      r3, r3, #0x16
	LSL      r4, r4, #0xa
	ORR      r3, r4
	STR      r3, [r2, #4]
	LDRB     r0, [r0, #8]
	MOV      r4, #3
	LSL      r4, r4, #0xa
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x1e
	LSL      r0, r0, #0xa
	BIC      r3, r4
	ORR      r0, r3
	STR      r0, [r2, #4]
	ADD      r2, #8
|loc_08038A5C|
	STR      r2, [r1]
	ADD      sp, #8
	MOV      r0, #0
	POP      {r4, r5, r6, r7, pc}
|loc_08038A64|
	DCW      0xe0dc
	DCW      0x0876,0x0000,0x0601,0x0cf4,0x0877,0x8110,0x086b,0x9680
	DCW      0x0804,0xdd6c,0x0804,0x0d0c,0x0877,0xffff
|sub_08038A82|
|unk_08038A82|
	INCBIN  baserom.gba_0x38a82_0x38a84.extracted
		PUSH {r4, r5, r6, lr}
	ADD      r4, r0, #0
	CMP      r1, #0xb
	BEQ      |loc_08038A9C|
	CMP      r1, #0xc
	BNE      |sub_08038ACC|
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |loc_080387DC|
	MOV      r0, #0
	POP      {r4, r5, r6, pc}
|loc_08038A9C|
	LDR      r0, [r4, #0x2c]
	LDR      r5, [pc, #0x30]
	STR      r0, [r4, #0x30]
	LDRH     r0, [r4, #0xc]
	LDR      r1, [pc, #0x2c]
	MOV      r6, #1
	LSL      r0, r0, #5
	ADD      r0, r0, r5
	LSL      r6, r6, #0xa
	ADD      r2, r6, #0
	LDR      r1, [r1, #8]
	BL       |inc_0x049120_0x055620| + 0x18
	LDRH     r0, [r4, #0xc]
	LDR      r1, [r4, #0x2c]
	LSL      r0, r0, #5
	ADD      r0, r0, r5
	ADD      r0, r0, r6
	LSR      r2, r6, #1
	LDR      r1, [r1, #8]
	BL       |inc_0x049120_0x055620| + 0x18
	MOV      r0, #0
	POP      {r4, r5, r6, pc}
