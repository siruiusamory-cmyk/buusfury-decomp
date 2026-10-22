	CODE16
|sub_0803C2EE|
	LSL      r0, r0, #0
|unk_0803C2F0|
	INCBIN	baserom.gba_0x3c2f0_0x3c2f2.extracted
	LSR      r7, r6, #1
	STMIA    r4!, {r2, r3, r4}
	LSR      r7, r6, #1
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDR      r0, [r0, #0xc]
	LDR      r4, [r1, #4]
	SUB      sp, #0x18
	STRB     r0, [r4, #0x10]
	MOV      r1, #3
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xed20
	MOV      r6, #0
	STRH     r6, [r4, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r4, #8]
	STRB     r6, [r4, #0x11]
	LDRB     r0, [r4, #0x10]
	LDR      r1, [pc, #0xe8]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #2
	ADD      r0, r0, r1
	ADD      r1, r4, #0
	ADD      r1, #0xff
	ADD      r1, #0xa1
	LDMIA    r1!, {r2}
	LDR      r1, [r1]
	ASR      r2, r2, #8
	ASR      r1, r1, #8
	STR      r1, [sp, #4]
	ADD      r1, r2, #0
	STR      r2, [sp]
	LDR      r2, [sp, #4]
	STR      r1, [sp, #8]
	STR      r2, [sp, #0xc]
	LDR      r2, [r0]
	ADD      r1, r1, r2
	LDR      r2, [sp, #0xc]
	LDR      r3, [r0, #4]
	STR      r1, [sp]
	ADD      r2, r2, r3
	STR      r2, [sp, #4]
	STR      r2, [sp, #0x14]
	LDR      r2, [pc, #0xb8]
	STR      r1, [sp, #0x10]
	STR      r2, [sp]
	LDR      r2, [r0, #8]
	ADD      r3, r4, #0
	MOV      r0, #0
	ADD      r1, sp, #0x10
	BL       |inc_0x1c3f2_0x2ab4c| + 0x42c6
	STR      r0, [r5, #0x10]
	STR      r6, [r0, #0x50]
	LDR      r0, [pc, #0x9c]
	LDR      r1, [r5, #0x10]
	SUB      r0, #4
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      sp, #0x18
	POP      {r4, r5, r6, pc}
	PUSH     {r4, lr}
	LDR      r4, [r1, #4]
	SUB      sp, #0x18
	LDRH     r1, [r4, #0x12]
	ADD      r1, #1
	LSL      r1, r1, #0x10
	LSR      r1, r1, #0x10
	STRH     r1, [r4, #0x12]
	CMP      r1, #0x18
	BCC      |loc_0803C3DA|
	CMP      r1, #0x18
	BNE      |loc_0803C3D6|
	ADD      r1, r4, #0
	ADD      r1, #0xff
	ADD      r1, #0xa1
	LDMIA    r1!, {r2}
	LDR      r1, [r1]
	ASR      r2, r2, #8
	ASR      r1, r1, #8
	STR      r1, [sp, #4]
	ADD      r1, r2, #0
	STR      r2, [sp]
	LDR      r2, [sp, #4]
	STR      r1, [sp, #8]
	STR      r2, [sp, #0xc]
	LDRB     r1, [r4, #0x10]
	LDR      r2, [pc, #0x58]
	ADD      r2, #0x30
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	LDR      r2, [sp, #8]
	LDR      r3, [r1]
	ADD      r2, r2, r3
	LDR      r3, [sp, #0xc]
	LDR      r1, [r1, #4]
	STR      r2, [sp]
	ADD      r1, r3, r1
	STR      r1, [sp, #4]
	ADD      r1, r2, #0
	LDR      r2, [sp, #4]
	STR      r1, [sp, #0x10]
	STR      r2, [sp, #0x14]
	LDRB     r1, [r4, #0x10]
	LDR      r0, [r0, #0x10]
	ADD      r2, sp, #0x10
	BL       |inc_0x1c3f2_0x2ab4c| + 0x43e0
|loc_0803C3D6|
	MOV      r0, #1
	STRB     r0, [r4, #0x11]
|loc_0803C3DA|
	ADD      sp, #0x18
	POP      {r4, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #8]
	SUB      r0, #1
	STR      r0, [r4, #8]
	BNE      |sub_0803C402|
	LDR      r0, [r1, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [r4, #0x10]
	BL       |inc_0x1c3f2_0x2ab4c| + 0x4438
	MOV      r0, #1
	POP      {r4, pc}
