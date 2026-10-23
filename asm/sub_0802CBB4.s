	CODE16
|sub_0802CBB4|
	PUSH     {r3, r4, r5, lr}
	LDR      r4, [r1, #4]
	ADD      r1, r0, #0
	ADD      r1, #8
	ADD      r5, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb58
	ADD      r5, #0x10
	ADD      r4, #0xff
	ADD      r4, #1
	ADD      r4, #0x78
	LDMIA    r5!, {r0, r1}
	STMIA    r4!, {r0, r1}
	POP      {r3, r4, r5, pc}
	LSL      r0, r0, #0
	PUSH     {r4, r5, r6, r7, lr}
	SUB      sp, #0x24
	ADD      r4, r1, #0
	LDR      r1, [pc, #0x134]
	MOV      r2, #0x20
	MOV      r6, sp
	MOV      r0, sp
	BL       |inc_0x049120_0x055620| + 0x18
	MOV      r0, #0xff
	ADD      r0, #0xa1
	LDR      r0, [r0, r4]
	ADD      r3, sp, #0
	ASR      r0, r0, #8
	STRH     r0, [r3, #0xc]
	MOV      r0, #0xff
	ADD      r0, #0xa5
	LDR      r0, [r0, r4]
	MOV      r1, #0
	ASR      r0, r0, #8
	STRH     r0, [r3, #0xe]
	ADD      r0, r4, #0
	ADD      r0, #0xff
	ADD      r0, #0xc1
	STR      r0, [sp, #0x20]
	STR      r1, [r0, #0x34]
	LDRH     r0, [r3, #0xe]
	LDR      r1, [pc, #0x10c]
	ADD      r7, r4, #0
	SUB      r0, #0xc
	STRH     r0, [r3, #0xe]
	LDR      r0, [pc, #0x100]
	MOV      r3, #0
	ADD      r4, r0, r1
	ADD      r2, r4, #0
	ADD      r1, r6, #0
	MVN      r3, r3
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xf534
	ADD      r5, r0, #0
	ADD      r1, r0, #0
	LDR      r0, [pc, #0xe4]
	SUB      r0, #4
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	LDR      r0, [sp, #0x20]
	ADD      r3, sp, #0
	STR      r5, [r0, #0x30]
	MOV      r0, #0xff
	ADD      r0, #0xf5
	STR      r7, [r0, r5]
	LDRH     r0, [r3, #0xe]
	ADD      r2, r4, #0
	SUB      r0, #0xc
	STRH     r0, [r3, #0xe]
	MOV      r3, #0
	MVN      r3, r3
	ADD      r1, r6, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xf534
	ADD      r7, r0, #0
	ADD      r1, r0, #0
	LDR      r0, [pc, #0xb8]
	SUB      r0, #4
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	MOV      r0, #0xff
	ADD      r0, #0xf1
	STR      r7, [r0, r5]
	ADD      r1, r0, #4
	STR      r5, [r1, r7]
	ADD      r3, sp, #0
	LDRH     r0, [r3, #0xe]
	ADD      r2, r4, #0
	SUB      r0, #0xc
	STRH     r0, [r3, #0xe]
	MOV      r3, #0
	MVN      r3, r3
	ADD      r1, r6, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xf534
	ADD      r5, r0, #0
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x88]
	SUB      r0, #4
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	MOV      r0, #0xff
	ADD      r0, #0xf1
	STR      r5, [r0, r7]
	ADD      r1, r0, #4
	STR      r7, [r1, r5]
	ADD      r3, sp, #0
	LDRH     r0, [r3, #0xe]
	ADD      r2, r4, #0
	SUB      r0, #0xc
	STRH     r0, [r3, #0xe]
	MOV      r3, #0
	MVN      r3, r3
	ADD      r1, r6, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xf534
	ADD      r7, r0, #0
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x5c]
	SUB      r0, #4
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	MOV      r0, #0xff
	ADD      r0, #0xf1
	STR      r7, [r0, r5]
	ADD      r1, r0, #4
	STR      r5, [r1, r7]
	ADD      r3, sp, #0
	LDRH     r0, [r3, #0xe]
	ADD      r2, r4, #0
	SUB      r0, #0xc
	STRH     r0, [r3, #0xe]
	MOV      r3, #0
	MVN      r3, r3
	ADD      r1, r6, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xf534
	ADD      r4, r0, #0
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x2c]
	SUB      r0, #4
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	MOV      r1, #0xff
	ADD      r1, #0xf1
	STR      r4, [r1, r7]
	ADD      r4, #0xff
	ADD      r4, #0xc1
	MOV      r0, #0
	ADD      r4, #0x30
	STMIA    r4!, {r0, r7}
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	MOV      r0, #4
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0802CD0E|
	LDR      r1, [pc, #0x10]
	STR      r1, [r0]
|loc_0802CD0E|
	POP      {r3, pc}
|sub_0802CD10|
|unk_0802CD10|
	INCBIN	baserom.gba_0x2cd10_0x2cd12.extracted
