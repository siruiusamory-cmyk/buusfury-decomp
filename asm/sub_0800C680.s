	CODE16
|sub_0800C680|
|unk_0800C680|
		LDR r0, [pc, #0x1c4]
		STR r0, [r4]
		STR r5, [r4, #0x28]
		LDRB r0, [r5, #5]
		STRB r0, [r4, #0xc]
		LDRH r0, [r5, #6]
		LDR r5, [pc, #0x1bc]
		STRH r0, [r4, #0xe]
		STR r6, [r4, #0x2c]
		LDRB r0, [r6, #8]
		ADD r5, sp
		STRB r0, [r4, #8]
		LDR r0, [r6, #4]
		STR r0, [r4, #4]
		MOV r0, #0
		STR r0, [r4, #0x24]
		STR r0, [r4, #0x10]
		LDR r0, [r6, #0x20]
		ADD r6, sp, #8
		LDR r2, [r0, #8]
		LDR r3, [r0]
		LDR r1, [r0, #0xc]
		SUB r2, r2, r3
		MOV r3, #1
		LDR r0, [r0, #4]
		LSL r3, r3, #0xc
		ADD r3, sp
		SUB r0, r1, r0
		STR r0, [r3, #4]
		STR r2, [r3]
		LDR r1, [r3, #4]
		STR r1, [r3, #0xc]
		STR r2, [r3, #8]
		LDR r0, [r4, #0x2c]
		MUL r2, r1
		LDRH r0, [r0, #0x16]
		LDR r1, [pc, #0x184]
		LSL r0, r0, #5
		ADD r1, r0, r1
		ADD r0, r6, #0
		BL       |Thunk_VramCopy|
		LDR r1, [r4, #0x2c]
		MOV r3, #1
		LDR r0, [r1, #0x20]
		MOV ip, r1
		LDR r2, [r0, #8]
		LDR r0, [r0, #0xc]
		LSL r3, r3, #0xc
		STR r0, [r4, #0x18]
		STR r2, [r4, #0x14]
		LDR r0, [r1, #0x20]
		ADD r3, sp
		LDR r1, [r0]
		LDR r0, [r0, #4]
		MOV r2, #0
		STR r0, [r4, #0x20]
		STR r1, [r4, #0x1c]
		LDR r0, [r3, #0xc]
		CMP r0, #0
		BLE      |loc_0800C782|
|loc_0800C6FA|
		ASR r0, r2, #3
		STR r0, [sp, #4]
		LSL r0, r2, #0x1d
		LSR r0, r0, #0x1d
		STR r0, [sp]
		MOV r1, ip
		LDR r0, [r1, #0x20]
		LDR r0, [r0, #4]
		LDR r3, [r5]
		ADD r1, r0, r2
		MOV r0, #0
		CMP r3, #0
		BLE      |loc_0800C77A|
		ADD r6, r1, #1
		MOV r3, #1
		LSL r3, r3, #0xc
		ADD r3, sp
		STR r6, [r3, #0x10]
|loc_0800C71E|
		LSL r6, r0, #0x1d
		LSR r6, r6, #0x1d
		MOV lr, r6
		LDR r6, [r5]
		LDR r3, [sp, #4]
		ASR r7, r0, #3
		MUL r6, r3
		LDR r3, [sp]
		ADD r3, r6, r3
		LSL r6, r3, #3
		LSL r3, r7, #6
		ADD r6, r6, r3
		ADD r6, lr
		ADD r7, sp, #8
		LDRB r3, [r7, r6]
		CMP r3, #0
		BEQ      |loc_0800C772|
		MOV r3, ip
		LDR r3, [r3, #0x20]
		LDR r6, [r3]
		LDR r7, [r4, #0x14]
		ADD r6, r6, r0
		CMP r7, r6
		BLE      |loc_0800C750|
		STR r6, [r4, #0x14]
|loc_0800C750|
		LDR r7, [r4, #0x18]
		CMP r7, r1
		BLE      |loc_0800C758|
		STR r1, [r4, #0x18]
|loc_0800C758|
		LDR r7, [r4, #0x1c]
		CMP r7, r6
		BGT      |loc_0800C762|
		ADD r6, #1
		STR r6, [r4, #0x1c]
|loc_0800C762|
		LDR r6, [r4, #0x20]
		CMP r6, r1
		BGT      |loc_0800C772|
		MOV r3, #1
		LSL r3, r3, #0xc
		ADD r3, sp
		LDR r6, [r3, #0x10]
		STR r6, [r4, #0x20]
|loc_0800C772|
		LDR r6, [r5]
		ADD r0, #1
		CMP r6, r0
		BGT      |loc_0800C71E|
|loc_0800C77A|
		LDR r0, [r5, #4]
		ADD r2, #1
		CMP r0, r2
		BGT      |loc_0800C6FA|
|loc_0800C782|
		LDR r0, [r4, #0x18]
		LDR r1, [r4, #0x20]
		ADD r0, r0, r1
		ASR r0, r0, #1
		STR r0, [r4, #0x18]
		MOV r1, ip
		LDR r0, [r1, #0x1c]
		CMP r0, #0
		BEQ      |loc_0800C7B2|
		LDR r0, [pc, #0x98]
		ADD r5, r4, #0
		LDR r6, [r0, #4]
		ADD r5, #0x14
		ADD r6, #0x80
		MOV r2, #0
		ADD r0, r5, #0
		LDR r1, [r6, #0x28]
		BL       |loc_08009930|
		MOV r2, #0
		ADD r0, r5, #0
		LDR r1, [r6, #0x30]
		BL       |loc_08009930|
|loc_0800C7B2|
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0xc522
