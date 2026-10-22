	CODE16
|sub_0803CD94|
|unk_0803CD94|
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0xa1
		LDMIA r0!, {r1}
		LDR r0, [r0]
		ASR r1, r1, #8
		ASR r0, r0, #8
		STR r0, [sp, #8]
		ADD r0, r1, #0
		STR r1, [sp, #4]
		LDR r1, [sp, #8]
		STR r0, [sp, #0xc]
		STR r1, [sp, #0x10]
		LDRB r0, [r4, #0x10]
		LDR r1, [pc, #0xb0]
		MOV r3, #2
		ADD r1, #4
		LSL r0, r0, #3
		ADD r0, r0, r1
		LDR r1, [sp, #0xc]
		LDR r2, [r0]
		ADD r1, r1, r2
		LDR r2, [sp, #0x10]
		LDR r0, [r0, #4]
		STR r1, [sp, #4]
		ADD r0, r2, r0
		STR r0, [sp, #8]
		ADD r0, r1, #0
		LDR r1, [sp, #8]
		STR r0, [sp, #0x14]
		ADD r2, r4, #0
		STR r1, [sp, #0x18]
		ADD r1, sp, #0x14
		MOV r0, #0
		BL       |inc_0x351c0_0x3d4d0| + 0x1de2
		ADD r1, r0, #0
		STR r0, [r6, #4]
		LDR r0, [r7]
		BL       |List_Append|
|loc_0803CDE6|
|unk_0803CDE6|
		LDR r0, [r4, #0x50]
		LDR r0, [r0]
		CMP r0, r5
		BGT      |loc_0803CDF8|
		ADD r5, #1
		LSL r0, r5, #0x1f
		LSR r0, r0, #0x1f
		ADD r0, #3
		STRB r0, [r4, #0x11]
|loc_0803CDF8|
		LDRH r0, [r4, #0x12]
		CMP r0, #0xb4
		BLS      |inc_0x351c0_0x3d4d0| + 0x7bd0
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
|loc_0803CE0C|
|unk_0803CE0C|
		B        |inc_0x351c0_0x3d4d0| + 0x7bd0
		PUSH {r4, r5, r6, lr}
		ADD r4, r1, #0
		LDR r1, [r0, #4]
		MOV r6, #1
		CMP r1, #0
		BNE      |loc_0803CE3C|
		STR r6, [r0, #4]
		MOV r0, #8
		DCW     0xF000
		DCW     0xFBCB
		CMP r0, #0
		BEQ      |loc_0803CE2A|
		LDR r1, [pc, #0x40]
		STR r1, [r0]
|loc_0803CE2A|
		ADD r5, r0, #0
		MOV r1, #0x13
		ADD r0, r4, #0
		BL       |Record_SelectIndexed|
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |loc_0800ED18|
|loc_0803CE3C|
		LDR r0, [r4, #0x58]
		ADD r0, #0x4c
		LDR r0, [r0, #0x54]
		LDR r1, [r4, #0x50]
		CMP r0, r1
		BNE      |sub_0803CE4C|
		MOV r0, #1
		B        |inc_0x351c0_0x3d4d0| + 0x7c8e
