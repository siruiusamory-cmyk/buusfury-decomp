	CODE16
|loc_0803CE94|
	PUSH     {r4, r5, r6}
	ADD      r2, r1, #0
	ADD      r2, #0xff
	ADD      r2, #0xa1
	ADD      r0, r2, #0
	ADD      r0, #0x20
	LDR      r3, [r0, #0x34]
	SUB      sp, #0x18
	LDR      r5, [pc, #0x258]
	MOV      r4, #1
	STR      r5, [sp, #0xc]
	LSL      r4, r4, #0xc
	ADD      r3, #0xff
	ADD      r3, #0xa1
	STR      r4, [sp, #8]
	LDMIA    r3!, {r4}
	MOV      r5, #1
	LSL      r5, r5, #0xc
	ADD      r4, r4, r5
	LDR      r5, [pc, #0x244]
	LDR      r3, [r3]
	STR      r4, [sp]
	ADD      r3, r3, r5
	STR      r3, [sp, #4]
	ADD      r3, r4, #0
	LDR      r4, [sp, #4]
	STR      r3, [sp, #0x10]
	STR      r4, [sp, #0x14]
	STMIA    r2!, {r3}
	LDR      r3, [sp, #0x14]
	LDR      r4, [pc, #0x234]
	STR      r3, [r2]
	LDR      r2, [r0, #0x38]
	LDR      r3, [r0, #0x34]
	LDR      r5, [pc, #0x228]
	ADD      r3, #0xff
	ADD      r3, #0xa1
	STR      r4, [sp, #0xc]
	STR      r5, [sp, #8]
	LDMIA    r3!, {r5}
	LDR      r6, [pc, #0x21c]
	LDR      r3, [r3]
	ADD      r5, r5, r6
	ADD      r3, r3, r4
	STR      r3, [sp, #4]
	ADD      r3, r5, #0
	STR      r5, [sp]
	LDR      r5, [sp, #4]
	ADD      r2, #0xff
	ADD      r2, #0xa1
	STR      r3, [sp, #0x10]
	STR      r5, [sp, #0x14]
	STMIA    r2!, {r3}
	LDR      r3, [sp, #0x14]
	MOV      r5, #0xb
	STR      r3, [r2]
	LDR      r2, [r0, #0x38]
	LSL      r5, r5, #0xa
	ADD      r2, #0xff
	ADD      r2, #0xc1
	LDR      r2, [r2, #0x38]
	LDR      r3, [r0, #0x34]
	STR      r5, [sp, #8]
	ADD      r3, #0xff
	ADD      r3, #0xa1
	STR      r4, [sp, #0xc]
	LDMIA    r3!, {r5}
	LDR      r3, [r3]
	MOV      r6, #0xb
	ADD      r3, r3, r4
	STR      r3, [sp, #4]
	LSL      r6, r6, #0xa
	ADD      r5, r5, r6
	LDR      r4, [sp, #4]
	ADD      r2, #0xff
	ADD      r2, #0xa1
	STR      r5, [sp]
	STR      r5, [sp, #0x10]
	STR      r4, [sp, #0x14]
	STMIA    r2!, {r5}
	LDR      r3, [sp, #0x14]
	STR      r3, [r2]
	LDR      r0, [r0, #0x34]
	LDRB     r0, [r0, #8]
	ADD      r0, #0xff
	STRB     r0, [r1, #8]
	ADD      sp, #0x18
	POP      {r4, r5, r6}
	BX       lr
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r0, #0
	MOV      r0, #0xff
	MVN      r0, r0
	SUB      sp, #0x10
	ADD      r4, r1, #0
	ASR      r1, r0, #7
	STR      r0, [sp, #4]
	ADD      r5, sp, #4
	ADD      r0, r5, #4
	BL       |inc_0x049120_0x055620| + 0x7364
	MOV      r1, #0
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
