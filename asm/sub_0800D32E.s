	CODE16
|sub_0800D32E|
|unk_0800D32E|
		MOV r0, #0x34
		LDR r1, [pc, #0x1f0]
		MUL r0, r5
		ADD r0, r0, r1
		NEG r1, r5
		MOV r3, #0x2c
		LDR r2, [pc, #0x1ec]
		MUL r1, r3
		ADD r1, r1, r2
		STR r0, [sp, #0x30]
		ADD r0, #0xc
		ADD r1, #4
		CMP r5, #0
		BLT      |loc_0800D34E|
		ADD r2, r0, #0
		B        |loc_0800D350|
|loc_0800D34E|
		ADD r2, r1, #0
|loc_0800D350|
		STR r2, [sp, #0x1c]
		CMP r5, #0
		BGE      |loc_0800D358|
		ADD r0, r1, #0
|loc_0800D358|
		ADD r1, r0, #0
		ADD r0, sp, #0x20
		ADD r2, r7, #0
		BL       |inc_0x0158_0x143f2| + 0xd8ce
		ADD r2, sp, #0x20
		ADD r0, r4, #0
		LDR r1, [sp, #0x1c]
		BL       |loc_0800D960|
		LDR r0, [pc, #0x1bc]
		ADD r1, r4, #0
		STR r0, [r4]
		ADD r0, r4, #0
		ADD r0, #0x30
		STR r0, [sp, #0x2c]
		ADD r0, #4
		STR r0, [sp, #0x28]
		STR r5, [r4, #0x48]
		LDR r2, [r4, #0x18]
		LDR r3, [r4, #0x1c]
		LSL r2, r2, #8
		LSL r3, r3, #8
		STR r2, [r4, #0x60]
		MOV r0, #0xff
		ADD r1, #0x60
		ADD r0, #1
		STR r3, [r4, #0x64]
		BL       |inc_0x03d784_0x041118| + 0x2348
		LDR r1, [r6, #4]
		SUB r0, #0x80
		MUL r0, r1
		LDR r1, [r6]
		ASR r0, r0, #8
		ADD r0, r0, r1
		STR r0, [r4, #0x68]
		MOV r0, #0xff
		ADD r0, #1
		BL       |inc_0x03d784_0x041118| + 0x2348
		LDR r1, [r6]
		SUB r0, #0x80
		MUL r0, r1
		LDR r1, [r6, #4]
		ASR r0, r0, #8
		ADD r0, r0, r1
		STR r0, [r4, #0x6c]
		MOV r0, #0x40
		BL       |inc_0x03d784_0x041118| + 0x2348
		LDR r1, [r4, #0x68]
		ADD r0, #0xe0
		MUL r0, r1
		ASR r0, r0, #8
		STR r0, [r4, #0x68]
		MOV r0, #0x40
		BL       |inc_0x03d784_0x041118| + 0x2348
		LDR r1, [r4, #0x6c]
		ADD r0, #0xe0
		MUL r0, r1
		ASR r0, r0, #8
		STR r0, [r4, #0x6c]
		LDR r0, [r7]
		LDR r1, [r7, #4]
		SUB r0, #8
		STR r0, [r4, #0x50]
		SUB r1, #6
		STR r1, [r4, #0x54]
		MOV r1, #1
		LDR r0, [sp, #0x2c]
		LSL r1, r1, #0xd
		STR r1, [r0]
		LDR r0, [sp, #0x28]
		LSR r1, r1, #2
		STR r1, [r0]
		MOV r7, #0
		STR r7, [r4, #0x38]
		MOV r1, #4
		MOV r0, #0xa
		STR r7, [r4, #0x40]
		BL       |loc_08013E38|
		STR r0, [r4, #0x4c]
		ADD r5, r0, #4
		LDMIA r5!, {r1, r5}
		STR r1, [sp, #0x24]
		LDRH r6, [r0, #2]
		LDRB r0, [r5]
		ADD r1, r0, #1
		STRB r1, [r5]
		CMP r0, #0
		BNE      |loc_0800D432|
		LDR r0, [pc, #0x108]
		ADD r1, r6, #0
		LDR r0, [r0]
		BL       |loc_0801124C|
		LSL r0, r0, #0x10
		ASR r0, r0, #0x10
		STRH r0, [r5, #2]
		LDR r1, [pc, #0x108]
		LSL r0, r0, #5
		ADD r0, r0, r1
		LDR r1, [sp, #0x24]
		ADD r2, r6, #0
		BL       |Thunk_VramCopy|
|loc_0800D432|
		MOV r0, #0x38
		STRB r0, [r4, #8]
		LDR r0, [r4, #0x48]
		CMP r0, #0
		BLT      |loc_0800D448|
		LDR r0, [sp, #0x30]
		LDRB r0, [r0]
		LSL r0, r0, #0x1d
		LSR r0, r0, #0x1f
		STR r0, [r4, #0x44]
		B        |loc_0800D44A|
|loc_0800D448|
		STR r7, [r4, #0x44]
|loc_0800D44A|
		ADD r1, r4, #0
		ADD r0, sp, #0x18
		STR r7, [r4, #0x3c]
		BL       |sub_0800DB64|
		LDR r1, [sp, #0x18]
		LDR r2, [r4, #0x18]
		ADD r0, r4, #0
		SUB r1, r1, r2
		LDR r2, [sp, #0x1c]
		LDR r3, [r4, #0x1c]
		STR r1, [sp]
		SUB r2, r2, r3
		ADD r3, r1, #0
		LDR r1, [sp, #0x20]
		STR r2, [sp, #4]
		ADD r5, r2, #0
		LDR r2, [r4, #0x18]
		ADD r0, #0x70
		SUB r1, r1, r2
		LDR r2, [sp, #0x24]
		LDR r6, [r4, #0x1c]
		STR r5, [sp, #0xc]
		SUB r2, r2, r6
		STR r2, [sp, #4]
		STR r2, [sp, #0x14]
		ADD r5, sp, #8
		STR r1, [sp]
		STR r3, [sp, #8]
		STR r1, [sp, #0x10]
		LDMIA r5!, {r1, r2, r3, r5}
		STMIA r0!, {r1, r2, r3, r5}
		LDR r0, [r4, #0x44]
		CMP r0, #0
		BEQ      |loc_0800D4CC|
		MOV r0, #0x14
		DCW     0xF030
		DCW     0xF891
		ADD r5, r0, #0
		BEQ      |loc_0800D4BA|
		BL       |loc_0800776C|
		LDR r1, [sp, #0x18]
		LDR r2, [sp, #0x1c]
		ADD r6, sp, #0x20
		SUB r1, #0xf
		LDMIA r6!, {r3, r6}
		STRH r1, [r5, #4]
		SUB r2, #7
		STRH r2, [r5, #6]
		STRH r3, [r5, #8]
		STRH r6, [r5, #0xa]
		STR r0, [r5, #0xc]
		LDR r0, [pc, #0x64]
		STR r0, [r5]
		STR r4, [r5, #0x10]
|loc_0800D4BA|
		LDR r0, [pc, #0x64]
		STR r5, [r4, #0x3c]
		LDR r0, [r0, #0x10]
		LDR r1, [r0]
		ADD r2, r1, #1
		STR r2, [r0]
		LSL r1, r1, #2
		ADD r0, r1, r0
		STR r5, [r0, #4]
|loc_0800D4CC|
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0xd1d2
