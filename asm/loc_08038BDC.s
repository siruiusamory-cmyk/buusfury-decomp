	CODE16
|loc_08038BDC|
	PUSH     {r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x4c]
	SUB      sp, #0x14
	CMP      r0, #0
	BEQ      |loc_08038BEC|
	BL       |loc_08038BDC|
|loc_08038BEC|
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
	LDR      r4, [pc, #0x1c4]
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
|sub_08038C32|
|unk_08038C32|
		PUSH {r4, r5, r6, r7, lr}
		ADD r5, r0, #0
		ADD r6, r1, #0
		MOV r1, #3
		LDR r2, [r0, #0x48]
		ADD r4, r0, #0
		ADD r0, #0x20
		LSL r1, r1, #8
		ADD r5, #0x40
		CMP r2, #0
		SUB sp, #0x34
		BEQ      |sub_08038CC2|
		LDR r1, [r4, #0x4c]
		CMP r1, #0
		BEQ      |inc_0x351c0_0x3d4d0| + 0x3b2a
		LDR r1, [r4, #0x4c]
		LDR r2, [r4, #0x48]
		ADD r1, #0x20
		ADD r2, #0x20
		LDMIA r1!, {r3}
		LDMIA r2!, {r7}
		LDR r1, [r1]
		LDR r2, [r2]
		ADD r3, r3, r7
		ADD r1, r1, r2
		STR r1, [sp, #0x18]
		LDR r2, [sp, #0x18]
		ASR r1, r3, #1
		STR r2, [sp, #0x20]
		ASR r2, r2, #1
		STR r3, [sp, #0x14]
		STR r1, [sp, #0x14]
		STR r2, [sp, #0x18]
		STR r2, [sp, #0x28]
		STR r2, [sp, #0x30]
		STR r1, [sp, #0x24]
		STR r1, [sp, #0x2c]
		STR r3, [sp, #0x1c]
		LDR r1, [r0]
		LDR r7, [r0, #4]
		LSL r3, r1, #1
		ADD r1, r3, r1
		LSL r3, r7, #1
		ADD r3, r3, r7
		LSL r3, r3, #8
		LSL r1, r1, #8
		ASR r2, r1, #8
		ASR r3, r3, #8
		STR r3, [sp, #0x10]
		STR r3, [sp, #0x18]
		STR r2, [sp, #0xc]
		LDR r3, [sp, #0x2c]
		STR r2, [sp, #0x14]
		ADD r2, r2, r3
		LDR r3, [sp, #0x18]
		LDR r7, [sp, #0x30]
		STR r2, [sp, #0xc]
		STR r2, [sp, #0x1c]
		ADD r1, r0, #4
		ADD r3, r3, r7
		ASR r2, r2, #2
		STR r3, [sp, #0x10]
		STR r3, [sp, #0x20]
		ASR r3, r3, #2
		STR r3, [sp, #0x10]
		STR r3, [sp, #0x28]
		STR r2, [sp, #0xc]
		STR r2, [sp, #0x24]
		STR r2, [r0]
		LDR r0, [sp, #0x28]
		STR r0, [r1]
		B        |inc_0x351c0_0x3d4d0| + 0x3b2a
