	CODE16
|sub_08036CB6|
|unk_08036CB6|
		LDR r1, [r0, #0x38]
		LDRH r0, [r0, #0xc]
		LDRB r3, [r1, #2]
		LDRB r4, [r1, #3]
		LSL r0, r0, #5
		LDR r1, [r1, #8]
		MUL r3, r4
		ADD r2, r3, #0
		LDR r3, [pc, #0xb0]
		ADD r0, r0, r3
		BL       |Thunk_VramCopy|
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x1af2
|loc_08036CD2|
|unk_08036CD2|
		LDR r1, [r0]
		LDR r2, [r1, #8]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x1af2
|loc_08036CE0|
|unk_08036CE0|
		LDR r2, [r0, #0x10]
		LDR r3, [r0, #0x14]
		ADD r2, #0x10
		STR r2, [sp, #4]
		STR r2, [sp, #0xc]
		ADD r3, #0x10
		ADD r2, #0x20
		STR r2, [sp, #0x14]
		ADD r2, r3, #0
		ADD r2, #0x20
		STR r2, [sp, #0x18]
		STR r3, [sp, #8]
		STR r3, [sp, #0x10]
		LDR r2, [r7]
		LDR r3, [sp, #0x14]
		ADD r6, sp, #0xc
		CMP r2, r3
		BGE      |inc_0x351c0_0x3d4d0| + 0x1b80
		LDR r2, [sp, #0xc]
		LDR r3, [r7, #8]
		CMP r2, r3
		BGE      |inc_0x351c0_0x3d4d0| + 0x1b80
		LDR r2, [r7, #4]
		LDR r3, [sp, #0x18]
		CMP r2, r3
		BGE      |inc_0x351c0_0x3d4d0| + 0x1b80
		LDR r2, [sp, #0x10]
		LDR r3, [r7, #0xc]
		CMP r2, r3
		BGE      |inc_0x351c0_0x3d4d0| + 0x1b80
		LDR r5, [pc, #0x54]
		ADD r2, r1, #0
		LDR r3, [r0, #0x38]
		ADD r1, #0xc
		ADD r5, #0x18
		CMP r3, r2
		BEQ      |loc_08036D2C|
		ADD r1, r5, #0
|loc_08036D2C|
		STR r1, [r0, #0x38]
		LDMIA r6!, {r1, r2, r3, r6}
		STMIA r7!, {r1, r2, r3, r6}
		LDR r0, [r0, #0x38]
		CMP r0, r5
		BEQ      |loc_08036D3A|
		MOV r4, #0
|loc_08036D3A|
		ADD r0, r4, #0
		B        |inc_0x351c0_0x3d4d0| + 0x1af2
|loc_08036D3E|
|unk_08036D3E|
		B        |inc_0x351c0_0x3d4d0| + 0x1ba2
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x1af2
