	CODE16
|sub_080247FA|
|unk_080247FA|
		LSL r3, r1, #1
		ADD r1, r3, r1
		LDR r0, [r4, #0x54]
		LSL r1, r1, #2
		ADD r0, r0, r1
		STR r0, [r4, #0x18]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		CMP r5, #0
		DCW     0xD0F2
		LDR r0, [r4, #0x1c]
		CMP r0, #0
		DCW     0xD0EF
		LDR r0, [r4, #0x40]
		CMP r0, #0
		DCW     0xD1EC
		LDR r0, [pc, #0x144]
		LDR r5, [r0]
		CMP r5, #0
		DCW     0xD0E8
		MOV r0, #0xff
		ADD r0, #0xcd
		LDR r0, [r0, r5]
		CMP r0, #0
		DCW     0xD0E3
		LDR r0, [r4, #0x20]
		LDR r1, [r4, #0x24]
		ASR r0, r0, #8
		SUB r0, #8
		STR r0, [sp, #0x18]
		ASR r1, r1, #8
		SUB r1, #8
		ADD r0, #0x10
		STR r0, [sp, #0x20]
		ADD r0, r1, #0
		ADD r0, #0x10
		STR r0, [sp, #0x24]
		STR r1, [sp, #0x1c]
		ADD r1, r5, #0
		ADD r0, sp, #4
		ADD r6, sp, #0x28
		BL       |loc_0800FE78|
		LDR r0, [sp, #4]
		LDR r1, [sp, #0x20]
		CMP r0, r1
		DCW     0xDACD
		LDR r0, [sp, #0x18]
		LDR r1, [sp, #0xc]
		CMP r0, r1
		DCW     0xDAC9
		LDR r0, [sp, #8]
		LDR r1, [sp, #0x24]
		CMP r0, r1
		DCW     0xDAC5
		LDR r0, [sp, #0x1c]
		LDR r1, [sp, #0x10]
		CMP r0, r1
		DCW     0xDAC1
		LDR r0, [r4, #0x1c]
		ADD r3, sp, #0x20
		STR r0, [sp, #0x34]
		LDRB r0, [r4, #0x10]
		STRB r0, [r3, #8]
		LDR r0, [pc, #0xe8]
		STR r0, [sp, #0x30]
		LDR r0, [pc, #0xe8]
		BL       |sub_08054A64|
		STR r0, [sp, #0x2c]
		LDRB r0, [r4, #0x11]
		ADD r3, sp, #0
		LDR r1, [pc, #0xb4]
		STRB r0, [r3, #0x14]
		STR r4, [sp, #0x44]
		MOV r0, #1
		STR r0, [r4, #0x40]
		LDR r0, [pc, #0xd8]
		LDR r0, [r0, #4]
		LDR r2, [r1, #4]
		SUB r2, r0, r2
		CMP r2, #0x80
		BLE      |loc_080248A4|
		STR r0, [r1, #4]
|loc_080248A4|
		ADD r1, r6, #0
		ADD r0, r5, #0
		BL       |Battle_ComputeDamage|
		LDR r1, [r5]
		ADD r0, r5, #0
		LDR r2, [r1, #0x5c]
		ADD r2, r2, r1
		ADD r1, r6, #0
		BL       |Thunk_JumpRegister1|
		LDR r1, [r5]
		ADD r0, r5, #0
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #0x17
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		DCW     0xD094
		LDR r1, [r5]
		ADD r0, r5, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
		DCW     0xE78C
