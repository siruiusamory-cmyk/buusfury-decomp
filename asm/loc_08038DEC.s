	CODE16
|loc_08038DEC|
	PUSH     {r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x48]
	SUB      sp, #0x14
	CMP      r0, #0
	BEQ      |loc_08038DFC|
	BL       |loc_08038DEC|
|loc_08038DFC|
	ADD      r0, r4, #0
	ADD      r0, #0x28
	ADD      r1, r0, #0
	LDR      r2, [r4, #0x28]
	LDR      r3, [r4, #0x30]
	ADD      r1, #8
	LDR      r0, [r4, #0x2c]
	LDR      r1, [r1, #4]
	ADD      r2, r2, r3
	ADD      r0, r0, r1
	STR      r0, [sp, #8]
	ASR      r1, r2, #1
	ASR      r0, r0, #1
	STR      r2, [sp, #4]
	STR      r1, [sp, #4]
	STR      r1, [sp, #0xc]
	ADD      r1, r4, #0
	LDR      r4, [pc, #0x100]
	STR      r0, [sp, #8]
	STR      r0, [sp, #0x10]
	LDR      r0, [r4]
	ADD      r5, sp, #0xc
	BL       |inc_0x0158_0x143f2| + 0x117ec
	MOV      r2, #0x38
	ADD      r1, r5, #0
	MOV      r0, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x413a
	ADD      r1, r0, #0
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      sp, #0x14
	POP      {r4, r5, pc}
	PUSH     {r4, r5, lr}
	SUB      sp, #0x34
|loc_08038E46|
	ADD      r1, r0, #0
	ADD      r0, #0x40
	MOV      r2, #1
	STRB     r2, [r0]
	LDR      r0, [r1, #0x48]
	CMP      r0, #0
	BEQ      |loc_08038E56|
	B        |loc_08038E46|
|loc_08038E56|
	LDR      r0, [r1, #0x1c]
	ADD      r3, sp, #0
	STR      r0, [sp, #0x20]
	LDRB     r0, [r1, #0x10]
	MOV      r4, sp
	ADD      r5, r4, #4
	STRB     r0, [r3, #0x14]
	LDR      r0, [pc, #0xbc]
	STR      r0, [sp, #0x1c]
	MOV      r0, #5
	LSL      r0, r0, #9
	STR      r0, [sp, #0x18]
	ADD      r0, r1, #0
	STRB     r2, [r3]
	STR      r1, [sp, #0x30]
	ADD      r0, #0x28
	LDMIA    r0!, {r0, r1, r2, r3}
	STMIA    r5!, {r0, r1, r2, r3}
	LDR      r0, [pc, #0xa4]
	ADD      r2, r4, #0
	MOV      r1, #0
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x11ab4
	ADD      sp, #0x34
	POP      {r4, r5, pc}
