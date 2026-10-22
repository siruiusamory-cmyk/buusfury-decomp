	CODE16
|sub_08023D6E|
	MOV      r0, #0
	MOV      r1, #1
	SUB      r0, r1, r0
	STRB     r0, [r5, #0x10]
	ADD      r0, r5, #0
	ADD      r0, #0xff
	ADD      r0, #1
	LDR      r1, [r0, #0x78]
	LDR      r0, [r0, #0x7c]
	STR      r0, [r4, #0x24]
	STR      r6, [r4, #0x28]
	STR      r1, [r4, #0x20]
	STR      r6, [r4, #0x2c]
	STR      r6, [r4, #0x30]
	LDR      r0, [r4, #0x38]
	LSL      r0, r0, #2
	STR      r0, [r4, #0x34]
	LDR      r1, [r4, #0xc]
	SUB      r0, r1, r0
	STR      r0, [r4, #0xc]
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x30]
	ADD      r3, r2, r1
	MOV      r2, #0
	MOV      r1, #0xe
	BL       |inc_0x046118_0x049114| + 0x98e
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x3c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	MOV      r0, #0x24
	STRB     r0, [r5, #8]
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
|loc_08023DBA|
	PUSH     {r4}
	LDR      r2, [r0, #0x34]
	SUB      sp, #0x10
	SUB      r2, #8
	STR      r2, [r0, #0x34]
	LDR      r3, [r0, #0x28]
	LDR      r4, [r0, #0x30]
	ADD      r3, r3, r4
	STR      r3, [r0, #0x28]
	LDR      r3, [r0, #0x2c]
	ADD      r2, r3, r2
	STR      r2, [r0, #0x2c]
	LDR      r2, [r0, #0xc]
	ADD      r2, #8
	STR      r2, [r0, #0xc]
	LDR      r3, [r0, #0x10]
	LDR      r4, [r0, #8]
	ADD      r3, r3, r4
	STR      r3, [r0, #0x10]
	LDR      r3, [r0, #0x14]
	ADD      r2, r3, r2
	STR      r2, [r0, #0x14]
	ADD      r2, r1, #0
	ADD      r2, #0xff
	LDR      r4, [r0, #0x10]
	ADD      r2, #0xa1
	STMIA    r2!, {r4}
	LDR      r3, [r0, #0x14]
	STR      r3, [r2]
	ADD      r3, r2, #0
	LDR      r2, [r0, #0x28]
	LDR      r1, [r0, #0x2c]
	ASR      r2, r2, #8
	ASR      r1, r1, #8
	STR      r1, [sp, #4]
	ADD      r1, r2, #0
	STR      r2, [sp]
	LDR      r2, [sp, #4]
	STR      r1, [sp, #8]
	STR      r2, [sp, #0xc]
	LDR      r1, [r0, #0x20]
	LDR      r2, [sp, #8]
	LDR      r0, [r0, #0x24]
	ADD      r1, r1, r2
	LDR      r2, [sp, #0xc]
	SUB      r3, #0x2c
	ADD      r0, r0, r2
	STR      r0, [sp, #4]
	ADD      r0, r1, #0
	STR      r1, [sp]
	LDR      r1, [sp, #4]
	STMIA    r3!, {r0, r1}
	ADD      sp, #0x10
	POP      {r4}
	BX       lr
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	LDR      r0, [r0, #0x3c]
	LDR      r4, [r1, #4]
	ADD      r0, #1
	STR      r0, [r5, #0x3c]
	CMP      r0, #8
	BLT      |loc_08023E54|
	CMP      r0, #8
	BNE      |sub_08023E56|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x30]
	ADD      r3, r2, r1
	MOV      r2, #1
	MOV      r1, #0xe
	BL       |inc_0x046118_0x049114| + 0x98e
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |loc_08023DBA|
|loc_08023E54|
	POP      {r3, r4, r5, pc}
