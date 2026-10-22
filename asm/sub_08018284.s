	CODE16
|sub_08018284|
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x28]
	SUB      sp, #0x10
	ADD      r0, #1
	STR      r0, [r4, #0x28]
	LSL      r0, r0, #0x18
	ADD      r5, r1, #0
	LSR      r1, r0, #0x1b
	CMP      r1, #3
	BLE      |loc_0801829C|
	MOV      r1, #0
|loc_0801829C|
	LDR      r0, [r4, #0x64]
	CMP      r0, r1
	BEQ      |loc_080182BC|
	STR      r1, [r4, #0x64]
	LDRH     r0, [r4, #0xc]
	LDR      r2, [pc, #0xe0]
	LDR      r3, [r4, #0x60]
	LSL      r0, r0, #5
	ADD      r0, r0, r2
	LDR      r2, [r3, #0x10]
	ADD      r6, r2, #0
	MUL      r6, r1
	ADD      r1, r3, r6
	ADD      r1, #0x18
	BL       |inc_0x049120_0x055620| + 0x18
|loc_080182BC|
	LDR      r0, [pc, #0xcc]
	LDR      r1, [r4, #0x38]
	LDR      r0, [r0, #0xc]
	LDR      r3, [pc, #0xcc]
	ADD      r0, #0x28
	LDR      r2, [r0]
	SUB      r1, r1, r2
	LDR      r2, [r4, #0x3c]
	LDR      r0, [r0, #4]
	STR      r1, [sp]
	SUB      r0, r2, r0
	STR      r0, [sp, #4]
	ADD      r0, r1, #0
	LDR      r1, [sp, #4]
	STR      r0, [sp, #8]
	STR      r1, [sp, #0xc]
	LDR      r0, [r5]
	ADD      r1, r0, #0
	ADD      r1, #8
	STR      r1, [r5]
	LDR      r1, [r4, #0x60]
	LDR      r1, [r1, #0x14]
	LDR      r2, [sp, #8]
	AND      r1, r3
	LSL      r2, r2, #0x17
	LSR      r2, r2, #7
	ORR      r2, r1
	LDR      r1, [sp, #0xc]
	LSR      r2, r2, #8
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x18
	LSL      r2, r2, #8
	ORR      r1, r2
	STR      r1, [r0]
	LDRB     r1, [r4, #8]
	LDR      r2, [r0, #4]
	MOV      r3, #3
	LSL      r1, r1, #0x1a
	LSR      r1, r1, #0x1e
	LSL      r3, r3, #0xa
	BIC      r2, r3
	LSL      r1, r1, #0xa
	ORR      r1, r2
	STR      r1, [r0, #4]
	LDRH     r2, [r4, #0xc]
	LSR      r1, r1, #0xa
	LSL      r1, r1, #0xa
	LSL      r2, r2, #0x16
	LSR      r2, r2, #0x16
	ORR      r1, r2
	STR      r1, [r0, #4]
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |loc_08018614|
	ADD      sp, #0x10
	POP      {r4, r5, r6, pc}
	PUSH     {r3, lr}
	CMP      r1, #0xb
	BNE      |sub_08018340|
	MOV      r3, #0
	MVN      r3, r3
	STR      r3, [r0, #0x64]
	BL       |loc_0801870E|
	POP      {r3, pc}
