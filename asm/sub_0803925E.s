	CODE16
|sub_0803925E|
	LSR      r4, r0, #0x20
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	STRB     r2, [r1, #0x11]
	BX       lr
|sub_0803926C|
|unk_0803926C|
		PUSH {r4, r5, r6, lr}
		ADD r4, r1, #0
		LDRH r1, [r1, #0x12]
		SUB sp, #0x30
		LSR r0, r1, #3
		LSL r0, r0, #0x18
		LSR r0, r0, #0x18
		STRB r0, [r4, #0x11]
		CMP r0, #4
		BLS      |loc_0803928A|
		ADD r0, #1
		LSL r0, r0, #0x1f
		LSR r0, r0, #0x1f
		ADD r0, #3
		STRB r0, [r4, #0x11]
|loc_0803928A|
		CMP r1, #0x28
		BNE      |loc_08039308|
		LDR r0, [pc, #0xc0]
		ADD r5, sp, #0x20
		LDMIA r0!, {r0, r1, r2, r3}
		STMIA r5!, {r0, r1, r2, r3}
		LDR r1, [pc, #0xb8]
		SUB r5, #0x10
		MOV r2, #0x20
		SUB r1, #0x20
		MOV r0, sp
		MOV r6, sp
		BL       |Thunk_VramCopy|
		MOV r0, #0xff
		ADD r0, #0xa1
		LDR r0, [r0, r4]
		ADD r3, sp, #0
		ASR r0, r0, #8
		STRH r0, [r3, #0xc]
		MOV r0, #0xff
		ADD r0, #0xa5
		LDR r0, [r0, r4]
		ASR r0, r0, #8
		STRH r0, [r3, #0xe]
		LDRB r0, [r4, #0x10]
		LDRH r1, [r3, #0xc]
		LSL r0, r0, #2
		ADD r0, r0, r5
		LDRH r2, [r0]
		ADD r1, r1, r2
		STRH r1, [r3, #0xc]
		LDRH r1, [r3, #0xe]
		LDRH r0, [r0, #2]
		LDR r2, [pc, #0x84]
		ADD r0, r1, r0
		STRH r0, [r3, #0xe]
		MOV r3, #0
		MVN r3, r3
		ADD r1, r6, #0
		MOV r0, #0
		BL       |Battle_CreateEnemy|
		ADD r5, r0, #0
		ADD r1, r0, #0
		LDR r0, [pc, #0x68]
		SUB r0, #0x24
		LDR r0, [r0]
		BL       |List_Append|
		ADD r1, r5, #0
		ADD r1, #0xff
		ADD r1, #0xc1
		STR r4, [r1, #0x34]
		LDRB r0, [r4, #0x10]
		ADD r2, r4, #0
		ADD r2, #0xff
		ADD r2, #0xc1
		STRB r0, [r5, #0x10]
		LDR r0, [r2, #0x30]
		CMP r0, #0
		BNE      |sub_0803930A|
		STR r5, [r2, #0x30]
|loc_08039308|
		B        |inc_0x351c0_0x3d4d0| + 0x416c
