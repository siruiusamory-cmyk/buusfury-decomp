	CODE16
|sub_0803605A|
|unk_0803605A|
		LDRH r0, [r4, #0x12]
		CMP r0, #0x8c
		BNE      |loc_08036132|
		LDR r0, [pc, #0x134]
		LDR r5, [r0]
		CMP r5, #0
		BEQ      |loc_08036072|
		MOV r0, #0xff
		ADD r0, #0xcd
		LDR r0, [r0, r5]
		CMP r0, #0
		BNE      |loc_08036076|
|loc_08036072|
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0xe96
|loc_08036076|
		ADD r1, r5, #0
		ADD r0, sp, #0x5c
		BL       |loc_0800FE78|
		ADD r1, r4, #0
		ADD r0, sp, #0x4c
		BL       |loc_0800FE78|
		LDR r0, [sp, #0x4c]
		LDR r1, [sp, #0x54]
		LDR r2, [sp, #0x58]
		ADD r0, r0, r1
		LDR r1, [sp, #0x50]
		STR r0, [sp, #0x3c]
		ADD r1, r1, r2
		ASR r0, r0, #1
		ASR r3, r1, #1
		STR r0, [sp, #0x44]
		STR r0, [sp, #0x3c]
		STR r1, [sp, #0x40]
		LDR r1, [sp, #0x64]
		LDR r0, [sp, #0x5c]
		STR r3, [sp, #0x40]
		ADD r1, r0, r1
		LDR r0, [sp, #0x60]
		STR r3, [sp, #0x48]
		LDR r2, [sp, #0x68]
		STR r1, [sp]
		ADD r0, r0, r2
		STR r0, [sp, #4]
		ASR r0, r0, #1
		ASR r1, r1, #1
		STR r0, [sp, #4]
		STR r0, [sp, #0xc]
		ADD r0, r1, #0
		STR r1, [sp]
		STR r1, [sp, #8]
		LDR r1, [sp, #0x44]
		LDR r2, [sp, #0x48]
		SUB r0, r0, r1
		LDR r1, [sp, #0xc]
		STR r0, [sp]
		SUB r6, r1, r2
		ADD r1, r0, #0
		CMP r0, #0
		STR r6, [sp, #4]
		BGE      |loc_080360D6|
		NEG r1, r0
|loc_080360D6|
		ADD r2, r6, #0
		CMP r6, #0
		BGE      |loc_080360DE|
		NEG r2, r2
|loc_080360DE|
		MOV r7, #0
		CMP r1, r2
		BLE      |loc_08036110|
		STR r3, [sp, #0x18]
		LDR r1, [sp, #0x58]
		ADD r1, #3
		STR r1, [sp, #0x20]
		CMP r0, #0
		BLE      |loc_08036100|
		MOV r0, #3
		STRB r0, [r4, #0x10]
		LDR r0, [sp, #0x44]
		STR r0, [sp, #0x14]
		LDR r0, [sp, #0x54]
		ADD r0, #3
		STR r0, [sp, #0x1c]
		B        |loc_08036140|
|loc_08036100|
		MOV r0, #2
		STRB r0, [r4, #0x10]
		LDR r0, [sp, #0x4c]
		SUB r0, #4
		STR r0, [sp, #0x14]
		LDR r0, [sp, #0x44]
		STR r0, [sp, #0x1c]
		B        |loc_08036140|
|loc_08036110|
		ADD r1, r4, #0
		MOV r0, sp
		BL       |Object_WriteBounds1|
		LDR r0, [sp]
		CMP r6, #0
		STR r0, [sp, #0x14]
		LDR r0, [sp, #8]
		STR r0, [sp, #0x1c]
		BLE      |loc_08036134|
		STRB r7, [r4, #0x10]
		LDR r0, [sp, #0x50]
		STR r0, [sp, #0x18]
		LDR r0, [sp, #0x58]
		SUB r0, #6
		STR r0, [sp, #0x20]
		B        |loc_08036140|
|loc_08036132|
		B        |loc_0803618E|
|loc_08036134|
		MOV r6, #1
		STRB r6, [r4, #0x10]
		LDR r0, [sp, #0x50]
		STR r0, [sp, #0x18]
		LDR r0, [sp, #4]
		STR r0, [sp, #0x20]
|loc_08036140|
		STR r4, [sp, #0x30]
		LDRB r0, [r4, #0x10]
		ADD r3, sp, #0x20
		ADD r2, sp, #0x10
		STRB r0, [r3, #4]
		LDR r0, [pc, #0x5c]
		ADD r3, sp, #0
		STR r0, [sp, #0x2c]
		MOV r0, #3
		LSL r0, r0, #9
		STR r0, [sp, #0x28]
		STRB r7, [r3, #0x10]
		STR r4, [sp, #0x40]
		LDR r1, [r5]
		ADD r0, r5, #0
		LDR r3, [r1, #0x24]
		ADD r3, r3, r1
		MOV r1, #0
		BL       |inc_0x046118_0x049114| + 0x98e
		CMP r0, #0
		BEQ      |loc_0803618E|
		LDR r0, [pc, #0x3c]
		LDR r4, [r0]
		MOV r0, #2
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r0, #0x30
|loc_08036178|
|unk_08036178|
		LSL r3, r0, #1
		ADD r0, r3, r0
		LDR r1, [pc, #0x30]
		LSL r0, r0, #2
		ADD r1, r0, r1
		LDR r0, [pc, #0x30]
		ADD r3, r7, #0
		MOV r2, #0x40
		ADD r0, r4, r0
		BL       |inc_0x03d784_0x041118| + 0xbf4
|loc_0803618E|
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0xe96
