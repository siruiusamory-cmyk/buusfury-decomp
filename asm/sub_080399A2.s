|sub_080399A2|
	EXPORT |sub_080399A2|
	PUSH     {r4, lr}
	LDR      r1, [r0, #0x34]
	CMP      r1, #0
	BNE      |loc_080399EE|
	LDR      r4, [r0, #0x30]
	CMP      r4, #0
	BEQ      |loc_080399EE|
	MOV      r1, #9
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #0x38]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	ADD      r4, #0xff
	ADD      r4, #0xc1
	LDR      r4, [r4, #0x38]
	CMP      r4, #0
	BEQ      |loc_080399EE|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #9
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, #0xff
	ADD      r4, #0xc1
	LDR      r0, [r4, #0x38]
	CMP      r0, #0
	BEQ      |loc_080399EE|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #9
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_080399EE|
	MOV      r0, #0
	POP      {r4, pc}
	LSL      r0, r0, #0
	ADD      r2, #0xbc
	LSL      r0, r0, #0xc
	MOV      r2, #0x10
	STRH     r2, [r1, #0x12]
	MOV      r2, #0x38
	STRB     r2, [r1, #8]
	MOV      r2, #2
	STRB     r2, [r1, #0x11]
	MOV      r2, #0xc7
	ADD      r1, #0xff
	ADD      r1, #0x61
	MVN      r2, r2
	STRH     r2, [r1, #0x16]
	MOV      r1, #0
	STR      r1, [r0, #4]
	STR      r1, [r0, #8]
	BX       lr
|sub_08039A16|
|unk_08039A16|
		PUSH {r4, r5, r6, r7, lr}
		ADD r4, r0, #0
		LDR r0, [pc, #0x1b0]
		ADD r6, r1, #0
		SUB sp, #0x4c
		ADD r7, sp, #0x24
		LDMIA r0!, {r1, r2, r3}
		STMIA r7!, {r1, r2, r3}
		LDMIA r0!, {r1, r2, r3}
		STMIA r7!, {r1, r2, r3}
		LDMIA r0!, {r0, r1, r2, r3}
		STMIA r7!, {r0, r1, r2, r3}
		ADD r0, r6, #0
		ADD r0, #0xff
		ADD r0, #0x61
		MOV r3, #0x16
		LDRSH r1, [r0, r3]
		SUB r7, #0x28
		CMP r1, #0
		BGE      |loc_08039A42|
		ADD r1, #3
		STRH r1, [r0, #0x16]
|loc_08039A42|
		MOV r3, #0x16
		LDRSH r1, [r0, r3]
		CMP r1, #0
		BLT      |loc_08039A5E|
		MOV r1, #0
		STRH r1, [r0, #0x16]
		LDRH r1, [r6, #0x12]
		CMP r1, #0
		BEQ      |loc_08039A58|
		SUB r1, #1
		STRH r1, [r6, #0x12]
|loc_08039A58|
		LDRH r1, [r6, #0x12]
		LSR r1, r1, #3
		STRB r1, [r6, #0x11]
|loc_08039A5E|
		MOV r1, #0xff
		ADD r1, #0xf1
		LDRH r2, [r0, #0x16]
		LDR r1, [r1, r6]
		MOV r3, #0xff
		ADD r3, #0x77
		STRH r2, [r3, r1]
		ADD r1, #0xff
		ADD r1, #0xc1
		LDRH r2, [r0, #0x16]
		LDR r1, [r1, #0x38]
		STRH r2, [r3, r1]
		ADD r1, #0xff
		ADD r1, #0xc1
		LDR r1, [r1, #0x38]
		LDRH r0, [r0, #0x16]
		ADD r1, #0xff
		ADD r1, #0x61
		STRH r0, [r1, #0x16]
		LDRH r0, [r6, #0x12]
		CMP r0, #0
		BNE      |inc_0x351c0_0x3d4d0| + 0x49a8
		LDR r0, [r4, #4]
		CMP r0, #0
		BNE      |sub_08039B04|
		MOV r1, #0x1e
		MOV r0, #0x46
		BL       |loc_0800797C|
		MOV r0, #0x99
		BL       |inc_0x0158_0x143f2|
		ADD r2, r0, #0
		LDR r0, [pc, #0x128]
		MOV r1, #5
		SUB r0, #0x24
		LDR r0, [r0]
		BL       |loc_08011CCA|
		MOV r1, #5
		SUB r0, r1, r0
		MOV r5, #0
		CMP r0, #0
		STR r0, [r4, #8]
		BLE      |sub_08039B6C|
		MOV r6, #1
		LSL r6, r6, #0xa
|loc_08039ABC|
		LDR r0, [pc, #0x10c]
		SUB r0, #0x24
		LDR r0, [r0]
		BL       |loc_080116FC|
		CMP r0, r6
		BLT      |loc_08039AFA|
		MOV r7, #1
		LSL r7, r7, #0xc
		ADD r0, r7, #0
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r0, r0, r7
		STR r0, [sp]
		MOV r2, #0x37
		LSL r0, r5, #3
		ADD r7, sp, #0x24
		ADD r1, r0, r7
		STR r2, [sp, #8]
		MOV r3, #4
		MOV r0, #0
		LDR r2, [pc, #0xe8]
		STR r6, [sp, #4]
		BL       |loc_0802A81C|
		ADD r1, r0, #0
		LDR r0, [pc, #0xd8]
		SUB r0, #0x24
		LDR r0, [r0]
		BL       |List_Append|
|loc_08039AFA|
		LDR r0, [r4, #8]
		ADD r5, #1
		CMP r0, r5
		BGT      |loc_08039ABC|
		B        |sub_08039B6C|
