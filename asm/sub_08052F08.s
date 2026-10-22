	CODE16
|sub_08052F08|
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r5, [r1]
	LDR      r6, [r2]
	MOV      ip, r5
	MUL      r5, r6
	MOV      lr, r6
	LDR      r6, [r1, #4]
	SUB      sp, #0x10
	STR      r6, [sp, #0xc]
	LDR      r3, [r2, #4]
	MOV      r7, lr
	STR      r3, [sp, #8]
	MUL      r6, r3
	LDR      r3, [r1, #8]
	SUB      r5, r5, r6
	LDR      r4, [r2, #8]
	ADD      r6, r3, #0
	MUL      r6, r4
	LDR      r1, [r1, #0xc]
	LDR      r2, [r2, #0xc]
	SUB      r5, r5, r6
	ADD      r6, r1, #0
	MUL      r6, r2
	SUB      r5, r5, r6
	MOV      r6, #1
	LSL      r6, r6, #0xe
	ADD      r5, r5, r6
	ASR      r5, r5, #0xf
	STR      r5, [sp]
	LDR      r6, [sp, #8]
	MOV      r5, ip
	MUL      r5, r6
	LDR      r6, [sp, #0xc]
	MUL      r6, r7
	ADD      r5, r5, r6
	ADD      r6, r3, #0
	MUL      r6, r2
	ADD      r5, r5, r6
	ADD      r6, r1, #0
	MUL      r6, r4
	SUB      r5, r5, r6
	MOV      r6, #1
	LSL      r6, r6, #0xe
	ADD      r5, r5, r6
	ASR      r5, r5, #0xf
	STR      r5, [sp, #4]
	MOV      r6, lr
	ADD      r7, r3, #0
	MOV      r5, ip
	MUL      r7, r6
	MUL      r5, r4
	ADD      r5, r5, r7
	LDR      r6, [sp, #8]
	ADD      r7, r1, #0
	MUL      r7, r6
	ADD      r5, r5, r7
	LDR      r6, [sp, #0xc]
	MOV      r7, lr
	MUL      r6, r2
	SUB      r5, r5, r6
	MOV      r6, #1
	LSL      r6, r6, #0xe
	ADD      r5, r5, r6
	MOV      r6, ip
	MUL      r6, r2
	MUL      r1, r7
	ADD      r1, r6, r1
	LDR      r6, [sp, #0xc]
	LDR      r2, [sp]
	MUL      r6, r4
	ADD      r1, r1, r6
	LDR      r6, [sp, #8]
	STR      r2, [r0]
	MUL      r3, r6
	SUB      r1, r1, r3
	MOV      r6, #1
	LSL      r6, r6, #0xe
	ADD      r1, r1, r6
	ASR      r1, r1, #0xf
	LDR      r3, [sp, #4]
	STR      r1, [r0, #0xc]
	ASR      r5, r5, #0xf
	ADD      r0, #4
	STMIA    r0!, {r3, r5}
	ADD      sp, #0x10
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4}
	LDR      r3, [r1]
	LDR      r1, [r1, #4]
	LDR      r4, [r2]
	LDR      r2, [r2, #4]
	ADD      r3, r3, r4
	ADD      r1, r1, r2
	SUB      sp, #8
	STR      r1, [sp, #4]
	LDR      r2, [sp, #4]
	STR      r3, [sp]
	STR      r2, [r0, #4]
	STR      r3, [r0]
	ADD      sp, #8
	POP      {r4}
	BX       lr
	PUSH     {r4, r5, r6}
	LDR      r3, [r1]
	LDR      r4, [r2]
	SUB      sp, #0x18
	ADD      r3, r3, r4
	LDR      r4, [r1, #4]
	LDR      r5, [r2, #4]
	STR      r3, [sp]
	ADD      r4, r4, r5
	STR      r4, [sp, #4]
	ADD      r1, #8
	LDR      r5, [r1]
	LDR      r6, [r2]
	LDR      r1, [r1, #4]
	LDR      r2, [r2, #4]
	ADD      r5, r5, r6
	ADD      r1, r1, r2
	STR      r1, [sp, #4]
	LDR      r2, [sp, #4]
	STR      r4, [sp, #0xc]
	ADD      r4, sp, #8
	STR      r5, [sp]
	STR      r5, [sp, #0x10]
	STR      r3, [sp, #8]
	STR      r2, [sp, #0x14]
	LDMIA    r4!, {r1, r2, r3, r4}
	STMIA    r0!, {r1, r2, r3, r4}
	ADD      sp, #0x18
	POP      {r4, r5, r6}
	BX       lr
	BX       pc
	LSL      r0, r0, #0
