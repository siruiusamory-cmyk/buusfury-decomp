	CODE16
|sub_0803C410|
	PUSH     {r3, r4, r5, lr}
	LDR      r4, [r1, #4]
	MOV      r1, #0x12
	ADD      r5, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xed20
	LDR      r0, [r5, #0xc]
	STRB     r0, [r4, #0x10]
	MOV      r0, #0
	STRH     r0, [r4, #0x12]
	MOV      r1, #0x38
	STRB     r1, [r4, #8]
	STRB     r0, [r4, #0x11]
	STR      r0, [r5, #0x10]
	POP      {r3, r4, r5, pc}
	PUSH     {r4, lr}
	LDR      r3, [r1, #4]
	ADD      r4, r0, #0
	LDRH     r0, [r3, #0x12]
	SUB      sp, #0x18
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r3, #0x12]
	CMP      r0, #0x20
	BCS      |loc_0803C4A6|
	LSR      r1, r0, #3
	STRB     r1, [r3, #0x11]
	CMP      r0, #0x10
	BNE      |loc_0803C4A6|
	ADD      r0, r3, #0
	ADD      r0, #0xff
	ADD      r0, #0xa1
	LDMIA    r0!, {r1}
	LDR      r0, [r0]
	ASR      r1, r1, #8
	ASR      r0, r0, #8
	STR      r0, [sp, #4]
	ADD      r0, r1, #0
	STR      r1, [sp]
	LDR      r1, [sp, #4]
	STR      r0, [sp, #8]
	STR      r1, [sp, #0xc]
	LDRB     r0, [r3, #0x10]
	LDR      r1, [pc, #0x64]
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	LDR      r1, [sp, #8]
	LDR      r2, [r0]
	ADD      r1, r1, r2
	LDR      r2, [sp, #0xc]
	LDR      r0, [r0, #4]
	STR      r1, [sp]
	ADD      r0, r2, r0
	STR      r0, [sp, #4]
	ADD      r0, r1, #0
	LDR      r1, [sp, #4]
	STR      r0, [sp, #0x10]
	STR      r1, [sp, #0x14]
	LDRB     r2, [r3, #0x10]
	ADD      r1, sp, #0x10
	MOV      r0, #0
	BL       |inc_0x1c3f2_0x2ab4c| + 0xc2e2
	ADD      r1, r0, #0
	STR      r0, [r4, #0x10]
	LDR      r0, [pc, #0x38]
	SUB      r0, #4
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_0803C4A6|
	ADD      sp, #0x18
	POP      {r4, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #8]
	SUB      r0, #1
	STR      r0, [r4, #8]
	BNE      |sub_0803C4D4|
	LDR      r0, [r1, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [r4, #0x10]
	CMP      r0, #0
	BEQ      |loc_0803C4D0|
	ADD      r1, r0, #0
	MOV      r0, #1
	STRB     r0, [r1, #0x10]
|loc_0803C4D0|
	MOV      r0, #1
	POP      {r4, pc}
