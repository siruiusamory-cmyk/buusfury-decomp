	CODE16
|loc_0803A16E|
	PUSH     {r4, lr}
	LDR      r0, [pc, #0x200]
	SUB      sp, #0x28
	LDR      r0, [r0]
	MOV      r1, #1
	LSL      r1, r1, #0xa
	MOV      r2, #0
	ADD      r0, #0xff
	ADD      r0, #0xa1
	STR      r2, [sp, #0x14]
	STR      r1, [sp, #0x10]
	LDMIA    r0!, {r2}
	LDR      r0, [r0]
	ADD      r1, r2, r1
	STR      r0, [sp, #0xc]
	ADD      r0, r1, #0
	STR      r1, [sp, #8]
	LDR      r1, [sp, #0xc]
	STR      r0, [sp, #0x18]
	STR      r1, [sp, #0x1c]
	STR      r1, [sp, #0x24]
	LDR      r1, [pc, #0x1dc]
	STR      r0, [sp, #0x20]
	MOV      r2, #0x20
	ADD      r1, #8
	MOV      r0, sp
	MOV      r4, sp
	BL       |inc_0x049120_0x055620| + 0x18
	LDR      r0, [sp, #0x20]
	ADD      r3, sp, #0
	ASR      r0, r0, #8
	STRH     r0, [r3, #0xc]
	LDR      r0, [sp, #0x24]
	LDR      r1, [pc, #0x1d0]
	ASR      r0, r0, #8
	STRH     r0, [r3, #0xe]
	LDR      r0, [sp, #8]
	LSL      r3, r0, #3
	SUB      r0, r3, r0
	LSL      r0, r0, #2
	ADD      r2, r0, r1
	MOV      r3, #0
	MVN      r3, r3
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xf534
	ADD      r4, r0, #0
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x1a4]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      r0, r4, #0
	ADD      sp, #0x28
	POP      {r4, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDRH     r0, [r1, #0x12]
	ADD      r4, r1, #0
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	CMP      r0, #0x10
	BNE      |loc_0803A222|
	ADD      r0, r5, #0
	BL       |loc_0803A16E|
	MOV      r1, #2
	STR      r0, [r5, #4]
	STRB     r1, [r0, #0x10]
	LDR      r6, [r5, #4]
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803A210|
	LDR      r1, [pc, #0x178]
	STR      r1, [r0]
|loc_0803A210|
	ADD      r7, r0, #0
	MOV      r1, #0x13
	ADD      r0, r6, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r7, #0
	ADD      r0, r6, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
|loc_0803A222|
	LDR      r0, [r5, #4]
	CMP      r0, #0
	BEQ      |loc_0803A246|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x34]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BEQ      |loc_0803A246|
	LDR      r0, [pc, #0x13c]
	LDR      r1, [r5, #4]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	MOV      r0, #0
	STR      r0, [r5, #4]
|loc_0803A246|
	LDRH     r0, [r4, #0x12]
	LSL      r0, r0, #0x15
	LSR      r0, r0, #0x18
	STRB     r0, [r4, #0x11]
	LDR      r1, [r4, #0x50]
	LDR      r1, [r1]
	CMP      r1, r0
	BNE      |loc_0803A264|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0803A264|
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0803A266|
|unk_0803A266|
		ADD r1, #0xff
		ADD r1, #0xc1
		PUSH {r4, r5, r6, lr}
		LDR r1, [r1, #0x30]
		MOV r6, #1
		ADD r1, #0xff
		ADD r1, #0xc1
		LDR r4, [r1, #0x38]
		LDR r1, [r0, #4]
		CMP r1, #0
		BNE      |loc_0803A29E|
		STR r6, [r0, #4]
		MOV r0, #8
		DCD     0xF99AF003
		CMP r0, #0
		BEQ      |loc_0803A28C|
		LDR r1, [pc, #0x100]
		STR r1, [r0]
|loc_0803A28C|
		ADD r5, r0, #0
		MOV r1, #0x12
		ADD r0, r4, #0
		BL       |Record_SelectIndexed|
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |loc_0800ED18|
|loc_0803A29E|
		LDR r0, [r4, #0x58]
		ADD r0, #0x48
		LDR r0, [r0, #0x54]
		LDR r1, [r4, #0x50]
		CMP r0, r1
		BNE      |sub_0803A2AE|
		MOV r0, #1
		B        |inc_0x351c0_0x3d4d0| + 0x50f0
