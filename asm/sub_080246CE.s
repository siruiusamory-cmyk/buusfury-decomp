	CODE16
|sub_080246CE|
|unk_080246CE|
		ADD r2, r6, #0
		MOV r1, #0x40
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x4712
		LDR r0, [pc, #0x264]
		STR r0, [r4]
		ADD r0, r4, #0
		BL       |sub_08011568|
		LDR r7, [pc, #0x260]
		LDRB r0, [r7]
		ADD r1, r0, #1
		STRB r1, [r7]
		CMP r0, #0
		BNE      |loc_08024710|
		LDR r0, [pc, #0x258]
		MOV r1, #0x13
		LSL r1, r1, #8
		LDR r0, [r0]
		BL       |loc_0801124C|
		LSL r0, r0, #0x10
		ASR r0, r0, #0x10
		STRH r0, [r7, #2]
		LDR r1, [pc, #0x248]
		LSL r0, r0, #5
		ADD r0, r0, r1
		MOV r2, #0x13
		LSL r2, r2, #8
		LDR r1, [pc, #0x244]
		BL       |Thunk_VramCopy|
|loc_08024710|
		LDR r1, [r5]
		LDR r2, [r5, #4]
		LDRB r6, [r6, #0x10]
		MOV r0, #0
		STR r0, [r4, #0x50]
		LSL r1, r1, #8
		STR r1, [r4, #0x20]
		LSL r2, r2, #8
		STR r2, [r4, #0x24]
		MOV r1, #0x44
		STRB r0, [r1, r4]
		STR r0, [r4, #0x40]
		LSL r0, r6, #4
		SUB r0, r0, r6
		LDR r1, [pc, #0x224]
		LSL r0, r0, #2
		ADD r0, r0, r1
		STR r0, [r4, #0x54]
		STR r0, [r4, #0x18]
		MOV r0, #0xc0
		BL       |inc_0x03d784_0x041118| + 0x2348
		LSL r5, r6, #3
		LDR r6, [pc, #0x208]
		ADD r6, #4
		LDR r1, [r6, r5]
		ADD r0, r0, r1
		SUB r0, #0x60
		STR r0, [r4, #0x48]
		MOV r0, #0xc0
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r1, r5, r6
		LDR r1, [r1, #4]
		ADD r0, r0, r1
		SUB r0, #0x60
		STR r0, [r4, #0x4c]
		MOV r0, #0x38
		STRB r0, [r4, #8]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		ADD r0, r4, #0
		DCW     0xE7B1
