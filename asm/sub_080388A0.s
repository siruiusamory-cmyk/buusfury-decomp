	CODE16
|sub_080388A0|
|unk_080388A0|
		LDR r0, [pc, #0x1d0]
		MOV r6, #3
		LSL r6, r6, #9
		LDR r5, [pc, #0x1bc]
		STR r0, [r4]
		STRH r6, [r4, #0xe]
		LDR r0, [r5]
		ADD r1, r6, #0
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_080388C8|
		ADD r1, r6, #0
		LDR r0, [r5]
		BL       |sub_08011732|
		ADD r1, r6, #0
		LDR r0, [r5]
		BL       |loc_0801124C|
|loc_080388C8|
		LSL r0, r0, #0x10
		LSR r0, r0, #0x10
		LDR r1, [pc, #0x1a8]
		STRH r0, [r4, #0xc]
		STR r1, [r4]
		LDR r1, [sp, #4]
		MOV r5, #0
		LDR r2, [r1]
		LDR r1, [r1, #4]
		LSL r0, r0, #5
		STR r1, [r4, #0x14]
		STR r2, [r4, #0x10]
		STR r5, [r4, #0x3c]
		STR r7, [r4, #0x34]
		LDRB r3, [r7, #0x10]
		ADD r6, r3, #0
		STR r3, [r4, #0x38]
		LSL r3, r6, #4
		SUB r3, r3, r6
		LDR r6, [pc, #0x18c]
		LSL r3, r3, #2
		ADD r3, r3, r6
		STR r3, [r4, #0x2c]
		STR r3, [r4, #0x30]
		STR r5, [r4, #0x28]
		ADD r3, r2, #0
		SUB r3, #0x10
		STR r3, [r4, #0x18]
		ADD r5, r1, #0
		SUB r5, #0x10
		STR r5, [r4, #0x1c]
		STR r1, [r4, #4]
		ADD r3, r1, #0
		ADD r2, #0x10
		STR r2, [r4, #0x20]
		ADD r3, #0x10
		STR r3, [r4, #0x24]
		MOV r1, #0x37
		STRB r1, [r4, #8]
		LDR r5, [pc, #0x150]
		LDR r1, [pc, #0x150]
		MOV r6, #1
		LSL r6, r6, #0xa
		ADD r0, r0, r5
		ADD r2, r6, #0
		LDR r1, [r1, #8]
		BL       |Thunk_VramCopy|
		LDRH r0, [r4, #0xc]
		LDR r1, [r4, #0x2c]
		LSL r0, r0, #5
		ADD r0, r0, r5
		ADD r0, r0, r6
		LSR r2, r6, #1
		LDR r1, [r1, #8]
		BL       |Thunk_VramCopy|
		ADD r0, r4, #0
		B        |inc_0x351c0_0x3d4d0| + 0x36dc
