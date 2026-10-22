	CODE16
|sub_08030210|
|unk_08030210|
		LDR r0, [pc, #0x158]
		MOV r6, #7
		LSL r6, r6, #7
		LDR r5, [pc, #0x158]
		STR r0, [r4]
		STRH r6, [r4, #0xe]
		LDR r0, [r5]
		ADD r1, r6, #0
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_08030238|
		ADD r1, r6, #0
		LDR r0, [r5]
		BL       |sub_08011732|
		ADD r1, r6, #0
		LDR r0, [r5]
		BL       |loc_0801124C|
|loc_08030238|
		LSL r0, r0, #0x10
		LSR r0, r0, #0x10
		LDR r1, [pc, #0x134]
		STRH r0, [r4, #0xc]
		STR r1, [r4]
		LDR r1, [r7, #4]
		LDR r2, [r7]
		STR r1, [r4, #0x14]
		STR r2, [r4, #0x10]
		MOV r2, #0x55
		STR r2, [r4, #0x20]
		MOV r2, #0
		MVN r2, r2
		STR r2, [r4, #0x18]
		STR r2, [r4, #0x1c]
		MOV r2, #0x10
		STRB r2, [r4, #8]
		STR r1, [r4, #4]
		LDR r1, [pc, #0x118]
		LSL r0, r0, #5
		ADD r0, r0, r1
		LSR r1, r1, #0x11
		ADD r0, r0, r1
		LDR r1, [pc, #0x108]
		MOV r2, #0x80
		ADD r1, #4
		BL       |Thunk_VramCopy|
		ADD r0, r4, #0
		B        |inc_0x301c0_0x311c0| + 0x4e
