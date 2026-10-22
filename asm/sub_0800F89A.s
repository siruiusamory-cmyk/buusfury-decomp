	CODE16
|sub_0800F89A|
	MOV      r0, #0
	STR      r0, [sp, #8]
	STR      r0, [sp, #0xc]
	LDR      r0, [pc, #0x60]
	LDR      r0, [r0]
	STR      r0, [sp, #4]
	MOV      r0, #1
	LSL      r0, r0, #9
	ADD      r0, r4, r0
	LDR      r1, [r0, #0x24]
	LDR      r1, [r1, #0x18]
	STR      r1, [sp]
	LDR      r5, [r0, #0x28]
	MOV      r0, #0x24
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0800F8DA|
	LDR      r1, [sp, #0x24]
	ADD      r3, sp, #8
	STR      r1, [r0, #4]
	LDR      r1, [pc, #0x58]
	STR      r1, [r0]
	STR      r6, [r0, #8]
	STR      r7, [r0, #0xc]
	LDMIA    r3!, {r2, r3}
	STR      r2, [r0, #0x10]
	STR      r3, [r0, #0x14]
	STR      r4, [r0, #0x20]
	LDR      r1, [sp]
	STR      r1, [r0, #0x18]
	STR      r5, [r0, #0x1c]
|loc_0800F8DA|
	ADD      r2, r0, #0
	LDR      r0, [sp, #4]
	MOV      r1, #0x61
	LSL      r1, r1, #4
	ADD      r0, r0, r1
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	ADD      r0, r4, #0
	BL       |loc_0800F80C|
	ADD      sp, #0x2c
	POP      {r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
	ASR      r0, r2, #0x20
	LSL      r0, r0, #0xc
	ASR      r0, r3, #0x20
	LSL      r0, r0, #0xc
	MOV      r6, #0xac
	LSR      r7, r0, #0x20
	SUB      r4, r5, r6
	LSL      r0, r0, #0xc
	SUB      r4, r1, r4
	LSL      r0, r0, #0xc
	STMIA    r4!, {r2, r7}
	LSR      r4, r0, #0x20
	SUB      r0, r6, r6
	LSL      r0, r0, #0xc
	ADD      r0, sp, #0x80
	LSR      r4, r0, #0x20
	MOV      r6, #0x8c
	LSR      r7, r0, #0x20
	STR      r5, [sp, #0x170]
	LSR      r4, r0, #0x20
|loc_0800F924|
	MOV      r1, #0x29
	LSL      r1, r1, #4
	ADD      r1, r0, r1
	PUSH     {r4, lr}
	LDRB     r2, [r1, #1]
	SUB      sp, #0x10
	CMP      r2, #0
	BNE      |loc_0800F950|
	MOV      r2, #1
	STRB     r2, [r1, #1]
	LDR      r1, [pc, #0x3a4]
	LDR      r4, [r1, #8]
	ADD      r1, r0, #0
	MOV      r0, sp
	BL       |Object_WriteBounds1|
	ADD      r4, #0x80
	LDR      r1, [r4, #0x30]
	MOV      r2, #1
	MOV      r0, sp
	BL       |loc_08009930|
|loc_0800F950|
	ADD      sp, #0x10
	POP      {r4, pc}
|loc_0800F954|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	MOV      r0, #0x29
	LSL      r0, r0, #4
	ADD      r6, r4, r0
	LDRB     r0, [r6, #1]
	SUB      sp, #0x14
	CMP      r0, #0
	BEQ      |sub_0800F99E|
	LDR      r0, [pc, #0x378]
	ADD      r1, r4, #0
	LDR      r5, [r0, #8]
	ADD      r0, sp, #4
	BL       |Object_WriteBounds1|
	ADD      r7, r5, #0
	ADD      r7, #0x80
	LDR      r1, [r7, #0x30]
	ADD      r0, sp, #4
	BL       |loc_08009324|
	MOV      r1, #1
	SUB      r5, r1, r0
	MOV      r0, #0
	STRB     r0, [r6, #1]
	ADD      r0, sp, #4
	ADD      r1, r4, #0
	BL       |Object_WriteBounds1|
	MOV      r2, #0
	ADD      r0, sp, #4
	LDR      r1, [r7, #0x30]
	BL       |loc_08009930|
	ADD      r0, r5, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
