	CODE16
|loc_0803CFC2|
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r0, #0
	MOV      r0, #0
	SUB      sp, #0x10
	STR      r0, [sp]
	ADD      r4, r1, #0
	MOV      r1, #1
	ADD      r0, sp, #4
	MOV      r5, sp
	BL       |inc_0x049120_0x055620| + 0x7364
	MOV      r1, #0
	ADD      r0, r5, #0
	ADD      r0, #8
	BL       |inc_0x049120_0x055620| + 0x7364
	MOV      r1, #0
	MVN      r1, r1
	ADD      r0, r5, #0
	ADD      r0, #0xc
	BL       |inc_0x049120_0x055620| + 0x7364
	ADD      r1, r4, #0
	ADD      r0, r6, #0
	BL       |loc_0803CE94|
	ADD      r0, r4, #0
	ADD      r0, #0xff
	ADD      r0, #0xa5
	ADD      r1, r0, #0
	ADD      r1, #0x1c
	LDR      r2, [r1, #0x34]
	LDR      r3, [r0]
	LDRB     r2, [r2, #0x11]
	LSL      r2, r2, #2
	ADD      r2, r2, r5
	LDR      r2, [r2]
	ADD      r2, r3, r2
	STR      r2, [r0]
	LDR      r2, [r1, #0x34]
	LDR      r0, [r1, #0x38]
	LDRB     r2, [r2, #0x11]
	ADD      r0, #0xff
	ADD      r0, #0xa5
	LSL      r2, r2, #2
	ADD      r2, r2, r5
	LDR      r2, [r2]
	LDR      r3, [r0]
	ADD      r2, r3, r2
	STR      r2, [r0]
	LDR      r0, [r1, #0x38]
	LDR      r1, [r1, #0x34]
	ADD      r0, #0xff
	ADD      r0, #0xc1
	LDRB     r1, [r1, #0x11]
	LDR      r0, [r0, #0x38]
	ADD      r0, #0xff
	LSL      r1, r1, #2
	ADD      r1, r1, r5
	ADD      r0, #0xa5
	LDR      r2, [r0]
	LDR      r1, [r1]
	ADD      r1, r2, r1
	STR      r1, [r0]
	ADD      sp, #0x10
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r0, #0
	MOV      r0, #0xf
	SUB      sp, #0x10
	ADD      r4, r1, #0
	MOV      r1, #2
	LSL      r0, r0, #8
	STR      r0, [sp, #4]
	MVN      r1, r1
	ADD      r5, sp, #4
	ADD      r0, r5, #4
	BL       |inc_0x049120_0x055620| + 0x7364
	MOV      r1, #4
	MVN      r1, r1
	ADD      r0, r5, #0
	ADD      r0, #8
	BL       |inc_0x049120_0x055620| + 0x7364
	ADD      r1, r4, #0
	ADD      r0, r6, #0
	BL       |loc_0803CE94|
	ADD      r0, r4, #0
	ADD      r0, #0xff
	ADD      r0, #0xa5
	ADD      r1, r0, #0
	ADD      r1, #0x1c
	LDR      r2, [r1, #0x34]
	LDR      r3, [r0]
	LDRB     r2, [r2, #0x11]
	LSL      r2, r2, #2
	ADD      r2, r2, r5
	LDR      r2, [r2]
	ADD      r2, r3, r2
	STR      r2, [r0]
	LDR      r2, [r1, #0x34]
	LDR      r0, [r1, #0x38]
	LDRB     r2, [r2, #0x11]
	ADD      r0, #0xff
	ADD      r0, #0xa5
	LSL      r2, r2, #2
	ADD      r2, r2, r5
	LDR      r2, [r2]
	LDR      r3, [r0]
	ADD      r2, r3, r2
	STR      r2, [r0]
	LDR      r0, [r1, #0x38]
	LDR      r1, [r1, #0x34]
	ADD      r0, #0xff
	ADD      r0, #0xc1
	LDRB     r1, [r1, #0x11]
	LDR      r0, [r0, #0x38]
	ADD      r0, #0xff
	LSL      r1, r1, #2
	ADD      r1, r1, r5
	ADD      r0, #0xa5
	LDR      r2, [r0]
	LDR      r1, [r1]
	ADD      r1, r2, r1
	STR      r1, [r0]
	ADD      sp, #0x10
	POP      {r4, r5, r6, pc}
	MOV      r2, #0xff
	ADD      r2, #0xf5
	PUSH     {r4, lr}
	LDR      r2, [r2, r1]
	CMP      r2, #0
	BNE      |sub_0803D0D4|
	MOV      r0, #0
	POP      {r4, pc}
