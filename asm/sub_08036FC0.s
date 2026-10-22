	CODE16
|sub_08036FC0|
|unk_08036FC0|
		LDR r0, [pc, #0x270]
		LDR r6, [pc, #0x274]
		STR r0, [r4]
		MOV r0, #3
		LSL r0, r0, #9
		STRH r0, [r4, #0xe]
		ADD r1, r0, #0
		LDR r0, [r6, #4]
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_08036FEC|
		MOV r1, #3
		LSL r1, r1, #9
		LDR r0, [r6, #4]
		BL       |sub_08011732|
		MOV r1, #3
		LSL r1, r1, #9
		LDR r0, [r6, #4]
		BL       |loc_0801124C|
|loc_08036FEC|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x24c]
		MOV r3, #0
		STR r0, [r4]
		LDMIA r5!, {r1, r2}
		STR r1, [r4, #0x1c]
		STR r2, [r4, #0x20]
		LDRB r0, [r7, #0x10]
		SUB r5, #8
		LDR r6, [pc, #0x238]
		STR r0, [r4, #0x38]
		MOV r0, #0x37
		STRB r0, [r4, #8]
		LDR r0, [r5, #4]
		STR r0, [r4, #4]
		STR r7, [r4, #0x44]
		MOV r0, #0x20
		STR r0, [r4, #0x18]
		STRB r3, [r4, #0x10]
		LDR r0, [r5]
		LDR r1, [r5, #4]
		SUB r0, #0xc
		SUB r1, #0xc
		STR r1, [sp, #0x10]
		STR r0, [sp, #0xc]
		LDR r0, [r5]
		LDR r1, [r5, #4]
		ADD r0, #0xc
		STR r0, [sp, #0x14]
		ADD r1, #0xc
		STR r1, [sp, #0x18]
		MOV r0, #8
		STR r0, [r4, #0x34]
		LDR r5, [r6, #8]
		ADD r0, sp, #0xc
		ADD r5, #0x80
		LDR r1, [r5, #0x2c]
		BL       |loc_08009324|
		LDR r6, [pc, #0x204]
		CMP r0, #0
		BEQ      |loc_08037082|
		ADD r7, sp, #0xc
|loc_08037042|
		LDR r0, [r4, #0x38]
		ADD r2, sp, #8
		LSL r0, r0, #3
		ADD r0, r0, r6
		LDR r1, [r0]
		LDR r0, [r0, #4]
		LSL r1, r1, #3
		LSL r0, r0, #3
		STR r0, [sp, #8]
		ADD r0, r1, #0
		STR r1, [sp, #4]
		LDMIA r2!, {r1, r2}
		ADD r2, r2, r0
		STR r2, [sp, #0xc]
		LDR r2, [sp, #0x10]
		ADD r2, r2, r1
		STR r2, [sp, #0x10]
		LDR r2, [sp, #0x14]
		ADD r0, r2, r0
		STR r0, [sp, #0x14]
		LDR r0, [sp, #0x18]
		ADD r0, r0, r1
		STR r0, [sp, #0x18]
		LDR r0, [r4, #0x34]
		ADD r0, #8
		STR r0, [r4, #0x34]
		LDR r1, [r5, #0x2c]
		ADD r0, r7, #0
		BL       |loc_08009324|
		CMP r0, #0
		BNE      |loc_08037042|
|loc_08037082|
		LDR r0, [sp, #0x28]
		LDR r1, [pc, #0x1bc]
		LSL r3, r0, #1
		ADD r0, r3, r0
		LSL r0, r0, #2
		ADD r0, r0, r1
		STR r0, [r4, #0x40]
		LDR r1, [r0]
		LDR r0, [r4, #0x38]
		LSL r2, r0, #1
		ADD r2, r2, r0
		LSL r2, r2, #3
		ADD r1, r1, r2
		STR r1, [r4, #0x3c]
		LDR r1, [pc, #0x1a8]
		LSL r0, r0, #3
		LDR r1, [r1, #4]
		ADD r0, r0, r6
		STR r1, [r4, #0x14]
		LDR r1, [r0]
		LDR r0, [r0, #4]
		STR r0, [r4, #0x30]
		STR r1, [r4, #0x2c]
		ADD r0, r4, #0
		BL       |inc_0x351c0_0x3d4d0| + 0x1dac
		LDR r6, [pc, #0x180]
		LDR r5, [pc, #0x194]
		LDR r0, [r6]
		MOV r3, #0
		MOV r2, #0x40
		ADD r0, r0, r5
		LDR r1, [pc, #0x188]
		BL       |inc_0x03d784_0x041118| + 0xbf4
		ADD r0, r4, #0
		B        |inc_0x351c0_0x3d4d0| + 0x1dfc
